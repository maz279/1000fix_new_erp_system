// Package main implements the 1000FiX High-Throughput Telemetry Collector (CD-M02-03)
// Architecture Reference: ARCH-040, NFR-056 (30s / 100m throttle), PDPA Tier-1
//
// Storage: every accepted ping is flushed with a real batch INSERT into the
// fix_technician_telemetry table (schema per
// migrations/sql/timescaledb_telemetry_hypertable.sql). On boot the collector
// creates the table (and, when the server has the TimescaleDB extension
// available, the hypertable conversion) if absent. When the extension is not
// available the collector stores into a plain PostgreSQL table and says so
// honestly on /health (storage_mode=plain-postgres-table, timescaledb_ready=false).
package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"math"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"sync/atomic"
	"syscall"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

// TelemetryPing represents a single GPS position update from a field technician
type TelemetryPing struct {
	TechnicianID      int       `json:"technician_id"`
	Time              time.Time `json:"time"`
	Latitude          float64   `json:"latitude"`
	Longitude         float64   `json:"longitude"`
	AccuracyMeters    float32   `json:"accuracy_meters"`
	SpeedMps          float32   `json:"speed_mps"`
	BearingDeg        float32   `json:"bearing_deg"`
	BatteryLevel      float32   `json:"battery_level"`
	IsCharging        bool      `json:"is_charging"`
	ConnectivityState string    `json:"connectivity_state"` // "online", "degraded", "offline_buffered"
	IsThrottled       bool      `json:"is_throttled"`
	OperatingUnitID   int       `json:"operating_unit_id"`
}

// CollectorMetrics tracks throughput and throttle metrics
type CollectorMetrics struct {
	sync.RWMutex
	TotalIngested    int64 `json:"total_ingested"`
	TotalThrottled   int64 `json:"total_throttled"`
	TotalBatched     int64 `json:"total_batched"`
	TotalFlushed     int64 `json:"total_flushed"` // rows actually written to the DB
	TotalFlushErrors int64 `json:"total_flush_errors"`
}

func (m *CollectorMetrics) snapshot() CollectorMetrics {
	m.RLock()
	defer m.RUnlock()
	return CollectorMetrics{
		TotalIngested:    m.TotalIngested,
		TotalThrottled:   m.TotalThrottled,
		TotalBatched:     m.TotalBatched,
		TotalFlushed:     m.TotalFlushed,
		TotalFlushErrors: m.TotalFlushErrors,
	}
}

// LastKnownState holds cached technician state for NFR-056 throttling evaluation
type LastKnownState struct {
	LastTime time.Time
	Lat      float64
	Lon      float64
}

// storageMode names where pings actually land; reported verbatim on /health.
const (
	storageModeHypertable  = "timescaledb-hypertable"
	storageModePlainTable  = "plain-postgres-table"
	storageModeUnavailable = "unavailable"
)

// telemetryStore is the real PostgreSQL/TimescaleDB write path for pings.
type telemetryStore struct {
	pool *pgxpool.Pool

	mu              sync.RWMutex
	storageMode     string
	timescaleReady  bool
	schemaReady     bool
	schemaInitError string
}

func newTelemetryStore(ctx context.Context, dsn string) (*telemetryStore, error) {
	cfg, err := pgxpool.ParseConfig(dsn)
	if err != nil {
		return nil, fmt.Errorf("parse DATABASE_URL: %w", err)
	}
	cfg.MaxConns = 4
	pool, err := pgxpool.NewWithConfig(ctx, cfg)
	if err != nil {
		return nil, fmt.Errorf("connect database: %w", err)
	}
	return &telemetryStore{pool: pool, storageMode: storageModeUnavailable}, nil
}

// status returns an honest snapshot of the storage state for /health.
func (s *telemetryStore) status() (mode string, timescale, schemaReady bool, initErr string) {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return s.storageMode, s.timescaleReady, s.schemaReady, s.schemaInitError
}

// Ping verifies the database is actually reachable right now.
func (s *telemetryStore) Ping(ctx context.Context) error {
	return s.pool.Ping(ctx)
}

// EnsureSchema creates the telemetry table (+ hypertable when TimescaleDB is
// available) if absent. Mirrors migrations/sql/timescaledb_telemetry_hypertable.sql.
func (s *telemetryStore) EnsureSchema(ctx context.Context) error {
	if _, err := s.pool.Exec(ctx, "SELECT 1"); err != nil {
		s.recordInit("", false, false, err)
		return err
	}

	timescale := false
	if _, err := s.pool.Exec(ctx, "CREATE EXTENSION IF NOT EXISTS timescaledb"); err != nil {
		// Plain PostgreSQL (e.g. the compose dev stack) has no TimescaleDB:
		// fall back to a plain table and report that honestly.
		log.Printf("[WARN] TimescaleDB extension unavailable (%v); using a plain PostgreSQL table", err)
	} else if err := s.pool.QueryRow(
		ctx, "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb')",
	).Scan(&timescale); err != nil {
		log.Printf("[WARN] TimescaleDB extension check failed: %v", err)
	}

	const createTable = `
CREATE TABLE IF NOT EXISTS fix_technician_telemetry (
    time TIMESTAMPTZ NOT NULL,
    technician_id INTEGER NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    accuracy_meters REAL DEFAULT 0.0,
    speed_mps REAL DEFAULT 0.0,
    bearing_deg REAL DEFAULT 0.0,
    battery_level REAL DEFAULT 100.0,
    is_charging BOOLEAN DEFAULT FALSE,
    connectivity_state VARCHAR(32) DEFAULT 'online',
    is_throttled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    operating_unit_id INTEGER,
    company_id INTEGER DEFAULT 1
)`
	if _, err := s.pool.Exec(ctx, createTable); err != nil {
		s.recordInit("", timescale, false, err)
		return err
	}

	mode := storageModePlainTable
	if timescale {
		if _, err := s.pool.Exec(ctx, `
SELECT create_hypertable('fix_technician_telemetry', 'time',
                          if_not_exists => TRUE,
                          chunk_time_interval => INTERVAL '1 day')`); err != nil {
			// Extension present but hypertable conversion failed: stay honest.
			s.recordInit(storageModePlainTable, false, false, err)
			return err
		}
		mode = storageModeHypertable
	}

	indexes := []string{
		`CREATE INDEX IF NOT EXISTS idx_telemetry_tech_time ON fix_technician_telemetry (technician_id, time DESC)`,
		`CREATE INDEX IF NOT EXISTS idx_telemetry_spatial_grid ON fix_technician_telemetry (latitude, longitude, time DESC)`,
		`CREATE INDEX IF NOT EXISTS idx_telemetry_ou_time ON fix_technician_telemetry (operating_unit_id, time DESC)`,
	}
	for _, ddl := range indexes {
		if _, err := s.pool.Exec(ctx, ddl); err != nil {
			s.recordInit(mode, timescale, false, err)
			return err
		}
	}

	if _, err := s.pool.Exec(ctx, `
CREATE OR REPLACE VIEW view_technician_current_locations AS
SELECT DISTINCT ON (technician_id)
    technician_id,
    time AS last_ping_time,
    latitude,
    longitude,
    accuracy_meters,
    speed_mps,
    battery_level,
    connectivity_state,
    operating_unit_id
FROM fix_technician_telemetry
WHERE time > NOW() - INTERVAL '24 hours'
ORDER BY technician_id, time DESC`); err != nil {
		s.recordInit(mode, timescale, false, err)
		return err
	}

	s.recordInit(mode, timescale, true, nil)
	return nil
}

func (s *telemetryStore) recordInit(mode string, timescale, ready bool, err error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if mode != "" {
		s.storageMode = mode
	} else {
		s.storageMode = storageModeUnavailable
	}
	s.timescaleReady = timescale
	s.schemaReady = ready
	if err != nil {
		s.schemaInitError = err.Error()
	} else {
		s.schemaInitError = ""
	}
	log.Printf("[INFO] telemetry storage: mode=%s timescaledb_ready=%t schema_ready=%t err=%v",
		s.storageMode, s.timescaleReady, s.schemaReady, err)
}

const insertPingSQL = `INSERT INTO fix_technician_telemetry (
	time, technician_id, latitude, longitude, accuracy_meters, speed_mps,
	bearing_deg, battery_level, is_charging, connectivity_state, is_throttled,
	operating_unit_id
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)`

// InsertBatch writes a batch of pings with one round trip (pgx batch INSERT).
func (s *telemetryStore) InsertBatch(ctx context.Context, batch []TelemetryPing) error {
	b := &pgx.Batch{}
	for _, p := range batch {
		b.Queue(insertPingSQL,
			p.Time, p.TechnicianID, p.Latitude, p.Longitude,
			p.AccuracyMeters, p.SpeedMps, p.BearingDeg, p.BatteryLevel,
			p.IsCharging, p.ConnectivityState, p.IsThrottled, p.OperatingUnitID,
		)
	}
	br := s.pool.SendBatch(ctx, b)
	defer br.Close()
	for range batch {
		if _, err := br.Exec(); err != nil {
			return fmt.Errorf("insert ping: %w", err)
		}
	}
	return nil
}

func (s *telemetryStore) Close() {
	s.pool.Close()
}

// TelemetryCollector manages the high-throughput buffer and batch flusher
type TelemetryCollector struct {
	bufferChan  chan TelemetryPing
	lastState   sync.Map // technician_id (int) -> LastKnownState
	latestPings sync.Map // technician_id (int) -> TelemetryPing
	metrics     CollectorMetrics
	batchSize   int
	flushInterval time.Duration
	// store is written by the background connect/retry loop and read by the
	// flush worker and HTTP handlers; atomic because those run concurrently.
	store atomic.Pointer[telemetryStore]
}

func NewTelemetryCollector(bufferCap int, batchSize int, flushInterval time.Duration) *TelemetryCollector {
	return &TelemetryCollector{
		bufferChan:    make(chan TelemetryPing, bufferCap),
		batchSize:     batchSize,
		flushInterval: flushInterval,
	}
}

func (tc *TelemetryCollector) currentStore() *telemetryStore { return tc.store.Load() }

// haversineMeters calculates spherical distance between two lat/lon coordinates in meters
func haversineMeters(lat1, lon1, lat2, lon2 float64) float64 {
	const r = 6371000.0 // Earth radius in meters
	dLat := (lat2 - lat1) * math.Pi / 180.0
	dLon := (lon2 - lon1) * math.Pi / 180.0
	a := math.Sin(dLat/2)*math.Sin(dLat/2) +
		math.Cos(lat1*math.Pi/180.0)*math.Cos(lat2*math.Pi/180.0)*
			math.Sin(dLon/2)*math.Sin(dLon/2)
	c := 2 * math.Atan2(math.Sqrt(a), math.Sqrt(1-a))
	return r * c
}

// IngestPing evaluates NFR-056 throttle rules (30s / 100m) and queues to ring buffer.
// The ping is taken by pointer so the caller can see the IsThrottled verdict.
func (tc *TelemetryCollector) IngestPing(ping *TelemetryPing) bool {
	if ping.Time.IsZero() {
		ping.Time = time.Now().UTC()
	}

	tc.metrics.Lock()
	tc.metrics.TotalIngested++
	tc.metrics.Unlock()

	// Check NFR-056 throttle guard: < 30s elapsed AND < 100m moved
	isThrottled := false
	if val, ok := tc.lastState.Load(ping.TechnicianID); ok {
		prev := val.(LastKnownState)
		elapsed := ping.Time.Sub(prev.LastTime)
		distance := haversineMeters(prev.Lat, prev.Lon, ping.Latitude, ping.Longitude)

		if elapsed < 30*time.Second && distance < 100.0 {
			isThrottled = true
			tc.metrics.Lock()
			tc.metrics.TotalThrottled++
			tc.metrics.Unlock()
		}
	}

	ping.IsThrottled = isThrottled

	// Update last known state if not throttled
	if !isThrottled {
		tc.lastState.Store(ping.TechnicianID, LastKnownState{
			LastTime: ping.Time,
			Lat:      ping.Latitude,
			Lon:      ping.Longitude,
		})
	}

	// Cache latest coordinate for real-time dispatch queries
	tc.latestPings.Store(ping.TechnicianID, *ping)

	// Non-blocking queue to buffer
	select {
	case tc.bufferChan <- *ping:
		tc.metrics.Lock()
		tc.metrics.TotalBatched++
		tc.metrics.Unlock()
		return true
	default:
		log.Printf("[WARN] Telemetry buffer capacity reached, dropping non-critical ping for tech %d", ping.TechnicianID)
		return false
	}
}

// StartWorkerPool runs the batch consumer that flushes pings to the database
func (tc *TelemetryCollector) StartWorkerPool(ctx context.Context, wg *sync.WaitGroup) {
	defer wg.Done()

	ticker := time.NewTicker(tc.flushInterval)
	defer ticker.Stop()

	batch := make([]TelemetryPing, 0, tc.batchSize)

	for {
		select {
		case <-ctx.Done():
			// Flush remainder on shutdown
			if len(batch) > 0 {
				tc.flushBatch(ctx, batch)
			}
			return

		case ping := <-tc.bufferChan:
			batch = append(batch, ping)
			if len(batch) >= tc.batchSize {
				tc.flushBatch(ctx, batch)
				batch = make([]TelemetryPing, 0, tc.batchSize)
			}

		case <-ticker.C:
			if len(batch) > 0 {
				tc.flushBatch(ctx, batch)
				batch = make([]TelemetryPing, 0, tc.batchSize)
			}
		}
	}
}

// flushBatch performs the REAL batch INSERT into fix_technician_telemetry.
// Rows are only counted as flushed when the database write committed.
func (tc *TelemetryCollector) flushBatch(ctx context.Context, batch []TelemetryPing) {
	store := tc.currentStore()
	if store == nil {
		tc.metrics.Lock()
		tc.metrics.TotalFlushErrors += int64(len(batch))
		tc.metrics.Unlock()
		log.Printf("[ERROR] Flush of %d pings skipped: no database store connected yet (DATABASE_URL)", len(batch))
		return
	}

	flushCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	err := store.InsertBatch(flushCtx, batch)
	cancel()
	if err != nil {
		tc.metrics.Lock()
		tc.metrics.TotalFlushErrors += int64(len(batch))
		tc.metrics.Unlock()
		log.Printf("[ERROR] Flush of %d pings to %s failed: %v", len(batch), tc.storageMode(), err)
		return
	}

	tc.metrics.Lock()
	tc.metrics.TotalFlushed += int64(len(batch))
	tc.metrics.Unlock()
	log.Printf("[FLUSH] Batched %d pings into fix_technician_telemetry (mode=%s)", len(batch), tc.storageMode())
}

func (tc *TelemetryCollector) storageMode() string {
	store := tc.currentStore()
	if store == nil {
		return storageModeUnavailable
	}
	mode, _, _, _ := store.status()
	return mode
}

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8084"
	}
	dbDSN := os.Getenv("DATABASE_URL")
	if dbDSN == "" {
		dbDSN = "postgres://fix:change-me-dev-only@127.0.0.1:5433/fix_dev?sslmode=disable"
	}

	// 50,000 events/minute capacity: buffer 100,000, batch 500, flush 100ms
	collector := NewTelemetryCollector(100000, 500, 100*time.Millisecond)

	ctx, cancel := context.WithCancel(context.Background())
	var wg sync.WaitGroup
	wg.Add(1)
	go collector.StartWorkerPool(ctx, &wg)

	// Connect the storage and keep retrying in the background: a database that
	// is down at boot must not wedge the collector, and /health must report the
	// real state at all times.
	go func() {
		backoff := time.Second
		for {
			store, err := newTelemetryStore(ctx, dbDSN)
			if err == nil {
				if err := store.EnsureSchema(ctx); err == nil {
					collector.store.Store(store)
					mode, _, _, _ := store.status()
					log.Printf("[INFO] telemetry storage connected and schema ensured (mode=%s)", mode)
					return
				} else if !errors.Is(err, context.Canceled) {
					log.Printf("[ERROR] Schema init failed: %v (retrying)", err)
				}
				store.Close()
			} else if !errors.Is(err, context.Canceled) {
				log.Printf("[ERROR] Database connect failed: %v (retrying)", err)
			}
			select {
			case <-ctx.Done():
				return
			case <-time.After(backoff):
			}
			if backoff < 15*time.Second {
				backoff *= 2
			}
		}
	}()

	mux := http.NewServeMux()

	// 1. Health check — every field is measured, never assumed
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) {
		store := collector.currentStore()
		payload := map[string]interface{}{
			"service":          "telemetry-collector",
			"version":          "v2.1.0",
			"capacity_epm":     50000,
			"nfr_056_throttle": "30s/100m",
		}

		if store == nil {
			payload["status"] = "degraded"
			payload["db_reachable"] = false
			payload["timescaledb_ready"] = false
			payload["storage_mode"] = storageModeUnavailable
			payload["detail"] = "database not connected yet (DATABASE_URL unreachable or schema init pending); pings are NOT persisted"
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusServiceUnavailable)
			json.NewEncoder(w).Encode(payload)
			return
		}

		pingCtx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
		dbErr := store.Ping(pingCtx)
		cancel()

		mode, timescale, schemaReady, initErr := store.status()
		payload["db_reachable"] = dbErr == nil
		payload["timescaledb_ready"] = timescale // measured: extension present AND hypertable created
		payload["storage_mode"] = mode
		payload["schema_ready"] = schemaReady
		if dbErr != nil {
			payload["status"] = "degraded"
			payload["detail"] = fmt.Sprintf("database ping failed: %v", dbErr)
		} else if initErr != "" {
			payload["status"] = "degraded"
			payload["detail"] = fmt.Sprintf("schema init error: %s", initErr)
		} else {
			payload["status"] = "healthy"
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(payload)
	})

	// 2. Metrics endpoint
	mux.HandleFunc("GET /metrics", func(w http.ResponseWriter, r *http.Request) {
		m := collector.metrics.snapshot()
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(m)
	})

	// 3. Ingestion endpoint (single ping object or batch array)
	mux.HandleFunc("POST /api/v1/telemetry", func(w http.ResponseWriter, r *http.Request) {
		body, err := io.ReadAll(io.LimitReader(r.Body, 8<<20))
		if err != nil {
			http.Error(w, "failed to read request body", http.StatusBadRequest)
			return
		}

		var pings []TelemetryPing
		trimmed := bytes.TrimLeft(body, " \t\r\n")
		if len(trimmed) > 0 && trimmed[0] == '[' {
			if err := json.Unmarshal(body, &pings); err != nil {
				http.Error(w, "invalid request body", http.StatusBadRequest)
				return
			}
		} else {
			var single TelemetryPing
			if err := json.Unmarshal(body, &single); err != nil || single.TechnicianID <= 0 {
				http.Error(w, "invalid request body", http.StatusBadRequest)
				return
			}
			pings = append(pings, single)
		}

		accepted := 0
		throttled := 0
		for i := range pings {
			p := &pings[i] // IngestPing flags throttling on the ping itself
			if collector.IngestPing(p) {
				accepted++
				if p.IsThrottled {
					throttled++
				}
			}
		}

		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusAccepted)
		json.NewEncoder(w).Encode(map[string]interface{}{
			"accepted":  accepted,
			"throttled": throttled,
		})
	})

	// 4. Latest technician location
	mux.HandleFunc("GET /api/v1/telemetry/latest/", func(w http.ResponseWriter, r *http.Request) {
		var techID int
		fmt.Sscanf(r.URL.Path, "/api/v1/telemetry/latest/%d", &techID)
		if techID <= 0 {
			http.Error(w, "invalid technician_id", http.StatusBadRequest)
			return
		}

		if val, ok := collector.latestPings.Load(techID); ok {
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(val)
			return
		}
		http.Error(w, "technician location not found", http.StatusNotFound)
	})

	srv := &http.Server{
		Addr:    ":" + port,
		Handler: mux,
	}

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)

	go func() {
		log.Printf("[INFO] Telemetry Collector listening on :%s (capacity: 50k epm)", port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("[FATAL] ListenAndServe error: %v", err)
		}
	}()

	<-stop
	log.Println("[INFO] Shutting down Telemetry Collector gracefully...")
	cancel()
	srv.Shutdown(context.Background())
	wg.Wait()
	if store := collector.currentStore(); store != nil {
		store.Close()
	}
	log.Println("[INFO] Collector shutdown complete.")
}

-- Runs once, on first initdb of the pgdata volume (docker-entrypoint-initdb.d).
-- Airflow (integration profile) needs its own metadata database; without it the
-- scheduler exits at boot with: database "airflow" does not exist.
-- Existing volumes: create once with
--   docker compose ... exec postgres psql -U fix -d fix_dev -c 'CREATE DATABASE airflow OWNER fix'
CREATE DATABASE airflow OWNER fix;

import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '../..');

const portals = [
  { name: 'corporate', port: 3001 },
  { name: 'analytics', port: 3002 },
  { name: 'seller', port: 3003 },
  { name: 'brand', port: 3004 },
  { name: 'agent-console', port: 3005 },
  { name: 'partner', port: 3006 },
  { name: 'vendor', port: 3007 }
];

console.log('--- Launching Portals Supervisor ---');

const processes = [];

for (const p of portals) {
  const dir = path.join(root, 'apps', 'web', p.name);
  console.log(`[Supervisor] Spawning ${p.name} on port ${p.port}...`);
  const child = spawn('npx.cmd', ['next', 'dev', '--turbopack', '--port', String(p.port), '--hostname', '127.0.0.1'], {
    cwd: dir,
    stdio: 'pipe',
    shell: true
  });

  child.stdout.on('data', (d) => {
    const msg = d.toString().trim();
    if (msg.includes('Ready in') || msg.includes('Local:')) {
      console.log(`[${p.name}] ${msg}`);
    }
  });

  child.stderr.on('data', (d) => {
    const err = d.toString().trim();
    if (err && !err.includes('ExperimentalWarning')) {
      console.error(`[${p.name} ERR] ${err}`);
    }
  });

  child.on('exit', (code) => {
    console.log(`[Supervisor] ${p.name} exited with code ${code}`);
  });

  processes.push(child);
}

// Keep supervisor alive
process.stdin.resume();

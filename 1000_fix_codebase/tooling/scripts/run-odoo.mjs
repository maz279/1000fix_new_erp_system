import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '../..');

const pythonExe = path.join(root, '.venv', 'Scripts', 'python.exe');
const odooBin = path.join(root, 'vendor', 'odoo', 'odoo-bin');
const confFile = path.join(root, 'infra', 'odoo-conf', 'local.resolved.conf');

console.log('[Odoo Supervisor] Starting Odoo 19 supervisor daemon...');

function startOdoo() {
  const env = {
    ...process.env,
    PYTHONPATH: `${root};${path.join(root, 'vendor', 'odoo')};${process.env.PYTHONPATH || ''}`,
    TZ: 'UTC',
  };

  const args = [odooBin, '-c', confFile, '-d', 'fix_dev', '--dev=all'];
  console.log(`[Odoo Supervisor] Launching: ${pythonExe} ${args.join(' ')}`);

  const child = spawn(pythonExe, args, {
    cwd: root,
    env,
    stdio: 'pipe',
  });

  child.stdout.on('data', (data) => {
    const text = data.toString().trim();
    if (text) {
      // Print significant lines
      if (text.includes('INFO') || text.includes('WARNING') || text.includes('ERROR') || text.includes('HTTP')) {
        console.log(`[Odoo] ${text.split('\n').slice(-2).join(' ')}`);
      }
    }
  });

  child.stderr.on('data', (data) => {
    const text = data.toString().trim();
    if (text) {
      console.error(`[Odoo ERR] ${text.split('\n').slice(-2).join(' ')}`);
    }
  });

  child.on('exit', (code, signal) => {
    console.warn(`[Odoo Supervisor] Odoo process exited (code=${code}, signal=${signal}). Restarting in 2s...`);
    setTimeout(startOdoo, 2000);
  });
}

startOdoo();
process.stdin.resume();

import { execSync } from 'child_process';
import fs from 'fs';

const results = {};
for (const mod of ['m21', 'm22', 'm55', 'm56', 'm57', 'm58', 'm59']) {
  const output = execSync(`node tooling/scripts/tmp_${mod}.mjs`, { encoding: 'utf-8' });
  const data = JSON.parse(output);
  results[mod] = data;
  fs.unlinkSync(`tooling/scripts/tmp_${mod}.mjs`);
}

fs.writeFileSync('tooling/scripts/a09_full_js_parsed.json', JSON.stringify(results, null, 2), 'utf-8');
console.log('Successfully saved tooling/scripts/a09_full_js_parsed.json');

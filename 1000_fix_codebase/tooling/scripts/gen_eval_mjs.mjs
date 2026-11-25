import fs from 'fs';
import path from 'path';

const a09_dir = path.resolve('addons/platform/cd_p03_portal/static/src/a09');
for (const mod of ['m21', 'm22', 'm55', 'm56', 'm57', 'm58', 'm59']) {
  const filePath = path.join(a09_dir, `${mod}.js`);
  let content = fs.readFileSync(filePath, 'utf-8');
  // strip odoo-module directive
  content = content.replace('/** @odoo-module **/', '');
  // replace export const with const
  content = content.replace(/export const/g, 'const');
  content += `\nconsole.log(JSON.stringify({MODULE, SCREENS: Object.keys(SCREENS).map(k => ({id: k, ...SCREENS[k]})), REPORT_ROUTES, FORM_CHIPS}, null, 2));`;
  
  const tmpFile = path.resolve(`tooling/scripts/tmp_${mod}.mjs`);
  fs.writeFileSync(tmpFile, content, 'utf-8');
}
console.log('Generated tmp modules');

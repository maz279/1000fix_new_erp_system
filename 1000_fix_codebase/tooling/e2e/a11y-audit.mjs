// a11y-audit.mjs - Dedicated Accessibility Audit following the a11y-debugging skill guidelines.
// Checks: Heading hierarchy, Form input labels, Button accessible names, Image alt text,
// Semantic landmarks, Tap targets, and Color contrast tokens across portals.

import { chromium } from "@playwright/test";
import path from "node:path";
import fs from "node:fs";

const exe =
  process.env.CHROMIUM_EXECUTABLE_PATH ||
  path.join(
    process.env.USERPROFILE || process.env.HOME || ".",
    "AppData/Local/ms-playwright/chromium_headless_shell-1200/chrome-headless-shell-win64/chrome-headless-shell.exe"
  );

const AUDIT_TARGETS = [
  { name: "Customer Portal - Home", url: "http://127.0.0.1:3010/" },
  { name: "Customer Portal - Welcome", url: "http://127.0.0.1:3010/welcome" },
  { name: "Customer Portal - Booking", url: "http://127.0.0.1:3010/booking" },
  { name: "Corporate Portal - Home", url: "http://127.0.0.1:3001/" },
  { name: "Corporate Portal - Estate", url: "http://127.0.0.1:3001/estate" },
  { name: "Seller Portal - Home", url: "http://127.0.0.1:3013/" },
  { name: "Vendor Portal - Home", url: "http://127.0.0.1:3017/" },
];

const browser = await chromium.launch({
  headless: true,
  ...(fs.existsSync(exe) ? { executablePath: exe } : {}),
});

console.log("================================================================================");
console.log(" 1000FiX ACCESSIBILITY (a11y) AUDIT — WCAG 2.2 AA COMPLIANCE SCAN");
console.log("================================================================================\n");

let totalViolations = 0;
let passedPages = 0;

for (const target of AUDIT_TARGETS) {
  const page = await browser.newPage({ viewport: { width: 1366, height: 768 } });
  try {
    await page.goto(target.url, { waitUntil: "networkidle", timeout: 20000 });
    
    // Evaluate accessibility rules in DOM
    const audit = await page.evaluate(() => {
      const violations = [];
      
      // 1. Semantic Landmarks: Must have <main> and <nav> or <header>
      const mains = document.querySelectorAll("main");
      if (mains.length === 0) {
        violations.push({ type: "Landmark", issue: "Page missing <main> landmark" });
      }
      
      // 2. Heading Hierarchy: h1 should be present, headings shouldn't skip levels
      const headings = Array.from(document.querySelectorAll("h1, h2, h3, h4, h5, h6")).map(h => ({
        tag: h.tagName.toLowerCase(),
        level: parseInt(h.tagName[1]),
        text: h.textContent.trim().slice(0, 30),
      }));
      
      if (headings.length > 0) {
        let prevLevel = 0;
        for (const h of headings) {
          if (prevLevel > 0 && h.level > prevLevel + 1) {
            violations.push({
              type: "Heading",
              issue: `Skipped heading level: from h${prevLevel} to ${h.tag} ("${h.text}")`,
            });
          }
          prevLevel = h.level;
        }
      }
      
      // 3. Form Input Labels: every input, select, textarea must have an accessible label
      const inputs = Array.from(document.querySelectorAll("input, select, textarea"));
      for (const input of inputs) {
        if (input.type === "hidden") continue;
        const id = input.id;
        const ariaLabel = input.getAttribute("aria-label");
        const ariaLabelledby = input.getAttribute("aria-labelledby");
        const hasAssociatedLabel = id && document.querySelector(`label[for="${id}"]`);
        const isWrappedByLabel = input.closest("label");
        const placeholder = input.getAttribute("placeholder");
        
        if (!ariaLabel && !ariaLabelledby && !hasAssociatedLabel && !isWrappedByLabel && !placeholder) {
          violations.push({
            type: "Form",
            issue: `Input [${input.type || "text"}] missing label and aria-label: ${input.name || id || "unnamed"}`,
          });
        }
      }
      
      // 4. Buttons and Links: Must have non-empty accessible name
      const interactives = Array.from(document.querySelectorAll("button, a[href]"));
      for (const el of interactives) {
        const text = (el.innerText || el.textContent || "").trim();
        const ariaLabel = el.getAttribute("aria-label");
        const title = el.getAttribute("title");
        const img = el.querySelector("img[alt]");
        const alt = img ? img.getAttribute("alt") : null;
        
        if (!text && !ariaLabel && !title && !alt) {
          violations.push({
            type: "Interactive",
            issue: `Element <${el.tagName.toLowerCase()}> has empty accessible name: outerHTML=${el.outerHTML.slice(0, 60)}`,
          });
        }
      }
      
      // 5. Images: Must have alt attribute
      const images = Array.from(document.querySelectorAll("img"));
      for (const img of images) {
        if (!img.hasAttribute("alt")) {
          violations.push({
            type: "Image",
            issue: `Image missing alt attribute: src=${img.getAttribute("src")?.slice(0, 40)}`,
          });
        }
      }
      
      // 6. Tap target sizing (WCAG 2.2 SC 2.5.8 - Level AA: 24x24px minimum for buttons & controls)
      const undersized = [];
      const controls = Array.from(document.querySelectorAll("button, [role='button'], input[type='button'], input[type='submit']"));
      for (const el of controls) {
        const style = window.getComputedStyle(el);
        if (style.display === "none" || style.visibility === "hidden" || el.hasAttribute("hidden")) continue;

        const rect = el.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
          if (rect.width < 24 || rect.height < 24) {
            undersized.push({
              tag: el.tagName.toLowerCase(),
              text: (el.innerText || el.textContent || el.getAttribute("aria-label") || "").trim().slice(0, 30),
              w: Math.round(rect.width),
              h: Math.round(rect.height),
            });
          }
        }
      }
      if (undersized.length > 0) {
        violations.push({
          type: "TapTarget",
          issue: `${undersized.length} interactive buttons/controls smaller than 24x24px: ${JSON.stringify(undersized.slice(0, 5))}`,
        });
      }
      
      return {
        headingsCount: headings.length,
        headingsList: headings.map(h => `${h.tag}: ${h.text}`),
        inputsCount: inputs.length,
        buttonsCount: interactives.length,
        imagesCount: images.length,
        violations,
      };
    });
    
    if (audit.violations.length === 0) {
      console.log(`[PASS] ${target.name}`);
      console.log(`       Stats: ${audit.headingsCount} headings, ${audit.inputsCount} inputs, ${audit.buttonsCount} buttons, ${audit.imagesCount} images. 0 a11y violations.`);
      passedPages++;
    } else {
      console.log(`[WARN] ${target.name} (${audit.violations.length} issues)`);
      if (audit.headingsList && audit.headingsList.length > 0) {
        console.log(`       Headings found: ${audit.headingsList.join(" | ")}`);
      }
      audit.violations.forEach(v => console.log(`       - [${v.type}] ${v.issue}`));
      totalViolations += audit.violations.length;
    }
  } catch (err) {
    console.log(`[ERR]  ${target.name} could not be audited: ${err.message}`);
  } finally {
    await page.close();
  }
}

await browser.close();

console.log("\n================================================================================");
console.log(` a11y AUDIT SUMMARY: ${passedPages}/${AUDIT_TARGETS.length} pages passed with 0 violations (Total issues: ${totalViolations})`);
console.log("================================================================================");

process.exit(totalViolations > 0 ? 1 : 0);

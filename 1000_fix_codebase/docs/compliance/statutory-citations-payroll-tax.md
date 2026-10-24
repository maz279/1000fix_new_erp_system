# Statutory Citations Register — Bangladesh Payroll & Income Tax (M56 / R06-M03)

**Document Reference**: `LEGAL-CIT-2026-BD-M56`  
**Governing Milestone**: R06-M03 — M56 Payroll Statutory Completion, BEFTN, and the 100% Gate  
**Compliance Verification Date**: 2026-10-18  
**Statutory Scope**: Bangladesh Labour Act 2006, Bangladesh Labour (Amendment) Act 2026, Income Tax Act 2023, Finance Act 2024, Finance Ordinance 2024, and Bangladesh Bank BEFTN Operating Rules.

---

## 1. Bangladesh Income Tax (Income Tax Act 2023 & Finance Acts)

| Statutory Area | Act & Section Citation | Legal Requirement / Statutory Formula | Enacted Rate / Threshold |
|---|---|---|---|
| **General Tax-Free Threshold** | Income Tax Act 2023 (Act 12 of 2023), Schedule 1; Finance Act 2024 | Minimum annual taxable income before income tax assessment applies. | **BDT 375,000** |
| **Female & Senior Citizen Threshold** | Section 173(2) & First Schedule | Female taxpayers and senior citizens aged 65 years and above. | **BDT 400,000** |
| **Persons with Disabilities & Third Gender** | First Schedule, Part 1 | Physically challenged individuals with registration and third gender individuals. | **BDT 475,000** |
| **Gazetted War-Wounded Freedom Fighters** | First Schedule, Part 1 | Gazetted war-wounded freedom fighters. | **BDT 500,000** |
| **Disabled Child Exemption** | First Schedule, Proviso | Additional threshold per disabled child/dependent. | **+BDT 50,000** |
| **Progressive Tax Slabs** | First Schedule, Part 1 | Progressive rates on annual taxable income exceeding statutory threshold: | <ul><li>Next BDT 300,000: **10%**</li><li>Next BDT 400,000: **15%**</li><li>Next BDT 500,000: **20%**</li><li>Next BDT 2,000,000: **25%**</li><li>Balance: **30%**</li></ul> |
| **Investment Tax Rebate** | Income Tax Act 2023, Section 78 | Tax rebate on allowable investments (DPS, approved securities, PF). Lower of: | <ul><li>3% of taxable income</li><li>15% of allowable investment</li><li>BDT 1,000,000 cap</li></ul> |
| **Minimum Tax (TDS)** | Section 173 & Rule 36 | Minimum annual income tax when taxable income triggers liability: | <ul><li>Dhaka & Chattogram City Corp: **BDT 5,000**</li><li>Other City Corporations: **BDT 4,000**</li><li>Non-City Corporation Areas: **BDT 3,000**</li></ul> |
| **Monthly TDS Withholding** | Section 102 | Employer deduction at source on monthly salary based on estimated annual projection. | `Tax_Month = Annual_Tax / 12` |

---

## 2. Bangladesh Labour Act 2006 & Labour (Amendment) Act 2026

| Statutory Area | BLA Citation | Legal Formula & Statutory Interpretation | Enacted Convention |
|---|---|---|---|
| **Provident Fund (PF)** | BLA 2006 Section 264; Bangladesh Labour Rules 2015, Rule 351 | Equal monthly contributions by employee and employer, managed by equal-representation Board of Trustees. | **10% Basic** (Employee) + **10% Basic** (Employer matching) |
| **PF Deposit Deadline** | Labour Rules 2015, Rule 351(4) | Total PF deduction and employer contribution must be credited into PF Trust account within **15 days** of the following month. | `Deposit_Date <= 15th of month (M+1)` |
| **Gratuity Vesting** | BLA 2006 Section 2(10) & Section 27 | Minimum qualifying period of continuous service to entitle an employee to gratuity on separation. | **5 Completed Years** continuous service |
| **Gratuity Banding** | BLA 2006 Section 27, amended 2026 | Monthly-rated worker daily wage formula: `Basic_Monthly / 30`. | <ul><li>Service <= 12 years: **30 days' basic** per completed year</li><li>Service > 12 years: **45 days' basic** per completed year exceeding 12</li></ul> |
| **Voluntary Resignation Pay** | BLA 2006 Section 27(3) as amended 2026 | Statutory compensation upon voluntary resignation by permanent workers based on completed service length. | <ul><li>Service < 5 years: **7 days' wages** per completed year</li><li>Service 5 to 10 years: **15 days' wages** per completed year</li><li>Service > 10 years: **30 days' wages** per completed year (or gratuity)</li></ul> |
| **Retrenchment / Notice Pay** | BLA 2006 Section 20 & Section 26 | Compensation for termination without cause / retrenchment of permanent worker. | **30 days' basic** per year of service + **120 days' wages** in lieu of notice |
| **Statutory Overtime** | BLA 2006 Section 108 | Overtime wage rate for work performed in excess of standard 8 hours/day or 48 hours/week. | **Double the ordinary rate of basic wage** (`2.0 * Basic / 240 hours`) |

---

## 3. Bangladesh Bank BEFTN Integration (INT-005)

| Operational Requirement | Regulatory Citation | Protocol Standard |
|---|---|---|
| **Clearing System** | Bangladesh Bank Payment Systems Dept. (PSD) Operating Rules (2010 as amended) | Bangladesh Electronic Funds Transfer Network (BEFTN) |
| **Banking Week** | Bangladesh Bank Circular on Clearing Schedules | **Sunday through Thursday** (Friday & Saturday are statutory non-banking days). |
| **Clearing Cut-off Window** | BEFTN Operating Schedule §4.2 | Daily batch submission deadline: **16:00 (4:00 PM)**. Submissions after 16:00 roll to the next business clearing day. |
| **Holiday Rollover** | Bangladesh Bank Annual Holiday Schedule | Transactions falling on statutory national holidays roll forward to the next business clearing day. |
| **Batch Record Format** | BEFTN File Specifications | **128-byte fixed-width ASCII records** (Header Types 1/5, Detail Type 6, Control Types 8/9). |

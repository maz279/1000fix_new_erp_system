# A02 ERP audit, pass 2 — owner decisions (20 Nov 2026)

The second, independent pass over A02 (M01-M06, M31) found about 100 distinct defects after
de-duplication (9 P0). Most need no business input and are being fixed. The items below change
money, policy or statute, so each needs your call. **R** = my recommendation, applied if you say
"apply all recommendations".

| # | Finding | Question | R (recommended) |
|---|---|---|---|
| D1 | M03-01 / X5-04 | A repaired device can go out on a delivery leg unpaid and un-QC'd. How may an unpaid order travel? | Delivery leg only when the order is Ready AND (paid, credit-released, or a cash-on-delivery leg). Build service-order COD: the rider/courier collects the amount due, it books as an M20 receipt via the COD clearing account 100204 and enters the rider settlement. |
| D2 | M04-01 / X5-02 | Drawer cash-outs post nothing to the GL. Which accounts? | Petty expense: Dr 500211 Miscellaneous Expense (an expense category on the movement can pick 500002 Conveyance / 500011 Entertainment); staff advance: Dr 100029 Advance Loan (Office Employee), employee as partner; safe drop: Dr a new 100112 "Cash in Safe" (branch safe), and the M50 deposit may take cash from the safe. All Cr 100108 Cash In Hand. |
| D3 | M02-01 | On-site payment smaller than the amount due. | Accept it as a part payment: it is booked as an advance receipt on the order (drawer and GL move together); the order stays unpaid for the rest. |
| D4 | M02-03 | On-site jobs never reach Delivered (need M01 QC at the depot). | On-site orders skip the depot QC: the field sign-off + post-work photo is the QC and delivery evidence; the tax invoice is raised at field completion. |
| D5 | M02-04 | Parts fitted on site that are not on the estimate. | Refused unless an approved estimate revision covers them; a configured consumables list (screws, thermal paste, cable ties) is exempt. |
| D6 | M01-03 | Customer refuses a repair that is already done (Ready). | Only a Service Supervisor can cancel from QC/Ready; the customer owes the approved estimate; any waiver goes through the goodwill approval. |
| D7 | M05-S04 / X5-08 | MSP SLA credit: share of fee before or after VAT? | Before VAT; the credit note is grossed up by the invoice's VAT so the VAT reversal (Mushak 6.7) is right. |
| D8 | M05-S06 | Price master for MSP billing. | The M05 contract terms; every commercial amendment (price, device count up or down) flows to the M39 subscription by event; a reconciliation report flags differences; go-live needs exactly one live subscription. |
| D9 | M05-S08 | Longest onboarding before the SLA binds. | The SLA binds at the target go-live date, capped at 30 days from contract start. |
| D10 | M05-S09 | What the per-device MSP fee covers. | Labour and remote support only. Parts and out-of-scope work are an approved overage estimate unless the contract has a parts entitlement. |
| D11 | M05-S17 / X5-15 | Remote-support hours. | Hours are an entitlement when the contract sets one; usage is metered; at 80% the client is told; above 100% the hours are billed at the contract's overage rate (no rate = not billed, flagged). |
| D12 | M01-08 | Default estimate validity. | 15 days from sending; locked once sent. |
| D13 | M01-13 | Uncollected devices (spec Q-01). | Reminders at 3, 7, 15 and 30 days after Ready; at 30 days a formal notice; disposal only after 90 days with manager approval. One parameter used everywhere. |
| D14 | M31-07 | Workshop cost gate against what? | Gate against the estimate's price excluding VAT; report cost variance against estimated cost. |
| D15 | M06-04 | How a data-case purge is proved. | Lab-side: the lab's working copy / key destruction is recorded on a purge certificate bound to the case and dated after hand-over. A customer's drive certificate never proves a purge. |
| D16 | M06-09 | Sanitisation technique matrix. | High-confidentiality or resale SSD/flash: Purge or crypto-erase only; HDD: Clear allowed for internal reuse, Purge for resale; physical destruction needs a witness and a photo. Quality Manager can amend the matrix. |
| D17 | M06-11 | Automatic purge after retention. | On (30 days after hand-over, unless on legal hold), with escalation to the lab manager. |
| D18 | M06-13 | Partial recovery under no-data-no-fee. | Fee is due only when the customer confirms their target data at hand-over; otherwise the lab manager sets a reduced fee (approval). |
| D19 | M02-09 / X5-06 | Dispatch working-time limit (BLA 2006). | 8 h a day normal, 10 h a day absolute with approved overtime (M55); max 6 jobs per technician per day; overtime approved by the Field Service Manager. |
| D20 | M02-11 / M03-08 | Field / rider cash hand-in deadline. | By the end of the next business day; after that the technician/rider gets no new cash jobs and the logistics manager and finance are alerted. Shortages book like the rider COD shortage (payroll recovery 2001821). |
| D21 | M02-12 | Customer-absent (wasted) visit fee. | A configurable fee (default BDT 0 = off) that a dispatcher can waive; failed visits reported by type, zone and technician. |
| D22 | M03-05 / M03-06 | Pick-and-drop charges and courier rate control. | A zone x weight tariff table (default empty = no charge); warranty/AMC orders waived; courier bills checked against the courier's rate card with a 5% tolerance; non-COD freight raises an AP bill per courier batch. |
| D23 | X5-03 | Who decides a non-standard VAT rate on an estimate. | The M51 tariff master only: estimates compute VAT per line through M51, so the estimate and the invoice always agree. |
| D24 | X5-05 | M09 warranty claim write-off. | The M09 Finance Manager approval is the M20 approval: the write-off posts Dr 510008 Bad Debts / Cr AR on the OEM invoice. |
| D25 | X5-09 | Loyalty points base. | Earned on the paid amount excluding VAT; none on warranty/zero-charge jobs; reversed on credit notes. |
| D26 | X5-11 | Approval thresholds. | The M63 DoA register is the single source; code values are only the fallback when no register row exists. |

**Decided 20 Nov 2026 (owner):** apply all recommendations D1-D26. Confirmed explicitly: D1 gate +
build service-order COD; D2 new account 100112 Cash in Safe; D10 MSP fee = labour + remote only.

## Needs your VAT adviser (not decided by me)
- X5-12: tax point when payment comes before delivery (VAT & SD Act 2012 s.32).
- X5-21: one Mushak 6.3 per counter-basket item vs one per basket.
- X5-13: parts consumption is posted to suspense 110999 until the cut-over entry (estate GV-005 design); per-movement COGS / warranty cost split is a finance design change.

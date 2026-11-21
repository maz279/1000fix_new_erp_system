# R5 findings: M40 partner/channel, plus A04-wide cross checks (20 Nov 2026)

- Probes are in `%TEMP%\a04erp\R5\`: probe_m40/b/c, probe_static, probe_reports, probe_events, probe_acl.
- Every probe ran as a fresh non-superuser env on fix_real_a04 and was rolled back.
- Counts: P0 4, P1 15, P2 16, P3 4.
- File abbreviations: fp = `cd_partner/models/fix_partner.py`, ops = `fix_partner_ops.py`, cap = `fix_partner_capture.py`.

## M40
| id | sev | finding / evidence | fix |
|---|---|---|---|
| F1 | P0 | **The franchise royalty never reaches AR or GL.** `action_record_invoice` stores a typed reference and sets the state to invoiced (cap:1859-1869). Probe: 0 AR invoices, 0 moves, no VAT. | Raise a `fix.ar.invoice` (royalty + levy, VAT via M51). |
| F2 | P0 | **The franchise initial fee is never billed.** `partner.franchise_activated` (ops:943) has 0 consumers: a 750,000 fee produced 0 invoices. | Add a consumer or raise the invoice inline. |
| F3 | P0 | **An MDF claim is "paid" by a typed reference.** Approval publishes nothing (cap:2074-2116): 120,000 marked paid, 0 moves, 0 payment instructions. | Approval creates a pending `fix.payment.execution`, like the rebate does. |
| F4 | P1 | **Attribution can be changed by anyone.** base.group_user can write and create `fix.referral` (ACL row 3). A plain user moved a converted referral from P (5%) to Q (50%), and Q earned 10,000. | Freeze partner, customer and invoice after "submitted"; read-only for base users. |
| F5 | P1 | **One Channel Manager can set a 100% commission rate alone** (fp:469-485). The default is a hard-coded 5% (fp:116), and the tier's `commission_ref` is a text field nobody reads. | DOFA/M63 approval on rate changes; source the rate from the tier/M11. |
| F6 | P1 | **Three commission rates disagree.** The referral shows 10,000 (50%) but the GL posted 600 (M53 scheme 3%), to a different payee (fp:867-875; `fix_settlement_ext.py:497-504`; `fix_settlement_m53.py:339-340`). | One rate source. |
| F7 | P1 | **Commission is paid on revenue from before the referral.** `_fix_referral_evidence` (m53:251-296) takes any paid invoice with no attribution window: an invoice dated 1 Mar 2025 paid a referral created 20 Nov 2026. | Invoices dated from the referral date, within the attribution window. |
| F8 | P1 | **The portal leaks customer names and allows customer squatting.** `partner_api.py:107` and `:154` return any res.partner's name via sudo (id 27376's real name was returned), and first-in-wins blocks other partners. | Never echo existing party data; a referral creates a lead. |
| F9 | P1 | **Partners that are not onboarded still earn.** A prospective partner earned 2,500, and a suspended partner's portal user still creates referrals (BRU-PCM-01/13). | Gate on the active state; revoke the portal on suspend. |
| F10 | P1 | **Portal referrals record no customer consent** (BRU-PCM-06): there are no consent fields. | Add consent capture. |
| F11 | P1 | **Onboarding needs no agreement, checklist or programme** (fp:372-420). | Gate onboarding on them. |
| F12 | P1 | **The rebate basis is typed by the officer who accrues it:** 9,999,999 accrued 1,999,999.80 (ops:603, 751). | Compute the basis from M20 paid invoices. |
| F13 | P1 | **Rebate payouts have no account, accrual or TDS.** Payout PEX/2026/00055 has no debit account; the `partner_rebate_payout` param is unset; `action_record_payout` takes a typed ref. | Accrue at approval; account + TDS; fail closed with no account. |
| F14 | P1 | **A lapsed brand authorisation blocks nothing.** Nothing outside cd_partner reads it; warnings are at 30 days only (spec: 180/90/30); M37 `fix.brand` keeps a second register. | Gate M09/M01 brand work on a valid authorisation. |
| F15 | P1 | **No real person can run the partner flows.** Every cd_partner role has 0 non-admin holders; referral manager has 0 (admin included). | Owner. |
| F16 | P1 | **Reseller pricing ignores M11** (a typed 1.00 was accepted), and a draw creates no stock move and no invoice (cap:1463-1586). | Price via M11; the draw moves stock and bills. |
| F17 | P2 | **ref_02 is only partly closed:** a child contact of a customer under an open referral is accepted (fp:747-753 compares exact ids). | Compare commercial_partner_id. |
| F18 | P2 | Any internal user can create a referral for any partner. | |
| F19 | P2 | **The royalty base is VAT-inclusive cash** (`amount_settled_bdt`), 15% over, with refunds not netted; there is no royalty income account. | |
| F20 | P2 | **M40 brand partners are not M09's recovery parties:** `fix.partner` has no brand link. | |
| F21 | P2 | 13 packs and the KPI hook use sudo `search([])`: no company, no dates. | |
| F22 | P2 | **KPIs measure the wrong thing:** "Brand Partners" counts authorisations; "Partner Revenue" is commission expense; the audit calendar ignores `fix.brand.audit`; the health score formula is not FR-PCM-018. | |
| F23 | P2 | Deal conflict checks are partial, and there is no M07 hand-off. | |
| F24 | P2 | No dormant/probation/exiting states; suspension does not revoke the portal. | |
| F25 | P2 | Payable 32656556 is not reconcilable; TDS goes to 200905 with no M51 record. | |
| F26 | P2 | Two MDF mechanisms exist. | |
| F27 | P2 | M40 child models have no company_id. | |
| F28 | P2 | The alliance `benefit_ref` is free text. | |
| F29 | P3 | A portal call to a manager action raises an AccessError on res.groups. | |
| F30 | P3 | Tier changes have no effective date. | |

**Verified as holding:**
- The portal cannot set its own rate or tier.
- The portal cannot create a referral with a state or amount, or for another partner.
- The portal cannot convert a referral or earn commission.
- Exact-duplicate and self referrals are refused.
- The referral posts Dr 500113 1,000 / Cr 32656556 1,000, with TDS of 150.

## Cross-area
- **X1 (P2): 96/96 A04 report packs ignore date_from/date_to.** 12 screens still show a period picker and print it on the PDF/XLSX.
- **X2 (P2): ~60 packs and 7 of 9 KPI hooks read sudo with no company filter** (against `p03_generic_api.py:577-580`).
- **X3 (P1): 84 of 92 A04 events have no consumer.** The ones that move money or gate work:
  - franchise_activated;
  - warranty_claim remitted / written_off / appeal_decided;
  - protection_claim.settled;
  - marketplace.chargeback_lost;
  - contract.entitlement_topped_up and contract.terminated;
  - subscription autopay_succeeded / adjustment_approved / proration_approved;
  - partner.authorisation_expiring.
- **X4 (P0): the M09 claim receivable dead-letters.** `fix_a04_claim_consumer.py:96-108` needs a res.partner whose ref equals the brand code: 0/161.
- **X5 (P2): company isolation gaps.**
  - 5 models have company_id but no rule: fix.claim.writeoff, fix.device.model, fix.rate.card, fix.sales.proforma.line, fix.warranty.product.
  - 63 A04 models have no company_id at all.
- **X6 (P1): approval roles nobody holds.**
  - 0 holders: warranty clerk/officer, storefront, subscription officer, catalogue officer/publisher, contract legal, tender committee, marketplace roles, M40.
  - The pricing officer and the releaser are the same user (emdadul.haq).
  - DOFA holders: T1 68, T2 48, T3 9, T4 2, T5 1.
- **X7 (P3): static integrity is clean.** 470 screens checked; the only defect is the M11 discount approval form offering the guarded `state` (`writable.py:444`).
- **X8 (P3): the export bar is present.** 96 packs and 9 KPI hooks run without error, but KPI exceptions are swallowed silently.

## Facts on fix_real_a04
- Data: 0 M40 records; 161 brands.
- Settlement accounts:
  - commission expense 500113;
  - payable 32656556 (not reconcilable);
  - TDS 200905;
  - clearing 101404 (a legacy POS bank account);
  - payout journal PBLM.
- Unset parameters: `partner_rebate_payout`, `lead_attribution_days`.
- Missing accounts: 101000, 200200, 210100, and no royalty income account.
- The one partner scheme has rate 0 and TDS 10%.
- Event outbox: 18,556 pending and 504 failed, none of them A04 types.

# Approval authority in force today — annex to decision D8 (A11 ERP audit)

Produced 2026-11-23 for the owner decision on the Delegation of Authority (A11 audit,
`audit_analysis/A11_ERP_AUDIT_DECISIONS_2026-11-23.md`, decision D8).

**What this is.** For every document type whose approval depends on an amount, the bands
the system applies RIGHT NOW and the approver tier each band requires. It was read from
the authority engine itself on a private copy of the live database
(`scratch/a11_deep/dofa_effective.py` → `evidence/dofa_effective.out`). Nothing was changed.

**How to read it.** Tiers: T1 team lead / contact-centre supervisor (20 holders on live) ·
T2 branch / operations manager (42) · T3 CX / commercial director (7) · T4 CFO / CCO / COO (3)
· T5 managing director / board (1). "No approval" means the record passes without anyone
signing. "Developer default" means the band was written in code by the build team and nobody
in the business has chosen it; only a "formal ladder" row has been ruled and countersigned.

**What to do.** Mark each line *accept* or *change* (new bands and/or tiers). Accepted lines
are loaded as formal ladders in one pass (no behaviour change); changed lines are loaded as
the new ruling and take effect from the date you give.

| Document | Decision | Amount band → approver (as in force today) | Formal ladder? |
|---|---|---|---|
| AR Write-off (`fix.ar.writeoff`) | ar_writeoff | up to ৳ 10,000 → **no approval** · above ৳ 10,000 → T2 branch / operations manager | no (developer default) |
| Asset Disposal / Write-Off (`fix.asset.disposal`) | asset_disposal | up to ৳ 25,000 → T2 branch / operations manager · above ৳ 25,000 → T4 CFO / CCO / COO | no (developer default) |
| Asset Revaluation / Impairment (`fix.asset.revaluation`) | asset_revaluation | any amount → T4 CFO / CCO / COO | no (developer default) |
| Budget Version (`fix.budget.version`) | budget_version | up to ৳ 10,000,000 → T4 CFO / CCO / COO · above ৳ 10,000,000 → T5 managing director / board | no (developer default) |
| Marketing Campaign (`fix.campaign`) | campaign_budget | up to ৳ 50,000 → **no approval** · ৳ 50,000 – 200,000 → T3 CX / commercial director · above ৳ 200,000 → T4 CFO / CCO / COO | no (developer default) |
| Capex Request (`fix.capex.request`) | capex_request | up to ৳ 50,000 → T2 branch / operations manager · ৳ 50,000 – 500,000 → T3 CX / commercial director · ৳ 500,000 – 2,000,000 → T4 CFO / CCO / COO · above ৳ 2,000,000 → T5 managing director / board | no (developer default) |
| Complaint (`fix.complaint`) | concession | up to ৳ 1,000 → T1 team lead / contact-centre supervisor · ৳ 1,000 – 5,000 → T2 branch / operations manager · ৳ 5,000 – 10,000 → T3 CX / commercial director · above ৳ 10,000 → T4 CFO / CCO / COO | **yes** |
| Contract (`fix.contract`) | contract_value | up to ৳ 50,000 → T1 team lead / contact-centre supervisor · ৳ 50,000 – 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Contract Amendment (`fix.contract.amendment`) | contract_amendment | up to ৳ 50,000 → T1 team lead / contact-centre supervisor · ৳ 50,000 – 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Contract Suspension / Termination (`fix.contract.termination`) | contract_termination | up to ৳ 500,000 → T3 CX / commercial director · ৳ 500,000 – 2,000,000 → T4 CFO / CCO / COO · above ৳ 2,000,000 → T5 managing director / board | no (developer default) |
| Credit Note (`fix.credit.note`) | credit_note | up to ৳ 10,000 → **no approval** · above ৳ 10,000 → T2 branch / operations manager | no (developer default) |
| Consignment Damage Claim (`fix.damage.claim`) | damage_claim | up to ৳ 15,000 → T2 branch / operations manager · ৳ 15,000 – 50,000 → T3 CX / commercial director · above ৳ 50,000 → T4 CFO / CCO / COO | no (developer default) |
| Test Equipment (`fix.equipment`) | equipment_writeoff | up to ৳ 25,000 → T2 branch / operations manager · above ৳ 25,000 → T4 CFO / CCO / COO | no (developer default) |
| Repair Estimate (`fix.estimate`) | estimate_discount | up to % 10 → **no approval** · % 10 – 20 → T2 branch / operations manager · % 20 – 35 → T3 CX / commercial director · above % 35 → T4 CFO / CCO / COO | no (developer default) |
| Facility Work Order (`fix.facility.work.order`) | facility_wo_spend | up to ৳ 10,000 → T2 branch / operations manager · ৳ 10,000 – 50,000 → T3 CX / commercial director · above ৳ 50,000 → T4 CFO / CCO / COO | no (developer default) |
| Letter of Credit (`fix.import.lc`) | import_lc | any amount → T4 CFO / CCO / COO | no (developer default) |
| LC Amendment (`fix.import.lc.amendment`) | import_lc_amendment | any amount → T4 CFO / CCO / COO | no (developer default) |
| Manual Journal Approval (`fix.journal.approval`) | journal_entry | up to ৳ 500,000 → T2 branch / operations manager · ৳ 500,000 – 5,000,000 → T4 CFO / CCO / COO · above ৳ 5,000,000 → T5 managing director / board | no (developer default) |
| Loyalty Points Audit Ledger (`fix.loyalty.ledger`) | loyalty_adjustment | up to ৳ 500 → **no approval** · ৳ 500 – 2,000 → T2 branch / operations manager · ৳ 2,000 – 10,000 → T3 CX / commercial director · above ৳ 10,000 → T4 CFO / CCO / COO | **yes** |
| Loyalty Scheme (`fix.loyalty.scheme`) | loyalty_scheme | up to ৳ 50,000 → **no approval** · ৳ 50,000 – 200,000 → T3 CX / commercial director · ৳ 200,000 – 10,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Wallet Transaction (append-only) (`fix.loyalty.wallet.txn`) | - | up to ৳ 5,000 → **no approval** · ৳ 5,000 – 50,000 → T2 branch / operations manager · ৳ 50,000 – 200,000 → T3 CX / commercial director · above ৳ 200,000 → T4 CFO / CCO / COO | no (developer default) |
| MSP SLA Credit (`fix.msp.sla.credit`) | msp_sla_credit | any amount → T4 CFO / CCO / COO | no (developer default) |
| Partner Commission Rate Change (`fix.partner.rate.change`) | partner_commission_rate | any amount → T3 CX / commercial director | no (developer default) |
| Partner Rebate (`fix.partner.rebate`) | partner_rebate | up to ৳ 15,000 → T2 branch / operations manager · ৳ 15,000 – 50,000 → T3 CX / commercial director · above ৳ 50,000 → T4 CFO / CCO / COO | no (developer default) |
| Payment Execution (`fix.payment.execution`) | payment_release | up to ৳ 50,000 → T2 branch / operations manager · ৳ 50,000 – 500,000 → T3 CX / commercial director · ৳ 500,000 – 2,000,000 → T4 CFO / CCO / COO · above ৳ 2,000,000 → T5 managing director / board | no (developer default) |
| Payout Run / পরিশোধ চক্র (`fix.payout.run`) | payout_run | up to ৳ 2,000,000 → T2 branch / operations manager · above ৳ 2,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Price Floor (`fix.price.floor`) | pricing_floor_override | up to % 15 → T2 branch / operations manager · % 15 – 30 → T3 CX / commercial director · above % 30 → T4 CFO / CCO / COO | no (developer default) |
| Below-Floor Price Override (`fix.price.override`) | pricing_floor_override | up to % 15 → T2 branch / operations manager · % 15 – 30 → T3 CX / commercial director · above % 30 → T4 CFO / CCO / COO | no (developer default) |
| Project (`fix.project`) | other | up to ৳ 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Purchase Order (`fix.purchase.order`) | purchase_order | up to ৳ 50,000 → T2 branch / operations manager · ৳ 50,000 – 500,000 → T3 CX / commercial director · ৳ 500,000 – 2,000,000 → T4 CFO / CCO / COO · above ৳ 2,000,000 → T5 managing director / board | no (developer default) |
| Quotation (`fix.quotation`) | quotation | up to ৳ 25,000 → T1 team lead / contact-centre supervisor · ৳ 25,000 – 100,000 → T2 branch / operations manager · above ৳ 100,000 → T3 CX / commercial director | no (developer default) |
| Rental Fleet Asset (`fix.rental.asset`) | rental_asset_writeoff | up to ৳ 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Rental Damage Charge Approval (`fix.rental.charge.approval`) | rental_damage_charge | up to ৳ 50,000 → T1 team lead / contact-centre supervisor · ৳ 50,000 – 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Rental Damage (`fix.rental.damage`) | rental_loss_waiver | up to ৳ 50,000 → T1 team lead / contact-centre supervisor · ৳ 50,000 – 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Requisition (`fix.requisition`) | requisition | up to ৳ 50,000 → T2 branch / operations manager · ৳ 50,000 – 500,000 → T3 CX / commercial director · ৳ 500,000 – 2,000,000 → T4 CFO / CCO / COO · above ৳ 2,000,000 → T5 managing director / board | no (developer default) |
| Revenue Recognition Schedule (`fix.revenue.schedule`) | revenue_manual_schedule | any amount → T4 CFO / CCO / COO | no (developer default) |
| Site Infrastructure Asset (`fix.site.asset`) | site_asset_retirement | up to ৳ 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Site Charge (deposit, advance rent, licence fee, penalty) (`fix.site.charge`) | site_charge_settlement | up to ৳ 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Site Lease (`fix.site.lease`) | lease_modification | up to ৳ 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Site Open / Close Project (`fix.site.project`) | site_capex | up to ৳ 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Stock Count (`fix.stock.count`) | inventory_writeoff | up to ৳ 25,000 → **no approval** · above ৳ 25,000 → T4 CFO / CCO / COO | no (developer default) |
| Stock Quarantine / Scrap (`fix.stock.quarantine`) | inventory_writeoff | up to ৳ 25,000 → **no approval** · above ৳ 25,000 → T4 CFO / CCO / COO | no (developer default) |
| Storefront Return & Reverse Logistics (`fix.storefront.return`) | storefront_refund | up to ৳ 1,000 → T1 team lead / contact-centre supervisor · ৳ 1,000 – 5,000 → T2 branch / operations manager · ৳ 5,000 – 10,000 → T3 CX / commercial director · above ৳ 10,000 → T4 CFO / CCO / COO | no (developer default) |
| Storefront RMA Request (`fix.storefront.rma`) | storefront_refund | up to ৳ 1,000 → T1 team lead / contact-centre supervisor · ৳ 1,000 – 5,000 → T2 branch / operations manager · ৳ 5,000 – 10,000 → T3 CX / commercial director · above ৳ 10,000 → T4 CFO / CCO / COO | no (developer default) |
| Subscription Credit / Adjustment (`fix.subscription.adjustment`) | subscription_credit | up to ৳ 25,000 → T1 team lead / contact-centre supervisor · ৳ 25,000 – 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Subscription Proration (`fix.subscription.proration`) | subscription_credit | up to ৳ 25,000 → T1 team lead / contact-centre supervisor · ৳ 25,000 – 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Tender Bond (`fix.tender.bond`) | tender_bond | up to ৳ 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Trade-In Request (`fix.tradein.request`) | tradein_payout | up to ৳ 50,000 → T1 team lead / contact-centre supervisor · ৳ 50,000 – 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Vehicle Accident / Incident (`fix.vehicle.accident`) | vehicle_accident_settlement | up to ৳ 250,000 → T2 branch / operations manager · ৳ 250,000 – 1,000,000 → T3 CX / commercial director · above ৳ 1,000,000 → T4 CFO / CCO / COO | no (developer default) |
| Vehicle Disposal (`fix.vehicle.disposal`) | vehicle_disposal | any amount → T4 CFO / CCO / COO | no (developer default) |
| Traffic Fine / Penalty (`fix.vehicle.penalty`) | vehicle_penalty_decision | up to ৳ 10,000 → **no approval** · ৳ 10,000 – 50,000 → T3 CX / commercial director · above ৳ 50,000 → T4 CFO / CCO / COO | no (developer default) |
| Workshop Repair Job (`fix.workshop.job`) | workshop_ber | up to ৳ 10,000 → T2 branch / operations manager · ৳ 10,000 – 50,000 → T3 CX / commercial director · above ৳ 50,000 → T4 CFO / CCO / COO | no (developer default) |
| Workshop Consumed Part Line (`fix.workshop.part.line`) | workshop_extra_parts | up to ৳ 10,000 → T2 branch / operations manager · ৳ 10,000 – 50,000 → T3 CX / commercial director · above ৳ 50,000 → T4 CFO / CCO / COO | no (developer default) |

**Bands that need no approval at all (10):**

- AR Write-off — up to 10,000
- Marketing Campaign — up to 50,000
- Credit Note — up to 10,000
- Repair Estimate — up to 10
- Loyalty Points Audit Ledger — up to 500
- Loyalty Scheme — up to 50,000
- Wallet Transaction (append-only) — up to 5,000
- Stock Count — up to 25,000
- Stock Quarantine / Scrap — up to 25,000
- Traffic Fine / Penalty — up to 10,000

## Points that deserve a second look

1. **No approval at all for real money.** Credit notes up to ৳10,000, AR write-offs up to
   ৳10,000, stock write-offs (count / quarantine-scrap) up to ৳25,000, loyalty wallet
   transactions up to ৳5,000, a loyalty scheme up to ৳50,000, a marketing campaign up to
   ৳50,000, traffic fines up to ৳10,000 and an estimate discount of up to 10% all pass with
   no signature.
2. **Large amounts at low tiers.** A payout run up to ৳2,000,000 and a manual journal up to
   ৳500,000 need only a branch / operations manager (T2); quotations up to ৳25,000 and
   rental damage waivers up to ৳50,000 need only a team lead (T1).
3. **Only two of 53 are formally ruled** (complaint concessions, loyalty point
   adjustments). The other 51 are developer defaults.
4. **Decisions outside this table** carry no amount bands and follow their own logic:
   expense claims (two-step, ৳25,000 parameter), inventory write-off approvals
   (৳5,000 parameter), general-ledger posting rules (maker–checker, no amount), and about
   129 further "approve" actions across the ERP that use their own inline role checks
   rather than the unified approval trail.


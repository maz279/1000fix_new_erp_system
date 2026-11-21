# A04 readiness probe on fix_real_a04 (copy of fix_real, A04 modules upgraded from the committed tree, rolled back), 21 Nov 2026

```
1 check_sale_price 1.00 quotation refused: HON-TAB-LCM-9706ADBH cannot be sold at BDT 1.00: the floor is BDT 2229.24 (M15 cost 2229.24 + 0% margin floor)
1 check_sale_price 1.00 service refused: HON-TAB-LCM-9706ADBH cannot be sold at BDT 1.00: the floor is BDT 2229.24 (M15 cost 2229.24 + 0% margin floor)
1 check_sale_price 1.00 storefront refused: Cannot sell HON-TAB-LCM-9706ADBH on the storefront channel: no released M11 price for HON-TAB-LCM-9706ADBH on 
2 released rate cards 0
3 ageing cron 193 True model._cron_monthly_snapshot()
3 ageing snapshots captured 1 {datetime.date(2026, 10, 31)}
4 reports ran 96 errors 0
5 param cd_partner.account_code.royalty_income = (unset)
5 param cd_partner.account_code.franchise_fee_income = (unset)
5 param cd_settlement_ext.account_code.partner_rebate_payout = (unset)
5 param cd_settlement_ext.account_code.partner_mdf_expense = (unset)
5 param cd_billing_engine.account_code.contract_revenue_amc = (unset)
5 param cd_quotation.account_code.bond_margin = (unset)
5 param cd_storefront.payment_timeout_minutes = (unset)
5 param cd_contract_core.labour_cost_per_hour = (unset)
5 param cd_rate_card.margin_floor_pct = (unset)
5 brands with billing partner 0 of 161
```

Script: lead_readiness.py (scratch). Upgrade of 18 modules on the fix_real copy: exit 0, 0 ERROR lines.

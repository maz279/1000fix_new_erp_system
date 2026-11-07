# cd_demand_plan 19.0.0.3.0 (A06 final pass, M43 step 3): segments and reviews
# gain company_id. Existing rows take their part's company, else the company of
# the record's creator; the two company-scoped packs then read them. A released
# plan whose requisition M16 has already converted moves to Converted.
def migrate(cr, version):
    if not version:
        return
    cr.execute(
        """
        UPDATE fix_demand_segment s SET company_id = p.company_id
          FROM fix_spare_part p
         WHERE s.part_id = p.id AND s.company_id IS NULL AND p.company_id IS NOT NULL
        """
    )
    cr.execute(
        """
        UPDATE fix_demand_segment t SET company_id = u.company_id
          FROM res_users u
         WHERE t.create_uid = u.id AND t.company_id IS NULL
        """
    )
    cr.execute(
        """
        UPDATE fix_demand_review t SET company_id = u.company_id
          FROM res_users u
         WHERE t.create_uid = u.id AND t.company_id IS NULL
        """
    )
    cr.execute(
        """
        UPDATE fix_demand_plan pl
           SET state = 'converted', purchase_order_id = r.purchase_order_id
          FROM fix_requisition r
         WHERE pl.pr_requisition_id = r.id AND pl.state = 'released' AND r.state = 'converted'
        """
    )

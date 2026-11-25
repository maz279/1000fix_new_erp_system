# A05 workflow audit M14-5 (E7): provenance rows were born "NID verified",
# "NEIR checked" and "Valid & Whitelisted" by DEFAULT, and no NEIR lookup has
# ever existed. Those values were never checks, so they are reset to what is
# true: unchecked and unverified. The rows and their other evidence stay.
def migrate(cr, version):
    if not version:
        return
    cr.execute(
        """
        UPDATE fix_tradein_provenance
           SET btrc_neir_status = 'unchecked',
               btrc_neir_checked = FALSE,
               customer_nid_verified = FALSE
         WHERE btrc_neir_status = 'valid'
            OR btrc_neir_checked
            OR customer_nid_verified
        """
    )

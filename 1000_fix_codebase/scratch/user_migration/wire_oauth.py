# ruff: noqa: F821, UP031, S608, E501, S101, SIM105  (odoo-bin shell script: env/cr are injected at runtime; table/column identifiers come from the staging CSVs and information_schema, not user input)
# Loader 5 — auth_oauth provider wiring on fix_real (odoo shell, superuser).
# Odoo 19 auth_oauth uses public clients: no secret is stored, the token
# exchange relies on the Keycloak standard flow. Local password login stays
# available alongside the SSO button.
env.cr.execute("SAVEPOINT oauth_l5")
try:
    Prov = env["auth.oauth.provider"].sudo()
    BASE = "http://localhost:8080/realms/1000fix/protocol/openid-connect"
    existing = Prov.search([("client_id", "=", "odoo-erp")], limit=1)
    vals = {
        "name": "1000FiX SSO (Keycloak)",
        "client_id": "odoo-erp",
        "auth_endpoint": BASE + "/auth",
        "validation_endpoint": BASE + "/userinfo",
        "scope": "openid profile email",
        "body": "1000FiX SSO",
        "enabled": True,
        "sequence": 5,
    }
    if existing:
        existing.write(vals)
        print("provider updated:", existing.name)
    else:
        p = Prov.create(vals)
        print("provider created:", p.name, p.id)
    env.cr.execute("COMMIT")
    print("OAUTH PROVIDER COMMIT OK")
except Exception as exc:
    env.cr.execute("ROLLBACK TO SAVEPOINT oauth_l5")
    print("OAUTH FAILED:", exc)
    raise

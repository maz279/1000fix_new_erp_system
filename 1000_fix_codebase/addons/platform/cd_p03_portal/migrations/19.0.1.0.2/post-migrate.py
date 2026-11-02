# D365 backend home reconciliation (user directive 2026-10-29: every
# back-office entry renders the D365 Operations Workspace, never old-Odoo
# chrome).
#
# End state, idempotent from any prior version:
#   - /odoo/operations → Operations Workspace (tag p03_workspace, path
#     "operations"); admin's home action, so /odoo and login land there.
#     From 19.0.1.0.3 the Team Chat serves at its stock /odoo/discuss URL,
#     Fluent-skinned by the cd_d365_chrome module (the interim redirect
#     controller was removed once the chat itself carried the D365 skin).
#   - mail.action_discuss stays exactly as vendor mail ships it (native
#     tag "mail.action_discuss", path "discuss") — its XML re-asserts those
#     values on every mail upgrade, so this module never contests them.
#     The restore below only guards databases that still carry the
#     pre-19.0.1.0.1 tag override.
#   - admin + __system__ home action = Operations Workspace (fixes
#     databases where res_users.action_id is NULL, which made /odoo fall
#     back to native Discuss)
from odoo import SUPERUSER_ID, api

NATIVE_DISCUSS = {
    "name": "Discuss",
    "tag": "mail.action_discuss",
    "path": "discuss",
    "params": {"default_active_id": "mail.box_inbox"},
}


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})

    discuss = env.ref("mail.action_discuss", raise_if_not_found=False)
    if discuss and (discuss.tag != "mail.action_discuss" or discuss.path != "discuss"):
        discuss.write(NATIVE_DISCUSS)

    workspace = env.ref("cd_p03_portal.action_p03_workspace", raise_if_not_found=False)
    if workspace and workspace.path != "operations":
        workspace.write({"path": "operations"})

    if workspace:
        env["res.users"].search([("login", "in", ["admin", "__system__"])]).write(
            {"action_id": workspace.id}
        )

# cd_portal_embed — the frame policy that lets the Next.js portals embed the
# P03 workspace.
#
# This module exists to swap Odoo's ``X-Frame-Options: DENY`` for a CSP
# ``frame-ancestors`` allow-list on the web-client bootstrap. Both halves are
# security-relevant and neither is visible from the source: that the header is
# actually removed and replaced on a 200, that a redirect is left alone (so the
# login bounce keeps stock protection), and that the production allow-list comes
# from the system parameter rather than the dev default.
from __future__ import annotations

from types import SimpleNamespace
from unittest import mock

import pytest
from odoo.addons.cd_portal_embed.controllers import home as embed_home
from odoo.http import Response

PARAM = "portal_embed.frame_ancestors"


def _Response(status_code=200, headers=None):
    """A real werkzeug/Odoo Response: the @http.route wrapper validates what the
    handler returns, so a stub object is rejected before the override runs."""
    response = Response(status=status_code)
    for key, value in (headers or {}).items():
        response.headers[key] = value
    return response


# ------------------------------------------------------------------ allow-list


def test_the_allow_list_falls_back_to_the_loopback_dev_origins(odoo_env):
    odoo_env["ir.config_parameter"].sudo().set_param(PARAM, "")
    with mock.patch.object(embed_home.http, "request", SimpleNamespace(env=odoo_env)):
        assert embed_home._frame_ancestors() == embed_home.DEFAULT_FRAME_ANCESTORS


def test_the_system_parameter_overrides_the_dev_default(odoo_env):
    """Production narrows the allow-list; if the parameter were ignored, every
    deployment would keep trusting localhost:3000."""
    odoo_env["ir.config_parameter"].sudo().set_param(
        PARAM, "https://portal.1000fix.com, https://staging.1000fix.com"
    )
    with mock.patch.object(embed_home.http, "request", SimpleNamespace(env=odoo_env)):
        assert embed_home._frame_ancestors() == [
            "https://portal.1000fix.com",
            "https://staging.1000fix.com",
        ]


@pytest.mark.parametrize("raw", ["   ", ",", " , , "])
def test_a_blank_or_separator_only_parameter_is_not_an_empty_allow_list(odoo_env, raw):
    """An empty list would emit ``frame-ancestors 'self'`` and silently break
    every portal pane, so a meaningless value must fall back, not pass through."""
    odoo_env["ir.config_parameter"].sudo().set_param(PARAM, raw)
    with mock.patch.object(embed_home.http, "request", SimpleNamespace(env=odoo_env)):
        assert embed_home._frame_ancestors() == embed_home.DEFAULT_FRAME_ANCESTORS


# ------------------------------------------------------------------ the swap


def _call_web_client(odoo_env, response):
    controller = embed_home.HomePortalEmbed()
    with (
        mock.patch.object(embed_home.Home, "web_client", return_value=response),
        mock.patch.object(embed_home.http, "request", SimpleNamespace(env=odoo_env)),
    ):
        return controller.web_client()


def test_a_200_bootstrap_loses_x_frame_options_and_gains_frame_ancestors(odoo_env):
    odoo_env["ir.config_parameter"].sudo().set_param(PARAM, "https://portal.1000fix.com")
    out = _call_web_client(odoo_env, _Response(200, {"X-Frame-Options": "DENY"}))

    assert "X-Frame-Options" not in out.headers, "DENY would block the portal pane"
    assert out.headers["Content-Security-Policy"] == (
        "frame-ancestors 'self' https://portal.1000fix.com"
    )


def test_a_redirect_keeps_stock_frame_protection(odoo_env):
    """Only the 200 bootstrap is relaxed. The login bounce must keep DENY, or the
    override would widen framing across every redirect the web client issues."""
    out = _call_web_client(odoo_env, _Response(303, {"X-Frame-Options": "DENY"}))

    assert out.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" not in out.headers


def test_the_policy_names_self_so_odoos_own_frames_keep_working(odoo_env):
    odoo_env["ir.config_parameter"].sudo().set_param(PARAM, "")
    out = _call_web_client(odoo_env, _Response(200, {"X-Frame-Options": "DENY"}))

    policy = out.headers["Content-Security-Policy"]
    assert policy.startswith("frame-ancestors 'self' ")
    for origin in embed_home.DEFAULT_FRAME_ANCESTORS:
        assert origin in policy

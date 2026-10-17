# D-034 — L6 Commercial Component: Cloud Telephony / CPaaS for Hotline 16743

| | |
|---|---|
| **Decision ID** | `D-034` |
| **Date** | 2026-10-17 (Milestone R05-M03-T01) |
| **Status** | ACCEPTED |
| **Deciders** | Chief Financial Officer (CFO), Chief Technology Officer (CTO), Chief Architect (`CA`) |
| **Allocating authority** (`DL-08`) | TSS §9 L6 Rule · `GV-003` Change Control · `IR-002` P07-M05-T01 |
| **Target Components** | `TC-070` Cloud Telephony / CPaaS · `INT-015` Telephony Integration · `M27` Contact Centre · `P10` Agent Console |
| **Budget Runway** | USD $200–$600 / month (seats + minutes allocation approved by CFO) |

---

## 1. Context & Regulatory Imperative
1000FiX Services Ltd operates Bangladesh's premier nation-wide after-sales repair platform. National Shortcode **Hotline 16743** receives thousands of inbound customer calls daily across 64 districts. Under BTRC (Bangladesh Telecommunication Regulatory Commission) regulations:
- Inbound shortcodes (5-digit `16XXX`) must terminate on licensed carrier gateways (BTCL, Grameenphone, Robi, Banglalink) with strict CLI (Caller Line Identification) validation and statutory intercept capability.
- PSTN interconnect requires carrier-grade E1/PRI trunks or licensed SIP trunks.

TSS §9 establishes that any L6 commercial software selection requires:
1. A written Open-Source Software (OSS) alternative evaluation.
2. CFO commercial authorization and budget allocation.
3. Architectural mediation preventing vendor lock-in.

---

## 2. Written Open-Source Software (OSS) Alternative Review

| Candidate | Architecture | Telecom Interconnect Feasibility | Assessment |
|---|---|---|---|
| **Asterisk / FreePBX** | Open-source PBX (GPL-2.0) | Requires physical E1/PRI cards or carrier-licensed SIP trunks, session border controllers (SBC), and direct PSTN interconnect in Dhaka datacenter | **Viable for PBX switching, but blocked by carrier interconnect gap**: The Company does not hold a BTRC carrier license nor maintain a 24/7 telecommunications hardware engineering team. Bare-metal trunk maintenance creates unacceptable outage risk for 16743. |
| **Kamailio / OpenSIPS** | Open-source SIP proxy (GPL-2.0) | High-throughput SIP signaling only; no native IVR, recording transcoding, or embedded agent WebRTC SDK | Insufficient standalone capabilities; still requires licensed carrier upstream termination. |
| **Licensed Cloud CPaaS (Selected)** | Carrier-grade cloud telephony platform | Pre-integrated BTRC licensed carrier interconnect, nationwide 16743 shortcode termination, managed IVR, audio recording compliance | **Selected**: Fully complies with Bangladesh regulatory interconnect, provides embedded softphone SDK for P10 console, abstracts telecom complexity. |

---

## 3. Decision

1. **Adopt Licensed CPaaS Provider (L6 / TC-070)** for Hotline **16743** inbound call routing, IVR tree management, agent queue ACD, and call recording storage.
2. **Abstracted Telephony Integration SEAM**: All communication with the CPaaS is strictly abstracted behind the `fix_softphone_*` parameters in Odoo `ir.config_parameter` (e.g. `fix_softphone_ws`, `fix_softphone_sip_realm`, `fix_softphone_dial_prefix`).
3. **Zero Host Literals or Credentials in Source**: API tokens, WebRTC session secrets, and SIP credentials reside strictly on the agent client / secure environment variables, never committed to git.
4. **Resilience & Degraded Mode**: In case of CPaaS unavailability, P10 agent console automatically degrades to non-voice channels (WhatsApp, Web Chat, Email) while maintaining full operational continuity.

---

## 4. Consequences & Annual Review

- **Cost Impact**: Monthly recurring cost of USD $200–$600 accounted for under Operational Expenditure (OpEx).
- **Vendor Portability**: Call control logic in `cd_contact_centre` communicates via standard webhook formats (`/contact/telephony/webhook`), ensuring zero lock-in if the carrier provider is renegotiated.
- **Review Cadence**: Annual commercial review aligned with `D-030` software currency ritual.

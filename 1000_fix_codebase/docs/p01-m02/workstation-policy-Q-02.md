# Q-02 policy position — Company-issued, disk-encrypted developer workstations

**Task `P01-M02-T08`** · Written 2026-10-01 · Author: Security Lead (`SL`)
**Status: POLICY POSITION ADOPTED for the programme.** Answers `BE-001` §11
`Q-02`. Blocking for `DE-12` enforceability.

---

## 1. Position (the answer to Q-02)

**Yes — workstations are Company-issued and full-disk-encrypted, and no
developer begins work on an unencrypted machine.**

1. **Issuance:** every machine that touches programme code or data is
   Company-issued and asset-registered. BYOD is not permitted for
   development work; personal machines may hold no repository clone and no
   environment credentials.
2. **Encryption:** the OS volume is encrypted at rest — on the Windows-native
   baseline (`D-WS-001`) this is **BitLocker with TPM protection**; recovery
   keys are escrowed to the Company directory, not held only by the user.
   (The Ubuntu alternative this policy supersedes specified LUKS at install.)
3. **The control it carries:** `DE-12` — *"a developer workstation never
   holds production data"* — is enforceable only under this position. With
   it, the residual risk of a lost/stolen machine is an encrypted device,
   not a notifiable event.

## 2. Evidence already on record (this programme, 2026-09-30/10-01)

The workstation baseline tooling (`P02-M01`, native Windows) enforces the
encryption check as task **T03** of `verify-workstation.ps1`:

- The baseline is **RED until BitLocker is on** (`DE-12`/`SC-009`/`DE-19`);
  the dev machine DESKTOP-CVE1HTI carries an open T03 operator action at the
  date of this policy (definitive elevated query 2026-09-30: Protection Off).
- Encryption is deliberately **never enabled silently by tooling** — it is a
  provisioning action with TPM/reboot and recovery-key implications; the
  operator runs `manage-bde -on C:` with the key escrowed per §1.2 above.

## 3. Fleet mechanics (owner: `SL`, with IT)

| Mechanism | Rule |
|---|---|
| Provisioning | BitLocker enabled at OOBE/imaging time for every new machine (the `D-WS-001` §5 trigger names BitLocker-on-OOBE policy) |
| Verification | `verify-workstation.ps1` T03 green per machine, per joiner (`DE-21` onboarding SLA); re-run after any OS service event |
| Exception | None for the OS volume. A machine that cannot encrypt (e.g. unsupported TPM) is not a developer machine |
| Consumer-cloud backups | Prohibited for any folder containing repository clones or environment configuration (`DE-15`) |

## 4. Standing consequence

An unencrypted workstation found at any gate is treated as a **security
incident, not a setup defect**: the machine is quarantined from programme
networks until encrypted, and any data exposure is assessed against PDPA
notification duties (the notifiable-event framing of the residency ruling,
`P01-M02-T03` context).

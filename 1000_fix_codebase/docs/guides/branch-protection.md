# Branch protection — apply at first push (P02-M03-T05)

**Configure BEFORE the first feature branch, not after** (roadmap's own
instruction). The declarative form is [`.github/settings.yml`](../settings.yml)
(Probot Settings format — applied automatically when the repo lands on the
Company host with the Settings app). The manual equivalent:

```bash
# develop (integration branch: 1 review, status checks, linear history)
gh api -X PUT repos/ORG/1000fix-erp/branches/develop/protection \
  -f required_pull_request_reviews.required_approving_review_count=1 \
  -f required_pull_request_reviews.dismiss_stale_reviews=true \
  -f required_status_checks.strict=true \
  -f required_status_checks.checks[]='precommit' \
  -f required_status_checks.checks[]='lint-type' \
  -f required_status_checks.checks[]='model-registry' \
  -f required_status_checks.checks[]='unit' \
  -f required_status_checks.checks[]='architecture' \
  -f enforce_admins=false -f allow_force_pushes=false -f allow_deletions=false \
  -f required_signatures=true

# main (production: 2 reviews incl. code owner, ALL pre-merge stages)
gh api -X PUT repos/ORG/1000fix-erp/branches/main/protection \
  -f required_pull_request_reviews.required_approving_review_count=2 \
  -f required_pull_request_reviews.require_code_owner_reviews=true \
  ...same checks plus contract/event/security/localisation/bundle/accessibility...
```

## Rules encoded (BE-003 §3.3)

| Rule | main | develop |
|---|---|---|
| Required approvals | 2, code-owner, stale-dismissed | 1, code-owner, stale-dismissed |
| Required status checks | all 11 pre-merge stages | 5 core stages |
| Strict (up-to-date) | yes | yes |
| Signed commits | **yes** (P02-M02-T08 precondition) | **yes** |
| Linear history | squash/rebase only; merge-commit disabled | same |
| Force push / delete | **never** | **never** |
| Enforce for admins | yes | no (break-glass path recorded in GV-003) |

**Signing setup (per developer, before the first PR):**
`git config commit.gpgsign true` + a key uploaded to the host — or SSH
signing (`git config gpg.format ssh`). `setup-toolchains.ps1` reminds; the
protection rule enforces.

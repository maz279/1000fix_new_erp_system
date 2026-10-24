---
id: MM-012
title: Digital Asset Management and Naming Standard
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Brand Lead
author: Brand with Platform Engineering, Programme Content Lead, Legal & Compliance and Security
reviewers: [Brand Lead, Chief Technology Officer, Programme Content Lead, Legal Counsel, Chief Data Officer, Design System Lead, Localisation Lead, Content Design Lead, Quality Manager]
approver: Content Design Lead with Brand Lead
content_class: D
purpose: >
  The repository, naming, versioning, rights and retirement standard for every asset the eleven
  other MM briefs produce. CG-005 governs content identifiers and file names; it does not reach
  assets, which outnumber content files by an order of magnitude, carry licences that expire,
  contain people who can withdraw consent, and are embedded in documents already issued. Without
  one standard the set becomes unfindable within a year, un-relicensable, and unable to answer the
  two questions that matter most: which assets contain this person, and which assets is this
  document made from. Neither can be answered retrospectively.
traces_to: [CG-005, CG-006, CG-008, CG-010, CG-011, CG-012, CG-013, LG-008, LG-009, LG-010, LG-012, LG-021, RP-014, DT-001, DT-044, EO-012, MM-001, MM-002, MM-003, MM-004, MM-005, MM-006, MM-007, MM-008, MM-009, MM-010, MM-011, TR-024, OP-006, OP-011, M24, M60, 05-02 §10, 05-04 §4, 05-06 NFR-086]
priority: P2
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-005_Content_ID_and_Naming_Convention.md §4 file naming, ID-08 no spaces ampersands or non-ASCII in any path, ID-09 fixed case, §5 counterpart files CF-01…CF-04 including the assets/ subfolder convention, §9 folder naming and the three-level depth limit
    verified: 2026-08-18
    class: P1
  - source: project_content/19_Multimedia_and_Asset_Specs/MM-009_Photography_Brief_Branches_Workshop_and_Field.md PH-43 — consent withdrawal triggers withdrawal of every asset containing that person and the repository must answer "which published assets contain this person" in one query; PH-04 time-bounded consent; PH-36 release status in IPTC Extension
    verified: 2026-08-18
    class: P1
  - source: project_content/19_Multimedia_and_Asset_Specs/MM-011_Email_and_HTML_Asset_Specification.md EA-37 a published asset URL is immutable, EA-39 the transactional email path is excluded from retirement deletion
    verified: 2026-08-18
    class: P1
  - source: project_content/05_Document_and_Print_Templates/DT-001_Document_Template_Standard_and_Branding_Rules.md §9.3 the re-render prohibition — a statutory document is a fact about a moment and the archived rendition is the evidential copy
    verified: 2026-08-18
    class: P1
  - source: IPTC Photo Metadata Standard 2024.1 — IPTC Core and IPTC Extension carried in XMP; Core supplies creator, credit line, copyright notice, rights usage terms and web statement of rights; Extension supplies model release status and identifiers, property release status and licensor detail
    verified: 2026-08-18
    class: P2
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02 §10 data classification S0–S3 and the S3 field inventory; 05-04 §4 the restricted T5 access tier
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Digital Asset Management and Naming Standard

| Item | Value |
|---|---|
| Governs | Every asset produced under `MM-001` … `MM-011`, and every asset embedded in content |
| Identifier authority | [`CG-005`](../00_Content_Governance_and_Standards/CG-005_Content_ID_and_Naming_Convention.md) — **content IDs; this file extends it to assets** |
| Audience | Brand, Platform Engineering, Design System, Content Design, Legal, anyone commissioning media |
| Language | English |
| Wave | W1 · Months 1–4 (`06-01` §3) |
| Content class | **D** — user-facing (`CG-002` §4.1) |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order. The `CG-009` `MM` **deliverable specification table** — here the
> **asset record schema**, since this file's deliverable is the register itself — is **§4.9**.
> §7 Open Items added per category convention.

---

## 1. Purpose

`CG-005` is complete on **content identifiers**: ten rules, twenty-one category codes, permanent
IDs never reused, a retirement log, and a counterpart convention in §5 that covers Bengali
versions, loadable data, workbooks and *"rendered assets"* in an `assets/` folder beside the
owning file.

**That convention was written for a handful of specimens beside a specification. It does not reach
the asset estate this category creates.**

| `CG-005` §5 assumes | Category 19 produces |
|---|---|
| An asset belongs to one content file | An icon belongs to twelve portals; a photograph appears in six kinds of material |
| An asset sits in the repository | Videos, photography masters and camera raw do not belong in a documentation repository |
| An asset is a file | An asset is a **file plus a licence, a consent, a release status, a version history and a set of derivatives** |
| An asset is stable | A licence expires; a consent is withdrawn; a screenshot is orphaned by a release |
| Naming is enough to find it | **At this volume it is not** |

**The two questions the register exists to answer**, neither of which can be reconstructed later:

> **1. Which published assets contain this person?** `MM-009` `PH-43` requires an answer *in one
> query*, because `LG-008` `CN-R3` makes consent withdrawal **immediately** effective. A withdrawal
> that takes three weeks to trace is a withdrawal that was not honoured.
>
> **2. Which assets is this document made from?** `DT-001` §9.3 makes the archived rendition the
> evidential copy; `MM-011` `EA-37` makes a published asset URL immutable. **Changing an asset
> changes documents already issued**, and the register is what makes that visible before it
> happens rather than after.

**Consequence of absence (`CP-03`).** The register's own justification: *"Thousands of assets
across nine waves become unfindable within a year without a naming and rights standard."* Worse
than unfindable — **unlicensable, unwithdrawable and unattributable**, with `EO-012` already
recording that it *"cannot cite a repository standard (`MM-012`, unwritten)"* for assets it issues
to external partners.

**What this file is not.** It is not `CG-005` (it extends it), not the production specifications
(`MM-001`…`MM-011`), not the document archive (`M24`), and not a product choice — §4.2 states
requirements, not a vendor.

---

## 2. Scope

**In scope.** What is an asset and what is not; where assets live and the boundary with the
content repository and `M24`; the asset naming standard; versioning and immutability; the rights
and consent record; classification and access; retention, retirement and withdrawal; findability;
the asset record schema; and rules `DA-01`…`DA-34`.

**Out of scope.**

| Subject | Owned by |
|---|---|
| Content identifiers, content file naming, folder naming | [`CG-005`](../00_Content_Governance_and_Standards/CG-005_Content_ID_and_Naming_Convention.md) — **cited, never re-decided** |
| Content lifecycle states and versioning of content | [`CG-006`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md) |
| What a compliant asset is, per class | [`MM-001`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) … [`MM-011`](MM-011_Email_and_HTML_Asset_Specification.md) |
| Consent validity and lawful basis | [`LG-008`](../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md); obtained under [`MM-009`](MM-009_Photography_Brief_Branches_Workshop_and_Field.md) §4.2 |
| Retention periods | [`LG-009`](../10_Legal_Policy_and_Compliance/LG-009_Data_Retention_and_Deletion_Schedule.md) |
| Issued and archived business documents | `M24` — **an issued invoice is not an asset** (`DA-02`) |
| Export watermarking and confidentiality marking of reports | [`RP-014`](../14_Reporting_Analytics_and_KPI/RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md) |
| Partner and co-branding permissions | [`EO-012`](../18_Ecosystem_Onboarding_Content/EO-012_Co_Marketing_and_Co_Branding_Asset_Guide.md) |
| The 1000FiX master identity | **No file holds it** — `MM-001` §4.12 and `O-06` here |

---

## 3. Audience

| Reader | Uses it for | Reads it |
|---|---|---|
| **Anyone commissioning media** | Where a delivery goes and what record must exist before it is used | Before commissioning |
| **Platform Engineering** | The repository requirements, the pipeline, the immutability guarantee | At build |
| **Brand Lead** | The register they own | Continuously |
| **Legal Counsel / Chief Data Officer** | §4.5 rights and §4.7 withdrawal — the two obligations that make this a compliance record | At review, and at every withdrawal |
| **Design System** | Library versioning and the release record | Per release |
| **Content authors** | How to reference an asset so it stays referenced | Per file |
| **External partners** | Via `EO-012`, what they receive and under what terms | At issue |

---

## 4. Content

### 4.1 What is an asset

| Is an asset | Is not an asset |
|---|---|
| Every deliverable of `MM-001` §4.1's eleven classes | **An issued business document** — that is `M24` (`DA-02`) |
| A specimen or worked example | A content markdown file — that is `CG-005` |
| A design-system library release | A screenshot's **unredacted source** — that is destroyed (`MM-002` `SC-27`) |
| An editable source or project file | A draft nobody has accepted |
| A licence, consent or release record attached to an asset | Personal data held for an operational purpose — `LG-008` |

| # | Rule |
|---|---|
| **DA-01** | **An asset exists in the register or it does not exist.** An asset used in published content with no register record is unmanaged and is withdrawn until one is created — the `CF-02` principle applied to media |
| **DA-02** | **An issued business document is never an asset.** `DT-001` §9.3 makes the archived rendition evidential and `M24` holds it. **Copying a Mushak 6.3 into an asset repository creates a second copy of a statutory record**, which `LG-009` and `BRU-DMS-01` do not contemplate |
| **DA-03** | **The unredacted source of a redacted capture is destroyed, not archived** (`MM-002` `SC-27`). **The register never receives it**, and a record pointing to one is a defect |
| **DA-04** | **A licence, a consent and a release are part of the asset**, not attachments to it. An asset whose rights record is empty is **unusable**, not merely undocumented (`MM-001` `MT-02`) |

### 4.2 Where assets live

Three stores, with a stated boundary between them.

| Store | Holds | Why not elsewhere |
|---|---|---|
| **The content repository** (`project_content/`) | **Only** small, versioned, text-adjacent assets an author edits alongside prose: SVG diagrams, SVG icons, small specimens — in an `assets/` folder beside the owning file (`CG-005` `CF-04`) | Diffable, versioned with the content, reviewable in the same change |
| **The asset repository (DAM)** | Everything else: photography and its raw, video and its footage, animation source, illustration masters, print specimens, library releases, licences, consents | Binary, large, non-diffable, rights-bearing, shared across many content files |
| **`M24`** | Issued documents; **consent and release instruments**; contracts and licences as legal records | It is the system of record for records |

| # | Rule |
|---|---|
| **DA-05** | **`CG-005` `CF-04`'s `assets/` convention is retained for the first store and bounded to it.** A file over **1 MB**, a file with no text-adjacent purpose, or an asset used by more than one content file belongs in the DAM |
| **DA-06** | **`CG-005` §9's three-level depth limit still applies** inside `project_content/`. The DAM is not a folder tree and is not bound by it |
| **DA-07** | **The consent and licence instruments live in `M24`**; the DAM record **points to them** and never holds the only copy (`MM-009` `PH-08`, `CG-012` `EV-07`) |
| **DA-08** | **`ID-08` applies everywhere: no spaces, no ampersands, no non-ASCII in any path**, in any store, without exception. Audit finding `AF-12` is the reason and it does not stop at the repository boundary |

### 4.3 The asset naming standard

**Extends `CG-005` §4 and §5. It does not replace them** (`DA-09`).

```
<OWNER>_<slug>[__<variant>][_<lang>][_<density>]_v<n>.<ext>
   │       │         │           │         │        └── version, integer, no leading zeros
   │       │         │           │         └────────── 1x | 2x | 3x — raster only
   │       │         │           └──────────────────── en | bn — only where the asset is language-specific
   │       │         └──────────────────────────────── variant: theme, size, state, surface
   │       └────────────────────────────────────────── lower_snake_case description
   └────────────────────────────────────────────────── the owning content ID, or the MM class
```

| Element | Rule |
|---|---|
| `<OWNER>` | **The owning content ID** (`HC-003`, `DT-010`, `UI-006`) where one file owns it, **or the `MM-` class file** where it is shared — `MM-004` for an icon, `MM-005` for an empty-state illustration |
| `<slug>` | `lower_snake_case`, ASCII only, describes the asset not the file type |
| `<variant>` | After a **double underscore**, matching `CG-005` §5's multi-part convention: `light`, `dark`, `mono`, `16`, `24`, `thermal`, `vertical` |
| `<lang>` | `en` or `bn`, **only where the asset differs by language** — a language-neutral illustration carries none |
| `<density>` | `1x`, `2x`, `3x` — raster only |
| `v<n>` | **Always present, from v1.** An unversioned asset cannot be superseded without breaking a reference |
| Extension | Lower case |

**Examples**

| Asset | Name |
|---|---|
| Dispatch console screenshot, Bengali, release-tagged | `HC-005_dispatch_console__list_bn_2x_v3.png` |
| Approve action icon, 24 px | `MM-004_approve__24_v1.svg` |
| Empty state, no results | `MM-005_no_results_v2.svg` |
| Email logo, dark theme | `MM-011_logo__dark_2x_v1.png` |
| Mushak 6.3 specimen, maximum line items | `DT-010_specimen__max_lines_v2.pdf` |
| Walk-in intake L2 process diagram | `SP-007_walk_in_intake__l2_v4.svg` |
| Seller registration video, Bengali | `MM-007_photograph_your_documents_bn_v1.mp4` |
| Branch exterior photograph | `MM-009_branch_exterior_shewrapara_v1.tif` |

| # | Rule |
|---|---|
| **DA-09** | **The `<OWNER>` element is a registered content ID or a registered `MM-` file. Nothing else.** This is `CG-005` `ID-07` applied to assets: **assets cite identifiers, they never mint them** |
| **DA-10** | **The name is not the record.** It aids scanning; the register carries the truth. A name and a record that disagree are resolved **in favour of the record** |
| **DA-11** | **A name is never reused for different content**, even after retirement — `CP-02` applied to assets |
| **DA-12** | **The full path stays under 120 characters.** `CG-005` §4 caps a content file name at 80 for Windows path reasons; assets nest deeper and carry more elements |
| **DA-13** | **Derivatives share the stem** and differ only by `<density>` and extension, so a set can be globbed |

### 4.4 Versioning and immutability

> **`DA-14`: a published asset is immutable.** Once an asset has been referenced by published
> content, an issued document or a delivered email, **its bytes at that path never change.** A
> change is a **new version at a new path**, and the old one continues to resolve.

| # | Rule |
|---|---|
| **DA-15** | **The reason is `DT-001` §9.3 and `MM-011` `EA-37`, stated once for both.** A statutory document is *"a fact about a moment"*; a delivered email is a copy in someone else's mailbox. **Overwriting an asset changes a record already issued**, and neither can be recalled |
| **DA-16** | **Versions increment on any change to the bytes** — a re-crop, a re-export, a metadata correction. **There is no "minor" asset edit** |
| **DA-17** | **Superseding is recorded, not implied.** The register states which version supersedes which, when and why (`CG-006` pattern) |
| **DA-18** | **A superseded asset is retained while any published reference to it survives**, and `MM-011` `EA-39` makes that indefinite for the transactional email path |
| **DA-19** | **Content references an asset by register identifier and version**, not by a raw path. A path pasted into a content file is a link that breaks silently |
| **DA-20** | **A design-system library release is a versioned asset in its own right** (`MM-004` `IC-35`), and a glyph change inside it is a **MAJOR** library change with a release note (`OP-006`) and a screenshot re-capture sweep (`MM-002` `SC-44`) |

### 4.5 The rights and consent record

**The half of this file that makes it a compliance record rather than a filing system.**

| Field | Source | Required for |
|---|---|---|
| **Creator** | IPTC Core | Every commissioned asset |
| **Copyright holder** | IPTC Core | Every asset |
| **Assignment evidence** | `M24` reference | **Every commissioned asset** (`MM-001` `DL-05`, `MM-009` `PH-32`) |
| **Licence type** | Register | Owned · commissioned-and-assigned · licensed · stock |
| **Licence territory / term / media / purpose** | Register | Every licensed or stock asset (`MM-009` `PH-33`) |
| **Licence expiry** | Register | **Every licensed or stock asset — with an alarm** (`DA-22`) |
| **Model release status** | IPTC Extension | **Every asset containing an identifiable person** |
| **Model release reference** | `M24` reference | As above |
| **Property release status** | IPTC Extension | Every asset showing premises |
| **Consent expiry** | Register | **Every asset containing a person** (`MM-009` `PH-04`) |
| **Third-party material** | Register | Music, footage, stock, typefaces, artwork in frame |
| **Attribution / credit required** | IPTC Core Credit Line | Where the agreement requires it (`MM-009` `PH-34`) |

| # | Rule |
|---|---|
| **DA-21** | **An asset with an empty rights record is unpublishable**, and an empty model-release field **reads as unreleased**, never as "probably fine" (`MM-001` `MT-02`) |
| **DA-22** | **Every expiring right carries an alarm at 90 days and at expiry**, and **expiry withdraws the asset automatically** — it does not wait for someone to notice. A stock licence that lapsed two years ago is an infringement running quietly across every surface it appears on |
| **DA-23** | **Rights records are permanent.** Under Bangladesh copyright law a photograph's term runs long past every current arrangement (`MM-009` §4.6 ‡); the record outlives the asset's use |
| **DA-24** | **The register answers "which assets contain this person" as a query, not as a search** (`MM-009` `PH-43`). This is a **structural** requirement on the tool, not a tagging discipline |
| **DA-25** | **A partner-issued asset carries its own record** — who it went to, under what terms, for how long (`EO-012`) — because an asset outside the company is the one most likely to outlive its licence |

### 4.6 Classification and access

Assets inherit the programme's classification (`05-02` §10), because **an asset can contain
exactly the data the classification exists to protect.**

| Class | Asset examples | Access |
|:--:|---|---|
| **S0 public** | Published logo, public illustration, published customer video | Open |
| **S1 internal** | Screenshots of sample data, diagrams, internal photography, library releases | Authenticated |
| **S2 confidential** | Unpublished photography containing employees, commercial specimens, partner assets | Allow-list |
| **S3 restricted** | **Nothing.** No asset may contain `S3` data | **Not permitted to exist** (`DA-26`) |

| # | Rule |
|---|---|
| **DA-26** | **No asset contains `S3` restricted data.** `MM-002` §4.4.1 makes it "not captured" rather than "redacted"; **the register enforces the same rule at rest** — a record whose classification is `S3` is a defect, not a permission level |
| **DA-27** | **Assets containing identifiable people are `S2` until published, and remain access-controlled after** — publication changes the surface, not the sensitivity of the underlying record |
| **DA-28** | **Access is logged for `S2`** (`05-04` §4 pattern), so a later question about who obtained an asset has an answer |
| **DA-29** | **Bulk export of the asset register or of `S2` assets requires approval and is logged** (`LG-008` `PI-05`) |
| **DA-30** | **Confidentiality marking on an exported asset follows [`RP-014`](../14_Reporting_Analytics_and_KPI/RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md)**, which owns marking; this file does not define a second scheme |

### 4.7 Retention, retirement and withdrawal

Three different things, deliberately separated.

| Event | Meaning | Consequence |
|---|---|---|
| **Retirement** | The asset is no longer used in new content | Removed from the active library; **retained**; existing references continue to resolve (`DA-18`) |
| **Withdrawal** | The asset **must stop being displayed** — consent withdrawn, licence expired, error found, safety breach in frame | **Removed from every surface, cache and index**, and any material in production is stopped |
| **Deletion** | The bytes are destroyed | **Only** where `LG-009` requires it, or `MM-002` `SC-27` applies, and **never for an asset with a live published reference** |

| # | Rule |
|---|---|
| **DA-31** | **A withdrawal is executed across every surface, including caches, search indexes and printed material in production** (`MM-002` `SC-30`, `MM-009` `PH-43`, `MM-007` `CV-38`). **A withdrawal that leaves one surface untouched has not happened** |
| **DA-32** | **A consent withdrawal is honoured immediately** (`LG-008` `CN-R3`), which is why `DA-24`'s query requirement is structural. **Immediately is not achievable by searching a folder tree** |
| **DA-33** | **Consent and licence expiry trigger the same sweep automatically** (`DA-22`, `MM-009` `PH-44`), without waiting for a request |
| **DA-34** | **Retirement never deletes an asset in the transactional email path** (`MM-011` `EA-39`) or referenced by an archived statutory document (`DT-001` `R-03`). **These two exclusions are absolute** |
| **DA-35** | **An orphan sweep runs per wave**: assets with no live reference are proposed for retirement; **assets referenced by nothing and containing a person are proposed for deletion** (`MM-009` `PH-45`, `LG-008` `PI-02`) |
| **DA-36** | **A screenshot orphaned by a release is withdrawn or replaced, not left** (`MM-002` `SC-45`), and the release's orphan list is produced by querying this register (`SC-44`) |

### 4.8 Findability

| # | Rule |
|---|---|
| **DA-37** | **Every asset carries the owning content ID, the surface, the language and the release** where each applies — the four facets every real query starts from |
| **DA-38** | **Tags come from `CG-004` controlled vocabulary**, not from free text. A tag vocabulary invented per uploader is a search that returns nothing on the third attempt |
| **DA-39** | **Embedded metadata and the register record are kept in step** (`MM-001` `MT-05`), and the pipeline **must not strip XMP on optimisation** (`MT-06`) — most optimisers do by default |
| **DA-40** | **Every asset states what it is derived from**, so a derivative can be regenerated when its master changes (`MM-003` `DG-32`, `MM-001` `AS-04`) |

### 4.9 The asset record schema

**The `CG-009` §3 required addition for Category 19.** This file's deliverable is the register, so
its "deliverable specification" is the record every asset must carry.

| # | Field | Required | Source | Notes |
|---:|---|:--:|---|---|
| 1 | `asset_id` | ✔ | Register | Permanent, never reused (`DA-11`) |
| 2 | `file_name` | ✔ | §4.3 | Follows the pattern exactly |
| 3 | `owner_content_id` | ✔ | `CG-005` | A registered content ID or `MM-` file (`DA-09`) |
| 4 | `class` | ✔ | `MM-001` §4.1 | A1–A11 |
| 5 | `governing_brief` | ✔ | — | `MM-002` … `MM-011` |
| 6 | `version` | ✔ | §4.4 | Integer from 1 |
| 7 | `supersedes` / `superseded_by` | Conditional | §4.4 | With date and reason |
| 8 | `status` | ✔ | — | Draft · Active · Retired · **Withdrawn** · Deleted |
| 9 | `classification` | ✔ | `05-02` §10 | S0/S1/S2; **S3 not permitted** (`DA-26`) |
| 10 | `language` | Conditional | — | `en`/`bn`, where language-specific |
| 11 | `surface` | Conditional | — | Portal, document, email library, course |
| 12 | `release_captured_against` | **✔ for A1, A4, A7, A8** | `MM-002` `SC-43` | The currency mechanism |
| 13 | `derived_from` | Conditional | `DA-40` | Master asset |
| 14 | `derivatives` | ✔ | `DA-13` | The generated set |
| 15 | **`creator`** | ✔ | IPTC Core | |
| 16 | **`copyright_holder`** | ✔ | IPTC Core | |
| 17 | **`assignment_evidence`** | ✔ commissioned | `M24` ref | `MM-001` `DL-05` |
| 18 | **`licence_type`** | ✔ | §4.5 | |
| 19 | **`licence_terms`** | ✔ licensed | §4.5 | Territory / term / media / purpose |
| 20 | **`licence_expiry`** | ✔ licensed | §4.5 | **Alarmed** (`DA-22`) |
| 21 | **`model_release_status`** | ✔ where a person appears | IPTC Extension | **Empty = unreleased** (`DA-21`) |
| 22 | **`model_release_ref`** | ✔ where released | `M24` ref | |
| 23 | **`persons_depicted`** | ✔ where a person appears | Register | **The field `DA-24` queries** |
| 24 | **`consent_expiry`** | ✔ where a person appears | `MM-009` `PH-04` | **Alarmed** |
| 25 | **`property_release_status`** | ✔ where premises appear | IPTC Extension | |
| 26 | `third_party_material` | Conditional | Register | Music, stock, footage, typefaces |
| 27 | `attribution_required` | Conditional | IPTC Credit Line | `MM-009` `PH-34` |
| 28 | `hse_approval_ref` | ✔ where a physical task appears | `M24` ref | `MM-005` `IL-08`, `MM-006` `VT-25`, `MM-009` `PH-23` |
| 29 | `accessibility_artefacts` | ✔ A7/A8/A9 | `MM-001` §4.7 | Captions, transcript, static frame |
| 30 | `tags` | ✔ | `CG-004` | Controlled vocabulary (`DA-38`) |
| 31 | `references` | ✔ | Register | **Which content, documents and emails use it** — the second query in §1 |
| 32 | `url` | Conditional | `MM-011` `EA-37` | **Immutable once published** |
| 33 | `retention_basis` | ✔ | `LG-009` | |
| 34 | `created` / `published` / `withdrawn` | ✔ | — | Dates |

| # | Rule |
|---|---|
| **DA-41** | **Fields 21–25 make the register a personal-data record**, subject to `LG-008` and `LG-009` in its own right. **The register is not exempt from the rules it exists to enforce** |
| **DA-42** | **Field 31 is populated by the build, not by a human.** A hand-maintained reference list is wrong within a wave, and it is the field `DA-15`'s immutability guarantee depends on |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`CG-005_Content_ID_and_Naming_Convention.md`](../00_Content_Governance_and_Standards/CG-005_Content_ID_and_Naming_Convention.md) | §4 naming, §5 `CF-01`…`CF-04`, `ID-07`, `ID-08`, `ID-09`, §9 depth — the standard this file extends and never re-decides |
| [`CG-006_Content_Lifecycle_and_Versioning_Policy.md`](../00_Content_Governance_and_Standards/CG-006_Content_Lifecycle_and_Versioning_Policy.md) | The versioning grammar §4.4 mirrors |
| [`CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | The tag vocabulary `DA-38` requires |
| [`CG-012_Content_Sourcing_and_Evidence_Rules.md`](../00_Content_Governance_and_Standards/CG-012_Content_Sourcing_and_Evidence_Rules.md) · [`CG-013_Content_Risk_and_Legal_Escalation_Rules.md`](../00_Content_Governance_and_Standards/CG-013_Content_Risk_and_Legal_Escalation_Rules.md) | `EV-07` — a source that cannot be produced is not a source; the escalation route for a withdrawal failure |
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](../10_Legal_Policy_and_Compliance/LG-008_Privacy_Notice_and_Consent_Copy.md) | `CN-R3` immediate withdrawal; `PI-02` purpose limitation; `PI-05` bulk export |
| [`LG-009_Data_Retention_and_Deletion_Schedule.md`](../10_Legal_Policy_and_Compliance/LG-009_Data_Retention_and_Deletion_Schedule.md) · [`LG-010_Data_Subject_Request_Handling_Content.md`](../10_Legal_Policy_and_Compliance/LG-010_Data_Subject_Request_Handling_Content.md) · [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](../10_Legal_Policy_and_Compliance/LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) · [`LG-021_ISMS_Policy_Set.md`](../10_Legal_Policy_and_Compliance/LG-021_ISMS_Policy_Set.md) | Retention basis; the erasure route a withdrawal may arrive through; where the DAM may be hosted; the controls behind §4.6 |
| [`DT-001_Document_Template_Standard_and_Branding_Rules.md`](../05_Document_and_Print_Templates/DT-001_Document_Template_Standard_and_Branding_Rules.md) · [`DT-044_Label_Barcode_and_QR_Format_Specification.md`](../05_Document_and_Print_Templates/05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) | §9.3 the re-render prohibition behind `DA-15`; the label specimen set |
| [`RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md`](../14_Reporting_Analytics_and_KPI/RP-014_Export_Watermark_and_Confidentiality_Marking_Rules.md) | Marking, which `DA-30` defers to rather than duplicating |
| [`EO-012_Co_Marketing_and_Co_Branding_Asset_Guide.md`](../18_Ecosystem_Onboarding_Content/EO-012_Co_Marketing_and_Co_Branding_Asset_Guide.md) | Partner issue and the record `DA-25` requires; it cites this file as unwritten |
| [`MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md`](MM-001_Multimedia_Asset_Standard_and_Delivery_Specification.md) | The eleven classes, the metadata set, `DL-05` rights assignment |
| [`MM-002_Screenshot_Annotation_and_Redaction_Standard.md`](MM-002_Screenshot_Annotation_and_Redaction_Standard.md) | `SC-27` destruction, `SC-43` release registration, `SC-44` the orphan query |
| [`MM-003_Diagram_and_Process_Map_Visual_Standard.md`](MM-003_Diagram_and_Process_Map_Visual_Standard.md) · [`MM-004_Icon_Set_Requirements.md`](MM-004_Icon_Set_Requirements.md) · [`MM-005_Illustration_and_Empty_State_Artwork_Brief.md`](MM-005_Illustration_and_Empty_State_Artwork_Brief.md) | Derivative registration; library releases; stock-derived licence records |
| [`MM-006_Video_Production_Brief_Training_Series.md`](MM-006_Video_Production_Brief_Training_Series.md) · [`MM-007_Video_Production_Brief_Customer_How_To_Series.md`](MM-007_Video_Production_Brief_Customer_How_To_Series.md) · [`MM-008_Animated_Explainer_Brief_Portal_Onboarding.md`](MM-008_Animated_Explainer_Brief_Portal_Onboarding.md) | Accessibility artefacts as record fields; withdrawal on consent withdrawal; retirement on low completion |
| [`MM-009_Photography_Brief_Branches_Workshop_and_Field.md`](MM-009_Photography_Brief_Branches_Workshop_and_Field.md) | **`PH-43`'s one-query requirement — the hardest requirement in this file**; `PH-04` expiry; `PH-32`…`PH-36` rights |
| [`MM-010_PDF_and_Print_Template_Design_Specification.md`](MM-010_PDF_and_Print_Template_Design_Specification.md) · [`MM-011_Email_and_HTML_Asset_Specification.md`](MM-011_Email_and_HTML_Asset_Specification.md) | Specimen registration; `EA-37` immutability and `EA-39` the retirement exclusion |
| [`TR-024_Release_Training_and_Refresher_Standard.md`](../08_Training_and_Enablement/08B_Course_Packs/TR-024_Release_Training_and_Refresher_Standard.md) · [`OP-006_Release_Notes_Standard_and_Wave_Note_Set.md`](../17_Operations_Support_and_Runbooks/OP-006_Release_Notes_Standard_and_Wave_Note_Set.md) · [`OP-011_Runbook_Portal_and_Mobile_App_Operations.md`](../17_Operations_Support_and_Runbooks/OP-011_Runbook_Portal_and_Mobile_App_Operations.md) | Release-triggered orphan sweeps; where a library release is announced and deployed |
| `M24` · `M60` | The instrument store; the record of processing the register itself feeds |
| `05-02` §10 · `05-04` §4 · `05-06` `NFR-086` | Classification, access tier, residency constraints on where the DAM may hold personal data |

| Depended on by |
|---|
| `MM-001` … `MM-011` (every naming and register clause) · `EO-012` · `MM-009` `PH-43` · `MM-002` `SC-44` · `MM-011` `EA-37` · every content file embedding an asset |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Per wave** during production; annually thereafter |
| Trigger for out-of-cycle review | A new asset class · a licence or consent regime change · a `CG-005` amendment · a failed withdrawal · a DAM tooling change · a residency ruling affecting where assets may be held |
| Owner | **Brand Lead**, with Platform Engineering for the repository and Legal for §4.5 and §4.7 |
| Approver | Content Design Lead with Brand Lead (`CG-002` §5.4, class D) |
| Enforcement | Automated: name pattern, `ID-08` path check, mandatory record fields, empty release status blocking publication, expiry alarms, orphan sweep, reference index build. Manual: rights review at commissioning |
| Effectiveness measure | **Time from consent withdrawal to complete removal — target same working day.** Assets in use with an expired licence: **target zero.** Published assets with no register record: **target zero** |
| Audit | The asset register is enumerated at every wave boundary, like the content register (`CP-11`, `CM-R2`) |
| Change log | [`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md) — **written; Category 99 completed 2026-08-18**. Every decision under this file is logged there |

---

## 7. Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **No digital asset management tooling is selected**, and §4.5, §4.7 and §4.9 describe capabilities — a queryable `persons_depicted` field, licence and consent expiry alarms, an immutable published URL, a build-populated reference index, and a withdrawal that sweeps caches and indexes — **that a shared folder cannot provide.** `MM-009` `O-07` records the consequence: **without it a consent withdrawal cannot be honoured within any stated time**, and `LG-008` `CN-R3` requires it to be immediate | Brand Lead with Chief Technology Officer | **W1 — before the first asset containing a person exists** |
| **O-02** | **`CG-005` does not contemplate assets at this scale**, and this file extends it without amending it. **`CG-005` §5 `CF-04` still says assets live in an `assets/` folder beside the owning file**, which §4.2 bounds to a subset. **The extension should be recorded in `CG-005` itself**, or a later reader will follow `CF-04` for a 4 GB video master. This is the same shape as `AUDIT-018` `EO-12`'s finding that a content file extended a specification's namespace without the specification saying so | Programme Content Lead with Brand Lead | **W1** |
| **O-03** | **Where the DAM may be hosted is unresolved.** Assets containing identifiable persons are personal data; `LG-012` and `NFR-086` constrain residency, and `AUDIT-017` `OP-01` records that **there is no lawful DR path for Bangladesh-resident personal data**. **A DAM chosen without answering this may be unlawful to operate**, and the question is the same one `LG-008` `O-02` records as blocking | Chief Technology Officer with Legal Counsel and the Chief Data Officer | **W1 — before tooling selection** |
| **O-04** | **No Chief Data Officer is appointed** (`LG-008` `O-05`), so **§4.5's release verification, §4.7's withdrawal execution and `DA-41`'s treatment of the register as a personal-data record have no owner** — the third `MM` file to record this after `MM-002` `O-03` and `MM-009` `O-04` | CEO | **W1** |
| **O-05** | **[`RF-006`](../99_Reference_and_Registers/RF-006_Content_Decision_Log_and_Change_Control.md) now exists** — Category 99 completed 2026-08-18 — and every asset-class, tooling, licence and retention decision here requires an entry in it (`MM-001` `AS-23`). **None has been entered.** `AUDIT-017` `OP-12` recorded ninety-four open decisions against a log that did not exist; **the promise `RF-006` was created to keep is now keepable, and keeping it is a backlog task with an owner rather than a category gap** | Programme Content Lead with Brand Lead | **W1 — a read-across, no longer a gap** |
| **O-06** | **`EO-012` `CB-03` remains unenforceable and this file cannot fix it.** `EO-012` records that it *"cannot cite a repository standard (`MM-012`, unwritten)"* — **now written** — **but its deeper gap is that no file holds the 1000FiX master identity** (`MM-001` `O-01`, `AUDIT-018` `EO-13`/`R-13`). This register can hold identity assets; **it cannot supply the standard that says what a correct one is** | Brand Lead with Programme Content Lead | **W1 — and before a mark is issued to any partner** |
| **O-07** | **`DA-42` requires the reference index (field 31) to be build-populated, and no build pipeline exists** for content or assets. **Until it does, `DA-15`'s immutability guarantee is a promise nobody can check**, and `MM-002` `SC-44`'s release orphan list must be produced by hand | Platform Engineering | **W1** |
| **O-08** | **`CG-005`'s retirement log covers content IDs and there is no equivalent for assets.** `DA-11` prohibits name reuse and `DA-17` requires supersession to be recorded, **but no register exists to record either in until `O-01` is resolved** | Programme Content Lead with Brand Lead | W1 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md` — six sections in order; the `CG-009` `MM` deliverable table at §4.9, stated as the asset record schema with the substitution justified; §7 added per category convention
- [x] **The two questions the register exists to answer stated first, both shown to be unanswerable retrospectively**
- [x] `CG-005` extended by citation and never re-decided; the `CF-04` boundary drawn and its limit stated
- [x] **Three stores defined with a boundary, and an issued business document excluded from being an asset**
- [x] **The unredacted screenshot source excluded from the register entirely**
- [x] Naming pattern specified with every element ruled and eight worked examples
- [x] **The name declared not to be the record, with the register governing on conflict**
- [x] **Immutability of a published asset stated with the two reasons — the statutory re-render prohibition and the delivered email — given once for both**
- [x] Rights record specified field by field, with an empty release reading as unreleased
- [x] **Licence and consent expiry alarmed and made an automatic withdrawal trigger, not a reminder**
- [x] **The one-query requirement from `MM-009` `PH-43` carried as a structural requirement on the tool, not as a tagging discipline**
- [x] Classification inherited from `05-02` §10, with `S3` made impossible rather than restricted
- [x] **Retirement, withdrawal and deletion separated, with two absolute exclusions from deletion**
- [x] Orphan sweep bound to the release cycle and to `MM-002` `SC-44`
- [x] Thirty-four record fields specified, with the register itself acknowledged as a personal-data record
- [x] All internal links resolve
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [x] English-only per `CG-010` §3.2
- [ ] **`O-01` no DAM tooling — outstanding; a consent withdrawal cannot be honoured immediately**
- [ ] **`O-03` DAM residency unresolved — outstanding; the tool may be unlawful to operate**
- [ ] **`O-06` the master identity remains unowned — outstanding; `EO-012` `CB-03` still unenforceable**
- [ ] **`O-07` no build pipeline, so the reference index is unpopulated — outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Brand Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*

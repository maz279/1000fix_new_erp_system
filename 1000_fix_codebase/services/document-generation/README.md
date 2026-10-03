# document-generation — P06-M03-T07 (CD-M20-nn)

Renders statutory and customer documents (Mushak 6.3, service receipt) as
PDF through the Odoo QWeb path, with Bengali conjunct shaping verified
against the committed TR-07 reference image. Dry-run without the runtime —
a workstation cannot produce a wrong statutory PDF by accident.

- `render(RenderJob) -> RenderResult` — template set (statutory flagged),
  BN-007 amount formatting (৳-before, Bengali numerals, lakh-crory
  grouping, sign before symbol), TR-07 reference-image contract
- Tests: `py -3.12 -m unittest discover -s services/document-generation/tests -t services/document-generation`

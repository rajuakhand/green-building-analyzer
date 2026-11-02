# Accessibility audit — Green Building Analyzer web app

- **Page audited:** `http://localhost:8017/#/calculator`
- **Engine:** axe-core 4.11.1
- **Date:** 2026-11-02
- **Scope:** accessibility only, as requested. SEO was not audited.

## Result

One violation, now fixed.

| Rule | Impact | Finding | Fix |
| --- | --- | --- | --- |
| `color-contrast` (WCAG 1.4.3) | Serious | `.calc-row__factor` — `#7e8e85` on white at 12.5px = 3.44:1, below the 4.5:1 threshold for normal text | The `--faint` token was darkened to `#6b7a72`, which measures 4.55:1 on white |

The affected selector was the only place that surfaced the token at normal text size in this
view, but `--faint` is used across the catalogue unit labels, stage sub-labels and field hints,
so the single token change fixes the same contrast gap everywhere it appears.

## Confirmed passing

- Names and roles: buttons, links and form fields all have discernible names; every input has an
  associated `<label>`; no nested interactive controls.
- Structure: one `<main>` landmark, one banner, unique landmarks, headings in order, one `<h1>`
  per view, valid `<dl>` / `<dt>` / `<dd>` grouping.
- Tables: `scope="col"` on headers, headers map to data cells, no duplicate summary/caption.
- Language and zoom: `lang="en"` on `<html>`, viewport allows pinch zoom and 500% text scaling.
- ARIA: no prohibited or invalid attributes, no `aria-hidden` on the body, no focusable elements
  inside `aria-hidden` containers.

## Notes for future work

- The data-quality notice is text, not colour-only, so its meaning survives greyscale.
- Chart bars carry their numeric values as text beside them, so the stages remain readable without
  relying on bar length.
- Status words (`Unverified`, `Illustrative`, `Needs-review`) come from the stored records rather
  than from colour.
- Re-run this audit when a new view is added, and check contrast whenever a new token is
  introduced.

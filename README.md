# Green Building Analyzer

**Embodied carbon and material cost estimates for Indian construction — with the assumptions always visible.**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23604851.svg)](https://doi.org/10.5281/zenodo.23604851)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/App-Streamlit-red.svg)](https://streamlit.io/)
[![Web app](https://img.shields.io/badge/Web%20app-no%20build%2C%20no%20dependencies-087f5b.svg)](https://rajuakhand.github.io/green-building-analyzer/)

Green Building Analyzer is a Python-based application for exploring the environmental impact and cost
of construction materials in India. It calculates material footprints, compares material-selection
scenarios, browses 78 published characterization factors and produces a printable material schedule.
Every screen states its own boundary and data quality, because an estimate that hides its assumptions
is worse than no estimate.

It is built for preliminary planning, teaching and exploration. It is **not** a certified life-cycle
assessment and does not replace verified environmental product declarations or professional
engineering advice.

---

## Open it

| | Link |
| --- | --- |
| **Web app** (recommended) | **https://rajuakhand.github.io/green-building-analyzer/** |
| Streamlit app | https://green-building-analyzer-xbwtufdrcywjjthgika3iw.streamlit.app/ |
| Source code | https://github.com/rajuakhand/green-building-analyzer |
| Software DOI | https://doi.org/10.5281/zenodo.23604851 |
| Product plan | [`docs/STARTUP-PLAN.md`](docs/STARTUP-PLAN.md) |
| Accessibility audit | [`docs/kombai-accessibility-audit-2026-11-02-23-53.md`](docs/kombai-accessibility-audit-2026-11-02-23-53.md) |

Individual screens have their own address, so a link can point straight at one:

```
…/#/estimate     material quantities, cost and carbon
…/#/compare      two scenarios side by side
…/#/statement    printable material schedule for a client
…/#/catalogue    the 78 research factors
…/#/method       the formulas and the boundary
…/#/sources      where every factor comes from
```

---

## What you can do

| View | What it answers |
| --- | --- |
| **Project estimate** | What do these four materials cost, and how much carbon do they carry? Quantities, rates, per-material carbon and contribution share, recalculated as you type. |
| **Compare scenarios** | If I change the quantities, what happens to carbon and to cost? Two columns over the same materials, with the change per material, the change in totals, and the rupee cost of each kilogram of CO₂e avoided. |
| **Project statement** | A material schedule a contractor can print and hand over: project and client details, quantities, rates, amounts, carbon per line, totals, the life-cycle summary and signature lines. |
| **Life-cycle assessment** | Which stage carries the carbon? Embodied, transport, operational energy and end-of-life, with the assumptions of one selected stage open beside them. |
| **Research catalogue** | Which published factor fits this material and this quantity basis? All 78 records with their own GWP unit, energy unit, boundary, geography and verification status. |
| **Research calculator** | What do the raised factors give for my quantities? GWP and energy totalled separately, in each factor's own unit. |
| **Method** | How is any number on this site produced? Five formulas, the unit rule and every exclusion, written out. |
| **Data sources** | Where does each factor come from, and how verified is it? Provenance for the pricing records, verification counts for the factors, and the source registry. |
| **Export** | CSV of the analysis, and a print-ready PDF report. |
| **AI recommendations** | A written sustainability report from Gemini, when an API key is configured on the server. |

The web app needs no accounts, no build step and no server. Values stay in the visitor's own browser,
so nothing is uploaded.

---

## How the numbers are produced

Each figure on the site comes from one of these, and nothing else:

| Figure | Formula |
| --- | --- |
| Estimated material cost | `quantity × unit cost` |
| Estimated material carbon | `quantity × emission factor` |
| Transport carbon | `mass (tonnes) × one-way distance (km) × transport factor` |
| Operational energy carbon | `annual electricity (kWh) × building lifetime (years) × grid factor` |
| End-of-life carbon | user-entered estimate |
| Total life-cycle carbon | `embodied + transport + operational + end-of-life` |

Two rules matter more than the arithmetic:

- **A quantity uses the denominator of its own factor.** A factor published per tonne is entered in
  tonnes; per quintal in quintals; per thousand bricks in thousands. No automatic conversion is
  applied anywhere.
- **A zero is not a verified zero.** A stage showing 0.00 means no impact was entered for it.

---

## Quick start

### Web app (no dependencies)

```bash
git clone https://github.com/rajuakhand/green-building-analyzer.git
cd green-building-analyzer
python3 -m http.server 8017 --directory web
# open http://localhost:8017
```

Plain HTML, vanilla CSS and ES modules. No npm install, no bundler, no framework. It reads the CSVs in
[`web/data/`](web/data/) — see [web/README.md](web/README.md) for the structure and how to deploy it.

### Streamlit app (Python)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Optional, for AI recommendations:

```bash
export GOOGLE_API_KEY="your-key"        # or GEMINI_API_KEY
```

The web app shows the configuration state instead of calling Gemini, because it has no server. The key
never reaches the browser.

---

## Data

| File | Contents |
| --- | --- |
| [`data/materials.csv`](data/materials.csv) | Four demo-priced materials: unit, emission factor, INR unit cost, source, system boundary, verification status |
| [`data/material_factors.csv`](data/material_factors.csv) | 78 cradle-to-gate characterization factors (GWP and energy) with their functional units, boundary, geography and verification status |
| [`data/source_registry.csv`](data/source_registry.csv) | The sources behind the factors, with boundary and verification status |
| [`data/equipment_factors.csv`](data/equipment_factors.csv) | Use-stage equipment factors (mixer, excavator, loader, crane, welding plant, diesel) |
| [`web/data/`](web/data/) | Copies of the CSVs the web app reads; refresh with `python3 scripts/sync_web_data.py` |

Attribution for the 78 factors: **Chaudhary & Akhtar (2023)**, *ACS Environ. Au* 3:94–104, Supporting
Information Table S3 — [doi:10.1021/acsenvironau.2c00035](https://pubs.acs.org/doi/10.1021/acsenvironau.2c00035).

**Data quality.** Several factor records are marked `Unverified`, `Illustrative` or `Needs-review` and
the interface says so wherever results appear. Confirm the source, reference year, functional unit and
system boundary before quoting any figure in a report.

---

## Testing

```bash
python -m pytest -q                 # Python: calculation, LCA and data validation
node web/tests/calc.test.mjs        # Web: 9 checks, no dependencies
```

The web tests assert the same expected values as the Python tests — 90.80 kg CO₂e and ₹400.00 for the
default project, 1,170 kg CO₂e and 9,400 MJ for the research example — so the two front ends cannot
drift apart without a test failing.

---

## Project structure

```
app.py                      Streamlit application
src/                        calculation, LCA, data loading, Gemini engine
data/                       CSV data
web/                        static front end (10 views, no build step)
  assets/css/style.css      design tokens and components
  assets/js/calc.js         the same formulas as src/calculator.py
  assets/js/views/          one module per view
  tests/calc.test.mjs       calculation tests
tests/                      pytest suite
scripts/                    data helpers
docs/                       product plan, accessibility audit
.github/workflows/          GitHub Pages deployment
```

---

## Limitations

- Results depend entirely on the quantities, rates and emission factors supplied. They are estimates.
- Emission factors and default prices are illustrative or unverified unless stated otherwise.
- Maintenance, repair and replacement are not modelled. Transport, operational energy and end-of-life
  are included only where you enter values.
- Selecting both concrete and its constituents double-counts carbon and cost.
- Comparisons are only valid when the boundary, the geography and the unit basis match.
- Not a life-cycle assessment. Not a substitute for professional engineering advice, a verified
  environmental product declaration or a formal LCA.
- AI-generated recommendations may be incomplete or wrong and must be reviewed before use.

---

## Roadmap

Phase 1 (method and data provenance) is shipped. Next: saved projects and comparisons with accounts,
then a server for metered AI recommendations and a branded PDF. The reasoning, effort and cost estimates
are in [`docs/STARTUP-PLAN.md`](docs/STARTUP-PLAN.md).

---

## Citation

If you use this software in academic work, cite the archived release. Check the Zenodo record before
using the citation; in particular, confirm the title, version and date.

```bibtex
@software{Akhand_Green_Building_Analyzer,
  author    = {Akhand, Abdul Gaffar Raju},
  title     = {{Green Building Analyzer: AI-Powered Green Building and Material Footprint Analysis}},
  publisher = {Zenodo},
  year      = {2026},
  version   = {v1.0.0},
  doi       = {10.5281/zenodo.23604851},
  url       = {https://doi.org/10.5281/zenodo.23604851}
}
```

---

## AI-assisted development

The author independently developed this project and used AI-assisted tools to support debugging,
interface work and error identification. The author reviews the implementation, checks outputs and
approves the final software. AI assistance does not replace verifying calculations, documenting sources,
testing the application and reporting limitations.

## License

MIT — see [LICENSE](LICENSE).

## Author

**Abdul Gaffar Raju Akhand**

- GitHub: [@rajuakhand](https://github.com/rajuakhand)
- Repository: [green-building-analyzer](https://github.com/rajuakhand/green-building-analyzer)

## Acknowledgements

The author acknowledges the guidance received from a teacher during project development, and the use of
AI-assisted tools for debugging support.

---

*This README describes the intended functionality of the software. Claims about scientific validation,
quantitative accuracy and performance require documented methods and reproducible evaluation.*

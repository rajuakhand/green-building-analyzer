# Green Building Analyzer — web app

A build-free front end for the analyzer, written in plain HTML, vanilla CSS and vanilla
ES modules. No npm, no bundler, no framework. It reads the same CSV data as the
Streamlit app and repeats its calculations, so both front ends agree.

## Run it locally

```bash
# from the repository root
python3 -m http.server 8017 --directory web
```

Then open <http://localhost:8017/>.

The pages fetch `data/materials.csv` and `data/material_factors.csv`, so the folder must be
served over HTTP. Opening `index.html` directly from disk will show a data-loading error.

## What is in here

| Path | Purpose |
| --- | --- |
| `index.html` | Shell; loads the stylesheet, fonts, icons and `assets/js/app.js` |
| `assets/css/style.css` | Design tokens and every component style |
| `assets/js/app.js` | Boot, hash routing, input routing, re-render |
| `assets/js/data.js` | CSV fetch and parse |
| `assets/js/calc.js` | Footprint and life-cycle formulas (mirrors `src/calculator.py`, `src/advanced_lca.py`) |
| `assets/js/store.js` | State and localStorage persistence |
| `assets/js/views/*.js` | The six views |
| `data/*.csv` | Copies of the project data files |

## The six views

- **Project estimate** — four demo-priced materials, live cost and carbon, contribution shares.
- **Life-cycle assessment** — four stage contributions, one stage's assumptions open at a time.
- **Research catalogue** — all 78 characterization factors, search, category filter, record inspector.
- **Research calculator** — quantities in each factor's own unit, GWP and energy kept separate.
- **AI recommendations** — the payload the advisor would receive and the current configuration state.
- **Export** — analysis CSV download and a print-ready PDF report.

## Data files

`web/data/` holds copies of `data/materials.csv` and `data/material_factors.csv`. After editing
the files under `data/`, refresh the copies:

```bash
python3 scripts/sync_web_data.py
```

The GitHub Pages workflow does the same copy before publishing.

## Values and limitations

- Calculations are the same formulas as the Python app: `quantity × unit_cost`,
  `quantity × emission_factor`, `tonnes × km × transport factor`,
  `kWh × years × grid factor`.
- Emission factors and default prices are illustrative or unverified, exactly as in the
  Python data files. The interface states this on every screen that shows results.
- Values are stored in the browser's localStorage. They stay on the visitor's device; nothing
  is sent anywhere.

## Deploying

GitHub Pages (automatic):

1. Push the folder to GitHub.
2. Repository **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. The included workflow `.github/workflows/deploy-web.yml` publishes `web/` on every push.

Any static host works the same way — upload the contents of `web/` to Netlify, Cloudflare
Pages, Vercel or an ordinary web server. Relative paths are used throughout, so subpaths
and custom domains both work.

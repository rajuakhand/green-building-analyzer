# Green Building Analyzer

**Embodied carbon and material cost estimates for construction — with assumptions always visible.**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23604851.svg)](https://doi.org/10.5281/zenodo.23604851)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/App-Streamlit-red.svg)](https://streamlit.io/)
[![Web App](https://img.shields.io/badge/Web%20app-No%20build%2C%20no%20dependencies-087f5b.svg)](https://rajuakhand.github.io/green-building-analyzer/)
[![Tests](https://img.shields.io/badge/tests-71%20passing-brightgreen.svg)](https://github.com/rajuakhand/green-building-analyzer/actions)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/rajuakhand/green-building-analyzer/pulls)

---

## Overview

Green Building Analyzer is a production-ready application for exploring the environmental impact and cost of construction materials. It calculates material footprints, compares material-selection scenarios, browses 78 published characterization factors, and produces printable material schedules. Every screen states its own boundary and data quality, because an estimate that hides its assumptions is worse than no estimate.

Built for preliminary planning, teaching, and exploration. **Not** a certified life-cycle assessment and does not replace verified environmental product declarations or professional engineering advice.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **Project Estimate** | Material quantities, cost, and carbon per material with live recalculation |
| **Compare Scenarios** | Side-by-side comparison of two material scenarios with delta analysis |
| **Project Statement** | Printable material schedule for clients and tenders with signature lines |
| **Life-Cycle Assessment** | Embodied, transport, operational energy, and end-of-life carbon breakdown |
| **Research Catalogue** | 78 published characterization factors with source provenance |
| **Research Calculator** | GWP and energy calculations using research factors in their own units |
| **AI Recommendations** | Gemini-powered sustainability advisor for carbon reduction and cost optimization |
| **Export** | CSV of analysis results and print-ready PDF reports |
| **Project Save/Load** | Per-user project persistence with authentication |
| **Dark Mode** | Light/dark theme toggle for comfortable viewing |
| **CSV Import** | Import custom materials from CSV files (merge or replace mode) |
| **Unit Converter** | Inline unit conversion supporting kg, tonne (吨), jin (斤), quintal, m³, liter, pcs, and more |
| **Authentication** | Email/password and mobile + SMS code login (China-ready) |

---

## 🏗️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.9+, Streamlit | Application server and UI |
| **Frontend** | HTML5, CSS3, ES6 Modules | Build-free web front end |
| **Calculations** | Vanilla JavaScript / Python | Carbon and cost formulas |
| **Visualization** | Plotly | Interactive charts and graphs |
| **PDF Generation** | fpdf2 | Print-ready reports |
| **AI** | Google Gemini (langchain-google-genai) | Sustainability recommendations |
| **Data** | CSV | Material factors and sources |
| **Storage** | localStorage | Client-side state and project persistence |
| **Testing** | pytest, Node.js | 71 Python tests + 9 JS calculation tests |

---

## 🚀 Quick Start

### Option 1: Web App (No Dependencies)

```bash
# Clone the repository
git clone https://github.com/rajuakhand/green-building-analyzer.git
cd green-building-analyzer

# Serve the web front end
python3 -m http.server 8017 --directory web

# Open in browser
# http://localhost:8017
```

### Option 2: Streamlit App (Python)

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Option 3: Docker

```bash
# Build image
docker build -t green-building-analyzer .

# Run container
docker run -p 8501:8501 green-building-analyzer
```

---

## 📖 Usage

### Web App Navigation

| Route | Page | Purpose |
|-------|------|---------|
| `#/estimate` | Project Estimate | Material quantities, cost, and carbon |
| `#/compare` | Compare Scenarios | Two-column scenario comparison |
| `#/statement` | Project Statement | Printable material schedule |
| `#/lca` | Life-Cycle Assessment | Stage-by-stage carbon breakdown |
| `#/catalogue` | Research Catalogue | 78 characterization factors |
| `#/calculator` | Research Calculator | GWP and energy calculations |
| `#/ai` | AI Recommendations | Gemini sustainability advisor |
| `#/method` | Method | Formulas and boundaries |
| `#/sources` | Data Sources | Provenance and verification |
| `#/export` | Export | CSV and PDF download |
| `#/import` | Import | CSV material import |

### Authentication

1. Click **Sign in** in the sidebar footer
2. Enter email and password (or mobile + SMS code)
3. Authenticated users can save, load, and delete projects
4. Project data is stored per-user in localStorage

### Unit Conversion

The estimate view supports inline unit conversion:

| Category | Supported Units |
|----------|----------------|
| Mass | kg, tonne (吨), quintal, jin (斤), liang (两), g, lb |
| Volume | m³, liter, ml, gallon |
| Count | pcs, thousand pcs, dozen, bag (包), roll, bundle |

Select a unit from the dropdown next to each material. Quantities automatically convert between display and base units.

---

## 📁 Project Structure

```
green-building-analyzer/
├── app.py                      # Streamlit application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── LICENSE                     # MIT License
├── data/                       # CSV data files
│   ├── materials.csv           # Demo-priced materials (4 items)
│   ├── material_factors.csv    # 78 characterization factors
│   ├── source_registry.csv     # Source provenance registry
│   └── equipment_factors.csv   # Use-stage equipment factors
├── src/                        # Python calculation modules
│   ├── calculator.py           # Footprint calculations
│   ├── advanced_lca.py         # Life-cycle assessment
│   ├── ai_engine.py            # Gemini AI recommendations
│   └── material_data.py        # Data loading and validation
├── tests/                      # Python test suite
├── web/                        # Static front end (no build step)
│   ├── index.html              # Application shell
│   ├── assets/css/style.css    # Design tokens and components
│   ├── assets/js/
│   │   ├── app.js              # Boot, routing, state management
│   │   ├── auth.js             # Authentication scaffolding
│   │   ├── calc.js             # Calculation formulas
│   │   ├── units.js            # Unit conversion module
│   │   ├── data.js             # CSV fetch and parse
│   │   ├── format.js           # Formatting utilities
│   │   ├── store.js            # Application state and persistence
│   │   ├── shell.js            # UI shell and navigation
│   │   └── views/              # One module per view
│   │       ├── estimate.js     # Project estimate view
│   │       ├── compare.js      # Scenario comparison view
│   │       ├── statement.js    # Project statement view
│   │       ├── lca.js          # Life-cycle assessment view
│   │       ├── catalogue.js    # Research catalogue view
│   │       ├── calculator.js   # Research calculator view
│   │       ├── ai.js           # AI recommendations view
│   │       ├── method.js       # Method documentation view
│   │       ├── sources.js      # Data sources view
│   │       ├── export.js       # CSV/PDF export view
│   │       └── import.js       # CSV import view
│   ├── tests/calc.test.mjs     # JavaScript calculation tests
│   └── data/                   # CSV copies for web app
├── scripts/                    # Data helper scripts
├── docs/                       # Product plan, accessibility audit
└── .github/workflows/          # GitHub Pages deployment
```

---

## 🔧 API Reference

### Python Functions

| Function | Module | Description |
|----------|--------|-------------|
| `calculate_footprint(df)` | `src.calculator` | Calculate cost and carbon per material |
| `summarize_footprint(df)` | `src.calculator` | Summarize totals |
| `calculate_lca(...)` | `src.advanced_lca` | Life-cycle carbon by stage |
| `get_ai_recommendations(...)` | `src.ai_engine` | Gemini AI sustainability report |
| `validate_materials(df)` | `src.material_data` | Validate material data integrity |
| `load_material_factors(path)` | `src.material_data` | Load research factor catalogue |

### JavaScript Functions

| Function | Module | Description |
|----------|--------|-------------|
| `calculateFootprint(rows)` | `assets/js/calc.js` | Calculate cost and carbon per row |
| `calculateLca({embodiedCarbon, lca})` | `assets/js/calc.js` | Life-cycle carbon by stage |
| `convertUnit(value, fromUnit, toUnit)` | `assets/js/units.js` | Convert between units |
| `getUnitsByCategory(category)` | `assets/js/units.js` | Get units for a category |
| `saveProject(name)` | `assets/js/store.js` | Save project (auth required) |
| `loadProject(name)` | `assets/js/store.js` | Load project (auth required) |
| `registerUser(email, password, mobile)` | `assets/js/auth.js` | Register new user |
| `loginUser(email, password)` | `assets/js/auth.js` | Login with email/password |
| `loginWithMobile(mobile, smsCode)` | `assets/js/auth.js` | Login with mobile + SMS |

---

## 🧪 Testing

### Python Tests

```bash
# Run all tests
python -m pytest -q

# Run with coverage
python -m pytest --cov=src --cov=web
```

### JavaScript Tests

```bash
# From web directory
cd web
npm test
# or
node tests/calc.test.mjs
```

**Test Coverage:** 71 Python tests + 9 JavaScript tests covering cost, carbon, transport, operational carbon, research totals, and validation.

---

## 🗺️ Roadmap

### Phase 1: Foundation (Completed)
- [x] Method and data provenance
- [x] 78 characterization factors from Chaudhary & Akhtar (2023)
- [x] Build-free web front end
- [x] Streamlit application
- [x] PDF and CSV export
- [x] Project save/load with authentication
- [x] Dark mode theme
- [x] Unit conversion (Chinese units included)
- [x] CSV import

### Phase 2: Enterprise Features (Planned)
- [ ] User accounts with backend API
- [ ] Saved projects and comparisons with cloud sync
- [ ] Team collaboration and role-based access
- [ ] Custom emission factors upload
- [ ] Building templates (residential, commercial, industrial)

### Phase 3: AI & Automation (Planned)
- [ ] Metered AI recommendations server
- [ ] Automated carbon reduction suggestions
- [ ] Cost optimization engine
- [ ] LEED / GRIHA certification integration
- [ ] Mobile applications (iOS/Android)

### Phase 4: Ecosystem (Planned)
- [ ] Third-party API integrations
- [ ] Plugin architecture
- [ ] White-label solutions
- [ ] Enterprise governance and audit logs

---

## 🤝 Contributing

We welcome contributions! Please read our contributing guidelines before submitting pull requests.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add: some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 for Python code
- Follow ES6+ standards for JavaScript
- Write tests for new features
- Update documentation for user-facing changes
- All PRs must pass CI tests

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📊 Data Quality & Limitations

> ⚠️ **Important:** Results depend entirely on the quantities, rates, and emission factors supplied. They are estimates.

- Emission factors and default prices are illustrative or unverified unless stated otherwise
- Maintenance, repair, and replacement are not modeled
- Transport, operational energy, and end-of-life are included only where values are entered
- Selecting both concrete and its constituents may double-count carbon and cost
- Comparisons are only valid when boundary, geography, and unit basis match
- Not a life-cycle assessment; not a substitute for professional engineering advice
- AI-generated recommendations may be incomplete or wrong and must be reviewed

---

## 📚 Citation

If you use this software in academic work, cite the archived release:

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

Data attribution: **Chaudhary & Akhtar (2023)**, *ACS Environ. Au* 3:94–104, Supporting Information Table S3 — [doi:10.1021/acsenvironau.2c00035](https://pubs.acs.org/doi/10.1021/acsenvironau.2c00035).

---

## 🏢 Enterprise Support

For enterprise deployments, custom integrations, or priority support, contact:

- **Email:** enterprise@green-building-analyzer.com
- **GitHub Issues:** [github.com/rajuakhand/green-building-analyzer/issues](https://github.com/rajuakhand/green-building-analyzer/issues)
- **Documentation:** [docs/STARTUP-PLAN.md](docs/STARTUP-PLAN.md)

---

## 👥 Authors

**Abdul Gaffar Raju Akhand**
- GitHub: [@rajuakhand](https://github.com/rajuakhand)
- Repository: [green-building-analyzer](https://github.com/rajuakhand/green-building-analyzer)

---

## 🙏 Acknowledgements

- Guidance received from a teacher during project development
- AI-assisted tools used for debugging, interface work, and error identification
- Chaudhary & Akhtar (2023) for characterization factor data
- Zenodo for software archival and DOI

---

> **Green Building Analyzer** — AI-assisted estimates for educational and preliminary planning purposes. Not a certified life-cycle assessment.

# Green Building Analyzer — startup plan

A working document for turning the analyzer from a repository demo into a product that other
people use, cite and pay for. Everything here is grounded in what the repository already has.

---

## 1. What already exists

| Asset | State |
| --- | --- |
| Calculation core | `src/calculator.py`, `src/advanced_lca.py` — tested with pytest |
| Research data | 78 cradle-to-gate characterization factors (Chaudhary & Akhtar 2023, SI Table S3) |
| Demo pricing data | 4 materials with units, emission factors, INR unit costs, verification status |
| Streamlit app | Full working application, deployed on Streamlit Community Cloud |
| Web front end | `web/` — six views, no build step, same formulas, deployable on any static host |
| Credibility | Published software DOI (Zenodo), MIT licence, CITATION.cff |
| Gaps | No accounts, no saved projects, no server API, no verified factor set, no analytics |

The web front end is the product surface to grow from. The Streamlit app stays as the
experimental lab for new analysis features.

---

## 2. Who it is for

1. **Students and teachers** in civil, environmental and architecture programmes — the largest
   audience, free, arrives through course material and search.
2. **Practising engineers and estimators** in India making preliminary material comparisons —
   the paying audience, wants saved projects, verified factors and a report they can attach.
3. **Sustainability consultants and researchers** — needs traceable sources, boundary clarity
   and a citable method, not a prettier calculator.

The first two pull in different directions. Keep students on the free tier and charge for what
the second group needs: verified data, saved projects and a branded report.

---

## 3. Positioning

> Preliminary embodied-carbon and cost estimates for construction materials, using published
> Indian factors, with the assumptions always visible.

Not "an LCA software". The product's honest boundary — preliminary, traceable, unit-checked —
is its advantage in a market full of opaque calculators.

---

## 4. Roadmap

### Phase 0 — Make it public (1–2 days of effort)

- Publish `web/` on GitHub Pages with the included workflow.
- Short URL: `rajuakhand.github.io/green-building-analyzer`.
- Link it from the repository README, the Zenodo record and the Streamlit app sidebar.
- Static, free, no server to maintain. This is the version to send to people today.

### Phase 1 — Credibility (about 2 weeks of effort)

- **Methodology page** in the web app: the four formulas written out, the boundary of each
  factor, what is not included (transport unless entered, maintenance, demolition credits).
- **Data provenance table**: every factor links to its source row, reference year, geography and
  verification status. Promote the `Needs-review` records to a visible flag.
- **Parity tests**: a script that runs the same inputs through Python and through the JS
  calculators and asserts the numbers match. Prevents the two front ends drifting.
- **Screenshots and a 60-second demo GIF** in the README.
- **Analytics**: privacy-friendly page counts (GoatCounter or Cloudflare Web Analytics) to learn
  which view people actually use.

### Phase 2 — Saved work (about 3 weeks of effort)

The first real product feature. Right now a visitor loses everything on refresh.

- Accounts (email one-time link, or Google sign-in) — Supabase Auth or Firebase Auth.
- A `projects` table: name, materials + quantities + unit costs, LCA inputs, timestamps.
- "Save project", "Duplicate", "Compare two projects" (a before/after material swap is the single
  most valuable comparison for this audience).
- Shareable read-only link per project.

### Phase 3 — Server and AI (about 3 weeks of effort)

- Small FastAPI service next to the existing Python code: `/api/recommendations` calls the same
  `src/ai_engine.py` with the project payload. The API key stops living in the browser and can be
  rate-limited per account.
- Server-side PDF with the project name, logo and the methodology appendix. The printer version
  in the web app is a stopgap, not a deliverable a consultant can send to a client.
- Usage metering: N AI reports per month per account, then a paid tier.

### Phase 4 — First hundred users (4–6 weeks of effort, ongoing)

- Post the tool in two or three places where Indian civil engineering students actually are
  (department WhatsApp groups, LinkedIn, Reddit r/civilengineering, university mailing lists).
- Write one short article: "Why counting concrete and its ingredients double-counts carbon" —
  the double-counting warning already in the app is a genuinely useful teaching point.
- Offer a 30-minute workshop to two or three departments; the app is a better teaching aid than
  slides and it generates feedback you cannot get from page views.
- Ask five practising engineers to use it on a live estimate and sit with them while they do.

### Phase 5 — Money (after Phase 2–3)

Options, cheapest to most involved:

| Model | What is sold | Realistic |
| --- | --- | --- |
| Sponsorship / grant | Institutional support, logo on the site | Small grants, university CSR budgets |
| Pro account | Saved projects, comparisons, branded PDF, AI reports | ₹500–1,500 per user per month |
| Institutional licence | Department-wide seats + a factor set curated for their region | ₹25,000–75,000 per year per department |
| Consulting | Custom factor sets, workshops, method review | Highest value per hour, least scalable |

Keep the calculator itself free. Charging for the calculator kills the funnel that makes the
paid tier credible.

---

## 5. Target architecture

```
Static front end (web/)  ──►  FastAPI service  ──►  Postgres (projects, accounts)
GitHub Pages or CDN           (same Python code)     Supabase or Neon
        │                           │
        │                           ├── Gemini (AI recommendations, metered)
        └── CSV data files          └── WeasyPrint (server PDF)
```

Rules that keep this maintainable:

- One calculation implementation per language, imported everywhere — never copied into a view.
- Factor data stays in CSV until there are more than a few hundred rows or per-user factor sets;
  then move to a table with the same column names.
- Every new analysis feature ships in Streamlit first, then moves to the web app once the method
  is settled.

---

## 6. Cost of running it

| Item | Free tier | Paid when it grows |
| --- | --- | --- |
| Static hosting | GitHub Pages, unlimited | not needed |
| Database + auth | Supabase free (500 MB) | ~$25/month |
| API host | Render/Fly free | ~$7–20/month |
| Gemini | free quota | pay per token, cents per report |
| Domain | — | ~₹1,000–1,500/year |
| Analytics | GoatCounter free | ~$5/month |

Realistic running cost before real traction: ₹0–500/month. After a paid tier exists: ₹2,000–4,000/month.

---

## 7. Risks to handle before charging anyone

- **Factor licensing.** The 78 factors were extracted from a paper's supporting information.
  Cite it, do not resell the dataset on its own, and keep the `source_tables` column visible.
  Commercial use of a curated factor set should use EPD/ICMD sources or your own extraction.
- **The disclaimer is the product.** "Not a certified life-cycle assessment" must stay on every
  screen and in every export. Users who need a certified LCA should be sent elsewhere politely.
- **Unit mismatch is the main failure mode.** The Python code already validates unit
  denominators. The web app derives quantity units from the factor itself; keep that rule.
- **Do not invent savings percentages** in AI output. The current prompt already forbids
  inventing factors and percentages — keep that guardrail if the prompt is rewritten.

---

## 8. Metrics that decide the next phase

| Metric | Why |
| --- | --- |
| Sessions that change a quantity | Did the visitor actually run an estimate? |
| Exports per session | Proxy for real use rather than curiosity |
| Catalogue searches per session | Tells you whether the 78 factors are a draw |
| Return visits within 14 days | The only honest signal of usefulness |
| Account → project saved | Conversion to the paid tier's foundation |

---

## 9. What can be done next in this repository

In order of value:

1. Publish the web app on GitHub Pages and link it from the README and Zenodo record.
2. Add the methodology and data-provenance views to the web app.
3. Add the Python↔JS parity test so the numbers can never drift.
4. Add "save project" with local storage first (no accounts), then accounts.
5. Add the FastAPI recommendations endpoint so the AI button works without exposing a key.

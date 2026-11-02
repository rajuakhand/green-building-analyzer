import { STAGES } from "../calc.js";
import { buildAnalysisCsv, downloadFile } from "../csv.js";
import { CO2E, escapeHtml, formatNumber } from "../format.js";
import { pageHead } from "../shell.js";

/**
 * Export: the analysis CSV, the printable report, and the assumptions the
 * export carries so a calculation can be reproduced later.
 */
export function render(root, ctx) {
  const { state, derived } = ctx;
  const { summary, lcaResult } = derived;

  const assumptions = [
    ["Transport mass (tonnes)", formatNumber(state.lca.transportTonnes, 2)],
    ["One-way transport distance (km)", formatNumber(state.lca.transportDistanceKm, 2)],
    [
      `Transport emission factor (kg ${CO2E}/tonne-km)`,
      formatNumber(state.lca.transportFactor, 4),
    ],
    ["Annual electricity (kWh)", formatNumber(state.lca.annualEnergyKwh, 2)],
    ["Building lifetime (years)", formatNumber(state.lca.lifetimeYears, 0)],
    [`Electricity emission factor (kg ${CO2E}/kWh)`, formatNumber(state.lca.electricityFactor, 4)],
    [`End-of-life emissions (kg ${CO2E})`, formatNumber(state.lca.endOfLifeKg, 2)],
  ];

  root.innerHTML = `
    ${pageHead({ title: "Export" })}

    <section class="notice notice--warn">
      <i class="ti ti-alert-triangle notice__icon" aria-hidden="true"></i>
      <p class="notice__text">
        <strong>Demo data disclaimer.</strong> Emission factors and default prices are illustrative and
        have not been independently verified. Confirm units, local prices and emission-factor sources
        before using these results for real construction decisions.
      </p>
    </section>

    <div class="export-grid">
      <div class="export-card">
        <div class="export-card__head">
          <span class="export-card__icon"><i class="ti ti-file-spreadsheet" aria-hidden="true"></i></span>
          <h2 class="export-card__title">Detailed results (CSV)</h2>
        </div>
        <p>Material results, the life-cycle input assumptions, the stage summary and the life-cycle total in one file.</p>
        <p class="export-card__meta">${summary.materialCount} materials, ${STAGES.length} life-cycle stages</p>
        <button class="btn btn--primary" type="button" data-action="download-analysis">
          <i class="ti ti-download" aria-hidden="true"></i>Download detailed results (CSV)
        </button>
      </div>

      <div class="export-card">
        <div class="export-card__head">
          <span class="export-card__icon"><i class="ti ti-file-type-pdf" aria-hidden="true"></i></span>
          <h2 class="export-card__title">Report (PDF)</h2>
        </div>
        <p>Project summary, life-cycle stage breakdown, material-wise results and the data limitations, laid out for printing.</p>
        <p class="export-card__meta">
          Total ${formatNumber(summary.totalCarbon, 2)} kg ${CO2E}, INR ${formatNumber(summary.totalCost, 2)}
        </p>
        <button class="btn btn--primary" type="button" data-action="print-report">
          <i class="ti ti-printer" aria-hidden="true"></i>Download PDF report
        </button>
      </div>
    </div>

    <div class="panel">
      <div class="panel__head">
        <h3 class="t-panel">Assumptions carried in this export</h3>
        <span class="panel__meta">life-cycle inputs</span>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th scope="col">Input</th>
            <th scope="col">Value</th>
          </tr>
        </thead>
        <tbody>
          ${assumptions
            .map(
              ([label, value]) => `
            <tr>
              <td>${label}</td>
              <td class="is-strong">${value}</td>
            </tr>`
            )
            .join("")}
        </tbody>
      </table>
    </div>

    <div class="panel">
      <div class="panel__head">
        <h3 class="t-panel">Life-cycle carbon summary</h3>
        <span class="panel__meta">kg ${CO2E}</span>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th scope="col">Life-cycle stage</th>
            <th scope="col">Carbon (kg ${CO2E})</th>
          </tr>
        </thead>
        <tbody>
          ${STAGES.map(
            (stage) => `
            <tr>
              <td>${stage.label}</td>
              <td class="is-strong">${formatNumber(lcaResult.byStage[stage.key], 2)}</td>
            </tr>`
          ).join("")}
          <tr class="is-total">
            <td>Total life-cycle carbon</td>
            <td>${formatNumber(lcaResult.total, 2)}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <section class="notice">
      <i class="ti ti-info-circle notice__icon" aria-hidden="true"></i>
      <p class="notice__text">
        <strong>Possible double counting.</strong> If the concrete quantity already includes cement,
        sand and aggregate, counting both concrete and its ingredients counts the same carbon and cost
        twice: ${escapeHtml(summary.totalCarbon > 0 ? "this export totals both." : "no quantities are entered yet.")}
      </p>
    </section>
  `;
}

export function handleAction(action, ctx) {
  if (action !== "download-analysis") return false;

  const csv = buildAnalysisCsv({
    rows: ctx.derived.rows,
    summary: ctx.derived.summary,
    state: ctx.state,
    lcaResult: ctx.derived.lcaResult,
    stageLabels: STAGES,
  });

  downloadFile("green_building_analysis.csv", csv);
  return true;
}

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

    <div class="export-tools">
      <h3 class="t-panel export-tools__title">Print Settings</h3>
      <div class="export-tools__controls">
        <label>
          <input type="checkbox" id="include-assumptions" checked>
          Include assumptions panel
        </label>
        <label>
          <input type="checkbox" id="include-summary" checked>
          Include carbon summary panel
        </label>
      </div>
    </div>
  `;
}

/**
 * Generate and print the PDF report
 */
function printReport(ctx) {
  const { state, derived } = ctx;
  const { summary, lcaResult } = derived;

  const windowFeatures = "width=1200,height=900,scrollbars=yes,menubar=yes";

  const reportContent = `
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <title>Green Building Analysis Report</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link
          href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.48.0/dist/tabler-icons.min.css"
        />
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }
          html, body { height: 100%; font-family: "Source Sans 3", sans-serif; font-size: 14px; }
          body { padding: 40px; background: #f8f9fa; }
          .report {
            max-width: 800px;
            margin: 0 auto;
            background: #ffffff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          }
          .report-header { text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 2px solid #087f5b; }
          .report-header h1 { color: #087f5b; font-size: 28px; margin-bottom: 10px; }
          .report-header p { color: #666; font-size: 14px; }
          .section { margin-bottom: 30px; }
          .section h2 { color: #333; font-size: 18px; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 1px solid #e0e0e0; }
          .summary-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 20px; }
          .summary-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 3px solid #087f5b;
          }
          .summary-item label { display: block; color: #666; font-size: 12px; margin-bottom: 5px; }
          .summary-item .value { font-size: 20px; font-weight: 600; color: #087f5b; }
          .table { width: 100%; border-collapse: collapse; margin: 15px 0; }
          .table th {
            background: #087f5b;
            color: white;
            text-align: left;
            padding: 10px 12px;
            font-size: 13px;
            font-weight: 600;
          }
          .table td {
            border: 1px solid #e0e0e0;
            padding: 10px 12px;
            font-size: 13px;
          }
          .table tr:nth-child(even) { background: #f8f9fa; }
          .table .is-total {
            background: #087f5b;
            color: white !important;
            font-weight: 600;
          }
          .assumption-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e0e0e0; }
          .assumption-item:last-child { border-bottom: none; }
          .assumption-item_label { color: #666; }
          .assumption-item_value { font-weight: 600; color: #087f5b; }
          .disclaimer {
            margin-top: 40px;
            padding: 15px;
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 6px;
            font-size: 12px;
            color: #856404;
          }
          .disclaimer i { margin-right: 5px; }
          @media print {
            body { background: white; padding: 0; }
            .report { box-shadow: none; padding: 20px; }
            .no-print { display: none; }
            .print-header { display: block; margin-bottom: 20px; }
          }
          .print-header { display: none; }
        </style>
      </head>
      <body>
        <div class="report">
          <div class="print-header">
            <button class="btn btn--primary" onclick="window.print()" style="display: none;">
              <i class="ti ti-printer"></i> Print
            </button>
          </div>

          <div class="report-header">
            <h1>Green Building Analysis Report</h1>
            <p>Material carbon and cost analysis with life-cycle assessment</p>
          </div>

          <div class="section">
            <h2>Project Summary</h2>
            <div class="summary-grid">
              <div class="summary-item">
                <label>Building Name</label>
                <div class="value">${state.project.name || "Not specified"}</div>
              </div>
              <div class="summary-item">
                <label>Location</label>
                <div class="value">${state.project.location || "Not specified"}</div>
              </div>
              <div class="summary-item">
                <label>Total Carbon</label>
                <div class="value">${state.totalCarbon.toLocaleString([], { maximumFractionDigits: 2 })} kg CO₂e</div>
              </div>
              <div class="summary-item">
                <label>Total Cost</label>
                <div class="value">₹${state.totalCost.toLocaleString([], { maximumFractionDigits: 2 })}</div>
              </div>
            </div>
          </div>

          <div class="section">
            <h2>Life-Cycle Carbon Breakdown</h2>
            <table class="table">
              <thead>
                <tr>
                  <th scope="col">Life-Cycle Stage</th>
                  <th scope="col">Carbon (kg CO₂e)</th>
                </tr>
              </thead>
              <tbody>
                ${derived.stageLabels.map(stage => `
                  <tr>
                    <td>${stage.label}</td>
                    <td class="is-strong">${lcaResult.byStage[stage.key].toLocaleString([], { maximumFractionDigits: 2 })}</td>
                  </tr>
                `).join('')}
                <tr class="is-total">
                  <td>Total Life-Cycle Carbon</td>
                  <td>${lcaResult.total.toLocaleString([], { maximumFractionDigits: 2 })}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="section">
            <h2>Material Results</h2>
            <table class="table">
              <thead>
                <tr>
                  <th scope="col">Material</th>
                  <th scope="col">Quantity</th>
                  <th scope="col">Unit Cost</th>
                  <th scope="col">Total Cost</th>
                  <th scope="col">Carbon (kg CO₂e)</th>
                </tr>
              </thead>
              <tbody>
                ${derived.rows.map(row => `
                  <tr>
                    <td>${row.material.name}</td>
                    <td>${row.quantity.toLocaleString([], { maximumFractionDigits: 2 })}</td>
                    <td>₹${row.unitCost.toLocaleString([], { maximumFractionDigits: 2 })}</td>
                    <td>₹${row.totalCost.toLocaleString([], { maximumFractionDigits: 2 })}</td>
                    <td>${row.totalCarbon.toLocaleString([], { maximumFractionDigits: 2 })}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>

          <div class="section">
            <h2>Life-Cycle Assumptions</h2>
            <div class="assumption-item">
              <span class="assumption-item_label">Transport mass (tonnes)</span>
              <span class="assumption-item_value">${state.lca.transportTonnes?.toLocaleString([], { maximumFractionDigits: 2 }) || "0"}</span>
            </div>
            <div class="assumption-item">
              <span class="assumption-item_label">Transport distance (km)</span>
              <span class="assumption-item_value">${state.lca.transportDistanceKm?.toLocaleString([], { maximumFractionDigits: 2 }) || "0"}</span>
            </div>
            <div class="assumption-item">
              <span class="assumption-item_label">Transport emission factor (kg CO₂e/tonne-km)</span>
              <span class="assumption-item_value">${state.lca.transportFactor?.toLocaleString([], { maximumFractionDigits: 4 }) || "0.0000"}</span>
            </div>
            <div class="assumption-item">
              <span class="assumption-item_label">Annual electricity (kWh)</span>
              <span class="assumption-item_value">${state.lca.annualEnergyKwh?.toLocaleString([], { maximumFractionDigits: 2 }) || "0"}</span>
            </div>
            <div class="assumption-item">
              <span class="assumption-item_label">Building lifetime (years)</span>
              <span class="assumption-item_value">${state.lca.lifetimeYears?.toLocaleString([], { maximumFractionDigits: 0 }) || "0"}</span>
            </div>
            <div class="assumption-item">
              <span class="assumption-item_label">Electricity emission factor (kg CO₂e/kWh)</span>
              <span class="assumption-item_value">${state.lca.electricityFactor?.toLocaleString([], { maximumFractionDigits: 4 }) || "0.0000"}</span>
            </div>
            <div class="assumption-item">
              <span class="assumption-item_label">End-of-life emissions (kg CO₂e)</span>
              <span class="assumption-item_value">${state.lca.endOfLifeKg?.toLocaleString([], { maximumFractionDigits: 2 }) || "0"}</span>
            </div>
          </div>

          <div class="disclaimer">
            <i class="ti ti-alert-triangle"></i>
            <strong>Demo data disclaimer:</strong> Emission factors and default prices are illustrative and have not been independently verified.
            Confirm units, local prices and emission-factor sources before using these results for real construction decisions.
          </div>

          <div style="margin-top: 30px; text-align: center; color: #999; font-size: 12px;">
            Generated by Green Building Analyzer • ${new Date().toLocaleDateString()}
          </div>
        </div>
      </body>
    </html>
  `;

  const printWindow = window.open("", "_blank", windowFeatures);
  if (printWindow) {
    printWindow.document.write(reportContent);
    printWindow.document.close();
    printWindow.focus();
  } else {
    alert("Please allow pop-ups to enable PDF download.");
  }
}

export function handleAction(action, ctx) {
  if (action === "download-analysis") {
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

  if (action === "print-report") {
    printReport(ctx);
    return true;
  }

  return false;
}

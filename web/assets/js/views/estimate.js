import { buildAnalysisCsv, downloadFile } from "../csv.js";
import { CO2E, escapeHtml, formatFactor, formatNumber, percentOf } from "../format.js";
import { footerNote, inputValue, pageHead } from "../shell.js";

/**
 * Project estimate: material quantities and rates on the left, their
 * calculated cost, carbon and contribution on the right.
 */
export function render(root, ctx) {
  const { materials, derived } = ctx;
  const { rows, summary } = derived;

  root.innerHTML = `
    ${pageHead({
      title: "Project estimate",
      actions: `
        <button class="btn btn--outline" type="button" data-action="download-analysis">
          <i class="ti ti-download" aria-hidden="true"></i>Download CSV
        </button>
        <button class="btn btn--primary" type="button" data-action="print-report">
          <i class="ti ti-file-type-pdf" aria-hidden="true"></i>Download PDF report
        </button>
      `,
    })}

    <section class="notice notice--warn">
      <i class="ti ti-alert-triangle notice__icon" aria-hidden="true"></i>
      <p class="notice__text">
        <strong>Data-quality notice.</strong> Emission factors are illustrative or not independently
        verified. ${statusSummary(rows)}
      </p>
    </section>

    <div class="bench">
      <section class="column">
        <div class="section-head">
          <h2 class="t-section">Material quantities</h2>
          <span class="section-head__meta">${summary.materialCount} materials</span>
        </div>

        <div class="material-groups">
          ${rows
            .map((row, index) => {
              const qtyId = `qty-${index}`;
              const costId = `cost-${index}`;
              const unit = escapeHtml(row.unit);
              return `
              <div class="material-group">
                <div class="material-group__head">
                  <p class="material-group__name">${escapeHtml(row.name)}</p>
                  ${
                    row.verificationStatus
                      ? `<span class="material-group__status">${escapeHtml(row.verificationStatus)}</span>`
                      : ""
                  }
                </div>
                <div class="field-row">
                  <label class="field" for="${qtyId}">
                    <span class="field__label">Quantity (${unit})</span>
                    <input class="input" id="${qtyId}" type="text" inputmode="decimal"
                      autocomplete="off" data-bind="material-qty" data-material="${escapeHtml(row.name)}"
                      value="${inputValue(ctx, qtyId, row.quantity)}">
                  </label>
                  <label class="field" for="${costId}">
                    <span class="field__label">Cost per ${unit} (INR)</span>
                    <input class="input" id="${costId}" type="text" inputmode="decimal"
                      autocomplete="off" data-bind="material-cost" data-material="${escapeHtml(row.name)}"
                      value="${inputValue(ctx, costId, row.unitCost)}">
                  </label>
                </div>
                <p class="material-group__ef">
                  Emission factor ${formatFactor(row.emissionFactor)} kg ${CO2E}/${unit}
                </p>
              </div>`;
            })
            .join("")}
        </div>
      </section>

      <section class="column">
        <div class="section-head">
          <h2 class="t-section">Estimated results</h2>
          <span class="section-head__meta">INR, kg ${CO2E}</span>
        </div>

        <div class="metric-list">
          <div class="metric">
            <p class="metric__label">Estimated material carbon</p>
            <p class="metric__figure">
              <span class="metric__value">${formatNumber(summary.totalCarbon, 2)}</span>
              <span class="metric__unit">kg ${CO2E}</span>
            </p>
          </div>
          <div class="metric">
            <p class="metric__label">Estimated material cost</p>
            <p class="metric__figure">
              <span class="metric__value">${formatNumber(summary.totalCost, 2)}</span>
              <span class="metric__unit">INR</span>
            </p>
          </div>
          <div class="metric">
            <p class="metric__label">Materials analyzed</p>
            <p class="metric__figure">
              <span class="metric__value">${summary.materialCount}</span>
              <span class="metric__unit">of ${materials.length} priced</span>
            </p>
          </div>
        </div>

        <div class="panel" style="margin-top:16px">
          <div class="panel__head">
            <h3 class="t-panel">Material contributions</h3>
            <span class="panel__meta">carbon share</span>
          </div>
          <table class="table">
            <thead>
              <tr>
                <th scope="col">Material</th>
                <th scope="col">Cost (INR)</th>
                <th scope="col">Carbon (kg ${CO2E})</th>
                <th scope="col">Share</th>
              </tr>
            </thead>
            <tbody>
              ${rows
                .map((row) => {
                  const share = percentOf(row.carbon, summary.totalCarbon);
                  return `
                <tr>
                  <td>${escapeHtml(row.name)}</td>
                  <td class="is-muted">${formatNumber(row.estimatedCost, 2)}</td>
                  <td class="is-strong">${formatNumber(row.carbon, 2)}</td>
                  <td>
                    <span class="share">
                      <span class="share__track"><span class="share__fill" style="width:${share.toFixed(1)}%"></span></span>
                      <span class="share__pct">${share.toFixed(2)}%</span>
                    </span>
                  </td>
                </tr>`;
                })
                .join("")}
              <tr class="is-total">
                <td>Total</td>
                <td>${formatNumber(summary.totalCost, 2)}</td>
                <td>${formatNumber(summary.totalCarbon, 2)}</td>
                <td>100.00%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    ${footerNote({
      text: "<strong>Possible double counting.</strong> If the concrete quantity already includes cement, sand and aggregate, counting both concrete and its ingredients counts the same carbon and cost twice.",
      actionLabel: "Detailed results",
      actionRoute: "export",
    })}
  `;
}

/**
 * Groups the stored verification statuses so the notice follows whatever the
 * data file contains, including files that carry no status column at all.
 */
function statusSummary(rows) {
  const byStatus = new Map();
  const unrecorded = [];

  rows.forEach((row) => {
    const status = (row.verificationStatus || "").trim();
    if (!status) {
      unrecorded.push(row.name);
      return;
    }
    if (!byStatus.has(status)) byStatus.set(status, []);
    byStatus.get(status).push(row.name);
  });

  const parts = [];
  byStatus.forEach((names, status) => {
    parts.push(`${names.map(escapeHtml).join(", ")}: ${escapeHtml(status)}`);
  });

  if (unrecorded.length) {
    parts.push(
      `${unrecorded.map(escapeHtml).join(", ")}: no verification status recorded in the data file`
    );
  }

  return `${parts.join(". ")}.`;
}

export function handleAction(action, ctx) {
  if (action === "download-analysis") {
    const csv = buildAnalysisCsv({
      rows: ctx.derived.rows,
      summary: ctx.derived.summary,
      state: ctx.state,
      lcaResult: ctx.derived.lcaResult,
      stageLabels: ctx.derived.stageLabels,
    });
    downloadFile("green_building_analysis.csv", csv);
    return true;
  }

  if (action === "print-report") {
    window.print();
    return true;
  }

  return false;
}

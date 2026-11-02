import { CO2E, escapeHtml, formatNumber, percentOf } from "../format.js";
import { pageHead } from "../shell.js";

/**
 * Project statement: a material schedule a contractor can print and hand to a
 * client or attach to a tender — quantities, rates, amounts on one side, carbon
 * per line on the other. Everything comes from the numbers entered in the app.
 */
export function render(root, ctx) {
  const { state, derived } = ctx;
  const { rows, summary, lcaResult } = derived;
  const project = state.project;

  const today = new Date().toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });

  const projectName = project.name.trim() || "Untitled project";
  const costPerKg = summary.totalCarbon > 0 ? summary.totalCost / summary.totalCarbon : 0;

  /** Text fields keep the exact string; only the focused one is left untouched. */
  const textValue = (id, value) =>
    ctx.focusId === id && ctx.rawValue !== null && ctx.rawValue !== undefined
      ? String(ctx.rawValue)
      : escapeHtml(value);

  const details = [
    { id: "project-name", field: "name", label: "Project name", value: project.name, placeholder: "Example: Two-storey residence, Mirpur" },
    { id: "project-client", field: "client", label: "Client", value: project.client, placeholder: "Client or department" },
    { id: "project-site", field: "site", label: "Site", value: project.site, placeholder: "Site or city" },
    { id: "project-prepared-by", field: "preparedBy", label: "Prepared by", value: project.preparedBy, placeholder: "Name and role" },
  ];

  root.innerHTML = `
    ${pageHead({
      title: "Project statement",
      meta: `prepared ${today}`,
      actions: `
        <button class="btn btn--outline" type="button" data-action="print-report">
          <i class="ti ti-printer" aria-hidden="true"></i>Print or save as PDF
        </button>
        <button class="btn btn--primary" type="button" data-action="download-analysis">
          <i class="ti ti-download" aria-hidden="true"></i>Download CSV
        </button>
      `,
    })}

    <div class="notice">
      <i class="ti ti-info-circle notice__icon" aria-hidden="true"></i>
      <p class="notice__text">
        Fill in the project details, then print. The schedule carries the current quantities, rates
        and carbon figures, and states its own limitations on the page.
      </p>
    </div>

    <div class="statement-print-head">
      <p class="statement-print-head__title">${escapeHtml(projectName)}</p>
      <table class="statement-print-head__table">
        <tbody>
          <tr><td>Client</td><td>${escapeHtml(project.client || "—")}</td><td>Date</td><td>${today}</td></tr>
          <tr><td>Site</td><td>${escapeHtml(project.site || "—")}</td><td>Prepared by</td><td>${escapeHtml(project.preparedBy || "—")}</td></tr>
        </tbody>
      </table>
    </div>

    <div class="bench statement-form">
      <section class="column">
        <div class="section-head">
          <h2 class="t-section">Project details</h2>
          <span class="section-head__meta">printed on the statement</span>
        </div>
        <div class="statement-fields">
          ${details
            .map(
              (detail) => `
            <label class="field" for="${detail.id}">
              <span class="field__label">${detail.label}</span>
              <input class="input" id="${detail.id}" type="text" autocomplete="off"
                data-bind="project" data-field="${detail.field}"
                placeholder="${escapeHtml(detail.placeholder)}"
                value="${textValue(detail.id, detail.value)}">
            </label>`
            )
            .join("")}
        </div>
      </section>

      <section class="column">
        <div class="section-head">
          <h2 class="t-section">Statement figures</h2>
          <span class="section-head__meta">INR, kg ${CO2E}</span>
        </div>
        <div class="metric-list">
          <div class="metric">
            <p class="metric__label">Material cost</p>
            <p class="metric__figure">
              <span class="metric__value">${formatNumber(summary.totalCost, 2)}</span>
              <span class="metric__unit">INR</span>
            </p>
          </div>
          <div class="metric">
            <p class="metric__label">Embodied carbon</p>
            <p class="metric__figure">
              <span class="metric__value">${formatNumber(summary.totalCarbon, 2)}</span>
              <span class="metric__unit">kg ${CO2E}</span>
            </p>
          </div>
          <div class="metric">
            <p class="metric__label">Material cost per kg ${CO2E}</p>
            <p class="metric__figure">
              <span class="metric__value">${formatNumber(costPerKg, 2)}</span>
              <span class="metric__unit">INR / kg ${CO2E}</span>
            </p>
          </div>
        </div>
      </section>
    </div>

    <div class="panel table-scroll">
      <div class="panel__head">
        <h2 class="t-panel">Material schedule</h2>
        <span class="panel__meta">${summary.materialCount} items</span>
      </div>
      <table class="table table--wide table--schedule">
        <thead>
          <tr>
            <th scope="col">No.</th>
            <th scope="col">Description</th>
            <th scope="col">Unit</th>
            <th scope="col">Quantity</th>
            <th scope="col">Rate (INR)</th>
            <th scope="col">Amount (INR)</th>
            <th scope="col">Carbon (kg ${CO2E})</th>
            <th scope="col">Share</th>
          </tr>
        </thead>
        <tbody>
          ${rows
            .map(
              (row, index) => `
            <tr>
              <td class="is-muted">${index + 1}</td>
              <td>${escapeHtml(row.name)}</td>
              <td class="is-muted">${escapeHtml(row.unit)}</td>
              <td>${formatNumber(row.quantity, 2)}</td>
              <td class="is-muted">${formatNumber(row.unitCost, 2)}</td>
              <td>${formatNumber(row.estimatedCost, 2)}</td>
              <td class="is-strong">${formatNumber(row.carbon, 2)}</td>
              <td class="is-muted">${percentOf(row.carbon, summary.totalCarbon).toFixed(2)}%</td>
            </tr>`
            )
            .join("")}
          <tr class="is-total">
            <td></td>
            <td>Total</td>
            <td></td>
            <td></td>
            <td></td>
            <td>${formatNumber(summary.totalCost, 2)}</td>
            <td>${formatNumber(summary.totalCarbon, 2)}</td>
            <td>100.00%</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="panel">
      <div class="panel__head">
        <h2 class="t-panel">Life-cycle summary</h2>
        <span class="panel__meta">kg ${CO2E}</span>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th scope="col">Stage</th>
            <th scope="col">Carbon (kg ${CO2E})</th>
          </tr>
        </thead>
        <tbody>
          <tr><td>Embodied carbon of the schedule above</td><td class="is-strong">${formatNumber(lcaResult.byStage.embodied, 2)}</td></tr>
          <tr><td>Transport</td><td>${formatNumber(lcaResult.byStage.transport, 2)}</td></tr>
          <tr><td>Operational energy</td><td>${formatNumber(lcaResult.byStage.operational, 2)}</td></tr>
          <tr><td>End of life</td><td>${formatNumber(lcaResult.byStage.endOfLife, 2)}</td></tr>
          <tr class="is-total"><td>Total life-cycle carbon</td><td>${formatNumber(lcaResult.total, 2)}</td></tr>
        </tbody>
      </table>
    </div>

    <div class="statement-foot">
      <p>
        <strong>Basis of the statement.</strong> Quantities and rates are entered by the preparer.
        Carbon is quantity multiplied by the emission factor stored for that material. Transport,
        operational energy and end-of-life are included only where inputs were entered; a zero means
        no impact was entered, not that the impact is zero. Emission factors can be illustrative or
        unverified, and this statement is a preliminary estimate, not a certified life-cycle
        assessment. Counting concrete together with its cement, sand and aggregate counts the same
        carbon twice.
      </p>
      <div class="signature-row">
        <div class="signature">Prepared by</div>
        <div class="signature">Checked by</div>
        <div class="signature">Client / authorised signatory</div>
      </div>
    </div>
  `;
}

import { calculateResearchRows, summariseResearch } from "../calc.js";
import { buildFactorCsv, downloadFile } from "../csv.js";
import { CO2E, escapeHtml, formatFactor, formatNumber, unitWithCo2e } from "../format.js";
import { emptyState, inputValue, pageHead } from "../shell.js";

/**
 * Research calculator: quantities against the catalogue's own factor units.
 * GWP and energy stay separate and are never mixed across boundaries.
 */
export function render(root, ctx) {
  const { factors, state } = ctx;

  if (state.selectedFactors.length === 0) {
    root.innerHTML = `
      ${pageHead({ title: "Research calculator" })}
      ${emptyState({
        icon: "ti-table",
        text: "No research materials selected. Choose records in the research catalogue, then enter their quantities here.",
        action: `<a class="btn btn--primary" href="#/catalogue">Research catalogue<i class="ti ti-arrow-right" aria-hidden="true"></i></a>`,
      })}
    `;
    return;
  }

  const selected = state.selectedFactors
    .map((id) => factors.find((factor) => factor.id === id))
    .filter(Boolean);

  const rows = calculateResearchRows(
    selected.map((factor) => ({
      ...factor,
      quantity: state.factorQuantities[factor.id] ?? 0,
    }))
  );

  const summary = summariseResearch(rows);

  root.innerHTML = `
    ${pageHead({
      title: "Research calculator",
      meta: `${rows.length} selected`,
      actions: `
        <button class="btn btn--outline" data-action="download-factors">
          <i class="ti ti-download" aria-hidden="true"></i>Download research CSV
        </button>
        <a class="btn btn--outline" href="#/catalogue">Research catalogue</a>
      `,
    })}

    <section class="notice">
      <i class="ti ti-info-circle notice__icon" aria-hidden="true"></i>
      <p class="notice__text">
        Factors come from Chaudhary &amp; Akhtar (2023), Supporting Information Table S3.
        Boundary ${escapeHtml(summary.boundary || "cradle-to-gate")}, geography
        ${escapeHtml(summary.geography || "India")}. Only the selected material factors are reported;
        transport, onsite construction, operational and end-of-life impacts are not added here.
      </p>
    </section>

    ${
      summary.mixedBoundary || summary.mixedGeography
        ? `<section class="notice notice--warn">
            <i class="ti ti-alert-triangle notice__icon" aria-hidden="true"></i>
            <p class="notice__text">The selected factors do not share one boundary and geography. These totals combine different scope assumptions.</p>
          </section>`
        : ""
    }

    <div class="bench">
      <section class="column">
        <div class="section-head">
          <h2 class="t-section">Selected materials</h2>
          <span class="section-head__meta">quantity in the factor unit</span>
        </div>

        <div class="calc-list">
          ${rows
            .map((row, index) => {
              const id = `factor-qty-${index}`;
              const quantityUnit = row.gwpUnit.includes("/")
                ? row.gwpUnit.split("/").slice(1).join("/").trim()
                : row.gwpUnit;
              return `
              <div class="calc-row">
                <div class="calc-row__main">
                  <p class="calc-row__id">${row.id}</p>
                  <p class="calc-row__name">${escapeHtml(row.name)}</p>
                  <p class="calc-row__factor">GWP ${formatFactor(row.gwpFactor)} ${unitWithCo2e(row.gwpUnit)}</p>
                </div>
                <label class="field calc-row__field" for="${id}">
                  <span class="field__label">Quantity (${unitWithCo2e(quantityUnit)})</span>
                  <input class="input" id="${id}" type="text" inputmode="decimal" autocomplete="off"
                    data-bind="factor-qty" data-id="${row.id}"
                    value="${inputValue(ctx, id, row.quantity)}">
                </label>
                <div class="calc-row__result">
                  <span class="field__label">Carbon</span>
                  <p><strong>${formatNumber(row.carbon, 2)}</strong> kg ${CO2E}</p>
                </div>
              </div>`;
            })
            .join("")}
        </div>
      </section>

      <section class="column">
        <div class="section-head">
          <h2 class="t-section">Research totals</h2>
          <span class="section-head__meta">kg ${CO2E}, MJ</span>
        </div>

        <div class="metric-list">
          <div class="metric">
            <p class="metric__label">Total GWP</p>
            <p class="metric__figure">
              <span class="metric__value">${formatNumber(summary.totalCarbon, 2)}</span>
              <span class="metric__unit">kg ${CO2E}</span>
            </p>
          </div>
          <div class="metric">
            <p class="metric__label">Total energy</p>
            <p class="metric__figure">
              <span class="metric__value">${formatNumber(summary.totalEnergy, 2)}</span>
              <span class="metric__unit">MJ</span>
            </p>
          </div>
        </div>

        <div class="panel" style="margin-top:16px">
          <div class="panel__head">
            <h3 class="t-panel">Scope</h3>
            <span class="panel__meta">stored record values</span>
          </div>
          <dl class="kv-list" style="margin:0;padding:8px 16px 16px">
            <div class="kv"><dt class="kv__key">Boundary</dt><dd class="kv__value">${escapeHtml(summary.boundary)}</dd></div>
            <div class="kv"><dt class="kv__key">Geography</dt><dd class="kv__value">${escapeHtml(summary.geography)}</dd></div>
            <div class="kv"><dt class="kv__key">Material count</dt><dd class="kv__value">${summary.count}</dd></div>
          </dl>
        </div>

        <button class="btn btn--outline btn--block" style="margin-top:16px" type="button" data-action="clear-factors">
          <i class="ti ti-x" aria-hidden="true"></i>Clear selected materials
        </button>
      </section>
    </div>

    <div class="panel table-scroll">
      <div class="panel__head">
        <h3 class="t-panel">Research calculation results</h3>
        <span class="panel__meta">GWP and energy kept separate</span>
      </div>
      <table class="table table--wide">
        <thead>
          <tr>
            <th scope="col">Material</th>
            <th scope="col">Quantity</th>
            <th scope="col">Quantity unit</th>
            <th scope="col">GWP factor</th>
            <th scope="col">Carbon (kg ${CO2E})</th>
            <th scope="col">Energy factor</th>
            <th scope="col">Energy (MJ)</th>
            <th scope="col">Verification</th>
          </tr>
        </thead>
        <tbody>
          ${rows
            .map((row) => {
              const quantityUnit = row.gwpUnit.includes("/")
                ? row.gwpUnit.split("/").slice(1).join("/").trim()
                : row.gwpUnit;
              return `
              <tr>
                <td>${row.id} — ${escapeHtml(row.name)}</td>
                <td>${formatNumber(row.quantity, 2)}</td>
                <td class="is-muted">${unitWithCo2e(quantityUnit)}</td>
                <td class="is-muted">${formatFactor(row.gwpFactor)} ${unitWithCo2e(row.gwpUnit)}</td>
                <td class="is-strong">${formatNumber(row.carbon, 2)}</td>
                <td class="is-muted">${formatFactor(row.energyFactor)} ${escapeHtml(row.energyUnit)}</td>
                <td class="is-strong">${formatNumber(row.energy, 2)}</td>
                <td class="is-muted">${escapeHtml(row.verificationStatus)}</td>
              </tr>`;
            })
            .join("")}
          <tr class="is-total">
            <td>Total</td>
            <td></td>
            <td></td>
            <td></td>
            <td>${formatNumber(summary.totalCarbon, 2)}</td>
            <td></td>
            <td>${formatNumber(summary.totalEnergy, 2)}</td>
            <td></td>
          </tr>
        </tbody>
      </table>
    </div>
  `;
}

export function handleAction(action, ctx) {
  if (action !== "download-factors") return false;

  const { factors, state } = ctx;
  const selected = state.selectedFactors
    .map((id) => factors.find((factor) => factor.id === id))
    .filter(Boolean);

  if (selected.length === 0) return true;

  const rows = calculateResearchRows(
    selected.map((factor) => ({
      ...factor,
      quantity: state.factorQuantities[factor.id] ?? 0,
    }))
  );

  downloadFile("research_material_calculation.csv", buildFactorCsv(rows));
  return true;
}

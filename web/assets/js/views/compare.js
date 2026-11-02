import { calculateFootprint, summariseFootprint } from "../calc.js";
import { downloadFile, toCsv } from "../csv.js";
import { CO2E, escapeHtml, formatNumber } from "../format.js";
import { footerNote, inputValue, pageHead } from "../shell.js";
import { setScenarioB } from "../store.js";

/**
 * Compare scenarios: the project estimate as column A, an editable alternative
 * as column B. Only quantities differ — rates and emission factors are shared,
 * so a difference in the totals is a difference in what is being built.
 */
export function render(root, ctx) {
  const { materials, state, derived } = ctx;
  const { rows: baseRows, summary: baseSummary } = ctx.derived;

  const alternativeRows = calculateFootprint(
    materials.map((material) => ({
      name: material.name,
      unit: material.unit,
      quantity: state.scenarioB[material.name] ?? state.quantities[material.name] ?? 0,
      unitCost: state.unitCosts[material.name] ?? 0,
      emissionFactor: material.emissionFactor,
    }))
  );

  const alternativeSummary = summariseFootprint(alternativeRows);

  const deltaCarbon = alternativeSummary.totalCarbon - baseSummary.totalCarbon;
  const deltaCost = alternativeSummary.totalCost - baseSummary.totalCost;
  const carbonPercent =
    baseSummary.totalCarbon > 0 ? (deltaCarbon / baseSummary.totalCarbon) * 100 : 0;
  const costPercent = baseSummary.totalCost > 0 ? (deltaCost / baseSummary.totalCost) * 100 : 0;
  const costPerKgAvoided = deltaCarbon < 0 ? deltaCost / -deltaCarbon : null;

  root.innerHTML = `
    ${pageHead({
      title: "Compare scenarios",
      meta: "baseline against alternative",
      actions: `
        <button class="btn btn--outline" type="button" data-action="copy-a-to-b">
          <i class="ti ti-copy" aria-hidden="true"></i>Copy baseline to B
        </button>
        <button class="btn btn--outline" type="button" data-action="download-comparison">
          <i class="ti ti-download" aria-hidden="true"></i>Download comparison (CSV)
        </button>
      `,
    })}

    <section class="notice">
      <i class="ti ti-columns-2 notice__icon" aria-hidden="true"></i>
      <p class="notice__text">
        Column <strong>A</strong> is the project estimate. Column <strong>B</strong> starts equal to
        it — change the quantities there to test an alternative. Both columns use the same unit costs
        and emission factors, so only the quantities differ.
      </p>
    </section>

    <div class="compare-summary">
      <div class="metric metric--stack">
        <p class="metric__label">Change in embodied carbon</p>
        <p class="metric__figure">
          <span class="metric__value ${deltaClass(deltaCarbon)}">${signed(deltaCarbon, 2)}</span>
          <span class="metric__unit">kg ${CO2E}</span>
        </p>
        <p class="metric__sub"><span class="${deltaClass(deltaCarbon)}">${signed(
          carbonPercent,
          2
        )}%</span> against the baseline</p>
      </div>
      <div class="metric metric--stack">
        <p class="metric__label">Change in material cost</p>
        <p class="metric__figure">
          <span class="metric__value ${deltaClass(deltaCost)}">${signed(deltaCost, 2)}</span>
          <span class="metric__unit">INR</span>
        </p>
        <p class="metric__sub"><span class="${deltaClass(deltaCost)}">${signed(
          costPercent,
          2
        )}%</span> against the baseline</p>
      </div>
      <div class="metric metric--stack">
        <p class="metric__label">Cost per kg ${CO2E} avoided</p>
        <p class="metric__figure">
          <span class="metric__value">${
            costPerKgAvoided === null ? "—" : formatNumber(costPerKgAvoided, 2)
          }</span>
          <span class="metric__unit">INR / kg ${CO2E}</span>
        </p>
        <p class="metric__sub">${
          costPerKgAvoided === null
            ? "column B does not emit less"
            : costPerKgAvoided <= 0
              ? "column B emits less and costs less"
              : "extra spend for each kg avoided"
        }</p>
      </div>
    </div>

    <div class="panel table-scroll">
      <div class="panel__head">
        <h2 class="t-panel">Material quantities, carbon and cost</h2>
        <span class="panel__meta">INR, kg ${CO2E}</span>
      </div>
      <table class="table table--wide table--compare">
        <thead>
          <tr>
            <th scope="col">Material</th>
            <th scope="col">Quantity A</th>
            <th scope="col">Quantity B</th>
            <th scope="col">Carbon A</th>
            <th scope="col">Carbon B</th>
            <th scope="col">Carbon change</th>
            <th scope="col">Cost A</th>
            <th scope="col">Cost B</th>
            <th scope="col">Cost change</th>
          </tr>
        </thead>
        <tbody>
          ${baseRows
            .map((baseRow, index) => {
              const alternative = alternativeRows[index];
              const carbonDelta = alternative.carbon - baseRow.carbon;
              const costDelta = alternative.estimatedCost - baseRow.estimatedCost;
              const inputId = `scenario-b-${index}`;
              return `
              <tr>
                <td>${escapeHtml(baseRow.name)} <span class="table__unit">${escapeHtml(
                  baseRow.unit
                )}</span></td>
                <td class="is-muted">${formatNumber(baseRow.quantity, 2)}</td>
                <td class="cell-input">
                  <input class="input input--cell" id="${inputId}" type="text" inputmode="decimal"
                    autocomplete="off" data-bind="scenario-b-qty"
                    data-material="${escapeHtml(baseRow.name)}"
                    aria-label="Alternative quantity for ${escapeHtml(baseRow.name)}"
                    value="${inputValue(ctx, inputId, alternative.quantity)}">
                </td>
                <td class="is-muted">${formatNumber(baseRow.carbon, 2)}</td>
                <td>${formatNumber(alternative.carbon, 2)}</td>
                <td class="${deltaClass(carbonDelta)}">${signed(carbonDelta, 2)}</td>
                <td class="is-muted">${formatNumber(baseRow.estimatedCost, 2)}</td>
                <td>${formatNumber(alternative.estimatedCost, 2)}</td>
                <td class="${deltaClass(costDelta)}">${signed(costDelta, 2)}</td>
              </tr>`;
            })
            .join("")}
          <tr class="is-total">
            <td>Total</td>
            <td>${formatNumber(totalQuantity(baseRows), 2)}</td>
            <td>${formatNumber(totalQuantity(alternativeRows), 2)}</td>
            <td>${formatNumber(baseSummary.totalCarbon, 2)}</td>
            <td>${formatNumber(alternativeSummary.totalCarbon, 2)}</td>
            <td class="${deltaClass(deltaCarbon)}">${signed(deltaCarbon, 2)}</td>
            <td>${formatNumber(baseSummary.totalCost, 2)}</td>
            <td>${formatNumber(alternativeSummary.totalCost, 2)}</td>
            <td class="${deltaClass(deltaCost)}">${signed(deltaCost, 2)}</td>
          </tr>
        </tbody>
      </table>
    </div>

    ${footerNote({
      text: "Both columns count concrete as one material. If a quantity already includes cement, sand and aggregate, do not add those ingredients separately in either column.",
      actionLabel: "Project statement",
      actionRoute: "statement",
    })}
  `;
}

function totalQuantity(rows) {
  return rows.reduce((sum, row) => sum + row.quantity, 0);
}

function deltaClass(value) {
  if (Math.abs(value) < 1e-9) return "delta-flat";
  return value > 0 ? "delta-up" : "delta-down";
}

function signed(value, decimals = 2) {
  const sign = value > 0 ? "+" : value < 0 ? "−" : "";
  return `${sign}${formatNumber(Math.abs(value), decimals)}`;
}

export function handleAction(action, ctx) {
  if (action === "copy-a-to-b") {
    const { materials, state } = ctx;
    setScenarioB(
      materials.reduce((draft, material) => {
        draft[material.name] = state.quantities[material.name] ?? 0;
        return draft;
      }, {})
    );
    return true;
  }

  if (action === "download-comparison") {
    const { materials, state, derived } = ctx;
    const alternativeRows = calculateFootprint(
      materials.map((material) => ({
        name: material.name,
        unit: material.unit,
        quantity: state.scenarioB[material.name] ?? state.quantities[material.name] ?? 0,
        unitCost: state.unitCosts[material.name] ?? 0,
        emissionFactor: material.emissionFactor,
      }))
    );

    const csv = toCsv(
      [
        "material",
        "unit",
        "quantity_a",
        "quantity_b",
        "carbon_a",
        "carbon_b",
        "carbon_change",
        "cost_a",
        "cost_b",
        "cost_change",
      ],
      derived.rows.map((baseRow, index) => {
        const alternative = alternativeRows[index];
        return [
          baseRow.name,
          baseRow.unit,
          baseRow.quantity,
          alternative.quantity,
          baseRow.carbon,
          alternative.carbon,
          alternative.carbon - baseRow.carbon,
          baseRow.estimatedCost,
          alternative.estimatedCost,
          alternative.estimatedCost - baseRow.estimatedCost,
        ];
      })
    );

    downloadFile("scenario_comparison.csv", "\ufeff" + csv + "\n");
    return true;
  }

  return false;
}

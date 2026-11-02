import { STAGES } from "../calc.js";
import { CO2E, escapeHtml, formatNumber, percentOf } from "../format.js";
import { footerNote, pageHead, valueFor } from "../shell.js";

/**
 * Life-cycle assessment: the four stage contributions with the assumptions of
 * one selected stage open beside them.
 */
export function render(root, ctx) {
  const { state, derived } = ctx;
  const { lcaResult, summary } = derived;
  const activeStage = state.activeStage;
  const stage = STAGES.find((entry) => entry.key === activeStage) || STAGES[1];

  root.innerHTML = `
    ${pageHead({
      title: "Life-cycle assessment",
      actions: `
        <button class="btn btn--outline" data-action="download-analysis">
          <i class="ti ti-download" aria-hidden="true"></i>Download detailed results (CSV)
        </button>
      `,
    })}

    <section class="notice notice--warn">
      <i class="ti ti-alert-triangle notice__icon" aria-hidden="true"></i>
      <div class="notice__text">
        <p>Embodied emission factors are illustrative or unverified. Confirm each factor before comparing options.</p>
        <p>Zero-valued inputs mean no impact has been entered for that stage, not that the impact is zero.</p>
      </div>
    </section>

    <div class="bench bench--lca">
      <div class="column column--gap">

        <div class="total-card">
          <div>
            <p class="total-card__label">Estimated total life-cycle carbon</p>
            <p class="total-card__figure">
              <span class="total-card__value">${formatNumber(lcaResult.total, 2)}</span>
              <span class="metric__unit">kg ${CO2E}</span>
            </p>
          </div>
          <div class="total-card__side">
            <p class="total-card__label">Building lifetime</p>
            <p class="total-card__side-value">${formatNumber(state.lca.lifetimeYears, 0)} years</p>
          </div>
        </div>

        <div class="breakdown">
          <div class="breakdown__head">
            <h2 class="t-panel">Carbon by life-cycle stage</h2>
            <span class="panel__meta">kg ${CO2E}</span>
          </div>
          <div class="stage-chart">
            ${STAGES.map((entry) => {
              const value = lcaResult.byStage[entry.key];
              const share = percentOf(value, lcaResult.total);
              return `
                <div class="stage-chart__row">
                  <span class="stage-chart__label">${entry.label}</span>
                  <span class="stage-chart__track${value > 0 ? "" : " is-empty"}">
                    <span class="stage-chart__fill" style="width:${share.toFixed(1)}%"></span>
                  </span>
                  <span class="stage-chart__value${value > 0 ? " is-strong" : ""}">${formatNumber(value, 2)}</span>
                </div>`;
            }).join("")}
          </div>
        </div>

        <div class="stage-list">
          <div class="stage-list__head">
            <span>Life-cycle stage</span>
            <span>Carbon (kg ${CO2E})</span>
            <span>Share of total</span>
          </div>
          ${STAGES.map((entry) => {
            const value = lcaResult.byStage[entry.key];
            const isActive = entry.key === activeStage;
            return `
              <button class="stage-row${isActive ? " is-active" : ""}" type="button"
                data-action="select-stage" data-stage="${entry.key}"
                aria-pressed="${isActive}">
                <span class="stage-row__main">
                  <span class="stage-row__name"><i class="ti ${entry.icon}" aria-hidden="true"></i>${entry.label}</span>
                  <span class="stage-row__sub">${entry.sub}</span>
                </span>
                <span class="stage-row__value">${formatNumber(value, 2)}</span>
                <span class="stage-row__share">${percentOf(value, lcaResult.total).toFixed(2)}%${
                  isActive ? '<i class="ti ti-chevron-right" aria-hidden="true"></i>' : ""
                }</span>
              </button>`;
          }).join("")}
        </div>
      </div>

      <div class="inspector inspector--stage">
        <div class="inspector__head">
          <span class="inspector__icon"><i class="ti ${stage.icon}" aria-hidden="true"></i></span>
          <h2 class="inspector__title">${stageInspectorTitle(stage.key)}</h2>
        </div>
        ${stageBody(stage.key, ctx)}
      </div>
    </div>

    ${footerNote({
      text: "<strong>Possible double counting.</strong> If the concrete quantity already includes cement, sand and aggregate, counting both concrete and its ingredients counts the same embodied carbon twice.",
      actionLabel: "Project estimate",
      actionRoute: "estimate",
    })}
  `;

  void summary;
}

function stageInspectorTitle(key) {
  if (key === "embodied") return "Embodied carbon";
  if (key === "transport") return "Transport emissions";
  if (key === "operational") return "Operational electricity";
  return "End-of-life estimate";
}

function field(ctx, { label, id, value, field: key, decimals = 2 }) {
  return `
    <label class="field" for="${id}">
      <span class="field__label">${label}</span>
      <input class="input" id="${id}" type="text" inputmode="decimal" autocomplete="off"
        data-bind="lca" data-field="${key}" value="${valueFor(ctx, id, value, decimals)}">
    </label>
  `;
}

function stageBody(key, ctx) {
  const { state, derived } = ctx;
  const { lcaResult, summary, rows } = derived;

  if (key === "embodied") {
    return `
      <div class="inspector__table">
        ${rows
          .map(
            (row) => `
          <div class="inspector__table-row">
            <span>${escapeHtml(row.name)}</span>
            <span>${formatNumber(row.carbon, 2)}</span>
          </div>`
          )
          .join("")}
        <div class="inspector__table-row">
          <span class="t-strong">Total embodied carbon</span>
          <span class="t-strong">${formatNumber(summary.totalCarbon, 2)}</span>
        </div>
      </div>
      <a class="btn btn--outline btn--block" style="margin-top:16px" href="#/estimate">
        Edit material inputs<i class="ti ti-arrow-right" aria-hidden="true"></i>
      </a>
      <div class="inspector__note">
        Embodied carbon is quantity multiplied by emission factor for each material listed above.
      </div>
    `;
  }

  if (key === "transport") {
    return `
      <div class="inspector__fields">
        ${field(ctx, {
          label: "Transported material mass (tonnes)",
          id: "lca-transport-tonnes",
          value: state.lca.transportTonnes,
          field: "transportTonnes",
        })}
        ${field(ctx, {
          label: "One-way transport distance (km)",
          id: "lca-transport-distance",
          value: state.lca.transportDistanceKm,
          field: "transportDistanceKm",
        })}
        ${field(ctx, {
          label: `Transport factor (kg ${CO2E}/tonne-km)`,
          id: "lca-transport-factor",
          value: state.lca.transportFactor,
          field: "transportFactor",
          decimals: 4,
        })}
      </div>
      <p class="inspector__hint">Enter a verified factor for the relevant vehicle and fuel.</p>
      <div class="inspector__calc">
        <p class="inspector__calc-label">Calculated transport carbon</p>
        <p class="inspector__calc-figure">
          <span class="inspector__calc-value">${formatNumber(lcaResult.byStage.transport, 2)}</span>
          <span class="metric__unit">kg ${CO2E}</span>
        </p>
        <p class="inspector__formula">mass × distance × factor</p>
      </div>
      <div class="inspector__note">Transport mass is entered separately from material quantities.</div>
    `;
  }

  if (key === "operational") {
    return `
      <div class="inspector__fields">
        ${field(ctx, {
          label: "Annual electricity use (kWh)",
          id: "lca-annual-energy",
          value: state.lca.annualEnergyKwh,
          field: "annualEnergyKwh",
        })}
        ${field(ctx, {
          label: "Building lifetime (years)",
          id: "lca-lifetime",
          value: state.lca.lifetimeYears,
          field: "lifetimeYears",
          decimals: 0,
        })}
        ${field(ctx, {
          label: `Electricity factor (kg ${CO2E}/kWh)`,
          id: "lca-electricity-factor",
          value: state.lca.electricityFactor,
          field: "electricityFactor",
          decimals: 4,
        })}
      </div>
      <p class="inspector__hint">Enter a verified grid emission factor for the relevant location.</p>
      <div class="inspector__calc">
        <p class="inspector__calc-label">Calculated operational carbon</p>
        <p class="inspector__calc-figure">
          <span class="inspector__calc-value">${formatNumber(lcaResult.byStage.operational, 2)}</span>
          <span class="metric__unit">kg ${CO2E}</span>
        </p>
        <p class="inspector__formula">annual electricity × lifetime × grid factor</p>
      </div>
      <div class="inspector__note">Operational carbon covers the entered electricity use over the stated building lifetime.</div>
    `;
  }

  return `
    <div class="inspector__fields">
      ${field(ctx, {
        label: `End-of-life emissions (kg ${CO2E})`,
        id: "lca-end-of-life",
        value: state.lca.endOfLifeKg,
        field: "endOfLifeKg",
      })}
    </div>
    <p class="inspector__hint">Enter a documented estimate; zero means no impact has been entered.</p>
    <div class="inspector__calc">
      <p class="inspector__calc-label">Calculated end-of-life carbon</p>
      <p class="inspector__calc-figure">
        <span class="inspector__calc-value">${formatNumber(lcaResult.byStage.endOfLife, 2)}</span>
        <span class="metric__unit">kg ${CO2E}</span>
      </p>
      <p class="inspector__formula">user-entered estimate</p>
    </div>
    <div class="inspector__note">No demolition factor or recovery credit is assumed anywhere in this stage.</div>
  `;
}

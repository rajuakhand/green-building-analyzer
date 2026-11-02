import { CO2E, formatNumber } from "../format.js";
import { footerNote, pageHead } from "../shell.js";

/**
 * Method: the exact formulas, the boundary and the interpretation limits.
 * Written so a reader can reproduce every number the app shows.
 */
export function render(root, ctx) {
  const { derived } = ctx;
  const { summary, lcaResult } = derived;

  const formulas = [
    ["Estimated material carbon", "quantity × emission factor"],
    ["Estimated material cost", "quantity × unit cost"],
    ["Transport carbon", "mass (tonnes) × distance (km) × transport factor"],
    ["Operational energy carbon", "annual kWh × lifetime (years) × grid factor"],
    ["End-of-life carbon", "user-entered estimate"],
    ["Total life-cycle carbon", "embodied + transport + operational + end-of-life"],
  ];

  root.innerHTML = `
    ${pageHead({
      title: "Method",
      meta: `current estimate ${formatNumber(lcaResult.total, 2)} kg ${CO2E}`,
    })}

    <section class="notice notice--warn">
      <i class="ti ti-alert-triangle notice__icon" aria-hidden="true"></i>
      <p class="notice__text">
        <strong>These are preliminary estimates.</strong> They are not a certified life-cycle
        assessment and must not be presented as one.
      </p>
    </section>

    <div class="bench">
      <section class="column">
        <div class="panel">
          <div class="panel__head">
            <h2 class="t-panel">Calculation</h2>
            <span class="panel__meta">applied to every view</span>
          </div>
          <div style="padding:4px 16px 16px">
            <div class="formula-list">
              ${formulas
                .map(
                  ([label, expr]) => `
                <div class="formula">
                  <span class="formula__label">${label}</span>
                  <span class="formula__expr">${expr}</span>
                </div>`
                )
                .join("")}
            </div>
            <div class="prose" style="margin-top:16px">
              <p>Each material row is calculated on its own, then summed. Nothing is averaged and no
              factor is applied to a material it was not published for.</p>
            </div>
          </div>
        </div>

        <div class="panel" style="margin-top:16px">
          <div class="panel__head">
            <h2 class="t-panel">Unit rule</h2>
            <span class="panel__meta">quantity must match the factor denominator</span>
          </div>
          <div class="prose" style="padding:12px 16px 16px">
            <p>A quantity uses the denominator of its own factor. A factor published per tonne is
            entered in tonnes, one published per quintal in quintals, one published per thousand
            bricks in thousands. No automatic conversion is applied.</p>
            <p>The research calculator reads the unit straight from the factor record, so the label
            beside the field is the denominator of the factor that will be multiplied into it.</p>
            <p>Where a quantity unit and a factor denominator disagree, the calculation is wrong even
            if the arithmetic is right.</p>
          </div>
        </div>
      </section>

      <section class="column">
        <div class="panel">
          <div class="panel__head">
            <h2 class="t-panel">Boundary</h2>
            <span class="panel__meta">what the total covers</span>
          </div>
          <div class="prose" style="padding:12px 16px 16px">
            <p><strong>Included</strong></p>
            <ul>
              <li>Embodied carbon of the materials listed in Project estimate</li>
              <li>Transport, when mass, distance and a factor are entered</li>
              <li>Operational electricity, when use and a grid factor are entered</li>
              <li>End-of-life carbon, when an estimate is entered</li>
            </ul>
            <p style="margin-top:8px"><strong>Not included</strong></p>
            <ul>
              <li>Maintenance, repair and replacement over the building's life</li>
              <li>Water, site energy and construction waste apart from what is entered</li>
              <li>Demolition credits, reuse or recycling benefits</li>
              <li>Any stage left at zero, which means no impact was entered</li>
            </ul>
            <p style="margin-top:8px">Research factors are cradle-to-gate: material extraction and
            manufacture only, up to the factory gate.</p>
          </div>
        </div>

        <div class="panel" style="margin-top:16px">
          <div class="panel__head">
            <h2 class="t-panel">Reading the numbers</h2>
            <span class="panel__meta">current state</span>
          </div>
          <div class="prose" style="padding:12px 16px 16px">
            <p>Two totals are comparable only when they share a boundary, a geography and a unit
            basis. Comparing a cradle-to-gate factor with a cradle-to-site figure compares different
            things.</p>
            <p>Emission factors can be illustrative or unverified, which is stated wherever results
            appear. Confirm the source, the reference year and the system boundary before quoting a
            figure in a report.</p>
            <p>Counting concrete together with its cement, sand and aggregate counts the same carbon
            twice. Use one or the other.</p>
          </div>
        </div>

        <div class="metric" style="margin-top:16px">
          <p class="metric__label">Current material carbon</p>
          <p class="metric__figure">
            <span class="metric__value">${formatNumber(summary.totalCarbon, 2)}</span>
            <span class="metric__unit">kg ${CO2E}</span>
          </p>
        </div>
      </section>
    </div>

    ${footerNote({
      text: "<strong>Every factor has a source row.</strong> The data sources view lists the publication, boundary, geography and verification status behind each factor.",
      actionLabel: "Data sources",
      actionRoute: "sources",
    })}
  `;
}

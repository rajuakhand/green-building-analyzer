import { STAGES } from "../calc.js";
import { CO2E, escapeHtml, formatNumber } from "../format.js";
import { pageHead } from "../shell.js";

const LIVE_APP_URL =
  "https://green-building-analyzer-xbwtufdrcywjjthgika3iw.streamlit.app/";

/**
 * AI recommendations. The advisor is a Gemini call that needs the Python
 * server, so this page shows exactly what would be sent and the configuration
 * state the app reports when no key is present.
 */
export function render(root, ctx) {
  const { state, derived } = ctx;
  const { rows, summary, lcaResult } = derived;

  root.innerHTML = `
    ${pageHead({
      title: "AI recommendations",
      meta: "Gemini",
      actions: `<a class="btn btn--outline" href="${LIVE_APP_URL}" target="_blank" rel="noopener noreferrer">
        <i class="ti ti-external-link" aria-hidden="true"></i>Open in Streamlit app
      </a>`,
    })}

    <section class="notice">
      <i class="ti ti-info-circle notice__icon" aria-hidden="true"></i>
      <p class="notice__text">
        The advisor receives the material results and project totals below, then returns a written
        report on carbon reduction, material selection, cost and data limitations. It does not receive
        the advanced life-cycle inputs.
      </p>
    </section>

    <div class="bench">
      <section class="column">
        <div class="section-head">
          <h2 class="t-section">Data sent to the advisor</h2>
          <span class="section-head__meta">${summary.materialCount} materials</span>
        </div>

        <div class="panel">
          <div class="panel__head">
            <h3 class="t-panel">Material results</h3>
            <span class="panel__meta">INR, kg ${CO2E}</span>
          </div>
          <div style="padding:4px 16px 12px">
          <table class="payload-table">
            <thead>
              <tr>
                <th scope="col">Material</th>
                <th scope="col">Quantity</th>
                <th scope="col">Carbon (kg ${CO2E})</th>
                <th scope="col">Cost (INR)</th>
              </tr>
            </thead>
            <tbody>
              ${rows
                .map(
                  (row) => `
                <tr>
                  <td>${escapeHtml(row.name)}</td>
                  <td>${formatNumber(row.quantity, 2)} ${escapeHtml(row.unit)}</td>
                  <td>${formatNumber(row.carbon, 2)}</td>
                  <td>${formatNumber(row.estimatedCost, 2)}</td>
                </tr>`
                )
                .join("")}
            </tbody>
          </table>
          </div>
        </div>

        <div class="metric-list">
          <div class="metric">
            <p class="metric__label">Total estimated carbon</p>
            <p class="metric__figure">
              <span class="metric__value">${formatNumber(summary.totalCarbon, 2)}</span>
              <span class="metric__unit">kg ${CO2E}</span>
            </p>
          </div>
          <div class="metric">
            <p class="metric__label">Total estimated material cost</p>
            <p class="metric__figure">
              <span class="metric__value">${formatNumber(summary.totalCost, 2)}</span>
              <span class="metric__unit">INR</span>
            </p>
          </div>
        </div>
      </section>

      <section class="column">
        <div class="section-head">
          <h2 class="t-section">Generated report</h2>
          <span class="section-head__meta">${state.aiRequested ? "not available" : "not generated"}</span>
        </div>

        ${
          state.aiRequested
            ? `<div class="advisor-output">
                <p><strong>Gemini API key not found.</strong> Configure <code>GOOGLE_API_KEY</code> or
                <code>GEMINI_API_KEY</code> in Streamlit Secrets or environment variables.</p>
                <p style="margin-top:12px">This static build has no server, so the request can only run in the
                Streamlit app. The button and the message above are the states the app reports today.</p>
              </div>`
            : `<div class="advisor-output">
                <p>No recommendations generated yet.</p>
                <p style="margin-top:12px">Generation needs a Gemini API key on the server side. Nothing is
                invented here — the panel stays empty until a real response comes back.</p>
              </div>`
        }

        <button class="btn btn--primary btn--block" style="margin-top:16px" type="button" data-action="generate-ai">
          <i class="ti ti-sparkles" aria-hidden="true"></i>Generate AI recommendations
        </button>

        <div class="panel" style="margin-top:16px">
          <div class="panel__head">
            <h3 class="t-panel">Not sent to the advisor</h3>
            <span class="panel__meta">life-cycle stages</span>
          </div>
          <dl class="kv-list" style="margin:0;padding:8px 16px 16px">
            ${STAGES.filter((stage) => stage.key !== "embodied")
              .map(
                (stage) =>
                  `<div class="kv"><dt class="kv__key">${stage.label}</dt><dd class="kv__value">${formatNumber(
                    lcaResult.byStage[stage.key],
                    2
                  )} kg ${CO2E}</dd></div>`
              )
              .join("")}
          </dl>
        </div>
      </section>
    </div>
  `;
}

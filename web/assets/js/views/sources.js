import { CO2E, escapeHtml, formatFactor, formatNumber } from "../format.js";
import { pageHead } from "../shell.js";

const PAPER_URL = "https://pubs.acs.org/doi/10.1021/acsenvironau.2c00035";

/**
 * Data sources: the stored provenance of both datasets — demo pricing records
 * and the 78 research characterization factors, plus the source registry.
 * Every value here comes from the CSV files, nothing is added.
 */
export function render(root, ctx) {
  const { materials, factors, sources } = ctx;

  const statusCounts = new Map();
  factors.forEach((factor) => {
    const status = factor.verificationStatus || "not recorded";
    statusCounts.set(status, (statusCounts.get(status) || 0) + 1);
  });

  const geography = [...new Set(factors.map((factor) => factor.geography))];
  const boundaries = [...new Set(factors.map((factor) => factor.boundary))];

  root.innerHTML = `
    ${pageHead({
      title: "Data sources",
      meta: `${materials.length} priced materials, ${factors.length} research factors`,
    })}

    <section class="notice">
      <i class="ti ti-file-description notice__icon" aria-hidden="true"></i>
      <p class="notice__text">
        <strong>Research factors</strong> come from Chaudhary &amp; Akhtar (2023), ACS Environ. Au
        3:94–104, Supporting Information Table S3. Each record states its own boundary and geography.
        The pricing records are separate and are not part of that publication.
      </p>
    </section>

    <div class="panel table-scroll">
      <div class="panel__head">
        <h2 class="t-panel">Demo pricing dataset</h2>
        <span class="panel__meta">data/materials.csv</span>
      </div>
      <table class="table table--wide">
        <thead>
          <tr>
            <th scope="col">Material</th>
            <th scope="col">Unit</th>
            <th scope="col">Emission factor</th>
            <th scope="col">Unit cost (INR)</th>
            <th scope="col">Source</th>
            <th scope="col">Verification status</th>
          </tr>
        </thead>
        <tbody>
          ${materials
            .map((material) => {
              const hasUrl = /^https?:\/\//i.test(material.sourceUrl || "");
              return `
              <tr>
                <td>${escapeHtml(material.name)}</td>
                <td class="is-muted">${escapeHtml(material.unit)}</td>
                <td class="is-strong">${formatFactor(material.emissionFactor)} kg ${CO2E}/${escapeHtml(
                material.unit
              )}</td>
                <td>${formatNumber(material.unitCost, 2)}</td>
                <td class="is-muted">${
                  hasUrl
                    ? `<a class="source-link" href="${escapeHtml(material.sourceUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(
                        material.source
                      )}</a>`
                    : escapeHtml(material.source || "not recorded")
                }</td>
                <td class="is-muted">${escapeHtml(material.verificationStatus || "not recorded")}</td>
              </tr>`;
            })
            .join("")}
        </tbody>
      </table>
    </div>

    <div class="panel">
      <div class="panel__head">
        <h2 class="t-panel">Research factor catalogue</h2>
        <span class="panel__meta">data/material_factors.csv</span>
      </div>
      <div style="padding:12px 16px 16px">
        <div class="count-row">
          <div class="count">
            <p class="count__value">${factors.length}</p>
            <p class="count__label">records</p>
          </div>
          ${[...statusCounts.entries()]
            .map(
              ([status, count]) => `
            <div class="count">
              <p class="count__value">${count}</p>
              <p class="count__label">${escapeHtml(status)}</p>
            </div>`
            )
            .join("")}
        </div>
        <div class="prose" style="margin-top:16px">
          <p>Boundary recorded on the records: ${boundaries.map(escapeHtml).join(", ")}. Geography:
          ${geography.map(escapeHtml).join(", ")}.</p>
          <p>A record marked <strong>Needs-review</strong> has not been confirmed against its
          original source. A record marked <strong>Verified-from-paper-SI</strong> was read from the
          paper's supporting information, which is not the same as an independently audited
          environmental product declaration.</p>
          <p><a class="source-link" href="${PAPER_URL}" target="_blank" rel="noopener noreferrer">Open the paper on ACS</a></p>
        </div>
      </div>
    </div>

    ${
      sources.length
        ? `
    <div class="panel table-scroll">
      <div class="panel__head">
        <h2 class="t-panel">Source registry</h2>
        <span class="panel__meta">data/source_registry.csv</span>
      </div>
      <table class="table table--wide">
        <thead>
          <tr>
            <th scope="col">Source ID</th>
            <th scope="col">Type</th>
            <th scope="col">Name</th>
            <th scope="col">Boundary</th>
            <th scope="col">Geography</th>
            <th scope="col">Verification status</th>
            <th scope="col">Link</th>
          </tr>
        </thead>
        <tbody>
          ${sources
            .map(
              (source) => `
            <tr>
              <td>${escapeHtml(source.id)}</td>
              <td class="is-muted">${escapeHtml(source.type)}</td>
              <td>${escapeHtml(source.name)}</td>
              <td class="is-muted">${escapeHtml(source.boundary)}</td>
              <td class="is-muted">${escapeHtml(source.geography)}</td>
              <td class="is-muted">${escapeHtml(source.status)}</td>
              <td class="is-muted">${
                /^https?:\/\//i.test(source.url || "")
                  ? `<a class="source-link" href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">Open</a>`
                  : "—"
              }</td>
            </tr>`
            )
            .join("")}
        </tbody>
      </table>
    </div>`
        : ""
    }
  `;
}

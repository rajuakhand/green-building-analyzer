import { escapeHtml, formatFactor, unitWithCo2e } from "../format.js";
import { emptyState, pageHead } from "../shell.js";

const PAPER_URL = "https://pubs.acs.org/doi/10.1021/acsenvironau.2c00035";

/**
 * Research catalogue: find a factor record, read its units and evidence,
 * then add it to the materials selected for the research calculator.
 */
export function render(root, ctx) {
  const { factors, state, categories } = ctx;
  const { search, category, inspectedId } = state.catalogue;

  const needle = search.trim().toLowerCase();
  const filtered = factors.filter((factor) => {
    const matchesCategory = category === "all" || factor.category === category;
    const matchesText =
      needle === "" ||
      factor.id.toLowerCase().includes(needle) ||
      factor.name.toLowerCase().includes(needle) ||
      factor.category.toLowerCase().includes(needle);
    return matchesCategory && matchesText;
  });

  const inspected =
    filtered.find((factor) => factor.id === inspectedId) || filtered[0] || null;

  const selectedNames = state.selectedFactors
    .map((id) => factors.find((factor) => factor.id === id))
    .filter(Boolean)
    .map((factor) => `${factor.id} ${factor.name}`);

  root.innerHTML = `
    ${pageHead({
      title: "Research catalogue",
      meta: `${factors.length} records`,
      actions: `
        <a class="btn btn--outline" href="${PAPER_URL}" target="_blank" rel="noopener noreferrer">
          <i class="ti ti-external-link" aria-hidden="true"></i>Source paper
        </a>
      `,
    })}

    <section class="notice">
      <i class="ti ti-file-description notice__icon" aria-hidden="true"></i>
      <p class="notice__text">
        <strong>Chaudhary &amp; Akhtar (2023)</strong>, ACS Environ. Au 3:94–104, Supporting Information
        Table S3. Boundary cradle-to-gate, geography India. These factors are separate from the demo
        pricing dataset.
      </p>
    </section>

    <div class="filters">
      <label class="field" for="catalogue-search">
        <span class="field__label">Search materials</span>
        <span class="input-wrap">
          <i class="ti ti-search input-icon" aria-hidden="true"></i>
          <input class="input input--search" id="catalogue-search" type="search" autocomplete="off"
            data-bind="catalogue-search" placeholder="Example: cement, brick, steel, sand"
            value="${escapeHtml(search)}">
        </span>
      </label>
      <label class="field" for="catalogue-category">
        <span class="field__label">Broad category</span>
        <span class="input-wrap">
          <select class="input select" id="catalogue-category" data-bind="catalogue-category">
            <option value="all"${category === "all" ? " selected" : ""}>All categories</option>
            ${categories
              .map(
                (entry) =>
                  `<option value="${escapeHtml(entry)}"${
                    entry === category ? " selected" : ""
                  }>${escapeHtml(entry)}</option>`
              )
              .join("")}
          </select>
          <i class="ti ti-chevron-down select-icon" aria-hidden="true"></i>
        </span>
      </label>
    </div>

    ${
      filtered.length === 0
        ? emptyState({
            icon: "ti-filter-off",
            text: "No research material matched this search and category.",
          })
        : `
    <div class="bench bench--catalogue">
      <div class="catalogue">
        <div class="catalogue__head">
          <span class="catalogue__id">Material ID</span>
          <span class="catalogue__name">Material</span>
          <span class="catalogue__cat">Category</span>
          <span class="catalogue__factor">GWP factor</span>
        </div>
        <div class="catalogue__body" role="listbox" aria-label="Research material factors">
          ${filtered
            .map((factor) => {
              const isActive = inspected && factor.id === inspected.id;
              return `
              <button class="catalogue__row${isActive ? " is-active" : ""}" type="button"
                data-action="inspect" data-id="${factor.id}" role="option" aria-selected="${isActive}">
                <span class="catalogue__id">${factor.id}</span>
                <span class="catalogue__name">${escapeHtml(factor.name)}</span>
                <span class="catalogue__cat">${escapeHtml(factor.category)}</span>
                <span class="catalogue__factor">
                  <span class="catalogue__factor-value">${formatFactor(factor.gwpFactor)}</span>
                  <span class="catalogue__factor-unit">${unitWithCo2e(factor.gwpUnit)}</span>
                </span>
              </button>`;
            })
            .join("")}
        </div>
        <div class="catalogue__foot">
          <span>Ordered by material ID</span>
          <span>${filtered.length} of ${factors.length}</span>
        </div>
      </div>

      <div class="inspector inspector--panel">
        ${
          inspected
            ? `
          <div class="record-head">
            <span class="record-chip">${inspected.id}</span>
            <span class="t-small">${escapeHtml(inspected.category)}</span>
          </div>
          <h2 class="record-name">${escapeHtml(inspected.name)}</h2>

          <dl class="factor-list">
            <div class="factor-row">
              <dt class="factor-row__label">GWP factor</dt>
              <dd class="factor-row__figure">
                <span class="factor-row__value">${formatFactor(inspected.gwpFactor)}</span>
                <span class="factor-row__unit">${unitWithCo2e(inspected.gwpUnit)}</span>
              </dd>
            </div>
            <div class="factor-row">
              <dt class="factor-row__label">Energy factor</dt>
              <dd class="factor-row__figure">
                <span class="factor-row__value">${formatFactor(inspected.energyFactor)}</span>
                <span class="factor-row__unit">${escapeHtml(inspected.energyUnit)}</span>
              </dd>
            </div>
          </dl>

          <dl class="kv-list">
            <div class="kv"><dt class="kv__key">Boundary</dt><dd class="kv__value">${escapeHtml(inspected.boundary)}</dd></div>
            <div class="kv"><dt class="kv__key">Geography</dt><dd class="kv__value">${escapeHtml(inspected.geography)}</dd></div>
            <div class="kv"><dt class="kv__key">Verification status</dt>
              <dd class="kv__value kv__value--verified">
                ${
                  /^Verified/i.test(inspected.verificationStatus)
                    ? '<i class="ti ti-circle-check" aria-hidden="true"></i>'
                    : ""
                }${escapeHtml(inspected.verificationStatus)}
              </dd>
            </div>
            <div class="kv"><dt class="kv__key">Source tables</dt><dd class="kv__value">${escapeHtml(inspected.sourceTables)}</dd></div>
          </dl>

          ${
            inspected.verificationStatus === "Needs-review"
              ? `<p class="t-faint" style="margin-top:12px">This record is marked Needs-review. Check the original source before treating its factors as verified.</p>`
              : ""
          }

          <button class="btn btn--outline btn--block" style="margin-top:auto" type="button"
            data-action="toggle-factor" data-id="${inspected.id}">
            <i class="ti ${state.selectedFactors.includes(inspected.id) ? "ti-minus" : "ti-plus"}" aria-hidden="true"></i>
            ${state.selectedFactors.includes(inspected.id) ? "Remove from selected materials" : "Add to selected materials"}
          </button>
        `
            : ""
        }
      </div>
    </div>

    <div class="selected-bar">
      <p class="selected-bar__text">
        <strong>Selected materials (${selectedNames.length})</strong>
        <span>${
          selectedNames.length
            ? escapeHtml(
                selectedNames.length > 3
                  ? `${selectedNames.slice(0, 3).join(", ")} and ${selectedNames.length - 3} more`
                  : selectedNames.join(", ")
              )
            : "None yet"
        }</span>
      </p>
      <a class="btn btn--primary" href="#/calculator">Research calculator<i class="ti ti-arrow-right" aria-hidden="true"></i></a>
    </div>
    `
    }
  `;
}

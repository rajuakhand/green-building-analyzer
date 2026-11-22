/**
 * Import materials from a CSV file.
 * Columns: name, unit, emission_factor, unit_cost, source, verification_status
 */
import { escapeHtml } from "../format.js";
import { pageHead } from "../shell.js";
import { setMaterials } from "../store.js";

export function render(root, ctx) {
  const { state, materials } = ctx;
  const existingNames = materials.map((m) => m.name);

  root.innerHTML = `
    ${pageHead({ title: "Import materials" })}

    <section class="notice notice--warn">
      <i class="ti ti-alert-triangle notice__icon" aria-hidden="true"></i>
      <p class="notice__text">
        <strong>Import from CSV.</strong> Upload a CSV with columns:
        <code>name, unit, emission_factor, unit_cost, source, verification_status</code>.
        <br />
        <em>Chinese units supported: kg, ton (吨), jin (斤), quintal, pcs, thousand pcs, m3, liter.</em>
      </p>
    </section>

    <div class="panel">
      <div class="panel__head">
        <h3 class="t-panel">Import CSV</h3>
      </div>
      <div class="panel__body" style="padding: 20px;">
        <div class="field" style="margin-bottom: 16px;">
          <label class="field__label">Select CSV file</label>
          <input class="input" type="file" id="import-file" accept=".csv" />
        </div>
        <div class="field">
          <label class="field__label">Import mode</label>
          <select class="input" id="import-mode">
            <option value="merge">Merge with existing materials</option>
            <option value="replace">Replace all materials</option>
          </select>
        </div>
        <button class="btn btn--primary btn--block" type="button" data-action="import-csv">
          <i class="ti ti-file-import" aria-hidden="true"></i>Import materials
        </button>
      </div>
    </div>

    <div class="panel">
      <div class="panel__head">
        <h3 class="t-panel">Preview</h3>
      </div>
      <div class="panel__body" style="padding: 20px;">
        <table class="table">
          <thead>
            <tr>
              <th scope="col">#</th>
              <th scope="col">Material</th>
              <th scope="col">Unit</th>
              <th scope="col">Emission factor</th>
              <th scope="col">Unit cost (INR)</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody id="import-preview-body">
            <tr><td colspan="6" class="is-muted">No file selected.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="panel">
      <div class="panel__head">
        <h3 class="t-panel">Existing materials (${materials.length})</h3>
      </div>
      <div class="panel__body" style="padding: 20px;">
        <table class="table">
          <thead>
            <tr>
              <th scope="col">#</th>
              <th scope="col">Material</th>
              <th scope="col">Unit</th>
              <th scope="col">Emission factor</th>
            </tr>
          </thead>
          <tbody>
            ${materials
              .map(
                (m, i) => `
              <tr>
                <td>${i + 1}</td>
                <td>${escapeHtml(m.name)}</td>
                <td>${escapeHtml(m.unit)}</td>
                <td>${m.emissionFactor.toFixed(4)}</td>
              </tr>
            `
              )
              .join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;

  const fileInput = document.getElementById("import-file");
  const previewBody = document.getElementById("import-preview-body");
  const modeSelect = document.getElementById("import-mode");

  fileInput.addEventListener("change", (event) => {
    const file = event.target.files[0];
    if (!file) {
      previewBody.innerHTML = '<tr><td colspan="6" class="is-muted">No file selected.</td></tr>';
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const lines = text.split("\n").filter((l) => l.trim());
      if (lines.length === 0) {
        previewBody.innerHTML = '<tr><td colspan="6" class="is-muted">Empty file.</td></tr>';
        return;
      }

      const header = lines[0].split(",").map((h) => h.trim().toLowerCase());
      const required = ["name", "unit", "emission_factor", "unit_cost"];
      const missing = required.filter((r) => !header.includes(r));

      if (missing.length > 0) {
        previewBody.innerHTML = `<tr><td colspan="6" class="is-muted">Missing columns: ${missing.join(", ")}</td></tr>`;
        return;
      }

      const rows = [];
      for (let i = 1; i < lines.length; i++) {
        const cols = lines[i].split(",");
        const row = {};
        header.forEach((h, idx) => {
          row[h] = cols[idx] ? cols[idx].trim() : "";
        });
        rows.push(row);
      }

      previewBody.innerHTML = rows
        .map(
          (row, idx) => `
          <tr>
            <td>${idx + 1}</td>
            <td>${escapeHtml(row.name || "")}</td>
            <td>${escapeHtml(row.unit || "")}</td>
            <td>${escapeHtml(row.emission_factor || "")}</td>
            <td>${escapeHtml(row.unit_cost || "")}</td>
            <td>${existingNames.includes(row.name) ? "exists" : "new"}</td>
          </tr>
        `
        )
        .join("");
    };
    reader.readAsText(file);
  });
}

export function handleAction(action, ctx) {
  if (action === "import-csv") {
    const fileInput = document.getElementById("import-file");
    const modeSelect = document.getElementById("import-mode");
    const file = fileInput.files[0];
    const mode = modeSelect.value;

    if (!file) {
      alert("Please select a CSV file first.");
      return true;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const lines = text.split("\n").filter((l) => l.trim());
      const header = lines[0].split(",").map((h) => h.trim().toLowerCase());

      const newMaterials = [];
      for (let i = 1; i < lines.length; i++) {
        const cols = lines[i].split(",");
        const row = {};
        header.forEach((h, idx) => {
          row[h] = cols[idx] ? cols[idx].trim() : "";
        });

        const emissionFactor = parseFloat(row.emission_factor) || 0;
        const unitCost = parseFloat(row.unit_cost) || 0;
        const unit = row.unit || "kg";

        newMaterials.push({
          name: row.name || `Material ${i}`,
          unit: unit,
          emissionFactor: emissionFactor,
          unitCost: unitCost,
          source: row.source || "imported",
          verificationStatus: row.verification_status || "Needs-review",
        });
      }

      let updatedMaterials;
      if (mode === "replace") {
        updatedMaterials = newMaterials;
      } else {
        const existingNames = new Set(ctx.materials.map((m) => m.name));
        const toAdd = newMaterials.filter((m) => !existingNames.has(m.name));
        updatedMaterials = [...ctx.materials, ...toAdd];
      }

      setMaterials(updatedMaterials);

      // Re-initialise quantities for new materials
      const state = ctx.state;
      updatedMaterials.forEach((m) => {
        if (!(m.name in state.quantities)) {
          state.quantities[m.name] = 100;
        }
        if (!(m.name in state.unitCosts)) {
          state.unitCosts[m.name] = m.unitCost;
        }
      });

      alert(`Imported ${newMaterials.length} material(s) (mode: ${mode}).`);
    };
    reader.readAsText(file);

    return true;
  }

  return false;
}

/**
 * Data loading. The two CSV files are copied into web/data from the project's
 * data/ folder so the site is self contained when deployed (see
 * scripts/sync_web_data.py).
 */

const MATERIALS_PATH = "data/materials.csv";
const FACTORS_PATH = "data/material_factors.csv";
const SOURCES_PATH = "data/source_registry.csv";

let cache = null;

export async function loadData() {
  if (cache) return cache;

  const [materialsText, factorsText, sourcesText] = await Promise.all([
    fetchText(MATERIALS_PATH),
    fetchText(FACTORS_PATH),
    fetchTextSafe(SOURCES_PATH),
  ]);

  const materials = parseCsv(materialsText).map(normaliseMaterial);
  const factors = parseCsv(factorsText).map(normaliseFactor);
  const sources = parseCsv(sourcesText).map(normaliseSource);

  cache = {
    materials,
    factors,
    sources,
    categories: [...new Set(factors.map((row) => row.broadCategory))].sort((a, b) =>
      a.localeCompare(b)
    ),
  };

  return cache;
}

async function fetchText(path) {
  const response = await fetch(path, { cache: "no-store" });

  if (!response.ok) {
    throw new Error(
      `Could not load ${path} (HTTP ${response.status}). ` +
        "Serve this folder over HTTP, for example: python3 -m http.server 8000"
    );
  }

  return response.text();
}

/** Optional data: a missing file leaves the view empty instead of failing. */
async function fetchTextSafe(path) {
  try {
    const response = await fetch(path, { cache: "no-store" });
    return response.ok ? await response.text() : "";
  } catch (error) {
    return "";
  }
}

function normaliseSource(row) {
  return {
    id: row.source_id,
    type: row.source_type,
    name: row.source_name,
    url: row.source_url,
    boundary: row.boundary,
    geography: row.geography,
    status: row.verification_status,
  };
}

function normaliseMaterial(row) {
  return {
    name: row.material,
    unit: row.unit,
    emissionFactor: Number(row.emission_factor),
    unitCost: Number(row.unit_cost),
    currency: row.currency || "INR",
    source: row.source || "",
    sourceUrl: row.source_url || "",
    verificationStatus: row.verification_status || "",
  };
}

function normaliseFactor(row) {
  return {
    id: row.material_id,
    category: row.broad_category,
    broadCategory: row.broad_category,
    name: row.material,
    gwpFactor: Number(row.gwp_cf),
    gwpUnit: row.gwp_unit,
    energyFactor: Number(row.energy_cf),
    energyUnit: row.energy_unit,
    boundary: row.boundary,
    geography: row.geography,
    verificationStatus: row.verification_status,
    sourceTables: row.source_tables,
  };
}

/**
 * Minimal RFC 4180 CSV parser: handles quoted fields, escaped quotes and
 * CRLF line endings. Returns an array of objects keyed by the header row.
 */
export function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let inQuotes = false;

  const source = text.charCodeAt(0) === 0xfeff ? text.slice(1) : text;

  for (let index = 0; index < source.length; index += 1) {
    const char = source[index];

    if (inQuotes) {
      if (char === '"') {
        if (source[index + 1] === '"') {
          field += '"';
          index += 1;
        } else {
          inQuotes = false;
        }
      } else {
        field += char;
      }
      continue;
    }

    if (char === '"') {
      inQuotes = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
    } else if (char !== "\r") {
      field += char;
    }
  }

  if (field !== "" || row.length > 0) {
    row.push(field);
    rows.push(row);
  }

  const [header, ...body] = rows.filter((entry) =>
    entry.some((cell) => cell.trim() !== "")
  );

  if (!header) return [];

  const keys = header.map((key) => key.trim());

  return body.map((entry) => {
    const record = {};
    keys.forEach((key, index) => {
      record[key] = (entry[index] ?? "").trim();
    });
    return record;
  });
}

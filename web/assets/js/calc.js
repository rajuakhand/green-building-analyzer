/**
 * Calculation layer. These functions mirror src/calculator.py and
 * src/advanced_lca.py:
 *
 *   estimated_cost      = quantity x unit_cost
 *   carbon_kg_co2e      = quantity x emission_factor
 *   transport_carbon    = tonnes x distance x transport_factor
 *   operational_carbon  = annual_kwh x lifetime_years x electricity_factor
 */

export const STAGES = [
  {
    key: "embodied",
    label: "Embodied carbon",
    shortLabel: "Embodied",
    icon: "ti-building",
    sub: "Material quantities and emission factors",
  },
  {
    key: "transport",
    label: "Transport carbon",
    shortLabel: "Transport",
    icon: "ti-truck",
    sub: "Mass × distance × factor",
  },
  {
    key: "operational",
    label: "Operational energy carbon",
    shortLabel: "Operational energy",
    icon: "ti-bolt",
    sub: "Electricity use over building lifetime",
  },
  {
    key: "endOfLife",
    label: "End-of-life carbon",
    shortLabel: "End-of-life",
    icon: "ti-recycle",
    sub: "User-entered estimate",
  },
];

export const STAGE_KEYS = STAGES.map((stage) => stage.key);

/** Estimated cost and embodied carbon for each material row. */
export function calculateFootprint(rows) {
  return rows.map((row) => {
    const quantity = Math.max(0, Number(row.quantity) || 0);
    const unitCost = Math.max(0, Number(row.unitCost) || 0);
    const emissionFactor = Math.max(0, Number(row.emissionFactor) || 0);

    return {
      ...row,
      quantity,
      unitCost,
      emissionFactor,
      estimatedCost: quantity * unitCost,
      carbon: quantity * emissionFactor,
    };
  });
}

export function summariseFootprint(rows) {
  return {
    totalCost: rows.reduce((sum, row) => sum + row.estimatedCost, 0),
    totalCarbon: rows.reduce((sum, row) => sum + row.carbon, 0),
    materialCount: rows.length,
  };
}

/** Carbon by life-cycle stage, using the inputs entered in the app. */
export function calculateLca({ embodiedCarbon, lca }) {
  const safeInput = (value) => {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? Math.max(0, numeric) : 0;
  };

  const transportCarbon =
    safeInput(lca.transportTonnes) *
    safeInput(lca.transportDistanceKm) *
    safeInput(lca.transportFactor);

  const operationalCarbon =
    safeInput(lca.annualEnergyKwh) *
    Math.max(1, Math.round(safeInput(lca.lifetimeYears) || 1)) *
    safeInput(lca.electricityFactor);

  const byStage = {
    embodied: Math.max(0, Number(embodiedCarbon) || 0),
    transport: transportCarbon,
    operational: operationalCarbon,
    endOfLife: Math.max(0, Number(lca.endOfLifeKg) || 0),
  };

  const total = STAGE_KEYS.reduce((sum, key) => sum + byStage[key], 0);

  return { byStage, total };
}

/** GWP and energy for the research factor catalogue. */
export function calculateResearchRows(rows) {
  return rows.map((row) => {
    const quantity = Math.max(0, Number(row.quantity) || 0);
    const gwpFactor = Number(row.gwpFactor);
    const energyFactor = Number(row.energyFactor);

    if (!Number.isFinite(gwpFactor) || gwpFactor < 0) {
      throw new Error(`Invalid GWP factor for ${row.name || row.id || "material"}`);
    }
    if (!Number.isFinite(energyFactor) || energyFactor < 0) {
      throw new Error(`Invalid energy factor for ${row.name || row.id || "material"}`);
    }

    if (row.gwpUnit && row.quantityUnit && !gwpUnitMatches(row.gwpUnit, row.quantityUnit)) {
      throw new Error(`GWP unit mismatch for ${row.name || row.id || "material"}`);
    }
    if (row.energyUnit && row.quantityUnit && !gwpUnitMatches(row.energyUnit, row.quantityUnit)) {
      throw new Error(`Energy unit mismatch for ${row.name || row.id || "material"}`);
    }

    return {
      ...row,
      quantity,
      carbon: quantity * gwpFactor,
      energy: quantity * energyFactor,
    };
  });
}

function gwpUnitMatches(factorUnit, quantityUnit) {
  if (typeof factorUnit !== "string" || typeof quantityUnit !== "string") {
    return false;
  }

  const denominator = factorUnit.includes("/")
    ? factorUnit.split("/", 1)[1].trim().toLower()
    : factorUnit.trim().toLower();
  return denominator === String(quantityUnit).trim().toLower();
}

export function summariseResearch(rows) {
  return {
    totalCarbon: rows.reduce((sum, row) => sum + row.carbon, 0),
    totalEnergy: rows.reduce((sum, row) => sum + row.energy, 0),
    count: rows.length,
    boundary: rows.length ? rows[0].boundary : "",
    geography: rows.length ? rows[0].geography : "",
    mixedBoundary: new Set(rows.map((row) => row.boundary)).size > 1,
    mixedGeography: new Set(rows.map((row) => row.geography)).size > 1,
  };
}

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
  const transportCarbon =
    (Number(lca.transportTonnes) || 0) *
    (Number(lca.transportDistanceKm) || 0) *
    (Number(lca.transportFactor) || 0);

  const operationalCarbon =
    (Number(lca.annualEnergyKwh) || 0) *
    (Number(lca.lifetimeYears) || 0) *
    (Number(lca.electricityFactor) || 0);

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
    return {
      ...row,
      quantity,
      carbon: quantity * row.gwpFactor,
      energy: quantity * row.energyFactor,
    };
  });
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

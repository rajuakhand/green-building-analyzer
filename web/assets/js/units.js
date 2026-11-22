/**
 * Unit conversion factors for construction materials.
 * All mass units convert to kg, volume to m3, count to pcs.
 * Chinese units included: 吨 (tonne), 斤 (jin = 0.5kg), 布 (bolt), 包 (bag).
 */

export const UNIT_CATEGORIES = {
  mass: "mass",
  volume: "volume",
  count: "count",
};

/** Base conversion: value in source unit -> value in base unit (kg / m3 / pcs). */
export const UNIT_TO_BASE = {
  // Mass
  kg: { toBase: 1, category: UNIT_CATEGORIES.mass, baseUnit: "kg" },
  kilogram: { toBase: 1, category: UNIT_CATEGORIES.mass, baseUnit: "kg" },
  tonne: { toBase: 1000, category: UNIT_CATEGORIES.mass, baseUnit: "kg" },
  ton: { toBase: 1000, category: UNIT_CATEGORIES.mass, baseUnit: "kg" },
  吨: { toBase: 1000, category: UNIT_CATEGORIES.mass, baseUnit: "kg" },
  quintal: { toBase: 100, category: UNIT_CATEGORIES.mass, baseUnit: "kg" },
  jin: { toBase: 0.5, category: UNIT_CATEGORIES.mass, baseUnit: "kg" },
  斤: { toBase: 0.5, category: UNIT_CATEGORIES.mass, baseUnit: "kg" },
  liang: { toBase: 0.05, category: UNIT_CATEGORIES.mass, baseUnit: "kg" },
  两: { toBase: 0.05, category: UNIT_CATEGORIES.mass, baseUnit: "kg" },
  g: { toBase: 0.001, category: UNIT_CATEGORIES.mass, baseUnit: "kg" },
  gram: { toBase: 0.001, category: UNIT_CATEGORIES.mass, baseUnit: "kg" },
  lb: { toBase: 0.453592, category: UNIT_CATEGORIES.mass, baseUnit: "kg" },
  pound: { toBase: 0.453592, category: UNIT_CATEGORIES.mass, baseUnit: "kg" },

  // Volume
  m3: { toBase: 1, category: UNIT_CATEGORIES.volume, baseUnit: "m3" },
  cubic_meter: { toBase: 1, category: UNIT_CATEGORIES.volume, baseUnit: "m3" },
  liter: { toBase: 0.001, category: UNIT_CATEGORIES.volume, baseUnit: "m3" },
  litre: { toBase: 0.001, category: UNIT_CATEGORIES.volume, baseUnit: "m3" },
  ml: { toBase: 0.000001, category: UNIT_CATEGORIES.volume, baseUnit: "m3" },
  gallon: { toBase: 0.00378541, category: UNIT_CATEGORIES.volume, baseUnit: "m3" },

  // Count
  pcs: { toBase: 1, category: UNIT_CATEGORIES.count, baseUnit: "pcs" },
  piece: { toBase: 1, category: UNIT_CATEGORIES.count, baseUnit: "pcs" },
  "thousand pcs": { toBase: 1000, category: UNIT_CATEGORIES.count, baseUnit: "pcs" },
  dozen: { toBase: 12, category: UNIT_CATEGORIES.count, baseUnit: "pcs" },
  bag: { toBase: 1, category: UNIT_CATEGORIES.count, baseUnit: "pcs" },
  包: { toBase: 1, category: UNIT_CATEGORIES.count, baseUnit: "pcs" },
  roll: { toBase: 1, category: UNIT_CATEGORIES.count, baseUnit: "pcs" },
  bundle: { toBase: 1, category: UNIT_CATEGORIES.count, baseUnit: "pcs" },
};

/** Convert a quantity from source unit to target unit. Returns null if incompatible. */
export function convertUnit(value, fromUnit, toUnit) {
  const from = UNIT_TO_BASE[fromUnit];
  const to = UNIT_TO_BASE[toUnit];

  if (!from || !to) return null;
  if (from.category !== to.category) return null;

  const baseValue = value * from.toBase;
  return baseValue / to.toBase;
}

/** Get all units for a category. */
export function getUnitsByCategory(category) {
  return Object.entries(UNIT_TO_BASE)
    .filter(([, info]) => info.category === category)
    .map(([unit]) => unit);
}

/** Get the base unit for a given unit. */
export function getBaseUnit(unit) {
  const info = UNIT_TO_BASE[unit];
  return info ? info.baseUnit : null;
}

/** Check if a unit is valid. */
export function isValidUnit(unit) {
  return unit in UNIT_TO_BASE;
}

/** Get display label for a unit. */
export function getUnitLabel(unit) {
  const labels = {
    kg: "kg",
    tonne: "ton (吨)",
    ton: "ton (吨)",
    吨: "ton (吨)",
    quintal: "quintal",
    jin: "jin (斤)",
    斤: "jin (斤)",
    liang: "liang (两)",
    两: "liang (两)",
    g: "g",
    lb: "lb",
    m3: "m³",
    liter: "liter",
    pcs: "pcs",
    "thousand pcs": "1000 pcs",
    dozen: "dozen",
    bag: "bag",
    包: "bag (包)",
  };
  return labels[unit] || unit;
}

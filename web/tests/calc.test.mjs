/**
 * Calculation tests for the web app. Run with:
 *
 *     node web/tests/calc.test.mjs
 *
 * The expected values are the same ones asserted by tests/test_calculator.py
 * and tests/test_advanced_lca.py, so the two front ends cannot drift apart
 * without a test failing.
 */

import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import {
  calculateFootprint,
  calculateLca,
  calculateResearchRows,
  summariseFootprint,
  summariseResearch,
} from "../assets/js/calc.js";
import { parseCsv } from "../assets/js/data.js";

const here = dirname(fileURLToPath(import.meta.url));
const webRoot = join(here, "..");

let passed = 0;

function check(name, fn) {
  fn();
  passed += 1;
  console.log(`ok - ${name}`);
}

function close(actual, expected, tolerance = 1e-9) {
  assert.ok(
    Math.abs(actual - expected) <= tolerance,
    `expected ${expected}, got ${actual}`
  );
}

const materials = parseCsv(readFileSync(join(webRoot, "data/materials.csv"), "utf8")).map(
  (row) => ({
    name: row.material,
    unit: row.unit,
    quantity: 100,
    unitCost: Number(row.unit_cost),
    emissionFactor: Number(row.emission_factor),
  })
);

check("the demo dataset has four priced materials", () => {
  assert.equal(materials.length, 4);
});

const rows = calculateFootprint(materials);
const summary = summariseFootprint(rows);

check("cost is quantity times unit cost", () => {
  rows.forEach((row) => close(row.estimatedCost, 100));
});

check("carbon is quantity times emission factor", () => {
  close(rows[0].carbon, 76);
  close(rows[1].carbon, 0.9);
  close(rows[2].carbon, 0.9);
  close(rows[3].carbon, 13);
});

check("the default project totals 90.80 kg CO2e and INR 400.00", () => {
  close(summary.totalCarbon, 90.8);
  close(summary.totalCost, 400);
  assert.equal(summary.materialCount, 4);
});

check("a life-cycle total with no extra inputs equals embodied carbon", () => {
  const lca = calculateLca({
    embodiedCarbon: summary.totalCarbon,
    lca: {
      transportTonnes: 0,
      transportDistanceKm: 0,
      transportFactor: 0,
      annualEnergyKwh: 0,
      lifetimeYears: 50,
      electricityFactor: 0,
      endOfLifeKg: 0,
    },
  });
  close(lca.byStage.transport, 0);
  close(lca.byStage.operational, 0);
  close(lca.total, 90.8);
});

check("transport is mass x distance x factor", () => {
  const lca = calculateLca({
    embodiedCarbon: 0,
    lca: {
      transportTonnes: 2,
      transportDistanceKm: 100,
      transportFactor: 0.1,
      annualEnergyKwh: 0,
      lifetimeYears: 50,
      electricityFactor: 0,
      endOfLifeKg: 0,
    },
  });
  close(lca.byStage.transport, 20);
  close(lca.total, 20);
});

check("operational carbon is kWh x lifetime x grid factor", () => {
  const lca = calculateLca({
    embodiedCarbon: summary.totalCarbon,
    lca: {
      transportTonnes: 0,
      transportDistanceKm: 0,
      transportFactor: 0,
      annualEnergyKwh: 10000,
      lifetimeYears: 50,
      electricityFactor: 0.7,
      endOfLifeKg: 0,
    },
  });
  close(lca.byStage.operational, 350000);
  close(lca.total, 350090.8);
});

check("research rows keep GWP and energy separate", () => {
  const rows = calculateResearchRows([
    { id: "MAT-002", name: "Portland cement", quantity: 1, gwpFactor: 910, energyFactor: 6400 },
    { id: "MAT-003", name: "Twisted steel / deformed bars", quantity: 1, gwpFactor: 260, energyFactor: 3000 },
  ]);
  const research = summariseResearch(rows);
  close(research.totalCarbon, 1170);
  close(research.totalEnergy, 9400);
  assert.equal(research.count, 2);
});

check("negative quantities cannot reduce a total", () => {
  const negative = calculateFootprint([
    { name: "Sand", unit: "kg", quantity: -50, unitCost: 1, emissionFactor: 0.009 },
  ]);
  assert.equal(negative[0].carbon, 0);
});

console.log(`\n${passed} checks passed`);

/**
 * CSV export helpers. The analysis file reproduces the sections the Streamlit
 * app writes: material results, LCA input assumptions, stage summary and the
 * life-cycle total, so the two exports can be compared line for line.
 */

export function toCsv(headers, rows) {
  const escape = (cell) => {
    const text = String(cell ?? "");
    return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
  };

  return [headers.map(escape).join(","), ...rows.map((row) => row.map(escape).join(","))].join(
    "\n"
  );
}

export function downloadFile(filename, content, mime = "text/csv;charset=utf-8;") {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();

  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function buildAnalysisCsv({ rows, summary, state, lcaResult, stageLabels }) {
  const results = toCsv(
    [
      "material",
      "unit",
      "quantity",
      "unit_cost",
      "estimated_cost",
      "emission_factor",
      "carbon_kg_co2e",
    ],
    rows.map((row) => [
      row.name,
      row.unit,
      row.quantity,
      row.unitCost,
      row.estimatedCost,
      row.emissionFactor,
      row.carbon,
    ])
  );

  const assumptions = toCsv(
    ["Input", "Value"],
    [
      ["Transport mass (tonnes)", state.lca.transportTonnes],
      ["Transport distance (km)", state.lca.transportDistanceKm],
      ["Transport emission factor (kg CO2e/tonne-km)", state.lca.transportFactor],
      ["Annual electricity (kWh)", state.lca.annualEnergyKwh],
      ["Building lifetime (years)", state.lca.lifetimeYears],
      ["Electricity emission factor (kg CO2e/kWh)", state.lca.electricityFactor],
      ["End-of-life emissions (kg CO2e)", state.lca.endOfLifeKg],
    ]
  );

  const stages = toCsv(
    ["Life-Cycle Stage", "Carbon (kg CO2e)"],
    stageLabels.map((stage) => [stage.label, lcaResult.byStage[stage.key]])
  );

  const total = toCsv(
    ["Life-Cycle Stage", "Carbon (kg CO2e)"],
    [["TOTAL LIFE-CYCLE CARBON", lcaResult.total]]
  );

  const summaryBlock = toCsv(
    ["Summary", "Value"],
    [
      ["Estimated material cost (INR)", summary.totalCost],
      ["Estimated material carbon (kg CO2e)", summary.totalCarbon],
      ["Materials analyzed", summary.materialCount],
    ]
  );

  return (
    "\ufeff" +
    summaryBlock +
    "\n\nMaterial Results\n" +
    results +
    "\n\nLCA Input Assumptions\n" +
    assumptions +
    "\nLife-Cycle Carbon Summary\n" +
    stages +
    "\n" +
    total +
    "\n"
  );
}

export function buildFactorCsv(rows) {
  return (
    "\ufeff" +
    toCsv(
      [
        "material_id",
        "material",
        "quantity",
        "quantity_unit",
        "gwp_cf",
        "gwp_unit",
        "carbon_kg_co2e",
        "energy_cf",
        "energy_unit",
        "energy_mj",
        "verification_status",
      ],
      rows.map((row) => {
        const quantityUnit = row.gwpUnit.includes("/")
          ? row.gwpUnit.split("/").slice(1).join("/").trim()
          : row.gwpUnit;
        return [
          row.id,
          row.name,
          row.quantity,
          quantityUnit,
          row.gwpFactor,
          row.gwpUnit,
          row.carbon,
          row.energyFactor,
          row.energyUnit,
          row.energy,
          row.verificationStatus,
        ];
      })
    ) +
    "\n"
  );
}

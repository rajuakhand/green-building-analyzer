/**
 * Application state, persisted to localStorage so values survive a reload and
 * stay consistent between views (the Streamlit app keeps the same values in
 * session state).
 */

const STORAGE_KEY = "gba.state.v1";

const DEFAULT_LCA = {
  transportTonnes: 0,
  transportDistanceKm: 0,
  transportFactor: 0,
  annualEnergyKwh: 0,
  lifetimeYears: 50,
  electricityFactor: 0,
  endOfLifeKg: 0,
};

const listeners = new Set();

let state = {
  /** material name -> quantity / unit cost */
  quantities: {},
  unitCosts: {},
  lca: { ...DEFAULT_LCA },
  /** research material ids chosen in the catalogue */
  selectedFactors: [],
  /** material id -> quantity for the research calculator */
  factorQuantities: {},
  catalogue: {
    search: "",
    category: "all",
    inspectedId: null,
  },
  activeStage: "transport",
  aiText: "",
  aiRequested: false,
};

export function getState() {
  return state;
}

/** Seeds per-material inputs from the CSV. Stored values win. */
export function initialiseMaterials(materials) {
  materials.forEach((material) => {
    if (!(material.name in state.quantities)) {
      state.quantities[material.name] = 100;
    }
    if (!(material.name in state.unitCosts)) {
      state.unitCosts[material.name] = material.unitCost;
    }
  });
  persist();
}

export function subscribe(listener) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function set(updater) {
  updater(state);
  persist();
  listeners.forEach((listener) => listener(state));
}

export function setValue(path, value) {
  set((draft) => {
    const keys = path.split(".");
    let target = draft;
    for (let index = 0; index < keys.length - 1; index += 1) {
      const key = keys[index];
      if (typeof target[key] !== "object" || target[key] === null) {
        target[key] = {};
      }
      target = target[key];
    }
    target[keys[keys.length - 1]] = value;
  });
}

export function toggleFactor(materialId) {
  set((draft) => {
    const index = draft.selectedFactors.indexOf(materialId);
    if (index === -1) {
      draft.selectedFactors.push(materialId);
      if (!(materialId in draft.factorQuantities)) {
        draft.factorQuantities[materialId] = 0;
      }
    } else {
      draft.selectedFactors.splice(index, 1);
    }
  });
}

export function resetLca() {
  set((draft) => {
    draft.lca = { ...DEFAULT_LCA };
  });
}

function persist() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (error) {
    // Private browsing or a full quota: the app keeps working in memory.
    console.warn("Could not persist state", error);
  }
}

function hydrate() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const saved = JSON.parse(raw);
    if (!saved || typeof saved !== "object") return;

    state = {
      ...state,
      ...saved,
      lca: { ...DEFAULT_LCA, ...(saved.lca || {}) },
      catalogue: { ...state.catalogue, ...(saved.catalogue || {}) },
    };
  } catch (error) {
    console.warn("Could not restore saved values", error);
  }
}

hydrate();

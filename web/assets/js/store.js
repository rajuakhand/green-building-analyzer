/**
 * Application state, persisted to localStorage so values survive a reload and
 * stay consistent between views (the Streamlit app keeps the same values in
 * session state).
 */

import { isAuthenticated, getCurrentUser } from "./auth.js";

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

const DEFAULT_THEME = "light";

const listeners = new Set();

let state = {
  /** material name -> quantity / unit cost */
  quantities: {},
  unitCosts: {},
  /** material name -> display unit (e.g. kg, jin, ton) */
  materialUnits: {},
  /** master material list (name, unit, emissionFactor, unitCost, source, verificationStatus) */
  materials: [],
  /** alternative scenario quantities, compared against the estimate above */
  scenarioB: {},
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
  /** Details printed on the project statement. */
  project: {
    name: "",
    client: "",
    site: "",
    preparedBy: "",
  },
  activeStage: "transport",
  aiText: "",
  aiRequested: false,
  theme: DEFAULT_THEME,
};

export function getState() {
  return state;
}

/** Returns the storage key scoped to the current authenticated user. */
function userProjectsKey() {
  const user = getCurrentUser();
  const email = user ? user.email : "anonymous";
  return `gba.projects.v1.${email}`;
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
    if (!(material.name in state.materialUnits)) {
      state.materialUnits[material.name] = material.unit;
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

/** Replaces the alternative scenario quantities in one go. */
export function setScenarioB(quantities) {
  set((draft) => {
    draft.scenarioB = { ...quantities };
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

export function toggleTheme() {
  set((draft) => {
    draft.theme = draft.theme === "light" ? "dark" : "light";
  });
}

export function setMaterials(newMaterials) {
  set((draft) => {
    draft.materials = newMaterials;
  });
}

export function setMaterialUnit(materialName, unit) {
  set((draft) => {
    draft.materialUnits[materialName] = unit;
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

/** Save the current state as a named project. Requires authentication. */
export function saveProject(name) {
  if (!isAuthenticated()) {
    throw new Error("Authentication required. Please sign in to save projects.");
  }
  const user = getCurrentUser();
  const projects = getUserProjects(user.email);
  projects[name] = {
    ...state,
    savedAt: new Date().toISOString(),
    owner: user.email,
  };
  try {
    localStorage.setItem(userProjectsKey(), JSON.stringify(projects));
  } catch (error) {
    console.warn("Could not save project", error);
  }
  return projects;
}

/** List all saved project names for the current user. */
export function listProjects() {
  const user = getCurrentUser();
  if (!user) return [];
  return Object.keys(getUserProjects(user.email));
}

/** Load a saved project into state. Returns true if found. Requires authentication. */
export function loadProject(name) {
  if (!isAuthenticated()) {
    throw new Error("Authentication required. Please sign in to load projects.");
  }
  const user = getCurrentUser();
  const projects = getUserProjects(user.email);
  const saved = projects[name];
  if (!saved) return false;

  state = {
    ...DEFAULT_STATE,
    ...saved,
    lca: { ...DEFAULT_LCA, ...(saved.lca || {}) },
    catalogue: { ...DEFAULT_STATE.catalogue, ...(saved.catalogue || {}) },
    project: { ...DEFAULT_STATE.project, ...(saved.project || {}) },
    scenarioB: { ...DEFAULT_STATE.scenarioB, ...(saved.scenarioB || {}) },
    quantities: { ...DEFAULT_STATE.quantities, ...(saved.quantities || {}) },
    unitCosts: { ...DEFAULT_STATE.unitCosts, ...(saved.unitCosts || {}) },
    materialUnits: { ...DEFAULT_STATE.materialUnits, ...(saved.materialUnits || {}) },
  };
  persist();
  listeners.forEach((listener) => listener(state));
  return true;
}

/** Delete a saved project. Requires authentication. */
export function deleteProject(name) {
  if (!isAuthenticated()) {
    throw new Error("Authentication required. Please sign in to delete projects.");
  }
  const user = getCurrentUser();
  const projects = getUserProjects(user.email);
  delete projects[name];
  try {
    localStorage.setItem(userProjectsKey(), JSON.stringify(projects));
  } catch (error) {
    console.warn("Could not delete project", error);
  }
  return projects;
}

/** Read all saved projects for a specific user from localStorage. */
function getUserProjects(email) {
  try {
    const raw = localStorage.getItem(`gba.projects.v1.${email}`);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? parsed : {};
  } catch (error) {
    console.warn("Could not read projects", error);
    return {};
  }
}

const DEFAULT_STATE = {
  quantities: {},
  unitCosts: {},
  materialUnits: {},
  materials: [],
  scenarioB: {},
  lca: { ...DEFAULT_LCA },
  selectedFactors: [],
  factorQuantities: {},
  catalogue: {
    search: "",
    category: "all",
    inspectedId: null,
  },
  project: {
    name: "",
    client: "",
    site: "",
    preparedBy: "",
  },
  activeStage: "transport",
  aiText: "",
  aiRequested: false,
  theme: DEFAULT_THEME,
};

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
      project: { ...state.project, ...(saved.project || {}) },
      scenarioB: { ...state.scenarioB, ...(saved.scenarioB || {}) },
      materialUnits: { ...state.materialUnits, ...(saved.materialUnits || {}) },
    };
  } catch (error) {
    console.warn("Could not restore saved values", error);
  }
}

hydrate();

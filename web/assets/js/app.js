/**
 * Application entry point: loads the CSV data, mounts the shell, routes
 * between views and routes every input back into the store.
 *
 * State lives in store.js and is persisted, so values carry across views the
 * same way they do between sections of the Streamlit app.
 */

import { calculateFootprint, calculateLca, STAGES, summariseFootprint } from "./calc.js";
import { loadData } from "./data.js";
import { readNumber } from "./format.js";
import { setActiveNav, shellHtml } from "./shell.js";
import {
  getState,
  initialiseMaterials,
  set,
  subscribe,
  toggleFactor,
} from "./store.js";

import * as aiView from "./views/ai.js";
import * as calculatorView from "./views/calculator.js";
import * as catalogueView from "./views/catalogue.js";
import * as estimateView from "./views/estimate.js";
import * as exportView from "./views/export.js";
import * as lcaView from "./views/lca.js";
import * as methodView from "./views/method.js";
import * as sourcesView from "./views/sources.js";
import * as compareView from "./views/compare.js";
import * as statementView from "./views/statement.js";

const VIEWS = {
  estimate: estimateView,
  lca: lcaView,
  catalogue: catalogueView,
  calculator: calculatorView,
  ai: aiView,
  method: methodView,
  sources: sourcesView,
  compare: compareView,
  statement: statementView,
  export: exportView,
};

const appEl = document.getElementById("app");
let viewEl = null;
let data = null;
let currentRoute = "estimate";

/* ------------------------------------------------------------------ context */

function buildContext() {
  const state = getState();

  const rows = calculateFootprint(
    data.materials.map((material) => ({
      name: material.name,
      unit: material.unit,
      quantity: state.quantities[material.name] ?? 0,
      unitCost: state.unitCosts[material.name] ?? 0,
      emissionFactor: material.emissionFactor,
      verificationStatus: material.verificationStatus,
      source: material.source,
    }))
  );

  const summary = summariseFootprint(rows);
  const lcaResult = calculateLca({ embodiedCarbon: summary.totalCarbon, lca: state.lca });

  return {
    materials: data.materials,
    factors: data.factors,
    sources: data.sources,
    categories: data.categories,
    state,
    derived: { rows, summary, lcaResult, stageLabels: STAGES },
  };
}

/* ------------------------------------------------------------------- render */

function renderView({ preserveFocus = true } = {}) {
  if (!viewEl) return;

  const active = document.activeElement;
  const hasFocus = preserveFocus && active && active.id && viewEl.contains(active);
  const focusId = hasFocus ? active.id : null;
  const rawValue = hasFocus ? active.value : null;
  const caret = hasFocus && typeof active.selectionStart === "number" ? active.selectionStart : null;

  const ctx = buildContext();
  ctx.focusId = focusId;
  ctx.rawValue = rawValue;

  const view = VIEWS[currentRoute] || VIEWS.estimate;
  view.render(viewEl, ctx);
  setActiveNav(currentRoute);

  if (focusId) {
    const restored = document.getElementById(focusId);
    if (restored) {
      restored.focus();
      if (caret !== null) {
        try {
          restored.setSelectionRange(caret, caret);
        } catch (error) {
          // Select elements and inputs without caret support.
        }
      }
    }
  }
}

/* ------------------------------------------------------------------- events */

function handleInput(event) {
  const el = event.target.closest("[data-bind]");
  if (!el) return;

  switch (el.dataset.bind) {
    case "material-qty":
      set((state) => {
        state.quantities[el.dataset.material] = readNumber(el.value);
      });
      break;
    case "material-cost":
      set((state) => {
        state.unitCosts[el.dataset.material] = readNumber(el.value);
      });
      break;
    case "lca": {
      const field = el.dataset.field;
      const value =
        field === "lifetimeYears" ? Math.max(1, Math.round(readNumber(el.value))) : readNumber(el.value);
      set((state) => {
        state.lca[field] = value;
      });
      break;
    }
    case "factor-qty":
      set((state) => {
        state.factorQuantities[el.dataset.id] = readNumber(el.value);
      });
      break;
    case "catalogue-search":
      set((state) => {
        state.catalogue.search = el.value;
      });
      break;
    case "project":
      set((state) => {
        state.project[el.dataset.field] = el.value;
      });
      break;
    case "scenario-b-qty":
      set((state) => {
        state.scenarioB[el.dataset.material] = readNumber(el.value);
      });
      break;
    default:
      break;
  }
}

function handleChange(event) {
  const el = event.target.closest('[data-bind="catalogue-category"]');
  if (!el) return;

  set((state) => {
    state.catalogue.category = el.value;
  });
}

function handleClick(event) {
  const trigger = event.target.closest("[data-action]");
  if (!trigger) return;

  const action = trigger.dataset.action;

  switch (action) {
    case "select-stage":
      set((state) => {
        state.activeStage = trigger.dataset.stage;
      });
      return;
    case "inspect":
      set((state) => {
        state.catalogue.inspectedId = trigger.dataset.id;
      });
      return;
    case "toggle-factor":
      toggleFactor(trigger.dataset.id);
      return;
    case "clear-factors":
      set((state) => {
        state.selectedFactors = [];
      });
      return;
    case "generate-ai":
      set((state) => {
        state.aiRequested = true;
      });
      return;
    default:
      break;
  }

  const ctx = buildContext();
  ctx.focusId = null;
  ctx.rawValue = null;

  if (estimateView.handleAction(action, ctx)) return;
  if (exportView.handleAction(action, ctx)) return;
  if (calculatorView.handleAction(action, ctx)) return;
  if (compareView.handleAction(action, ctx)) return;
}

function routeFromHash() {
  const match = window.location.hash.match(/^#\/([a-z]+)/);
  return match && VIEWS[match[1]] ? match[1] : "estimate";
}

/* --------------------------------------------------------------------- boot */

function renderFatalError(message) {
  viewEl.innerHTML = `
    <header class="page-head">
      <h1 class="t-page-title">Green Building Analyzer</h1>
    </header>
    <section class="notice notice--warn">
      <i class="ti ti-alert-triangle notice__icon" aria-hidden="true"></i>
      <div class="notice__text">
        <p><strong>The material data could not be loaded.</strong></p>
        <p>${message}</p>
      </div>
    </section>
  `;
}

async function main() {
  appEl.innerHTML = shellHtml();
  viewEl = document.getElementById("view");
  viewEl.innerHTML = '<p class="t-small">Loading material data…</p>';

  viewEl.addEventListener("input", handleInput);
  viewEl.addEventListener("change", handleChange);
  viewEl.addEventListener("click", handleClick);

  try {
    data = await loadData();
  } catch (error) {
    renderFatalError(error.message);
    return;
  }

  initialiseMaterials(data.materials);

  if (!getState().catalogue.inspectedId) {
    set((state) => {
      state.catalogue.inspectedId = data.factors[0].id;
    });
  }

  subscribe(() => renderView());

  currentRoute = routeFromHash();
  renderView({ preserveFocus: false });

  window.addEventListener("hashchange", () => {
    currentRoute = routeFromHash();
    renderView({ preserveFocus: false });
    window.scrollTo({ top: 0 });
  });
}

main();

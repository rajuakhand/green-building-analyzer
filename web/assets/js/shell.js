import { formatInput, formatNumber } from "./format.js";
import { isAuthenticated, logout } from "./auth.js";

/** Navigation is the product's six real destinations, in a fixed order. */
export const NAV = [
  { route: "estimate", label: "Project estimate", icon: "ti-calculator" },
  { route: "lca", label: "Life-cycle assessment", icon: "ti-chart-histogram" },
  { route: "catalogue", label: "Research catalogue", icon: "ti-table" },
  { route: "calculator", label: "Research calculator", icon: "ti-list-details" },
  { route: "ai", label: "AI recommendations", icon: "ti-sparkles" },
  { route: "method", label: "Method", icon: "ti-math-function" },
  { route: "sources", label: "Data sources", icon: "ti-database" },
  { route: "compare", label: "Compare scenarios", icon: "ti-columns-2" },
  { route: "statement", label: "Project statement", icon: "ti-file-invoice" },
  { route: "export", label: "Export", icon: "ti-download" },
  { route: "import", label: "Import", icon: "ti-file-import" },
];

export function shellHtml() {
  return `
    <aside class="sidebar">
      <div class="brand">
        <span class="brand__mark"><i class="ti ti-leaf" aria-hidden="true"></i></span>
        <span class="brand__name">Green Building<br>Analyzer</span>
      </div>
      <nav class="nav" aria-label="Main">
        ${NAV.map(
          (item) => `
          <a class="nav-item" href="#/${item.route}" data-route="${item.route}">
            <i class="ti ${item.icon} nav-item__icon" aria-hidden="true"></i>
            ${item.label}
          </a>`
        ).join("")}
      </nav>
      <div class="sidebar__foot">
        <p>AI-assisted estimates for educational and preliminary planning. Not a certified life-cycle assessment.</p>
        <div class="project-tools">
          <button class="btn btn--primary btn--block" type="button" data-action="save-project">
            <i class="ti ti-save" aria-hidden="true"></i>Project.save
          </button>
          <button class="btn btn--outline btn--block" type="button" data-action="load-project">
            <i class="ti ti-folder-open" aria-hidden="true"></i>Project.load
          </button>
          <button class="btn btn--outline btn--block" type="button" data-action="delete-project">
            <i class="ti ti-trash" aria-hidden="true"></i>Project.delete
          </button>
          <button class="btn btn--outline btn--block" type="button" data-action="toggle-theme">
            <i class="ti ti-sun" aria-hidden="true"></i>Theme.toggle
          </button>
        </div>
        <div class="auth-tools" style="margin-top: 12px;">
          <button class="btn btn--outline btn--block" type="button" data-action="auth-toggle">
            <i class="ti ti-user" aria-hidden="true"></i><span class="auth-text">Sign in</span>
          </button>
        </div>
      </div>
    </aside>
    <main class="main" id="view" tabindex="-1"></main>
  `;
}

export function setActiveNav(route) {
  document.querySelectorAll(".nav-item").forEach((item) => {
    const isActive = item.dataset.route === route;
    item.classList.toggle("is-active", isActive);
    if (isActive) {
      item.setAttribute("aria-current", "page");
    } else {
      item.removeAttribute("aria-current");
    }
  });
}

/**
 * Keeps the text a person is typing intact. Views re-render on every change,
 * so the focused input is given back its raw, unformatted value.
 */
export function valueFor(ctx, id, numeric, decimals = 2) {
  if (ctx && ctx.focusId === id && ctx.rawValue !== null && ctx.rawValue !== undefined) {
    return String(ctx.rawValue);
  }
  return formatNumber(numeric, decimals);
}

/** Like valueFor, but without padding or thousands separators. */
export function inputValue(ctx, id, numeric) {
  if (ctx && ctx.focusId === id && ctx.rawValue !== null && ctx.rawValue !== undefined) {
    return String(ctx.rawValue);
  }
  return formatInput(numeric);
}

export function pageHead({ title, meta = "", actions = "" }) {
  return `
    <header class="page-head">
      <div>
        <h1 class="t-page-title">${title}</h1>
      </div>
      ${meta ? `<span class="page-head__meta">${meta}</span>` : ""}
      ${actions ? `<div class="page-actions">${actions}</div>` : ""}
    </header>
  `;
}

export function emptyState({ icon, text, action = "" }) {
  return `
    <div class="empty">
      <i class="ti ${icon} empty__icon" aria-hidden="true"></i>
      <p class="empty__text">${text}</p>
      ${action}
    </div>
  `;
}

export function footerNote({ text, actionLabel, actionRoute, actionIcon = "ti-arrow-right" }) {
  return `
    <div class="footer-note">
      <p>${text}</p>
      ${
        actionLabel
          ? `<a class="btn btn--primary" href="#/${actionRoute}">${actionLabel}<i class="ti ${actionIcon}" aria-hidden="true"></i></a>`
          : ""
      }
    </div>
  `;
}

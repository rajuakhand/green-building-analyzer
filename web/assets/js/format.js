/**
 * Formatting helpers shared by every view.
 * Numbers follow the Python app's `f"{value:,.2f}"` output so printed
 * figures and the CSV export stay identical between the two front ends.
 */

const NUMBER_LOCALE = "en-US";

export function formatNumber(value, decimals = 2) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "0";
  return numeric.toLocaleString(NUMBER_LOCALE, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/** Reads a numeric input. Empty or invalid values become 0, negatives clamp to 0. */
export function readNumber(raw) {
  const cleaned = String(raw ?? "").replace(/,/g, "").trim();
  if (cleaned === "") return 0;
  const numeric = Number(cleaned);
  if (!Number.isFinite(numeric)) return 0;
  return numeric < 0 ? 0 : numeric;
}

export function formatInteger(value) {
  return formatNumber(value, 0);
}

/**
 * Stored factors keep their published precision: 1,120 stays 1,120 and
 * 14.679 stays 14.679 instead of being padded to a fixed number of decimals.
 */
export function formatFactor(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "0";
  return numeric.toLocaleString(NUMBER_LOCALE, { maximumFractionDigits: 4 });
}

/** Value for an editable field: no thousands separators, no padding. */
export function formatInput(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "";
  return numeric.toLocaleString(NUMBER_LOCALE, {
    maximumFractionDigits: 4,
    useGrouping: false,
  });
}

export function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/** CO2 with a real subscript, matching the wording used across the product. */
export const CO2E = "CO<sub>2</sub>e";

export function unitWithCo2e(unit) {
  return escapeHtml(unit).replace(/CO2e/g, CO2E);
}

export function percentOf(part, whole) {
  if (!whole || whole <= 0) return 0;
  return (part / whole) * 100;
}

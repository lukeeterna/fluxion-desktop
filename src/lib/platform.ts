/**
 * Platform detection utilities for Tauri WebView compatibility
 *
 * Tauri WebView has specific quirks with CSS transforms and z-index stacking contexts:
 * - CSS transforms create new stacking contexts that break z-index hierarchy
 * - Radix UI Portals may not work correctly in some WebView configurations
 * - Need conditional rendering strategies for dropdowns/popovers
 */

/**
 * Detects if the app is running inside a Tauri WebView environment
 *
 * Checks for:
 * 1. window.__TAURI__ object (Tauri v1)
 * 2. window.__TAURI_INTERNALS__ object (Tauri v2)
 * 3. navigator.userAgent containing 'Tauri'
 *
 * @returns boolean - true if running in Tauri WebView
 */
export function isInTauriWebView(): boolean {
  if (typeof window === 'undefined') {
    return false;
  }

  // Tauri v2 detection (primary)
  if ('__TAURI_INTERNALS__' in window) {
    return true;
  }

  // Tauri v1 detection (fallback)
  if ('__TAURI__' in window) {
    return true;
  }

  // User agent fallback (less reliable but useful for edge cases)
  if (typeof window.navigator !== 'undefined' && window.navigator.userAgent.includes('Tauri')) {
    return true;
  }

  return false;
}

/**
 * Detects if we're in a standard web browser (not Tauri)
 * Useful for enabling browser-specific features
 */
export function isInBrowser(): boolean {
  return !isInTauriWebView();
}

/**
 * Gets the current platform type
 */
export type PlatformType = 'tauri' | 'browser' | 'unknown';

export function getPlatformType(): PlatformType {
  if (typeof window === 'undefined') {
    return 'unknown';
  }

  if (isInTauriWebView()) {
    return 'tauri';
  }

  return 'browser';
}

/**
 * Z-Index hierarchy for consistent layering across the app
 * Higher numbers appear on top
 *
 * Usage in Tailwind: z-[var(--z-dropdown)] or direct z-[9000]
 */
export const Z_INDEX = {
  // Base content
  base: 0,

  // Sticky headers, fixed sidebars
  sticky: 100,

  // Modals backdrop
  modalBackdrop: 8000,

  // Modals content
  modal: 8500,

  // Dropdowns, selects, popovers (MUST be above modals for nested usage)
  dropdown: 9000,
  popover: 9000,
  select: 9000,

  // Tooltips (highest)
  tooltip: 9500,

  // Toast notifications (absolute highest)
  toast: 9999,
} as const;

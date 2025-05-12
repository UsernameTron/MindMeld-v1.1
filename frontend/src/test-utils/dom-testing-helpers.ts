// dom-testing-helpers.ts
// This file provides alternative assertion helpers for DOM testing in Vitest
// since the jest-dom extensions aren't working properly

/**
 * Check if an element is present in the document
 */
export function isInDocument(element: Element | null): boolean {
  return !!element && element.isConnected;
}

/**
 * Check if an element has a specific class
 */
export function hasClass(element: Element | null, className: string): boolean {
  return !!element && element.classList.contains(className);
}

/**
 * Check if an element has an attribute with a specific value
 */
export function hasAttribute(element: Element | null, attr: string, value?: string): boolean {
  if (!element) return false;
  
  if (value === undefined) {
    return element.hasAttribute(attr);
  }
  
  return element.getAttribute(attr) === value;
}

/**
 * Check if element has text content
 */
export function hasText(element: Element | null, text: string): boolean {
  return !!element && element.textContent?.includes(text) === true;
}

/**
 * Check if element is visible (not display: none, visibility: hidden, etc.)
 */
export function isVisible(element: Element | null): boolean {
  if (!element) return false;
  
  // Simple visibility check
  const style = window.getComputedStyle(element);
  return style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0';
}
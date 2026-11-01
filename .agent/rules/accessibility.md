# Workspace Rule: Accessibility (a11y)

## Requirements
1. **WCAG Compliance**: All components must satisfy WCAG 2.1 Level AA standards.
2. **Contrast**: Normal text contrast ratio $\ge 4.5:1$; large text and UI elements $\ge 3:1$.
3. **Keyboard Navigation**:
   - Complete focus rings (`focus-visible:ring-2`) on all interactive buttons, inputs, links, and dropdowns.
   - Global command palette accessible via `Cmd+K` / `Ctrl+K`.
   - Modals and drawers must trap focus and close cleanly on `Escape`.
4. **ARIA & Screen Readers**:
   - All charts and visual elements must have descriptive `aria-label` or accessible summary tables.
   - Screen-reader accessible data tables with semantic `th` and `td` tags.
5. **Automated Audit**:
   - Run `@axe-core/playwright` or equivalent in CI to enforce zero critical accessibility violations.

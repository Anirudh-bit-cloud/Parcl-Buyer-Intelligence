# Workspace Rule: Design Tokens & Visual Language

## Design Language
1. **Inspiration**: Modern B2B analytics (Linear × Stripe Dashboard × Mixpanel). Dense, breathable, data-first, high information fidelity.
2. **Color Tokens**:
   - Neutral slate/zinc base with high contrast text.
   - Primary brand accent: Indigo / Emerald accents.
   - Color-blind safe categorical palette for clusters (Okabe-Ito or Tol palettes).
   - Strict CSS variable definitions for light and dark modes.
3. **Typography**:
   - Primary: Inter for UI text.
   - Numeric Data: Tabular figures enabled (`font-variant-numeric: tabular-nums;`) for all metric cards, tables, and financial values.
   - Monospace: JetBrains Mono for client IDs, unit numbers, and transaction codes.
4. **Prohibitions**:
   - No generic template appearance.
   - No gratuitous animations or distracting rainbow gradients.
   - No emoji icons in core production UI; use Lucide icons.

# Workspace Rule: Testing Requirements

## Standards & Coverage
1. **Target**: Maintain $\ge 85\%$ test coverage on `packages/core`.
2. **Test Suites**:
   - **Unit Tests**: Test every transform, cleaner, schema, and derived feature in isolation (`pytest`).
   - **Property-Based Testing**: Use `hypothesis` to test edge cases, random unicode strings, date formats, and numeric extremes for cleaning pipelines.
   - **Golden Metric Regression Tests**: Verify that cluster assignment counts, ARI, and silhouette scores match saved golden references within tight numerical tolerance ($\pm 10^{-4}$).
   - **API Contract Tests**: Validate that FastAPI endpoints match OpenAPI / Pydantic schemas.
   - **Frontend & E2E Tests**: Component tests via Vitest, end-to-end critical journey testing via Playwright.

# Workflow: Run Tests

## Description
Executes the comprehensive automated testing suite: unit tests, property-based tests, golden-metric regression tests, and contract checks.

## Execution
```powershell
pytest packages/core/tests -v --cov=packages/core/parcl_core
```

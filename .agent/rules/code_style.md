# Workspace Rule: Code Style & Quality

## Standards
1. **Python**:
   - Python 3.11+ compatibility.
   - Adhere to PEP 8 standards enforced via Ruff (`ruff check` and `ruff format`).
   - Line length limit: 100 characters.
   - Meaningful docstrings on all public classes, functions, and modules.
   - Use pathlib `Path` over `os.path` manipulation.
2. **TypeScript / React**:
   - Strict mode enabled (`tsconfig.json` `strict: true`).
   - Standardize on functional components with React hooks.
   - Use clean JSX structure with named exports for reusable components.
   - Prettier + ESLint for consistent formatting.
3. **Repository Structure**:
   - Absolute imports within packages (e.g., `parcl_core.schemas`).
   - Maintain clear separation between core ML packages, API services, and frontends.

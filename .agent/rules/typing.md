# Workspace Rule: Strict Static Typing

## Python Typing (`mypy --strict`)
1. All function signatures in `packages/core` and `apps/api` must have explicit argument types and return type annotations.
2. Prohibit `Any` unless interfacing with an untyped 3rd-party library, in which case use explicit casting or typed wrappers.
3. Use Pydantic v2 schemas for all API payloads and settings.
4. Use Pandera schemas for runtime DataFrame validation across pipeline boundaries.

## TypeScript Typing (`tsc --noEmit`)
1. No `any` types allowed in the frontend codebase. Use `unknown` with runtime type narrowing or Zod schemas.
2. All API responses must be parsed or validated against Zod schemas.
3. Strongly typed component props with explicit interfaces or type aliases.

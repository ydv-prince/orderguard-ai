# Contributing to OrderGuard AI

Thank you for your interest in contributing!

## Branching & Commit Practices
- We follow **Conventional Commits** (e.g., `feat:`, `fix:`, `docs:`, `test:`).
- Always branch off `main` for your feature work.
- Keep commits focused on a single logical change. Do not bundle unrelated features together.

## Local Development
1. Use the provided instructions in `README.md` to spin up the local development environment using `npm run dev` and `uvicorn main:app --reload`.
2. Ensure you run the `pytest` test suite before proposing a change.
3. Update relevant documentation (e.g., `docs/api.md` or `docs/architecture.md`) if you modify core behavior.

## Pull Requests
- Provide a clear summary of your changes.
- Ensure all tests and linting steps pass.
- Do not commit sensitive environment variables or credentials.

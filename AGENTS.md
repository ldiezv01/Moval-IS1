# Repository Guidelines

## Project Structure & Module Organization
- Root: `README.md`, `AGENTS.md` (this file).
- Source: `code/` (each module owns its build/test config).
- Documentation: `docs/` (guides, diagrams, ADRs, SRS: `docs/Plantilla_IEEE830-1998_Moval.pdf`).
- Tests: keep near source (e.g., `code/<module>/tests` or `code/<module>/__tests__`).

## Build, Test, and Development Commands
- Per-module: run commands from the module folder inside `code/`.
- Node module: `npm ci && npm test` (if `package.json` exists), `npm run build` to produce artifacts.
- Python module: `python -m venv .venv && .venv/Scripts/Activate.ps1` then `pip install -r requirements.txt`, `pytest` to run tests.
- Generic: prefer module-level `Makefile` or `package.json` scripts when present. Check `README.md` inside each module.

## Coding Style & Naming Conventions
- Indentation: 2 spaces (JS/TS), 4 spaces (Python/Java).
- Naming: `camelCase` for variables/functions, `PascalCase` for classes/types, `snake_case` for Python functions/tests.
- Formatting: use the formatter configured by the module (`prettier`, `black`, etc.). Run before committing.
- File names: tests `*.spec.ts|js` or `test_*.py`; avoid spaces.

## Testing Guidelines
- Frameworks: Jest/Vitest for JS, Pytest for Python (module-dependent).
- Location: co-locate tests with code; small units over large fixtures.
- Coverage: aim >= 80% per module unless documented otherwise.
- Run: from module folder, use `npm test` or `pytest -q`. Add failing test first when fixing bugs.

## Requirements & Traceability
- Use SRS requirement IDs (e.g., REQ-012) from `docs/Plantilla_IEEE830-1998_Moval.pdf`.
- Commits: include relevant IDs. Example: "feat: discount calc (REQ-012)".
- Tests: tag/name with IDs (e.g., `test_req_012_*`, `@pytest.mark.req_012`).
- Traceability: maintain `docs/traceability.csv` mapping `REQ-ID,module path,test name`.

## Commit & Pull Request Guidelines
- Commits: imperative mood, concise scope. Example: "feat: add auth middleware".
- Reference issues: `Fixes #123` or `Refs #123` when applicable.
- Reference SRS where relevant (IDs/sections, e.g., REQ-012; §3.2.1).
- PRs: include summary, motivation, testing steps, screenshots (UI), and linked issue. Keep PRs focused and small.

## Security & Configuration Tips
- Never commit secrets. Use `.env.local` and provide `.env.example` with placeholders.
- Validate inputs and handle errors centrally in each module.

## Agent-Specific Instructions
- This file applies repo-wide. Prefer module-level READMEs for specifics.
- When editing or generating files, match existing patterns within that module before introducing new ones.

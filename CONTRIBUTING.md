# Contributing

This repository is set up as a small **software factory**: a labeled issue can become a draft PR, required CI must pass, a human merges, and a git tag publishes the package.

## Factory flow

1. Open an issue with the Bug or Enhancement template. Include Airflow version, reproduction, and expected vs actual behavior.
2. Maintainers triage it (see [Labels](#labels)). Issues marked `factory-eligible` are in scope for an implementation PR.
3. Open a **draft** pull request from a feature branch. Do not merge your own factory PRs.
4. Wait for required GitHub checks (see [Required checks](#required-checks)). Fix failures on the PR; do not disable checks.
5. A human reviews, marks the PR ready, and merges to `main`.
6. A maintainer cuts a tagged release (`vX.Y.Z` or `vX.Y.ZrcN`). See [RELEASING.md](RELEASING.md).

## Labels

Create these labels in the GitHub repo settings before using them. Templates document the scheme; they do not create labels.

| Label | Meaning |
| --- | --- |
| `needs-triage` | New issue, not yet classified |
| `factory-eligible` | Scoped enough for an implementation PR |
| `security` | Security-sensitive (auth, secrets, access control) |
| `airflow-2` | Affects Apache Airflow 2.x / REST `/api/v1` |
| `airflow-3` | Affects Apache Airflow 3.x / REST `/api/v2` |
| `size/S` | Small (roughly one file or a config-only change) |
| `size/M` | Medium (one area, limited API surface) |
| `size/L` | Large (cross-cutting or Airflow-version work) |

## Development setup

```bash
uv sync --dev
```

Optional: copy environment variables into `.env`. Tests do not require a live Airflow instance.

### Commands

| Command | What it does |
| --- | --- |
| `make lint` | Ruff format **check** and ruff check (**no `--fix`**) |
| `make lint-fix` | Apply ruff fixes and formatting |
| `make typecheck` | mypy on `src/` |
| `make test` | Unit + contract tests (`-m "not integration"`) |
| `make test-contract` | OpenAPI contract tests only |
| `make airflow-up` | Start Airflow 2.10.5 via docker compose |
| `make test-integration` | Live tool calls (`-m integration`) |
| `make airflow-down` | Stop the compose stack |

CI never passes `--fix` to ruff. A lint failure means the PR must be updated, not auto-fixed in GitHub Actions.

### Contract tests

`test/contracts` vendors Airflow **2.10.5** stable REST OpenAPI (`/api/v1`) and checks that each MCP tool's client path, HTTP method, parameters, and request-body fields exist in that spec.

The runtime client is `apache-airflow-client>=2.7.0,<3`, so Airflow 3 is out of contract scope until the pin is lifted.

### Integration tests

`test/integration` starts Airflow with `test/integration/docker-compose.yaml` and calls a few tools (health, version, list DAGs, pools, variable round-trip).

The CI matrix runs Airflow **2.10.5** (required) and **3.4.0** (skipped / allowed-failure). The 3.x job is skipped because `apache-airflow-client` is pinned to `<3`.

## Required checks

Maintainers should mark these GitHub Actions **job names** as required status checks on `main` (branch protection is configured in repo settings, not in this PR):

- `lint`
- `typecheck`
- `test (3.10)`
- `test (3.11)`
- `test (3.12)`
- `contract`
- `integration (2.10.5)`
- `factory-gate`

Do **not** require `integration (3.4.0)`; it is an allowed-failure placeholder until the client pin is removed.

`factory-gate` fails the workflow if any of the required jobs above failed.

## Pull requests

- Keep behavior changes covered by unit, contract, or integration tests as appropriate.
- Do not bump `project.version` unless the PR is meant to be released; tagging is the release trigger (see [RELEASING.md](RELEASING.md)).
- Draft PRs are the default for factory work until CI is green and a human is ready to merge.

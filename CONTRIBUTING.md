# Contributing

This repository is a **software factory**: an issue that is labeled and sized can become a draft PR, must pass required checks, is merged by a human, and is released from a version tag.

## Factory flow

1. Open an issue with the bug or enhancement template. Include Airflow version, reproduction, and expected vs actual.
2. A maintainer triages it (labels below) and, if it is self-contained, marks it `factory-eligible`.
3. Work happens on a branch. Open a **draft** pull request first.
4. Required CI checks must be green. Do not merge your own factory PR unless you are the code owner doing an explicit review.
5. A human (code owner) marks the PR ready, reviews, and merges to `main`.
6. A tagged release (`vX.Y.Z` or `vX.Y.ZrcN`) publishes the package. See [RELEASING.md](RELEASING.md).

Do not change GitHub branch protection, create labels, or publish from a PR. Those are maintainer actions.

## Labels

These labels are the triage scheme. They may need to be created once in the GitHub UI (Issues → Labels). Do not invent extra labels for the factory.

| Label | Meaning |
| --- | --- |
| `needs-triage` | New issue, not yet classified |
| `factory-eligible` | Scoped enough for an agent or contributor to draft a PR |
| `security` | Credential handling, auth, or untrusted input |
| `airflow-2` | Affects Airflow 2.x / stable REST `/api/v1` |
| `airflow-3` | Affects Airflow 3.x / REST `/api/v2` (blocked today by `apache-airflow-client>=2.7.0,<3`) |
| `size/S` | Small, localized change |
| `size/M` | Moderate, a few files or a new check |
| `size/L` | Large or cross-cutting |

GitHub also has default `bug` / `enhancement` labels, which the issue forms apply.

## Development

```bash
uv sync --dev
make lint          # ruff format --check and ruff check (no --fix)
make lint-fix      # apply ruff fixes locally
make typecheck     # mypy on src/
make test          # unit + contract tests (not live Airflow)
make test-contract
```

Integration tests start Airflow 2.10 with Docker Compose:

```bash
docker compose -f docker/airflow/docker-compose.yaml up -d --wait
AIRFLOW_INTEGRATION=1 AIRFLOW_HOST=http://127.0.0.1:8080 \
  AIRFLOW_USERNAME=airflow AIRFLOW_PASSWORD=airflow \
  make test-integration
docker compose -f docker/airflow/docker-compose.yaml down -v
```

CI never runs `ruff check --fix`. `make lint` is check-only so a dirty tree cannot be auto-fixed in GitHub Actions.

## Required checks

Ask a maintainer to mark these GitHub Actions **job names** as required on `main` (Settings → Branches). This repo does not change branch protection from PRs.

- `lint`
- `typecheck`
- `test (3.10)`
- `test (3.11)`
- `test (3.12)`
- `contract`
- `integration (2.10.4)`

Do **not** require `integration (3.x)` (skipped / allowed to fail while the client is pinned `<3`), `publish-pypi`, `smoke-pypi`, `publish-testpypi`, `smoke-testpypi`, or `claude`.

## Pull requests

- Keep the PR focused. Backlog features belong in their own PRs.
- Include tests for new tools: unit tests plus an OpenAPI contract expectation (path, params, schema).
- Do not bump `project.version` unless the change is meant to ship in the next tagged release (see [RELEASING.md](RELEASING.md)).
- Draft until required checks are green.

## Airflow 3

`apache-airflow-client` is pinned to `>=2.7.0,<3`, which only supports the v1 stable REST API. Airflow 3 integration is a skipped/allowed-failure job until that pin is removed and the wrappers speak `/api/v2`.

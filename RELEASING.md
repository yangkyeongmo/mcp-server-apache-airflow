# Releasing

Releases are **tags**, not GitHub "release created" events and not PyPI API tokens.

## Versioning

- Follow [SemVer](https://semver.org/) in `pyproject.toml` `project.version`.
- Production tag: `vX.Y.Z` (example `v0.2.11`) must equal that version.
- Pre-release tag: `vX.Y.ZrcN` (example `v0.2.11rc1`) publishes only to TestPyPI.

## Publish flow

1. Merge the release-ready changes to `main` (human merge after required checks).
2. Set `project.version` on `main` if it is not already the version you will tag.
3. Tag and push:
   - Production: `git tag v0.2.11 && git push origin v0.2.11`
   - TestPyPI: `git tag v0.2.11rc1 && git push origin v0.2.11rc1`
4. GitHub Actions workflow `.github/workflows/publish.yml` builds the sdist/wheel and publishes with **OIDC trusted publishing** (no `PYPI_API_TOKEN`).
5. A follow-on job smoke-installs that exact version (`mcp-server-apache-airflow --help`).

Do not upload with `twine` and a token from a laptop unless trusted publishing is down and you are doing an emergency hotfix.

## Trusted publisher settings to register

Register these once on PyPI and TestPyPI (Publishing settings). Environment names must match the workflow.

### PyPI (`https://pypi.org/manage/project/mcp-server-apache-airflow/settings/publishing/`)

| Field | Value |
| --- | --- |
| Owner | `yangkyeongmo` |
| Repository | `mcp-server-apache-airflow` |
| Workflow | `publish.yml` |
| Environment | `pypi` |

### TestPyPI (`https://test.pypi.org/manage/project/mcp-server-apache-airflow/settings/publishing/`)

| Field | Value |
| --- | --- |
| Owner | `yangkyeongmo` |
| Repository | `mcp-server-apache-airflow` |
| Workflow | `publish.yml` |
| Environment | `testpypi` |

Also create GitHub Environments named `pypi` and `testpypi` (optional protection rules such as required reviewers). The workflow references them; this repository does not create them from a PR.

After the first successful trusted publish you can delete any leftover `PYPI_API_TOKEN` repository secret. Do not add a new token.

## Rollback

Prefer a **hotfix release**:

1. Revert or fix on a branch from `main`.
2. Bump the patch version (or a new `rc` for TestPyPI).
3. Merge, tag `vX.Y.Z`, and let `publish.yml` ship the new version.

**Yank** on PyPI only if the release is actively harmful (for example it deletes user data or ships credentials) and a hotfix cannot ship quickly enough. Yanking does not remove already-installed copies. Document the yank reason on the GitHub tag.

Do not reuse a version number. Do not force-push tags that have already published.

## What this workflow no longer does

- It does not publish on `release: created`.
- It does not pass `user` / `password` to `pypa/gh-action-pypi-publish`.

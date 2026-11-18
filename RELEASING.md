# Releasing

Publishing is tag-driven and uses **PyPI trusted publishing (OIDC)**. There is no API token in GitHub Actions.

## Version numbers

1. Set `project.version` in `pyproject.toml` to the version you are releasing.
2. The git tag must match that version with a `v` prefix.

| Tag | Destination |
| --- | --- |
| `vX.Y.Z` (for example `v0.2.11`) | PyPI |
| `vX.Y.ZrcN` (for example `v0.2.11rc1`) | TestPyPI |

Follow [SemVer](https://semver.org/). Release candidates go to TestPyPI only.

## Cut a release

```bash
# after merging to main, on a clean checkout of main
git tag -a v0.2.11 -m "v0.2.11"
git push origin v0.2.11
```

The `Publish Python Package` workflow then:

1. Rejects tags that are not `vX.Y.Z` or `vX.Y.ZrcN`, and rejects a tag that does not match `pyproject.toml`.
2. Builds the sdist and wheel.
3. Uploads with `pypa/gh-action-pypi-publish` via OIDC (no `password` / `PYPI_API_TOKEN`).
4. Smoke-installs the published version and runs `mcp-server-apache-airflow --help`.

GitHub Environments used by the workflow: `pypi` and `testpypi`.

## Trusted publisher settings

Register these on PyPI and TestPyPI **before** the first tag. Do not store a PyPI token in GitHub secrets.

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

## Rollback

Prefer a **hotfix release**, not a yank:

1. Merge the fix to `main`.
2. Bump `project.version` (patch bump).
3. Tag and push `vX.Y.Z` so a newer version supersedes the bad one.

Yank from PyPI only if the release is actively harmful (for example, it deletes user data or ships credentials). A yank hides the version from `pip install` but does not delete files already downloaded.

```bash
# last resort, from a trusted maintainer machine — not from CI
pip install twine
twine yank mcp-server-apache-airflow 0.2.11 --reason "broken release; use 0.2.12"
```

Do not reuse a yanked version number. Always ship a new tag.

# Airflow MCP Servers: Comparison & Migration Guide

This document covers why we chose our upstream fork, alternative MCP server options, and Airflow v2 → v3 migration considerations.

---

## Why We Forked yangkyeongmo/mcp-server-apache-airflow

We forked [yangkyeongmo/mcp-server-apache-airflow](https://github.com/yangkyeongmo/mcp-server-apache-airflow) as our base because:

- **Stability & simplicity** — A foundational, no-frills implementation with ~130 GitHub stars
- **Standardized API wrapping** — Clean abstraction over the Airflow REST API
- **Active maintenance** — Regular updates and community contributions
- **Extensible architecture** — Easy to add our SSO authentication layer without rewriting core logic

**Note:** This is a community-maintained project, not an official Apache Airflow project.

---

## Alternative MCP Servers

| Server | Primary Focus | Airflow Support | Authentication | Best For |
|--------|---------------|-----------------|----------------|----------|
| [yangkyeongmo/mcp-server-apache-airflow](https://github.com/yangkyeongmo/mcp-server-apache-airflow) | Standardized API wrapping | 2.x/3.x (configurable) | Env vars (Basic Auth) | **Our choice** — stable foundation |
| [abhishekbhakat/airflow-mcp-server](https://github.com/abhishekbhakat/airflow-mcp-server) | MCPHub certified, Airflow 3.0+ | 3.0+ only | JWT Token | Teams fully on Airflow 3.0+ |
| [call518/MCP-Airflow-API](https://github.com/call518/MCP-Airflow-API) | Natural language, version flexibility | 2.x and 3.x | Bearer/Basic Auth | Mixed v2/v3 environments |
| [hipposys-ltd/airflow-mcp](https://github.com/hipposys-ltd/airflow-mcp) | LangChain integration, analytics | 2.x/3.x | Env vars | High-level analysis |

### Why not abhishekbhakat?

While it's MCPHub certified and optimized for Airflow 3.0+, it requires JWT authentication — which doesn't work with our enterprise SSO setup. Our fork adds SSO cookie-based auth on top of yangkyeongmo's flexible base.

### Feature Comparison

| Feature | yangkyeongmo | abhishekbhakat | call518 |
|---------|--------------|----------------|---------|
| Airflow 2.x support | ✅ | ❌ | ✅ |
| Airflow 3.0+ support | ⚠️ Configurable | ✅ Native | ✅ Dynamic |
| SSO/Cookie auth | ✅ (our fork) | ❌ | ❌ |
| JWT auth | ❌ | ✅ | ✅ |
| MCPHub certified | ❌ | ✅ | ❌ |

---

## Airflow v2 → v3 Migration

### TASK: https://linear.app/ready-boss/issue/DATA-2081/evaluate-mcp-server-for-airflow-3-compatibility 

### Timeline

⚠️ **Apache Airflow 2.x reaches end-of-life in April 2026.**

| Date | Event |
|------|-------|
| April 2025 | Airflow 3.0 released |
| May 2025 | Airflow 2.11.0 released (final 2.x) |
| **April 2026** | **Airflow 2.x end-of-life** — no more security patches |
| May 2026 | Airflow project moves to >= 3.1 |

### Key API Changes in Airflow 3.0

| Aspect | Airflow 2.x | Airflow 3.0+ |
|--------|-------------|--------------|
| REST API version | `/api/v1/*` | `/api/v2/*` |
| Authentication | Basic Auth, Session cookies | **JWT required** |
| Context keys | `execution_date` | `logical_date` |
| Operators | Built-in | Moved to `airflow-providers-standard` |
| SubDAGs | Supported (deprecated) | Removed — use Task Groups |
| SLA feature | Supported | Removed |

### Current MCP Server Support

- ✅ `AIRFLOW_API_VERSION=v1` — Airflow 2.x clusters (default, fully tested)
- ⚠️ `AIRFLOW_API_VERSION=v2` — Airflow 3.0+ (env var exists, but **not tested**)

### Known v3 Limitations

1. **SSO auth probe hardcodes v1** — [sso_cookie_auth.py:149](src/airflow/sso_cookie_auth.py#L149) uses `/api/v1/dags`
2. **Cookie-based auth may not work** — Airflow 3.0 requires JWT tokens
3. **Untested** — No validation against Airflow 3.0 environments yet

### Migration Options

When migrating to Airflow 3:

1. **Test first** — Try `AIRFLOW_API_VERSION=v2` with your Airflow 3 instance. May work if cookies are still accepted.

2. **If JWT required**, consider:
   - **Option A:** Update this fork's SSO module to support JWT token exchange
   - **Option B:** Fork [abhishekbhakat/airflow-mcp-server](https://github.com/abhishekbhakat/airflow-mcp-server) and add SSO support
   - **Option C:** Use [call518/MCP-Airflow-API](https://github.com/call518/MCP-Airflow-API) with dynamic API versioning

3. **Track progress** — See [DATA-2081](https://linear.app/ready-boss/issue/DATA-2081/evaluate-mcp-server-for-airflow-3-compatibility) for our evaluation task

---

## Migration Resources

- [Upgrading Airflow 2 to 3 Checklist](https://www.astronomer.io/blog/upgrading-airflow-2-to-airflow-3-a-checklist-for-2026/) (Astronomer)
- [Official Airflow 3 Upgrade Guide](https://airflow.apache.org/docs/apache-airflow/stable/installation/upgrading_to_airflow3.html)
- [Ruff AIR3 rules](https://airflow.apache.org/docs/apache-airflow/stable/installation/upgrading.html) for automatic DAG migration
- [DATA-2079: Establish Airflow 3 Repository](https://linear.app/ready-boss/issue/DATA-2079) — Team migration plan

---

## References

- [The AI Engineer's Guide to Airflow MCP Servers](https://skywork.ai/skypage/en/ai-engineer-guide-airflow-server/1980148238091145216)
- [Apache Airflow Release Plan](https://cwiki.apache.org/confluence/display/AIRFLOW/Release+Plan)
- [Airflow Summit 2026: Seamless Upgrades](https://airflowsummit.org/sessions/2025/seamless-airflow-upgrades/)

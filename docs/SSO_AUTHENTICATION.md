# Apache Airflow MCP Server — SSO Authentication Extension

## Purpose

This document describes a fork of the public Apache Airflow MCP server with an enterprise SSO cookie-based authentication extension. The extension integrates Playwright-driven SSO login, encrypted cookie persistence, and automatic session refresh into the existing Airflow SDK client — without rewriting upstream transport logic.

| Repository | URL |
|------------|-----|
| **Upstream** | https://github.com/yangkyeongmo/mcp-server-apache-airflow |
| **Fork (Ready)** | https://github.com/zedahmed144/mcp-server-apache-airflow |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MCP Client (AMP)                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         mcp-server-apache-airflow                           │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      create_api_client()                              │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│  │  │ SSO Cookie  │◀─│ JWT Token   │◀─│ Basic Auth  │◀─│ Unauth      │   │  │
│  │  │ (priority 1)│  │ (priority 2)│  │ (priority 3)│  │ (fallback)  │   │  │
│  │  └──────┬──────┘  └─────────────┘  └─────────────┘  └─────────────┘   │  │
│  └─────────┼─────────────────────────────────────────────────────────────┘  │
│            │                                                                 │
│            ▼                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        SSORESTClient                                  │  │
│  │  • Injects Cookie header into requests                                │  │
│  │  • Refreshes cookies on 401/403/302                                   │  │
│  │  • Thread-safe cookie refresh via lock                                │  │
│  └──────┬────────────────────────────────────────────────────────────────┘  │
│         │                                                                    │
│         ▼                                                                    │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     EncryptedCookieStore                              │  │
│  │  ┌─────────────┐    ┌─────────────────┐                               │  │
│  │  │ key (Fernet)│───▶│ cookies.enc     │                               │  │
│  │  │ (AES-128)   │    │ (encrypted JSON)│                               │  │
│  │  └─────────────┘    └─────────────────┘                               │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              │                                               │
              ▼                                               ▼
┌──────────────────────────┐                    ┌──────────────────────────┐
│   Playwright (Chromium)  │                    │     Airflow REST API     │
│   • Opens SSO login page │                    │     /api/v1/*            │
│   • Captures cookies     │                    │                          │
│   • 5-minute timeout     │                    │                          │
└──────────────────────────┘                    └──────────────────────────┘
              │                                               ▲
              ▼                                               │
┌──────────────────────────┐                                  │
│   Enterprise IdP         │                                  │
│   (Okta, Azure AD, etc.) │──────────────────────────────────┘
└──────────────────────────┘
```

---

## Authentication Flow

```
1. MCP server starts
2. create_api_client() checks AIRFLOW_SSO_AUTH=true
3. Load encrypted cookies from {STATE_DIR}/cookies.enc
   │
   ├─▶ Cookies exist & valid?
   │      │
   │      ├─▶ YES: Decrypt with Fernet key, validate against API
   │      │         └─▶ API returns 200? Use session
   │      │         └─▶ API returns 401/403? → Trigger re-auth
   │      │
   │      └─▶ NO (expired/missing/corrupted):
   │
   └─▶ Launch Playwright browser
         │
         ├─▶ Navigate to AIRFLOW_HOST
         ├─▶ User completes SSO login (5-min timeout)
         ├─▶ Poll /api/v1/dags until 200
         ├─▶ Capture cookies from browser context
         ├─▶ Encrypt & save to cookies.enc
         └─▶ Return authenticated session
```

---

## Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `AIRFLOW_HOST` | string | `http://localhost:8080` | Airflow base URL (required for production) |
| `AIRFLOW_SSO_AUTH` | bool | `false` | Enable SSO cookie-based authentication |
| `AIRFLOW_STATE_DIR` | path | `~/.airflow_cookie_state` | Directory for encrypted cookie/key storage |
| `AIRFLOW_HEADLESS` | bool | `false` | Run Playwright browser in headless mode |
| `AIRFLOW_MAX_COOKIE_AGE_HOURS` | int | `24` | Force re-authentication after N hours |
| `AIRFLOW_VERIFY` | bool/path | `true` | TLS verification (`true`, `false`, or path to CA bundle) |
| `AIRFLOW_COOKIE_KEY` | string | auto-generated | Override Fernet encryption key (base64-encoded) |
| `AIRFLOW_JWT_TOKEN` | string | — | JWT bearer token (if not using SSO) |
| `AIRFLOW_USERNAME` | string | — | Basic auth username (if not using SSO/JWT) |
| `AIRFLOW_PASSWORD` | string | — | Basic auth password (if not using SSO/JWT) |
| `AIRFLOW_API_VERSION` | string | `v1` | Airflow REST API version |
| `READ_ONLY` | bool | `false` | Restrict to read-only API operations |

---

## Files Added & Modified

### NEW: `src/airflow/sso_cookie_auth.py`

**Role:** Implements SSO-based session acquisition, cookie encryption, caching, and refresh.

**Classes:**

| Class | Responsibility |
|-------|----------------|
| `AirflowAuthConfig` | Dataclass holding auth configuration |
| `EncryptedCookieStore` | Manages Fernet key generation, cookie encryption/decryption, file I/O |
| `AirflowCookieAuth` | Orchestrates Playwright login, cookie capture, session validation |

**Key Methods:**

```python
EncryptedCookieStore._get_key()      # Load/generate Fernet key
EncryptedCookieStore.save(payload)   # Encrypt and persist cookies
EncryptedCookieStore.load()          # Decrypt and return cookies

AirflowCookieAuth.ensure_session()   # Get valid session (cached or fresh)
AirflowCookieAuth.get_cookie_header() # Return "Cookie: ..." header value
```

### MODIFIED: `src/airflow/airflow_client.py`

**Purpose:** Extend upstream Airflow SDK client to support SSO cookie injection.

**New Class: `SSORESTClient`**

Subclass of `RESTClientObject` that:
- Injects `Cookie` header into every request
- Refreshes cookies on `401`, `403`, or `302` responses
- Retries failed request once after refreshing
- Maintains thread-safe cookie refresh via `threading.Lock`

---

## Cookie Storage & Security

### File Locations

| File | Path | Permissions | Contents |
|------|------|-------------|----------|
| Fernet key | `{STATE_DIR}/key` | `0600` | 32-byte base64-encoded key |
| Encrypted cookies | `{STATE_DIR}/cookies.enc` | `0600` | Fernet-encrypted JSON blob |

### Encryption Details

- **Algorithm:** Fernet (AES-128-CBC + HMAC-SHA256)
- **Key source priority:**
  1. `AIRFLOW_COOKIE_KEY` environment variable
  2. Auto-generated file at `{STATE_DIR}/key`
- **Payload format:**
  ```json
  {
    "cookies": [{"name": "session", "value": "...", "domain": "...", "path": "/"}],
    "captured_at": 1706198400
  }
  ```

### Key Rotation

To rotate the encryption key:
```bash
rm -f $AIRFLOW_STATE_DIR/key $AIRFLOW_STATE_DIR/cookies.enc
# Next run will generate new key and require re-authentication
```

---

## Local Developer Setup

### 1. Clone the Repository

```bash
git clone https://github.com/zedahmed144/mcp-server-apache-airflow
cd mcp-server-apache-airflow
```

### 2. Install Dependencies

```bash
# Install with SSO support
uv sync --extra sso

# Install Playwright browser
uv run playwright install chromium
```

### 3. Configure AMP

Add to `~/.config/amp/settings.json`:

```json
{
  "mcpServers": {
    "airflow-sso": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/mcp-server-apache-airflow",
        "--extra",
        "sso",
        "mcp-server-apache-airflow"
      ],
      "env": {
        "AIRFLOW_HOST": "https://your-airflow-instance.example.com",
        "AIRFLOW_SSO_AUTH": "true",
        "AIRFLOW_VERIFY": "true",
        "AIRFLOW_STATE_DIR": "/path/to/mcp-server-apache-airflow/.airflow_state",
        "READ_ONLY": "true"
      }
    }
  }
}
```

### 4. First Run

1. Restart AMP and trust the new MCP server
2. A browser window will open to your Airflow instance
3. Complete SSO authentication (Okta, Azure AD, etc.)
4. Cookies are captured, encrypted, and saved automatically
5. Subsequent runs use cached cookies until expiry

---

## Debug Mode

### Non-Headless Login (See Browser)

```bash
AIRFLOW_HOST=https://airflow.example.com \
AIRFLOW_SSO_AUTH=true \
AIRFLOW_HEADLESS=false \
AIRFLOW_STATE_DIR=./.airflow_state \
uv run mcp-server-apache-airflow
```

### Verbose Output

The SSO module prints status to stderr:
```
Using SSO cookie-based authentication for Airflow
[SSO] API probe status: 302
[SSO] API probe status: 200
[SSO] Captured 5 cookies
```

### Force Re-Authentication

```bash
# Delete cached cookies to trigger fresh login
rm -f $AIRFLOW_STATE_DIR/cookies.enc
```

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `InvalidToken` exception on startup | Key/cookie mismatch (key rotated or corrupted) | Delete `cookies.enc` and `key`, re-authenticate |
| Browser doesn't open | Playwright not installed | Run `uv run playwright install chromium` |
| `403 Forbidden` after login | Cookies not captured correctly | Ensure SSO redirects back to Airflow domain |
| `Login did not yield an authorized browser session` | SSO login timed out (5 min) | Complete login faster, or check network issues |
| SSL certificate errors | Self-signed or internal CA | Set `AIRFLOW_VERIFY=false` or path to CA bundle |
| `No 'session' cookie captured` warning | Airflow uses different cookie name | Usually safe to ignore; auth may still work |
| Cookies expire too quickly | IdP session shorter than 24h | Lower `AIRFLOW_MAX_COOKIE_AGE_HOURS` |
| `Cookie file corrupted` warning | Disk issue or interrupted write | Automatic recovery; re-auth triggered |

### Reset All State

```bash
rm -rf $AIRFLOW_STATE_DIR
# Fresh start on next run
```

---

## CI/CD Integration

For headless environments (CI pipelines, servers):

### Option 1: Pre-Authenticated Cookies

1. Run locally with `AIRFLOW_HEADLESS=false` to capture cookies
2. Copy `cookies.enc` and `key` to CI environment
3. Set `AIRFLOW_STATE_DIR` to point to copied files

### Option 2: Use JWT or Basic Auth

```bash
# CI environment - skip SSO, use service account
export AIRFLOW_SSO_AUTH=false
export AIRFLOW_USERNAME=ci-service-account
export AIRFLOW_PASSWORD=$CI_AIRFLOW_PASSWORD
```

### Option 3: Headless SSO (If IdP Supports)

Some IdPs allow programmatic auth. Set:
```bash
AIRFLOW_HEADLESS=true
```
Note: This only works if your IdP doesn't require interactive CAPTCHA/MFA.

---

## Security Considerations

| Aspect | Implementation |
|--------|----------------|
| **Cookie encryption** | Fernet (AES-128-CBC + HMAC-SHA256) |
| **File permissions** | Key and cookies stored with `0600` (owner-only) |
| **Key storage** | Local file or environment variable (not in repo) |
| **TLS verification** | Enabled by default; disable only for testing |
| **Session hijacking** | Cookies tied to Airflow domain; encrypted at rest |
| **Credential exposure** | No passwords stored; only session cookies |

### Recommendations

1. **Never commit** `STATE_DIR` contents to version control
2. **Add to `.gitignore`:**
   ```
   .airflow_state/
   ```
3. **Use short cookie TTL** in production (`AIRFLOW_MAX_COOKIE_AGE_HOURS=8`)
4. **Rotate keys periodically** by deleting key file

---

## API Reference

### `AirflowCookieAuth`

```python
from src.airflow.sso_cookie_auth import AirflowAuthConfig, AirflowCookieAuth

cfg = AirflowAuthConfig(
    base_url="https://airflow.example.com",
    state_dir="~/.airflow_state",
    headless=False,
    verify=True,
    max_cookie_age_hours=24,
)

auth = AirflowCookieAuth(cfg)

# Get authenticated requests.Session
session = auth.ensure_session()
response = session.get("https://airflow.example.com/api/v1/dags")

# Get raw cookie header for SDK injection
cookie_header = auth.get_cookie_header()
# Returns: "session=abc123; other_cookie=xyz"
```

### `EncryptedCookieStore`

```python
from src.airflow.sso_cookie_auth import EncryptedCookieStore

store = EncryptedCookieStore(state_dir="~/.airflow_state")

# Save cookies
store.save({"cookies": [...], "captured_at": 1706198400})

# Load cookies (returns None if missing/corrupted)
payload = store.load()
```

---

## Changelog

| Version | Changes |
|---------|---------|
| 0.2.9 | Added SSO cookie authentication support |
| 0.2.8 | Upstream baseline (JWT + Basic Auth only) |

"""
SSO Cookie-based authentication for Apache Airflow.

Supports enterprise identity providers like Okta, Azure AD, Ping Identity, etc.
Uses Playwright to capture SSO session cookies via browser-based login.
"""

import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import requests
from cryptography.fernet import Fernet, InvalidToken


@dataclass
class AirflowAuthConfig:
    base_url: str
    state_dir: str
    headless: bool = False
    verify: Union[bool, str] = True
    max_cookie_age_hours: int = 24


class EncryptedCookieStore:
    """Securely stores and retrieves encrypted SSO cookies."""

    def __init__(self, state_dir: str):
        self.state_dir = os.path.expanduser(state_dir)
        self.key_path = os.path.join(self.state_dir, "key")
        self.cookie_path = os.path.join(self.state_dir, "cookies.enc")
        os.makedirs(self.state_dir, exist_ok=True)
        try:
            os.chmod(self.state_dir, 0o700)
        except OSError:
            pass

    def _get_key(self) -> bytes:
        env_key = os.environ.get("AIRFLOW_COOKIE_KEY")
        if env_key:
            return env_key.encode("utf-8")

        if not os.path.exists(self.key_path):
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as f:
                f.write(key)
            try:
                os.chmod(self.key_path, 0o600)
            except OSError:
                pass
        else:
            with open(self.key_path, "rb") as f:
                key = f.read()
        return key

    def _fernet(self) -> Fernet:
        return Fernet(self._get_key())

    def save(self, payload: Dict[str, Any]) -> None:
        f = self._fernet()
        token = f.encrypt(json.dumps(payload).encode("utf-8"))

        fd, tmp_path = tempfile.mkstemp(dir=self.state_dir, prefix="cookies_", suffix=".tmp")
        try:
            os.write(fd, token)
            os.close(fd)
            try:
                os.chmod(tmp_path, 0o600)
            except OSError:
                pass
            os.replace(tmp_path, self.cookie_path)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def load(self) -> Optional[Dict[str, Any]]:
        if not os.path.exists(self.cookie_path):
            return None

        try:
            f = self._fernet()
            with open(self.cookie_path, "rb") as inp:
                token = inp.read()
            data = f.decrypt(token)
            return json.loads(data.decode("utf-8"))
        except (InvalidToken, json.JSONDecodeError, OSError) as e:
            backup_path = self.cookie_path + f".corrupted.{int(time.time())}"
            try:
                os.rename(self.cookie_path, backup_path)
                print(f"Warning: Cookie file corrupted, moved to {backup_path}: {e}", file=sys.stderr)
            except OSError:
                pass
            return None


class AirflowCookieAuth:
    """
    SSO Cookie-based authentication for Airflow.
    
    Automatically handles:
    - Browser-based SSO login via Playwright
    - Secure cookie storage with encryption
    - Cookie refresh when expired
    - Session validation
    """

    def __init__(self, cfg: AirflowAuthConfig):
        self.cfg = cfg
        self.store = EncryptedCookieStore(cfg.state_dir)

        if cfg.verify is False:
            print(
                "WARNING: TLS verification is disabled (AIRFLOW_VERIFY=false). "
                "This enables man-in-the-middle attacks.",
                file=sys.stderr,
            )

    def _session_from_cookies(self, cookies: List[dict]) -> requests.Session:
        s = requests.Session()
        s.headers.update({"User-Agent": "airflow-mcp/1.0"})
        s.verify = self.cfg.verify

        host = (urlparse(self.cfg.base_url).hostname or "").lower()

        for c in cookies:
            name = c.get("name")
            value = c.get("value")
            if not name:
                continue

            path = c.get("path") or "/"
            domain = (c.get("domain") or "").lower()
            domain_stripped = domain.lstrip(".")

            if domain_stripped == host:
                s.cookies.set(name=name, value=value, path=path)
            else:
                s.cookies.set(name=name, value=value, domain=domain, path=path)

        return s

    def _validate_session(self, s: requests.Session) -> bool:
        probe = f"{self.cfg.base_url}/api/v1/dags?limit=1"
        try:
            r = s.get(probe, timeout=(5, 20), allow_redirects=False)
            return r.status_code == 200
        except requests.RequestException:
            return False

    def _interactive_login_and_capture(self) -> List[dict]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ImportError(
                "Playwright is required for SSO authentication. "
                "Install it with: pip install playwright && playwright install chromium"
            )

        last_exc: Optional[Exception] = None
        last_status: Optional[int] = None

        with sync_playwright() as p:
            browser = None
            try:
                browser = p.chromium.launch(headless=self.cfg.headless)

                ignore_tls = (self.cfg.verify is False) or isinstance(self.cfg.verify, str)
                ctx = browser.new_context(ignore_https_errors=ignore_tls)

                page = ctx.new_page()
                page.goto(self.cfg.base_url, wait_until="domcontentloaded")

                deadline = time.time() + 300  # 5 minutes
                probe = f"{self.cfg.base_url}/api/v1/dags?limit=1"
                wait_time = 1000

                while time.time() < deadline:
                    try:
                        resp = page.request.get(probe, timeout=20_000)
                        last_status = resp.status
                        print(f"[SSO] API probe status: {last_status}", file=sys.stderr)
                        if last_status == 200:
                            break
                    except Exception as e:
                        last_exc = e
                        print(f"[SSO] API probe error: {e}", file=sys.stderr)

                    page.wait_for_timeout(wait_time)
                    wait_time = min(wait_time * 2, 5000)

                cookies = ctx.cookies(self.cfg.base_url)
                print(f"[SSO] Captured {len(cookies)} cookies", file=sys.stderr)

            finally:
                if browser:
                    browser.close()

        if last_status != 200:
            exc_msg = f" (last exception: {last_exc})" if last_exc else ""
            raise RuntimeError(
                f"Login did not yield an authorized browser session for API "
                f"(last API status: {last_status}){exc_msg}."
            )

        if not any(c.get("name") == "session" for c in cookies):
            print(
                "Warning: No 'session' cookie captured. Auth may use a different cookie name.",
                file=sys.stderr,
            )

        return cookies

    def _is_cookie_expired(self, payload: Dict[str, Any]) -> bool:
        captured_at = payload.get("captured_at", 0)
        max_age_seconds = self.cfg.max_cookie_age_hours * 3600
        return (time.time() - captured_at) > max_age_seconds

    def ensure_session(self) -> requests.Session:
        """Get a valid session, using cached cookies or triggering interactive login."""
        payload = self.store.load()
        if payload and "cookies" in payload:
            if self._is_cookie_expired(payload):
                print(
                    f"Cookies older than {self.cfg.max_cookie_age_hours}h, refreshing...",
                    file=sys.stderr,
                )
            else:
                s = self._session_from_cookies(payload["cookies"])
                if self._validate_session(s):
                    return s

        cookies = self._interactive_login_and_capture()
        self.store.save({"cookies": cookies, "captured_at": int(time.time())})

        s = self._session_from_cookies(cookies)
        if not self._validate_session(s):
            raise RuntimeError("Captured cookies still not authorized (API returned non-200).")
        return s

    def get_cookie_header(self) -> str:
        """Get the cookie header value for use with the Airflow SDK."""
        session = self.ensure_session()
        cookies = []
        for cookie in session.cookies:
            cookies.append(f"{cookie.name}={cookie.value}")
        return "; ".join(cookies)

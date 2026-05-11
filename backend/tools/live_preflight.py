#!/usr/bin/env python3
"""Production preflight for AD MediaSolution Studio live human tests."""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional
from urllib import error, request


DEFAULT_BASE_URL = "https://scriptdna-preview.vercel.app"
INSTAGRAM_TEST_URL = "https://www.instagram.com/reel/DYA3um5EVLh/"


@dataclass
class HttpResult:
    status: int
    text: str
    content_type: str


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str
    status: Optional[int] = None


def normalize_base_url(value: str) -> str:
    return value.rstrip("/")


def fetch(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: Optional[dict[str, Any]] = None,
    timeout: int = 30,
) -> HttpResult:
    data = None
    headers = {"User-Agent": "ADMediaSolution-LivePreflight/1.0"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = request.Request(
        f"{base_url}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return HttpResult(
                status=response.status,
                text=response.read().decode("utf-8", "replace"),
                content_type=response.headers.get("content-type", ""),
            )
    except error.HTTPError as exc:
        return HttpResult(
            status=exc.code,
            text=exc.read().decode("utf-8", "replace"),
            content_type=exc.headers.get("content-type", ""),
        )


def parse_json(result: HttpResult) -> Any:
    return json.loads(result.text)


def check_status(
    base_url: str,
    name: str,
    path: str,
    validator: Optional[Callable[[HttpResult], str]] = None,
) -> CheckResult:
    try:
        result = fetch(base_url, path)
        if result.status != 200:
            return CheckResult(name, False, f"expected 200, got {result.status}", result.status)
        detail = validator(result) if validator else "200 OK"
        return CheckResult(name, True, detail, result.status)
    except Exception as exc:
        return CheckResult(name, False, str(exc))


def validate_app(result: HttpResult) -> str:
    if "AD MediaSolution Studio" not in result.text:
        raise ValueError("HTML loaded but product title not found")
    return "UI HTML loaded"


def validate_config(result: HttpResult) -> str:
    data = parse_json(result)
    required = {
        "is_cloud": True,
        "is_vercel": True,
        "insforge_configured": True,
        "openrouter_api_key_configured": True,
    }
    for key, expected in required.items():
        if data.get(key) is not expected:
            raise ValueError(f"{key} expected {expected}, got {data.get(key)}")
    return "cloud, vercel, OpenRouter and InsForge configured"


def validate_ai_status(result: HttpResult) -> str:
    data = parse_json(result)
    openrouter = data.get("openrouter") or {}
    if openrouter.get("available") is not True:
        raise ValueError("openrouter.available is not true")
    return f"OpenRouter available with {openrouter.get('keys_available')}/{openrouter.get('keys_total')} keys"


def validate_diagnostic(result: HttpResult) -> str:
    data = parse_json(result)
    openrouter = data.get("openrouter") or {}
    vault = data.get("vault") or {}
    if data.get("status") != "ok":
        raise ValueError(f"status expected ok, got {data.get('status')}")
    # Relajamos gemini.live_test ya que ahora usamos OpenRouter
    if vault.get("writable") is not True:
        raise ValueError(f"vault.writable expected true, got {vault.get('writable')}")
    return "diagnostic ok, vault writable"


def validate_vault_brands(result: HttpResult) -> str:
    data = parse_json(result)
    brands = data.get("brands")
    if not isinstance(brands, list):
        raise ValueError("brands is not a list")
    return f"{len(brands)} brands visible"


def check_ai_test(base_url: str) -> CheckResult:
    payload = {
        "provider": "openrouter",
        "prompt": 'Responde solo JSON: {"ok": true, "scope": "live-preflight"}',
    }
    try:
        result = fetch(base_url, "/ai/test", method="POST", payload=payload, timeout=90)
        if result.status != 200:
            return CheckResult("/ai/test", False, result.text[:300], result.status)
        data = parse_json(result)
        if data.get("provider") != "openrouter":
            raise ValueError(f"provider expected openrouter, got {data.get('provider')}")
        if not data.get("response"):
            raise ValueError("empty OpenRouter response")
        return CheckResult("/ai/test", True, "OpenRouter generated a response", result.status)
    except Exception as exc:
        return CheckResult("/ai/test", False, str(exc))


def check_instagram_guardrail(base_url: str) -> CheckResult:
    payload = {
        "brand_name": "Live Preflight",
        "video_id": f"instagram-guardrail-{int(time.time())}",
        "url": INSTAGRAM_TEST_URL,
        "ai_provider": "openrouter",
    }
    try:
        result = fetch(base_url, "/jobs/process-url", method="POST", payload=payload)
        if result.status != 400:
            return CheckResult(
                "/jobs/process-url instagram guardrail",
                False,
                f"expected 400 guardrail, got {result.status}: {result.text[:300]}",
                result.status,
            )
        data = parse_json(result)
        detail = str(data.get("detail") or "")
        required = ("Instagram", "Arrastra video")
        missing = [item for item in required if item not in detail]
        if missing:
            raise ValueError(f"guardrail detail missing {missing}: {detail}")
        return CheckResult(
            "/jobs/process-url instagram guardrail",
            True,
            "Instagram URL rejected with upload guidance",
            result.status,
        )
    except Exception as exc:
        return CheckResult("/jobs/process-url instagram guardrail", False, str(exc))


def run_checks(base_url: str) -> list[CheckResult]:
    checks = [
        check_status(base_url, "/app", "/app", validate_app),
        check_status(base_url, "/static/app.css", "/static/app.css?v=2.7"),
        check_status(base_url, "/static/app.js", "/static/app.js?v=2.7"),
        check_status(base_url, "/config/status", "/config/status", validate_config),
        check_status(base_url, "/ai/status", "/ai/status", validate_ai_status),
        check_status(base_url, "/diagnostic", "/diagnostic", validate_diagnostic),
        check_status(base_url, "/vault/brands", "/vault/brands", validate_vault_brands),
        check_ai_test(base_url),
        check_instagram_guardrail(base_url),
    ]
    return checks


def print_report(base_url: str, results: list[CheckResult]) -> None:
    print(f"Live preflight: {base_url}")
    for result in results:
        label = "PASS" if result.ok else "FAIL"
        status = f" [{result.status}]" if result.status is not None else ""
        print(f"{label} {result.name}{status} - {result.detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run live production preflight checks.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Production base URL")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    base_url = normalize_base_url(args.base_url)
    results = run_checks(base_url)
    ok = all(result.ok for result in results)

    if args.json:
        print(json.dumps({
            "base_url": base_url,
            "ok": ok,
            "results": [result.__dict__ for result in results],
        }, indent=2, ensure_ascii=False))
    else:
        print_report(base_url, results)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

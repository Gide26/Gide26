#!/usr/bin/env python3
"""Northstar local server and Twelve Data adapter. API keys stay on the server."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API_BASE = "https://api.twelvedata.com"
PORT = int(os.environ.get("PORT", "4173"))
CACHE_SECONDS = max(60, int(os.environ.get("LIVE_SCAN_CACHE_SECONDS", "300")))
MAX_BATCH_SYMBOLS = max(1, min(120, int(os.environ.get("TWELVEDATA_BATCH_SIZE", "60"))))
CACHE: dict[str, object] = {"at": 0.0, "data": None}


def load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def read_universe() -> list[dict]:
    try:
        content = json.loads((ROOT / "universe.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not read universe.json: {exc}") from exc
    if not isinstance(content, list) or not content:
        raise RuntimeError("universe.json must contain a non-empty list of instruments.")
    result = []
    seen = set()
    for item in content:
        ticker = str(item.get("ticker", "")).strip().upper()
        provider_symbol = str(item.get("providerSymbol", ticker)).strip()
        if not ticker or not provider_symbol or ticker in seen:
            continue
        seen.add(ticker)
        result.append({
            "ticker": ticker,
            "name": str(item.get("name", ticker)),
            "asset": str(item.get("asset", "stock")).lower(),
            "providerSymbol": provider_symbol,
            "exchange": str(item.get("exchange", "")).strip(),
        })
    return result


def _api_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "Northstar-Market-Scanner/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            message = exc.read().decode("utf-8")[:350]
        except Exception:
            message = str(exc)
        if exc.code == 401 or exc.code == 403:
            raise RuntimeError("Twelve Data rejected the API key or this endpoint is not enabled on the current plan.") from exc
        if exc.code == 429:
            raise RuntimeError("Twelve Data rate limit reached. Check your plan quotas or reduce the scan frequency.") from exc
        raise RuntimeError(f"Twelve Data returned HTTP {exc.code}: {message}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("Could not reach Twelve Data. Check your internet connection and try again.") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("Twelve Data returned an unreadable response.") from exc
    if isinstance(data, dict) and str(data.get("status", "")).lower() == "error":
        message = str(data.get("message", "Provider error"))
        code = data.get("code")
        if code == 429 or "limit" in message.lower() or "credits" in message.lower():
            raise RuntimeError("Twelve Data rate limit or API-credit limit reached. Check your plan quota.")
        raise RuntimeError(f"Twelve Data: {message}")
    return data


def _batches(items: list[dict], size: int):
    for start in range(0, len(items), size):
        yield items[start:start + size]


def _series_for_symbol(response: dict, item: dict) -> dict | None:
    wanted = item["providerSymbol"].casefold()
    ticker = item["ticker"].casefold()
    if isinstance(response.get("values"), list):
        meta = response.get("meta", {})
        symbol = str(meta.get("symbol", "")).casefold()
        if not symbol or symbol == wanted or symbol == ticker:
            return response
    for key, value in response.items():
        if isinstance(value, dict) and isinstance(value.get("values"), list):
            key_norm = str(key).casefold()
            meta_symbol = str(value.get("meta", {}).get("symbol", "")).casefold()
            if key_norm in {wanted, ticker} or meta_symbol in {wanted, ticker}:
                return value
    return None


def ema(values: list[float], period: int) -> list[float]:
    if not values:
        return []
    alpha = 2 / (period + 1)
    result = [values[0]]
    for value in values[1:]:
        result.append(value * alpha + result[-1] * (1 - alpha))
    return result


def rsi(values: list[float], period: int = 14) -> float:
    if len(values) < 2:
        return 50.0
    deltas = [values[i] - values[i - 1] for i in range(1, len(values))][-period:]
    gains = sum(max(d, 0) for d in deltas) / len(deltas)
    losses = sum(max(-d, 0) for d in deltas) / len(deltas)
    if losses == 0:
        return 100.0 if gains else 50.0
    return 100 - 100 / (1 + gains / losses)


def analyze(item: dict, series: dict, live_series: dict | None = None) -> dict:
    meta = series.get("meta", {})
    raw_values = series.get("values", [])
    if not raw_values:
        raise RuntimeError("No historical bars were returned for this instrument.")
    bars = []
    for row in raw_values:
        try:
            bars.append({
                "date": str(row.get("datetime", "")),
                "close": float(row["close"]),
                "volume": float(row.get("volume") or 0),
            })
        except (KeyError, TypeError, ValueError):
            continue
    bars.sort(key=lambda bar: bar["date"])
    if len(bars) < 2:
        raise RuntimeError("At least two valid daily bars are required to calculate signals.")
    closes = [bar["close"] for bar in bars]
    latest = closes[-1]
    as_of = bars[-1]["date"]
    if live_series and live_series.get("values"):
        try:
            minute_bars = sorted(live_series["values"], key=lambda row: str(row.get("datetime", "")))
            latest = float(minute_bars[-1]["close"])
            as_of = str(minute_bars[-1].get("datetime", as_of))
        except (KeyError, TypeError, ValueError):
            pass
    previous = closes[-2]
    indicator_closes = closes[:-1] + [latest]
    sma20 = sum(closes[-20:]) / len(closes[-20:])
    sma50 = sum(closes[-50:]) / len(closes[-50:])
    fast, slow = ema(indicator_closes, min(12, len(indicator_closes))), ema(indicator_closes, min(26, len(indicator_closes)))
    macd_line = [f - s for f, s in zip(fast, slow)]
    macd_signal = ema(macd_line, min(9, len(macd_line)))
    macd_positive = bool(macd_line and macd_signal and macd_line[-1] >= macd_signal[-1])
    volumes = [bar["volume"] for bar in bars]
    recent_avg = sum(volumes[-21:-1]) / max(1, len(volumes[-21:-1]))
    volume_ratio = volumes[-1] / recent_avg if recent_avg > 0 else 1.0
    currency = (meta.get("currency_quote") or meta.get("currency") or "USD").upper()
    raw_volume = volumes[-1]
    # Normalize raw provider volume counts to millions for a compact table display.
    shown_volume = raw_volume / 1_000_000
    return {
        "ticker": item["ticker"],
        "name": item["name"],
        "asset": item["asset"],
        "providerSymbol": item["providerSymbol"],
        "currency": currency,
        "price": latest,
        "change": (latest / previous - 1) * 100 if previous else 0,
        "volume": shown_volume,
        "rsi": rsi(indicator_closes),
        "macd": macd_positive,
        "trend20": latest > sma20,
        "trend50": latest > sma50,
        "volumeRatio": volume_ratio,
        "asOf": as_of,
        "exchange": meta.get("exchange", item.get("exchange", "")),
    }


def scan_live() -> dict:
    load_env_file()
    api_key = os.environ.get("TWELVEDATA_API_KEY", "").strip()
    if not api_key or api_key.lower() in {"your_api_key_here", "replace_me"}:
        raise RuntimeError("Live feed not configured. Add your Twelve Data API key to the local .env file, then restart server.py.")
    universe = read_universe()
    scanned = []
    errors = []
    warnings = []
    for group in _batches(universe, MAX_BATCH_SYMBOLS):
        symbols = ",".join(item["providerSymbol"] for item in group)
        exchanges = {item["exchange"] for item in group if item.get("exchange")}
        common_exchange = next(iter(exchanges)) if len(exchanges) == 1 else ""
        def request_series(interval: str, outputsize: int) -> dict:
            params = {"symbol": symbols, "interval": interval, "outputsize": str(outputsize), "apikey": api_key}
            if common_exchange:
                params["exchange"] = common_exchange
            url = f"{API_BASE}/time_series?{urllib.parse.urlencode(params)}"
            return _api_json(url)
        try:
            daily_response = request_series("1day", 60)
        except RuntimeError as exc:
            errors.extend({"ticker": item["ticker"], "message": str(exc)} for item in group)
            continue
        try:
            minute_response = request_series("1min", 1)
        except RuntimeError as exc:
            minute_response = {}
            warnings.append(f"Intraday quotes unavailable for this batch; using the latest daily bar. {exc}")
        for item in group:
            series = _series_for_symbol(daily_response, item)
            if not series:
                errors.append({"ticker": item["ticker"], "message": "No daily series returned; check symbol formatting and provider market coverage."})
                continue
            live_series = _series_for_symbol(minute_response, item) if minute_response else None
            if minute_response and not live_series:
                warnings.append(f"{item['ticker']}: intraday quote unavailable; showing the latest daily bar.")
            try:
                scanned.append(analyze(item, series, live_series))
            except RuntimeError as exc:
                errors.append({"ticker": item["ticker"], "message": str(exc)})
    if not scanned:
        detail = errors[0]["message"] if errors else "No symbols returned."
        raise RuntimeError(f"Live scan returned no usable instruments. {detail}")
    return {
        "assets": scanned,
        "source": "Twelve Data",
        "universeSize": len(universe),
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "errors": errors[:20],
        "warnings": warnings[:5],
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "NorthstarLocal/1.0"

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/status":
            load_env_file()
            key = os.environ.get("TWELVEDATA_API_KEY", "").strip().lower()
            has_key = bool(key and key not in {"your_api_key_here", "replace_me"})
            try:
                universe_size = len(read_universe())
            except RuntimeError:
                universe_size = 0
            self._json(200, {"connected": has_key, "provider": "Twelve Data", "universeSize": universe_size, "cacheSeconds": CACHE_SECONDS})
            return
        if path == "/api/scan":
            now = time.monotonic()
            cached = CACHE.get("data")
            if cached and now - float(CACHE["at"]) < CACHE_SECONDS:
                self._json(200, {**cached, "cached": True})
                return
            try:
                result = scan_live()
            except RuntimeError as exc:
                self._json(503, {"error": str(exc), "provider": "Twelve Data"})
                return
            CACHE["at"] = now
            CACHE["data"] = result
            self._json(200, {**result, "cached": False})
            return
        self._serve_file(path)

    def _serve_file(self, url_path: str) -> None:
        relative = urllib.parse.unquote(url_path).lstrip("/") or "index.html"
        requested = (ROOT / relative).resolve()
        if not requested.is_relative_to(ROOT) or not requested.is_file():
            self.send_error(404, "Not found")
            return
        types = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8"}
        body = requested.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", types.get(requested.suffix, "application/octet-stream"))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        # Avoid accidentally printing query strings (which could contain credentials).
        print(f"{self.address_string()} - {fmt % args}")


def main() -> None:
    load_env_file()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Northstar local server at http://localhost:{PORT}")
    key = os.environ.get("TWELVEDATA_API_KEY", "").strip().lower()
    print("Live provider key: configured" if key and key not in {"your_api_key_here", "replace_me"} else "Live provider key: not configured (demo mode remains available)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Northstar.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

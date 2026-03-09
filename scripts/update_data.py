import json
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
ROUTES_PATH = ROOT / "docs" / "data" / "routes.json"
LATEST_PATH = ROOT / "docs" / "data" / "latest.json"
API_URL = "https://tdas-api.hkemobility.gov.hk/tdas/api/route"
TIMEOUT = 20

def load_json(path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default

def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def parse_speed(value):
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None

def is_worse(new_speed, old_speed):
    # worst congestion = lower speed
    if new_speed is None:
        return False
    if old_speed is None:
        return True
    return new_speed < old_speed

def fetch_route(route):
    payload = {
        "start": route["start"],
        "end": route["end"],
        "departIn": 0,
        "lang": "en",
        "type": "ST",
    }
    r = requests.post(API_URL, json=payload, timeout=TIMEOUT)
    status = str(r.status_code)
    if r.status_code != 200:
        return {
            "ok": False,
            "last_api_status": status,
            "response_text": r.text[:500]
        }
    data = r.json()
    return {
        "ok": True,
        "last_api_status": status,
        "speed": data.get("jSpeed"),
        "distance": data.get("distU") or (str(data.get("distM")) + " m" if data.get("distM") is not None else None),
        "distance_m": data.get("distM"),
        "eta": data.get("eta"),
        "extract_time": datetime.now(timezone.utc).isoformat(),
    }

def main():
    routes = load_json(ROUTES_PATH, [])
    latest = load_json(LATEST_PATH, {"updated_at": None, "records": []})
    current = {(r["route_id"], r["direction_key"]): r for r in latest.get("records", [])}
    for route in routes:
        key = (route["route_id"], route["direction_key"])
        result = fetch_route(route)
        existing = current.get(key)
        base = {
            "route_id": route["route_id"],
            "line_index": route["line_index"],
            "english_name": route.get("english_name"),
            "chinese_name": route.get("chinese_name"),
            "display_name": route.get("display_name"),
            "direction": route["direction"],
            "direction_key": route["direction_key"],
            "lane": route.get("lane"),
            "capacity": route.get("capacity"),
            "start": route["start"],
            "end": route["end"],
            "last_api_status": result.get("last_api_status"),
        }
        if not result["ok"]:
            if existing:
                existing["last_api_status"] = result.get("last_api_status")
            else:
                current[key] = base
            continue
        new_speed = parse_speed(result.get("speed"))
        old_speed = parse_speed(existing.get("speed")) if existing else None
        if (existing is None) or is_worse(new_speed, old_speed):
            current[key] = {
                **base,
                "speed": result.get("speed"),
                "distance": result.get("distance"),
                "distance_m": result.get("distance_m"),
                "eta": result.get("eta"),
                "extract_time": result.get("extract_time"),
            }
        else:
            existing["last_api_status"] = result.get("last_api_status")
    records = list(current.values())
    records.sort(key=lambda r: (parse_speed(r.get("speed")) is None, parse_speed(r.get("speed")) if parse_speed(r.get("speed")) is not None else 999999, r.get("english_name") or "", r.get("direction") or ""))
    latest = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "records": records
    }
    save_json(LATEST_PATH, latest)
    print(f"updated {len(records)} records")

if __name__ == "__main__":
    main()

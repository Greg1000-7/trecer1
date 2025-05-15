from flask import Flask, request, redirect
from datetime import datetime
from device_detector import DeviceDetector
import requests
import json
import os

app = Flask(__name__)

IPINFO_TOKEN = "9bc48d8ba04675"
LOG_FILE = "flask_geo_redirect.jsonl"

def geolocate(ip):
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json?token={IPINFO_TOKEN}", timeout=2)
        if r.status_code == 200:
            data = r.json()
            return {
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country"),
                "loc": data.get("loc"),
                "org": data.get("org")
            }
    except Exception as e:
        print(f"[geo error] {e}")
    return {}

@app.route("/")
def index():
    return "🟢 Flask redirector is running!"

@app.route("/r")
def redirector():
    xff = request.headers.get("X-Forwarded-For", "")
    ip = xff.split(",")[0].strip() if xff else request.remote_addr

    user_agent_str = request.headers.get("User-Agent", "")
    device = DeviceDetector(user_agent_str).parse()

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ip": ip,
        "geo": geolocate(ip),
        "user_agent": user_agent_str,
        "device": {
            "family": device.device().family if device.device() else "unknown",
            "brand": device.device().brand if device.device() else "unknown",
            "model": device.device().model if device.device() else "unknown"
        },
        "os": f"{device.os_name() or 'unknown'} {device.os_version() or ''}".strip(),
        "browser": f"{device.client_name() or 'unknown'} {device.client_version() or ''}".strip()
    }

    log_line = json.dumps(log_entry, ensure_ascii=False)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

    print("[LOG ENTRY]", log_line)

    return redirect("https://send.monobank.ua/jar/2JbpBYkhMv")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

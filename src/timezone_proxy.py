from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import pytz
from datetime import datetime
import time

print("🚀 timezone_proxy.py loaded!")  # Debug log

app = FastAPI()

# Root route for debug
@app.get("/")
def root():
    return {"status": "timezone proxy running"}

@app.get("/timezone")
async def get_timezone(timezone: str = None):
    return handle_timezone_request(timezone)

@app.post("/timezone")
async def post_timezone(request: Request):
    try:
        body = await request.json()
        timezone = body.get("timezone")
    except Exception:
        timezone = None
    return handle_timezone_request(timezone)

def handle_timezone_request(tz_name):
    if not tz_name:
        return {
            "status": "ERROR",
            "message": "Missing 'timezone' parameter.",
            "gmtOffset": None,
            "zoneEnd": None
        }

    try:
        tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        return {
            "status": "ERROR",
            "message": f"Unknown timezone '{tz_name}'.",
            "gmtOffset": None,
            "zoneEnd": None
        }

    now = datetime.utcnow()
    now_with_tz = tz.localize(now, is_dst=None)
    gmt_offset = int(now_with_tz.utcoffset().total_seconds())

    try:
        transitions = tz._utc_transition_times
        next_transition = next((t for t in transitions if t > now.replace(tzinfo=None)), None)
        zone_end = int(time.mktime(next_transition.timetuple())) if next_transition else 2147483647
    except Exception:
        zone_end = 2147483647

    return {
        "status": "OK",
        "message": "",
        "gmtOffset": gmt_offset,
        "zoneEnd": zone_end
    }

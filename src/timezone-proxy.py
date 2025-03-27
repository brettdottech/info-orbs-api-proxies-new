from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import pytz
from datetime import datetime
import time

app = FastAPI()

@app.api_route("/timezone", methods=["GET", "POST"])
async def timezone_info(request: Request):
    # Support both query param (GET) and JSON body (POST)
    if request.method == "GET":
        tz_name = request.query_params.get("timezone")
    else:
        try:
            body = await request.json()
            tz_name = body.get("timezone")
        except Exception:
            tz_name = None

    if not tz_name:
        return JSONResponse(status_code=400, content={
            "status": "ERROR",
            "message": "Missing 'timezone' parameter.",
            "gmtOffset": None,
            "zoneEnd": None
        })

    try:
        tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        return JSONResponse(status_code=400, content={
            "status": "ERROR",
            "message": f"Unknown timezone '{tz_name}'.",
            "gmtOffset": None,
            "zoneEnd": None
        })

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

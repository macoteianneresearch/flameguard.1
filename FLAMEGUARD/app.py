from __future__ import annotations
from datetime import datetime, timezone
from itertools import count
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder=".", static_url_path="")
run_counter = count(1)

FUEL_FACTORS = {
    "cellulose": 1.05, "pmma": 1.12, "polymer": 1.10,
    "fabric": 1.08, "foam": 1.20, "composite": 1.04,
    "reference": 0.25,
}

def calculate(p: dict) -> dict:
    """Deterministic, input-driven educational estimate. Not a validated fire-safety model."""
    temp = float(p.get("temperature_c", 650))
    oxygen = float(p.get("oxygen_pct", 21))
    diameter = max(1.0, float(p.get("diameter_mm", 12)))
    pressure = float(p.get("pressure_kpa", 101))
    gravity = float(p.get("gravity_g", 0))
    fuel = str(p.get("fuel", "cellulose"))
    duration = max(1.0, float(p.get("duration_s", 60)))
    mf = FUEL_FACTORS.get(fuel, 1.0)
    of = oxygen / 21.0
    tf = temp / 650.0
    gf = 1.08 if gravity == 0 else 0.92

    loi = max(8.0, min(100.0, 100.0 / max(0.01, of * mf)))
    margin = oxygen - 21.0
    spread = max(0.0, min(30.0, tf * of * gf * mf * (diameter / 12) ** 0.5 * 4))
    peak = max(0.0, min(1500.0, temp * (0.86 + 0.12 * of)))
    smoke = max(0.0, min(100.0, (tf * mf * 0.8 + of * 0.18) * 12))
    co = max(0.0, min(100.0, (tf * mf * 0.7 + (0.3 if oxygen < 18 else 0)) * 10))
    duration_factor = min(1.5, duration / 60.0)
    score = (tf * 0.25 + of * 0.30 + mf * 0.15 + gf * 0.10
             + (diameter / 12) ** 0.5 * 0.10 + (pressure / 101) * 0.10
             + max(0.0, duration_factor - 1.0) * 0.05)
    hazard = "LOW" if score < 1.25 else "MODERATE" if score < 1.65 else "HIGH"
    return {
        "loi_index": round(loi, 2),
        "oxygen_margin_pct_points": round(margin, 2),
        "flame_spread_index": round(spread, 3),
        "peak_temperature_c": round(peak, 2),
        "smoke_optical_density_index": round(smoke, 3),
        "co_index": round(co, 3),
        "hazard_level": hazard,
        "prediction_score": round(score, 3),
        "model": "input-driven-educational-estimate-v2",
        "model_note": "Deterministic estimate from supplied parameters; not experimentally validated.",
    }

@app.get("/")
def index():
    return send_from_directory(".", "index.html")

@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "FLAMEGUARD local API",
        "telemetry": "user-input-driven",
        "prediction": "deterministic educational estimate",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

@app.post("/api/live-telemetry")
def live_telemetry():
    p = request.get_json(silent=True) or {}
    result = calculate(p)
    return jsonify({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **p,
        "smoke_optical_density_index": result["smoke_optical_density_index"],
        "result": result,
        "source": "current-user-inputs",
    })

@app.post("/api/simulate")
def simulate():
    p = request.get_json(silent=True) or {}
    result = calculate(p)
    run_id = f"FG-{next(run_counter):04d}"
    return jsonify({
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "inputs": p,
        "result": result,
        "source": "python-input-driven-model",
    })

@app.post("/api/reset")
def reset():
    return jsonify({"status": "reset", "timestamp": datetime.now(timezone.utc).isoformat()})

@app.post("/api/sample")
def sample():
    p = request.get_json(silent=True) or {}
    return jsonify({"inputs": p, "result": calculate(p), "source": "current-user-inputs"})

if __name__ == "__main__":
    print("\\nFLAMEGUARD local API: http://127.0.0.1:8080")
    print("Predictions are deterministic and based on the values supplied in the dashboard.")
    print("No physical sensor is connected unless you configure a real sensor data source.\\n")
    app.run(host="127.0.0.1", port=8080, debug=False)

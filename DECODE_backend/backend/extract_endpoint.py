import numpy as np
import cv2
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from core.chart_extractor import extract_chart_data

app = FastAPI(title="DECODE Local Extraction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_to_frontend_payload(raw: dict, title=None) -> dict:
    categories = raw.get("categories", [])
    series_raw = raw.get("series", [])

    # Build ONE canonical list of {name, values} first -- everything else
    # (preview AND render) reads from this single list.
    canonical_series = []
    for s in series_raw:
        points = s.get("points", [])
        values = [p.get("value", 0.0) for p in points]
        
        canonical_series.append({
            "name": s.get("name") or "Series 1",
            "color": s.get("color"),  # may be None; frontend can default
            "values": values,
        })

    preview = {
        "series": [
            {
                "name": s["name"],
                "data": [
                    {"x": cat, "y": val}
                    for cat, val in zip(categories, s["values"])
                ],
            }
            for s in canonical_series
        ]
    }

    render = {
        "library_hint": "recharts",
        "categories": categories,
        "series": [
            {"name": s["name"], "color": s["color"], "values": s["values"]}
            for s in canonical_series
        ],
    }

    # Map confidence to high/medium/low based on the float value
    conf_val = raw.get("extraction_confidence", 0.0)
    if conf_val > 0.8:
        overall_conf = "high"
    elif conf_val > 0.5:
        overall_conf = "medium"
    else:
        overall_conf = "low"

    return {
        "chart_type": raw.get("resolved_chart_type", "bar"),
        "title": title,
        "preview": preview,
        "render": render,
        "confidence": {"overall": overall_conf},
    }


@app.post("/extract")
async def extract(file: UploadFile = File(...), use_gemini: bool = True):
    image_bytes = await file.read()
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(status_code=422, detail="Could not decode image -- unsupported format or corrupt file")

    try:
        if use_gemini:
            from services.llm_service import get_llm
            raw_result = get_llm().extract_with_decode_vision(image)
        else:
            raw_result = extract_chart_data(image)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Extraction failed: {e}")

    chart = normalize_to_frontend_payload(raw_result, title=file.filename)
    return {"success": True, "charts": [chart]}


import json

@app.post("/save_demo")
@app.post("/save_demo/{demo_id}")
async def save_demo(request: Request, demo_id: str = "1"):
    data = await request.json()
    import os
    frontend_public_dir = os.path.join(os.path.dirname(__file__), "..", "..", "decode-frontend", "public")
    os.makedirs(frontend_public_dir, exist_ok=True)
    filename = os.path.join(frontend_public_dir, f"perfect_demo_state_{demo_id}.json")
    with open(filename, "w") as f:
        json.dump(data, f)
    return {"success": True}

@app.get("/load_demo")
@app.get("/load_demo/{demo_id}")
async def load_demo(demo_id: str = "1"):
    import os
    frontend_public_dir = os.path.join(os.path.dirname(__file__), "..", "..", "decode-frontend", "public")
    filename = os.path.join(frontend_public_dir, f"perfect_demo_state_{demo_id}.json")
    if not os.path.exists(filename):
        raise HTTPException(status_code=404, detail="No demo state saved yet.")
    with open(filename, "r") as f:
        return json.load(f)

@app.get("/health")
async def health():
    return {"status": "ok"}

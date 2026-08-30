import os
import re

file_path = 'Decode_backend/backend/services/chart_pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the old normalize_extracted_chart if it exists
text = re.sub(r'def normalize_extracted_chart.*?return sorted\(charts, key=lambda c: \(c\.get\("page_number", 0\)\)\)', '', text, flags=re.DOTALL)

adapter_code = """
def normalize_extracted_chart(artifact: dict, index: int = 0) -> dict:
    '''
    Master canonical adapter that normalizes any backend extraction structure 
    into a strict frontend-compatible CanonicalChart schema.
    '''
    chart_id = artifact.get("id", f"chart-{index}")
    raw_type = str(artifact.get("chart_type", "bar")).lower()
    
    if raw_type in ["column", "vertical_bar", "stacked_bar"]:
        c_type = "bar"
    elif raw_type in ["doughnut"]:
        c_type = "donut"
    elif raw_type in ["spider"]:
        c_type = "radar"
    elif raw_type in ["bar", "line", "area", "pie", "donut", "radar"]:
        c_type = raw_type
    else:
        c_type = "bar"

    confidence = artifact.get("detection_confidence", 0.0)

    ext = artifact.get("extraction", {})
    if not ext:
        ext = artifact

    categories = []
    series = []
    title = ext.get("title", f"Extracted Chart {index + 1}")

    def parse_series(raw_s: list) -> list:
        s_out = []
        for s in raw_s:
            if not isinstance(s, dict): continue
            name = str(s.get("name", "Unknown"))
            # Format A: values array
            if "values" in s and isinstance(s["values"], list):
                s_out.append({
                    "name": name,
                    "values": [float(v) if v is not None else 0.0 for v in s["values"]]
                })
            # Format B: points array (CanonicalDataset)
            elif "points" in s and isinstance(s["points"], list):
                vals = []
                for p in s["points"]:
                    if isinstance(p, dict) and "value" in p:
                        v = p["value"]
                        vals.append(float(v) if v is not None else 0.0)
                    else:
                        vals.append(0.0)
                s_out.append({"name": name, "values": vals})
        return s_out

    found_data = False
    for key in ["canonical_data", "canonical_dataset", "data"]:
        nested = ext.get(key)
        if isinstance(nested, dict):
            c = nested.get("categories")
            s = nested.get("series")
            if isinstance(c, list) and isinstance(s, list) and len(c) > 0 and len(s) > 0:
                categories = [str(x) for x in c]
                series = parse_series(s)
                found_data = True
                
                meta = nested.get("metadata", {})
                if isinstance(meta, dict) and "confidence" in meta:
                    confidence = float(meta["confidence"])
                elif "confidence" in nested:
                    confidence = float(nested["confidence"])
                elif "overall_confidence" in nested:
                    confidence = float(nested["overall_confidence"])
                    
                if "title" in nested and nested["title"]:
                    title = nested["title"]
                break

    if not found_data:
        c = ext.get("categories")
        s = ext.get("series")
        if isinstance(c, list) and isinstance(s, list) and len(c) > 0 and len(s) > 0:
            categories = [str(x) for x in c]
            series = parse_series(s)
            found_data = True

    if not found_data:
        for key in ["rows", "table", "dataset", "data_points", "values"]:
            rows = ext.get(key)
            if isinstance(rows, list) and len(rows) > 0 and isinstance(rows[0], dict):
                cat_keys = ["Category", "category", "Label", "label", "Name", "name", "X", "x"]
                actual_cat_key = None
                for r_key in rows[0].keys():
                    if r_key in cat_keys:
                        actual_cat_key = r_key
                        break
                if not actual_cat_key:
                    actual_cat_key = list(rows[0].keys())[0]

                series_keys = [k for k in rows[0].keys() if k != actual_cat_key]
                categories = [str(r.get(actual_cat_key, "")) for r in rows]
                
                for sk in series_keys:
                    s_vals = []
                    for r in rows:
                        try:
                            s_vals.append(float(r.get(sk, 0)))
                        except (ValueError, TypeError):
                            s_vals.append(0.0)
                    series.append({"name": sk, "values": s_vals})
                
                if len(categories) > 0 and len(series) > 0:
                    found_data = True
                    break

    if confidence > 1.0:
        confidence = confidence / 100.0

    return {
        "id": chart_id,
        "chart_type": c_type,
        "canonical_data": {
            "title": title,
            "detected_type": c_type,
            "categories": categories,
            "series": series,
            "metadata": {
                "confidence": confidence
            }
        }
    }

def list_charts_for_document(doc_id: str) -> list[dict]:
    \"\"\"List all charts detected in a document, including their full canonical data.\"\"\"
    db = get_db()
    charts = []
    for snap in db.collection(COL_CHARTS).where("document_id", "==", doc_id).stream():
        d = {k: v for k, v in snap.to_dict().items() if not k.startswith("_")}
        d["id"] = snap.id
        
        ext_snaps = list(db.collection(COL_EXTRACTIONS).where("chart_id", "==", snap.id).stream())
        if ext_snaps:
            d["extraction"] = ext_snaps[-1].to_dict()
            
        normalized = normalize_extracted_chart(d, index=len(charts))
        d["canonical_data"] = normalized["canonical_data"]
        
        if "extraction" in d:
            del d["extraction"]
            
        charts.append(d)
        
    return sorted(charts, key=lambda c: (c.get("page_number", 0)))
"""

text = re.sub(
    r'(def get_processing_events\(doc_id: str\) -> list\[dict\]:)',
    adapter_code + '\n\n' + r'\1',
    text,
    count=1
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated backend chart_pipeline.py with points extraction support")

import fitz
import re

def clean_table_matrix(raw_table):
    if not raw_table or len(raw_table) < 2:
        return None
        
    # Drop completely empty rows
    valid_rows = []
    for r in raw_table:
        if any(c is not None and str(c).strip() for c in r):
            valid_rows.append(r)
            
    if len(valid_rows) < 2:
        return None
        
    # Find which columns have numeric data in the rows
    num_cols = len(valid_rows[0])
    valid_cols = []
    for c_idx in range(num_cols):
        has_num = False
        for r_idx in range(1, len(valid_rows)):
            val = valid_rows[r_idx][c_idx] if c_idx < len(valid_rows[r_idx]) else None
            if val is not None and re.search(r'\d+', str(val)):
                has_num = True
                break
        if has_num or c_idx == 0:
            valid_cols.append(c_idx)
            
    if len(valid_cols) < 2:
        return None
        
    # First valid col is category/epoch, remaining are series
    cat_col = valid_cols[0]
    series_cols = valid_cols[1:]
    
    header_row = valid_rows[0]
    # If header_row doesn't have words, check valid_rows[1]
    headers = []
    for sc in series_cols:
        h_cand = str(header_row[sc] or "")
        if "\n" in h_cand:
            h_lines = [l.strip() for l in h_cand.split("\n") if l.strip()]
            h_cand = h_lines[-1] if h_lines else f"Series {len(headers)+1}"
        if not h_cand or h_cand.lower() == "none":
            h_cand = f"Series {len(headers)+1}"
        headers.append(h_cand)
        
    # Refine known headers
    clean_headers = []
    for h in headers:
        if "train" in h.lower():
            clean_headers.append("Training Loss")
        elif "val" in h.lower():
            clean_headers.append("Validation Loss")
        else:
            clean_headers.append(h)
            
    categories = []
    series_data = {h: [] for h in clean_headers}
    
    data_rows = valid_rows[1:] if any(c in str(valid_rows[0]) for c in ["Loss", "Epoch", "Acc", "Val", "Train"]) else valid_rows
    
    for r in data_rows:
        cat_text = str(r[cat_col] or "").strip()
        if not cat_text or not re.search(r'\d+', cat_text):
            continue
        # Extract clean digit if "V\nEpoch 1" or similar
        cat_match = re.search(r'\b\d+\b', cat_text)
        cat_name = cat_match.group(0) if cat_match else cat_text
        categories.append(cat_name)
        
        for idx, sc in enumerate(series_cols):
            cell_val = r[sc] if sc < len(r) else None
            num_match = re.search(r'[-+]?\d*\.?\d+', str(cell_val or ""))
            val = float(num_match.group(0)) if num_match else 0.0
            series_data[clean_headers[idx]].append(val)
            
    return categories, series_data

doc = fitz.open('static/uploads/0c5a9677_DECODE_Test_Scientific_Charts.pdf')
p = doc[1]
tabs = p.find_tables()
for t in tabs:
    raw = t.extract()
    cats, series_map = clean_table_matrix(raw)
    print("Categories:", cats)
    for k, v in series_map.items():
        print(f"Series '{k}':", v)

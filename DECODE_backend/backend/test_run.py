from services.chart_pipeline import run_chart_pipeline
import json

res = run_chart_pipeline('test-verify-round1', 'static/uploads/0c5a9677_DECODE_Test_Scientific_Charts.pdf')
print('Status:', res.get('status'))
print('Charts found:', len(res.get('charts', [])))
for i, c in enumerate(res.get('charts', [])):
    print(f'Chart {i}: id={c.get("id")} type={c.get("chart_type")} page={c.get("page_number")}')
for i, e in enumerate(res.get('extractions', [])):
    print(f'Ext {i}: title="{e.get("title")}" series_count={len(e.get("series", []))} categories={e.get("categories", [])}')
    for s in e.get("series", []):
        print(f'   Series "{s.get("name")}": points={[p.get("value") for p in s.get("points", [])]}')

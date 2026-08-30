import re

with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix page:
text = re.sub(r'page:[\s\S]*?\?\? null,\n', '', text)
text = re.sub(r'page:[\s\S]*?\?\? 1,\n', '', text)

# Fix setChartMode
text = re.sub(r'setChartMode\(\n\s*chart\.chart_type\n\s*\);', 'setChartMode(chart.chart_type as any);', text)
text = re.sub(r'setChartMode\(\n\s*first\.chart_type\n\s*\);', 'setChartMode(first.chart_type as any);', text)

# Fix canonical
text = text.replace('const extractedType = canonical?.detected_type ?? firstChart?.extraction?.resolved_chart_type ?? firstChart?.chart_type ?? "bar";', 'const extractedType = firstChart?.chart_type ?? "bar";')

# Fix primary.id
text = text.replace('row.values[\n                  primary.id\n                ]', 'row.values[primary.name]')

with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed remaining TS errors.')

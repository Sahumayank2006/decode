import re

with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

missing_imports = '''import { uploadDocument, getDocumentStatus, getDocumentCharts } from "@/lib/api";
function getChartSummary(charts: any[]) {
    return { total_charts: charts.length, total_data_points: 0, overall_confidence: 0 };
}
'''

if 'uploadDocument' not in text[:2000]:
    text = text.replace('import { type NormalizedChart } from "@/lib/canonicalNormalizer";', 'import { type NormalizedChart } from "@/lib/canonicalNormalizer";\n' + missing_imports)

text = text.replace('getChart(normalizedCharts)', 'setBackendCharts(normalizedCharts)')
text = text.replace('canonical.', 'chart.')

with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed missing variables in DemoWorkspace.tsx')

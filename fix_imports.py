import re

with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Update import
match = re.search(r'import \{[\s\S]*?\} from "@/lib/extractionAdapter";', text)
if match:
    text = text.replace(match.group(0), 'import { type NormalizedChart } from "@/lib/canonicalNormalizer";')

# Update CanonicalChart to NormalizedChart
text = text.replace('CanonicalChart', 'NormalizedChart')

with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated DemoWorkspace.tsx imports and types.")

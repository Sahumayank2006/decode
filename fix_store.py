import re

with open('decode-frontend/src/store/useChartStore.ts', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace extractionAdapter with canonicalNormalizer
text = re.sub(r'import \{.*?CanonicalChart.*?\} from "@/lib/extractionAdapter";', 'import { type NormalizedChart as CanonicalChart } from "@/lib/canonicalNormalizer";', text)

# Just map CanonicalChart to NormalizedChart by renaming the type
text = text.replace('import { type CanonicalChart } from "@/lib/extractionAdapter";', 'import { type NormalizedChart as CanonicalChart } from "@/lib/canonicalNormalizer";')
text = text.replace('import { CanonicalChart } from "@/lib/extractionAdapter";', 'import { type NormalizedChart as CanonicalChart } from "@/lib/canonicalNormalizer";')

with open('decode-frontend/src/store/useChartStore.ts', 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated useChartStore.ts')

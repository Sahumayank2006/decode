import json
import re

path = r'C:\Users\licsa\.gemini\antigravity-ide\brain\7293c467-f712-49b1-9e97-1b2c8881b1e2\.system_generated\logs\transcript_full.jsonl'
with open(path, 'r', encoding='utf-8') as f:
    for line in f:
        if 'export default function DemoWorkspace' in line:
            try:
                data = json.loads(line)
                if data.get('type') == 'USER_INPUT':
                    content = data.get('content', '')
                    matches = re.finditer(r'```(?:tsx|typescript)?\s*([\s\S]*?)```', content)
                    for match in matches:
                        code = match.group(1)
                        if 'export default function DemoWorkspace' in code:
                            with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'w', encoding='utf-8') as out:
                                out.write(code.strip())
                            print('Recovered DemoWorkspace from user prompt!')
                            exit(0)
            except Exception as e:
                pass

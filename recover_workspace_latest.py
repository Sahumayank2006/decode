import json
import re

path = r'C:\Users\licsa\.gemini\antigravity-ide\brain\7293c467-f712-49b1-9e97-1b2c8881b1e2\.system_generated\logs\transcript_full.jsonl'
best_code = None

with open(path, 'r', encoding='utf-8') as f:
    for line in f:
        if 'export default function DemoWorkspace' in line:
            try:
                data = json.loads(line)
                # It could be from USER_INPUT or PLANNER_RESPONSE (if I wrote it)
                # Wait, if I wrote it using `write_to_file`, it would be in a tool call!
                # Let's check both tool calls and user inputs.
                if data.get('type') == 'USER_INPUT':
                    content = data.get('content', '')
                    matches = re.finditer(r'```(?:tsx|typescript)?\s*([\s\S]*?)```', content)
                    for match in matches:
                        code = match.group(1)
                        if 'export default function DemoWorkspace' in code:
                            best_code = code.strip()
                elif 'tool_calls' in data:
                    for tc in data.get('tool_calls', []):
                        if tc.get('function', {}).get('name') == 'write_to_file':
                            args_str = tc.get('function', {}).get('arguments', '')
                            if 'DemoWorkspace.tsx' in args_str:
                                args = json.loads(args_str)
                                if 'CodeContent' in args and 'export default function DemoWorkspace' in args['CodeContent']:
                                    best_code = args['CodeContent'].strip()
            except Exception as e:
                pass

if best_code:
    with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'w', encoding='utf-8') as out:
        out.write(best_code)
    print('Recovered the LATEST DemoWorkspace.tsx!')
else:
    print('Failed to find any DemoWorkspace.tsx!')

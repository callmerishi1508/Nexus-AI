import json
import sys

with open(r'C:\Users\admin\.gemini\antigravity-ide\brain\fa730d07-7394-46db-a474-f1c54a041eb6\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            tool_calls = data.get('tool_calls', [])
            for call in tool_calls:
                args = call.get('arguments', {})
                if 'page.tsx' in str(args):
                    print("TOOL:", call['name'], args)
        except Exception as e:
            pass

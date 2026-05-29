import json
import sys
import re

found = False
with open(r'C:\Users\admin\.gemini\antigravity-ide\brain\fa730d07-7394-46db-a474-f1c54a041eb6\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            tool_calls = data.get('tool_calls', [])
            if not tool_calls:
                continue
            for call in tool_calls:
                args_str = json.dumps(call)
                if 'COMMAND CENTER TAB' in args_str and 'SCENARIO SANDBOX TAB' in args_str:
                    found = True
                    with open('recovered.txt', 'w', encoding='utf-8') as out:
                        out.write(args_str)
        except Exception as e:
            pass

print("Found:", found)

import json
import sys

with open(r'C:\Users\admin\.gemini\antigravity-ide\brain\fa730d07-7394-46db-a474-f1c54a041eb6\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    idx = 0
    for line in f:
        try:
            data = json.loads(line)
            content = data.get('content', '')
            if 'SCENARIO SANDBOX' in content and 'app/page.tsx' in content:
                with open(f'dump_{idx}.txt', 'w', encoding='utf-8') as out:
                    out.write(content)
                idx += 1
        except Exception as e:
            pass

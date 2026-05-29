import json
import sys

full_contents = []
with open(r'C:\Users\admin\.gemini\antigravity-ide\brain\fa730d07-7394-46db-a474-f1c54a041eb6\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get('content', '')
            if 'export default function Page()' in content and 'SCENARIO SANDBOX TAB' in content:
                full_contents.append(content)
        except Exception as e:
            pass

if full_contents:
    print(f"Found {len(full_contents)} full file contents!")
    with open('best_backup.txt', 'w', encoding='utf-8') as out:
        out.write(full_contents[-1])
else:
    print("No full file found.")

import json
import sys

with open(r'C:\Users\admin\.gemini\antigravity-ide\brain\fa730d07-7394-46db-a474-f1c54a041eb6\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get('content', '')
            if 'SCENARIO SANDBOX TAB' in content and 'flex-1 flex flex-col min-h-0' in content:
                with open('recovered_chunk.txt', 'a', encoding='utf-8') as out:
                    out.write(content + '\n\n--------------------------\n\n')
        except Exception as e:
            pass

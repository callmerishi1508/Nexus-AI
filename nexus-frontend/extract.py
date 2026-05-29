import json
import sys

with open(r'C:\Users\admin\.gemini\antigravity-ide\brain\fa730d07-7394-46db-a474-f1c54a041eb6\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get('content', '')
            if 'activeTab === "topology"' in content and 'SCENARIO SANDBOX TAB' in content:
                print("FOUND A MATCH IN TRANSCRIPT!")
                print(content[:500])
                with open('recovered.txt', 'w', encoding='utf-8') as out:
                    out.write(content)
        except:
            pass

import json

with open(r'C:\Users\admin\.gemini\antigravity-ide\brain\fa730d07-7394-46db-a474-f1c54a041eb6\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get('content', '')
            if 'activeTab === "topology"' in content and 'Network' in content and 'grid-cols-12' in content:
                print("Found Topology in content!")
                with open('topo_chunk.txt', 'a', encoding='utf-8') as out:
                    out.write(content + '\n\n')
        except Exception:
            pass

import re

with open('recovered_chunk.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
for line in lines:
    if line.startswith('+'):
        output_lines.append(line[1:])

with open('missing_components.tsx', 'w', encoding='utf-8') as out:
    out.writelines(output_lines)

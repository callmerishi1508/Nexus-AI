with open(r"C:\Web Hackathon\nexus-frontend\app\page.tsx.bak", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "Live Topology" in line and "<Network" in line:
        # Keep it but we need to fix the broken block below it
        pass
    
    if "anomaly_segments_routed" in line and "<span" in line and lines[i-1].strip() == ">":
        # This is where it broke: 
        # <motion.div ...>
        # <span className="text-base... anomaly_segments_routed
        # We need to restore the full Topology
        continue

# Actually, it's easier to just write the whole page.tsx from scratch.
# I will write the file contents directly.

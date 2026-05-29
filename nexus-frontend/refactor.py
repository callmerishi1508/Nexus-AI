import re

with open('app/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. We will insert the isViewAllowed check at the top of the main workspace render.
# Right after:
#          {activeTab === "strategic_synthesis" ? (
# We will replace it with:
#          {(() => {
#             const allowedViews = ROLE_NAVIGATION_MAP[activeRole]?.modeViews[masterMode]?.map(v => v.id) || [];
#             const isViewAllowed = allowedViews.includes(activeTab);
#             if (!isViewAllowed) {
#                 return (
#                    <div className="flex-1 flex flex-col items-center justify-center font-mono text-sm text-zinc-500 uppercase tracking-widest gap-6 m-4 glass-panel border border-zinc-800/50">
#                       <Lock className="w-12 h-12 text-zinc-700 opacity-50 mb-2" />
#                       <div className="text-center">
#                         <p className="text-zinc-400 mb-2 text-base font-semibold">Workspace Unavailable</p>
#                         <p className="text-xs text-zinc-600">The requested intelligence vector is restricted or inactive for the <span className="text-indigo-500">{activeRole}</span> clearance level.</p>
#                       </div>
#                    </div>
#                 );
#             }
#             return (
#               <>
#                  {activeTab === "strategic_synthesis" && (

start_idx = content.find('{activeTab === "strategic_synthesis" ? (')
content = content[:start_idx] + '''{(() => {
            const allowedViews = ROLE_NAVIGATION_MAP[activeRole]?.modeViews[masterMode]?.map(v => v.id) || [];
            const isViewAllowed = allowedViews.includes(activeTab);
            if (!isViewAllowed) {
                return (
                   <div className="flex-1 flex flex-col items-center justify-center font-mono text-sm text-zinc-500 uppercase tracking-widest gap-6 m-4 glass-panel border border-zinc-800/50">
                      <Lock className="w-12 h-12 text-zinc-700 opacity-50 mb-2" />
                      <div className="text-center">
                        <p className="text-zinc-400 mb-2 text-base font-semibold">Workspace Unavailable</p>
                        <p className="text-xs text-zinc-600">The requested intelligence vector is restricted or inactive for the <span className="text-indigo-500">{activeRole}</span> clearance level.</p>
                      </div>
                   </div>
                );
            }
            return (
              <>
                 {activeTab === "strategic_synthesis" && (''' + content[start_idx + len('{activeTab === "strategic_synthesis" ? ('):]


# 2. Fix the end of strategic_synthesis block
end_idx = content.find(') : null}', start_idx)
content = content[:end_idx] + ')}' + content[end_idx + len(') : null}'):]

# 3. Change topology block from ternary to &&
topo_idx = content.find('{activeTab === "topology" ? (')
content = content[:topo_idx] + '{activeTab === "topology" && (' + content[topo_idx + len('{activeTab === "topology" ? ('):]

# 4. Change strategic_memory block from else-if to &&
mem_idx = content.find(') : activeTab === "strategic_memory" ? (')
content = content[:mem_idx] + ')}\n          {activeTab === "strategic_memory" && (' + content[mem_idx + len(') : activeTab === "strategic_memory" ? ('):]

# 5. Change scenario_sandbox block from else-if to &&
sim_idx = content.find(') : masterMode === "SIMULATION" ? (')
content = content[:sim_idx] + ')}\n          {activeTab === "scenario_sandbox" && (' + content[sim_idx + len(') : masterMode === "SIMULATION" ? ('):]

# 6. Change the final else block (the old fallback) to just close the fragment and IIFE
end_block_idx = content.find(') : (\n            <div className="flex-1 flex flex-col items-center justify-center font-mono text-sm text-zinc-500 uppercase tracking-widest gap-6 m-4 glass-panel border border-zinc-800/50">')

# Wait, this block is large, let's find the closing tag.
# We know it ends with )} at the end of the ) : ( block.
# Let's replace from ) : ( down to that )} with )}\n              </>\n            );\n          })()}
if end_block_idx != -1:
    close_idx = content.find(')}\n            </>\n         )}', end_block_idx)
    content = content[:end_block_idx] + ')}\n              </>\n            );\n          })()}' + content[close_idx:]

with open('app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("done")

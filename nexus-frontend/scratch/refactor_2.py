import sys
import re

with open('app/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Locate the Main Workspace <div> opening tag
div_open_idx = content.find('{/* Main Workspace */}')
div_tag_start = content.find('<div className={`flex-1 flex flex-col ${ROLE_LAYOUT_PRESETS[activeRole]?.density', div_open_idx)
div_tag_end = content.find('>', div_tag_start) + 1

# The content inside the Main Workspace div starts after `div_tag_end`.
# The end of the Main Workspace is right before `</div>\n      </div>\n\n      <AnimatePresence>`
end_str = '</div>\n      </div>\n\n      <AnimatePresence>'
end_idx = content.find(end_str)

inner_content = content[div_tag_end:end_idx]

# In inner_content, we want to REMOVE the `{activeRole === "EXECUTIVE" ? ( <ExecutiveView ... /> ) : ( <>` wrapper.
# And REMOVE the `</> )}` at the very end.

# 1. Find the start of the `<> ... {/* Top Control Bar */}`
top_bar_idx = inner_content.find('{/* Top Control Bar */}')
# 2. Find the view switcher `{( () => {`
switcher_idx = inner_content.find('{(() => {')
# 3. Find the end of the view switcher
switcher_end = inner_content.rfind('})()}') + 6 # length of `})()` + `}` + `}` ? Wait, `})()}`
# Let's find the closing of the fragment and condition `</>\n         )}`
fragment_close_idx = inner_content.rfind('</>\n         )}')

switcher_content = inner_content[switcher_idx:fragment_close_idx].strip()

new_inner_content = """
         {/* Executive Cinematic Header */}
         {ROLE_LAYOUT_PRESETS[activeRole]?.density === 'sparse' && (
            <div className="bg-[#0b0f14] border-b border-[#1a2230] p-10 relative shrink-0">
               <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/5 to-transparent pointer-events-none" />
               <h2 className="text-sm font-sans tracking-[0.25em] uppercase text-zinc-500 mb-4">Executive Briefing Room</h2>
               <h1 className="text-4xl leading-[1.2] max-w-4xl font-serif text-zinc-100 mb-6">Strategic Projections: <span className="text-indigo-400 font-light italic">{simTarget || 'Awaiting Target'}</span></h1>
            </div>
         )}
         
         {/* Top Control Bar */}
         <div className={`flex justify-between items-center bg-white/[0.01] border-b border-white/5 shadow-sm shrink-0 ${ROLE_LAYOUT_PRESETS[activeRole]?.density === 'sparse' ? 'px-16 py-4' : 'mb-8 p-4 rounded-xl border'}`}>
             <div className="flex gap-4">
                  {ROLE_NAVIGATION_MAP[activeRole].modeViews[masterMode]?.map(view => (
                      <button 
                          key={view.id}
                          onClick={() => setActiveTab(view.id)}
                          className={`px-4 py-2 rounded-md text-xs font-semibold tracking-wide transition-colors ${activeTab === view.id ? 'bg-white/10 text-white shadow-sm' : 'text-zinc-400 hover:text-white hover:bg-white/5'}`}
                      >
                          {view.label}
                      </button>
                  ))}
             </div>
             {ROLE_LAYOUT_PRESETS[activeRole]?.density !== 'sparse' && (
                 <div className="flex items-center gap-6">
                     <button
                        onClick={() => setIsFocusMode(!isFocusMode)}
                        className={`text-xs font-semibold uppercase tracking-widest transition-colors flex items-center gap-2 px-3 py-1.5 rounded-md ${isFocusMode ? 'bg-indigo-500/20 text-indigo-400' : 'text-zinc-500 hover:text-white hover:bg-white/5'}`}
                     >
                        <Search className="w-4 h-4" /> Focus
                     </button>
                     <select 
                       className="bg-white/5 border border-white/10 rounded-md px-3 py-1.5 text-sm font-medium text-zinc-300 outline-none hover:bg-white/10 transition-colors"
                       value={activeSector}
                       onChange={(e) => setActiveSector(e.target.value)}
                     >
                       {Object.keys(SECTOR_TARGETS).map(s => <option className="bg-zinc-900" key={s} value={s}>{s}</option>)}
                     </select>
                 </div>
             )}
         </div>

         {/* Workspace Content */}
         <div className={`flex-1 flex flex-col min-h-0 ${ROLE_LAYOUT_PRESETS[activeRole]?.density === 'sparse' ? 'px-24 py-16' : ''}`}>
           """ + switcher_content + """
         </div>
"""

new_content = content[:div_tag_end] + "\n" + new_inner_content + "\n" + content[end_idx:]

with open('app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Updated Main Workspace")

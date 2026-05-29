import sys

content = open('app/page.tsx', 'r', encoding='utf-8').read()

# 1. Update Sidebar Conditions
old_sidebar_cond = '{activeRole !== "EXECUTIVE" && ('
new_sidebar_cond = '{ROLE_LAYOUT_PRESETS[activeRole]?.sidebar && ('
content = content.replace(old_sidebar_cond, new_sidebar_cond)

# 2. Main Workspace
idx1 = content.find('{/* Main Workspace */}')
# Find the end of the <div className="flex-1 ..."> for the workspace.
# The structure is:
# {/* Main Workspace */}
# <div className={`flex-1 ...`}>
#    {activeRole === "EXECUTIVE" ? ( ... ) : ( ... )}
# </div>

start_div = content.find('<div className={`flex-1 flex flex-col ${activeRole === \'EXECUTIVE\' ? \'p-0\' : \'p-6\'} overflow-y-auto`}>', idx1)

if start_div != -1:
    new_div = '<div className={`flex-1 flex flex-col ${ROLE_LAYOUT_PRESETS[activeRole]?.density === \'sparse\' ? \'p-0\' : \'p-6\'} overflow-y-auto`}>'
    content = content[:start_div] + new_div + content[start_div+len('<div className={`flex-1 flex flex-col ${activeRole === \'EXECUTIVE\' ? \'p-0\' : \'p-6\'} overflow-y-auto`}>'):]

# Let's just output the current modifications to test.
with open('app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated page.tsx sidebar conditionals")

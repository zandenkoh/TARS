import re

file_path = "TARS/webui/templates/index.html"
with open(file_path, "r") as f:
    content = f.read()

# Fix 1: Add title attribute to "New Chat" button
content = re.sub(
    r'(<button aria-label="New Chat" onclick="newChat\(\); closeSidebarOnMobile\(\)")(\s*class="p-2)',
    r'\1 title="New Chat"\2',
    content
)

# Fix 2: Add title attribute to "Toggle Sidebar" button (header)
content = re.sub(
    r'(<button aria-label="Toggle Sidebar" onclick="toggleSidebar\(\)")(\s*class="md:hidden p-2 hover:bg-white/7 rounded-lg text-zinc-400 hover:text-white">)',
    r'\1 title="Toggle Sidebar"\2',
    content
)

# Fix 3: Add title attribute to "Toggle Sidebar" button (sidebar)
content = re.sub(
    r'(<button aria-label="Toggle Sidebar" onclick="toggleSidebar\(\)")(\s*class="md:hidden p-2 hover:bg-white/5 rounded-lg transition-all text-zinc-500 hover:text-white ml-2">)',
    r'\1 title="Toggle Sidebar"\2',
    content
)

# Fix 4: Add title attribute to "Notifications" button
content = re.sub(
    r'(<button aria-label="Notifications" class="p-2 text-zinc-500 hover:text-zinc-200 transition-colors">)',
    r'<button aria-label="Notifications" title="Notifications" class="p-2 text-zinc-500 hover:text-zinc-200 transition-colors">',
    content
)

# Fix 5: Add title attribute to "Close Search" button
content = re.sub(
    r'(<button aria-label="Close Search" onclick="closeSearchModal\(\)" class="absolute right-2 p-2 text-zinc-500 hover:text-white transition-colors">)',
    r'<button aria-label="Close Search" title="Close Search" onclick="closeSearchModal()" class="absolute right-2 p-2 text-zinc-500 hover:text-white transition-colors">',
    content
)

# Fix 6: Add title attribute to "Close Modal" button (sidebar)
content = re.sub(
    r'(<button aria-label="Close Modal" onclick="closeModal\(\)" class="p-2 -ml-2 text-zinc-400 hover:text-white transition-colors">)',
    r'<button aria-label="Close Modal" title="Close Modal" onclick="closeModal()" class="p-2 -ml-2 text-zinc-400 hover:text-white transition-colors">',
    content
)

# Fix 7: Add title attribute to "Close Modal" button (header)
content = re.sub(
    r'(<button id="modal-header-close" aria-label="Close Modal" onclick="closeModal\(\)" class="p-2 hover:bg-white/5 rounded-xl text-zinc-400 hover:text-white transition-colors">)',
    r'<button id="modal-header-close" aria-label="Close Modal" title="Close Modal" onclick="closeModal()" class="p-2 hover:bg-white/5 rounded-xl text-zinc-400 hover:text-white transition-colors">',
    content
)

# Fix 8: Add title attribute to "Toggle password visibility" button
content = re.sub(
    r'(<button aria-label="Toggle password visibility" onclick="this\.previousElementSibling\.type = \(this\.previousElementSibling\.type === \'password\' \? \'text\' : \'password\'\)" class="absolute right-3 top-1/2 -translate-y-1/2 p-1\.5 text-zinc-500 hover:text-white transition-colors">)',
    r'<button aria-label="Toggle password visibility" title="Toggle password visibility" onclick="this.previousElementSibling.type = (this.previousElementSibling.type === \'password\' ? \'text\' : \'password\')" class="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-zinc-500 hover:text-white transition-colors">',
    content
)

# Fix 9: Add title attribute to "Session Options" button
content = re.sub(
    r'(<button aria-label="Session Options" aria-haspopup="true" onclick="toggleSessionMenu\(event, \'\$\{s\.key\}\'\)" class="p-1 hover:bg-white/10 rounded-md transition-colors opacity-0 group-hover:opacity-100">)',
    r'<button aria-label="Session Options" title="Session Options" aria-haspopup="true" onclick="toggleSessionMenu(event, \'${s.key}\')" class="p-1 hover:bg-white/10 rounded-md transition-colors opacity-0 group-hover:opacity-100">',
    content
)

with open(file_path, "w") as f:
    f.write(content)

file_path_2 = "TARS/webui/templates/components/file_explorer.html"
with open(file_path_2, "r") as f:
    content_2 = f.read()

# Fix 10: Add title attribute to "Item Options" button
content_2 = re.sub(
    r'(<button aria-label="Item Options" class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100 p-2 text-zinc-500 hover:text-white transition-opacity focus:outline-none focus-visible:ring-2 focus-visible:ring-tars-primary rounded-lg">)',
    r'<button aria-label="Item Options" title="Item Options" class="opacity-0 group-hover:opacity-100 focus-visible:opacity-100 p-2 text-zinc-500 hover:text-white transition-opacity focus:outline-none focus-visible:ring-2 focus-visible:ring-tars-primary rounded-lg">',
    content_2
)

with open(file_path_2, "w") as f:
    f.write(content_2)

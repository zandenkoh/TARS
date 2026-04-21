## 2024-05-18 - [Accessibility: Forms and Modals]
**Learning:** Found multiple inputs, buttons, and textareas lacking basic ARIA labels and explicit label associations in `TARS/webui/templates/index.html`. While screen readers can sometimes guess context, explicit labels (`aria-label` or `for`/`id` combinations) are crucial for guaranteed accessibility.
**Action:** When creating new interactive elements, immediately add semantic labeling. Ensure SVGs inside buttons have `aria-hidden="true"` to prevent redundant reading.

## 2024-05-18 - [Accessibility: SVGs inside Buttons]
**Learning:** Found multiple SVGs inside navigation buttons (e.g., Workspace, Tasks, Search) that lacked `aria-hidden="true"`. Since these buttons already have visible text that conveys their meaning, screen readers will redundantly read the SVG content if it is not explicitly hidden.
**Action:** Always add `aria-hidden="true"` to decorative SVGs inside buttons that also contain text to prevent redundant screen reader announcements.

## 2024-05-20 - [UX: Empty States in File Explorer]
**Learning:** Empty states are often overlooked in file explorers, leading to dead-end screens. By adding a drag-and-drop target to the empty state, users immediately know what action is required when encountering an empty directory, and we take advantage of the existing `handleDrop` javascript function.
**Action:** Always consider what the "next step" is when a user hits an empty state, and make the empty state itself an interactive target for that next step when possible.


## 2024-05-21 - [UX: Icon-only Button Tooltips]
**Learning:** Found multiple icon-only buttons (like "New Chat", "Toggle Sidebar", "Notifications") that had correct `aria-label` attributes for screen readers but lacked `title` attributes. Sighted users relying on a mouse need visible tooltips on hover to understand the purpose of ambiguous icons.
**Action:** Always pair `aria-label` attributes with visible `title` tooltips on icon-only interactive elements to ensure accessibility for all user types.

## 2026-04-21 - [Accessibility: Hover vs Focus]
**Learning:** Found multiple contextual actions hidden by default (`opacity-0 group-hover:opacity-100`) that were completely inaccessible to keyboard users because they only revealed on hover. By adding `focus-within:opacity-100` to the parent container and `focus:outline-none focus-visible:opacity-100 focus-visible:ring-2` to the buttons, these critical actions are now discoverable and usable via keyboard navigation.
**Action:** When hiding contextual UI elements via hover state, always pair it with `focus-within` on the container and explicit focus states on the interactive elements to guarantee keyboard accessibility.

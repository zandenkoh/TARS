## 2024-05-18 - [Accessibility: Forms and Modals]
**Learning:** Found multiple inputs, buttons, and textareas lacking basic ARIA labels and explicit label associations in `TARS/webui/templates/index.html`. While screen readers can sometimes guess context, explicit labels (`aria-label` or `for`/`id` combinations) are crucial for guaranteed accessibility.
**Action:** When creating new interactive elements, immediately add semantic labeling. Ensure SVGs inside buttons have `aria-hidden="true"` to prevent redundant reading.

## 2024-05-18 - [Accessibility: SVGs inside Buttons]
**Learning:** Found multiple SVGs inside navigation buttons (e.g., Workspace, Tasks, Search) that lacked `aria-hidden="true"`. Since these buttons already have visible text that conveys their meaning, screen readers will redundantly read the SVG content if it is not explicitly hidden.
**Action:** Always add `aria-hidden="true"` to decorative SVGs inside buttons that also contain text to prevent redundant screen reader announcements.

## 2024-05-20 - [UX: Empty States in File Explorer]
**Learning:** Empty states are often overlooked in file explorers, leading to dead-end screens. By adding a drag-and-drop target to the empty state, users immediately know what action is required when encountering an empty directory, and we take advantage of the existing `handleDrop` javascript function.
**Action:** Always consider what the "next step" is when a user hits an empty state, and make the empty state itself an interactive target for that next step when possible.

## 2024-05-22 - [Accessibility: Keyboard Traps with Visually Hidden Elements]
**Learning:** Found multiple contextual actions (like hover-based toolbars or delete options) that were visually hidden using `opacity-0 group-hover:opacity-100`. While mouse users can see and interact with them, keyboard-only users navigating via tab order would focus on these elements but remain completely unaware of them, creating a keyboard trap and hiding functionality.
**Action:** Always pair `opacity-0 group-hover:opacity-100` patterns with explicit focus visibility utilities (e.g., `focus-within:opacity-100`, `group-focus-visible:opacity-100`, `focus-visible:opacity-100`) and ensure they have a visible focus outline (e.g., `focus-visible:ring-1`).

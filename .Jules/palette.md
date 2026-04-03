## 2024-05-18 - [Accessibility: Forms and Modals]
**Learning:** Found multiple inputs, buttons, and textareas lacking basic ARIA labels and explicit label associations in `TARS/webui/templates/index.html`. While screen readers can sometimes guess context, explicit labels (`aria-label` or `for`/`id` combinations) are crucial for guaranteed accessibility.
**Action:** When creating new interactive elements, immediately add semantic labeling. Ensure SVGs inside buttons have `aria-hidden="true"` to prevent redundant reading.

## 2024-05-18 - [Accessibility: SVGs inside Buttons]
**Learning:** Found multiple SVGs inside navigation buttons (e.g., Workspace, Tasks, Search) that lacked `aria-hidden="true"`. Since these buttons already have visible text that conveys their meaning, screen readers will redundantly read the SVG content if it is not explicitly hidden.
**Action:** Always add `aria-hidden="true"` to decorative SVGs inside buttons that also contain text to prevent redundant screen reader announcements.

## 2024-05-20 - [UX: Empty States in File Explorer]
**Learning:** Empty states are often overlooked in file explorers, leading to dead-end screens. By adding a drag-and-drop target to the empty state, users immediately know what action is required when encountering an empty directory, and we take advantage of the existing `handleDrop` javascript function.
**Action:** Always consider what the "next step" is when a user hits an empty state, and make the empty state itself an interactive target for that next step when possible.

## 2024-05-25 - [Accessibility: Hidden Contextual Actions]
**Learning:** Contextual actions in the UI (such as "Session Options", "Wipe Data", or hover-actions on search results) are often styled to only appear on hover (`opacity-0 group-hover:opacity-100`). This completely hides these actions from keyboard-only users because there are no visual indicators when tabbing to these buttons.
**Action:** Always pair `group-hover:opacity-100` visual patterns with `group-focus-visible:opacity-100` or `focus-visible:opacity-100` alongside clear focus rings (`focus-visible:ring-1`) so that users navigating via keyboard can discover and interact with contextual actions.

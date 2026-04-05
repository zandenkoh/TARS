## 2024-05-18 - [Accessibility: Forms and Modals]
**Learning:** Found multiple inputs, buttons, and textareas lacking basic ARIA labels and explicit label associations in `TARS/webui/templates/index.html`. While screen readers can sometimes guess context, explicit labels (`aria-label` or `for`/`id` combinations) are crucial for guaranteed accessibility.
**Action:** When creating new interactive elements, immediately add semantic labeling. Ensure SVGs inside buttons have `aria-hidden="true"` to prevent redundant reading.

## 2024-05-18 - [Accessibility: SVGs inside Buttons]
**Learning:** Found multiple SVGs inside navigation buttons (e.g., Workspace, Tasks, Search) that lacked `aria-hidden="true"`. Since these buttons already have visible text that conveys their meaning, screen readers will redundantly read the SVG content if it is not explicitly hidden.
**Action:** Always add `aria-hidden="true"` to decorative SVGs inside buttons that also contain text to prevent redundant screen reader announcements.

## 2024-05-20 - [UX: Empty States in File Explorer]
**Learning:** Empty states are often overlooked in file explorers, leading to dead-end screens. By adding a drag-and-drop target to the empty state, users immediately know what action is required when encountering an empty directory, and we take advantage of the existing `handleDrop` javascript function.
**Action:** Always consider what the "next step" is when a user hits an empty state, and make the empty state itself an interactive target for that next step when possible.

## 2024-05-22 - [Accessibility: Hover-only Contextual Actions]
**Learning:** Found multiple contextual actions (like the message Copy/Export buttons and Session options menu) that were visually hidden by default using `opacity-0 group-hover:opacity-100`. This creates a keyboard trap where the elements are technically focusable by tabbing, but remain invisible because the `:hover` state is not triggered.
**Action:** When implementing contextual actions that are hidden by default, always pair `group-hover:opacity-100` with focus visibility styles (e.g., `focus-within:opacity-100` on the parent, or `focus-visible:opacity-100` on the child itself) and explicit focus indicators (e.g., `focus-visible:ring-2`) so keyboard users know exactly where their focus is and can access the hidden actions.

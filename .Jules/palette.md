## 2024-05-18 - [Accessibility: Forms and Modals]
**Learning:** Found multiple inputs, buttons, and textareas lacking basic ARIA labels and explicit label associations in `TARS/webui/templates/index.html`. While screen readers can sometimes guess context, explicit labels (`aria-label` or `for`/`id` combinations) are crucial for guaranteed accessibility.
**Action:** When creating new interactive elements, immediately add semantic labeling. Ensure SVGs inside buttons have `aria-hidden="true"` to prevent redundant reading.

## 2024-05-18 - [Accessibility: SVGs inside Buttons]
**Learning:** Found multiple SVGs inside navigation buttons (e.g., Workspace, Tasks, Search) that lacked `aria-hidden="true"`. Since these buttons already have visible text that conveys their meaning, screen readers will redundantly read the SVG content if it is not explicitly hidden.
**Action:** Always add `aria-hidden="true"` to decorative SVGs inside buttons that also contain text to prevent redundant screen reader announcements.

## 2024-05-20 - [UX: Empty States in File Explorer]
**Learning:** Empty states are often overlooked in file explorers, leading to dead-end screens. By adding a drag-and-drop target to the empty state, users immediately know what action is required when encountering an empty directory, and we take advantage of the existing `handleDrop` javascript function.
**Action:** Always consider what the "next step" is when a user hits an empty state, and make the empty state itself an interactive target for that next step when possible.

## 2024-04-11 - Adding aria-hidden to decorative SVGs in UI components
**Learning:** In the TARS WebUI templates, there were numerous interactive elements (buttons, div placeholders, etc.) that contained inline `<svg>` elements used purely for decorative purposes or iconography alongside visible text. These SVGs were missing `aria-hidden="true"`, causing screen readers to redundantly announce the SVG content or announce it poorly.
**Action:** Applied a bulk update to ensure all `<svg>` elements across the main and component templates explicitly include `aria-hidden="true"`. In the future, explicitly define `aria-hidden="true"` when inserting new inline SVGs within interactive elements that already have text labels.

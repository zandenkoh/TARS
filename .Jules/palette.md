## 2024-05-18 - [Accessibility: Forms and Modals]
**Learning:** Found multiple inputs, buttons, and textareas lacking basic ARIA labels and explicit label associations in `TARS/webui/templates/index.html`. While screen readers can sometimes guess context, explicit labels (`aria-label` or `for`/`id` combinations) are crucial for guaranteed accessibility.
**Action:** When creating new interactive elements, immediately add semantic labeling. Ensure SVGs inside buttons have `aria-hidden="true"` to prevent redundant reading.

## 2024-05-18 - [Accessibility: SVGs inside Buttons]
**Learning:** Found multiple SVGs inside navigation buttons (e.g., Workspace, Tasks, Search) that lacked `aria-hidden="true"`. Since these buttons already have visible text that conveys their meaning, screen readers will redundantly read the SVG content if it is not explicitly hidden.
**Action:** Always add `aria-hidden="true"` to decorative SVGs inside buttons that also contain text to prevent redundant screen reader announcements.

## 2024-05-20 - [UX: Empty States in File Explorer]
**Learning:** Empty states are often overlooked in file explorers, leading to dead-end screens. By adding a drag-and-drop target to the empty state, users immediately know what action is required when encountering an empty directory, and we take advantage of the existing `handleDrop` javascript function.
**Action:** Always consider what the "next step" is when a user hits an empty state, and make the empty state itself an interactive target for that next step when possible.

## 2024-05-22 - [Accessibility: Hidden Contextual Actions]
**Learning:** Actions that rely on hover states (`group-hover:opacity-100`) for visibility are inherently inaccessible to keyboard-only and screen reader users unless paired with equivalent focus utilities. Furthermore, if a parent element is keyboard focusable, its hidden child actions won't appear when the parent is focused unless `group-focus-within:opacity-100` is used.
**Action:** When implementing contextual actions in Tailwind that are visually hidden by default (e.g., using `opacity-0 group-hover:opacity-100`), always pair them with `group-focus-within:opacity-100` and `focus-visible:opacity-100` on the interactive elements, alongside explicit focus outlines (e.g., `focus-visible:ring-1`) to prevent keyboard traps and ensure visual parity.

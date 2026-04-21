## 2024-05-22 - [Accessibility: Hover-only Context Actions]
**Learning:** Found several context actions (like "Copy", "Export", "Session Options", and "Wipe Data" icons) that were hidden by default and only visible on `group-hover` (using `opacity-0 group-hover:opacity-100`). This made them completely invisible to keyboard-only users who navigate via Tab.
**Action:** Always pair hover-based visibility classes with focus-based visibility classes. For parent containers, add `focus-within:opacity-100` so the children appear when navigating inside. For the hidden interactive elements themselves, add `focus-visible:opacity-100` along with visible focus rings (`focus-visible:ring-2`) to ensure they are perceivable and usable via keyboard.

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

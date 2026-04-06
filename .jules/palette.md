## 2024-03-31 - [Workspace Explorer A11y]
**Learning:** HTMX-powered `<div>` elements used for navigation (`hx-get`) lack native keyboard accessibility by default. Users cannot tab to them or activate them with the Enter key, and hover-only CSS classes hide contextual actions from keyboard users.
**Action:** When using `div` elements as interactive buttons with HTMX, explicitly add `tabindex="0"`, `role="button"`, and handle keyboard events (e.g., `hx-trigger="click, keyup[key=='Enter']"`). Ensure contextual actions use `focus-visible` variants instead of relying solely on `group-hover`.

## 2024-05-24 - [Adding A11y to Custom Toggles]
**Learning:** Custom interactive components (like divs used as switches) are completely invisible to keyboard-only users by default. To make them accessible and navigable, they need `tabindex="0"`, a proper semantic `role="switch"`, an `aria-checked` attribute that updates dynamically, an `onkeydown` handler mapping `Enter` and `Space` to click actions, and a visible focus ring using Tailwind utility classes (`focus-visible:ring-1 focus-visible:ring-white/20`).
**Action:** Always add `tabindex="0"`, `role`, `aria-*` attributes, keyboard event handlers (`onkeydown`), and `focus-visible:` classes whenever constructing custom interactive form controls like toggles instead of relying only on native input elements.

## 2025-02-18 - Keyboard Accessibility for Interactive Divs
**Learning:** When using `<div>` elements for interactive components (like dropdown menus or clickable search results) instead of native `<button>` or `<a>` elements, they inherently lack keyboard accessibility. Users cannot tab to them or trigger them with the Enter key. Adding `tabindex="0"` and `role="button"` makes them discoverable by screen readers and keyboard navigation, but does not automatically add keyboard activation. We must manually attach an `onkeydown` listener (checking for the 'Enter' or 'Space' key) to replicate native button behavior and ensure full keyboard accessibility. Furthermore, focus styling (e.g., `focus-visible:ring-2`) is critical to visually indicate the active state to keyboard users.
**Action:** Always prefer native `<button>` or `<a>` elements for interactive actions. If a `<div>` must be used, always include `tabindex="0"`, `role="button"`, an `onkeydown` activation handler, and `focus-visible` styling.

## 2025-03-30 - Added ARIA labels to icon buttons
**Learning:** The TARS webui relies heavily on Tailwind CSS and icon-only buttons for a minimalist aesthetic. Many of these buttons (such as the toggle sidebar, attach files, send message, grid/list view toggles, etc.) were completely invisible to screen readers because they lacked `aria-label`s. In addition, the internal `<svg>` elements were lacking `aria-hidden="true"`, which is considered best practice.
**Action:** When working on UI enhancements in the future, proactively check for missing `aria-label` and `aria-hidden` attributes on icon-only interactive elements. Use `aria-haspopup` for elements that trigger menus or dialogs to further aid assistive technologies.

## 2025-05-01 - Connected Setting Labels to Inputs
**Learning:** Settings forms in TARS were generated programmatically and missed `for` attributes on their `<label>`s, and the inputs lacked matching `id`s. This meant clicking the label text didn't focus or toggle the input, reducing the clickable area and negatively impacting usability and accessibility.
**Action:** When dynamically generating forms or using templates (like Jinja's `render_config_item`), always dynamically generate `id` and `for` attributes to properly associate labels with their respective inputs.

## 2026-04-02 - Standardizing Dynamic Empty States
**Learning:** Empty states should never replace or rename core creation actions. In TARS, the "Projects" sidebar empty state previously hid the main category header and replaced the "New project" button with a mislabeled "Projects" button that functioned identically but broke consistency. This confused users who didn't expect a navigation-like label to act as a creation action.
**Action:** Unify empty and filled states to consistently display core structural elements (headers, creation buttons). Use a dedicated, clearly labeled empty state placeholder instead of co-opting existing actions. Additionally, always remember to add `focus-visible` styling to dynamically generated interactive elements to preserve keyboard accessibility.

## 2025-05-24 - [Inline Feedback for Async Actions]
**Learning:** Using native browser `alert()` dialogues for success messages on forms is jarring, blocks the UI thread, and requires an extra click from the user. It breaks the flow of a modern web application.
**Action:** Replace blocking `alert()` calls with inline visual feedback on the triggering button itself (e.g., changing text to "SAVING...", disabling the button, and then showing "SAVED!" temporarily on success). This provides clear, non-intrusive feedback and prevents double submissions.

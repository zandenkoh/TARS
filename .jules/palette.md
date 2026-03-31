## 2025-03-30 - Added ARIA labels to icon buttons
**Learning:** The TARS webui relies heavily on Tailwind CSS and icon-only buttons for a minimalist aesthetic. Many of these buttons (such as the toggle sidebar, attach files, send message, grid/list view toggles, etc.) were completely invisible to screen readers because they lacked `aria-label`s. In addition, the internal `<svg>` elements were lacking `aria-hidden="true"`, which is considered best practice.
**Action:** When working on UI enhancements in the future, proactively check for missing `aria-label` and `aria-hidden` attributes on icon-only interactive elements. Use `aria-haspopup` for elements that trigger menus or dialogs to further aid assistive technologies.

## 2024-03-31 - [Workspace Explorer A11y]
**Learning:** HTMX-powered `<div>` elements used for navigation (`hx-get`) lack native keyboard accessibility by default. Users cannot tab to them or activate them with the Enter key, and hover-only CSS classes hide contextual actions from keyboard users.
**Action:** When using `div` elements as interactive buttons with HTMX, explicitly add `tabindex="0"`, `role="button"`, and handle keyboard events (e.g., `hx-trigger="click, keyup[key=='Enter']"`). Ensure contextual actions use `focus-visible` variants instead of relying solely on `group-hover`.

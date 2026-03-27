---
name: inline_buttons
description: Use inline buttons for interactive Telegram bot flows.
metadata:
  platforms: [telegram]
  tools: [message]
---

# Inline Buttons Skill

This skill allows you to create interactive flows in Telegram using inline buttons. You can attach buttons directly to a message, and when the user clicks them, you will receive a new message with the callback data.

## Creating Buttons

To send a message with inline buttons, use the `message` tool with the `reply_markup` parameter.

### Example: Simple Choice

```json
{
  "content": "What would you like to do?",
  "reply_markup": {
    "inline_keyboard": [
      [
        {"text": "Option A", "callback_data": "opt_a"},
        {"text": "Option B", "callback_data": "opt_b"}
      ]
    ]
  }
}
```

### Example: URL Buttons

```json
{
  "content": "Check out our website!",
  "reply_markup": {
    "inline_keyboard": [
      [
        {"text": "Open Google", "url": "https://google.com"}
      ]
    ]
  }
}
```

## Handling Interactions

When a user clicks a button (with `callback_data`), you will receive a new inbound message that looks like this:

`[User clicked button with callback_data: 'opt_a' on message: 'What would you like to do?']`

You should:
1.  Analyze the `callback_data` (e.g., `opt_a`).
2.  Respond accordingly based on the context of the interaction.
3.  You can send another message with updated buttons if needed, creating a dynamic interface.

## Best Practices

-   Keep `callback_data` short and descriptive.
-   Use rows of buttons to organize complex options.
-   Provide a "Back" or "Cancel" button if appropriate.
-   Acknowledge the button press by sending a new message or updating the state.

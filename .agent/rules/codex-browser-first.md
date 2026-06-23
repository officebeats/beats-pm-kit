# Codex Browser First

Use this rule whenever Codex needs a browser for local apps, rendered UI checks, localhost demos, screenshots, click-through validation, or web page inspection.

## Default

1. Use the Codex in-app Browser first.
2. Keep browser work contained in the Codex session unless the user explicitly asks to use an external browser.
3. For local apps, start the required local server normally, then open and validate the URL in the Codex Browser.
4. Capture screenshots, DOM state, console warnings/errors, and interaction evidence through the Codex Browser whenever possible.
5. Do not default to macOS `open`, Chrome, Edge, Safari, Computer Use, or standalone Playwright before trying the Codex Browser.

## External Browser Fallback

Use an external browser only when there is a concrete reason, such as:

- The user explicitly asks for an external browser.
- The task requires the user's browser profile, cookies, extensions, SSO state, or saved credentials.
- The issue is browser-specific and needs Chrome, Edge, Safari, or Firefox reproduction.
- The Codex Browser is unavailable, cannot reach the target, or fails after a reasonable attempt.
- The workflow requires browser permissions, downloads, or OS integration that the Codex Browser cannot provide.

When using an external browser, state the reason briefly and keep the external action scoped to that need.

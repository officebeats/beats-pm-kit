# Type: Architecture

Used for system stacks, API flows, and cloud infrastructure.

## Pattern: The "Bilateral Bridge"

Best for Partner API integrations.

- **Partner Domain (Left)**: A large, muted gray block representing the external system.
- **Reasoning Engine (Right Stack)**: A stack of vertical blocks representing the core reasoning services.
- **The Bridge**: Horizontal connectors representing the synchronous requests.

## Implementation Details

```html
<div class="arch-container">
  <!-- Actor -->
  <div class="node partner" style="width: 440px; height: 320px;">
    <div class="label">Partner System</div>
  </div>

  <!-- Flows -->
  <div class="bridge">
    <div class="connector" style="top: 100px;">1. Auth</div>
    <div class="connector" style="bottom: 100px;">2. Logic</div>
  </div>

  <!-- Stack -->
  <div class="stack">
    <div class="node accent" style="width: 440px; height: 140px;">Identity</div>
    <div class="node secondary" style="width: 440px; height: 140px;">Reasoning API</div>
  </div>
</div>
```

## CSS Primitive

```css
.arch-container { display: flex; position: relative; }
.node { border: 1px solid var(--ink); border-radius: 8px; }
.node.accent { background: var(--accent); color: white; }
.node.secondary { border: 2px solid var(--secondary); color: var(--ink); }
.connector { border-bottom: 2px solid var(--muted); position: absolute; }
```

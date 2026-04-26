# Diagram Designer Skill

Editorial-quality architecture, flow, and strategy diagrams. Self-contained HTML + SVG. No shadows, no Mermaid-slop.

## Selection Guide

| Type | Best For | Reference |
| :--- | :--- | :--- |
| **Architecture** | System flows, API integrations, Cloud stacks | `references/type-architecture.md` |
| **Flowchart** | Logical decision trees, user journeys | `references/type-flowchart.md` |
| **Sequence** | Handshakes, auth flows, timing | `references/type-sequence.md` |
| **Quadrant** | Impact vs Effort, Market maps | `references/type-quadrant.md` |
| **Timeline** | Product roadmaps, project phases | `references/type-timeline.md` |

## Design System (Enterprise Healthcare Palette)

- **Paper**: `#ffffff` (Background)
- **Ink**: `#1e293b` (Primary text/strokes)
- **Accent**: `#025893` (Navy — Primary focal points)
- **Secondary**: `#00968F` (Teal — Supporting elements)
- **Muted**: `#e2e8f0` (Connectors/Secondary borders)

## Rules of the Grid

1. **Hierarchy**: Every node must earn its place. Reserve the **Accent** color for the 1–2 most important elements.
2. **The 4px Grid**: All coordinates, widths, and gaps must be divisible by 4.
3. **Typography**:
    - Titles: `Inter`, Bold, 54px.
    - Node Labels: `Inter`, Semibold, 24-32px.
    - Sublabels/Technical: `monospace` (Geist Mono equivalent), 18-22px.
4. **No Shadows**: Use 1px hairlines and solid fills. Max border-radius: 10px.
5. **Connectors**: Use flat paths with simple 2D arrowheads. No gradients.

## Checklist

- [ ] Does every node have a clear purpose?
- [ ] Is the focal point clear (Accent color)?
- [ ] Are all dimensions on the 4px grid?
- [ ] Is contrast WCAG AA compliant?

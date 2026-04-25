---
name: documentation
description: Generate and update technical documentation. Use when Documenting new features or APIs, Updating docs for code changes, or Creating README or getting started guides
---

# Documentation

Use this skill to create or update technical documentation that matches the current code and the target audience.

## Workflow
1. Identify the target audience
2. Determine what needs to be documented
3. Write clear, concise explanations
4. Include working code examples
5. Add any necessary diagrams or visuals
6. Review for clarity and completeness
7. Verify examples work with current code

## Examples
**Function documentation:**
```typescript
/**
 * Calculates the total price of items in a cart.
 *
 * @param items - Array of cart items with price property
 * @returns The sum of all item prices
 * @throws {Error} If items is not an array
 *
 * @example
 * const total = calculateTotal([{ price: 10 }, { price: 20 }]);
 * // Returns: 30
 */
function calculateTotal(items: CartItem[]): number
```

## Quality Bar
- Write for your audience's knowledge level
- Lead with the most important information
- Include working, copy-pasteable examples
- Keep documentation close to the code
- Update docs in the same PR as code changes
- Use consistent formatting and terminology

## Resource Strategy
- Add `scripts/` only when the task is fragile, repetitive, or benefits from deterministic execution.
- Add `references/` only when details are too large or too variant-specific to keep in `SKILL.md`.
- Add `assets/` only for files that will be consumed in the final output.
- Keep extra docs out of the skill folder; prefer `SKILL.md` plus only the resources that materially help.

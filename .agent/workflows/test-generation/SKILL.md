---
name: test-generation
description: Generate comprehensive test cases for code. Use when Writing tests for new functionality, Adding tests for bug fixes (regression tests), or Improving test coverage for existing code
---

# Test Generation

Use this skill to produce tests that cover behavior, regressions, and the repository testing conventions.

## Workflow
1. Identify the function/component to test
2. List the behaviors that need testing
3. Write tests for happy path scenarios
4. Add tests for edge cases and boundaries
5. Include error handling tests
6. Mock external dependencies appropriately
7. Verify tests are deterministic and isolated

## Examples
**Unit test example:**
```typescript
describe('calculateTotal', () => {
  it('should sum item prices correctly', () => {
    const items = [{ price: 10 }, { price: 20 }];
    expect(calculateTotal(items)).toBe(30);
  });

  it('should return 0 for empty array', () => {
    expect(calculateTotal([])).toBe(0);
  });

  it('should handle negative prices', () => {
    const items = [{ price: 10 }, { price: -5 }];
    expect(calculateTotal(items)).toBe(5);
  });
});
```

## Quality Bar
- Test behavior, not implementation
- Use descriptive test names that explain what and why
- Follow Arrange-Act-Assert pattern
- Keep tests independent and isolated
- Don't test external libraries
- Mock at the boundary, not everywhere
- Aim for fast, reliable tests

## Resource Strategy
- Add `scripts/` only when the task is fragile, repetitive, or benefits from deterministic execution.
- Add `references/` only when details are too large or too variant-specific to keep in `SKILL.md`.
- Add `assets/` only for files that will be consumed in the final output.
- Keep extra docs out of the skill folder; prefer `SKILL.md` plus only the resources that materially help.

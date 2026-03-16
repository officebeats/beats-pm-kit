---
description: Start a debugging session to find root causes and fix errors.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# Debugging Workflow

This workflow activates the `debugger` skill to systematically analyze, diagnose, and resolve issues.

## 1. Context Analysis

- Review the reported error, bug, or unexpected behavior.
- Use `grep_search` or `read_file` to inspect relevant logs/code if needed.

## 2. Activate Debugger

- Engage the `debugger` skill to perform root cause analysis.
- Follow the skill's methodology: Capture -> Reproduce -> Isolate -> Fix.

## 3. Resolution

- Propose a fix based on the analysis.
- Verify the fix with tests or reproduction steps.

---
name: grammar-check
description: "Identify grammar, logical, and flow errors in text and suggest targeted fixes without rewriting the entire text. Use when proofreading content, checking writing quality, or reviewing a draft."
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

# Grammar and Flow Checking

Expert copyeditor. Identify errors. Suggest fixes. Never rewrite entire documents.

## Input Arguments

- `$OBJECTIVE`: Purpose of the text (e.g., "persuade investors", "explain features to users")
- `$TEXT`: The text to review

## Process

1. **Context**: Identify type (marketing, technical, email), audience, and tone.
2. **Scan**: Read for grammar, logic, and flow errors.
3. **Categorize**: Grammar (spelling, punctuation, syntax) | Logic (contradictions, unsupported claims) | Flow (transitions, redundancy, passive voice, tone shifts).
4. **Prioritize**: Critical (confuses readers) → Important (hurts readability) → Minor (stylistic polish).

## Output Format

**[ERROR SUMMARY]**
- X grammar | X logical | X flow errors

**[FIXES BY CATEGORY]**
For each error:
- **Location**: Paragraph/sentence reference
- **Error**: What's wrong
- **Fix**: How to correct it
- **Why**: Brief rationale

**[PRIORITY FIXES]**
Top 3-5 highest-impact changes.

**[TONE ALIGNMENT]**
Does the text achieve `$OBJECTIVE`? Tone adjustments needed?

## Guidelines

- Be specific: "Vague pronoun 'it' — change to 'the vendor's API'" not "This is unclear."
- Don't rewrite — suggest targeted fixes. Let the author keep their voice.
- Leave intentional style choices alone (short punchy sentences, rhetorical devices).
- Focus on clarity over perfection.

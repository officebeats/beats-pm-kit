---
description: Launch a product.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.



# /launch - Go-to-Market Strategy

**Trigger**: User types `/launch` or asks for a GTM plan.

## Steps

1. **Parallel Context Analysis**:
   - **Action**: In a SINGLE turn, read `2. Products/` AND `grep_search` `3. Meetings/transcripts/` for "launch", "release", or "GTM".
   - **Goal**: Understand _what_ is launching and if dates were discussed.

2. **Extract Value Proposition**:
   - **Agent**: `prd-author`
   - Extract core Value Prop, Target Audience, and Key Differentiators from the relevant PRD.
   - **Output**: `2. Products/[Product]/launch/Value_Matrix.md`

3. **Define Audience & Channels**:
   - Who is this for? (Target Persona).
   - Which channels reach them? (Email, Blog, Social, In-App).

4. **Draft Plan**: Create a T-Minus schedule (Internal Comms, Beta, GA).

5. **Generate Marketing Assets**:
   - Draft 3 tagline ideas and a 1-paragraph "Press Release" based on the Value Matrix.
   - Generate a Blog Post and Tweet thread.
   - **Output**: `2. Products/[Product]/launch/Marketing_Copy.md`

6. **Draft Release Comms**:
   - **Agent**: `stakeholder-manager`
   - Draft a "General Availability" email to the target audience.
   - **Output**: `2. Products/[Product]/launch/Release_Email.md`

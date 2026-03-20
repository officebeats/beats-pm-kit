---
name: youtube-summarizer
description: Advanced agent for chatting with and summarizing YouTube videos.
---

# Chat with YouTube Videos

**Advanced agent for chatting with and summarizing YouTube videos.**

This skill leverages an advanced Python-based AI Agent or Multi-Agent Team located in the `scripts/` directory.

## Instructions
1. Use this skill whenever the user triggers the associated playbook or asks for youtube-summarizer.
2. Navigate to `scripts/` inside this skill's directory.
3. Review the `requirements.txt` and python script to understand how to invoke the agent (e.g. via `streamlit run` or `python`).
4. Execute the agent script to perform the requested tasks.

## Protocol constraints
- Do not hallucinate capabilities. Rely on the underlying python agent.
- Keep output concise and delegate complex reasoning to the agent in `scripts/`.

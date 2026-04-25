---
description: Check if OfficeCLI is installed and install it if not. Creates, reads, and edits Word, Excel, and PowerPoint files.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

# /office-cli — OfficeCLI Setup & Status

**Trigger**: `/office-cli`

---

## Step 1: Check Installation

// turbo
```bash
officecli --version 2>&1 || echo "NOT_INSTALLED"
```

- If the output contains a version number (e.g., `1.0.52`) → **OfficeCLI is installed.** Skip to Step 3.
- If the output contains `NOT_INSTALLED` or any error → **OfficeCLI is not installed.** Continue to Step 2.

---

## Step 2: Install OfficeCLI

Tell the user:
```
📦 OfficeCLI is not installed. Installing now...
   Single binary, no dependencies, no Office installation required.
```

### Windows
```powershell
irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
```

### macOS / Linux
```bash
curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
```

After installation, verify:

// turbo
```bash
officecli --version
```

If verification fails, tell the user to restart their terminal (PATH update may require a new session).

---

## Step 3: Show Status

Display:
```
✅ OfficeCLI v{version} is installed and ready.

📄 What you can do:
  • Create PowerPoint decks     → officecli create deck.pptx
  • Create Word documents       → officecli create report.docx
  • Create Excel spreadsheets   → officecli create data.xlsx
  • Live preview presentations  → officecli watch deck.pptx

💡 Ask me to "make a PowerPoint about X" or "export this as a Word doc" to get started.
```

---

## Step 4: Activate Skill

Load the `office-cli` skill from `.agent/skills/office-cli/SKILL.md` for any follow-up document creation requests.

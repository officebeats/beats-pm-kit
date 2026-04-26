---
name: office-cli
description: Create, read, and edit Word (.docx), Excel (.xlsx), and PowerPoint (.pptx) files using OfficeCLI. Use when user requests Office documents, presentations, spreadsheets, or exports to Office formats.
---

> **Compatibility Directive**: This component is optimized primarily for the Google Antigravity runtime, but gracefully degrades to support Gemini CLI, Claude Code, and Kilocode CLI.

# OfficeCLI Skill

Use this skill when the user requests a PowerPoint deck, Word document, Excel spreadsheet, or any Office format export. OfficeCLI is a single-binary CLI that creates and edits `.pptx`, `.docx`, and `.xlsx` files — no Microsoft Office installation required.

## Prerequisites

Verify OfficeCLI is installed:

```bash
officecli --version
```

If not installed, run:

```powershell
# Windows
irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex

# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
```

## Core Commands

| Command | Purpose |
|---------|---------|
| `officecli create <file>` | Create a blank document |
| `officecli add <file> <path> --type <type> --prop key=value` | Add elements |
| `officecli set <file> <path> --prop key=value` | Modify properties |
| `officecli get <file> <path> [--json]` | Read element properties |
| `officecli view <file> outline` | View document structure |
| `officecli view <file> html` | Preview in browser |
| `officecli batch <file> --commands '<json>'` | Multi-op atomic writes |
| `officecli remove <file> <path>` | Delete elements |
| `officecli validate <file>` | Check document integrity |
| `officecli watch <file>` | Live preview (auto-refresh) |

## Key Rules

1. **All attributes use `--prop`** — never `--name "foo"`, always `--prop name="foo"`
2. **Paths are 1-based** — `/slide[1]` = first slide, `/body/p[3]` = third paragraph
3. **Single-quote paths in shell** — `'/slide[1]/shape[2]'` to avoid glob expansion
4. **`--index` is 0-based** — `--index 0` = first position (for `add`/`move`)
5. **PPT shape[1] is usually the title** — content shapes start at `shape[2]`
6. **Use `officecli <format> set <element>` when unsure** about property names

---

## PowerPoint Workflow

### Create a Presentation from Content

```bash
# 1. Create blank deck
officecli create deck.pptx

# 2. Add title slide
officecli add deck.pptx / --type slide --prop title="Q4 Revenue Report" --prop background=1A1A2E

# 3. Add content shapes to slide 1
officecli add deck.pptx '/slide[1]' --type shape \
  --prop text="Revenue grew 25% YoY" \
  --prop x=2cm --prop y=5cm --prop w=20cm --prop h=3cm \
  --prop font=Arial --prop size=28 --prop color=FFFFFF

# 4. Add a second slide with a table
officecli add deck.pptx / --type slide --prop title="Breakdown"
officecli add deck.pptx '/slide[2]' --type table \
  --prop rows=4 --prop cols=3 \
  --prop x=2cm --prop y=4cm --prop w=22cm --prop h=10cm

# 5. Populate table cells
officecli set deck.pptx '/slide[2]/table[1]/row[1]/cell[1]' --prop text="Region" --prop bold=true
officecli set deck.pptx '/slide[2]/table[1]/row[1]/cell[2]' --prop text="Revenue" --prop bold=true
officecli set deck.pptx '/slide[2]/table[1]/row[1]/cell[3]' --prop text="Growth" --prop bold=true

# 6. Add image to a slide
officecli add deck.pptx '/slide[1]' --type picture \
  --prop file=logo.png --prop x=22cm --prop y=1cm --prop w=4cm --prop h=4cm

# 7. Validate
officecli validate deck.pptx
```

### Batch Mode (Recommended for 3+ Operations)

```bash
officecli batch deck.pptx --commands '[
  {"command":"add","parent":"/","type":"slide","props":{"title":"Slide 3","background":"2D2D44"}},
  {"command":"add","parent":"/slide[3]","type":"shape","props":{"text":"Key Takeaways","x":"2cm","y":"3cm","w":"22cm","h":"2cm","font":"Arial","size":"32","bold":"true","color":"FFFFFF"}},
  {"command":"add","parent":"/slide[3]","type":"shape","props":{"text":"• Metric A up 15%\n• Metric B steady\n• Metric C needs attention","x":"2cm","y":"6cm","w":"22cm","h":"10cm","font":"Arial","size":"20","color":"E0E0E0"}}
]' --json
```

---

## Word Document Workflow

### Create a Report

```bash
# 1. Create blank document
officecli create report.docx

# 2. Set document defaults
officecli set report.docx / --prop docDefaults.font=Arial --prop docDefaults.fontSize=11pt

# 3. Add title
officecli add report.docx / --type paragraph \
  --prop text="Quarterly Business Review" --prop style=Heading1

# 4. Add body paragraphs
officecli add report.docx / --type paragraph \
  --prop text="This report covers Q4 performance metrics and strategic outlook."

# 5. Add a table
officecli add report.docx / --type table --prop rows=3 --prop cols=2

# 6. Populate table
officecli set report.docx '/body/table[1]/row[1]/cell[1]' --prop text="Metric" --prop bold=true
officecli set report.docx '/body/table[1]/row[1]/cell[2]' --prop text="Value" --prop bold=true

# 7. Add image
officecli add report.docx / --type image --prop file=chart.png --prop w=15cm

# 8. Validate
officecli validate report.docx
```

---

## Excel Workflow

### Create a Tracker/Dashboard

```bash
# 1. Create blank workbook
officecli create tracker.xlsx

# 2. Set header row
officecli batch tracker.xlsx --commands '[
  {"command":"set","path":"/Sheet1/A1","props":{"value":"Task","bold":"true","fill":"1A1A2E","color":"FFFFFF"}},
  {"command":"set","path":"/Sheet1/B1","props":{"value":"Owner","bold":"true","fill":"1A1A2E","color":"FFFFFF"}},
  {"command":"set","path":"/Sheet1/C1","props":{"value":"Status","bold":"true","fill":"1A1A2E","color":"FFFFFF"}},
  {"command":"set","path":"/Sheet1/D1","props":{"value":"Due Date","bold":"true","fill":"1A1A2E","color":"FFFFFF"}}
]' --json

# 3. Add data rows
officecli set tracker.xlsx '/Sheet1/A2' --prop value="Launch feature X"
officecli set tracker.xlsx '/Sheet1/B2' --prop value="Alice"
officecli set tracker.xlsx '/Sheet1/C2' --prop value="In Progress"

# 4. Add formulas
officecli set tracker.xlsx '/Sheet1/E1' --prop value="=COUNTA(A2:A100)" --prop bold=true

# 5. Add chart
officecli add tracker.xlsx /Sheet1 --type chart \
  --prop type=bar --prop source="Sheet1!A1:D10" \
  --prop x=6 --prop y=12 --prop w=10 --prop h=8

# 6. Validate
officecli validate tracker.xlsx
```

---

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `--name "foo"` | Use `--prop name="foo"` — all attributes go through `--prop` |
| Negative coordinates `x=-3cm` | Not supported. Use `x=0cm` minimum |
| PPT `shape[1]` for content | `shape[1]` is usually the title placeholder. Use `shape[2]+` |
| Guessing property names | Run `officecli <format> set <element>` to see exact names |
| Editing an open file | Close the file in Office/WPS first |
| `\n` in shell strings | Use `\\n` for newlines in `--prop text="..."` |
| Unquoted paths | Always single-quote: `'/slide[1]'` to prevent shell glob |

## Full Reference

For the complete command reference (L1/L2/L3 layers, pivot tables, raw XML, MCP server, specialized sub-skills):

```bash
curl -fsSL https://officecli.ai/SKILL.md
```

Or see the cached reference at `.agent/skills/office-cli/references/upstream-SKILL.md`.

## Specialized Sub-Skills

For complex scenarios, OfficeCLI provides dedicated skill files:

| Skill | Use Case |
|-------|----------|
| `officecli-pptx` | General slide decks |
| `officecli-pitch-deck` | Investor/sales pitch decks with charts |
| `morph-ppt` | Morph-animated cinematic presentations |
| `officecli-docx` | Word reports, letters, memos |
| `officecli-academic-paper` | Academic papers with TOC, equations, bibliography |
| `officecli-xlsx` | Financial models, trackers, formulas |
| `officecli-data-dashboard` | CSV/data → Excel dashboards with charts |

Load these with: `curl -fsSL https://officecli.ai/skills/<name>/SKILL.md`

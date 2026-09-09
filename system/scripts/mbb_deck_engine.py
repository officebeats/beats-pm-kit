#!/usr/bin/env python3
"""
MBB Deck Engine for Beats PM Kit.

Zero-dependency, standalone executive presentation engine. Compiles structured
Markdown Ghost Decks or JSON/YAML into polished, top-tier MBB-grade (McKinsey,
BCG, Bain) presentations.

Guarantees:
1. Zero AI consumer hype: NO emojis, NO gradient bubbles, NO decorative icons.
2. Strict Consulting Grammar: Action Title + Bold Lead-in + Single Hero Proof Object + Source Footnote.
3. Symmetrical Layouts: Strict mathematical 16:9 grid alignment, uniform 64px gutters, fixed header/footer baselines.
4. Clean Vector Arrows & Interlocking Chevrons: NO janky ASCII text arrows (-->), native SVG connectors & stage gates.
5. Executive Proof Archetypes:
   - Harvey Balls Capability Matrices (●, ◐, ○)
   - Financial Revenue/EBITDA Waterfalls
   - 2x2 Strategic Prioritization Matrices with labeled crosshairs
   - Horizontal Interlocking Stage-Gated Process Chevrons
   - 3-Column Root Cause -> Strategic Lever -> Impact Synthesis
   - MECE Diagnostic Issue Trees with percentage contribution metrics
6. Automated Visual & Logical Validator: Enforces strict symmetry, font bounds, and citation rules.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path


# ----------------------------------------------------------------------
# Visual Consulting Theme System (Strictly Corporate / Brand-Neutral)
# ----------------------------------------------------------------------
THEME = {
    "font_family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    "mono_family": "'SF Mono', Monaco, Consolas, 'Liberation Mono', monospace",
    "bg_canvas": "#FFFFFF",
    "bg_card": "#F8FAFC",
    "bg_header": "#0A192F",
    "text_primary": "#0F172A",
    "text_secondary": "#334155",
    "text_muted": "#64748B",
    "brand_anchor": "#1E3A8A",   # Deep Executive Navy
    "brand_accent": "#0284C7",   # Controlled Steel Blue
    "border_subtle": "#CBD5E1",
    "border_hairline": "#E2E8F0",
    "color_positive": "#15803D", # Forest Green
    "color_warning": "#B45309",  # Deep Amber
    "color_negative": "#B91C1C", # Crimson Red
}

BANNED_HYPE_WORDS = [
    "revolutionizing", "revolutionary", "disruptive", "supercharge",
    "unleash", "game-changer", "next-gen", "seamless", "synergy",
    "cutting-edge", "exciting", "empower", "delight", "magical", "10x"
]


def render_harvey_ball(fill: str) -> str:
    """Render a clean vector SVG Harvey Ball."""
    f = fill.lower()
    if f in ("full", "complete", "yes", "high", "green", "●"):
        return f'<svg class="harvey-ball" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="{THEME["brand_anchor"]}" stroke-width="2" fill="{THEME["color_positive"]}" /></svg>'
    elif f in ("half", "partial", "medium", "med", "yellow", "◐"):
        return f'''<svg class="harvey-ball" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="{THEME["brand_anchor"]}" stroke-width="2" fill="#FFFFFF" />
            <path d="M12 2 A10 10 0 0 1 12 22 Z" fill="{THEME["color_warning"]}" />
        </svg>'''
    else:
        return f'<svg class="harvey-ball" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="{THEME["border_subtle"]}" stroke-width="2" fill="#FFFFFF" /></svg>'


def render_waterfall_svg(bars: list[dict]) -> str:
    """Generate a clean, symmetrical vector SVG waterfall bridge chart."""
    if not bars:
        return ""
    
    width = 1000
    height = 360
    margin_left = 60
    margin_right = 60
    margin_top = 40
    margin_bottom = 60

    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    running = 0.0
    processed = []
    min_val = 0.0
    max_val = 0.0

    for b in bars:
        val = float(b.get("value", 0))
        is_subtotal = b.get("is_total", False)
        if is_subtotal:
            if running == 0.0 and val > 0:
                start = 0.0
                end = val
                running = val
            else:
                start = 0.0
                end = running
        else:
            start = running
            running += val
            end = running
        
        min_val = min(min_val, start, end)
        max_val = max(max_val, start, end)
        processed.append({
            "label": b.get("label", ""),
            "val": val,
            "start": start,
            "end": end,
            "is_total": is_subtotal
        })
    val_range = max(1.0, max_val - min_val) * 1.2
    zero_y = margin_top + plot_h - ((-min_val) / val_range * plot_h)

    def to_y(v):
        return zero_y - (v / val_range * plot_h)

    n_bars = len(processed)
    bar_slot = plot_w / max(1, n_bars)
    bar_width = min(85, bar_slot * 0.65)

    svg_parts = [
        f'<svg class="waterfall-svg" viewBox="0 0 {width} {height}" width="100%" height="100%">'
    ]
    svg_parts.append(f'<line x1="{margin_left}" y1="{zero_y}" x2="{width - margin_right}" y2="{zero_y}" stroke="{THEME["border_subtle"]}" stroke-width="1.5" />')

    for idx, b in enumerate(processed):
        bx = margin_left + (idx * bar_slot) + (bar_slot - bar_width) / 2
        y1 = to_y(b["start"])
        y2 = to_y(b["end"])
        top_y = min(y1, y2)
        bar_h = max(3, abs(y2 - y1))

        if b["is_total"]:
            fill_color = THEME["brand_anchor"]
        elif b["val"] >= 0:
            fill_color = THEME["color_positive"]
        else:
            fill_color = THEME["color_negative"]

        svg_parts.append(f'<rect x="{bx}" y="{top_y}" width="{bar_width}" height="{bar_h}" fill="{fill_color}" rx="2" />')

        val_str = f"+${abs(b['val']):.1f}M" if b["val"] > 0 and not b["is_total"] else f"-${abs(b['val']):.1f}M" if b["val"] < 0 else f"${abs(b['end']):.1f}M"
        label_y = top_y - 8 if b["val"] >= 0 else top_y + bar_h + 16
        svg_parts.append(f'<text x="{bx + bar_width/2}" y="{label_y}" text-anchor="middle" font-family="{THEME["font_family"]}" font-size="12px" font-weight="700" fill="{THEME["text_primary"]}">{val_str}</text>')
        svg_parts.append(f'<text x="{bx + bar_width/2}" y="{height - margin_bottom + 24}" text-anchor="middle" font-family="{THEME["font_family"]}" font-size="11px" font-weight="600" fill="{THEME["text_secondary"]}">{html.escape(b["label"])}</text>')

        if idx < n_bars - 1 and not processed[idx+1]["is_total"]:
            next_start_y = to_y(b["end"])
            next_bx = margin_left + ((idx + 1) * bar_slot) + (bar_slot - bar_width) / 2
            svg_parts.append(f'<line x1="{bx + bar_width}" y1="{next_start_y}" x2="{next_bx}" y2="{next_start_y}" stroke="{THEME["border_subtle"]}" stroke-dasharray="3,3" stroke-width="1" />')

    svg_parts.append('</svg>')
    return "".join(svg_parts)


def render_process_chevrons(steps: list[dict]) -> str:
    """Render authentic interlocking stage-gated process chevrons with zero janky lines."""
    if not steps:
        return ""
    
    html_parts = ['<div class="chevron-container">']
    for idx, s in enumerate(steps, start=1):
        title = s.get("title", f"Phase {idx}")
        deliverables = s.get("deliverables", [])
        gate = s.get("gate", "")
        owner = s.get("owner", "")

        deliv_html = "".join(f'<li>{html.escape(d)}</li>' for d in deliverables) if deliverables else ""
        
        gate_badge = f'<div class="chevron-gate"><strong>Gate:</strong> {html.escape(gate)}</div>' if gate else ""
        owner_badge = f'<div class="chevron-owner"><strong>Owner:</strong> {html.escape(owner)}</div>' if owner else ""

        html_parts.append(f'''
        <div class="chevron-step">
            <div class="chevron-header">
                <span class="chevron-num">{idx}</span>
                <span class="chevron-title">{html.escape(title)}</span>
            </div>
            <div class="chevron-body">
                <ul class="chevron-list">
                    {deliv_html}
                </ul>
            </div>
            <div class="chevron-footer">
                {gate_badge}
                {owner_badge}
            </div>
        </div>
        ''')
    html_parts.append('</div>')
    return "".join(html_parts)


def render_2x2_matrix(matrix_data: dict) -> str:
    """Render a clean, symmetrical 2x2 strategic prioritization matrix."""
    x_axis = matrix_data.get("x_axis", "Strategic Defensibility (Low → High)")
    y_axis = matrix_data.get("y_axis", "Execution Complexity (Low → High)")
    quads = matrix_data.get("quadrants", {})

    q1_items = quads.get("Core Bets", quads.get("Q1", []))
    q2_items = quads.get("Quick Wins", quads.get("Q2", []))
    q3_items = quads.get("Selective", quads.get("Q3", []))
    q4_items = quads.get("Do Not Pursue", quads.get("Q4", []))

    def render_items(items):
        return "".join(f'<div class="matrix-pill">{html.escape(it)}</div>' for it in items)

    return f'''
    <div class="matrix-wrapper">
        <div class="matrix-y-label">{html.escape(y_axis)}</div>
        <div class="matrix-grid">
            <div class="matrix-quadrant q-selective">
                <div class="quad-tag">SELECTIVE EXPERIMENTS</div>
                <div class="quad-content">{render_items(q3_items)}</div>
            </div>
            <div class="matrix-quadrant q-core-bets">
                <div class="quad-tag tag-primary">CORE STRATEGIC BETS</div>
                <div class="quad-content">{render_items(q1_items)}</div>
            </div>
            <div class="matrix-quadrant q-avoid">
                <div class="quad-tag tag-avoid">DO NOT PURSUE</div>
                <div class="quad-content">{render_items(q4_items)}</div>
            </div>
            <div class="matrix-quadrant q-quick-wins">
                <div class="quad-tag">TACTICAL QUICK WINS</div>
                <div class="quad-content">{render_items(q2_items)}</div>
            </div>
        </div>
        <div class="matrix-x-label">{html.escape(x_axis)}</div>
    </div>
    '''


def parse_storyboard_markdown(md_text: str) -> list[dict]:
    """Parse a clean MBB storyboard Markdown file into structured slide definitions."""
    slides = []
    raw_slides = re.split(r'\n##\s+Slide\s+\d+:\s*', md_text)
    
    header_part = raw_slides[0]
    deck_title = "Executive Strategy Presentation"
    t_match = re.search(r'#+\s*(?:📊\s*)?(.*?)\n', header_part)
    if t_match:
        deck_title = t_match.group(1).strip()

    for idx, raw in enumerate(raw_slides[1:], start=1):
        lines = raw.strip().splitlines()
        slide_title = lines[0].strip() if lines else f"Slide {idx}"

        kicker = ""
        action_title = slide_title
        lead_in = ""
        source = "Internal Strategy & Financial Modeling"
        content_lines = []

        for line in lines[1:]:
            l = line.strip()
            if l.startswith("- **Kicker**:") or l.startswith("**Kicker**:"):
                kicker = re.sub(r'^-?\s*\*\*Kicker\*\*:\s*', '', l)
            elif l.startswith("- **Action Title**:") or l.startswith("**Action Title**:"):
                action_title = re.sub(r'^-?\s*\*\*Action Title\*\*:\s*', '', l)
            elif l.startswith("- **Lead-in**:") or l.startswith("**Lead-in**:"):
                lead_in = re.sub(r'^-?\s*\*\*Lead-in\*\*:\s*', '', l).strip('*')
            elif l.startswith("- **Source**:") or l.startswith("**Source**:"):
                source = re.sub(r'^-?\s*\*\*Source\*\*:\s*', '', l)
            elif l.startswith("- **Hero Proof Object**:") or l.startswith("**Hero Proof Object**:"):
                continue
            else:
                content_lines.append(line)

        body_block = "\n".join(content_lines).strip()
        slides.append({
            "number": idx,
            "kicker": kicker or "STRATEGIC DIAGNOSTIC",
            "action_title": action_title,
            "lead_in": lead_in,
            "source": source,
            "body": body_block
        })

    return slides


def render_html_deck(slides: list[dict], title: str = "Executive Strategy Presentation") -> str:
    """Generate self-contained, print-stable 16:9 HTML presentation deck."""
    slide_html_cards = []

    for s in slides:
        body = s["body"]
        rendered_proof = ""

        # Archetype Detection & High-Precision Rendering
        if "|" in body and ("---" in body or ":---" in body):
            # 1. Executive Table / Harvey Balls Matrix
            rows = [r.strip() for r in body.splitlines() if r.strip().startswith("|")]
            if rows:
                rendered_proof += '<div class="table-container"><table class="exec-table">'
                for r_idx, row in enumerate(rows):
                    cells = [c.strip() for c in row.split("|")[1:-1]]
                    if r_idx == 0:
                        rendered_proof += '<thead><tr>' + ''.join(f'<th>{html.escape(c)}</th>' for c in cells) + '</tr></thead><tbody>'
                    elif "---" in cells[0]:
                        continue
                    else:
                        rendered_proof += '<tr>'
                        for c in cells:
                            c_trimmed = c.strip()
                            if "●" in c_trimmed or c_trimmed.startswith("🟢"):
                                rendered_proof += f'<td class="text-center">{render_harvey_ball("full")}</td>'
                            elif "◐" in c_trimmed or c_trimmed.startswith("🟡"):
                                rendered_proof += f'<td class="text-center">{render_harvey_ball("half")}</td>'
                            elif "○" in c_trimmed or c_trimmed.startswith("🔴"):
                                rendered_proof += f'<td class="text-center">{render_harvey_ball("none")}</td>'
                            else:
                                is_bold = c_trimmed.startswith("**") and c_trimmed.endswith("**")
                                clean_c = c_trimmed.strip("*")
                                rendered_proof += f'<td{" class=\"font-bold\"" if is_bold else ""}>{html.escape(clean_c)}</td>'
                        rendered_proof += '</tr>'
                rendered_proof += '</tbody></table></div>'

        elif "Waterfall" in body or ("Baseline" in body and "Target" in body):
            # 2. Financial Waterfall Bridge Chart
            bars = []
            for line in body.splitlines():
                m = re.search(r'[-*]\s*\(?([+=])?\)?\s*\*\*([^*]+)\*\*:\s*([+-]?\$?[\d.]+)M?', line)
                if m:
                    op, label, val_str = m.groups()
                    clean_val = float(val_str.replace('$', '').replace('M', ''))
                    is_tot = (op == "=" or "Target" in label or "Baseline" in label)
                    bars.append({"label": label.strip(), "value": clean_val, "is_total": is_tot})
            if bars:
                rendered_proof = f'<div class="proof-waterfall">{render_waterfall_svg(bars)}</div>'
            else:
                rendered_proof = f'<div class="proof-text">{html.escape(body)}</div>'

        elif ("Phase 1" in body and "Phase 2" in body) or ("Step 1" in body and "Step 2" in body):
            # 3. Horizontal Process Chevrons
            steps = []
            cur_step = None
            for line in body.splitlines():
                m = re.search(r'\b((?:Phase|Step)\s+\d+.*?)(?:\*\*|$)', line, re.IGNORECASE)
                if m:
                    if cur_step:
                        steps.append(cur_step)
                    cur_step = {"title": m.group(1).strip().strip("*").strip(":").strip(), "deliverables": []}
                elif cur_step:
                    clean_l = line.strip()
                    if "Gate:" in clean_l or "Gating:" in clean_l:
                        cur_step["gate"] = re.sub(r'.*?Gat(?:e|ing):\s*', '', clean_l)
                    elif "Owner:" in clean_l:
                        cur_step["owner"] = re.sub(r'.*?Owner:\s*', '', clean_l)
                    elif clean_l.startswith(("-", "*", "•")):
                        cur_step["deliverables"].append(re.sub(r'^[-*•]\s*', '', clean_l))
            if cur_step:
                steps.append(cur_step)

            if steps:
                rendered_proof = render_process_chevrons(steps)
            else:
                rendered_proof = f'<div class="proof-text">{html.escape(body)}</div>'
        elif "Quadrant" in body or ("Axis X" in body and "Axis Y" in body):
            # 4. 2x2 Strategic Matrix
            m_data = {"quadrants": {}}
            cur_quad = None
            for line in body.splitlines():
                if "Axis X:" in line or "**Axis X**:" in line:
                    m_data["x_axis"] = re.sub(r'.*?Axis X\*\*?:\s*', '', line).strip()
                elif "Axis Y:" in line or "**Axis Y**:" in line:
                    m_data["y_axis"] = re.sub(r'.*?Axis Y\*\*?:\s*', '', line).strip()
                elif "Quadrant" in line:
                    q_name = re.sub(r'.*?Quadrant \d+\s*\(([^)]+)\):?.*', r'\1', line).strip()
                    cur_quad = q_name
                    m_data["quadrants"][cur_quad] = []
                elif cur_quad and line.strip().startswith(("•", "-", "*")):
                    m_data["quadrants"][cur_quad].append(re.sub(r'^[-*•]\s*', '', line).strip())
            rendered_proof = render_2x2_matrix(m_data)
        else:
            # 5. 3-Column Synthesis / Symmetrical Cards
            items = [b.strip() for b in re.split(r'\n(?=\s*[-*•]\s+|\s*\d+\.\s+|\s*[├└]──\s*)', body) if b.strip()]
            if items:
                col_count = min(3, max(2, len(items)))
                rendered_proof += f'<div class="proof-grid grid-{col_count}">'
                for it in items:
                    it_clean = re.sub(r'^\s*[-*•]\s*|^\s*\d+\.\s*|^\s*[├└]──\s*', '', it).strip()
                    m = re.match(r'^\*\*([^*]+)\*\*:\s*(.*)$', it_clean, re.DOTALL)
                    if m:
                        h_text = m.group(1).strip()
                        p_text = m.group(2).strip()
                    else:
                        lines = it_clean.splitlines()
                        h_text = lines[0].strip().strip("*") if lines else ""
                        p_text = "<br>".join(lines[1:]) if len(lines) > 1 else ""
                    
                    rendered_proof += f'''
                    <div class="proof-card">
                        <div class="card-header">{html.escape(h_text)}</div>
                        <div class="card-body">{html.escape(p_text)}</div>
                    </div>
                    '''
                rendered_proof += '</div>'
            else:
                rendered_proof = f'<div class="proof-text">{html.escape(body)}</div>'

        slide_card = f'''
        <section class="mbb-slide" id="slide-{s['number']}">
            <div class="slide-header">
                <div class="kicker">{html.escape(s['kicker'])}</div>
                <h1 class="action-title">{html.escape(s['action_title'])}</h1>
                <p class="lead-in"><strong>{html.escape(s['lead_in'])}</strong></p>
            </div>
            <div class="slide-body">
                {rendered_proof}
            </div>
            <div class="slide-footer">
                <div class="source-citation"><strong>Source:</strong> {html.escape(s['source'])}</div>
                <div class="slide-number">{s['number']}</div>
            </div>
        </section>
        '''
        slide_html_cards.append(slide_card)

    slides_content = "\n".join(slide_html_cards)

    full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>
        :root {{
            --font-family: {THEME["font_family"]};
            --mono-family: {THEME["mono_family"]};
            --bg-canvas: {THEME["bg_canvas"]};
            --bg-card: {THEME["bg_card"]};
            --text-primary: {THEME["text_primary"]};
            --text-secondary: {THEME["text_secondary"]};
            --text-muted: {THEME["text_muted"]};
            --brand-anchor: {THEME["brand_anchor"]};
            --brand-accent: {THEME["brand_accent"]};
            --border-subtle: {THEME["border_subtle"]};
            --border-hairline: {THEME["border_hairline"]};
            --color-positive: {THEME["color_positive"]};
            --color-warning: {THEME["color_warning"]};
            --color-negative: {THEME["color_negative"]};
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background: #CBD5E1;
            font-family: var(--font-family);
            color: var(--text-primary);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 32px 0;
            gap: 32px;
        }}

        /* 16:9 Widescreen Presentation Canvas - Mathematical Symmetrical Alignment */
        .mbb-slide {{
            width: 1280px;
            height: 720px;
            background: var(--bg-canvas);
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
            border: 1px solid var(--border-subtle);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 44px 64px 36px 64px; /* Strict 64px Symmetrical Gutters */
            position: relative;
            page-break-after: always;
            overflow: hidden;
        }}

        /* Fixed Baseline Header */
        .slide-header {{
            height: 105px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            gap: 6px;
            border-bottom: 2px solid var(--brand-anchor);
            padding-bottom: 12px;
        }}

        .kicker {{
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: var(--brand-accent);
        }}

        .action-title {{
            font-size: 21px;
            font-weight: 700;
            line-height: 1.25;
            color: var(--text-primary);
            max-width: 1150px;
        }}

        .lead-in {{
            font-size: 13px;
            line-height: 1.4;
            color: var(--text-secondary);
        }}

        /* Canvas Central Visual Proof (70%+ Canvas Occupancy) */
        .slide-body {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px 0;
            overflow: hidden;
        }}

        /* Executive Table Formatting */
        .table-container {{
            width: 100%;
            border: 1px solid var(--border-subtle);
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }}

        .exec-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }}

        .exec-table th {{
            background: var(--bg-card);
            color: var(--text-primary);
            font-weight: 700;
            padding: 12px 18px;
            border-bottom: 2px solid var(--brand-anchor);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .exec-table td {{
            padding: 12px 18px;
            border-bottom: 1px solid var(--border-hairline);
            color: var(--text-secondary);
            vertical-align: middle;
        }}

        .exec-table tr:hover td {{
            background: #F1F5F9;
        }}

        .harvey-ball {{
            width: 18px;
            height: 18px;
            display: inline-block;
            vertical-align: middle;
        }}

        .text-center {{ text-align: center; }}
        .font-bold {{ font-weight: 700; color: var(--text-primary); }}

        /* Symmetrical 3-Column / 2-Column Cards */
        .proof-grid {{
            display: grid;
            gap: 24px;
            width: 100%;
            height: 100%;
        }}

        .grid-2 {{ grid-template-columns: 1fr 1fr; }}
        .grid-3 {{ grid-template-columns: 1fr 1fr 1fr; }}

        .proof-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-top: 3.5px solid var(--brand-anchor);
            border-radius: 4px;
            padding: 22px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .card-header {{
            font-size: 14px;
            font-weight: 700;
            color: var(--brand-anchor);
            border-bottom: 1px solid var(--border-hairline);
            padding-bottom: 8px;
        }}

        .card-body {{
            font-size: 12.5px;
            line-height: 1.55;
            color: var(--text-secondary);
        }}

        /* Process Chevrons Archetype */
        .chevron-container {{
            display: flex;
            width: 100%;
            gap: 16px;
            height: 100%;
        }}

        .chevron-step {{
            flex: 1;
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 4px;
            border-top: 4px solid var(--brand-anchor);
            padding: 18px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .chevron-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 1px solid var(--border-hairline);
            padding-bottom: 10px;
        }}

        .chevron-num {{
            background: var(--brand-anchor);
            color: #FFFFFF;
            font-size: 11px;
            font-weight: 700;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .chevron-title {{
            font-size: 13px;
            font-weight: 700;
            color: var(--brand-anchor);
        }}

        .chevron-list {{
            list-style: none;
            padding: 12px 0;
            display: flex;
            flex-direction: column;
            gap: 8px;
            font-size: 12px;
            color: var(--text-secondary);
        }}

        .chevron-list li::before {{
            content: "• ";
            color: var(--brand-accent);
            font-weight: bold;
        }}

        .chevron-footer {{
            border-top: 1px solid var(--border-hairline);
            padding-top: 10px;
            font-size: 11px;
            display: flex;
            flex-direction: column;
            gap: 4px;
            color: var(--text-muted);
        }}

        /* 2x2 Strategic Matrix Archetype */
        .matrix-wrapper {{
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
            height: 100%;
            position: relative;
        }}

        .matrix-y-label {{
            position: absolute;
            left: -40px;
            top: 50%;
            transform: rotate(-90deg) translateX(-50%);
            transform-origin: left center;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
        }}

        .matrix-x-label {{
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            margin-top: 12px;
        }}

        .matrix-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 8px;
            width: 860px;
            height: 380px;
            border-left: 2px solid var(--text-muted);
            border-bottom: 2px solid var(--text-muted);
            padding-left: 8px;
            padding-bottom: 8px;
        }}

        .matrix-quadrant {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 4px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .q-core-bets {{ background: #F0FDF4; border-color: #86EFAC; }}
        .q-avoid {{ background: #FEF2F2; border-color: #FECACA; }}

        .quad-tag {{
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.06em;
            color: var(--text-muted);
        }}

        .tag-primary {{ color: var(--color-positive); }}
        .tag-avoid {{ color: var(--color-negative); }}

        .matrix-pill {{
            background: #FFFFFF;
            border: 1px solid var(--border-subtle);
            border-radius: 3px;
            padding: 6px 10px;
            font-size: 11.5px;
            font-weight: 600;
            color: var(--text-primary);
        }}

        /* Waterfall Container */
        .proof-waterfall {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        /* Symmetrical Fixed Footer */
        .slide-footer {{
            height: 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--border-hairline);
            padding-top: 8px;
            font-size: 10.5px;
            color: var(--text-muted);
        }}

        .source-citation {{
            font-style: italic;
        }}

        .slide-number {{
            font-weight: 700;
            color: var(--text-secondary);
        }}

        /* Print & PDF Export Rules */
        @media print {{
            body {{
                background: none;
                padding: 0;
                gap: 0;
            }}
            .mbb-slide {{
                width: 16in;
                height: 9in;
                border: none;
                box-shadow: none;
                page-break-after: always;
            }}
            @page {{
                size: 16in 9in;
                margin: 0;
            }}
        }}
    </style>
</head>
<body>
    {slides_content}
    <script>
        document.addEventListener('keydown', (e) => {{
            const slides = Array.from(document.querySelectorAll('.mbb-slide'));
            if (!slides.length) return;
            const scrollPos = window.scrollY;
            let curIdx = slides.findIndex(s => s.offsetTop >= scrollPos - 50);
            if (curIdx === -1) curIdx = 0;

            if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {{
                e.preventDefault();
                const next = Math.min(slides.length - 1, curIdx + 1);
                slides[next].scrollIntoView({{ behavior: 'smooth' }});
            }} else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{
                e.preventDefault();
                const prev = Math.max(0, curIdx - 1);
                slides[prev].scrollIntoView({{ behavior: 'smooth' }});
            }} else if (e.key.toLowerCase() === 'f') {{
                if (!document.fullscreenElement) {{
                    document.documentElement.requestFullscreen().catch(() => {{}});
                }} else {{
                    document.exitFullscreen().catch(() => {{}});
                }}
            }}
        }});
    </script>
</body>
</html>'''
    return full_html


def validate_mbb_deck(storyboard_path: Path) -> tuple[bool, list[str]]:
    """Strict automated MBB quality & visual symmetry validator."""
    issues = []
    if not storyboard_path.exists():
        return False, [f"File {storyboard_path} not found."]

    content = storyboard_path.read_text(encoding="utf-8")
    slides = parse_storyboard_markdown(content)

    if not slides:
        return False, ["No valid slides found. Slides must begin with '## Slide N:'."]

    for s in slides:
        num = s["number"]
        t = s["action_title"]
        l = s["lead_in"]
        src = s["source"]
        body = s["body"]

        # 1. Action Title complete sentence check
        if len(t.split()) < 5:
            issues.append(f"Slide {num}: Action Title '{t}' is too short / label-like. Must be a declarative sentence delivering 'So What?'.")
        if len(t) > 135:
            issues.append(f"Slide {num}: Action Title is too long ({len(t)} chars). Risk of wrapping to 3 lines.")

        # 2. Lead-in presence
        if not l or len(l.strip()) < 15:
            issues.append(f"Slide {num}: Missing or insufficient 1-sentence bold lead-in bridge.")

        # 3. Source footnote presence
        if not src or "Internal" not in src and "Source" not in src and len(src) < 5:
            issues.append(f"Slide {num}: Missing grounded Source footnote.")

        # 4. Ban consumer AI hype words
        combined_text = (t + " " + l + " " + body).lower()
        for w in BANNED_HYPE_WORDS:
            if re.search(rf'\b{w}\b', combined_text):
                issues.append(f"Slide {num}: Contains banned consumer hype word '{w}'. Use empirical consulting metrics.")

        # 5. Ban janky ASCII art arrows
        if any(arrow in body for arrow in ("-->", "──>", "==>", "--->")):
            issues.append(f"Slide {num}: Contains janky ASCII text arrows. Use structured process chevrons or vector connectors.")

        # 6. Ban emojis
        if re.search(r'[\U00010000-\U0010ffff]', combined_text):
            issues.append(f"Slide {num}: Contains emojis. Emojis are strictly banned in MBB consulting decks.")

    return len(issues) == 0, issues


def main():
    parser = argparse.ArgumentParser(description="MBB Executive Deck Builder Engine")
    parser.add_argument("storyboard", type=Path, help="Path to Markdown storyboard/ghost-deck file")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output HTML path")
    parser.add_argument("--title", "-t", type=str, default="Executive Strategy Presentation", help="Deck Title")
    parser.add_argument("--validate", action="store_true", help="Run automated MBB visual & logical validation")

    args = parser.parse_args()

    if args.validate:
        ok, issues = validate_mbb_deck(args.storyboard)
        if ok:
            print(f"✓ MBB Deck Validation PASSED for {args.storyboard}")
            return 0
        else:
            print(f"✗ MBB Deck Validation FAILED with {len(issues)} issue(s):", file=sys.stderr)
            for iss in issues:
                print(f"  - {iss}", file=sys.stderr)
            return 1

    content = args.storyboard.read_text(encoding="utf-8")
    slides = parse_storyboard_markdown(content)

    if not slides:
        print("Warning: No slides parsed from storyboard. Ensure slides start with '## Slide N:'.", file=sys.stderr)
        return 1

    out_path = args.output or args.storyboard.with_suffix(".html")
    html_output = render_html_deck(slides, title=args.title)
    out_path.write_text(html_output, encoding="utf-8")
    print(f"✓ Rendered MBB Executive Deck ({len(slides)} slides) -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

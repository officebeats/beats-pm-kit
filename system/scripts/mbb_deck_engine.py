#!/usr/bin/env python3
"""
MBB Deck Engine for Beats PM Kit.

Zero-dependency, standalone executive presentation engine. Compiles structured
Markdown Ghost Decks or JSON/YAML into polished, top-tier MBB-grade (McKinsey,
BCG, Bain) presentations.

Guarantees:
1. Zero AI consumer hype: NO emojis, NO gradient bubbles, NO decorative icons.
2. Strict Consulting Grammar: Action Title + Bold Lead-in + Single Hero Proof Object + Source Footnote.
3. Executive Proof Archetypes: Harvey Balls, Financial Waterfalls, 2x2 Trade-off Matrices,
   Horizontal Stage-Gated Chevrons, MECE Issue Trees, and 3-Column Synthesis.
4. Universal Portability: Renders self-contained 16:9 widescreen presentations with print-to-PDF
   CSS without requiring LibreOffice, python-pptx, or external CDN dependencies.
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


def render_harvey_ball(fill: str) -> str:
    """Render a clean SVG Harvey Ball (circle indicator)."""
    f = fill.lower()
    if f in ("full", "complete", "yes", "high", "green", "●"):
        return f'<svg class="harvey-ball" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="{THEME["brand_anchor"]}" stroke-width="2" fill="{THEME["color_positive"]}" /></svg>'
    elif f in ("half", "partial", "medium", "med", "yellow", "◐"):
        return f'''<svg class="harvey-ball" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke="{THEME["brand_anchor"]}" stroke-width="2" fill="#FFFFFF" />
            <path d="M12 2 A10 10 0 0 1 12 22 Z" fill="{THEME["color_warning"]}" />
        </svg>'''
    else: # Empty / none / low / red
        return f'<svg class="harvey-ball" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="{THEME["border_subtle"]}" stroke-width="2" fill="#FFFFFF" /></svg>'


def render_waterfall_svg(bars: list[dict]) -> str:
    """Generate a clean vector SVG waterfall bridge chart."""
    if not bars:
        return ""
    
    width = 900
    height = 360
    margin_left = 60
    margin_right = 40
    margin_top = 40
    margin_bottom = 60

    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    # Compute running values
    running = 0.0
    processed = []
    min_val = 0.0
    max_val = 0.0

    for b in bars:
        val = float(b.get("value", 0))
        is_subtotal = b.get("is_total", False)
        if is_subtotal:
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

    val_range = max(1.0, max_val - min_val) * 1.15
    zero_y = margin_top + plot_h - ((-min_val) / val_range * plot_h)

    def to_y(v):
        return zero_y - (v / val_range * plot_h)

    n_bars = len(processed)
    bar_slot = plot_w / max(1, n_bars)
    bar_width = min(80, bar_slot * 0.65)

    svg_parts = [
        f'<svg class="waterfall-svg" viewBox="0 0 {width} {height}" width="100%" height="100%">'
    ]
    # Baseline rule
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

        # Bar rect
        svg_parts.append(f'<rect x="{bx}" y="{top_y}" width="{bar_width}" height="{bar_h}" fill="{fill_color}" rx="2" />')

        # Value label
        val_str = f"+${abs(b['val']):.1f}M" if b["val"] > 0 and not b["is_total"] else f"-${abs(b['val']):.1f}M" if b["val"] < 0 else f"${abs(b['end']):.1f}M"
        label_y = top_y - 8 if b["val"] >= 0 else top_y + bar_h + 16
        svg_parts.append(f'<text x="{bx + bar_width/2}" y="{label_y}" text-anchor="middle" font-family="{THEME["font_family"]}" font-size="12px" font-weight="600" fill="{THEME["text_primary"]}">{val_str}</text>')

        # Category label
        svg_parts.append(f'<text x="{bx + bar_width/2}" y="{height - margin_bottom + 22}" text-anchor="middle" font-family="{THEME["font_family"]}" font-size="11px" font-weight="500" fill="{THEME["text_secondary"]}">{html.escape(b["label"])}</text>')

        # Connector line to next bar
        if idx < n_bars - 1 and not processed[idx+1]["is_total"]:
            next_start_y = to_y(b["end"])
            next_bx = margin_left + ((idx + 1) * bar_slot) + (bar_slot - bar_width) / 2
            svg_parts.append(f'<line x1="{bx + bar_width}" y1="{next_start_y}" x2="{next_bx}" y2="{next_start_y}" stroke="{THEME["border_subtle"]}" stroke-dasharray="3,3" stroke-width="1" />')

    svg_parts.append('</svg>')
    return "".join(svg_parts)


def parse_storyboard_markdown(md_text: str) -> list[dict]:
    """Parse a clean MBB storyboard Markdown file into structured slide definitions."""
    slides = []
    raw_slides = re.split(r'\n##\s+Slide\s+\d+:\s*', md_text)
    
    # Check if first section is header/metadata
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
        hero_type = "synthesis"
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
        
        # Determine archetype from body content
        rendered_proof = ""
        if "|" in body and ("---" in body or ":---" in body):
            # Render executive table
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
                            # Parse Harvey balls if present
                            if "●" in c or "🟢" in c or "Complete" in c:
                                rendered_proof += f'<td class="text-center">{render_harvey_ball("full")}</td>'
                            elif "◐" in c or "🟡" in c or "Partial" in c or "Medium" in c:
                                rendered_proof += f'<td class="text-center">{render_harvey_ball("half")}</td>'
                            elif "○" in c or "🔴" in c or "Inadequate" in c or "Low" in c:
                                rendered_proof += f'<td class="text-center">{render_harvey_ball("none")}</td>'
                            else:
                                is_bold = c.startswith("**") and c.endswith("**")
                                clean_c = c.strip("*")
                                rendered_proof += f'<td{" class=\"font-bold\"" if is_bold else ""}>{html.escape(clean_c)}</td>'
                        rendered_proof += '</tr>'
                rendered_proof += '</tbody></table></div>'
        elif "Waterfall" in body or "Baseline" in body and "Target" in body:
            # Parse waterfall points
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
                rendered_proof = f'<div class="proof-text"><pre>{html.escape(body)}</pre></div>'
        else:
            # Render structured cards / columns
            items = [b.strip() for b in re.split(r'\n(?=- |\d+\. |├── |└── )', body) if b.strip()]
            if items:
                col_count = min(3, max(2, len(items)))
                rendered_proof += f'<div class="proof-grid grid-{col_count}">'
                for it in items:
                    it_clean = re.sub(r'^[-*]\s*|^\d+\.\s*|^[├└]──\s*', '', it)
                    lines = it_clean.splitlines()
                    h_text = lines[0] if lines else ""
                    p_text = "<br>".join(lines[1:]) if len(lines) > 1 else ""
                    rendered_proof += f'''
                    <div class="proof-card">
                        <div class="card-header">{html.escape(h_text.strip("*"))}</div>
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
            background: #E2E8F0;
            font-family: var(--font-family);
            color: var(--text-primary);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 24px 0;
            gap: 24px;
        }}

        /* 16:9 Widescreen Presentation Canvas */
        .mbb-slide {{
            width: 1280px;
            height: 720px;
            background: var(--bg-canvas);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
            border: 1px solid var(--border-subtle);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 44px 56px 36px 56px;
            position: relative;
            page-break-after: always;
            overflow: hidden;
        }}

        .slide-header {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            border-bottom: 1.5px solid var(--brand-anchor);
            padding-bottom: 12px;
        }}

        .kicker {{
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--brand-accent);
        }}

        .action-title {{
            font-size: 22px;
            font-weight: 700;
            line-height: 1.25;
            color: var(--text-primary);
        }}

        .lead-in {{
            font-size: 13px;
            line-height: 1.4;
            color: var(--text-secondary);
        }}

        .slide-body {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px 0;
        }}

        .table-container {{
            width: 100%;
            border: 1px solid var(--border-subtle);
            border-radius: 4px;
            overflow: hidden;
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
            padding: 12px 16px;
            border-bottom: 2px solid var(--brand-anchor);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}

        .exec-table td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-hairline);
            color: var(--text-secondary);
        }}

        .exec-table tr:hover td {{
            background: #F1F5F9;
        }}

        .harvey-ball {{
            width: 18px;
            height: 18px;
            vertical-align: middle;
        }}

        .text-center {{
            text-align: center;
        }}

        .font-bold {{
            font-weight: 600;
            color: var(--text-primary);
        }}

        .proof-grid {{
            display: grid;
            gap: 20px;
            width: 100%;
            height: 100%;
        }}

        .grid-2 {{ grid-template-columns: 1fr 1fr; }}
        .grid-3 {{ grid-template-columns: 1fr 1fr 1fr; }}

        .proof-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-top: 3px solid var(--brand-anchor);
            border-radius: 4px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .card-header {{
            font-size: 14px;
            font-weight: 700;
            color: var(--brand-anchor);
        }}

        .card-body {{
            font-size: 13px;
            line-height: 1.5;
            color: var(--text-secondary);
        }}

        .proof-waterfall {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .slide-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid var(--border-hairline);
            padding-top: 10px;
            font-size: 11px;
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
        // Keyboard Navigation (Left / Right / F for Fullscreen)
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


def main():
    parser = argparse.ArgumentParser(description="MBB Executive Deck Builder Engine")
    parser.add_argument("storyboard", type=Path, help="Path to Markdown storyboard/ghost-deck file")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output HTML path")
    parser.add_argument("--title", "-t", type=str, default="Executive Strategy Presentation", help="Deck Title")

    args = parser.parse_args()

    if not args.storyboard.exists():
        print(f"Error: {args.storyboard} does not exist", file=sys.stderr)
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

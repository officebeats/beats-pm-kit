#!/usr/bin/env python3
"""First-Time User Experience (FTUE) configuration engine for Beats PM Kit.

Provides fast profile introspection, atomic SETTINGS.md updates,
consulting/multi-client engagement matrix support, and high-tech
terminal matrix glyph ASCII art for interactive onboarding.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

# --- Glyph Matrix Terminal ASCII Art ---

BANNER_MATRIX = r"""
 ▞▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▚
▌   ██████╗ ███████╗ █████╗ ████████╗███████╗   ██████╗ ███╗   ███╗  ▐
▌   ██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔════╝   ██╔══██╗████╗ ████║  ▐
▌   ██████╔╝█████╗  ███████║   ██║   ███████╗   ██████╔╝██╔████╔██║  ▐
▌   ██╔══██╗██╔══╝  ██╔══██║   ██║   ╚════██║   ██╔═══╝ ██║╚██╔╝██║  ▐
▌   ██████╔╝███████╗██║  ██║   ██║   ███████║██╗██║     ██║ ╚═╝ ██║  ▐
▌   ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝╚═╝     ╚═╝     ╚═╝  ▐
▌       [ ◈ B E A T S   P M   K I T  ::  F T U E   O N L I N E ◈ ]   ▐
 ▚▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▞
"""
BANNER_COMPLETE = r"""
 ▞▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▚
▌   ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗   ██████╗  ▐
▌   ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║  ██╔═══██╗ ▐
▌   ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║  ██║   ██║ ▐
▌   ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║  ██║   ██║ ▐
▌   ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║  ╚██████╔╝ ▐
▌   ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝   ╚═════╝  ▐
▌      [ ◈ B E A T S   P M   K I T  ::  S Y S T E M   R E A D Y ◈ ]   ▐
 ▚▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▞
"""

STEP_IDENTITY = r"""
┌──[ STEP 1/3 :: IDENTITY MATRIX ]──────────────────────────────────┐
│ ⌁ Configure local task ownership and boss-request routing.        │
└───────────────────────────────────────────────────────────────────┘
"""

STEP_PRODUCTS = r"""
┌──[ STEP 2/3 :: PRODUCT PORTFOLIO ]────────────────────────────────┐
│ ⌁ Define active products and tags for automated task routing.     │
└───────────────────────────────────────────────────────────────────┘
"""

STEP_CONSULTING_PORTFOLIO = r"""
┌──[ STEP 2/3 :: CLIENT & ENGAGEMENT MATRIX ]───────────────────────┐
│ ⌁ Map consulting firm, client companies, and active projects.     │
│ ⌁ Auto-generates client workspace folders and workstream tags.    │
└───────────────────────────────────────────────────────────────────┘
"""

STEP_TELEMETRY = r"""
┌──[ STEP 3/3 :: EVIDENCE TELEMETRY ]───────────────────────────────┐
│ ⌁ Set up read-only communication sources and meeting transcripts. │
└───────────────────────────────────────────────────────────────────┘
"""

BANNERS = {
    "welcome": BANNER_MATRIX,
    "complete": BANNER_COMPLETE,
    "identity": STEP_IDENTITY,
    "products": STEP_PRODUCTS,
    "consulting_step": STEP_CONSULTING_PORTFOLIO,
    "telemetry": STEP_TELEMETRY,
}


@dataclass
class ProfileStatus:
    exists: bool
    owner: str | None
    role: str | None
    timezone: str | None
    org_type: str = "in-house"  # "in-house" or "consulting"
    firm: str | None = None  # Consulting Firm / Agency
    boss_name: str | None = None
    boss_alias: str | None = None
    client_sponsors: dict[str, str] = field(default_factory=dict)
    products: list[dict[str, str]] = field(default_factory=list)
    clients: list[dict[str, Any]] = field(default_factory=list)
    outlook_window: str | None = None
    teams_window: str | None = None
    slack_window: str | None = None
    granola_intake: str | None = None
    quill_intake: str | None = None
    is_configured: bool = False


def _slugify(name: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", name).strip().lower()
    return re.sub(r"[-\s]+", "-", cleaned)


def _is_placeholder(val: str | None) -> bool:
    if not val:
        return True
    val = val.strip()
    return val.startswith("[") and val.endswith("]")


def parse_clients_input(raw: str | list[Any]) -> list[dict[str, Any]]:
    """Parse flexible consulting client/projects definitions.
    
    Accepts:
      - 'Client A: Project 1, Project 2; Client B: Project 3'
      - Lines: 'Client A: Project 1, Project 2'
      - JSON string or list of dicts
    """
    if isinstance(raw, list):
        results = []
        for item in raw:
            if isinstance(item, dict) and "client" in item:
                client_name = str(item["client"]).strip()
                projects_raw = item.get("projects", [])
                projects = []
                for p in projects_raw:
                    if isinstance(p, dict):
                        projects.append(p)
                    else:
                        p_name = str(p).strip()
                        p_alias = _make_alias(client_name, p_name)
                        projects.append({"name": p_name, "alias": p_alias, "description": f"{client_name} - {p_name}"})
                results.append({
                    "client": client_name,
                    "sponsor": item.get("sponsor"),
                    "projects": projects,
                })
        return results

    if isinstance(raw, str):
        raw = raw.strip()
        if raw.startswith("[") and raw.endswith("]"):
            try:
                data = json.loads(raw)
                return parse_clients_input(data)
            except json.JSONDecodeError:
                pass

        results = []
        # Split by semicolon or newline
        blocks = re.split(r"[;\n]+", raw)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            if ":" in block:
                client_part, projects_part = block.split(":", 1)
                client_name = client_part.strip().replace("**", "")
                p_items = [p.strip().replace("**", "") for p in projects_part.split(",") if p.strip()]
                projects = []
                for p_name in p_items:
                    p_alias = _make_alias(client_name, p_name)
                    projects.append({
                        "name": p_name,
                        "alias": p_alias,
                        "description": f"{client_name} engagement: {p_name}",
                    })
                results.append({
                    "client": client_name,
                    "sponsor": None,
                    "projects": projects,
                })
            else:
                # Just client name, default project
                client_name = block.strip().replace("**", "")
                p_alias = _slugify(client_name)[:6]
                results.append({
                    "client": client_name,
                    "sponsor": None,
                    "projects": [{"name": f"{client_name} Engagement", "alias": p_alias, "description": f"{client_name} core engagement"}],
                })
        return results

    return []


def _make_alias(client: str, project: str) -> str:
    c_part = re.sub(r"[^\w]", "", client).lower()[:4]
    p_part = re.sub(r"[^\w]", "", project).lower()[:4]
    return f"{c_part}-{p_part}" if c_part and p_part else (c_part or p_part or "proj")


def inspect_profile(root: Path = ROOT) -> ProfileStatus:
    settings_file = root / "SETTINGS.md"
    if not settings_file.exists():
        return ProfileStatus(
            exists=False,
            owner=None,
            role=None,
            timezone=None,
            org_type="in-house",
            firm=None,
            boss_name=None,
            boss_alias=None,
            client_sponsors={},
            products=[],
            clients=[],
            outlook_window=None,
            teams_window=None,
            slack_window=None,
            granola_intake=None,
            quill_intake=None,
            is_configured=False,
        )

    text = settings_file.read_text(encoding="utf-8", errors="replace")

    def _extract_field(pattern: str) -> str | None:
        m = re.search(pattern, text, re.MULTILINE)
        if m:
            val = m.group(1).strip()
            return None if _is_placeholder(val) else val
        return None

    owner = _extract_field(r"^-\s+\*\*Owner\*\*:\s*(.*)$")
    role = _extract_field(r"^-\s+\*\*Role\*\*:\s*(.*)$")
    tz = _extract_field(r"^-\s+\*\*Timezone\*\*:\s*(.*)$")
    org_type_raw = _extract_field(r"^-\s+\*\*Organization Type\*\*:\s*(.*)$")
    firm = _extract_field(r"^-\s+\*\*Consulting Firm\*\*:\s*(.*)$")
    boss_name = _extract_field(r"^-\s+\*\*Name\*\*:\s*(.*)$") or _extract_field(r"^-\s+\*\*Internal Boss\*\*:\s*(.*)$")
    boss_alias = _extract_field(r"^-\s+\*\*Alias\*\*:\s*(.*)$")
    outlook = _extract_field(r"^-\s+\*\*Outlook source window\*\*:\s*(.*)$")
    teams = _extract_field(r"^-\s+\*\*Teams source window\*\*:\s*(.*)$")
    slack = _extract_field(r"^-\s+\*\*Slack source window\*\*:\s*(.*)$")
    granola = _extract_field(r"^-\s+\*\*Granola intake\*\*:\s*(.*)$")
    quill = _extract_field(r"^-\s+\*\*Quill intake\*\*:\s*(.*)$")

    client_sponsors: dict[str, str] = {}
    sponsors_raw = _extract_field(r"^-\s+\*\*Client Sponsors\*\*:\s*(.*)$")
    if sponsors_raw:
        for part in re.split(r"[;,]+", sponsors_raw):
            if ":" in part:
                c, s = part.split(":", 1)
                client_sponsors[c.strip()] = s.strip()

    # Extract portfolio table
    products: list[dict[str, str]] = []
    clients: list[dict[str, Any]] = []
    client_map: dict[str, list[dict[str, str]]] = {}

    table_match = re.search(
        r"## 📂 (?:Product|Product & Client|Portfolio).*?\n\|(.*?)\|\n\|[-|\s]+\|\n(.*?)(?=\n---|\n##|\Z)",
        text,
        re.DOTALL,
    )
    if table_match:
        header_cols = [h.strip().lower() for h in table_match.group(1).split("|")]
        has_client_col = any("client" in h for h in header_cols)

        for line in table_match.group(2).strip().splitlines():
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if has_client_col and len(cols) >= 4:
                c_name = cols[0].replace("**", "").strip()
                p_name = cols[1].replace("**", "").strip()
                alias = cols[2].replace("`", "").strip()
                desc = cols[3].strip()
                item = {"name": p_name, "alias": alias, "client": c_name, "description": desc}
                products.append(item)
                client_map.setdefault(c_name, []).append(item)
            elif len(cols) >= 3:
                p_name = cols[0].replace("**", "").strip()
                alias = cols[1].replace("`", "").strip()
                desc = cols[2].strip()
                products.append({"name": p_name, "alias": alias, "description": desc})

    for c_name, c_projs in client_map.items():
        clients.append({
            "client": c_name,
            "sponsor": client_sponsors.get(c_name),
            "projects": c_projs,
        })

    org_type = "consulting" if (firm or clients or (org_type_raw and "consult" in org_type_raw.lower())) else "in-house"
    is_configured = bool(owner and (boss_name or clients))

    return ProfileStatus(
        exists=True,
        owner=owner,
        role=role,
        timezone=tz or "America/Chicago",
        org_type=org_type,
        firm=firm,
        boss_name=boss_name,
        boss_alias=boss_alias,
        client_sponsors=client_sponsors,
        products=products,
        clients=clients,
        outlook_window=outlook,
        teams_window=teams,
        slack_window=slack,
        granola_intake=granola,
        quill_intake=quill,
        is_configured=is_configured,
    )


def seed_consulting_workspace(
    root: Path,
    firm: str | None,
    clients: list[dict[str, Any]],
    client_sponsors: dict[str, str] | None = None,
) -> None:
    """Seed dedicated 8. Clients/<Client>/ folders and workstream notes for consulting users."""
    client_sponsors = client_sponsors or {}

    for c in clients:
        c_name = c["client"]
        c_slug = _slugify(c_name)
        sponsor = c.get("sponsor") or client_sponsors.get(c_name, "TBD")

        client_dir = root / "8. Clients" / c_name
        client_dir.mkdir(parents=True, exist_ok=True)
        (client_dir / "projects").mkdir(parents=True, exist_ok=True)

        overview_file = client_dir / "CLIENT_OVERVIEW.md"
        if not overview_file.exists():
            projs_list = "\n".join(f"- **{p.get('name', 'Engagement')}** (`{p.get('alias', '')}`): {p.get('description', '')}" for p in c.get("projects", []))
            overview_content = f"""---
title: '{c_name} — Client Overview'
client: '{c_name}'
type: client-overview
---

# {c_name} — Client Overview

- **Client Company**: {c_name}
- **Consulting Firm**: {firm or 'Consulting Advisory'}
- **Primary Executive Sponsor**: {sponsor}
- **Created**: Initialized via Beats PM Kit FTUE

---

## Active Engagements & Projects

{projs_list or '- General Advisory'}

---

## Strategic Context & Objectives

> Capture high-level engagement scope, governance cadence, and billing milestones here.
"""
            overview_file.write_text(overview_content, encoding="utf-8")

        # Seed workstream notes in 5. Trackers/workstreams/
        ws_dir = root / "5. Trackers" / "workstreams"
        ws_dir.mkdir(parents=True, exist_ok=True)

        for p in c.get("projects", []):
            p_name = p.get("name", "Project")
            p_slug = _slugify(p_name)
            ws_id = f"{c_slug}-{p_slug}"
            ws_file = ws_dir / f"{ws_id}.md"
            if not ws_file.exists():
                ws_content = f"""---
title: '{c_name} — {p_name}'
workstream: '{ws_id}'
client: '{c_name}'
type: workstream
---

# {c_name} — {p_name}

> Client engagement under [[{c_name}|8. Clients/{c_name}/CLIENT_OVERVIEW.md]].

## Objectives & Deliverables

- **Client**: {c_name}
- **Consulting Firm**: {firm or 'Consulting Advisory'}
- **Executive Sponsor**: {sponsor}

<!-- BEGIN AUTO-EVIDENCE (managed by workstream_moc.py) -->
<!-- END AUTO-EVIDENCE -->
"""
                ws_file.write_text(ws_content, encoding="utf-8")

    # Update 4. People/PEOPLE.md with clients and sponsors
    people_file = root / "4. People" / "PEOPLE.md"
    if people_file.exists():
        people_text = people_file.read_text(encoding="utf-8", errors="replace")
        new_entries = []
        for c in clients:
            c_name = c["client"]
            sponsor = c.get("sponsor") or client_sponsors.get(c_name)
            if sponsor and sponsor not in people_text:
                new_entries.append(f"| **{sponsor}** | Executive Sponsor ({c_name}) | Client Leadership |\n")
        if new_entries:
            people_file.write_text(people_text.rstrip() + "\n" + "".join(new_entries), encoding="utf-8")


def update_profile(
    root: Path = ROOT,
    *,
    owner: str | None = None,
    role: str | None = None,
    timezone: str | None = None,
    org_type: str | None = None,
    firm: str | None = None,
    boss_name: str | None = None,
    boss_alias: str | None = None,
    client_sponsors: dict[str, str] | None = None,
    products: list[dict[str, str]] | None = None,
    clients: list[dict[str, Any]] | None = None,
    outlook: str | None = None,
    teams: str | None = None,
    slack: str | None = None,
    granola: str | None = None,
    quill: str | None = None,
) -> bool:
    settings_file = root / "SETTINGS.md"
    if not settings_file.exists():
        template = root / ".agent" / "templates" / "SETTINGS_TEMPLATE.md"
        if template.exists():
            settings_file.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            return False

    text = settings_file.read_text(encoding="utf-8", errors="replace")

    def _replace_field(field_pattern: str, new_val: str | None) -> None:
        nonlocal text
        if new_val is not None:
            text = re.sub(
                rf"^(-\s+\*\*{field_pattern}\*\*:\s*).*$",
                rf"\g<1>{new_val}",
                text,
                flags=re.MULTILINE,
            )

    _replace_field("Owner", owner)
    _replace_field("Role", role)
    _replace_field("Timezone", timezone)
    _replace_field("Name", boss_name)
    _replace_field("Alias", boss_alias or (boss_name.lower().replace(" ", "") if boss_name else None))
    _replace_field("Outlook source window", outlook)
    _replace_field("Teams source window", teams)
    _replace_field("Slack source window", slack)
    _replace_field("Granola intake", granola)
    _replace_field("Quill intake", quill)

    # Determine organization mode
    is_consulting = bool(
        (org_type and "consult" in org_type.lower())
        or firm
        or clients
    )

    if is_consulting:
        # Add or update Organization Type and Consulting Firm in System section
        if "**Organization Type**" in text:
            _replace_field("Organization Type", "consulting")
        else:
            text = re.sub(
                r"^(-\s+\*\*Role\*\*:\s*.*$)",
                r"\g<1>\n- **Organization Type**: consulting",
                text,
                flags=re.MULTILINE,
            )

        if firm:
            if "**Consulting Firm**" in text:
                _replace_field("Consulting Firm", firm)
            else:
                text = re.sub(
                    r"^(-\s+\*\*Organization Type\*\*:\s*.*$)",
                    rf"\g<1>\n- **Consulting Firm**: {firm}",
                    text,
                    flags=re.MULTILINE,
                )

        if client_sponsors:
            sponsors_formatted = "; ".join(f"{c}: {s}" for c, s in client_sponsors.items())
            if "**Client Sponsors**" in text:
                _replace_field("Client Sponsors", sponsors_formatted)
            else:
                text = re.sub(
                    r"^(-\s+\*\*Deadline warning\*\*:\s*.*$)",
                    rf"\g<1>\n- **Client Sponsors**: {sponsors_formatted}",
                    text,
                    flags=re.MULTILINE,
                )

    # Replace Portfolio table
    if clients and is_consulting:
        lines = [
            "## 📂 Portfolio & Client Engagements",
            "",
            "> Define your clients and projects here. Beats PM Kit uses this to route items across client engagements.",
            "",
            "| Client | Project / Workstream | Alias | Description / Keywords |",
            "| ------ | -------------------- | ----- | ---------------------- |",
        ]
        flat_products = []
        for c in clients:
            c_name = c["client"]
            for p in c.get("projects", []):
                p_name = p.get("name", "Engagement")
                p_alias = p.get("alias", _make_alias(c_name, p_name))
                p_desc = p.get("description", f"{c_name} engagement")
                lines.append(f"| **{c_name}** | **{p_name}** | `{p_alias}` | {p_desc} |")
                flat_products.append({"name": f"{c_name} - {p_name}", "alias": p_alias, "client": c_name, "description": p_desc})
        new_section = "\n".join(lines)

        portfolio_re = r"## 📂 [^\n]+.*?(?=\n---|\n## Boss)"
        if re.search(portfolio_re, text, flags=re.DOTALL):
            text = re.sub(portfolio_re, new_section + "\n", text, flags=re.DOTALL)

        # Seed workspace folders for clients
        seed_consulting_workspace(root, firm, clients, client_sponsors)

    elif products:
        lines = [
            "## 📂 Product Portfolio",
            "",
            "> Define your products here. Antigravity uses this to route items automatically.",
            "",
            "| Product Name | Alias | Description / Keywords |",
            "| ------------ | ----- | ---------------------- |",
        ]
        for p in products:
            p_name = p.get("name", "Product")
            p_alias = p.get("alias", p_name.lower()[:4])
            p_desc = p.get("description", "")
            lines.append(f"| **{p_name}** | `{p_alias}` | {p_desc} |")
        new_section = "\n".join(lines)

        portfolio_re = r"## 📂 [^\n]+.*?(?=\n---|\n## Boss)"
        if re.search(portfolio_re, text, flags=re.DOTALL):
            text = re.sub(portfolio_re, new_section + "\n", text, flags=re.DOTALL)

    settings_file.write_text(text, encoding="utf-8")

    # If boss name provided, also append to People if PEOPLE.md exists
    if boss_name:
        people_file = root / "4. People" / "PEOPLE.md"
        if people_file.exists():
            people_text = people_file.read_text(encoding="utf-8", errors="replace")
            if boss_name not in people_text:
                entry = f"| **{boss_name}** | Manager / Partner | Leadership Alignment |\n"
                people_file.write_text(people_text.rstrip() + "\n" + entry, encoding="utf-8")

    return True


def render_human_status(status: ProfileStatus) -> str:
    lines = []
    lines.append(BANNER_MATRIX)
    lines.append("◈ BEATS PM KIT :: FTUE PROFILE STATUS ◈")
    lines.append(f"  Owner       : {status.owner or '⚡ [NOT SET] Run /start to configure'}")
    lines.append(f"  Role        : {status.role or '⚡ [NOT SET]'}")
    lines.append(f"  Timezone    : {status.timezone or 'America/Chicago'}")
    lines.append(f"  Setup Type  : {'Consulting (Multi-Client Engagements)' if status.org_type == 'consulting' else 'In-House Product Management'}")

    if status.org_type == "consulting":
        lines.append(f"  Firm        : {status.firm or '⚡ [NOT SET]'}")
        lines.append(f"  Internal Lead: {status.boss_name or '⚡ [NOT SET]'}")
        if status.clients:
            lines.append(f"  Engagements : {len(status.clients)} Client Companies ({len(status.products)} Projects)")
            for c in status.clients:
                sponsor_info = f" [Sponsor: {c.get('sponsor')}]" if c.get('sponsor') else ""
                lines.append(f"    ◈ {c['client']}{sponsor_info}")
                for p in c.get("projects", []):
                    lines.append(f"      ⌁ {p.get('name')} (`{p.get('alias')}`)")
        else:
            lines.append(f"  Engagements : ⚡ [PENDING SETUP]")
    else:
        lines.append(f"  Manager     : {status.boss_name or '⚡ [NOT SET]'}")
        if status.products:
            p_names = ", ".join(f"{p['name']} ({p['alias']})" for p in status.products)
            lines.append(f"  Products    : {p_names}")
        else:
            lines.append(f"  Products    : ⚡ [DEFAULT]")

    lines.append(f"  Configured  : {'✓ YES' if status.is_configured else '✗ PENDING'}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Beats PM Kit FTUE Helper")
    sub = parser.add_subparsers(dest="command", required=True)

    # status
    p_status = sub.add_parser("status", help="Show current FTUE profile status")
    p_status.add_argument("--json", action="store_true", help="Output JSON")
    p_status.add_argument("--root", default=str(ROOT), help="Repo root")

    # configure
    p_config = sub.add_parser("configure", help="Update profile fields in SETTINGS.md")
    p_config.add_argument("--owner", help="Your name")
    p_config.add_argument("--role", help="Your PM role (e.g. 'Senior Consultant', 'Engagement Manager')")
    p_config.add_argument("--timezone", help="Your timezone")
    p_config.add_argument("--org-type", choices=["in-house", "consulting"], default=None, help="Organization type")
    p_config.add_argument("--firm", help="Consulting firm or agency name (e.g. 'Slalom', 'Apex Advisory')")
    p_config.add_argument("--manager", help="Internal manager or partner name")
    p_config.add_argument("--alias", help="Manager nickname/alias")
    p_config.add_argument("--clients", help="Consulting client & project mapping (e.g. 'ClientA: Proj1, Proj2; ClientB: Proj3')")
    p_config.add_argument("--client-sponsors", help="Client sponsor mapping (e.g. 'ClientA: Jane Smith; ClientB: Dan Lee')")
    p_config.add_argument("--products", help="In-house comma-separated product names (e.g. 'Mobile App, Web Portal')")
    p_config.add_argument("--outlook", help="Outlook source window or 'disabled'")
    p_config.add_argument("--teams", help="Teams source window or 'disabled'")
    p_config.add_argument("--slack", help="Slack source window or 'disabled'")
    p_config.add_argument("--granola", help="Granola intake mode or 'disabled'")
    p_config.add_argument("--quill", help="Quill intake mode or 'disabled'")
    p_config.add_argument("--root", default=str(ROOT), help="Repo root")
    p_config.add_argument("--json", action="store_true", help="Output JSON")

    # banner
    p_banner = sub.add_parser("banner", help="Print glyph matrix ASCII banner")
    p_banner.add_argument(
        "step",
        nargs="?",
        default="welcome",
        choices=["welcome", "complete", "identity", "products", "consulting_step", "telemetry"],
    )

    args = parser.parse_args(argv)
    if args.command == "banner":
        print(BANNERS.get(args.step, BANNER_MATRIX))
        return 0

    root = Path(getattr(args, "root", ROOT)).resolve()

    if args.command == "status":
        status = inspect_profile(root)
        if args.json:
            print(json.dumps(asdict(status), indent=2))
        else:
            print(render_human_status(status))
        return 0

    if args.command == "configure":
        parsed_clients = None
        parsed_sponsors = None

        if args.client_sponsors:
            parsed_sponsors = {}
            for part in re.split(r"[;,]+", args.client_sponsors):
                if ":" in part:
                    c, s = part.split(":", 1)
                    parsed_sponsors[c.strip()] = s.strip()

        if args.clients:
            parsed_clients = parse_clients_input(args.clients)
            if parsed_sponsors:
                for c in parsed_clients:
                    c_name = c["client"]
                    if c_name in parsed_sponsors:
                        c["sponsor"] = parsed_sponsors[c_name]

        parsed_products = None
        if args.products and not parsed_clients:
            parsed_products = []
            for item in args.products.split(","):
                item = item.strip()
                if item:
                    alias = item.lower().split()[0][:4]
                    parsed_products.append({"name": item, "alias": alias, "description": f"Focus area: {item}"})

        ok = update_profile(
            root,
            owner=args.owner,
            role=args.role,
            timezone=args.timezone,
            org_type=args.org_type or ("consulting" if (args.firm or parsed_clients) else None),
            firm=args.firm,
            boss_name=args.manager,
            boss_alias=args.alias,
            client_sponsors=parsed_sponsors,
            products=parsed_products,
            clients=parsed_clients,
            outlook=args.outlook,
            teams=args.teams,
            slack=args.slack,
            granola=args.granola,
            quill=args.quill,
        )
        status = inspect_profile(root)
        if args.json:
            print(json.dumps({"success": ok, "profile": asdict(status)}, indent=2))
        else:
            print(BANNER_COMPLETE)
            print("✓ Settings updated successfully in SETTINGS.md")
            print(render_human_status(status))
        return 0 if ok else 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

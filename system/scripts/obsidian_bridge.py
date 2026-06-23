#!/usr/bin/env python3
"""
Obsidian bridge for Beats PM Kit.

Provides local-first Obsidian detection, configuration, opening, sync, and
optional MCP template generation without storing private values in tracked files.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


SCRIPT_DIR = Path(__file__).resolve().parent
KIT_ROOT = SCRIPT_DIR.parent.parent
LOCAL_CONFIG = KIT_ROOT / "system" / "config" / "obsidian.local.json"
LEGACY_CONFIG = KIT_ROOT / "system" / "config.json"
MCP_TEMPLATE = KIT_ROOT / "system" / "config" / "mcp.obsidian.local.json"

DEFAULT_TARGET_FOLDER = "Beats PM Kit"
DEFAULT_DASHBOARD = "OBSIDIAN.md"
DEFAULT_REST_HOST = "127.0.0.1"
DEFAULT_REST_PORT = 27124

SYNC_MAP = {
    "0. Incoming": "Incoming",
    "1. Company": "Company",
    "2. Products": "Products",
    "3. Meetings": "Meetings",
    "4. People": "People",
    "5. Trackers": "Trackers",
}

FOLDER_TAGS = {
    "Incoming": ["inbox"],
    "Company": ["company", "strategy"],
    "Products": ["product", "prd"],
    "Meetings": ["meeting", "notes"],
    "People": ["people", "stakeholder"],
    "Trackers": ["tracker", "task"],
}

FOLDER_TYPES = {
    "Incoming": "inbox",
    "Company": "company",
    "Products": "product",
    "Meetings": "meeting",
    "People": "person",
    "Trackers": "tracker",
}

SKIP_PATTERNS = {
    ".gitkeep",
    ".DS_Store",
    "__pycache__",
    ".git",
    ".obsidian",
}

FRONTMATTER_RE = re.compile(r"\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n?", re.DOTALL)
META_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:\*\*)?(priority|owner|due)(?:\*\*)?\s*[:|-]\s*(.+?)\s*$",
    re.IGNORECASE,
)


@dataclass
class SyncStats:
    new: int = 0
    updated: int = 0
    skipped: int = 0
    removed: int = 0
    conflicts: list[str] = field(default_factory=list)
    written: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "new": self.new,
            "updated": self.updated,
            "skipped": self.skipped,
            "removed": self.removed,
            "conflicts": self.conflicts,
            "written": self.written,
        }


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def as_path(value: str | os.PathLike[str] | None) -> Path | None:
    if not value:
        return None
    try:
        return Path(str(value)).expanduser()
    except (OSError, ValueError):
        return None


def path_info(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {"path": None, "exists": False, "is_dir": False}
    return {
        "path": str(path),
        "exists": path.exists(),
        "is_dir": path.is_dir(),
        "has_obsidian_config": (path / ".obsidian").exists(),
    }


def obsidian_global_config_path(
    platform_name: str | None = None,
    home: Path | None = None,
    env: dict[str, str] | None = None,
) -> Path:
    system = platform_name or platform.system()
    env = env or os.environ
    home = home or Path.home()
    if system == "Windows":
        appdata = env.get("APPDATA")
        if appdata:
            return Path(appdata) / "obsidian" / "obsidian.json"
        return home / "AppData" / "Roaming" / "obsidian" / "obsidian.json"
    if system == "Darwin":
        return home / "Library" / "Application Support" / "obsidian" / "obsidian.json"
    xdg = env.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg) / "obsidian" / "obsidian.json"
    return home / ".config" / "obsidian" / "obsidian.json"


def windows_uri_handler(registry_command: str | None = None) -> str | None:
    if registry_command is not None:
        return registry_command
    if platform.system() != "Windows":
        return None
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"obsidian\shell\open\command") as key:
            value, _ = winreg.QueryValueEx(key, None)
            return value
    except OSError:
        return None


def spotlight_obsidian_apps() -> list[Path]:
    if platform.system() != "Darwin":
        return []
    try:
        result = subprocess.run(
            ["mdfind", "kMDItemCFBundleIdentifier == 'md.obsidian'"],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []
    return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def app_candidates(
    platform_name: str | None = None,
    home: Path | None = None,
    env: dict[str, str] | None = None,
    extra_app_paths: list[Path] | None = None,
    spotlight_paths: list[Path] | None = None,
) -> list[Path]:
    system = platform_name or platform.system()
    home = home or Path.home()
    env = env or os.environ
    candidates: list[Path] = []

    if system == "Windows":
        local = env.get("LOCALAPPDATA")
        program_files = env.get("ProgramFiles")
        program_files_x86 = env.get("ProgramFiles(x86)")
        if local:
            candidates.extend(
                [
                    Path(local) / "Programs" / "Obsidian" / "Obsidian.exe",
                    Path(local) / "Obsidian" / "Obsidian.exe",
                ]
            )
        if program_files:
            candidates.append(Path(program_files) / "Obsidian" / "Obsidian.exe")
        if program_files_x86:
            candidates.append(Path(program_files_x86) / "Obsidian" / "Obsidian.exe")
    elif system == "Darwin":
        candidates.extend(
            [
                Path("/Applications/Obsidian.app"),
                home / "Applications" / "Obsidian.app",
            ]
        )
        candidates.extend(spotlight_paths if spotlight_paths is not None else spotlight_obsidian_apps())
    else:
        candidates.extend(
            [
                Path("/usr/bin/obsidian"),
                Path("/usr/local/bin/obsidian"),
                home / ".local" / "bin" / "obsidian",
            ]
        )

    if extra_app_paths:
        candidates.extend(extra_app_paths)

    seen: set[str] = set()
    unique: list[Path] = []
    for candidate in candidates:
        key = str(candidate)
        if key not in seen:
            unique.append(candidate)
            seen.add(key)
    return unique


def parse_saved_vaults(config_path: Path) -> list[dict[str, Any]]:
    data = read_json(config_path)
    vaults = data.get("vaults", {})
    parsed: list[dict[str, Any]] = []
    if not isinstance(vaults, dict):
        return parsed
    for vault_id, raw in vaults.items():
        if not isinstance(raw, dict):
            continue
        vault_path = as_path(raw.get("path"))
        info = path_info(vault_path)
        parsed.append(
            {
                "id": vault_id,
                "path": info["path"],
                "exists": info["exists"],
                "is_dir": info["is_dir"],
                "has_obsidian_config": info["has_obsidian_config"],
                "open": bool(raw.get("open", False)),
                "ts": raw.get("ts"),
                "source": str(config_path),
            }
        )
    return sorted(parsed, key=lambda item: item.get("ts") or 0, reverse=True)


def probe_rest_api(
    host: str = DEFAULT_REST_HOST,
    port: int = DEFAULT_REST_PORT,
    timeout: float = 1.5,
) -> dict[str, Any]:
    url = f"https://{host}:{port}/"
    request = urllib.request.Request(url, headers={"User-Agent": "beats-pm-kit"})
    context = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            return {
                "url": url,
                "reachable": True,
                "status": response.status,
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        return {"url": url, "reachable": True, "status": exc.code, "error": None}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"url": url, "reachable": False, "status": None, "error": str(exc)}


def detect_obsidian(
    platform_name: str | None = None,
    home: Path | None = None,
    env: dict[str, str] | None = None,
    extra_app_paths: list[Path] | None = None,
    registry_command: str | None = None,
    command_lookup: Callable[[str], str | None] | None = None,
    rest_probe: Callable[[], dict[str, Any]] | None = None,
    spotlight_paths: list[Path] | None = None,
) -> dict[str, Any]:
    """Detect Obsidian app, CLI, URI handler, saved vaults, and REST health."""

    system = platform_name or platform.system()
    env = env or os.environ
    home = home or Path.home()
    command_lookup = command_lookup or shutil.which
    global_config = obsidian_global_config_path(system, home, env)
    candidates = app_candidates(system, home, env, extra_app_paths, spotlight_paths)
    existing_apps = [str(path) for path in candidates if path.exists()]
    cli_path = command_lookup("obsidian")
    uri_handler = windows_uri_handler(registry_command) if system == "Windows" else None
    if system == "Darwin" and existing_apps:
        uri_handler = "macOS LaunchServices (Obsidian.app present)"
    saved_vaults = parse_saved_vaults(global_config)
    valid_vaults = [vault for vault in saved_vaults if vault["exists"] and vault["is_dir"]]
    stale_vaults = [vault for vault in saved_vaults if not vault["exists"]]
    rest_api = rest_probe() if rest_probe is not None else probe_rest_api()

    return {
        "platform": system,
        "installed": bool(existing_apps or cli_path or uri_handler),
        "app_paths": existing_apps,
        "cli_path": cli_path,
        "uri_handler": uri_handler,
        "global_config": str(global_config),
        "saved_vaults": saved_vaults,
        "valid_vaults": valid_vaults,
        "stale_vaults": stale_vaults,
        "rest_api": rest_api,
    }


def load_legacy_obsidian_config(root: Path = KIT_ROOT) -> dict[str, Any]:
    cfg = read_json(root / "system" / "config.json")
    obs = cfg.get("obsidian", {}) if isinstance(cfg, dict) else {}
    if not isinstance(obs, dict):
        return {}
    result: dict[str, Any] = {}
    if obs.get("vault_path"):
        result["vault_path"] = str(Path(obs["vault_path"]).expanduser())
    if obs.get("target_folder"):
        result["target_folder"] = obs["target_folder"]
    return result


def choose_default_config(
    detection: dict[str, Any],
    root: Path = KIT_ROOT,
    target_folder: str = DEFAULT_TARGET_FOLDER,
) -> dict[str, Any]:
    root = root.resolve()
    for vault in detection.get("valid_vaults", []):
        vault_path = as_path(vault.get("path"))
        if vault_path and vault_path.resolve() == root:
            return {
                "mode": "kit-vault",
                "vault_path": str(root),
                "vault_id": vault.get("id"),
                "target_folder": "",
                "dashboard_note": DEFAULT_DASHBOARD,
            }

    valid_vaults = detection.get("valid_vaults", [])
    if valid_vaults:
        vault = valid_vaults[0]
        return {
            "mode": "sync",
            "vault_path": vault["path"],
            "vault_id": vault.get("id"),
            "target_folder": target_folder,
            "dashboard_note": DEFAULT_DASHBOARD,
        }

    return {
        "mode": "kit-vault",
        "vault_path": str(root),
        "vault_id": None,
        "target_folder": "",
        "dashboard_note": DEFAULT_DASHBOARD,
    }


def load_local_config(root: Path = KIT_ROOT) -> dict[str, Any]:
    config = read_json(root / "system" / "config" / "obsidian.local.json")
    return config if isinstance(config, dict) else {}


def active_config(root: Path = KIT_ROOT, detection: dict[str, Any] | None = None) -> dict[str, Any]:
    detection = detection or detect_obsidian()
    local = load_local_config(root)
    if local.get("vault_path"):
        return normalize_config(local, root)

    legacy = load_legacy_obsidian_config(root)
    if legacy.get("vault_path"):
        mode = "kit-vault" if Path(legacy["vault_path"]).expanduser().resolve() == root.resolve() else "sync"
        legacy.setdefault("mode", mode)
        legacy.setdefault("dashboard_note", DEFAULT_DASHBOARD)
        legacy.setdefault("target_folder", DEFAULT_TARGET_FOLDER if mode == "sync" else "")
        return normalize_config(legacy, root)

    return normalize_config(choose_default_config(detection, root), root)


def normalize_config(config: dict[str, Any], root: Path = KIT_ROOT) -> dict[str, Any]:
    mode = config.get("mode") or "sync"
    vault_path = Path(config.get("vault_path") or root).expanduser()
    if vault_path.resolve() == root.resolve():
        mode = "kit-vault"
    normalized = {
        "schema_version": 1,
        "mode": mode,
        "vault_path": str(vault_path),
        "vault_id": config.get("vault_id"),
        "target_folder": "" if mode == "kit-vault" else config.get("target_folder", DEFAULT_TARGET_FOLDER),
        "dashboard_note": config.get("dashboard_note", DEFAULT_DASHBOARD),
        "rest_api": {
            "host": config.get("rest_api", {}).get("host", DEFAULT_REST_HOST)
            if isinstance(config.get("rest_api"), dict)
            else DEFAULT_REST_HOST,
            "port": config.get("rest_api", {}).get("port", DEFAULT_REST_PORT)
            if isinstance(config.get("rest_api"), dict)
            else DEFAULT_REST_PORT,
        },
    }
    return normalized


def configured_target(config: dict[str, Any]) -> Path:
    vault_path = Path(config["vault_path"]).expanduser()
    if config.get("mode") == "kit-vault":
        return vault_path
    target = config.get("target_folder") or DEFAULT_TARGET_FOLDER
    return vault_path / target


def yaml_quote(value: Any) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def split_frontmatter(content: str) -> tuple[str | None, str]:
    match = FRONTMATTER_RE.match(content)
    if not match:
        return None, content
    return match.group(1), content[match.end() :]


def is_managed_frontmatter(frontmatter: str | None) -> bool:
    if not frontmatter:
        return False
    return "source: beats-pm-kit" in frontmatter or "sync_managed: beats-pm-kit" in frontmatter


def is_managed_file(path: Path) -> bool:
    if path.suffix.lower() not in {".md", ".markdown"}:
        return False
    try:
        frontmatter, _ = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return False
    return is_managed_frontmatter(frontmatter)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    try:
        return sha256_bytes(path.read_bytes())
    except OSError:
        return ""


def should_skip(path: Path) -> bool:
    name = path.name
    if name in SKIP_PATTERNS:
        return True
    return name.endswith(".pyc") or name.endswith(".bak")


def infer_fields(content: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in content.splitlines()[:120]:
        match = META_RE.match(line)
        if not match:
            continue
        key = match.group(1).lower()
        value = match.group(2).strip().strip("*`")
        if value and key not in fields:
            fields[key] = value
    return fields


def build_frontmatter(src: Path, folder_tag: str, kit_root: Path, body: str) -> str:
    rel_path = src.relative_to(kit_root).as_posix()
    modified = dt.datetime.fromtimestamp(src.stat().st_mtime).astimezone().isoformat(timespec="seconds")
    title = src.stem.replace("-", " ").replace("_", " ")
    source_hash = sha256_bytes(body.encode("utf-8"))
    tags = FOLDER_TAGS.get(folder_tag, [])
    inferred = infer_fields(body)

    lines = [
        "---",
        f"title: {yaml_quote(title)}",
        "source: beats-pm-kit",
        "sync_managed: beats-pm-kit",
        f"type: {yaml_quote(FOLDER_TYPES.get(folder_tag, folder_tag.lower()))}",
        f"source_path: {yaml_quote(rel_path)}",
        f"source_modified: {yaml_quote(modified)}",
        f"source_hash: {yaml_quote(source_hash)}",
    ]
    for key in ("priority", "owner", "due"):
        if key in inferred:
            lines.append(f"{key}: {yaml_quote(inferred[key])}")
    lines.append("tags:")
    if tags:
        lines.extend(f"  - {tag}" for tag in tags)
    else:
        lines.append("  - beats-pm-kit")
    lines.extend(["---", ""])
    return "\n".join(lines) + "\n"


def render_markdown(src: Path, folder_tag: str, kit_root: Path) -> tuple[str, bool]:
    content = src.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = split_frontmatter(content)
    if frontmatter and not is_managed_frontmatter(frontmatter):
        return content, False
    frontmatter_text = build_frontmatter(src, folder_tag, kit_root, body.lstrip("\n"))
    return frontmatter_text + body.lstrip("\n"), True


def sync_file(src: Path, dst: Path, folder_tag: str, kit_root: Path, dry_run: bool) -> str:
    is_markdown = src.suffix.lower() in {".md", ".markdown"}
    if is_markdown:
        rendered, _ = render_markdown(src, folder_tag, kit_root)
        new_bytes = rendered.encode("utf-8")
    else:
        try:
            new_bytes = src.read_bytes()
        except OSError:
            return "skipped"

    if dst.exists():
        try:
            old_bytes = dst.read_bytes()
        except OSError:
            old_bytes = b""
        if old_bytes == new_bytes:
            return "skipped"
        status = "updated"
    else:
        status = "new"

    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if is_markdown:
            dst.write_bytes(new_bytes)
        else:
            shutil.copy2(src, dst)
    return status


def clean_stale(vault_target: Path, kit_sources: dict[str, Path], dry_run: bool) -> list[str]:
    removed: list[str] = []
    for obs_folder, kit_folder in kit_sources.items():
        obs_path = vault_target / obs_folder
        if not obs_path.exists():
            continue
        for candidate in obs_path.rglob("*"):
            if candidate.is_dir() or should_skip(candidate):
                continue
            rel = candidate.relative_to(obs_path)
            source = kit_folder / rel
            if source.exists() or not is_managed_file(candidate):
                continue
            removed.append(str(candidate))
            if not dry_run:
                candidate.unlink()
    return removed


def dashboard_content() -> str:
    return """---
title: "Beats PM Kit"
source: beats-pm-kit
sync_managed: beats-pm-kit
type: dashboard
tags:
  - beats-pm-kit
  - dashboard
---

# Beats PM Kit

## Start Here

- [[SETTINGS]]
- [[0. Incoming]]
- [[3. Meetings]]
- [[5. Trackers]]

## Core Workflows

- `/day` - daily brief and planning
- `/paste` - capture raw notes, screenshots, and links
- `/meet` - synthesize meeting notes
- `/track` - manage tasks, bugs, and boss asks
- `/week` - weekly planning and rollup
- `/obsidian` - inspect, configure, open, and sync Obsidian

## Operating Areas

- [[1. Company]]
- [[2. Products]]
- [[4. People]]
- [[5. Trackers/TASK_MASTER]]
"""


def ensure_dashboard(target_root: Path, dry_run: bool = False) -> str:
    dashboard = target_root / DEFAULT_DASHBOARD
    content = dashboard_content()
    if dashboard.exists():
        existing = dashboard.read_text(encoding="utf-8", errors="replace")
        frontmatter, _ = split_frontmatter(existing)
        if not is_managed_frontmatter(frontmatter):
            return "skipped"
        if existing == content:
            return "skipped"
        status = "updated"
    else:
        status = "new"

    if not dry_run:
        target_root.mkdir(parents=True, exist_ok=True)
        dashboard.write_bytes(content.encode("utf-8"))
    return status


def run_sync(
    config: dict[str, Any] | None = None,
    root: Path = KIT_ROOT,
    dry_run: bool = True,
    folder: str | None = None,
    clean: bool = False,
) -> SyncStats:
    config = normalize_config(config or active_config(root), root)
    target = configured_target(config)
    stats = SyncStats()

    if config["mode"] == "kit-vault":
        status = ensure_dashboard(target, dry_run=dry_run)
        setattr(stats, status, getattr(stats, status) + 1)
        if status in {"new", "updated"}:
            stats.written.append(str(target / DEFAULT_DASHBOARD))
        return stats

    vault_path = Path(config["vault_path"]).expanduser()
    if not vault_path.exists():
        raise FileNotFoundError(f"Obsidian vault not found: {vault_path}")

    sync_folders = SYNC_MAP
    if folder:
        selected = None
        for kit_folder, obs_folder in SYNC_MAP.items():
            if folder == obs_folder or folder in kit_folder:
                selected = kit_folder
                break
        if selected is None:
            raise ValueError(f"Unknown sync folder: {folder}")
        sync_folders = {selected: SYNC_MAP[selected]}

    dashboard_status = ensure_dashboard(target, dry_run=dry_run)
    setattr(stats, dashboard_status, getattr(stats, dashboard_status) + 1)
    if dashboard_status in {"new", "updated"}:
        stats.written.append(str(target / DEFAULT_DASHBOARD))

    kit_sources: dict[str, Path] = {}
    for kit_folder_name, obs_folder_name in sync_folders.items():
        kit_folder = root / kit_folder_name
        obs_folder = target / obs_folder_name
        kit_sources[obs_folder_name] = kit_folder
        if not kit_folder.exists():
            continue
        for src in kit_folder.rglob("*"):
            if src.is_dir() or should_skip(src):
                continue
            rel = src.relative_to(kit_folder)
            dst = obs_folder / rel
            status = sync_file(src, dst, obs_folder_name, root, dry_run)
            setattr(stats, status, getattr(stats, status) + 1)
            if status in {"new", "updated"}:
                stats.written.append(str(dst))

    if clean:
        removed = clean_stale(target, kit_sources, dry_run=dry_run)
        stats.removed = len(removed)

    if not dry_run:
        meta = {
            "last_sync": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "source": str(root),
            "target": str(target),
            "mode": config["mode"],
            "stats": stats.as_dict(),
        }
        write_json(target / ".sync_meta.json", meta)

    return stats


def write_mcp_template(output: Path = MCP_TEMPLATE) -> Path:
    template = {
        "schema_version": 1,
        "description": "Local-only Obsidian MCP template. Keep API keys in this ignored file or environment variables, never in tracked files.",
        "mcpServers": {
            "mcp-obsidian": {
                "command": "uvx",
                "args": ["mcp-obsidian"],
                "env": {
                    "OBSIDIAN_API_KEY": "<your-local-rest-api-key>",
                    "OBSIDIAN_HOST": DEFAULT_REST_HOST,
                    "OBSIDIAN_PORT": str(DEFAULT_REST_PORT),
                },
            }
        },
    }
    write_json(output, template)
    return output


def save_config(config: dict[str, Any], root: Path = KIT_ROOT) -> Path:
    normalized = normalize_config(config, root)
    normalized["configured_at"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    path = root / "system" / "config" / "obsidian.local.json"
    write_json(path, normalized)
    return path


def build_uri(action: str, params: dict[str, str]) -> str:
    return "obsidian://" + action + "?" + urllib.parse.urlencode(params, safe="/:")


def vault_param(config: dict[str, Any]) -> dict[str, str]:
    if config.get("vault_id"):
        return {"vault": str(config["vault_id"])}
    return {"vault": Path(config["vault_path"]).name}


def open_uri(uri: str) -> None:
    system = platform.system()
    if system == "Windows":
        os.startfile(uri)  # type: ignore[attr-defined]
    elif system == "Darwin":
        subprocess.run(["open", uri], check=False)
    else:
        subprocess.run(["xdg-open", uri], check=False)


def open_target(config: dict[str, Any], target: str, query: str | None = None, file_path: str | None = None) -> str:
    config = normalize_config(config)
    if target == "vault":
        if config["mode"] == "kit-vault":
            uri = build_uri("open", {"path": str(Path(config["vault_path"]) / DEFAULT_DASHBOARD)})
        else:
            uri = build_uri("open", vault_param(config))
    elif target == "dashboard":
        uri = build_uri("open", {"path": str(configured_target(config) / DEFAULT_DASHBOARD)})
    elif target == "daily":
        uri = build_uri("daily", vault_param(config))
    elif target == "tracker":
        uri = build_uri("open", {"path": str(configured_target(config) / "5. Trackers" / "TASK_MASTER.md")})
    elif target == "search":
        if not query:
            raise ValueError("open search requires --query")
        params = vault_param(config)
        params["query"] = query
        uri = build_uri("search", params)
    elif target == "file":
        if not file_path:
            raise ValueError("open file requires --file")
        candidate = Path(file_path)
        if not candidate.is_absolute():
            candidate = configured_target(config) / candidate
        uri = build_uri("open", {"path": str(candidate)})
    else:
        raise ValueError(f"Unknown open target: {target}")
    open_uri(uri)
    return uri


def print_status(data: dict[str, Any], config: dict[str, Any]) -> None:
    rest = data["rest_api"]
    print("Obsidian status")
    print(f"  Platform: {data['platform']}")
    print(f"  Installed: {'yes' if data['installed'] else 'no'}")
    print(f"  App paths: {', '.join(data['app_paths']) if data['app_paths'] else 'none'}")
    print(f"  CLI: {data['cli_path'] or 'not found'}")
    print(f"  URI handler: {data['uri_handler'] or 'not found'}")
    print(f"  Saved vaults: {len(data['saved_vaults'])}")
    print(f"  Valid vaults: {len(data['valid_vaults'])}")
    print(f"  Stale vaults: {len(data['stale_vaults'])}")
    print(f"  REST API: {'reachable' if rest.get('reachable') else 'not reachable'} ({rest.get('url')})")
    print(f"  Active mode: {config['mode']}")
    print(f"  Active vault: {config['vault_path']}")
    print(f"  Target folder: {config.get('target_folder') or '(vault root)'}")


def command_status(args: argparse.Namespace) -> int:
    detection = detect_obsidian()
    config = active_config(KIT_ROOT, detection)
    payload = {"detection": detection, "config": config}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print_status(detection, config)
    return 0


def command_configure(args: argparse.Namespace) -> int:
    detection = detect_obsidian()
    if args.vault:
        vault_path = Path(args.vault).expanduser()
        mode = args.mode if args.mode != "auto" else ("kit-vault" if vault_path.resolve() == KIT_ROOT.resolve() else "sync")
        config = {
            "mode": mode,
            "vault_path": str(vault_path),
            "target_folder": args.target_folder,
            "dashboard_note": DEFAULT_DASHBOARD,
        }
    else:
        config = choose_default_config(detection, KIT_ROOT, args.target_folder)
        if args.mode != "auto":
            config["mode"] = args.mode
            if args.mode == "kit-vault":
                config["vault_path"] = str(KIT_ROOT)
                config["target_folder"] = ""
    path = save_config(config, KIT_ROOT)
    normalized = active_config(KIT_ROOT, detection)
    if not args.no_dashboard:
        ensure_dashboard(configured_target(normalized), dry_run=False)
    if args.json:
        print(json.dumps({"config_path": str(path), "config": normalized}, indent=2))
    else:
        print(f"Wrote {path}")
        print(f"Mode: {normalized['mode']}")
        print(f"Vault: {normalized['vault_path']}")
    return 0


def command_open(args: argparse.Namespace) -> int:
    config = active_config(KIT_ROOT)
    uri = open_target(config, args.target, query=args.query, file_path=args.file)
    if args.json:
        print(json.dumps({"opened": uri}, indent=2))
    else:
        print(f"Opened: {uri}")
    return 0


def command_sync(args: argparse.Namespace) -> int:
    dry_run = not args.apply
    try:
        stats = run_sync(dry_run=dry_run, folder=args.folder, clean=args.clean)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(stats.as_dict(), indent=2))
    else:
        mode = "DRY RUN" if dry_run else "APPLY"
        print(f"Obsidian sync ({mode})")
        print(
            f"  {stats.new} new, {stats.updated} updated, "
            f"{stats.skipped} unchanged, {stats.removed} removed"
        )
        for path in stats.written[:20]:
            print(f"  write: {path}")
        if len(stats.written) > 20:
            print(f"  ... {len(stats.written) - 20} more")
    return 0


def command_mcp_template(args: argparse.Namespace) -> int:
    output = Path(args.output).expanduser() if args.output else MCP_TEMPLATE
    path = write_mcp_template(output)
    if args.json:
        print(json.dumps({"path": str(path)}, indent=2))
    else:
        print(f"Wrote {path}")
        print("Fill OBSIDIAN_API_KEY locally after enabling the Obsidian Local REST API plugin.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Beats PM Kit Obsidian bridge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Detect Obsidian, vaults, config, and REST API health")
    status.add_argument("--json", action="store_true")
    status.set_defaults(func=command_status)

    configure = subparsers.add_parser("configure", help="Write ignored local Obsidian config")
    configure.add_argument("--vault", help="Vault path to use; defaults to best detected option")
    configure.add_argument("--mode", choices=["auto", "kit-vault", "sync"], default="auto")
    configure.add_argument("--target-folder", default=DEFAULT_TARGET_FOLDER)
    configure.add_argument("--no-dashboard", action="store_true")
    configure.add_argument("--json", action="store_true")
    configure.set_defaults(func=command_configure)

    open_cmd = subparsers.add_parser("open", help="Open vault, dashboard, daily note, tracker, search, or file")
    open_cmd.add_argument(
        "target",
        choices=["vault", "dashboard", "daily", "tracker", "search", "file"],
        nargs="?",
        default="dashboard",
    )
    open_cmd.add_argument("--query", help="Search query when target is search")
    open_cmd.add_argument("--file", help="File path when target is file")
    open_cmd.add_argument("--json", action="store_true")
    open_cmd.set_defaults(func=command_open)

    sync = subparsers.add_parser("sync", help="Sync kit files into configured Obsidian vault")
    sync.add_argument("--dry-run", action="store_true", help="Preview without writing; default unless --apply is set")
    sync.add_argument("--apply", action="store_true", help="Write changes")
    sync.add_argument("--folder", help="Sync one kit folder, such as 3 or Meetings")
    sync.add_argument("--clean", action="store_true", help="Remove stale managed files")
    sync.add_argument("--json", action="store_true")
    sync.set_defaults(func=command_sync)

    mcp = subparsers.add_parser("mcp-template", help="Write ignored MCP config template for Obsidian")
    mcp.add_argument("--output", help="Output path; defaults to system/config/mcp.obsidian.local.json")
    mcp.add_argument("--json", action="store_true")
    mcp.set_defaults(func=command_mcp_template)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

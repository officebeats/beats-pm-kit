#!/usr/bin/env python3
"""Fail when tracked content exposes PII, secrets, or local runtime state."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from system.utils.root_policy import (
    LOCAL_RUNTIME_EXACT_PATHS,
    PRIVATE_WORKSPACE_ROOTS,
    generated_or_local_prefixes,
)

MAX_FINDINGS = 200
MAX_TEXT_BYTES = 2_000_000
FORBIDDEN_PATH_PREFIXES = generated_or_local_prefixes()
FORBIDDEN_EXACT_PATHS = LOCAL_RUNTIME_EXACT_PATHS

ALLOW_EMAIL_DOMAINS = {
    "example.com",
    "example.org",
    "example.net",
    "acme.com",
    "acmeworkflows.com",
    "company.com",
    "yourcompany.com",
    "domain.com",
    "test.com",
}

ALLOW_EMAIL_ADDRESSES = {
    "firstname.lastname@gmail.com",
    "randomnickname123@gmail.com",
    "cutesurfer@yahoo.com",
}


@dataclass(frozen=True)
class Finding:
    location: str
    rule: str
    sample: str


PRIVATE_ORG_TERMS = (
    "autono" "mize",
    "solve" "ntum",
    "know" "tion",
    "r" "source",
    "high" "mark",
    "digital" "api",
    "mcg" "health",
)
PRIVATE_ORG_RE = re.compile(r"\b(?:" + "|".join(PRIVATE_ORG_TERMS) + r")\b", re.I)
USER_DIR = "Users"
LOCAL_USER_PATH_RE = re.compile(
    r"(?:"
    + r"[A-Za-z]:[\\/]"
    + USER_DIR
    + r"[\\/][^\\/\s\"'<>]+|/"
    + USER_DIR
    + r"/[^/\s\"'<>]+|\\"
    + USER_DIR
    + r"\\[^\\\s\"'<>]+)"
)


CONTENT_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "private-atlassian-url",
        re.compile(r"https?://[A-Za-z0-9.-]*atlassian\.net[^\s\)\]\}\"'<>]*", re.I),
    ),
    (
        "private-organization-name",
        PRIVATE_ORG_RE,
    ),
    (
        "local-user-path",
        LOCAL_USER_PATH_RE,
    ),
    (
        "local-account-name",
        re.compile(r"\b" + "admin" + "-beats" + r"\b", re.I),
    ),
    (
        "private-key",
        re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    ),
    (
        "api-token",
        re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{20,}|AIza[0-9A-Za-z_-]{20,})\b", re.I),
    ),
    (
        "bearer-token",
        re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{30,}\b", re.I),
    ),
    (
        "phone-like-value",
        re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]\d{3}[-.\s]\d{4}(?!\d)"),
    ),
)

EMAIL_RE = re.compile(r"(?<![\w.-])[\w.+-]{2,64}@([A-Za-z0-9.-]+\.[A-Za-z]{2,})(?![\w.-])")


def run_git(args: list[str], *, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"git {' '.join(args)} failed: {stderr}")
    return result.stdout


def decode_path(raw: bytes) -> str:
    return raw.decode("utf-8", errors="replace").replace("\\", "/")


def iter_tree_paths() -> list[str]:
    raw = run_git(["ls-files", "-z"])
    return [decode_path(part) for part in raw.split(b"\0") if part]


def iter_all_object_paths() -> list[tuple[str, str]]:
    raw = run_git(["rev-list", "--objects", "--all"])
    records: list[tuple[str, str]] = []
    for line in raw.splitlines():
        if b" " not in line:
            continue
        object_id, path = line.split(b" ", 1)
        records.append((object_id.decode("ascii"), decode_path(path)))
    return records


def batch_object_info(object_ids: list[str]) -> dict[str, tuple[str, int]]:
    if not object_ids:
        return {}
    input_bytes = ("\n".join(object_ids) + "\n").encode("ascii")
    raw = run_git(["cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"], input_bytes=input_bytes)
    info: dict[str, tuple[str, int]] = {}
    for line in raw.splitlines():
        parts = line.decode("ascii", errors="replace").split()
        if len(parts) != 3:
            continue
        object_id, object_type, size = parts
        try:
            info[object_id] = (object_type, int(size))
        except ValueError:
            continue
    return info


def batch_object_data(object_ids: list[str]) -> dict[str, bytes]:
    if not object_ids:
        return {}
    input_bytes = ("\n".join(object_ids) + "\n").encode("ascii")
    raw = run_git(["cat-file", "--batch"], input_bytes=input_bytes)
    data: dict[str, bytes] = {}
    offset = 0
    while offset < len(raw):
        header_end = raw.find(b"\n", offset)
        if header_end == -1:
            break
        header = raw[offset:header_end].decode("ascii", errors="replace").split()
        if len(header) < 3:
            break
        object_id, object_type, size_text = header[:3]
        try:
            size = int(size_text)
        except ValueError:
            break
        start = header_end + 1
        end = start + size
        if object_type == "blob":
            data[object_id] = raw[start:end]
        offset = end + 1
    return data


def path_findings(path: str, ref: str | None = None) -> list[Finding]:
    normalized = path.replace("\\", "/")
    location = f"{ref}:{normalized}" if ref else normalized
    findings: list[Finding] = []

    root = normalized.split("/", 1)[0]
    if root in PRIVATE_WORKSPACE_ROOTS and not normalized.endswith("/.gitkeep"):
        findings.append(Finding(location, "private-workspace-content", normalized))

    if normalized in FORBIDDEN_EXACT_PATHS:
        findings.append(Finding(location, "local-runtime-path", normalized))

    if LOCAL_USER_PATH_RE.search(normalized):
        findings.append(Finding(location, "local-user-path", normalized))

    for prefix in FORBIDDEN_PATH_PREFIXES:
        if normalized == prefix.rstrip("/") or normalized.startswith(prefix):
            findings.append(Finding(location, "generated-or-local-runtime-path", normalized))
            break

    return findings


def is_text(data: bytes) -> bool:
    if b"\0" in data[:4096]:
        return False
    return True


def safe_text(data: bytes) -> str | None:
    if len(data) > MAX_TEXT_BYTES or not is_text(data):
        return None
    return data.decode("utf-8", errors="replace")


def line_for_match(text: str, start: int) -> tuple[int, str]:
    line_no = text.count("\n", 0, start) + 1
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", start)
    if line_end == -1:
        line_end = len(text)
    sample = text[line_start:line_end].strip()
    if len(sample) > 160:
        sample = sample[:157] + "..."
    return line_no, sample


def email_findings(text: str, location: str) -> list[Finding]:
    findings: list[Finding] = []
    for match in EMAIL_RE.finditer(text):
        address = match.group(0).lower()
        domain = match.group(1).lower()
        if address in ALLOW_EMAIL_ADDRESSES:
            continue
        if domain in ALLOW_EMAIL_DOMAINS or domain.endswith(".example"):
            continue
        line_no, sample = line_for_match(text, match.start())
        findings.append(Finding(f"{location}:{line_no}", "email-address", sample))
    return findings


def content_findings(text: str, location: str) -> list[Finding]:
    findings = email_findings(text, location)
    for rule, pattern in CONTENT_RULES:
        for match in pattern.finditer(text):
            if rule == "local-user-path" and any(
                placeholder in match.group(0).lower()
                for placeholder in (
                    "username",
                    "yourname",
                    "<user>",
                    "{user}",
                    "{id}",
                    "$user",
                    "[redacted-user]",
                )
            ):
                continue
            if rule == "phone-like-value" and "555" in match.group(0):
                continue
            line_no, sample = line_for_match(text, match.start())
            findings.append(Finding(f"{location}:{line_no}", rule, sample))
    return findings


def read_worktree_file(path: str) -> bytes:
    return (ROOT / path).read_bytes()


def scan_tree() -> list[Finding]:
    findings: list[Finding] = []
    for path in iter_tree_paths():
        if not (ROOT / path).exists():
            continue
        findings.extend(path_findings(path))
        if len(findings) >= MAX_FINDINGS:
            return findings
        try:
            text = safe_text(read_worktree_file(path))
        except FileNotFoundError:
            continue
        except OSError as exc:
            findings.append(Finding(path, "unreadable-file", str(exc)))
            continue
        if text is None:
            continue
        findings.extend(content_findings(text, path))
        if len(findings) >= MAX_FINDINGS:
            return findings
    return findings


def scan_all_refs() -> list[Finding]:
    findings: list[Finding] = []
    object_paths = iter_all_object_paths()
    object_info = batch_object_info([object_id for object_id, _path in object_paths])
    seen_blobs: dict[str, str] = {}

    for object_id, path in object_paths:
        object_type, _size = object_info.get(object_id, ("", 0))
        if object_type != "blob":
            continue
        findings.extend(path_findings(path, "all-refs"))
        if len(findings) >= MAX_FINDINGS:
            return findings
        seen_blobs.setdefault(object_id, path)

    blob_ids = [
        object_id
        for object_id, (object_type, size) in object_info.items()
        if object_id in seen_blobs and object_type == "blob" and size <= MAX_TEXT_BYTES
    ]

    for object_id, data in batch_object_data(blob_ids).items():
        text = safe_text(data)
        if text is None:
            continue
        findings.extend(content_findings(text, f"all-refs:{seen_blobs[object_id]}"))
        if len(findings) >= MAX_FINDINGS:
            return findings
    return findings


def print_findings(findings: list[Finding]) -> None:
    print("Privacy guard failed. Findings:")
    for finding in findings[:MAX_FINDINGS]:
        print(f"  - {finding.location} [{finding.rule}] {finding.sample}")
    if len(findings) > MAX_FINDINGS:
        print(f"  ... and {len(findings) - MAX_FINDINGS} more")


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan tracked content for PII, secrets, and runtime leaks")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--tree", action="store_true", help="Scan the current tracked tree")
    group.add_argument("--all-refs", action="store_true", help="Scan every reachable commit")
    args = parser.parse_args()

    findings = scan_all_refs() if args.all_refs else scan_tree()
    if findings:
        print_findings(findings)
        return 1
    scope = "all reachable commits" if args.all_refs else "current tracked tree"
    print(f"Privacy guard passed for {scope}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

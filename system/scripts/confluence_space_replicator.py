#!/usr/bin/env python3
"""
Confluence Space Replicator for Beats PM Kit.

A generic, token-efficient utility to replicate any Confluence space
into local Markdown files with YAML frontmatter, cross-document link resolution,
and automated hierarchy indexing.

Usage:
  python3 system/scripts/confluence_space_replicator.py \
    --input-json <path-to-confluence-pages.json> \
    --output-dir <destination-markdown-folder> \
    --base-url <confluence-instance-base-url> \
    --space-key <SPACE_KEY>
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


def sanitize_filename(title: str) -> str:
    cleaned = html.unescape(title)
    cleaned = cleaned.replace(":", " -").replace("/", " - ").replace('"', '').replace("'", "")
    cleaned = re.sub(r'[<>|?*]', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned or "Untitled"


def build_page_paths(pages: list[dict], base_url: str, space_key: str):
    page_map = {}
    
    # Identify parent folders / hierarchy
    for p in pages:
        pid = str(p["id"])
        title = html.unescape(p.get("title", "Untitled"))
        ancestors = p.get("ancestors", [])
        
        # Build relative folder path from ancestors (excluding space root)
        folder_parts = []
        if len(ancestors) > 1:
            for anc in ancestors[1:]:
                folder_parts.append(sanitize_filename(anc.get("title", "")))
        folder = "/".join(part for part in folder_parts if part)

        filename = f"{sanitize_filename(title)}.md"
        rel_path = f"{folder}/{filename}" if folder else filename
        
        confluence_slug = re.sub(r'[^a-zA-Z0-9]+', '+', title).strip('+')
        confluence_url = f"{base_url.rstrip('/')}/wiki/spaces/{space_key}/pages/{pid}/{confluence_slug}"
        
        page_map[pid] = {
            "id": pid,
            "title": title,
            "folder": folder,
            "filename": filename,
            "rel_path": rel_path,
            "confluence_url": confluence_url,
            "data": p
        }
    return page_map


class ConfluenceHTMLToMarkdown(HTMLParser):
    def __init__(self, current_page_id: str, page_map: dict, base_url: str):
        super().__init__()
        self.current_page_id = current_page_id
        self.page_map = page_map
        self.base_url = base_url.rstrip('/')
        self.current_page_folder = page_map[current_page_id]["folder"]
        
        self.out = []
        self.tag_stack = []
        self.table_stack = []
        self.list_stack = []
        self.in_pre = False
        self.in_code = False
        self.current_href = None
        self.current_link_text = []

    def get_markdown(self) -> str:
        text = "".join(self.out)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        self.tag_stack.append((tag, attr_dict))

        if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            level = int(tag[1])
            self.out.append("\n\n" + "#" * level + " ")
        elif tag == "p":
            if not self.table_stack and not (self.list_stack and self.tag_stack[-2][0] == "li" if len(self.tag_stack) > 1 else False):
                self.out.append("\n\n")
        elif tag in ["strong", "b"]:
            self._write("**")
        elif tag in ["em", "i"]:
            self._write("*")
        elif tag in ["s", "del"]:
            self._write("~~")
        elif tag == "code":
            if not self.in_pre:
                self.in_code = True
                self._write("`")
        elif tag == "pre":
            self.in_pre = True
            lang = attr_dict.get("data-syntaxhighlighter-params", "")
            lang_match = re.search(r'brush:\s*([a-zA-Z0-9]+)', lang)
            lang_name = lang_match.group(1) if lang_match else ""
            self.out.append(f"\n\n```{lang_name}\n")
        elif tag == "blockquote":
            self.out.append("\n\n> ")
        elif tag == "hr":
            self.out.append("\n\n---\n\n")
        elif tag == "br":
            if self.table_stack:
                self._write("<br>")
            else:
                self.out.append("\n")
        elif tag == "ul":
            self.list_stack.append(("ul", 0))
            if len(self.list_stack) == 1:
                self.out.append("\n\n")
            else:
                self.out.append("\n")
        elif tag == "ol":
            self.list_stack.append(("ol", 0))
            if len(self.list_stack) == 1:
                self.out.append("\n\n")
            else:
                self.out.append("\n")
        elif tag == "li":
            depth = len(self.list_stack) - 1
            indent = "  " * depth
            if self.list_stack and self.list_stack[-1][0] == "ol":
                l_type, count = self.list_stack[-1]
                count += 1
                self.list_stack[-1] = (l_type, count)
                self.out.append(f"{indent}{count}. ")
            else:
                self.out.append(f"{indent}- ")
        elif tag == "table":
            self.table_stack.append({
                "rows": [],
                "current_row": [],
                "current_cell": [],
                "is_header": False
            })
        elif tag == "tr":
            if self.table_stack:
                self.table_stack[-1]["current_row"] = []
        elif tag in ["th", "td"]:
            if self.table_stack:
                self.table_stack[-1]["current_cell"] = []
                if tag == "th":
                    self.table_stack[-1]["is_header"] = True
        elif tag == "a":
            self.current_href = attr_dict.get("href", "")
            self.current_link_text = []
        elif tag == "div":
            cls = attr_dict.get("class", "")
            if "confluence-information-macro" in cls:
                macro_type = "Note"
                if "confluence-information-macro-tip" in cls:
                    macro_type = "Tip"
                elif "confluence-information-macro-warning" in cls:
                    macro_type = "Warning"
                elif "confluence-information-macro-information" in cls:
                    macro_type = "Info"
                self.out.append(f"\n\n> **{macro_type}**: ")
        elif tag == "span":
            cls = attr_dict.get("class", "")
            if "status-macro" in cls:
                self._write("**[")

    def handle_endtag(self, tag):
        if self.tag_stack and self.tag_stack[-1][0] == tag:
            _, attr_dict = self.tag_stack.pop()
        else:
            attr_dict = {}

        if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            self.out.append("\n\n")
        elif tag == "p":
            if not self.table_stack:
                self.out.append("\n\n")
            else:
                self._write(" ")
        elif tag in ["strong", "b"]:
            self._write("**")
        elif tag in ["em", "i"]:
            self._write("*")
        elif tag in ["s", "del"]:
            self._write("~~")
        elif tag == "code":
            if not self.in_pre:
                self.in_code = False
                self._write("`")
        elif tag == "pre":
            self.in_pre = False
            self.out.append("\n```\n\n")
        elif tag == "blockquote":
            self.out.append("\n\n")
        elif tag in ["ul", "ol"]:
            if self.list_stack:
                self.list_stack.pop()
            if not self.list_stack:
                self.out.append("\n\n")
        elif tag == "li":
            self.out.append("\n")
        elif tag in ["th", "td"]:
            if self.table_stack:
                cell_text = "".join(self.table_stack[-1]["current_cell"]).strip()
                cell_text = cell_text.replace("|", "\\|").replace("\n", "<br>")
                self.table_stack[-1]["current_row"].append(cell_text)
                self.table_stack[-1]["current_cell"] = []
        elif tag == "tr":
            if self.table_stack:
                row = self.table_stack[-1]["current_row"]
                if row:
                    self.table_stack[-1]["rows"].append((row, self.table_stack[-1]["is_header"]))
                self.table_stack[-1]["current_row"] = []
                self.table_stack[-1]["is_header"] = False
        elif tag == "table":
            if self.table_stack:
                table_info = self.table_stack.pop()
                rows = table_info["rows"]
                if rows:
                    max_cols = max(len(r[0]) for r in rows)
                    if max_cols > 0:
                        self.out.append("\n\n")
                        first_row, was_header = rows[0]
                        padded_first = first_row + [""] * (max_cols - len(first_row))
                        self.out.append("| " + " | ".join(padded_first) + " |\n")
                        self.out.append("| " + " | ".join(["---"] * max_cols) + " |\n")
                        for row, _ in rows[1:]:
                            padded = row + [""] * (max_cols - len(row))
                            self.out.append("| " + " | ".join(padded) + " |\n")
                        self.out.append("\n\n")
        elif tag == "a":
            raw_text = "".join(self.current_link_text).strip()
            href = self.current_href or ""
            if href.startswith("/"):
                full_href = self.base_url + href
            else:
                full_href = href
                
            link_text = raw_text if raw_text else full_href
            
            page_id_match = re.search(r'/pages/(\d+)', href)
            if page_id_match and page_id_match.group(1) in self.page_map:
                target_page = self.page_map[page_id_match.group(1)]
                target_rel = target_page["rel_path"]
                if self.current_page_folder:
                    if target_page["folder"] == self.current_page_folder:
                        rel_link = f"./{target_page['filename']}"
                    elif target_page["folder"]:
                        rel_link = f"../{target_page['rel_path']}"
                    else:
                        rel_link = f"../{target_page['filename']}"
                else:
                    rel_link = f"./{target_page['rel_path']}"
                
                if " " in rel_link or "(" in rel_link or ")" in rel_link:
                    md_link = f"[{link_text}](<{rel_link}>)"
                else:
                    md_link = f"[{link_text}]({rel_link})"
            else:
                md_link = f"[{link_text}]({full_href})"
                
            self._write(md_link)
            self.current_href = None
            self.current_link_text = []
        elif tag == "span":
            cls = attr_dict.get("class", "")
            if "status-macro" in cls:
                self._write("]**")

    def handle_data(self, data):
        clean = html.unescape(data)
        if self.current_href is not None:
            self.current_link_text.append(clean)
        else:
            self._write(clean)

    def _write(self, text):
        if self.table_stack and self.table_stack[-1]["current_cell"] is not None:
            self.table_stack[-1]["current_cell"].append(text)
        else:
            self.out.append(text)


def generate_frontmatter(info: dict, space_key: str) -> str:
    p = info["data"]
    title = info["title"].replace('"', '\\"')
    labels = json.dumps(p.get("labels", []))
    ancestors = p.get("ancestors", [])
    parent_title = ancestors[-1].get("title", "Root") if ancestors else "Root"
    author = p.get("author", "Unknown")
    
    fm = [
        "---",
        f'title: "{title}"',
        f'confluence_id: "{info["id"]}"',
        f'confluence_url: "{info["confluence_url"]}"',
        f'space_key: "{space_key}"',
        f'folder: "{info["folder"] or "Root"}"',
        f'parent_title: "{parent_title.replace(chr(34), chr(92)+chr(34))}"',
        f'version: {p.get("version", 1)}',
        f'last_updated: "{p.get("lastUpdated", "")}"',
        f'author: "{author.replace(chr(34), chr(92)+chr(34))}"',
        f'labels: {labels}',
        "---",
        ""
    ]
    return "\n".join(fm)


def generate_header(info: dict, space_key: str) -> str:
    p = info["data"]
    author = p.get("author", "Unknown")
    lines = [
        f"# {info['title']}",
        "",
        f"> **Confluence Source**: [{info['confluence_url']}]({info['confluence_url']})  ",
        f"> **Space**: `{space_key}` | **Page ID**: `{info['id']}` | **Version**: `{p.get('version', 1)}`  ",
        f"> **Last Updated**: `{p.get('lastUpdated', 'Unknown')}` by `{author}`",
        "",
        "---",
        ""
    ]
    return "\n".join(lines)


def generate_index_readme(page_map: dict, space_key: str, base_url: str) -> str:
    content = [
        f"# Confluence Knowledge Base — Space `{space_key}`",
        "",
        f"> Local replication of Confluence space `{space_key}`.  ",
        f"> Source: `{base_url.rstrip('/')}/wiki/spaces/{space_key}`  ",
        "",
        "---",
        "",
        "## Index of Replicated Pages",
        "",
        "| Document | Folder | Confluence ID | Version |",
        "| :--- | :--- | :--- | :--- |"
    ]
    
    sorted_pages = sorted(page_map.values(), key=lambda x: (x["folder"], x["title"]))
    for p in sorted_pages:
        rel = p["rel_path"]
        link = f"[{p['title']}](<{rel}>)"
        folder = p["folder"] or "Root"
        ver = p["data"].get("version", 1)
        content.append(f"| {link} | {folder} | `{p['id']}` | {ver} |")
        
    content.extend([
        "",
        "---",
        "_Replication generated automatically with complete provenance and internal cross-references._",
        ""
    ])
    return "\n".join(content)


def replicate_space(input_json: Path, output_dir: Path, base_url: str, space_key: str) -> int:
    if not input_json.exists():
        print(f"Error: {input_json} does not exist", file=sys.stderr)
        return 1

    with open(input_json, "r", encoding="utf-8") as f:
        pages = json.load(f)

    page_map = build_page_paths(pages, base_url, space_key)
    output_dir.mkdir(parents=True, exist_ok=True)

    for pid, info in page_map.items():
        file_path = output_dir / info["rel_path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)

        parser = ConfluenceHTMLToMarkdown(pid, page_map, base_url)
        parser.feed(info["data"].get("viewHtml", ""))
        body_md = parser.get_markdown()

        frontmatter = generate_frontmatter(info, space_key)
        header = generate_header(info, space_key)
        full_content = f"{frontmatter}{header}{body_md}\n"

        file_path.write_text(full_content, encoding="utf-8")
        print(f"  Replicated: {info['rel_path']}")

    index_path = output_dir / "README.md"
    index_md = generate_index_readme(page_map, space_key, base_url)
    index_path.write_text(index_md, encoding="utf-8")
    print(f"  Generated Index: {index_path.name}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Replicate Confluence Space into Local Markdown")
    parser.add_argument("--input-json", required=True, type=Path, help="Path to JSON dump of Confluence pages")
    parser.add_argument("--output-dir", required=True, type=Path, help="Target directory for Markdown output")
    parser.add_argument("--base-url", required=True, help="Confluence instance base URL")
    parser.add_argument("--space-key", required=True, help="Confluence space key")

    args = parser.parse_args()
    return replicate_space(args.input_json, args.output_dir, args.base_url, args.space_key)


if __name__ == "__main__":
    sys.exit(main())

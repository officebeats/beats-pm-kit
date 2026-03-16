
import base64
import os
import sys

# Usage: python3 md_to_pdf.py input.md output.html

def image_to_base64(path):
    # Support both absolute paths and relative paths
    if not os.path.isabs(path):
        # Assume relative to the script execution directory or handle as needed
        # For now, we assume user provides valid absolute paths in MD or standard relative
        pass
    
    if not os.path.exists(path):
        print(f"WARNING: Image not found: {path}")
        return ""
        
    try:
        with open(path, "rb") as image_file:
            data = image_file.read()
            encoded = base64.b64encode(data).decode('utf-8')
            return encoded
    except Exception as e:
        print(f"ERROR: Error encoding {path}: {e}")
        return ""

def markdown_to_html(md_path, html_path):
    print(f"DEBUG: Converting {md_path} to {html_path}")
    
    if not os.path.exists(md_path):
        print(f"ERROR: Markdown file not found: {md_path}")
        sys.exit(1)

    try:
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
    except Exception as e:
        print(f"ERROR: Failed to read markdown file: {e}")
        sys.exit(1)

    # CSS for Professional Look
    css = """
        body { font-family: 'Helvetica', 'Arial', sans-serif; max-width: 850px; margin: 40px auto; line-height: 1.6; color: #333; }
        h1 { border-bottom: 2px solid #333; padding-bottom: 10px; margin-top: 40px; page-break-before: always; }
        h1:first-of-type { page-break-before: auto; }
        h2 { margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 5px; color: #2c3e50; }
        h3 { margin-top: 25px; color: #34495e; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 14px; page-break-inside: avoid; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f8f9fa; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        img { max-width: 100%; height: auto; border: 1px solid #ddd; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 20px 0; display: block; page-break-inside: avoid; }
        blockquote { border-left: 4px solid #007bff; margin: 20px 0; padding: 10px 20px; background-color: #e9ecef; color: #495057; }
        .warning { background-color: #fff3cd; border: 1px solid #ffeeba; padding: 15px; border-radius: 5px; color: #856404; margin: 20px 0; }
        code { background-color: #f8f9fa; padding: 2px 4px; border-radius: 4px; font-family: 'Consolas', monospace; font-size: 0.9em; border: 1px solid #e9ecef; }
        pre { background-color: #f8f9fa; padding: 15px; border-radius: 5px; border: 1px solid #e9ecef; overflow-x: auto; }
        pre code { border: none; padding: 0; background: none; }
        ul { padding-left: 20px; }
        li { margin-bottom: 5px; }
        .mermaid { display: none; }
    """

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Document Export</title>
    <style>{css}</style>
</head>
<body>
"""
    
    lines = md_content.splitlines()
    in_table = False
    in_code_block = False
    
    for line in lines:
        line = line.strip()

        # Skip carousel markers
        if "````carousel" in line or "````" in line or "<!-- slide -->" in line:
            continue
        
        # Code blocks
        if line.startswith("```"):
            if in_code_block:
                html_content += "</code></pre>"
                in_code_block = False
            else:
                html_content += "<pre><code>"
                in_code_block = True
            continue
            
        if in_code_block:
            html_content += line + "\\n"
            continue

        # Images (Markdown syntax: ![Alt](Src))
        # Logic: find `![` and `](` and `)`
        if "![" in line and "](" in line:
             try:
                # Naive match
                parts = line.split("](")
                alt = parts[0].split("![")[1]
                src = parts[1].split(")")[0]
                
                # If src is valid, encode it
                if src:
                    b64 = image_to_base64(src)
                    if b64:
                        html_content += f'<div style="text-align:center"><img src="data:image/png;base64,{b64}" alt="{alt}"><br><em>{alt}</em></div>'
                    else:
                        # Fallback to text if image not found
                        html_content += f"<p><strong>[Image Not Found: {src}]</strong></p>"
             except IndexError:
                html_content += f"<p>{line}</p>"
             continue

        # Simple Markdown Parsing
        
        # Headers
        if line.startswith("# "):
            html_content += f"<h1>{line[2:]}</h1>"
            continue
        elif line.startswith("## "):
            html_content += f"<h2>{line[3:]}</h2>"
            continue
        elif line.startswith("### "):
            html_content += f"<h3>{line[4:]}</h3>"
            continue
        
        # Horizontal Rule
        elif line == "---":
            html_content += "<hr>"
            continue

        # Tables
        if line.startswith("|"):
            if not in_table:
                html_content += "<table>"
                in_table = True
            
            if "---" in line:
                continue
                
            cells = [c.strip() for c in line.split("|") if c.strip()]
            row_html = "<tr>"
            for cell in cells:
                cell = cell.replace("**", "<b>").replace("**", "</b>")
                cell = cell.replace("`", "<code>").replace("`", "</code>")
                row_html += f"<td>{cell}</td>"
            row_html += "</tr>"
            html_content += row_html
            continue
            
        elif in_table and not line.startswith("|"):
            html_content += "</table>"
            in_table = False
            
        # Lists
        if line.startswith("- [ ]") or line.startswith("- [x]"):
            icon = "☑" if "[x]" in line else "☐"
            text = line[6:]
            text = text.replace("**", "<b>").replace("**", "</b>").replace("`", "<code>").replace("`", "</code>")
            html_content += f'<div style="margin-left: 20px; margin-bottom: 5px;">{icon} {text}</div>'
            continue
        elif line.startswith("- "):
            text = line[2:]
            text = text.replace("**", "<b>").replace("**", "</b>").replace("`", "<code>").replace("`", "</code>")
            # Link Parsing [Text](Url)
            if "](" in text:
                try:
                    parts = text.split("](")
                    if len(parts) == 2:
                        link_text = parts[0].split("[")[-1]
                        link_url = parts[1].split(")")[0]
                        pre = parts[0].split("[")[0]
                        post = parts[1].split(")", 1)[1] if ")" in parts[1] else ""
                        text = f'{pre}<a href="{link_url}">{link_text}</a>{post}'
                except: pass
            html_content += f"<ul><li>{text}</li></ul>"
            continue
            
        # Blockquotes / Alerts
        if line.startswith(">"):
            content = line[1:].strip()
            alert_class = ""
            if "[!IMPORTANT]" in content or "[!WARNING]" in content:
                alert_class = "warning"
                content = content.replace("[!IMPORTANT]", "<strong>IMPORTANT:</strong>").replace("[!WARNING]", "<strong>WARNING:</strong>")
            content = content.replace("**", "<b>").replace("**", "</b>")
            html_content += f'<blockquote class="{alert_class}">{content}</blockquote>'
            continue
            
        # Normal text (paragraph)
        if line:
            line = line.replace("**", "<b>").replace("**", "</b>")
            line = line.replace("`", "<code>").replace("`", "</code>")
            html_content += f"<p>{line}</p>"

    if in_table:
        html_content += "</table>"

    html_content += "</body></html>"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML written to {html_path} ({len(html_content)} bytes)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 md_to_pdf.py <input.md> <output.html>")
        sys.exit(1)
        
    markdown_to_html(sys.argv[1], sys.argv[2])

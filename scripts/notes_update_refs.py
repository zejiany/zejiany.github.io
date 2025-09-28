#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Update "Reference" sections in Markdown files based on bibfile + citekeys
declared in the YAML frontmatter.

Example frontmatter:

---
title: 'Source inference'
date: 2025-09-28
permalink: /posts/2025/08/source-inference/
tags:
  - passive scalar
bibfile: "reference.bib"
citekeys:
  - alapatiRecoveringReleaseHistory2000
  - brandtPhysicsVortexMerger2007
---

The script (re)generates everything between:
<!-- BEGIN:references -->
... generated content ...
<!-- END:references -->
"""

import argparse
import glob
import os
import re
import shutil
from datetime import datetime

import yaml  # pip install pyyaml
import bibtexparser

BEGIN_MARK = "<!-- BEGIN:references -->"
END_MARK = "<!-- END:references -->"

HAS_STYLE_RE = re.compile(r"<style>.*?</style>", re.DOTALL | re.IGNORECASE)

DEFAULT_STYLE = """<style>
p {
  font-family: sans;
}
a:link {
  color: navy; 
  background-color: transparent; 
  text-decoration: none;
}
ol {
columns:1;
}
ol > li::marker {
content:"["counter(list-item) "] ";
}
</style>
"""

# Cache loaded .bib files
_BIB_CACHE = {}


def clean_bibtex_braces(text: str) -> str:
    """Remove nested braces from BibTeX titles like {Two-{{Dimensional Turbulence}}}."""
    if not text:
        return ""
    # Remove outermost braces
    cleaned = text.strip()
    if cleaned.startswith("{") and cleaned.endswith("}"):
        cleaned = cleaned[1:-1]
    # Remove any remaining double or single braces
    cleaned = re.sub(r"[{}]", "", cleaned)
    return cleaned.strip()

def make_backup(path):
    folder = os.path.dirname(path)
    fname = os.path.basename(path)
    root, _ = os.path.splitext(fname)   # remove .md / .markdown
    # Drop leading date-like prefix if present (YYYY-MM-DD-)
    parts = root.split("-", 3)
    if len(parts) >= 4 and parts[0].isdigit() and parts[1].isdigit() and parts[2].isdigit():
        root = parts[3]
    backup_name = f"tmp-{root}.bak"
    backup_path = os.path.join(folder, backup_name)
    shutil.copyfile(path, backup_path)
    return backup_path

def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def format_authors(author_field: str) -> str:
    """Convert BibTeX 'author' to 'Last, F.' joined by ' and '."""
    if not author_field:
        return ""
    out = []
    for raw in author_field.split(" and "):
        name = raw.strip()
        if not name:
            continue
        parts = [p.strip() for p in name.split(",")]
        if len(parts) == 2:
            last, first = parts[0], parts[1]
        else:
            words = name.split()
            last = words[-1]
            first = " ".join(words[:-1]) if len(words) > 1 else ""
        initials = " ".join([w[0] + "." for w in first.split() if w])
        out.append(f"{last}, {initials}" if initials else last)
    return " and ".join(out)

def entry_link(entry: dict) -> str:
    doi = (entry.get("doi") or "").strip()
    url = (entry.get("url") or "").strip()
    if doi:
        if doi.lower().startswith("10."):
            return "https://doi.org/" + doi
        if "doi.org" in doi:
            return doi
        return url or doi
    return url

def safe_get(entry: dict, key: str) -> str:
    return (entry.get(key) or "").strip()

def format_reference_html(key: str, entry: dict) -> str:
    authors = format_authors(safe_get(entry, "author"))
    year = safe_get(entry, "year")
    raw_title = safe_get(entry, "title")
    title = normalize_whitespace(clean_bibtex_braces(raw_title))
    journal = safe_get(entry, "journal")
    volume = safe_get(entry, "volume")
    number = safe_get(entry, "number")
    pages = safe_get(entry, "pages")
    link = entry_link(entry)

    author_html = f'<span style="font-variant: small-caps"> {authors} </span>' if authors else ""

    parts = []
    parts.append(f'1. <p id="{key}">')
    if author_html:
        parts.append(f" {author_html} ")
    if year:
        parts.append(f"{year} ")

    if title:
        if link:
            parts.append(f' <a href="{link}"> {title}. </a>')
        else:
            parts.append(f" {title}. ")

    if journal:
        parts.append(f" <i> {journal}</i>")
    if volume:
        parts.append(f" <b> {volume} </b>")
    if number:
        parts.append(f" ({number})")
    if pages:
        parts.append(f" {pages}")

    parts.append("</p>")
    return "".join(parts)

def has_style_block(md_text: str) -> bool:
    return bool(HAS_STYLE_RE.search(md_text))

def generate_reference_block(keys, bib_map, add_style=True) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    if add_style:
        lines.append(DEFAULT_STYLE.strip())
        lines.append("")

    lines.append("# Reference")
    lines.append(f"Generated bibliography markdown file. Date: {now}")

    missing = []
    for k in keys:
        entry = bib_map.get(k)
        if not entry:
            missing.append(k)
            continue
        lines.append(format_reference_html(k, entry))
        lines.append("")

    if missing:
        lines.append("> **Note:** Missing BibTeX entries for keys: " + ", ".join(missing))

    content = "\n".join(lines).rstrip() + "\n"
    return f"{BEGIN_MARK}\n{content}\n{END_MARK}\n"

def insert_or_replace_reference_block(md_text: str, new_block: str) -> str:
    if BEGIN_MARK in md_text and END_MARK in md_text:
        pattern = re.compile(
            re.escape(BEGIN_MARK) + r".*?" + re.escape(END_MARK),
            flags=re.DOTALL
        )
        return pattern.sub(new_block.strip(), md_text, count=1)
    else:
        if not md_text.endswith("\n"):
            md_text += "\n"
        if not md_text.endswith("\n\n"):
            md_text += "\n"
        return md_text + new_block

def load_bib_map(bib_path: str) -> dict:
    if bib_path in _BIB_CACHE:
        return _BIB_CACHE[bib_path]
    with open(bib_path, "r", encoding="utf-8") as f:
        db = bibtexparser.load(f)
    bib_map = {e.get("ID", ""): e for e in db.entries}
    _BIB_CACHE[bib_path] = bib_map
    return bib_map

def extract_frontmatter(md_text: str):
    """
    Return (yaml_dict, rest_of_file).
    """
    if not md_text.startswith("---"):
        return {}, md_text
    parts = md_text.split("---", 2)
    if len(parts) < 3:
        return {}, md_text
    yaml_block, rest = parts[1], parts[2]
    try:
        data = yaml.safe_load(yaml_block)
        if not isinstance(data, dict):
            return {}, md_text
        return data, "---".join(["", yaml_block, rest])
    except yaml.YAMLError:
        return {}, md_text

def process_file(path: str, inline_style: bool = True, dry_run: bool = False, base_folder: str = "."):
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    front, _ = extract_frontmatter(original)
    bibfile = front.get("bibfile")
    keys = front.get("citekeys", [])

    if not bibfile or not keys:
        return False, "No bibfile or citekeys in frontmatter."

    bib_path = os.path.join(base_folder, bibfile) if not os.path.isabs(bibfile) else bibfile
    if not os.path.exists(bib_path):
        return False, f"Bib file not found: {bibfile}"

    bib_map = load_bib_map(bib_path)

    add_style = inline_style
    block = generate_reference_block(keys, bib_map, add_style=add_style)
    updated = insert_or_replace_reference_block(original, block)

    if updated == original:
        return False, "No changes."

    if dry_run:
        return True, "Would update (dry run)."

    backup = make_backup(path)
    shutil.copyfile(path, backup)
    with open(path, "w", encoding="utf-8") as f:
        f.write(updated)
    return True, f"Updated. Backup: {os.path.basename(backup)}"

def main():
    ap = argparse.ArgumentParser(description="Update Markdown references from YAML frontmatter (bibfile + citekeys).")
    ap.add_argument("--folder", required=True, help="Folder containing Markdown files.")
    ap.add_argument("--style-inline", action="store_true",
                    help="Insert <style> block above Reference header if missing.")
    ap.add_argument("--dry-run", action="store_true", help="Show planned changes without writing files.")
    args = ap.parse_args()

    md_paths = sorted(
        [p for ext in ("*.md", "*.markdown") for p in glob.glob(os.path.join(args.folder, ext))]
    )
    if not md_paths:
        print("No Markdown files found.")
        return

    changed = 0
    for p in md_paths:
        updated, msg = process_file(
            p,
            inline_style=args.style_inline,
            dry_run=args.dry_run,
            base_folder=args.folder
        )
        rel = os.path.relpath(p, args.folder)
        prefix = "[CHANGED]" if updated else "[SKIP]"
        print(f"{prefix} {rel}: {msg}")
        if updated and not args.dry_run:
            changed += 1

    if not args.dry_run:
        print(f"\nDone. Files updated: {changed}/{len(md_paths)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:  # no args passed
        # Debug mode: run main() with test args
        sys.argv.extend([
            "--folder", "scripts/test_update_ref",   # adjust your folder
            "--dry-run",           # don’t overwrite files
        ])
    main()

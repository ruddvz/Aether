#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"

repository = os.environ.get("GITHUB_REPOSITORY", "ruddvz/Aether").strip()
if "/" not in repository:
    raise SystemExit(f"Invalid GITHUB_REPOSITORY value: {repository!r}")
owner, repo = repository.split("/", 1)

github_base = f"https://github.com/{owner}/{repo}"
pages_base = f"https://{owner}.github.io/{repo}/"

github_candidates = {
    "https://github.com/ruddvz/Aether",
    "https://github.com/ruddvz/aethar",
}
pages_candidates = {
    "https://ruddvz.github.io/Aether/",
    "https://ruddvz.github.io/aethar/",
}

text_suffixes = {".html", ".json", ".xml", ".txt", ".js", ".css", ".svg"}
changed_files = 0
replacement_count = 0

if not OUT.exists():
    raise SystemExit("_site does not exist; run scripts/build_site.py first")

for path in sorted(OUT.rglob("*")):
    if not path.is_file() or path.suffix.lower() not in text_suffixes:
        continue
    original = path.read_text(encoding="utf-8")
    updated = original
    for candidate in github_candidates:
        count = updated.count(candidate)
        if count:
            replacement_count += count
            updated = updated.replace(candidate, github_base)
    for candidate in pages_candidates:
        count = updated.count(candidate)
        if count:
            replacement_count += count
            updated = updated.replace(candidate, pages_base)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        changed_files += 1

print(
    f"Prepared AETHERIA Pages artifact for {repository}: "
    f"{changed_files} file(s), {replacement_count} replacement(s), base {pages_base}"
)

"""Documentation search tool for TI5 Motor Agent.

Searches project documentation files for keywords and topics.
"""

import os
import re
from pathlib import Path

_project_root = os.environ.get("TI5_PROJECT_ROOT", os.path.expanduser("~/test-ti5-kkw"))


def search_docs(query: str, path: str = "docs/") -> dict:
    """Search project documentation for a keyword or topic.

    Searches markdown files for the query string (case-insensitive).
    Returns matching file paths and context snippets.

    Args:
        query: Search query (keyword or topic)
        path: Directory to search in, relative to project root (default: docs/)
    """
    search_dir = os.path.join(_project_root, path)
    if not os.path.isdir(search_dir):
        return {"success": False, "error": f"Directory not found: {search_dir}"}

    results = []
    query_lower = query.lower()
    pattern = re.compile(re.escape(query), re.IGNORECASE)

    for root, dirs, files in os.walk(search_dir):
        for fname in sorted(files):
            if not fname.endswith((".md", ".py", ".txt")):
                continue

            fpath = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, _project_root)

            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except Exception:
                continue

            matches = list(pattern.finditer(content))
            if not matches:
                continue

            # Extract context snippets (up to 3)
            snippets = []
            lines = content.split("\n")
            seen_lines = set()

            for match in matches[:3]:
                # Find line number
                line_num = content[:match.start()].count("\n")
                if line_num in seen_lines:
                    continue
                seen_lines.add(line_num)

                start = max(0, line_num - 1)
                end = min(len(lines), line_num + 3)
                snippet = "\n".join(lines[start:end]).strip()
                if len(snippet) > 300:
                    snippet = snippet[:300] + "..."
                snippets.append({"line": line_num + 1, "text": snippet})

            results.append({
                "file": rel_path,
                "match_count": len(matches),
                "snippets": snippets,
            })

    # Sort by match count descending
    results.sort(key=lambda x: x["match_count"], reverse=True)

    return {
        "success": True,
        "query": query,
        "total_files": len(results),
        "results": results[:10],  # Top 10 files
    }

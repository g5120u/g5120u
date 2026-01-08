from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from ._lib import ensure_dir, repo_root


@dataclass(frozen=True)
class Evidence:
    path: str  # relative to evidence/
    title: str
    date: str
    tags: list[str]
    repo: str

    @property
    def tags_text(self) -> str:
        return ", ".join(self.tags) if self.tags else ""


def _parse_front_matter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}, text
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}, text
    fm_text = "\n".join(lines[1:end_idx]).strip() + "\n"
    body = "\n".join(lines[end_idx + 1 :]).lstrip("\n")
    data = yaml.safe_load(fm_text) or {}
    if not isinstance(data, dict):
        data = {}
    return data, body


def _guess_title(body: str, fallback: str) -> str:
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return fallback


def _normalize_tags(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, str):
        return [t.strip() for t in v.split(",") if t.strip()]
    if isinstance(v, list):
        out = []
        for x in v:
            if x is None:
                continue
            out.append(str(x).strip())
        return [t for t in out if t]
    return [str(v).strip()] if str(v).strip() else []


def _normalize_date(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, datetime):
        return v.strftime("%Y-%m-%d")
    s = str(v).strip()
    return s


def collect_evidence(evidence_dir: Path) -> list[Evidence]:
    items: list[Evidence] = []
    for p in sorted(evidence_dir.glob("*.md")):
        if p.name.startswith("_template"):
            continue
        text = p.read_text(encoding="utf-8")
        fm, body = _parse_front_matter(text)

        title = str(fm.get("title", "")).strip() or _guess_title(body, p.stem)
        date = _normalize_date(fm.get("date", "")).strip()
        tags = _normalize_tags(fm.get("tags"))
        repo = str(fm.get("repo", "")).strip()

        items.append(
            Evidence(
                path=p.name,
                title=title,
                date=date,
                tags=tags,
                repo=repo,
            )
        )

    def sort_key(ev: Evidence) -> tuple[int, str]:
        # Prefer valid YYYY-MM-DD; else push to bottom.
        try:
            dt = datetime.strptime(ev.date, "%Y-%m-%d")
            return (0, dt.strftime("%Y%m%d"))
        except Exception:
            return (1, ev.date)

    return sorted(items, key=sort_key, reverse=True)


def write_index(evidence: list[Evidence], out_path: Path) -> None:
    ensure_dir(out_path.parent)
    lines: list[str] = []
    lines.append("# Evidence Vault（實戰證據庫）")
    lines.append("")
    lines.append("> 目的：把「我會什麼」落地成「我做過且可驗證」。")
    lines.append("")

    if not evidence:
        lines.append("目前尚無 evidence。你可以先從 `evidence/sample-case-study.md` 複製一份開始。")
        lines.append("")
        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return

    lines.append("| Date | Title | Tags | Repo |")
    lines.append("|---|---|---|---|")
    for ev in evidence:
        date = ev.date or "-"
        title = ev.title.replace("|", "\\|")
        tags = ev.tags_text.replace("|", "\\|")
        repo = (ev.repo or "-").replace("|", "\\|")
        link = f"[{title}](../evidence/{ev.path})"
        lines.append(f"| {date} | {link} | {tags} | {repo} |")
    lines.append("")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate() -> list[Evidence]:
    root = repo_root()
    evidence_dir = root / "evidence"
    ensure_dir(evidence_dir)
    items = collect_evidence(evidence_dir)
    write_index(items, root / "generated" / "evidence-index.md")
    return items


def main() -> None:
    items = generate()
    print(f"Indexed evidence: {len(items)}")


if __name__ == "__main__":
    main()


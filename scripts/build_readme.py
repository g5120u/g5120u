from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from ._lib import ensure_dir, read_yaml, repo_root
from .generate_skill_radar import generate as generate_skill_radar
from .github_recent import fetch_recent_repos, fetch_repo_month_range


def _month_now_utc() -> str:
    now = datetime.now(timezone.utc)
    return f"{now.year:04d}-{now.month:02d}"


def _project_status_to_gantt(status: str) -> str:
    s = (status or "").strip().lower()
    if s in {"active", "in-progress", "in_progress"}:
        return "active"
    if s in {"maintained"}:
        return "active"
    if s in {"paused"}:
        return "crit"
    if s in {"archived"}:
        return "done"
    return "active"


def build_mermaid_lines(projects: list[dict[str, Any]]) -> list[str]:
    lines: list[str] = []
    lines.append("section Projects")
    now = _month_now_utc()
    for p in projects:
        name = str(p.get("name", "")).strip() or str(p.get("key", "project"))
        status = _project_status_to_gantt(str(p.get("status", "")))
        repo = str(p.get("repo", "")).strip()

        # Prefer real dates from GitHub (created_at -> pushed_at)
        start_end = None
        if repo and "/" in repo:
            try:
                start_end = fetch_repo_month_range(repo)
            except Exception:
                start_end = None

        if start_end:
            start, end = start_end
        else:
            period = p.get("period", {}) if isinstance(p.get("period"), dict) else {}
            start = str(period.get("start", "")).strip() or now
            end = str(period.get("end", "")).strip() or now
        # Mermaid gantt: "Task :active, 2025-01, 2025-03"
        lines.append(f"{name} :{status}, {start}, {end}")
    return lines


def build_project_timeline(projects: list[dict[str, Any]]) -> list[dict[str, str]]:
    """
    Timeline shown on README (avoid Mermaid viewer overlay on GitHub).
    Prefer real timestamps from GitHub (created_at -> pushed_at month), fallback to YAML period.
    """
    now = _month_now_utc()
    rows: list[dict[str, str]] = []
    for p in projects:
        name = str(p.get("name", "")).strip() or str(p.get("key", "project"))
        repo = str(p.get("repo", "")).strip()
        status = str(p.get("status", "")).strip() or "active"

        start_end = None
        if repo and "/" in repo:
            try:
                start_end = fetch_repo_month_range(repo)
            except Exception:
                start_end = None

        if start_end:
            start, end = start_end
        else:
            period = p.get("period", {}) if isinstance(p.get("period"), dict) else {}
            start = str(period.get("start", "")).strip() or now
            end = str(period.get("end", "")).strip() or now

        rows.append(
            {
                "name": name,
                "repo": repo,
                "status": status,
                "start": start,
                "end": end,
            }
        )
    return rows


def load_data() -> dict[str, Any]:
    root = repo_root()
    profile = read_yaml(root / "data" / "profile.yml")
    skills = read_yaml(root / "data" / "skills.yml")
    projects_doc = read_yaml(root / "data" / "projects.yml")

    username = str(profile.get("username", "")).strip() or "g5120u"

    identity = profile.get("identity", {}) if isinstance(profile.get("identity"), dict) else {}
    identity_zh = identity.get("zh", {}) if isinstance(identity.get("zh"), dict) else {}
    identity_en = identity.get("en", {}) if isinstance(identity.get("en"), dict) else {}

    links = profile.get("links", {}) if isinstance(profile.get("links"), dict) else {}

    engine = profile.get("engine", {}) if isinstance(profile.get("engine"), dict) else {}
    engine_zh = engine.get("zh", {}) if isinstance(engine.get("zh"), dict) else {}
    engine_en = engine.get("en", {}) if isinstance(engine.get("en"), dict) else {}

    projects = projects_doc.get("projects", [])
    if not isinstance(projects, list):
        projects = []

    mermaid_lines = build_mermaid_lines(projects)
    project_timeline = build_project_timeline(projects)

    # Recent repos (auto-updated when you push elsewhere; refreshed by schedule)
    recent_repos = []
    recent_repos_error = ""
    try:
        recent_repos = fetch_recent_repos(username, limit=6)
    except Exception as e:
        recent_repos_error = str(e)

    return {
        "username": username,
        "identity_zh": identity_zh,
        "identity_en": identity_en,
        "links": links,
        "engine_zh": engine_zh,
        "engine_en": engine_en,
        "projects": projects,
        "skills": skills,
        "mermaid_lines": mermaid_lines,
        "project_timeline": project_timeline,
        "recent_repos": recent_repos,
        "recent_repos_error": recent_repos_error,
    }


def render_readme(context: dict[str, Any]) -> str:
    root = repo_root()
    env = Environment(
        loader=FileSystemLoader(str(root / "templates")),
        autoescape=False,
        keep_trailing_newline=True,
    )
    tpl = env.get_template("profile_readme.md.j2")
    return tpl.render(**context)


def build() -> Path:
    root = repo_root()
    ensure_dir(root / "assets")

    # Generate assets / indexes
    generate_skill_radar()

    context = load_data()

    # Display in Asia/Taipei (UTC+8) to match what you see day-to-day.
    tz_tw = timezone(timedelta(hours=8))
    now_tw = datetime.now(timezone.utc).astimezone(tz_tw)
    context["generated_at"] = now_tw.strftime("%Y-%m-%d %H:%M (UTC+8)")
    readme = render_readme(context)
    out = root / "README.md"
    out.write_text(readme, encoding="utf-8")
    return out


def main() -> None:
    out = build()
    print(f"Wrote: {out}")


if __name__ == "__main__":
    main()


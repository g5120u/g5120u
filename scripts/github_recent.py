from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib.request import Request, urlopen


def _get_json(url: str, *, timeout: int = 20) -> Any:
    req = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "profile-readme-bot",
        },
        method="GET",
    )
    with urlopen(req, timeout=timeout) as resp:  # nosec - url is trusted
        return json.loads(resp.read().decode("utf-8"))


@dataclass(frozen=True)
class RecentRepo:
    full_name: str
    html_url: str
    description: str
    language: str
    pushed_at: str
    stargazers_count: int

    @property
    def name(self) -> str:
        return self.full_name.split("/")[-1]

    @property
    def pushed_date(self) -> str:
        # ISO 8601 -> YYYY-MM-DD (keep UTC date)
        try:
            dt = datetime.fromisoformat(self.pushed_at.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return self.pushed_at


def fetch_recent_repos(username: str, *, limit: int = 6, include_forks: bool = False) -> list[RecentRepo]:
    # Public endpoint; rate-limited but fine for a profile README job.
    url = f"https://api.github.com/users/{username}/repos?sort=pushed&per_page={max(1, min(limit, 20))}&type=owner"
    data = _get_json(url)
    if not isinstance(data, list):
        return []

    out: list[RecentRepo] = []
    for r in data:
        if not isinstance(r, dict):
            continue
        if (not include_forks) and bool(r.get("fork")):
            continue
        out.append(
            RecentRepo(
                full_name=str(r.get("full_name", "")).strip(),
                html_url=str(r.get("html_url", "")).strip(),
                description=str(r.get("description") or "").strip(),
                language=str(r.get("language") or "").strip(),
                pushed_at=str(r.get("pushed_at") or "").strip(),
                stargazers_count=int(r.get("stargazers_count") or 0),
            )
        )
        if len(out) >= limit:
            break
    return out


def fetch_repo_month_range(full_name: str) -> tuple[str, str] | None:
    # Returns (created_YYYY-MM, pushed_YYYY-MM)
    url = f"https://api.github.com/repos/{full_name}"
    r = _get_json(url)
    if not isinstance(r, dict):
        return None
    created_at = str(r.get("created_at") or "").strip()
    pushed_at = str(r.get("pushed_at") or "").strip()
    if not created_at or not pushed_at:
        return None

    def to_month(s: str) -> str:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m")

    return to_month(created_at), to_month(pushed_at)


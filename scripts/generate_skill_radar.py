from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from ._lib import clamp, ensure_dir, read_yaml, repo_root


@dataclass(frozen=True)
class RadarAxis:
    zh: str
    en: str
    score: float


def _svg_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _poly_points(cx: float, cy: float, r: float, angles: list[float]) -> str:
    pts = []
    for a in angles:
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        pts.append(f"{x:.2f},{y:.2f}")
    return " ".join(pts)


def build_radar_svg(
    *,
    title: str,
    axes: list[RadarAxis],
    max_score: float,
    size: int = 720,
    padding: int = 120,
) -> str:
    if len(axes) < 3:
        raise ValueError("Radar requires at least 3 axes")

    w = h = size
    cx = cy = size / 2
    radius = (size / 2) - padding

    # Start at -90 degrees (top), go clockwise.
    n = len(axes)
    angles = [(-math.pi / 2) + (2 * math.pi * i / n) for i in range(n)]

    # Grid rings
    rings = int(max_score)
    grid_polys = []
    for k in range(1, rings + 1):
        r = radius * (k / max_score)
        grid_polys.append(_poly_points(cx, cy, r, angles))

    # Axes lines + labels
    axis_lines = []
    labels = []
    for i, ax in enumerate(axes):
        a = angles[i]
        x2 = cx + radius * math.cos(a)
        y2 = cy + radius * math.sin(a)
        axis_lines.append((cx, cy, x2, y2))

        # Keep labels inside viewbox to avoid being cut on GitHub.
        label_r = radius + 12
        lx = cx + label_r * math.cos(a)
        ly = cy + label_r * math.sin(a)

        # text-anchor based on angle
        ca = math.cos(a)
        anchor = "middle"
        if ca > 0.35:
            anchor = "start"
        elif ca < -0.35:
            anchor = "end"

        # Clamp label positions to safe margins (helps long text)
        margin = 16.0
        lx = clamp(lx, margin, w - margin)
        ly = clamp(ly, 96.0, h - 56.0)  # reserve space for 2 lines

        labels.append((lx, ly, anchor, _svg_escape(ax.zh), _svg_escape(ax.en)))

    # Value polygon
    value_pts = []
    for i, ax in enumerate(axes):
        score = clamp(ax.score, 0, max_score)
        r = radius * (score / max_score)
        a = angles[i]
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        value_pts.append(f"{x:.2f},{y:.2f}")
    value_poly = " ".join(value_pts)

    title_esc = _svg_escape(title)

    # SVG
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">')
    parts.append("<defs>")
    parts.append(
        "<style>"
        "text{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;"
        "fill:#111827}"
        ".muted{fill:#6b7280}"
        ".grid{fill:none;stroke:#e5e7eb;stroke-width:2}"
        ".axis{stroke:#d1d5db;stroke-width:2}"
        ".value{fill:rgba(37,99,235,0.20);stroke:#2563eb;stroke-width:3}"
        "</style>"
    )
    parts.append("</defs>")

    # Background
    parts.append('<rect x="0" y="0" width="100%" height="100%" fill="white"/>')

    # Title
    parts.append(f'<text x="{cx:.2f}" y="48" text-anchor="middle" font-size="22" font-weight="700">{title_esc}</text>')
    parts.append(f'<text x="{cx:.2f}" y="72" text-anchor="middle" class="muted" font-size="14">relative capability focus, not an exam score</text>')

    # Grid
    for pts in grid_polys:
        parts.append(f'<polygon class="grid" points="{pts}"/>')

    # Axes
    for x1, y1, x2, y2 in axis_lines:
        parts.append(f'<line class="axis" x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')

    # Value polygon
    parts.append(f'<polygon class="value" points="{value_poly}"/>')

    # Labels
    for x, y, anchor, zh, en in labels:
        if zh:
            parts.append(f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" font-size="14" font-weight="700">{zh}</text>')
        if en:
            parts.append(
                f'<text x="{x:.2f}" y="{(y + 16):.2f}" text-anchor="{anchor}" class="muted" font-size="12" font-weight="600">{en}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def build_boundary_svg(*, size_w: int = 960, size_h: int = 460) -> str:
    public_items = [
        "Google Play availability signal",
        "Live mobile demonstration",
        "Public samples with mock data",
        "GitHub activity and learning labs",
    ]
    private_items = [
        "Source code",
        "Settlement flow",
        "Operations details",
        "Data design and business logic",
    ]

    def text_lines(items: list[str], *, x: int, y: int) -> list[str]:
        lines = []
        for i, item in enumerate(items):
            yy = y + (i * 34)
            lines.append(f'<text x="{x}" y="{yy}" class="item">- {_svg_escape(item)}</text>')
        return lines

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{size_w}" height="{size_h}" viewBox="0 0 {size_w} {size_h}">')
    parts.append("<defs>")
    parts.append(
        "<style>"
        "text{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;fill:#111827}"
        ".muted{fill:#6b7280}"
        ".panel{fill:#ffffff;stroke:#d1d5db;stroke-width:2}"
        ".public{fill:#ecfdf5;stroke:#10b981;stroke-width:2}"
        ".private{fill:#fff7ed;stroke:#f97316;stroke-width:2}"
        ".title{font-size:24px;font-weight:800}"
        ".heading{font-size:20px;font-weight:800}"
        ".item{font-size:15px;font-weight:650}"
        ".caption{font-size:14px;font-weight:650}"
        "</style>"
    )
    parts.append("</defs>")
    parts.append('<rect width="100%" height="100%" fill="#f9fafb"/>')
    parts.append('<text x="480" y="44" text-anchor="middle" class="title">Public / Private Boundary | 公開與私有邊界</text>')
    parts.append('<text x="480" y="72" text-anchor="middle" class="muted caption">Show delivery capability without exposing the system blueprint.</text>')
    parts.append('<rect x="60" y="105" width="390" height="270" rx="14" class="public"/>')
    parts.append('<rect x="510" y="105" width="390" height="270" rx="14" class="private"/>')
    parts.append('<text x="90" y="150" class="heading">Public Signals</text>')
    parts.append('<text x="540" y="150" class="heading">Kept Private</text>')
    parts.extend(text_lines(public_items, x=90, y=196))
    parts.extend(text_lines(private_items, x=540, y=196))
    parts.append('<line x1="480" y1="118" x2="480" y2="362" stroke="#9ca3af" stroke-width="2" stroke-dasharray="8 8"/>')
    parts.append('<text x="480" y="405" text-anchor="middle" class="muted caption">The public profile is a controlled portfolio surface, not a full product handoff.</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def build_engineering_evidence_svg(*, size_w: int = 960, size_h: int = 430) -> str:
    rows = [
        ("Public profile", "capability radar, boundary map, public repo activity", "no source code or product rules"),
        ("Safe evidence", "redacted screenshots, QA notes, issue-style summaries", "no real data, secrets, or full flows"),
        ("Controlled demo", "phone demo, selected behavior walkthrough", "no open download link or public credentials"),
        ("Technical review", "limited diff reading, call-path explanation, test result discussion", "no full repo handoff"),
    ]

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{size_w}" height="{size_h}" viewBox="0 0 {size_w} {size_h}">')
    parts.append("<defs>")
    parts.append(
        "<style>"
        "text{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;fill:#111827}"
        ".muted{fill:#6b7280}"
        ".title{font-size:24px;font-weight:850}"
        ".head{font-size:16px;font-weight:850}"
        ".cell{font-size:13px;font-weight:650}"
        ".box{fill:#ffffff;stroke:#d1d5db;stroke-width:2}"
        ".safe{fill:#eff6ff;stroke:#3b82f6;stroke-width:2}"
        ".private{fill:#fef2f2;stroke:#ef4444;stroke-width:2}"
        "</style>"
    )
    parts.append("</defs>")
    parts.append('<rect width="100%" height="100%" fill="#f8fafc"/>')
    parts.append('<text x="480" y="42" text-anchor="middle" class="title">Engineering Evidence Without Core Exposure | 不暴露核心的工程證據</text>')
    parts.append('<text x="480" y="70" text-anchor="middle" class="muted">Code matters, but proof can be layered: public signals first, controlled review only when appropriate.</text>')

    x = 54
    y = 104
    col1 = 190
    col2 = 370
    col3 = 290
    row_h = 62
    parts.append(f'<rect x="{x}" y="{y}" width="{col1}" height="46" class="box"/>')
    parts.append(f'<rect x="{x + col1}" y="{y}" width="{col2}" height="46" class="safe"/>')
    parts.append(f'<rect x="{x + col1 + col2}" y="{y}" width="{col3}" height="46" class="private"/>')
    parts.append(f'<text x="{x + 18}" y="{y + 30}" class="head">Layer</text>')
    parts.append(f'<text x="{x + col1 + 18}" y="{y + 30}" class="head">Visible proof</text>')
    parts.append(f'<text x="{x + col1 + col2 + 18}" y="{y + 30}" class="head">Protected boundary</text>')

    for i, (layer, proof, boundary) in enumerate(rows):
        yy = y + 46 + (i * row_h)
        parts.append(f'<rect x="{x}" y="{yy}" width="{col1}" height="{row_h}" class="box"/>')
        parts.append(f'<rect x="{x + col1}" y="{yy}" width="{col2}" height="{row_h}" class="box"/>')
        parts.append(f'<rect x="{x + col1 + col2}" y="{yy}" width="{col3}" height="{row_h}" class="box"/>')
        parts.append(f'<text x="{x + 18}" y="{yy + 37}" class="head">{_svg_escape(layer)}</text>')
        parts.append(f'<text x="{x + col1 + 18}" y="{yy + 37}" class="cell">{_svg_escape(proof)}</text>')
        parts.append(f'<text x="{x + col1 + col2 + 18}" y="{yy + 37}" class="cell">{_svg_escape(boundary)}</text>')

    parts.append('<text x="480" y="394" text-anchor="middle" class="muted">The goal is credibility, not full disclosure: show reasoning, verification, and ownership without handing over the blueprint.</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def build_case_study_svg(*, size_w: int = 960, size_h: int = 420) -> str:
    layers = [
        ("行動端", "Flutter / Android", "App 流程、權限、實機 QA"),
        ("後端", "Node.js / Express", "服務、API、診斷"),
        ("即時事件", "WebSocket / FCM", "事件、推播、狀態同步"),
        ("地圖定位", "Location APIs", "定位與地圖整合"),
        ("資料層", "關聯式資料庫", "狀態、稽核、版本遷移"),
        ("QA", "Playwright / ADB", "截圖、log、回歸檢查"),
    ]

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{size_w}" height="{size_h}" viewBox="0 0 {size_w} {size_h}">')
    parts.append("<defs>")
    parts.append(
        "<style>"
        "text{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;fill:#111827}"
        ".muted{fill:#6b7280}"
        ".title{font-size:24px;font-weight:850}"
        ".layer{font-size:16px;font-weight:850}"
        ".tool{font-size:13px;font-weight:750;fill:#2563eb}"
        ".body{font-size:12px;font-weight:650;fill:#4b5563}"
        ".box{fill:#ffffff;stroke:#d1d5db;stroke-width:2}"
        ".shield{fill:#fff7ed;stroke:#f97316;stroke-width:2}"
        ".line{stroke:#9ca3af;stroke-width:3;stroke-linecap:round}"
        "</style>"
    )
    parts.append("</defs>")
    parts.append('<rect width="100%" height="100%" fill="#f8fafc"/>')
    parts.append('<text x="480" y="42" text-anchor="middle" class="title">去敏案例研究 | Sanitized Case Study</text>')
    parts.append('<text x="480" y="70" text-anchor="middle" class="muted">我把真實專案整理成能力層，不公開原始碼、流程規則或底層選型。</text>')

    start_x = 50
    start_y = 112
    box_w = 270
    box_h = 76
    gap_x = 25
    gap_y = 26
    for i, (layer, tool, body) in enumerate(layers):
        col = i % 3
        row = i // 3
        x = start_x + col * (box_w + gap_x)
        y = start_y + row * (box_h + gap_y)
        parts.append(f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="12" class="box"/>')
        parts.append(f'<text x="{x + 18}" y="{y + 28}" class="layer">{_svg_escape(layer)}</text>')
        parts.append(f'<text x="{x + 18}" y="{y + 48}" class="tool">{_svg_escape(tool)}</text>')
        parts.append(f'<text x="{x + 18}" y="{y + 66}" class="body">{_svg_escape(body)}</text>')

    parts.append('<line x1="120" y1="304" x2="840" y2="304" class="line"/>')
    parts.append('<rect x="240" y="328" width="480" height="54" rx="14" class="shield"/>')
    parts.append('<text x="480" y="352" text-anchor="middle" class="layer">保留不公開</text>')
    parts.append('<text x="480" y="372" text-anchor="middle" class="body">原始碼、資料設計、結算、營運規則、憑證、真實使用者</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def generate() -> tuple[Path, Path]:
    root = repo_root()
    skills = read_yaml(root / "data" / "skills.yml")
    max_score = float(skills.get("max_score", 5))
    axes = skills.get("axes", [])
    if not isinstance(axes, list) or len(axes) == 0:
        raise ValueError("data/skills.yml must have a non-empty 'axes' list")

    bi_axes: list[RadarAxis] = []
    for a in axes:
        if not isinstance(a, dict):
            continue
        score = float(a.get("score", 0))
        zh = str(a.get("zh", a.get("key", ""))).strip()
        en = str(a.get("en", a.get("key", ""))).strip()
        bi_axes.append(RadarAxis(zh=zh, en=en, score=score))

    assets = root / "assets"
    ensure_dir(assets)

    out_path = assets / "skill-radar.svg"
    boundary_path = assets / "public-private-boundary.svg"
    evidence_path = assets / "engineering-evidence.svg"
    case_study_path = assets / "sanitized-case-study.svg"

    svg = build_radar_svg(title="Product Capability Focus | 產品能力重心", axes=bi_axes, max_score=max_score)
    boundary_svg = build_boundary_svg()
    evidence_svg = build_engineering_evidence_svg()
    case_study_svg = build_case_study_svg()

    out_path.write_text(svg, encoding="utf-8")
    boundary_path.write_text(boundary_svg, encoding="utf-8")
    evidence_path.write_text(evidence_svg, encoding="utf-8")
    case_study_path.write_text(case_study_svg, encoding="utf-8")

    return out_path, boundary_path


def main() -> None:
    out, _ = generate()
    print(f"Generated: {out}")


if __name__ == "__main__":
    main()


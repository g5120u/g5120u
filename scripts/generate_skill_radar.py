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
    parts.append(f'<text x="{cx:.2f}" y="72" text-anchor="middle" class="muted" font-size="14">0–{max_score:g}</text>')

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


def build_ai_workflow_svg(*, size_w: int = 960, size_h: int = 360) -> str:
    steps = [
        ("1", "Define scope", "requirements, roles, constraints"),
        ("2", "Design flow", "screens, states, data boundaries"),
        ("3", "Read changes", "diffs, call paths, side effects"),
        ("4", "Verify behavior", "manual QA, logs, regression checks"),
        ("5", "Own delivery", "ship only understood changes"),
    ]

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{size_w}" height="{size_h}" viewBox="0 0 {size_w} {size_h}">')
    parts.append("<defs>")
    parts.append(
        "<style>"
        "text{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;fill:#111827}"
        ".muted{fill:#6b7280}"
        ".card{fill:#ffffff;stroke:#d1d5db;stroke-width:2}"
        ".num{fill:#2563eb;font-size:20px;font-weight:900}"
        ".head{font-size:16px;font-weight:850}"
        ".body{font-size:12px;font-weight:650;fill:#4b5563}"
        ".title{font-size:24px;font-weight:850}"
        ".arrow{stroke:#9ca3af;stroke-width:3;stroke-linecap:round;stroke-linejoin:round;fill:none}"
        "</style>"
    )
    parts.append("</defs>")
    parts.append('<rect width="100%" height="100%" fill="#f8fafc"/>')
    parts.append('<text x="480" y="46" text-anchor="middle" class="title">Code Ownership Workflow | 工程掌控流程</text>')
    parts.append('<text x="480" y="74" text-anchor="middle" class="muted">AI can assist implementation, but design, review, debugging, and delivery remain owned.</text>')

    x0 = 54
    y = 122
    card_w = 154
    gap = 32
    for i, (num, head, body) in enumerate(steps):
        x = x0 + i * (card_w + gap)
        parts.append(f'<rect x="{x}" y="{y}" width="{card_w}" height="150" rx="14" class="card"/>')
        parts.append(f'<text x="{x + 18}" y="{y + 38}" class="num">{num}</text>')
        parts.append(f'<text x="{x + 18}" y="{y + 72}" class="head">{_svg_escape(head)}</text>')
        parts.append(f'<text x="{x + 18}" y="{y + 100}" class="body">{_svg_escape(body)}</text>')
        if i < len(steps) - 1:
            ax = x + card_w + 8
            ay = y + 75
            parts.append(f'<path d="M {ax} {ay} L {ax + 16} {ay} M {ax + 10} {ay - 6} L {ax + 16} {ay} L {ax + 10} {ay + 6}" class="arrow"/>')

    parts.append('<text x="480" y="322" text-anchor="middle" class="muted">The useful signal is not typing speed; it is whether the change is understood, traceable, and verified.</text>')
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
    ai_workflow_path = assets / "ai-assisted-workflow.svg"

    svg = build_radar_svg(title="Product Capability Radar | 產品能力雷達", axes=bi_axes, max_score=max_score)
    boundary_svg = build_boundary_svg()
    ai_workflow_svg = build_ai_workflow_svg()

    out_path.write_text(svg, encoding="utf-8")
    boundary_path.write_text(boundary_svg, encoding="utf-8")
    ai_workflow_path.write_text(ai_workflow_svg, encoding="utf-8")

    return out_path, boundary_path


def main() -> None:
    out, _ = generate()
    print(f"Generated: {out}")


if __name__ == "__main__":
    main()


from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from ._lib import clamp, ensure_dir, read_yaml, repo_root


@dataclass(frozen=True)
class RadarAxis:
    label: str
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
    padding: int = 90,
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

        lx = cx + (radius + 26) * math.cos(a)
        ly = cy + (radius + 26) * math.sin(a)

        # text-anchor based on angle
        ca = math.cos(a)
        anchor = "middle"
        if ca > 0.35:
            anchor = "start"
        elif ca < -0.35:
            anchor = "end"

        labels.append((lx, ly, anchor, _svg_escape(ax.label)))

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
    for x, y, anchor, label in labels:
        parts.append(f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" font-size="16" font-weight="600">{label}</text>')

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def generate() -> tuple[Path, Path]:
    root = repo_root()
    skills = read_yaml(root / "data" / "skills.yml")
    max_score = float(skills.get("max_score", 5))
    axes = skills.get("axes", [])
    if not isinstance(axes, list) or len(axes) == 0:
        raise ValueError("data/skills.yml must have a non-empty 'axes' list")

    zh_axes: list[RadarAxis] = []
    en_axes: list[RadarAxis] = []
    for a in axes:
        if not isinstance(a, dict):
            continue
        score = float(a.get("score", 0))
        zh_axes.append(RadarAxis(label=str(a.get("zh", a.get("key", ""))), score=score))
        en_axes.append(RadarAxis(label=str(a.get("en", a.get("key", ""))), score=score))

    assets = root / "assets"
    ensure_dir(assets)

    zh_path = assets / "skill-radar.zh.svg"
    en_path = assets / "skill-radar.en.svg"

    zh_svg = build_radar_svg(title="Skill Radar（技能雷達）", axes=zh_axes, max_score=max_score)
    en_svg = build_radar_svg(title="Skill Radar", axes=en_axes, max_score=max_score)

    zh_path.write_text(zh_svg, encoding="utf-8")
    en_path.write_text(en_svg, encoding="utf-8")

    return zh_path, en_path


def main() -> None:
    zh, en = generate()
    print(f"Generated: {zh}")
    print(f"Generated: {en}")


if __name__ == "__main__":
    main()


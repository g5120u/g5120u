from __future__ import annotations
from pathlib import Path

from ._lib import ensure_dir, repo_root


def _svg_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def build_engineering_evidence_svg(*, size_w: int = 960, size_h: int = 430) -> str:
    rows = [
        ("Public profile", "engineering trace, tech scope, public repo activity", "no source code or product rules"),
        ("Safe evidence", "redacted screenshots, QA notes, issue-style summaries", "no real data, secrets, or full flows"),
        ("Controlled demo", "phone demo, selected behavior walkthrough", "no open download link or public credentials"),
        ("Controlled walkthrough", "screens, logs, QA notes, selected behavior discussion", "no full repo handoff"),
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
    parts.append('<text x="480" y="70" text-anchor="middle" class="muted">Proof can be layered: public signals first, controlled walkthrough only when appropriate.</text>')

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
    assets = root / "assets"
    ensure_dir(assets)

    evidence_path = assets / "engineering-evidence.svg"
    case_study_path = assets / "sanitized-case-study.svg"

    evidence_svg = build_engineering_evidence_svg()
    case_study_svg = build_case_study_svg()

    evidence_path.write_text(evidence_svg, encoding="utf-8")
    case_study_path.write_text(case_study_svg, encoding="utf-8")

    return evidence_path, case_study_path


def main() -> None:
    out, _ = generate()
    print(f"Generated: {out}")


if __name__ == "__main__":
    main()


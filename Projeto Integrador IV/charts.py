from __future__ import annotations

from html import escape
from pathlib import Path


COLORS = ["#2f6f73", "#bf7d30", "#425c8a", "#7c4f35", "#5b7f43", "#8f6f2f", "#596a7a"]


def _fmt(value: float) -> str:
    if abs(value - round(value)) < 0.01:
        return str(int(round(value)))
    return f"{value:.1f}"


def write_bar_chart(
    path: str | Path,
    title: str,
    data: list[tuple[str, float]],
    *,
    subtitle: str = "",
    value_suffix: str = "",
    width: int = 920,
    height: int = 520,
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plot_left = 260
    plot_right = 40
    plot_top = 92
    plot_bottom = 42
    plot_width = width - plot_left - plot_right
    plot_height = height - plot_top - plot_bottom
    row_height = max(26, plot_height // max(len(data), 1))
    bar_height = min(28, max(16, row_height - 8))
    max_value = max((value for _, value in data), default=1) or 1

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfaf7"/>',
        f'<text x="32" y="38" font-family="Georgia, serif" font-size="24" font-weight="700" fill="#263238">{escape(title)}</text>',
    ]
    if subtitle:
        parts.append(
            f'<text x="32" y="64" font-family="Verdana, sans-serif" font-size="13" fill="#59656a">{escape(subtitle)}</text>'
        )

    axis_y = plot_top + len(data) * row_height + 4
    parts.append(f'<line x1="{plot_left}" y1="{axis_y}" x2="{width - plot_right}" y2="{axis_y}" stroke="#d8d2c7"/>')

    for idx, (label, value) in enumerate(data):
        y = plot_top + idx * row_height
        bar_width = (float(value) / max_value) * plot_width
        color = COLORS[idx % len(COLORS)]
        label_text = label if len(label) <= 32 else label[:29] + "..."
        parts.extend(
            [
                f'<text x="32" y="{y + bar_height - 3}" font-family="Verdana, sans-serif" font-size="12" fill="#263238">{escape(label_text)}</text>',
                f'<rect x="{plot_left}" y="{y}" width="{bar_width:.2f}" height="{bar_height}" rx="4" fill="{color}"/>',
                f'<text x="{plot_left + bar_width + 8:.2f}" y="{y + bar_height - 5}" font-family="Verdana, sans-serif" font-size="12" fill="#263238">{_fmt(float(value))}{escape(value_suffix)}</text>',
            ]
        )

    parts.append("</svg>")
    output_path.write_text("\n".join(parts), encoding="utf-8")


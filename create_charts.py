#!/usr/bin/env python3
"""Create portfolio-ready SVG charts from the Guardian SQLite database."""

from __future__ import annotations

import html
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATABASE = ROOT / "data" / "guardian_editorial_analysis.sqlite"
CHARTS = ROOT / "charts"

NAVY = "#052962"
BLUE = "#1f78b4"
PALE_BLUE = "#dce8f5"
RED = "#c70000"
TEXT = "#1f2933"
MUTED = "#5f6b76"
GRID = "#d9dee3"
BACKGROUND = "#ffffff"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def base_svg(title: str, description: str, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" '
        f'viewBox="0 0 1000 {height}" role="img" aria-labelledby="chart-title chart-desc">',
        f"<title id=\"chart-title\">{esc(title)}</title>",
        f"<desc id=\"chart-desc\">{esc(description)}</desc>",
        f'<rect width="1000" height="{height}" fill="{BACKGROUND}"/>',
        f'<text x="70" y="58" fill="{NAVY}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="30" font-weight="700">{esc(title)}</text>',
    ]


def footer(lines: list[str], height: int) -> None:
    lines.append(
        f'<text x="70" y="{height - 28}" fill="{MUTED}" '
        'font-family="Arial, Helvetica, sans-serif" font-size="14">'
        "Source: Guardian Open Platform Content API · Analysis conducted in SQLite"
        "</text>"
    )
    lines.append("</svg>")


def horizontal_bars(
    data: list[tuple[str, float]],
    title: str,
    subtitle: str,
    value_label: str,
    output_name: str,
    *,
    reference: float | None = None,
    highlighted_label: str | None = None,
    axis_max: float,
    tick_step: float,
) -> None:
    width, height = 1000, 620
    plot_left, plot_right = 260, 915
    plot_top, plot_bottom = 150, 505
    plot_width = plot_right - plot_left
    scale_max = axis_max

    lines = base_svg(
        title,
        f"Horizontal bar chart comparing {value_label.lower()} across Guardian sections.",
        height,
    )
    lines.append(
        f'<text x="70" y="91" fill="{MUTED}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="17">{esc(subtitle)}</text>'
    )

    tick_values = [
        value
        for value in range(0, int(scale_max) + 1, int(tick_step))
    ]
    for value in tick_values:
        x = plot_left + plot_width * value / scale_max
        lines.append(
            f'<line x1="{x:.1f}" y1="{plot_top - 8}" x2="{x:.1f}" y2="{plot_bottom}" '
            f'stroke="{GRID}" stroke-width="1"/>'
        )
        lines.append(
            f'<text x="{x:.1f}" y="{plot_bottom + 27}" text-anchor="middle" fill="{MUTED}" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="14">{value:,.0f}</text>'
        )

    row_height = (plot_bottom - plot_top) / len(data)
    bar_height = min(44, row_height * 0.58)
    for index, (label, value) in enumerate(data):
        centre_y = plot_top + row_height * (index + 0.5)
        bar_width = plot_width * value / scale_max
        colour = RED if label == highlighted_label else BLUE
        lines.append(
            f'<text x="{plot_left - 18}" y="{centre_y + 6:.1f}" text-anchor="end" fill="{TEXT}" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="18">{esc(label)}</text>'
        )
        lines.append(
            f'<rect x="{plot_left}" y="{centre_y - bar_height / 2:.1f}" width="{bar_width:.1f}" '
            f'height="{bar_height:.1f}" rx="3" fill="{colour}"/>'
        )
        lines.append(
            f'<text x="{plot_left + bar_width + 12:.1f}" y="{centre_y + 6:.1f}" fill="{TEXT}" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="700">'
            f"{value:,.0f}</text>"
        )

    if reference is not None:
        x = plot_left + plot_width * reference / scale_max
        lines.append(
            f'<line x1="{x:.1f}" y1="{plot_top - 10}" x2="{x:.1f}" y2="{plot_bottom}" '
            f'stroke="{NAVY}" stroke-width="2" stroke-dasharray="7 6"/>'
        )
        label_x = min(x + 10, plot_right - 165)
        lines.append(
            f'<text x="{label_x:.1f}" y="{plot_top - 22}" fill="{NAVY}" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="700">'
            f"Overall average: {reference:,.0f}</text>"
        )

    lines.append(
        f'<text x="{(plot_left + plot_right) / 2:.1f}" y="{plot_bottom + 58}" text-anchor="middle" '
        f'fill="{MUTED}" font-family="Arial, Helvetica, sans-serif" font-size="15">'
        f"{esc(value_label)}</text>"
    )
    footer(lines, height)
    (CHARTS / output_name).write_text("\n".join(lines), encoding="utf-8")


def weekday_chart(data: list[tuple[str, float]]) -> None:
    width, height = 1000, 620
    plot_left, plot_right = 95, 930
    plot_top, plot_bottom = 145, 500
    plot_width = plot_right - plot_left
    plot_height = plot_bottom - plot_top
    maximum = max(value for _, value in data)
    scale_max = 225

    lines = base_svg(
        "Guardian articles published by day of the week",
        "Vertical bar chart comparing article counts from Monday to Sunday.",
        height,
    )
    lines.append(
        f'<text x="70" y="91" fill="{MUTED}" font-family="Arial, Helvetica, sans-serif" '
        'font-size="17">Four complete weeks · 30 August to 26 September 2026</text>'
    )

    for value in range(0, scale_max + 1, 50):
        y = plot_bottom - plot_height * value / scale_max
        lines.append(
            f'<line x1="{plot_left}" y1="{y:.1f}" x2="{plot_right}" y2="{y:.1f}" '
            f'stroke="{GRID}" stroke-width="1"/>'
        )
        lines.append(
            f'<text x="{plot_left - 14}" y="{y + 5:.1f}" text-anchor="end" fill="{MUTED}" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="14">{value}</text>'
        )

    slot = plot_width / len(data)
    bar_width = slot * 0.56
    for index, (label, value) in enumerate(data):
        x = plot_left + slot * index + (slot - bar_width) / 2
        bar_height = plot_height * value / scale_max
        y = plot_bottom - bar_height
        colour = RED if value == maximum else BLUE
        lines.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{bar_height:.1f}" '
            f'rx="3" fill="{colour}"/>'
        )
        lines.append(
            f'<text x="{x + bar_width / 2:.1f}" y="{y - 11:.1f}" text-anchor="middle" fill="{TEXT}" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="17" font-weight="700">'
            f"{value:,.0f}</text>"
        )
        lines.append(
            f'<text x="{x + bar_width / 2:.1f}" y="{plot_bottom + 30}" text-anchor="middle" fill="{TEXT}" '
            f'font-family="Arial, Helvetica, sans-serif" font-size="16">{esc(label)}</text>'
        )

    lines.append(
        f'<text x="22" y="{(plot_top + plot_bottom) / 2:.1f}" text-anchor="middle" fill="{MUTED}" '
        'font-family="Arial, Helvetica, sans-serif" font-size="15" '
        f'transform="rotate(-90 22 {(plot_top + plot_bottom) / 2:.1f})">Articles</text>'
    )
    footer(lines, height)
    (CHARTS / "articles-by-weekday.svg").write_text("\n".join(lines), encoding="utf-8")


def query_all(connection: sqlite3.Connection, sql: str) -> list[tuple[str, float]]:
    return [(str(label), float(value)) for label, value in connection.execute(sql).fetchall()]


def main() -> None:
    if not DATABASE.exists():
        raise SystemExit(f"Database not found: {DATABASE}")

    CHARTS.mkdir(exist_ok=True)
    with sqlite3.connect(DATABASE) as connection:
        sections = query_all(
            connection,
            """
            SELECT section_name, COUNT(*)
            FROM articles
            GROUP BY section_name
            ORDER BY COUNT(*) DESC
            """,
        )
        weekdays = query_all(
            connection,
            """
            SELECT publication_day, COUNT(*)
            FROM articles
            GROUP BY publication_day
            ORDER BY CASE publication_day
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7
            END
            """,
        )
        word_counts = query_all(
            connection,
            """
            SELECT section_name, AVG(word_count)
            FROM articles
            GROUP BY section_name
            ORDER BY AVG(word_count) DESC
            """,
        )
        overall_average = float(
            connection.execute("SELECT AVG(word_count) FROM articles").fetchone()[0]
        )

    horizontal_bars(
        sections,
        "Guardian articles published by section",
        "30 Aug–26 Sep 2026 · 1,098 content items",
        "Articles",
        "articles-by-section.svg",
        highlighted_label="World news",
        axis_max=500,
        tick_step=100,
    )
    weekday_chart(weekdays)
    horizontal_bars(
        word_counts,
        "Average Guardian article length by section",
        "30 Aug–26 Sep 2026 · Word counts available for all 1,098 items",
        "Average word count",
        "average-word-count-by-section.svg",
        reference=overall_average,
        highlighted_label="Politics",
        axis_max=1500,
        tick_step=300,
    )
    print(f"Created 3 charts in {CHARTS}")


if __name__ == "__main__":
    main()

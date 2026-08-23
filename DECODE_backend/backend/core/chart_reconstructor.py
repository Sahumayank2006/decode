"""
DECODE – Chart Reconstruction Engine
Converts extracted chart data into:
  1. Recharts-compatible JSON configs for the frontend
  2. Matplotlib/Plotly server-side PNG/SVG exports

Supports chart type switching: same data → bar / line / pie / heatmap / table.
"""

import io
import logging
import base64
import json
from pathlib import Path
from typing import Optional

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

logger = logging.getLogger("decode.chart_reconstructor")

# ── Default color palettes ───────────────────────────────────────────────────

PALETTES = {
    "default": ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f",
                 "#edc949", "#af7aa1", "#ff9da7", "#9c755f", "#bab0ac"],
    "vibrant": ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00",
                "#ffff33", "#a65628", "#f781bf", "#999999", "#66c2a5"],
    "pastel":  ["#b3e2cd", "#fdcdac", "#cbd5e8", "#f4cae4", "#e6f5c9",
                "#fff2ae", "#f1e2cc", "#cccccc", "#fbb4ae", "#b3cde3"],
    "dark":    ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e",
                "#e6ab02", "#a6761d", "#666666", "#e78ac3", "#8da0cb"],
    "academic": ["#2c3e50", "#e74c3c", "#3498db", "#2ecc71", "#f39c12",
                 "#9b59b6", "#1abc9c", "#e67e22", "#34495e", "#95a5a6"],
}


# ─────────────────────────────────────────────────────────────────────────────
# Recharts config generation
# ─────────────────────────────────────────────────────────────────────────────

def _series_to_recharts_data(series: list[dict]) -> list[dict]:
    """
    Convert DECODE series format to Recharts-compatible data array.

    DECODE format:
        [{"name": "S1", "color": "#4e79a7",
          "points": [{"label": "Q1", "value": 42}, ...]}]

    Recharts format:
        [{"name": "Q1", "S1": 42, "S2": 18}, ...]
    """
    if not series:
        return []

    # Collect all unique labels (preserving order from first series)
    label_order = []
    for s in series:
        for pt in s.get("points", []):
            lbl = pt.get("label", "")
            if lbl and lbl not in label_order:
                label_order.append(lbl)

    # Build data rows
    data = []
    for label in label_order:
        row = {"name": label}
        for s in series:
            for pt in s.get("points", []):
                if pt.get("label") == label:
                    row[s["name"]] = pt.get("value", 0)
                    break
        data.append(row)

    return data


def generate_recharts_config(
    series: list[dict],
    chart_type: str = "bar",
    axis_labels: Optional[dict] = None,
    title: str = "",
    palette_name: str = "default",
) -> dict:
    """
    Generate a Recharts-compatible configuration object.

    Returns a JSON-serialisable dict that the frontend can render directly
    with Recharts <BarChart>, <LineChart>, <PieChart>, etc.
    """
    palette = PALETTES.get(palette_name, PALETTES["default"])
    axis_labels = axis_labels or {}

    data = _series_to_recharts_data(series)

    # Assign colors to each series
    series_configs = []
    for i, s in enumerate(series):
        color = s.get("color", palette[i % len(palette)])
        series_configs.append({
            "dataKey": s["name"],
            "name": s["name"],
            "color": color,
            "fill": color,
            "stroke": color,
        })

    config = {
        "chartType": chart_type,
        "title": title,
        "data": data,
        "series": series_configs,
        "xAxis": {
            "dataKey": "name",
            "label": axis_labels.get("x_label", ""),
        },
        "yAxis": {
            "label": axis_labels.get("y_label", ""),
        },
        "palette": palette_name,
        "legend": True,
        "tooltip": True,
        "grid": True,
        "animation": True,
    }

    # Pie chart needs a different data format
    if chart_type == "pie":
        pie_data = []
        for s in series:
            for pt in s.get("points", []):
                pie_data.append({
                    "name": pt.get("label", "Unknown"),
                    "value": pt.get("value", 0),
                    "fill": palette[len(pie_data) % len(palette)],
                })
        config["data"] = pie_data
        config["series"] = [{
            "dataKey": "value",
            "nameKey": "name",
        }]

    return config


def switch_chart_type(
    current_config: dict,
    new_chart_type: str,
    series: list[dict],
    axis_labels: Optional[dict] = None,
) -> dict:
    """
    Re-generate the Recharts config for a different chart type
    using the same underlying data.
    """
    return generate_recharts_config(
        series=series,
        chart_type=new_chart_type,
        axis_labels=axis_labels or {},
        title=current_config.get("title", ""),
        palette_name=current_config.get("palette", "default"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Server-side chart rendering  (Matplotlib)
# ─────────────────────────────────────────────────────────────────────────────

def _render_bar_chart(
    series: list[dict],
    axis_labels: dict,
    title: str,
    palette: list[str],
    figsize: tuple = (10, 6),
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=figsize)

    labels = []
    for s in series:
        for pt in s.get("points", []):
            if pt["label"] not in labels:
                labels.append(pt["label"])

    n_series = len(series)
    x = np.arange(len(labels))
    width = 0.8 / max(n_series, 1)

    for i, s in enumerate(series):
        values = []
        for lbl in labels:
            val = next((p["value"] for p in s["points"] if p["label"] == lbl), 0)
            values.append(val)
        offset = (i - n_series / 2 + 0.5) * width
        color = s.get("color", palette[i % len(palette)])
        ax.bar(x + offset, values, width, label=s["name"], color=color, alpha=0.85)

    ax.set_xlabel(axis_labels.get("x_label", ""))
    ax.set_ylabel(axis_labels.get("y_label", ""))
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    return fig


def _render_line_chart(
    series: list[dict],
    axis_labels: dict,
    title: str,
    palette: list[str],
    figsize: tuple = (10, 6),
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=figsize)

    for i, s in enumerate(series):
        labels = [p["label"] for p in s["points"]]
        values = [p["value"] for p in s["points"]]
        color = s.get("color", palette[i % len(palette)])
        ax.plot(labels, values, marker="o", label=s["name"],
                color=color, linewidth=2, markersize=6)

    ax.set_xlabel(axis_labels.get("x_label", ""))
    ax.set_ylabel(axis_labels.get("y_label", ""))
    ax.set_title(title)
    ax.legend()
    ax.grid(alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig


def _render_pie_chart(
    series: list[dict],
    axis_labels: dict,
    title: str,
    palette: list[str],
    figsize: tuple = (8, 8),
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=figsize)

    # Flatten all points from all series
    labels, values, colors = [], [], []
    for s in series:
        for j, pt in enumerate(s.get("points", [])):
            labels.append(pt["label"])
            values.append(pt["value"])
            colors.append(palette[(len(colors)) % len(palette)])

    if not values:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=14)
    else:
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct="%1.1f%%",
            colors=colors, startangle=90, pctdistance=0.85,
        )
        for t in autotexts:
            t.set_fontsize(9)

    ax.set_title(title)
    plt.tight_layout()
    return fig


def _render_heatmap(
    series: list[dict],
    axis_labels: dict,
    title: str,
    palette: list[str],
    figsize: tuple = (10, 6),
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=figsize)

    # Build matrix from series
    labels = []
    for s in series:
        for pt in s.get("points", []):
            if pt["label"] not in labels:
                labels.append(pt["label"])

    matrix = []
    series_names = []
    for s in series:
        row = []
        series_names.append(s["name"])
        for lbl in labels:
            val = next((p["value"] for p in s["points"] if p["label"] == lbl), 0)
            row.append(val)
        matrix.append(row)

    if matrix:
        im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto")
        ax.set_xticks(np.arange(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_yticks(np.arange(len(series_names)))
        ax.set_yticklabels(series_names)
        plt.colorbar(im, ax=ax)

        # Add value annotations
        for i in range(len(series_names)):
            for j in range(len(labels)):
                ax.text(j, i, f"{matrix[i][j]:.1f}",
                        ha="center", va="center", fontsize=8)

    ax.set_title(title)
    plt.tight_layout()
    return fig


_RENDERERS = {
    "bar": _render_bar_chart,
    "line": _render_line_chart,
    "pie": _render_pie_chart,
    "heatmap": _render_heatmap,
}


def render_chart_image(
    series: list[dict],
    chart_type: str = "bar",
    axis_labels: Optional[dict] = None,
    title: str = "",
    palette_name: str = "default",
    output_format: str = "png",
    figsize: tuple = (10, 6),
) -> bytes:
    """
    Render a chart as PNG or SVG bytes using Matplotlib.
    """
    palette = PALETTES.get(palette_name, PALETTES["default"])
    axis_labels = axis_labels or {}

    renderer = _RENDERERS.get(chart_type, _render_bar_chart)
    fig = renderer(series, axis_labels, title, palette, figsize)

    buf = io.BytesIO()
    fig.savefig(buf, format=output_format, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def render_chart_base64(
    series: list[dict],
    chart_type: str = "bar",
    axis_labels: Optional[dict] = None,
    title: str = "",
    palette_name: str = "default",
    output_format: str = "png",
) -> str:
    """Render chart and return as base64 string."""
    raw = render_chart_image(
        series, chart_type, axis_labels, title, palette_name, output_format,
    )
    return base64.b64encode(raw).decode("utf-8")


def save_chart_export(
    series: list[dict],
    chart_type: str = "bar",
    axis_labels: Optional[dict] = None,
    title: str = "",
    palette_name: str = "default",
    output_dir: str = ".",
    filename_prefix: str = "chart",
) -> dict:
    """
    Save chart as both PNG and SVG files.
    Returns dict with file paths.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {}
    for fmt in ("png", "svg"):
        raw = render_chart_image(
            series, chart_type, axis_labels, title, palette_name, fmt,
        )
        fpath = output_dir / f"{filename_prefix}.{fmt}"
        with open(fpath, "wb") as f:
            f.write(raw)
        paths[fmt] = str(fpath)
        logger.info("Saved chart export: %s", fpath)

    return paths


# ─────────────────────────────────────────────────────────────────────────────
# Full reconstruction pipeline
# ─────────────────────────────────────────────────────────────────────────────

def reconstruct_chart(
    extraction: dict,
    chart_type: Optional[str] = None,
    palette_name: str = "default",
    export_dir: Optional[str] = None,
    export_prefix: str = "chart",
) -> dict:
    """
    Full reconstruction from extraction data.

    Args:
        extraction: output from chart_extractor.extract_chart_data()
        chart_type: override chart type (None = use original)
        palette_name: color palette to use
        export_dir: if set, save PNG/SVG exports
        export_prefix: filename prefix for exports

    Returns:
        {
            "chart_type": str,
            "chart_config": dict,       # Recharts-compatible
            "image_base64": str,         # PNG preview
            "export_paths": dict,        # {"png": path, "svg": path} if exported
            "recommended_alt_type": str, # Rule-based suggestion
            "recommendation_reason": str,
        }
    """
    series = extraction.get("series", [])
    axis_labels = extraction.get("axis_labels", {})
    title = extraction.get("title", "Reconstructed Chart")

    if chart_type is None:
        chart_type = "bar"  # default

    # Generate Recharts config
    config = generate_recharts_config(
        series=series,
        chart_type=chart_type,
        axis_labels=axis_labels,
        title=title,
        palette_name=palette_name,
    )

    # Server-side render for preview
    image_b64 = render_chart_base64(
        series=series,
        chart_type=chart_type,
        axis_labels=axis_labels,
        title=title,
        palette_name=palette_name,
    )

    # Export files if requested
    export_paths = {}
    if export_dir:
        export_paths = save_chart_export(
            series=series,
            chart_type=chart_type,
            axis_labels=axis_labels,
            title=title,
            palette_name=palette_name,
            output_dir=export_dir,
            filename_prefix=export_prefix,
        )

    # Rule-based chart type recommendation
    rec_type, rec_reason = _recommend_chart_type(series, chart_type)

    return {
        "chart_type": chart_type,
        "chart_config": config,
        "image_base64": image_b64,
        "export_paths": export_paths,
        "recommended_alt_type": rec_type,
        "recommendation_reason": rec_reason,
    }


def _recommend_chart_type(series: list[dict], current_type: str) -> tuple[str, str]:
    """
    Rule-based recommendation for alternative chart type.
    Returns (recommended_type, reason).
    """
    if not series:
        return current_type, "No data to analyse."

    total_points = sum(len(s.get("points", [])) for s in series)
    n_series = len(series)

    # Check if labels look like dates/time
    labels = []
    for s in series:
        for p in s.get("points", []):
            labels.append(p.get("label", ""))

    time_patterns = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug",
                     "sep", "oct", "nov", "dec", "q1", "q2", "q3", "q4",
                     "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
    has_time = any(
        any(tp in lbl.lower() for tp in time_patterns)
        for lbl in labels
    )

    if current_type == "bar":
        if has_time and total_points >= 4:
            return "line", "Data appears to have a time dimension — a line chart would better show trends over time."
        if total_points <= 5 and n_series == 1:
            return "pie", "With few categories and a single series, a pie chart effectively shows proportional distribution."
    elif current_type == "line":
        if total_points <= 4:
            return "bar", "With few data points, a bar chart provides clearer comparison between categories."
    elif current_type == "pie":
        if total_points > 6:
            return "bar", "With many segments, a bar chart is easier to read than a pie chart."

    # Default: suggest heatmap for multi-series
    if n_series >= 3 and current_type != "heatmap":
        return "heatmap", "Multiple data series can be compared effectively in a heatmap format."

    return current_type, "Current chart type is well-suited for this data."

from __future__ import annotations

from typing import Dict, List


PALETTES: Dict[
    str,
    List[str]
] = {

    "default": [
        "#2563EB",
        "#16A34A",
        "#F59E0B",
        "#DC2626",
        "#7C3AED",
        "#0891B2",
        "#DB2777",
        "#4F46E5",
    ],

    "professional": [
        "#1D4ED8",
        "#0F766E",
        "#B45309",
        "#7C3AED",
        "#BE123C",
        "#0369A1",
        "#374151",
        "#047857",
    ],

    "pastel": [
        "#93C5FD",
        "#86EFAC",
        "#FDE68A",
        "#FCA5A5",
        "#C4B5FD",
        "#67E8F9",
        "#F9A8D4",
        "#A5B4FC",
    ],

    "vibrant": [
        "#2563EB",
        "#16A34A",
        "#F97316",
        "#DC2626",
        "#9333EA",
        "#0891B2",
        "#DB2777",
        "#4F46E5",
    ],
}


def get_palette(
    name: str = "default",
) -> List[str]:

    return list(
        PALETTES.get(
            name,
            PALETTES["default"],
        )
    )


def color_for_series(
    series_name: str,
    index: int,
    palette_name: str = "default",
) -> str:

    palette = get_palette(
        palette_name
    )

    if not palette:

        return "#2563EB"

    return palette[
        index % len(palette)
    ]

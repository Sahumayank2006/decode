from core.extraction_normalizer import (
    normalize_extraction_result,
)


def main():

    # Simulate the kind of result an existing
    # extractor might return.

    raw_result = {

        "series": [

            {
                "name": "Revenue",

                "color": "#2563EB",

                "points": [

                    {
                        "label": "2023",
                        "value": 100,
                        "confidence": 0.94,
                    },

                    {
                        "label": "2024",
                        "value": 140,
                        "confidence": 0.96,
                    },

                    {
                        "label": "2025",
                        "value": 180,
                        "confidence": 0.95,
                    },

                ],
            },

        ],

        "axis_labels": {

            "x_label": "Year",

            "y_label": "Revenue",

            "x_ticks": [
                "2023",
                "2024",
                "2025",
            ],

            "y_ticks": [
                0,
                50,
                100,
                150,
                200,
            ],
        },

        "legend": [

            {
                "name": "Revenue",
                "color": "#2563EB",
            },

        ],

        "title": "Revenue",

        "raw_ocr_text": (
            "Revenue 2023 100 "
            "2024 140 2025 180"
        ),

        "extraction_confidence": 0.95,
    }

    dataset = (
        normalize_extraction_result(
            raw_result
        )
    )

    print(
        "\n=== NORMALIZED DATASET ==="
    )

    print(
        dataset.to_dict()
    )

    assert (
        dataset.detected_type
        == "unknown"
    )

    assert (
        dataset.title
        == "Revenue"
    )

    assert (
        dataset.x_axis_label
        == "Year"
    )

    assert (
        dataset.y_axis_label
        == "Revenue"
    )

    assert (
        dataset.categories
        == [
            "2023",
            "2024",
            "2025",
        ]
    )

    assert (
        dataset.numeric_values
        == [
            100.0,
            140.0,
            180.0,
        ]
    )

    assert (
        dataset.overall_confidence
        == 0.95
    )

    assert (
        dataset.metadata[
            "confidence_source"
        ]
        == "extractor"
    )

    assert (
        dataset.metadata[
            "axis_labels"
        ][
            "x_ticks"
        ]
        == [
            "2023",
            "2024",
            "2025",
        ]
    )

    assert (
        dataset.metadata[
            "legend"
        ][0][
            "name"
        ]
        == "Revenue"
    )

    assert (
        "Revenue 2023 100"
        in dataset.metadata[
            "raw_ocr_text"
        ]
    )

    print(
        "\nEXTRACTION NORMALIZER TEST PASSED"
    )


if __name__ == "__main__":

    main()

"""
Integration test for the extraction -> canonical
data boundary.

This test does not require a real image or OCR model.

It verifies that the exact structure returned by
DECODE's chart extractor can be converted into the
canonical representation used by reconstruction.
"""

from core.extraction_normalizer import (
    normalize_extraction_result,
)


def main():

    extraction = {

        "series": [

            {
                "name": "Revenue",

                "color": "#2563EB",

                "points": [

                    {
                        "label": "2023",
                        "value": 100.0,
                        "confidence": 0.94,
                    },

                    {
                        "label": "2024",
                        "value": 140.0,
                        "confidence": 0.96,
                    },

                    {
                        "label": "2025",
                        "value": 180.0,
                        "confidence": 0.95,
                    },
                ],
            },

            {
                "name": "Profit",

                "color": "#16A34A",

                "points": [

                    {
                        "label": "2023",
                        "value": 40.0,
                        "confidence": 0.93,
                    },

                    {
                        "label": "2024",
                        "value": 65.0,
                        "confidence": 0.95,
                    },

                    {
                        "label": "2025",
                        "value": 90.0,
                        "confidence": 0.96,
                    },
                ],
            },
        ],

        "axis_labels": {

            "x_label": "Year",

            "y_label": "Amount",

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

            {
                "name": "Profit",
                "color": "#16A34A",
            },
        ],

        "title": "Revenue and Profit",

        "raw_ocr_text": (
            "Revenue Profit "
            "2023 100 40 "
            "2024 140 65 "
            "2025 180 90"
        ),

        "extraction_confidence": 0.95,
    }

    dataset = normalize_extraction_result(

        extraction,

        detected_type="bar",

        extraction_method=(
            "decode_chart_extractor"
        ),

        metadata={
            "chart_id": "test-chart-001",
            "document_id": "test-document-001",
        },
    )

    result = dataset.to_dict()

    print(
        "\n=== PIPELINE CANONICAL RESULT ==="
    )

    print(result)

    # -----------------------------------------
    # Basic validation
    # -----------------------------------------

    assert (
        result["detected_type"]
        == "bar"
    )

    assert (
        result["title"]
        == "Revenue and Profit"
    )

    assert (
        result["x_axis_label"]
        == "Year"
    )

    assert (
        result["y_axis_label"]
        == "Amount"
    )

    assert len(
        result["series"]
    ) == 2

    assert (
        result["series"][0]["name"]
        == "Revenue"
    )

    assert (
        result["series"][1]["name"]
        == "Profit"
    )

    assert (
        result["series"][0]["color"]
        == "#2563EB"
    )

    assert (
        result["series"][1]["color"]
        == "#16A34A"
    )

    assert (
        len(
            result["series"][0]["points"]
        )
        == 3
    )

    assert (
        len(
            result["series"][1]["points"]
        )
        == 3
    )

    assert (
        result["numeric_values"]
        == [
            100.0,
            140.0,
            180.0,
            40.0,
            65.0,
            90.0,
        ]
    )

    assert (
        result["overall_confidence"]
        == 0.95
    )

    assert (
        result["metadata"][
            "chart_id"
        ]
        == "test-chart-001"
    )

    print(
        "\nPIPELINE CANONICAL "
        "INTEGRATION TEST PASSED"
    )


if __name__ == "__main__":
    main()

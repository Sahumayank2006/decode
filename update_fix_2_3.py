import os
import re

file_path = 'Decode_backend/backend/services/chart_pipeline.py'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Fix 2: Replace list_charts_for_document
list_charts_func = """def list_charts_for_document(doc_id: str) -> list[dict]:
    \"\"\"
    List all charts detected in a document.

    The frontend needs one consolidated chart object, so this endpoint
    attaches the latest extraction, reconstruction and compliance records
    to every detected chart.
    \"\"\"

    db = get_db()

    charts = []

    chart_snaps = (
        db.collection(COL_CHARTS)
        .where(
            "document_id",
            "==",
            doc_id,
        )
        .stream()
    )

    for snap in chart_snaps:

        chart = {
            k: v
            for k, v in (
                snap.to_dict() or {}
            ).items()
            if not k.startswith("_")
        }

        chart["id"] = snap.id

        # --------------------------------------------------------
        # Latest extraction
        # --------------------------------------------------------

        extraction_snaps = list(
            db.collection(COL_EXTRACTIONS)
            .where(
                "chart_id",
                "==",
                snap.id,
            )
            .stream()
        )

        extraction = None

        if extraction_snaps:
            extraction = {
                k: v
                for k, v in (
                    extraction_snaps[-1].to_dict()
                    or {}
                ).items()
                if not k.startswith("_")
            }

        chart["extraction"] = extraction

        # --------------------------------------------------------
        # Latest reconstruction
        # --------------------------------------------------------

        reconstruction_snaps = list(
            db.collection(COL_RECONSTRUCTIONS)
            .where(
                "chart_id",
                "==",
                snap.id,
            )
            .stream()
        )

        reconstruction = None

        if reconstruction_snaps:
            reconstruction = {
                k: v
                for k, v in (
                    reconstruction_snaps[-1].to_dict()
                    or {}
                ).items()
                if not k.startswith("_")
            }

        chart["reconstruction"] = reconstruction

        # --------------------------------------------------------
        # Latest compliance score
        # --------------------------------------------------------

        compliance_snaps = list(
            db.collection(COL_COMPLIANCE)
            .where(
                "chart_id",
                "==",
                snap.id,
            )
            .stream()
        )

        compliance = None

        if compliance_snaps:
            compliance = {
                k: v
                for k, v in (
                    compliance_snaps[-1].to_dict()
                    or {}
                ).items()
                if not k.startswith("_")
            }

        chart["compliance"] = compliance

        # --------------------------------------------------------
        # Build canonical frontend representation
        # --------------------------------------------------------

        canonical_data = None

        if extraction:
            extracted_series = (
                extraction.get(
                    "series",
                    [],
                )
                or []
            )

            categories = []

            for series_item in extracted_series:
                for point in (
                    series_item.get(
                        "points",
                        [],
                    )
                    or []
                ):
                    label = point.get(
                        "label"
                    )

                    if label is not None:
                        label = str(label)

                        if label not in categories:
                            categories.append(
                                label
                            )

            canonical_series = []

            for series_item in extracted_series:

                values = []

                point_map = {
                    str(
                        point.get(
                            "label",
                            "",
                        )
                    ): point.get(
                        "value"
                    )
                    for point in (
                        series_item.get(
                            "points",
                            [],
                        )
                        or []
                    )
                }

                for category in categories:
                    value = point_map.get(
                        category,
                        0,
                    )

                    try:
                        value = float(value)
                    except (
                        TypeError,
                        ValueError,
                    ):
                        value = 0

                    values.append(value)

                canonical_series.append({
                    "name": series_item.get(
                        "name",
                        "Series",
                    ),
                    "color": series_item.get(
                        "color",
                        "#4e79a7",
                    ),
                    "values": values,
                })

            canonical_data = {
                "title": extraction.get(
                    "title",
                    "",
                ),
                "detected_type": (
                    extraction.get(
                        "resolved_chart_type"
                    )
                    or chart.get(
                        "chart_type",
                        "bar",
                    )
                ),
                "categories": categories,
                "series": canonical_series,
                "metadata": {
                    "confidence": extraction.get(
                        "extraction_confidence",
                        0,
                    ),
                    "page_number": chart.get(
                        "page_number"
                    ),
                    "bounding_box": chart.get(
                        "bounding_box"
                    ),
                },
            }

        chart["canonical_data"] = canonical_data

        charts.append(chart)

    return sorted(
        charts,
        key=lambda c: (
            c.get(
                "page_number",
                0,
            ),
            c.get(
                "bounding_box",
                {}).get(
                    "y",
                    0,
                )
                if isinstance(
                    c.get(
                        "bounding_box"
                    ),
                    dict,
                )
                else 0,
        ),
    )"""

# We need to replace the old list_charts_for_document
pattern_list = re.compile(r'def list_charts_for_document.*?return charts\n', re.DOTALL)
if pattern_list.search(text):
    text = pattern_list.sub(list_charts_func + '\n', text)
else:
    # try another pattern
    pattern_list2 = re.compile(r'def list_charts_for_document.*?return sorted\(\s*charts,.*?\)\n', re.DOTALL)
    if pattern_list2.search(text):
        text = pattern_list2.sub(list_charts_func + '\n', text)
    else:
        # maybe it's completely different now. Let's just use string replace from def list_charts_for_document
        idx = text.find('def list_charts_for_document')
        if idx != -1:
            end_idx = text.find('def ', idx + 10)
            if end_idx == -1: end_idx = len(text)
            text = text[:idx] + list_charts_func + '\n\n' + text[end_idx:]

# Fix 3: update _stage_extract
# We need to replace the try block inside _stage_extract
stage_extract_old = r'''        try:
            extraction = extract_chart_data\(
                cropped, chart\["chart_type"\]
            \)
        except Exception as e:'''

stage_extract_new = '''        try:
            extraction = extract_chart_data(
                cropped, chart.get("chart_type", "bar")
            )
            
            resolved_type = extraction.get(
                "resolved_chart_type"
            )
            
            if resolved_type:
                chart["chart_type"] = resolved_type
                
                db.collection(
                    COL_CHARTS
                ).document(
                    chart_id
                ).update({
                    "chart_type": resolved_type
                })
        except Exception as e:'''

text = re.sub(stage_extract_old, stage_extract_new, text)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated chart_pipeline.py successfully")

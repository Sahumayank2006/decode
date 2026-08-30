from typing import Any, Dict, Optional

from core.canonical_data_model import CanonicalDataset
from core.reconstruction.spec import VisualizationSpec
from core.reconstruction.service import CanonicalReconstructionService

from .recommendations import recommend_visualizations
from .validators import validate_for_visualization


class UniversalVisualizationService:
    """
    Converts canonical extracted data into one or more visual
    representations without re-running extraction.
    """

    def __init__(self):
        self.reconstruction = CanonicalReconstructionService()

    def load_dataset(self, payload: Dict[str, Any]) -> CanonicalDataset:
        """
        Rehydrate canonical data from its persisted dictionary form.
        """

        if not isinstance(payload, dict):
            raise TypeError("Canonical dataset must be a dictionary.")

        return CanonicalDataset.from_dict(payload)

    def recommend(self, payload: Dict[str, Any]):
        """
        Recommend compatible visualization types.
        """

        dataset = self.load_dataset(payload)

        return recommend_visualizations(dataset)

    def validate(
        self,
        payload: Dict[str, Any],
        visualization_type: str,
    ):
        """
        Validate whether canonical data can be represented
        by the requested visualization.
        """

        dataset = self.load_dataset(payload)

        problems = validate_for_visualization(
            dataset,
            visualization_type,
        )
        
        if not problems:
            return {"valid": True}
        return {"valid": False, "reason": problems[0]}

    def render(
        self,
        payload: Dict[str, Any],
        visualization_type: str,
        export_dir: str,
        export_prefix: str = "chart",
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Render canonical data into a selected visualization.
        """

        dataset = self.load_dataset(payload)

        options = dict(options or {})

        problems = validate_for_visualization(
            dataset,
            visualization_type,
        )

        if problems:
            raise ValueError(
                problems[0]
            )

        spec = VisualizationSpec(
            chart_type=visualization_type,
            title=options.get(
                "title",
                dataset.title,
            ),
            x_axis_label=options.get(
                "x_axis_label",
                dataset.x_axis_label,
            ),
            y_axis_label=options.get(
                "y_axis_label",
                dataset.y_axis_label,
            ),
            width=int(options.get("width", 1200)),
            height=int(options.get("height", 700)),
            palette_name=options.get(
                "palette_name",
                "default",
            ),
            show_legend=bool(
                options.get("show_legend", True)
            ),
            show_grid=bool(
                options.get("show_grid", True)
            ),
            background=options.get(
                "background",
                "#FFFFFF",
            ),
            text_color=options.get(
                "text_color",
                "#1F2937",
            ),
            grid_color=options.get(
                "grid_color",
                "#E5E7EB",
            ),
            axis_color=options.get(
                "axis_color",
                "#64748B",
            ),
        )

        result = self.reconstruction.reconstruct(
            dataset=dataset,
            spec=spec,
            export_dir=export_dir,
            export_prefix=export_prefix,
        )

        return {
            "visualization_type": visualization_type,
            "dataset": dataset.to_dict(),
            "spec": spec.to_dict(),
            "result": result,
        }

    def supports(self, visualization_type: str) -> bool:
        """
        Check if the requested visualization type is supported.
        """
        supported_types = {
            "bar",
            "line",
            "area",
            "scatter",
            "pie",
            "donut",
            "table",
        }
        return str(visualization_type).strip().lower() in supported_types


# Dataset Generator

Browser-based Apache ECharts chart generator for creating training data with perfect ground truth.

## Purpose

Generates realistic chart images using actual Apache ECharts instances. Each chart produces:

- **PNG Image** (600×400px)
- **JSON Metadata** with complete ECharts configuration and extracted properties

## Quick Start

```bash
# Install dependencies
bun install

# Start development server
bun run dev
```

Server runs at `http://localhost:5173`

## Example Chart URLs

Once the dev server is running, open any of these URLs to generate sophisticated charts:

| Chart                                       | URL                                                                                                                                                                                                                                                      |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Stacked Multi-Series Bar (large dataset)    | [http://localhost:5173/?seed=stack42&type=bar&dataSize=8&minValue=10&maxValue=90&colorScheme=vibrant](http://localhost:5173/?seed=stack42&type=bar&dataSize=8&minValue=10&maxValue=90&colorScheme=vibrant)                                               |
| Smooth Trend Line (ocean palette)           | [http://localhost:5173/?seed=trend99&type=line&dataSize=20&minValue=0&maxValue=500&colorScheme=ocean](http://localhost:5173/?seed=trend99&type=line&dataSize=20&minValue=0&maxValue=500&colorScheme=ocean)                                               |
| Area Chart (negative + positive values)     | [http://localhost:5173/?seed=area77&type=area&dataSize=15&minValue=-80&maxValue=120&colorScheme=earth&includeNegatives=true](http://localhost:5173/?seed=area77&type=area&dataSize=15&minValue=-80&maxValue=120&colorScheme=earth&includeNegatives=true) |
| Pie Chart (sparse high-contrast wedges)     | [http://localhost:5173/?seed=pie55&type=pie&dataSize=7&minValue=5&maxValue=100&colorScheme=pastel](http://localhost:5173/?seed=pie55&type=pie&dataSize=7&minValue=5&maxValue=100&colorScheme=pastel)                                                     |
| Doughnut Chart (monochrome, dense segments) | [http://localhost:5173/?seed=donut11&type=doughnut&dataSize=9&minValue=10&maxValue=80&colorScheme=monochrome](http://localhost:5173/?seed=donut11&type=doughnut&dataSize=9&minValue=10&maxValue=80&colorScheme=monochrome)                               |
| Edge Cases Template (randomized variant)    | [http://localhost:5173/?seed=edge88&template=edge-cases&type=line&colorScheme=vibrant](http://localhost:5173/?seed=edge88&template=edge-cases&type=line&colorScheme=vibrant)                                                                             |

## Chart Control

The generator supports randomization of:

**Chart Types:**

- Bar (vertical/horizontal)
- Line (smooth curves)
- Pie
- Doughnut

**Randomization Options:**

- Data values (configurable ranges, decimals)
- Data size (3-20 points)
- Color schemes (vibrant, pastel, dark, monochrome, cool, warm)
- Labels (months, categories, custom)
- Styling (titles, legends, backgrounds)

**Reproducible Seeds:**
Each chart can be regenerated deterministically using seed values for consistent testing and validation.

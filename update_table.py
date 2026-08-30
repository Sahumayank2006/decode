import os
import re

file_path = 'decode-frontend/src/components/demo/DemoWorkspace.tsx'
with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 12. Fix the Table Header
table_head = """<thead>
  <tr>
    <th className="px-5 py-3">
      Category
    </th>

    {(
      selectedExtractedChart
        ?.series ?? []
    ).map((series) => (
      <th
        key={series.name}
        className="px-5 py-3"
      >
        {series.name}
      </th>
    ))}

    <th className="px-5 py-3 text-right">
      Action
    </th>
  </tr>
</thead>"""

text = re.sub(r'<thead[^>]*>.*?<\/thead>', table_head, text, flags=re.DOTALL)

# 13. Fix the Table Body
table_body = """<tbody>
  {selectedExtractedChart?.categories.map(
    (category, rowIndex) => (
      <tr
        key={`${category}-${rowIndex}`}
        className="border-b border-white/[0.04]"
      >
        <td className="px-5 py-3">
          <input
            value={category}
            onChange={(event) => {
              const value =
                event.target.value;

              setExtractedCharts(
                (current) =>
                  current.map(
                    (chart, chartIndex) =>
                      chartIndex ===
                      selectedChartIndex
                        ? {
                            ...chart,
                            categories:
                              chart.categories.map(
                                (
                                  item,
                                  index
                                ) =>
                                  index ===
                                  rowIndex
                                    ? value
                                    : item
                              ),
                          }
                        : chart
                  )
              );
            }}
            className="w-full bg-transparent text-xs text-white/80 outline-none"
          />
        </td>

        {(
          selectedExtractedChart
            .series ?? []
        ).map((series) => (
          <td
            key={series.name}
            className="px-5 py-3"
          >
            <input
              type="number"
              value={
                series.values[
                  rowIndex
                ] ?? 0
              }
              onChange={(event) => {
                const value =
                  Number(
                    event.target.value
                  );

                setExtractedCharts(
                  (current) =>
                    current.map(
                      (
                        chart,
                        chartIndex
                      ) => {
                        if (
                          chartIndex !==
                          selectedChartIndex
                        ) {
                          return chart;
                        }

                        return {
                          ...chart,

                          series:
                            chart.series.map(
                              (
                                currentSeries
                              ) =>
                                currentSeries.name ===
                                series.name
                                  ? {
                                      ...currentSeries,

                                      values:
                                        currentSeries.values.map(
                                          (
                                            item,
                                            index
                                          ) =>
                                            index ===
                                            rowIndex
                                              ? value
                                              : item
                                        ),
                                    }
                                  : currentSeries
                            ),
                        };
                      }
                    )
                );
              }}
              className="w-full bg-transparent text-xs text-white/80 outline-none"
            />
          </td>
        ))}

        <td className="px-5 py-3 text-right">
          <button
            type="button"
            className="rounded-md p-1.5 text-white/20 hover:text-red-300"
          >
            <Trash2
              size={13}
            />
          </button>
        </td>
      </tr>
    )
  )}
</tbody>"""

text = re.sub(r'<tbody[^>]*>.*?<\/tbody>', table_body, text, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated table in DemoWorkspace.tsx')

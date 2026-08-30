import re

with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Find the getDocumentCharts loop and replace it
old_fetch = r'''      let chartsPayload: any = null;
      for \(let attempt = 0; attempt < 12; attempt\+\+\) \{
        chartsPayload = await getDocumentCharts\(newDocumentId\);
        const charts: any\[\] = Array.isArray\(chartsPayload\)
            \? chartsPayload
            : Array.isArray\(chartsPayload\?\.charts\)
            \? chartsPayload\.charts
            : Array.isArray\(chartsPayload\?\.data\?\.charts\)
            \? chartsPayload\.data\.charts
            : \[\];
        if \(charts\.length > 0\) break;
        await new Promise\(\(resolve\) => setTimeout\(resolve, 800\)\);
      \}

      const charts: any\[\] = Array.isArray\(chartsPayload\)
        \? chartsPayload
        : Array.isArray\(chartsPayload\?\.charts\)
        \? chartsPayload\.charts
        : Array.isArray\(chartsPayload\?\.data\?\.charts\)
        \? chartsPayload\.data\.charts
        : \[\];'''

new_fetch = '''      let charts: any[] = [];
      for (let attempt = 0; attempt < 12; attempt++) {
        charts = await getDocumentCharts(newDocumentId);
        if (charts.length > 0) break;
        await new Promise((resolve) => setTimeout(resolve, 800));
      }'''

text = re.sub(old_fetch, new_fetch, text)

# For the rows setup:
old_rows_setup = r'''        const canonical = firstChart.canonical_data \?\? firstChart.extraction\?\.canonical_data \?\? null;
        let extractedRows: any\[\] \| null = null;

        if \(canonical && Array.isArray\(canonical\.categories\) && Array.isArray\(canonical\.series\)\) \{
          const categories = canonical\.categories;
          const series = canonical\.series;

          const revenueSeries = series\.find\(\(item: any\) => String\(item\?\.name \?\? ""\)\.toLowerCase\(\)\.includes\(\"revenue\"\)\) \?\? series\[0\];
          const profitSeries = series\.find\(\(item: any\) => String\(item\?\.name \?\? ""\)\.toLowerCase\(\)\.includes\(\"profit\"\)\) \?\? series\[1\];

          if \(revenueSeries\) \{
            const revenueValues = Array\.isArray\(revenueSeries\.values\) \? revenueSeries\.values : \[\];
            const profitValues = Array\.isArray\(profitSeries\?\.values\) \? profitSeries\.values : \[\];

            extractedRows = categories\.map\(\(category: any, index: number\) => \(\{
              category: String\(category \?\? `Row \$\{index \+ 1\}`\),
              revenue: safeNumber\(revenueValues\[index\]\),
              profit: safeNumber\(profitValues\[index\]\),
              // Support arbitrary series for flexible extraction
              "series-0": safeNumber\(revenueValues\[index\]\),
              "series-1": safeNumber\(profitValues\[index\]\)
            \}\)\);
          \}
        \}'''

new_rows_setup = '''        let extractedRows: any[] | null = null;
        const categories = firstChart.categories || [];
        const series = firstChart.series || [];
        
        if (categories.length > 0 && series.length > 0) {
          extractedRows = categories.map((category: any, index: number) => {
            const row: any = { category: String(category ?? `Row ${index + 1}`) };
            
            series.forEach((s: any, i: number) => {
               const val = s.values[index];
               row[s.name] = safeNumber(val);
               row[`series-${i}`] = safeNumber(val);
               if (i === 0) row.revenue = safeNumber(val);
               if (i === 1) row.profit = safeNumber(val);
            });
            return row;
          });
        }'''

text = re.sub(old_rows_setup, new_rows_setup, text)

# For the chart selector loop:
old_selector_loop = r'''              const canonical = chart.canonical_data;
              if \(canonical && Array\.isArray\(canonical\.categories\) && Array\.isArray\(canonical\.series\)\) \{
                const revenueSeries = canonical\.series\.find\(\(item: any\) => String\(item\?\.name \?\? ""\)\.toLowerCase\(\)\.includes\(\"revenue\"\)\) \?\? canonical\.series\[0\];
                const profitSeries = canonical\.series\.find\(\(item: any\) => String\(item\?\.name \?\? ""\)\.toLowerCase\(\)\.includes\(\"profit\"\)\) \?\? canonical\.series\[1\];
                if \(revenueSeries\) \{
                  const revenueValues = revenueSeries\.values \?\? \[\];
                  const profitValues = profitSeries\?\.values \?\? \[\];
                  const nextRows = canonical\.categories\.map\(\(category: any, rowIndex: number\) => \(\{
                    category: String\(category\),
                    revenue: safeNumber\(revenueValues\[rowIndex\]\),
                    profit: safeNumber\(profitValues\[rowIndex\]\),
                    "series-0": safeNumber\(revenueValues\[rowIndex\]\),
                    "series-1": safeNumber\(profitValues\[rowIndex\]\)
                  \}\)\);
                  if \(nextRows\.length > 0\) setRows\(nextRows\);
                  else setRows\(\[\]\);
                \}
              \} else \{
                setRows\(\[\]\);
              \}
              
              const chartType = chart\?\.canonical_data\?\.detected_type \?\? chart\?\.extraction\?\.resolved_chart_type \?\? chart\?\.chart_type \?\? \"chart\";
              setChartMode\(\(chartType === \"bar\" \|\| chartType === \"line\" \|\| chartType === \"pie\" \|\| chartType === \"donut\" \|\| chartType === \"area\" \|\| chartType === \"radar\"\) \? chartType as any : \"bar\"\);'''

new_selector_loop = '''              const categories = chart.categories || [];
              const series = chart.series || [];
              
              if (categories.length > 0 && series.length > 0) {
                const nextRows = categories.map((category: any, rowIndex: number) => {
                  const row: any = { category: String(category ?? `Row ${rowIndex + 1}`) };
                  series.forEach((s: any, i: number) => {
                     const val = s.values[rowIndex];
                     row[s.name] = safeNumber(val);
                     row[`series-${i}`] = safeNumber(val);
                     if (i === 0) row.revenue = safeNumber(val);
                     if (i === 1) row.profit = safeNumber(val);
                  });
                  return row;
                });
                if (nextRows.length > 0) setRows(nextRows);
                else setRows([]);
              } else {
                setRows([]);
              }
              
              const chartType = chart.chart_type ?? "bar";
              setChartMode((chartType === "bar" || chartType === "line" || chartType === "pie" || chartType === "donut" || chartType === "area" || chartType === "radar") ? chartType as any : "bar");'''

text = re.sub(old_selector_loop, new_selector_loop, text)

with open('decode-frontend/src/components/demo/DemoWorkspace.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

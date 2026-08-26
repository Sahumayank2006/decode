import { CanonicalChart, ChartRenderType, ChartSeries, ChartDataPoint } from '../store/useChartStore';

export function reconstructChart(extraction: any, chartType: string): CanonicalChart {
  const activeType = chartType as ChartRenderType;
  
  // Basic validation and mapping from extraction format to canonical
  const series: ChartSeries[] = (extraction.series || []).map((s: any, idx: number) => ({
    id: s.id || `series_${idx}`,
    name: s.name || `Series ${idx + 1}`,
    color: s.color || ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#0088FE', '#00C49F', '#FFBB28', '#FF8042'][idx % 8]
  }));

  const data: ChartDataPoint[] = (extraction.data || []).map((d: any, idx: number) => {
    // If the data is missing values, default them to null
    const values: Record<string, number | null> = {};
    series.forEach((s) => {
      values[s.id] = (d.values && d.values[s.id] !== undefined && d.values[s.id] !== null) ? Number(d.values[s.id]) : null;
    });

    return {
      id: d.id || `cat_${idx}`,
      category: d.category || `Category ${idx + 1}`,
      values
    };
  });

  return {
    id: extraction.id || `chart_${Date.now()}`,
    title: extraction.title || 'Untitled Chart',
    sourceType: chartType,
    activeType,
    xAxisLabel: extraction.xAxisLabel,
    yAxisLabel: extraction.yAxisLabel,
    series,
    data,
    confidence: extraction.confidence || 1.0,
    editHistory: []
  };
}

export function getValidChartTypes(chart: CanonicalChart): { type: ChartRenderType, disabled: boolean, reason?: string }[] {
  const numericSeriesCount = chart.series.length;
  const categoryCount = chart.data.length;

  const validTypes: { type: ChartRenderType, disabled: boolean, reason?: string }[] = [
    { type: 'bar', disabled: false },
    { type: 'stacked_bar', disabled: false },
    { type: 'line', disabled: false },
    { type: 'area', disabled: false },
    { type: 'pie', disabled: false },
    { type: 'donut', disabled: false },
    { type: 'table', disabled: false }
  ];

  if (numericSeriesCount < 2) {
    validTypes.push({ type: 'scatter', disabled: true, reason: 'Scatter requires at least 2 series' });
  } else {
    validTypes.push({ type: 'scatter', disabled: false });
  }

  if (categoryCount < 3) {
    validTypes.push({ type: 'radar', disabled: true, reason: 'Radar requires at least 3 categories' });
  } else {
    validTypes.push({ type: 'radar', disabled: false });
  }

  // Sort them in a consistent order
  const order: ChartRenderType[] = ['bar', 'stacked_bar', 'line', 'area', 'pie', 'donut', 'scatter', 'radar', 'table'];
  validTypes.sort((a, b) => order.indexOf(a.type) - order.indexOf(b.type));

  return validTypes;
}

export function exportToCSV(chart: CanonicalChart) {
  const headers = ['Category', ...chart.series.map(s => s.name)];
  const rows = chart.data.map(d => {
    const row = [d.category];
    chart.series.forEach(s => {
      row.push(d.values[s.id] !== null ? String(d.values[s.id]) : '');
    });
    return row.join(',');
  });

  const csvContent = [headers.join(','), ...rows].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `${chart.title || 'chart_data'}.csv`);
  link.click();
}

export function copyChartConfig(chart: CanonicalChart) {
  navigator.clipboard.writeText(JSON.stringify(chart, null, 2)).then(() => {
    alert("Chart config copied to clipboard!");
  }).catch(err => {
    console.error("Failed to copy config", err);
  });
}

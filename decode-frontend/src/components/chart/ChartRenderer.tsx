import React, { useRef, useMemo, useCallback } from 'react';
import { useChartStore } from '../../store/useChartStore';
import { ChartTableEditor } from './ChartTableEditor';
import { ChartTypeSwitcher } from './ChartTypeSwitcher';
import { toPng, toSvg } from 'html-to-image';
import { Download, AlertCircle, RefreshCw } from 'lucide-react';
import {
  BarChart, Bar, LineChart, Line, AreaChart, Area, PieChart, Pie, Cell,
  ScatterChart, Scatter, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

interface ChartRendererProps {
  chartId: string;
}

export function ChartRenderer({ chartId }: ChartRendererProps) {
  const chart = useChartStore((state) => state.charts[chartId]);
  const chartRef = useRef<HTMLDivElement>(null);

  const handleExportPNG = useCallback(() => {
    if (chartRef.current) {
      toPng(chartRef.current, { cacheBust: true, backgroundColor: 'white' })
        .then((dataUrl) => {
          const link = document.createElement('a');
          link.download = `${chart?.title || 'chart'}.png`;
          link.href = dataUrl;
          link.click();
        })
        .catch((err) => {
          console.error('Error exporting PNG:', err);
        });
    }
  }, [chart]);

  const rechartsData = useMemo(() => {
    if (!chart) return [];
    return chart.data.map(d => ({
      category: d.category,
      ...d.values
    }));
  }, [chart]);

  if (!chart) {
    return <div className="p-4 border border-dashed text-gray-400">Loading chart...</div>;
  }
  
  if (chart.series.length === 0 || chart.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full min-h-[400px] p-8 text-center bg-gray-50/50 rounded-2xl border border-dashed border-gray-200">
        <AlertCircle className="w-12 h-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-semibold text-gray-700 mb-2">Extraction Incomplete</h3>
        <p className="text-sm text-gray-500 max-w-md mb-6">
          No usable series data was extracted for this chart. The visual extractor could not confidently map the axes or legend.
        </p>
        <button 
          onClick={() => window.location.reload()}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 transition-colors font-medium text-sm"
        >
          <RefreshCw className="w-4 h-4" /> Re-extract
        </button>
      </div>
    );
  }

  // Handle Table explicitly first as it's not a Recharts component
  if (chart.activeType === 'table') {
    return (
      <div className="flex flex-col gap-2 w-full h-full">
        <ChartTypeSwitcher chartId={chartId} />
        <div className="flex-1 min-h-[400px]">
          <ChartTableEditor chartId={chartId} />
        </div>
      </div>
    );
  }

  const renderInnerChart = () => {
    switch (chart.activeType) {
      case 'bar':
      case 'stacked_bar':
        const isStacked = chart.activeType === 'stacked_bar';
        return (
          <BarChart data={rechartsData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" label={{ value: chart.xAxisLabel, position: 'insideBottom', offset: -10 }} />
            <YAxis label={{ value: chart.yAxisLabel, angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend verticalAlign="top" height={36}/>
            {chart.series.map(s => (
              <Bar key={s.id} dataKey={s.id} name={s.name} fill={s.color} stackId={isStacked ? "a" : undefined} />
            ))}
          </BarChart>
        );

      case 'line':
        return (
          <LineChart data={rechartsData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" label={{ value: chart.xAxisLabel, position: 'insideBottom', offset: -10 }} />
            <YAxis label={{ value: chart.yAxisLabel, angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend verticalAlign="top" height={36}/>
            {chart.series.map(s => (
              <Line key={s.id} type="monotone" dataKey={s.id} name={s.name} stroke={s.color} strokeWidth={2} activeDot={{ r: 8 }} />
            ))}
          </LineChart>
        );

      case 'area':
        return (
          <AreaChart data={rechartsData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" label={{ value: chart.xAxisLabel, position: 'insideBottom', offset: -10 }} />
            <YAxis label={{ value: chart.yAxisLabel, angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend verticalAlign="top" height={36}/>
            {chart.series.map(s => (
              <Area key={s.id} type="monotone" dataKey={s.id} name={s.name} fill={s.color} stroke={s.color} fillOpacity={0.3} />
            ))}
          </AreaChart>
        );

      case 'pie':
      case 'donut':
        const innerRadius = chart.activeType === 'donut' ? '50%' : 0;
        const targetSeries = chart.series[0];
        
        // Map the specific series data for Recharts Pie
        const pieData = chart.data.map(d => ({
          name: d.category,
          value: d.values[targetSeries.id] !== null ? Number(d.values[targetSeries.id]) : 0
        })).filter(d => d.value !== 0 && !isNaN(d.value));

        // Distinct colors for pie slices since they represent categories, not series
        const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658'];

        return (
          <>
            {chart.series.length > 1 && (
              <div className="absolute top-2 left-1/2 -translate-x-1/2 z-10 flex items-center gap-1.5 px-3 py-1 bg-blue-50 text-blue-700 text-xs rounded-full border border-blue-200">
                <AlertCircle size={14} />
                <span>Pie shows <strong>{targetSeries.name}</strong> only. Switch to bar/line to compare all series.</span>
              </div>
            )}
            <PieChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <Tooltip />
              <Legend verticalAlign="bottom" height={36}/>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={innerRadius}
                outerRadius="80%"
                label
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </>
        );

      case 'scatter':
        if (chart.series.length < 2) return <div>Scatter chart requires 2+ series.</div>;
        const xSeries = chart.series[0];
        const ySeries = chart.series[1];

        // Format data: { x: val1, y: val2, name: category }
        const scatterData = chart.data.map(d => ({
          name: d.category,
          x: d.values[xSeries.id],
          y: d.values[ySeries.id]
        })).filter(d => d.x !== null && d.y !== null);

        return (
          <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid />
            <XAxis type="number" dataKey="x" name={xSeries.name} label={{ value: xSeries.name, position: 'insideBottom', offset: -10 }} />
            <YAxis type="number" dataKey="y" name={ySeries.name} label={{ value: ySeries.name, angle: -90, position: 'insideLeft' }} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Legend verticalAlign="top" height={36}/>
            <Scatter name="Data" data={scatterData} fill="#8884d8" />
          </ScatterChart>
        );

      case 'radar':
        return (
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={rechartsData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <PolarGrid />
            <PolarAngleAxis dataKey="category" />
            <PolarRadiusAxis />
            <Tooltip />
            <Legend verticalAlign="top" height={36}/>
            {chart.series.map(s => (
              <Radar key={s.id} name={s.name} dataKey={s.id} stroke={s.color} fill={s.color} fillOpacity={0.6} />
            ))}
          </RadarChart>
        );
        
      default:
        return <div>Unsupported chart type: {chart.activeType}</div>;
    }
  };

  return (
    <div className="flex flex-col gap-2 w-full h-full">
      <ChartTypeSwitcher chartId={chartId} />
      
      <div className="flex flex-col flex-1 bg-white dark:bg-zinc-950 rounded-lg shadow-sm border border-gray-200 dark:border-zinc-800 min-h-[400px] overflow-hidden relative">
        <div className="flex justify-between items-center p-3 border-b border-gray-200 dark:border-zinc-800">
          <h3 className="font-semibold text-sm text-gray-700 dark:text-gray-300">
            {chart.title}
          </h3>
          <button 
            onClick={handleExportPNG}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-white dark:bg-zinc-800 border border-gray-200 dark:border-zinc-700 rounded-md hover:bg-gray-50 dark:hover:bg-zinc-700 transition-colors"
          >
            <Download size={14} /> Export Image
          </button>
        </div>
        
        <div className="flex-1 w-full relative" ref={chartRef}>
          <ResponsiveContainer width="100%" height="100%">
            {renderInnerChart()}
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

"use client";

import React, { useEffect, useState } from 'react';
import { useChartStore } from '@/store/useChartStore';
import { reconstructChart } from '@/lib/chartUtils';
import { ChartRenderer } from '@/components/chart/ChartRenderer';

const mockExtractionData = {
  id: "test_chart_123",
  title: "Quarterly Revenue by Region",
  xAxisLabel: "Quarter",
  yAxisLabel: "Revenue (M)",
  confidence: 0.95,
  series: [
    { id: "series_na", name: "North America" },
    { id: "series_eu", name: "Europe" },
    { id: "series_ap", name: "Asia Pacific" }
  ],
  data: [
    { id: "q1", category: "Q1", values: { series_na: 120, series_eu: 85, series_ap: 45 } },
    { id: "q2", category: "Q2", values: { series_na: 135, series_eu: null, series_ap: 55 } }, // simulating a missing/unreadable value
    { id: "q3", category: "Q3", values: { series_na: 150, series_eu: 105, series_ap: 65 } },
    { id: "q4", category: "Q4", values: { series_na: 175, series_eu: 120, series_ap: 80 } }
  ]
};

export default function TestChartPage() {
  const setChart = useChartStore(state => state.setChart);
  const chartId = mockExtractionData.id;
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Reconstruct into canonical shape on mount (simulate initial fetch)
    const canonical = reconstructChart(mockExtractionData, 'bar');
    setChart(canonical);
    setMounted(true);
  }, [setChart]);

  if (!mounted) return <div className="p-10">Loading test page...</div>;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-zinc-900 p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Chart Universal Reconstruction Test</h1>
        
        <div className="bg-white dark:bg-zinc-950 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-zinc-800 h-[600px]">
          <ChartRenderer chartId={chartId} />
        </div>
      </div>
    </div>
  );
}

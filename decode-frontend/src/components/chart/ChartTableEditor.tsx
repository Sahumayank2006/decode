/* eslint-disable */
// @ts-nocheck
import React, { useState } from 'react';
import { useChartStore } from '../../store/useChartStore';
import { exportToCSV, copyChartConfig } from '../../lib/chartUtils';
import { Download, Copy, Plus } from 'lucide-react';

import { CanonicalChart } from '../../store/useChartStore';

interface Props {
  chart: CanonicalChart;
}

export function ChartTableEditor({ chart }: Props) {
  const updateDataPoint = useChartStore((state) => state.updateDataPoint);
  const addCategory = useChartStore((state) => state.addCategory);
  const addSeries = useChartStore((state) => state.addSeries);

  const [newCatName, setNewCatName] = useState('');
  const [newSeriesName, setNewSeriesName] = useState('');

  if (!chart) return null;

  const handleCellChange = (
    rowIndex: number,
    seriesKey: string,
    value: string
  ) => {
    updateDataPoint(
      chart.id,
      rowIndex,
      seriesKey,
      value === ""
        ? null
        : Number.isNaN(Number(value))
          ? value
          : Number(value)
    );
  };

  const handleCellKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.currentTarget.blur();
    }
  };

  const handleAddCategory = () => {
    if (newCatName.trim()) {
      addCategory(chart.id, newCatName.trim());
      setNewCatName('');
    }
  };

  const handleAddSeries = () => {
    if (newSeriesName.trim()) {
      addSeries(chart.id, {
        id: `series_${Date.now()}`,
        name: newSeriesName.trim(),
        values: []
      });
      setNewSeriesName('');
    }
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-zinc-950 rounded-lg shadow-sm border border-gray-200 dark:border-zinc-800 overflow-hidden">
      <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-zinc-900 border-b border-gray-200 dark:border-zinc-800">
        <h3 className="font-semibold text-sm text-gray-700 dark:text-gray-300">Data Editor (Canonical)</h3>
        <div className="flex gap-2">
          <button 
            onClick={() => exportToCSV(chart)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-white dark:bg-zinc-800 border border-gray-200 dark:border-zinc-700 rounded-md hover:bg-gray-50 dark:hover:bg-zinc-700 transition-colors"
          >
            <Download size={14} /> Export CSV
          </button>
          <button 
            onClick={() => copyChartConfig(chart)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-white dark:bg-zinc-800 border border-gray-200 dark:border-zinc-700 rounded-md hover:bg-gray-50 dark:hover:bg-zinc-700 transition-colors"
          >
            <Copy size={14} /> Copy Config
          </button>
        </div>
      </div>

      <div className="overflow-x-auto p-4">
        <table className="w-full text-sm text-left border-collapse">
          <thead>
            <tr>
              <th className="px-4 py-3 bg-gray-50 dark:bg-zinc-900 border border-gray-200 dark:border-zinc-700 font-medium text-gray-900 dark:text-gray-100 min-w-[150px]">
                {chart.xAxisLabel || 'Category'}
              </th>
              {chart.series.map((s) => (
                <th key={s.id} className="px-4 py-3 bg-gray-50 dark:bg-zinc-900 border border-gray-200 dark:border-zinc-700 font-medium text-gray-900 dark:text-gray-100 min-w-[120px]">
                  {s.name}
                </th>
              ))}
              <th className="px-4 py-2 bg-gray-50 dark:bg-zinc-900 border border-gray-200 dark:border-zinc-700 w-[200px]">
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={newSeriesName}
                    onChange={(e) => setNewSeriesName(e.target.value)}
                    placeholder="New Series..."
                    className="w-full px-2 py-1 text-xs border border-gray-300 dark:border-zinc-600 rounded bg-white dark:bg-zinc-800 text-black dark:text-white"
                    onKeyDown={(e) => e.key === 'Enter' && handleAddSeries()}
                  />
                  <button onClick={handleAddSeries} className="p-1 hover:bg-gray-200 dark:hover:bg-zinc-700 rounded text-gray-500 dark:text-gray-400">
                    <Plus size={16} />
                  </button>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            {chart.data.map((row: Record<string, unknown>, rowIndex: number) => (
              <tr key={rowIndex} className="hover:bg-gray-50 dark:hover:bg-zinc-900/50">
                <td className="px-4 py-2 border border-gray-200 dark:border-zinc-700 font-medium text-gray-700 dark:text-gray-300">
                  {row.category}
                </td>
                {chart.series.map((s) => (
                  <td key={s.id} className="p-0 border border-gray-200 dark:border-zinc-700">
                    <input
                      value={
                        row?.[s.id] == null
                          ? ""
                          : String(row[s.id])
                      }
                      onChange={(event) =>
                        handleCellChange(
                          rowIndex,
                          s.id,
                          event.target.value
                        )
                      }
                      placeholder="-"
                      className="w-full h-full min-h-[40px] px-4 py-2 bg-transparent focus:bg-white dark:focus:bg-zinc-800 focus:outline-none focus:ring-1 focus:ring-blue-500 text-black dark:text-white"
                      onKeyDown={handleCellKeyDown}
                    />
                  </td>
                ))}
                <td className="border border-gray-200 dark:border-zinc-700 bg-gray-50/50 dark:bg-zinc-900/30"></td>
              </tr>
            ))}
            <tr>
              <td className="px-4 py-2 border border-gray-200 dark:border-zinc-700">
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={newCatName}
                    onChange={(e) => setNewCatName(e.target.value)}
                    placeholder="New Category..."
                    className="w-full px-2 py-1 text-xs border border-gray-300 dark:border-zinc-600 rounded bg-white dark:bg-zinc-800 text-black dark:text-white"
                    onKeyDown={(e) => e.key === 'Enter' && handleAddCategory()}
                  />
                  <button onClick={handleAddCategory} className="p-1 hover:bg-gray-200 dark:hover:bg-zinc-700 rounded text-gray-500 dark:text-gray-400">
                    <Plus size={16} />
                  </button>
                </div>
              </td>
              {chart.series.map((s) => (
                <td key={s.id} className="border border-gray-200 dark:border-zinc-700 bg-gray-50/50 dark:bg-zinc-900/30"></td>
              ))}
              <td className="border border-gray-200 dark:border-zinc-700 bg-gray-50/50 dark:bg-zinc-900/30"></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

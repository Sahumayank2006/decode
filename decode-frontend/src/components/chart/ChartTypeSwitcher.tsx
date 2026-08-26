import React from 'react';
import { CanonicalChart, ChartRenderType, useChartStore } from '../../store/useChartStore';
import { getValidChartTypes } from '../../lib/chartUtils';
import { BarChart, LineChart, PieChart, ScatterChart, Radar, Table, Activity, Layers, Circle } from 'lucide-react'; 

const TYPE_ICONS: Record<ChartRenderType, React.ReactNode> = {
  bar: <BarChart size={16} />,
  stacked_bar: <Layers size={16} />,
  line: <LineChart size={16} />,
  area: <Activity size={16} />,
  pie: <PieChart size={16} />,
  donut: <Circle size={16} />,
  scatter: <ScatterChart size={16} />,
  radar: <Radar size={16} />,
  table: <Table size={16} />,
};

interface ChartTypeSwitcherProps {
  chartId: string;
}

export function ChartTypeSwitcher({ chartId }: ChartTypeSwitcherProps) {
  const chart = useChartStore((state) => state.charts[chartId]);
  const setActiveType = useChartStore((state) => state.setActiveType);

  if (!chart) return null;

  const validTypes = getValidChartTypes(chart);

  return (
    <div className="flex flex-wrap gap-1.5 mb-4 p-1 bg-gray-100/80 dark:bg-zinc-900 rounded-lg border border-gray-200 dark:border-zinc-800">
      {validTypes.map(({ type, disabled, reason }) => {
        const isActive = chart.activeType === type;
        
        return (
          <div key={type} className="relative group">
            <button
              onClick={() => !disabled && setActiveType(chartId, type)}
              disabled={disabled}
              className={`
                flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200
                ${isActive 
                  ? 'bg-white text-blue-600 shadow-sm dark:bg-zinc-800 dark:text-blue-400' 
                  : 'text-gray-600 hover:bg-gray-200/50 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-zinc-800/50 dark:hover:text-gray-200'
                }
                ${disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}
              `}
              aria-label={`Switch to ${type}`}
            >
              {TYPE_ICONS[type]}
              <span className="capitalize">{type.replace('_', ' ')}</span>
            </button>
            
            {disabled && reason && (
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 pointer-events-none">
                {reason}
                <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

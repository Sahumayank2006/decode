// Chart configuration templates for edge cases
export interface ChartTemplate {
  id: string
  name: string
  description: string
  baseType: 'bar' | 'line' | 'area' | 'pie' | 'doughnut' | 'scatter' | 'mixed'
  variants: ChartVariant[]
}

export interface ChartVariant {
  id: string
  name: string
  weight: number // Probability weight for random selection
  config: ChartConfigTemplate
}

export interface ChartConfigTemplate {
  // Data configuration
  dataSeries?: number // Number of data series (for multi-series charts)
  dataSize: [number, number] // Min/max data points
  valueRange: [number, number] // Min/max values
  allowNegatives?: boolean
  dataPatterns?: DataPattern[] // Special data patterns

  // Visual configuration
  colorSchemes: string[]
  customColors?: string[]
  
  // Chart-specific options
  chartOptions?: {
    stacked?: boolean
    grouped?: boolean
    smooth?: boolean
    showDataLabels?: boolean
    orientation?: 'horizontal' | 'vertical'
    pieStartAngle?: number
    doughnutInnerRadius?: string
  }

  // Special features
  annotations?: AnnotationConfig[]
  multiAxis?: boolean
  legend?: LegendConfig
  customTitle?: boolean
}

export interface DataPattern {
  type: 'trend' | 'seasonal' | 'outliers' | 'missing' | 'sparse'
  intensity: number // 0-1 scale
}

export interface AnnotationConfig {
  type: 'line' | 'band' | 'point' | 'text'
  position?: string
  color?: string
}

export interface LegendConfig {
  show: boolean
  position: 'top' | 'bottom' | 'left' | 'right'
  orientation: 'horizontal' | 'vertical'
}

// Predefined templates for different edge cases
export const CHART_TEMPLATES: ChartTemplate[] = [
  {
    id: 'basic-bar',
    name: 'Basic Bar Charts',
    description: 'Simple single-series bar charts',
    baseType: 'bar',
    variants: [
      {
        id: 'vertical-bar',
        name: 'Vertical Bar',
        weight: 0.4,
        config: {
          dataSize: [3, 8],
          valueRange: [0, 100],
          colorSchemes: ['vibrant', 'pastel'],
          chartOptions: { orientation: 'vertical' }
        }
      },
      {
        id: 'horizontal-bar',
        name: 'Horizontal Bar',
        weight: 0.3,
        config: {
          dataSize: [3, 6],
          valueRange: [0, 100],
          colorSchemes: ['monochrome', 'earth'],
          chartOptions: { orientation: 'horizontal' }
        }
      },
      {
        id: 'negative-bar',
        name: 'Bar with Negatives',
        weight: 0.3,
        config: {
          dataSize: [4, 7],
          valueRange: [-50, 50],
          allowNegatives: true,
          colorSchemes: ['ocean'],
          dataPatterns: [{ type: 'trend', intensity: 0.3 }]
        }
      }
    ]
  },

  {
    id: 'multi-series-bar',
    name: 'Multi-Series Bar Charts',
    description: 'Bar charts with multiple data series',
    baseType: 'bar',
    variants: [
      {
        id: 'grouped-bar',
        name: 'Grouped Bar',
        weight: 0.5,
        config: {
          dataSeries: 2,
          dataSize: [4, 6],
          valueRange: [0, 100],
          colorSchemes: ['vibrant'],
          chartOptions: { grouped: true }
        }
      },
      {
        id: 'stacked-bar',
        name: 'Stacked Bar',
        weight: 0.5,
        config: {
          dataSeries: 3,
          dataSize: [3, 5],
          valueRange: [10, 80],
          colorSchemes: ['pastel', 'earth'],
          chartOptions: { stacked: true }
        }
      }
    ]
  },

  {
    id: 'advanced-pie',
    name: 'Advanced Pie Charts',
    description: 'Pie charts with special configurations',
    baseType: 'pie',
    variants: [
      {
        id: 'labeled-pie',
        name: 'Pie with Data Labels',
        weight: 0.4,
        config: {
          dataSize: [4, 8],
          valueRange: [5, 100],
          colorSchemes: ['vibrant', 'pastel'],
          chartOptions: { 
            showDataLabels: true,
            pieStartAngle: 0
          }
        }
      },
      {
        id: 'rotated-pie',
        name: 'Rotated Pie',
        weight: 0.3,
        config: {
          dataSize: [3, 6],
          valueRange: [10, 80],
          colorSchemes: ['monochrome'],
          chartOptions: { pieStartAngle: 90 }
        }
      },
      {
        id: 'sparse-pie',
        name: 'Sparse Data Pie',
        weight: 0.3,
        config: {
          dataSize: [6, 10],
          valueRange: [1, 20],
          colorSchemes: ['ocean'],
          dataPatterns: [{ type: 'sparse', intensity: 0.7 }]
        }
      }
    ]
  },

  {
    id: 'trend-lines',
    name: 'Trend Line Charts',
    description: 'Line charts with trend patterns',
    baseType: 'line',
    variants: [
      {
        id: 'smooth-trend',
        name: 'Smooth Trend Line',
        weight: 0.4,
        config: {
          dataSize: [8, 15],
          valueRange: [0, 100],
          colorSchemes: ['vibrant'],
          chartOptions: { smooth: true },
          dataPatterns: [{ type: 'trend', intensity: 0.8 }]
        }
      },
      {
        id: 'seasonal-pattern',
        name: 'Seasonal Pattern',
        weight: 0.3,
        config: {
          dataSize: [12, 24],
          valueRange: [20, 80],
          colorSchemes: ['earth', 'ocean'],
          dataPatterns: [{ type: 'seasonal', intensity: 0.6 }]
        }
      },
      {
        id: 'outlier-data',
        name: 'Data with Outliers',
        weight: 0.3,
        config: {
          dataSize: [8, 12],
          valueRange: [0, 100],
          colorSchemes: ['monochrome'],
          dataPatterns: [
            { type: 'outliers', intensity: 0.2 },
            { type: 'trend', intensity: 0.4 }
          ]
        }
      }
    ]
  },

  {
    id: 'edge-cases',
    name: 'Special Edge Cases',
    description: 'Unusual chart configurations',
    baseType: 'mixed',
    variants: [
      {
        id: 'tiny-dataset',
        name: 'Minimal Data',
        weight: 0.2,
        config: {
          dataSize: [2, 3],
          valueRange: [0, 10],
          colorSchemes: ['vibrant', 'pastel'],
          dataPatterns: [{ type: 'sparse', intensity: 0.9 }]
        }
      },
      {
        id: 'large-dataset',
        name: 'Large Dataset',
        weight: 0.2,
        config: {
          dataSize: [20, 30],
          valueRange: [0, 1000],
          colorSchemes: ['monochrome', 'ocean'],
          dataPatterns: [{ type: 'trend', intensity: 0.3 }]
        }
      },
      {
        id: 'decimal-precision',
        name: 'High Precision Decimals',
        weight: 0.2,
        config: {
          dataSize: [5, 8],
          valueRange: [-1, 1],
          allowNegatives: true,
          colorSchemes: ['earth'],
          dataPatterns: [{ type: 'outliers', intensity: 0.1 }]
        }
      },
      {
        id: 'zero-heavy',
        name: 'Zero-Heavy Data',
        weight: 0.2,
        config: {
          dataSize: [6, 10],
          valueRange: [0, 50],
          colorSchemes: ['pastel'],
          dataPatterns: [{ type: 'sparse', intensity: 0.8 }]
        }
      },
      {
        id: 'custom-annotations',
        name: 'Annotated Charts',
        weight: 0.2,
        config: {
          dataSize: [5, 8],
          valueRange: [0, 100],
          colorSchemes: ['vibrant'],
          annotations: [
            { type: 'line', position: 'average' },
            { type: 'text', position: 'max' }
          ]
        }
      }
    ]
  }
]

// Template selection logic
export class TemplateSelector {
  private rng: any

  constructor(rng: any) {
    this.rng = rng
  }

  selectTemplate(templateId?: string): { template: ChartTemplate, variant: ChartVariant } {
    let selectedTemplate: ChartTemplate
    
    if (templateId) {
      selectedTemplate = CHART_TEMPLATES.find(t => t.id === templateId)!
    } else {
      selectedTemplate = this.rng.choice(CHART_TEMPLATES)
    }

    // Weighted selection of variant
    const totalWeight = selectedTemplate.variants.reduce((sum, v) => sum + v.weight, 0)
    let randomWeight = this.rng.next() * totalWeight
    
    let selectedVariant = selectedTemplate.variants[0]
    for (const variant of selectedTemplate.variants) {
      randomWeight -= variant.weight
      if (randomWeight <= 0) {
        selectedVariant = variant
        break
      }
    }

    return { template: selectedTemplate, variant: selectedVariant }
  }
}
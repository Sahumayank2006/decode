import './style.css'
import * as echarts from 'echarts'

interface ChartVariant {
  id: string
  name: string
  weight: number
  config: any
}

// Simplified template data
const EDGE_CASE_TEMPLATES = [
  {
    id: 'tiny-dataset',
    name: 'Minimal Data',
    weight: 0.2,
    config: {
      dataSize: [2, 3],
      valueRange: [0, 10],
      colorSchemes: ['vibrant', 'pastel']
    }
  },
  {
    id: 'large-dataset', 
    name: 'Large Dataset',
    weight: 0.2,
    config: {
      dataSize: [15, 20],
      valueRange: [0, 1000],
      colorSchemes: ['monochrome', 'ocean']
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
      colorSchemes: ['earth']
    }
  },
  {
    id: 'zero-heavy',
    name: 'Zero-Heavy Data',
    weight: 0.2,
    config: {
      dataSize: [6, 10], 
      valueRange: [0, 20],
      colorSchemes: ['pastel']
    }
  },
  {
    id: 'negative-values',
    name: 'Negative Heavy',
    weight: 0.2,
    config: {
      dataSize: [4, 7],
      valueRange: [-100, 50],
      allowNegatives: true,
      colorSchemes: ['vibrant']
    }
  }
]

// Seeded random number generator for reproducible results
class SeededRandom {
  private seed: number

  constructor(seed: string | number) {
    this.seed = typeof seed === 'string' ? this.hashCode(seed) : seed
  }

  private hashCode(str: string): number {
    let hash = 0
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32-bit integer
    }
    return Math.abs(hash)
  }

  next(): number {
    this.seed = (this.seed * 9301 + 49297) % 233280
    return this.seed / 233280
  }

  range(min: number, max: number): number {
    return min + this.next() * (max - min)
  }

  choice<T>(array: T[]): T {
    return array[Math.floor(this.next() * array.length)]
  }

  shuffle<T>(array: T[]): T[] {
    const result = [...array]
    for (let i = result.length - 1; i > 0; i--) {
      const j = Math.floor(this.next() * (i + 1));
      [result[i], result[j]] = [result[j], result[i]]
    }
    return result
  }
}

// Configuration types
type ChartType = 'bar' | 'line' | 'area' | 'pie' | 'doughnut'
type ColorScheme = 'vibrant' | 'pastel' | 'monochrome' | 'earth' | 'ocean'

interface ChartParams {
  type: ChartType
  dataSize: number
  minValue: number
  maxValue: number
  colorScheme: ColorScheme
  includeNegatives: boolean
}

// Color palettes for different schemes
const COLOR_PALETTES = {
  vibrant: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF'],
  pastel: ['#FFD93D', '#6BCF7F', '#4D96FF', '#FF6B9D', '#C44569', '#F8B500', '#6C5CE7'],
  monochrome: ['#2C3E50', '#34495E', '#7F8C8D', '#95A5A6', '#BDC3C7', '#ECF0F1', '#1ABC9C'],
  earth: ['#8D6E63', '#A1887F', '#BCAAA4', '#D7CCC8', '#8BC34A', '#4CAF50', '#FF9800'],
  ocean: ['#006064', '#00838F', '#0097A7', '#00ACC1', '#26C6DA', '#4DD0E1', '#80DEEA']
}

// Label generators
const CATEGORIES = {
  months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  quarters: ['Q1', 'Q2', 'Q3', 'Q4'],
  products: ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
  regions: ['North', 'South', 'East', 'West', 'Central'],
  departments: ['Sales', 'Marketing', 'Engineering', 'Support', 'HR'],
  categories: ['Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5']
}

class ChartGenerator {
  private rng: SeededRandom
  private params: ChartParams

  constructor(seed: string, params: ChartParams) {
    this.rng = new SeededRandom(seed)
    this.params = params
  }

  generateData(): number[] {
    const data: number[] = []
    for (let i = 0; i < this.params.dataSize; i++) {
      let value = this.rng.range(this.params.minValue, this.params.maxValue)
      
      // Special edge case handling
      if (this.params.minValue === -1 && this.params.maxValue === 1) {
        // High precision decimals - round to 3 decimal places
        value = Math.round(value * 1000) / 1000
      } else if (this.params.maxValue <= 20) {
        // Zero-heavy data - 30% chance of zero
        if (this.rng.next() < 0.3) {
          value = 0
        } else {
          value = Math.round(value * 10) / 10 // 1 decimal place
        }
      } else {
        // Regular rounding to 2 decimal places
        value = Math.round(value * 100) / 100
      }
      
      // Ensure we don't include negatives if not wanted
      if (!this.params.includeNegatives && value < 0) {
        value = Math.abs(value)
      }
      
      data.push(value)
    }
    return data
  }

  generateLabels(): string[] {
    const categoryKeys = Object.keys(CATEGORIES) as (keyof typeof CATEGORIES)[]
    const selectedCategory = this.rng.choice(categoryKeys)
    const availableLabels = CATEGORIES[selectedCategory]
    
    // If we need more labels than available, generate generic ones
    if (this.params.dataSize <= availableLabels.length) {
      return this.rng.shuffle(availableLabels).slice(0, this.params.dataSize)
    } else {
      const labels: string[] = []
      for (let i = 0; i < this.params.dataSize; i++) {
        labels.push(`Item ${i + 1}`)
      }
      return labels
    }
  }

  generateColors(): string[] {
    const palette = COLOR_PALETTES[this.params.colorScheme]
    const colors: string[] = []
    
    for (let i = 0; i < this.params.dataSize; i++) {
      colors.push(palette[i % palette.length])
    }
    
    return this.rng.shuffle(colors)
  }

  generateChart(): any {
    const data = this.generateData()
    const labels = this.generateLabels()
    const colors = this.generateColors()
    
    const baseConfig = {
      animation: false,
      backgroundColor: '#ffffff',
      title: {
        text: this.generateTitle(),
        left: 'center',
        top: 20,
        textStyle: {
          fontSize: 16,
          color: '#333'
        }
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b} : {c} ({d}%)'
      }
    }

    switch (this.params.type) {
      case 'bar':
        return {
          ...baseConfig,
          xAxis: {
            type: 'category',
            data: labels,
            axisLabel: { color: '#666' }
          },
          yAxis: {
            type: 'value',
            axisLabel: { color: '#666' }
          },
          series: [{
            name: 'Data',
            type: 'bar',
            data: data,
            itemStyle: {
              color: (params: any) => colors[params.dataIndex]
            }
          }]
        }

      case 'line':
        return {
          ...baseConfig,
          xAxis: {
            type: 'category',
            data: labels,
            axisLabel: { color: '#666' }
          },
          yAxis: {
            type: 'value',
            axisLabel: { color: '#666' }
          },
          series: [{
            name: 'Data',
            type: 'line',
            data: data,
            lineStyle: { color: colors[0], width: 3 },
            itemStyle: { color: colors[0] },
            smooth: this.rng.next() > 0.5
          }]
        }

      case 'area':
        return {
          ...baseConfig,
          xAxis: {
            type: 'category',
            data: labels,
            axisLabel: { color: '#666' }
          },
          yAxis: {
            type: 'value',
            axisLabel: { color: '#666' }
          },
          series: [{
            name: 'Data',
            type: 'line',
            data: data,
            areaStyle: { color: colors[0] + '40' }, // Add transparency
            lineStyle: { color: colors[0], width: 2 },
            itemStyle: { color: colors[0] },
            smooth: this.rng.next() > 0.5
          }]
        }

      case 'pie':
        return {
          ...baseConfig,
          series: [{
            name: 'Data',
            type: 'pie',
            radius: '70%',
            center: ['50%', '60%'],
            data: labels.map((label, index) => ({
              value: data[index],
              name: label,
              itemStyle: { color: colors[index] }
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }]
        }

      case 'doughnut':
        return {
          ...baseConfig,
          series: [{
            name: 'Data',
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '60%'],
            data: labels.map((label, index) => ({
              value: data[index],
              name: label,
              itemStyle: { color: colors[index] }
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }]
        }

      default:
        throw new Error(`Unsupported chart type: ${this.params.type}`)
    }
  }

  private generateTitle(): string {
    const titles = [
      'Sales Performance',
      'Revenue Analysis',
      'Market Share',
      'Growth Metrics',
      'Performance Overview',
      'Data Insights',
      'Trend Analysis',
      'Key Metrics'
    ]
    return this.rng.choice(titles)
  }
}

// Parse URL parameters
const params = new URLSearchParams(window.location.search)
const seed = params.get('seed') || Date.now().toString()
const template = params.get('template')

// Create RNG instance
const rng = new SeededRandom(seed)

let chartParams: ChartParams
let selectedVariant: ChartVariant | null = null

if (template === 'edge-cases') {
  // Select random edge case variant
  const totalWeight = EDGE_CASE_TEMPLATES.reduce((sum, v) => sum + v.weight, 0)
  let randomWeight = rng.next() * totalWeight
  
  selectedVariant = EDGE_CASE_TEMPLATES[0]
  for (const variant of EDGE_CASE_TEMPLATES) {
    randomWeight -= variant.weight
    if (randomWeight <= 0) {
      selectedVariant = variant
      break
    }
  }
  
  console.log('Using edge case variant:', selectedVariant.name, selectedVariant.config)
  
  // Build chart params from template
  const config = selectedVariant.config
  
  // URL parameters override template defaults
  const dataSize = params.has('dataSize') 
    ? parseInt(params.get('dataSize')!)
    : Math.floor(rng.range(config.dataSize[0], config.dataSize[1] + 1))
  
  chartParams = {
    type: (params.get('type') as ChartType) || 'bar',
    dataSize: dataSize,
    minValue: parseFloat(params.get('minValue') || config.valueRange[0].toString()),
    maxValue: parseFloat(params.get('maxValue') || config.valueRange[1].toString()),
    colorScheme: (params.get('colorScheme') as ColorScheme) || (rng.choice(config.colorSchemes) as ColorScheme),
    includeNegatives: params.has('includeNegatives') 
      ? (params.get('includeNegatives') === 'true' || params.get('includeNegatives') === 'yes')
      : (config.allowNegatives || false)
  }
} else {
  // Use URL parameter-based generation (backwards compatibility)
  chartParams = {
    type: (params.get('type') as ChartType) || 'bar',
    dataSize: parseInt(params.get('dataSize') || '5'),
    minValue: parseFloat(params.get('minValue') || '0'),
    maxValue: parseFloat(params.get('maxValue') || '100'),
    colorScheme: (params.get('colorScheme') as ColorScheme) || 'vibrant',
    includeNegatives: params.get('includeNegatives') === 'true' || params.get('includeNegatives') === 'yes'
  }
}

console.log('Chart Generation Params:', { 
  seed, 
  templateUsed: !!template,
  variant: selectedVariant?.name || 'none',
  ...chartParams 
})

// Initialize chart ready state
window.chartReady = false

// Generate chart
const generator = new ChartGenerator(seed, chartParams)
const option = generator.generateChart()

// Initialize ECharts instance
const chartDom = document.getElementById('chart')!
const myChart = echarts.init(chartDom)
myChart.on('finished', () => {
  console.log('Chart rendering finished')
  window.chartReady = true
})

// Set chart option
myChart.setOption(option)

// Expose comprehensive chart config to window for Python script access
declare global {
  interface Window {
    chartConfig: {
      generatedOption: typeof option
      metadata: {
        seed: string
        template: string | null
        variantName: string | null
        chartType: ChartType
        dataSize: number
        valueRange: [number, number]
        colorScheme: ColorScheme
        colors: string[]
        labels: string[]
        values: number[]
      }
    }
    chartReady: boolean
  }
}

// Extract colors and labels for ML training
const extractColorsAndLabels = (config: any) => {
  const colors: string[] = []
  const labels: string[] = []
  const values: number[] = []

  if (config.series && config.series[0]) {
    const series = config.series[0]
    
    if (series.type === 'pie') {
      // Pie/Doughnut charts
      series.data.forEach((item: any) => {
        colors.push(item.itemStyle.color)
        labels.push(item.name)
        values.push(item.value)
      })
    } else if (series.type === 'bar') {
      // Bar charts
      labels.push(...config.xAxis.data)
      values.push(...series.data)
      // Colors are generated dynamically, extract from generator
      const gen = new ChartGenerator(seed, chartParams)
      colors.push(...gen.generateColors())
    } else if (series.type === 'line') {
      // Line/Area charts
      labels.push(...config.xAxis.data)
      values.push(...series.data)
      colors.push(series.lineStyle.color)
    }
  }

  return { colors, labels, values }
}

const { colors, labels, values } = extractColorsAndLabels(option)

window.chartConfig = {
  generatedOption: option,
  metadata: {
    seed,
    template: template || null,
    variantName: selectedVariant?.name || null,
    chartType: chartParams.type,
    dataSize: chartParams.dataSize,
    valueRange: [chartParams.minValue, chartParams.maxValue],
    colorScheme: chartParams.colorScheme,
    colors,
    labels,
    values
  }
}

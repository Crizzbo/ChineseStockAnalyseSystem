import React, { useRef, useEffect, useState } from 'react'
import { Card, Radio, Select, Space, Typography } from 'antd'
import { FullscreenOutlined, DownloadOutlined } from '@ant-design/icons'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import type { StockInfo } from '@store/modules/stocks'
import './StockChart.scss'

const { Title } = Typography

export interface StockPriceData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface StockChartProps {
  title?: string
  data: StockPriceData[]
  height?: number
  showControls?: boolean
}

const StockChart: React.FC<StockChartProps> = ({
  title = '股票走势图',
  data,
  height = 400,
  showControls = true
}) => {
  const chartRef = useRef<HTMLDivElement>(null)
  const chartInstance = useRef<echarts.ECharts | null>(null)
  const [chartType, setChartType] = useState<'line' | 'candlestick'>('candlestick')
  const [timeRange, setTimeRange] = useState('all')

  useEffect(() => {
    if (!chartRef.current || !data.length) return

    // 初始化图表
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current)
    }

    const chart = chartInstance.current

    // 处理数据
    const processedData = data.map(item => [
      item.date,
      item.open,
      item.close,
      item.low,
      item.high,
      item.volume
    ])

    const dates = data.map(item => item.date)
    const volumes = data.map(item => item.volume)

    let option: EChartsOption

    if (chartType === 'candlestick') {
      // K线图配置
      option = {
        animation: true,
        legend: {
          bottom: 10,
          left: 'center',
          data: ['K线', '成交量']
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
          borderWidth: 1,
          borderColor: '#ccc',
          padding: 10,
          textStyle: {
            color: '#000'
          },
          formatter: function (params: any) {
            const data = params[0]
            if (!data || !data.data) return ''

            const [date, open, close, low, high] = data.data
            const change = ((close - open) / open * 100).toFixed(2)
            const changeColor = close >= open ? '#ff4d4f' : '#52c41a'

            return `
              <div>
                <div><strong>${date}</strong></div>
                <div>开盘: ${open}</div>
                <div>收盘: <span style="color: ${changeColor}">${close}</span></div>
                <div>最高: ${high}</div>
                <div>最低: ${low}</div>
                <div>涨跌幅: <span style="color: ${changeColor}">${change}%</span></div>
              </div>
            `
          }
        },
        axisPointer: {
          link: [
            {
              xAxisIndex: 'all'
            }
          ],
          label: {
            backgroundColor: '#777'
          }
        },
        grid: [
          {
            left: '10%',
            right: '8%',
            height: '50%'
          },
          {
            left: '10%',
            right: '8%',
            top: '65%',
            height: '16%'
          }
        ],
        xAxis: [
          {
            type: 'category',
            data: dates,
            boundaryGap: false,
            axisLine: { onZero: false },
            splitLine: { show: false },
            min: 'dataMin',
            max: 'dataMax'
          },
          {
            type: 'category',
            gridIndex: 1,
            data: dates,
            boundaryGap: false,
            axisLine: { onZero: false },
            axisTick: { show: false },
            splitLine: { show: false },
            axisLabel: { show: false },
            min: 'dataMin',
            max: 'dataMax'
          }
        ],
        yAxis: [
          {
            scale: true,
            splitArea: {
              show: true
            }
          },
          {
            scale: true,
            gridIndex: 1,
            splitNumber: 2,
            axisLabel: { show: false },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { show: false }
          }
        ],
        dataZoom: [
          {
            type: 'inside',
            xAxisIndex: [0, 1],
            start: 80,
            end: 100
          },
          {
            show: true,
            xAxisIndex: [0, 1],
            type: 'slider',
            top: '85%',
            start: 80,
            end: 100
          }
        ],
        series: [
          {
            name: 'K线',
            type: 'candlestick',
            data: processedData.map(item => [item[1], item[2], item[3], item[4]]),
            itemStyle: {
              color: '#ff4d4f',
              color0: '#52c41a',
              borderColor: '#ff4d4f',
              borderColor0: '#52c41a'
            }
          },
          {
            name: '成交量',
            type: 'bar',
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: volumes,
            itemStyle: {
              color: function(params: any) {
                const dataIndex = params.dataIndex
                if (dataIndex === 0) return '#1890ff'
                const current = processedData[dataIndex]
                const prev = processedData[dataIndex - 1]
                return current[2] >= prev[2] ? '#ff4d4f' : '#52c41a'
              }
            }
          }
        ]
      }
    } else {
      // 线图配置
      const closeData = data.map(item => item.close)

      option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['收盘价', '成交量']
        },
        grid: [
          {
            left: '10%',
            right: '8%',
            height: '50%'
          },
          {
            left: '10%',
            right: '8%',
            top: '65%',
            height: '16%'
          }
        ],
        xAxis: [
          {
            type: 'category',
            boundaryGap: false,
            data: dates
          },
          {
            type: 'category',
            gridIndex: 1,
            data: dates,
            axisLabel: { show: false }
          }
        ],
        yAxis: [
          {
            type: 'value',
            scale: true
          },
          {
            type: 'value',
            gridIndex: 1,
            axisLabel: { show: false }
          }
        ],
        dataZoom: [
          {
            type: 'inside',
            start: 80,
            end: 100
          },
          {
            show: true,
            type: 'slider',
            top: '85%',
            start: 80,
            end: 100
          }
        ],
        series: [
          {
            name: '收盘价',
            type: 'line',
            data: closeData,
            smooth: true,
            lineStyle: {
              width: 2
            },
            areaStyle: {
              opacity: 0.2
            }
          },
          {
            name: '成交量',
            type: 'bar',
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: volumes,
            itemStyle: {
              color: '#1890ff',
              opacity: 0.7
            }
          }
        ]
      }
    }

    chart.setOption(option, true)

    // 响应式调整
    const handleResize = () => {
      chart.resize()
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [data, chartType])

  useEffect(() => {
    return () => {
      if (chartInstance.current) {
        chartInstance.current.dispose()
      }
    }
  }, [])

  const handleExport = () => {
    if (chartInstance.current) {
      const url = chartInstance.current.getDataURL({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: '#fff'
      })
      const link = document.createElement('a')
      link.href = url
      link.download = `${title}-${new Date().toISOString().split('T')[0]}.png`
      link.click()
    }
  }

  const handleFullscreen = () => {
    if (chartRef.current) {
      if (chartRef.current.requestFullscreen) {
        chartRef.current.requestFullscreen()
      }
    }
  }

  return (
    <Card
      title={<Title level={4}>{title}</Title>}
      className="stock-chart-card"
      extra={
        showControls && (
          <Space>
            <Radio.Group
              value={chartType}
              onChange={(e) => setChartType(e.target.value)}
              size="small"
            >
              <Radio.Button value="line">线图</Radio.Button>
              <Radio.Button value="candlestick">K线</Radio.Button>
            </Radio.Group>

            <Select
              value={timeRange}
              onChange={setTimeRange}
              size="small"
              style={{ width: 80 }}
            >
              <Select.Option value="1d">1日</Select.Option>
              <Select.Option value="5d">5日</Select.Option>
              <Select.Option value="1m">1月</Select.Option>
              <Select.Option value="3m">3月</Select.Option>
              <Select.Option value="1y">1年</Select.Option>
              <Select.Option value="all">全部</Select.Option>
            </Select>

            <Space.Compact>
              <button
                className="chart-action-btn"
                onClick={handleFullscreen}
                title="全屏"
              >
                <FullscreenOutlined />
              </button>
              <button
                className="chart-action-btn"
                onClick={handleExport}
                title="导出图片"
              >
                <DownloadOutlined />
              </button>
            </Space.Compact>
          </Space>
        )
      }
    >
      <div
        ref={chartRef}
        style={{ height, width: '100%' }}
        className="stock-chart-container"
      />
    </Card>
  )
}

export default StockChart
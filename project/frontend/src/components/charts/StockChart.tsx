import React, { useEffect, useRef } from 'react'
import { Empty } from 'antd'
import * as echarts from 'echarts'

interface StockChartProps {
  data: any[]
  type: 'line' | 'candlestick'
  height?: number
  symbol?: string
}

const StockChart: React.FC<StockChartProps> = ({
  data,
  type = 'candlestick',
  height = 400,
  symbol
}) => {
  const chartRef = useRef<HTMLDivElement>(null)
  const chartInstance = useRef<echarts.ECharts | null>(null)

  useEffect(() => {
    if (!chartRef.current || !data || data.length === 0) return

    // 初始化图表
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current)
    }

    // 处理数据
    const processedData = data.map(item => ({
      date: item.date,
      open: item.open,
      close: item.close,
      high: item.high,
      low: item.low,
      volume: item.volume
    }))

    const dates = processedData.map(item => item.date)
    const values = processedData.map(item => [item.open, item.close, item.low, item.high])
    const volumes = processedData.map(item => item.volume)

    // 计算移动平均线
    const calculateMA = (dayCount: number) => {
      const result = []
      for (let i = 0; i < processedData.length; i++) {
        if (i < dayCount - 1) {
          result.push('-')
        } else {
          let sum = 0
          for (let j = 0; j < dayCount; j++) {
            sum += processedData[i - j].close
          }
          result.push((sum / dayCount).toFixed(2))
        }
      }
      return result
    }

    const ma5 = calculateMA(5)
    const ma10 = calculateMA(10)
    const ma20 = calculateMA(20)

    let option: any

    if (type === 'line') {
      // 线图配置
      option = {
        title: {
          text: symbol ? `${symbol} 价格走势` : '价格走势',
          left: 0,
          textStyle: {
            fontSize: 16,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
          formatter: function (params: any) {
            let result = `${params[0].axisValue}<br/>`
            params.forEach((param: any) => {
              const color = param.color
              result += `<span style="display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:${color}"></span>`
              result += `${param.seriesName}: ${param.value}<br/>`
            })
            return result
          }
        },
        legend: {
          data: ['收盘价', 'MA5', 'MA10', 'MA20'],
          top: 30
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%',
          top: '15%'
        },
        xAxis: {
          type: 'category',
          data: dates,
          scale: true,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false },
          min: 'dataMin',
          max: 'dataMax'
        },
        yAxis: {
          scale: true,
          splitArea: {
            show: true
          }
        },
        dataZoom: [
          {
            type: 'inside',
            start: 50,
            end: 100
          },
          {
            show: true,
            type: 'slider',
            top: '90%',
            start: 50,
            end: 100
          }
        ],
        series: [
          {
            name: '收盘价',
            type: 'line',
            data: processedData.map(item => item.close),
            smooth: true,
            lineStyle: {
              width: 2
            },
            itemStyle: {
              color: '#1890ff'
            }
          },
          {
            name: 'MA5',
            type: 'line',
            data: ma5,
            smooth: true,
            lineStyle: {
              width: 1,
              opacity: 0.8
            },
            itemStyle: {
              color: '#f5222d'
            }
          },
          {
            name: 'MA10',
            type: 'line',
            data: ma10,
            smooth: true,
            lineStyle: {
              width: 1,
              opacity: 0.8
            },
            itemStyle: {
              color: '#52c41a'
            }
          },
          {
            name: 'MA20',
            type: 'line',
            data: ma20,
            smooth: true,
            lineStyle: {
              width: 1,
              opacity: 0.8
            },
            itemStyle: {
              color: '#fa8c16'
            }
          }
        ]
      }
    } else {
      // K线图配置
      option = {
        title: {
          text: symbol ? `${symbol} K线图` : 'K线图',
          left: 0,
          textStyle: {
            fontSize: 16,
            fontWeight: 'normal'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
          formatter: function (params: any) {
            const data = params[0]
            const value = data.value
            return `${data.axisValue}<br/>
                    开盘: ${value[1]}<br/>
                    收盘: ${value[2]}<br/>
                    最低: ${value[3]}<br/>
                    最高: ${value[4]}<br/>`
          }
        },
        legend: {
          data: ['K线', 'MA5', 'MA10', 'MA20'],
          top: 30
        },
        grid: {
          left: '10%',
          right: '10%',
          bottom: '15%',
          top: '15%'
        },
        xAxis: {
          type: 'category',
          data: dates,
          scale: true,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false },
          min: 'dataMin',
          max: 'dataMax'
        },
        yAxis: {
          scale: true,
          splitArea: {
            show: true
          }
        },
        dataZoom: [
          {
            type: 'inside',
            start: 50,
            end: 100
          },
          {
            show: true,
            type: 'slider',
            top: '90%',
            start: 50,
            end: 100
          }
        ],
        series: [
          {
            name: 'K线',
            type: 'candlestick',
            data: values,
            itemStyle: {
              color: '#f5222d',
              color0: '#52c41a',
              borderColor: '#f5222d',
              borderColor0: '#52c41a'
            }
          },
          {
            name: 'MA5',
            type: 'line',
            data: ma5,
            smooth: true,
            lineStyle: {
              width: 1,
              opacity: 0.8
            },
            itemStyle: {
              color: '#1890ff'
            }
          },
          {
            name: 'MA10',
            type: 'line',
            data: ma10,
            smooth: true,
            lineStyle: {
              width: 1,
              opacity: 0.8
            },
            itemStyle: {
              color: '#722ed1'
            }
          },
          {
            name: 'MA20',
            type: 'line',
            data: ma20,
            smooth: true,
            lineStyle: {
              width: 1,
              opacity: 0.8
            },
            itemStyle: {
              color: '#fa8c16'
            }
          }
        ]
      }
    }

    chartInstance.current.setOption(option, true)

    // 响应式
    const handleResize = () => {
      chartInstance.current?.resize()
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [data, type, symbol])

  useEffect(() => {
    return () => {
      chartInstance.current?.dispose()
    }
  }, [])

  if (!data || data.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Empty description="暂无数据" />
      </div>
    )
  }

  return (
    <div
      ref={chartRef}
      style={{
        width: '100%',
        height: height
      }}
    />
  )
}

export default StockChart
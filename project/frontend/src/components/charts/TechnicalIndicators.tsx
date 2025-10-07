import React, { useEffect, useRef } from 'react'
import { Empty } from 'antd'
import * as echarts from 'echarts'

interface TechnicalIndicatorsProps {
  data: any[]
  type: 'volume' | 'rsi' | 'macd' | 'kdj'
  height?: number
}

const TechnicalIndicators: React.FC<TechnicalIndicatorsProps> = ({
  data,
  type,
  height = 200
}) => {
  const chartRef = useRef<HTMLDivElement>(null)
  const chartInstance = useRef<echarts.ECharts | null>(null)

  useEffect(() => {
    if (!chartRef.current || !data || data.length === 0) return

    // 初始化图表
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current)
    }

    const dates = data.map(item => item.date)
    let option: any

    switch (type) {
      case 'volume':
        // 成交量图表
        const volumes = data.map(item => item.volume)
        const volumeColors = data.map((item, index) => {
          if (index === 0) return '#1890ff'
          return item.close >= item.open ? '#f5222d' : '#52c41a'
        })

        option = {
          title: {
            text: '成交量',
            left: 0,
            textStyle: {
              fontSize: 14,
              fontWeight: 'normal'
            }
          },
          tooltip: {
            trigger: 'axis',
            formatter: function (params: any) {
              const value = params[0].value
              return `${params[0].axisValue}<br/>成交量: ${(value / 10000).toFixed(2)}万手`
            }
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
            axisLine: { show: false },
            axisTick: { show: false },
            axisLabel: { show: false }
          },
          yAxis: {
            type: 'value',
            axisLabel: {
              formatter: function (value: number) {
                return (value / 10000).toFixed(0) + '万'
              }
            }
          },
          series: [
            {
              type: 'bar',
              data: volumes.map((volume, index) => ({
                value: volume,
                itemStyle: {
                  color: volumeColors[index]
                }
              })),
              barWidth: '60%'
            }
          ]
        }
        break

      case 'rsi':
        // RSI指标
        const calculateRSI = (period = 14) => {
          const rsi = []
          for (let i = 0; i < data.length; i++) {
            if (i < period) {
              rsi.push(null)
            } else {
              let gains = 0
              let losses = 0

              for (let j = 1; j <= period; j++) {
                const change = data[i - j + 1].close - data[i - j].close
                if (change > 0) gains += change
                else losses -= change
              }

              const avgGain = gains / period
              const avgLoss = losses / period
              const rs = avgGain / avgLoss
              const rsiValue = 100 - (100 / (1 + rs))

              rsi.push(rsiValue.toFixed(2))
            }
          }
          return rsi
        }

        const rsiData = calculateRSI()

        option = {
          title: {
            text: 'RSI指标',
            left: 0,
            textStyle: {
              fontSize: 14,
              fontWeight: 'normal'
            }
          },
          tooltip: {
            trigger: 'axis',
            formatter: function (params: any) {
              return `${params[0].axisValue}<br/>RSI: ${params[0].value || '--'}`
            }
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
            axisLine: { show: false },
            axisTick: { show: false },
            axisLabel: { show: false }
          },
          yAxis: {
            type: 'value',
            min: 0,
            max: 100,
            axisLabel: {
              formatter: '{value}'
            }
          },
          series: [
            {
              name: 'RSI',
              type: 'line',
              data: rsiData,
              lineStyle: {
                color: '#1890ff',
                width: 2
              },
              itemStyle: {
                color: '#1890ff'
              },
              markLine: {
                silent: true,
                data: [
                  { yAxis: 70, lineStyle: { color: '#f5222d', type: 'dashed' } },
                  { yAxis: 30, lineStyle: { color: '#52c41a', type: 'dashed' } }
                ]
              }
            }
          ]
        }
        break

      case 'macd':
        // MACD指标
        const calculateMACD = () => {
          const ema12 = []
          const ema26 = []
          const dif = []
          const dea = []
          const macd = []

          // 计算EMA12和EMA26
          for (let i = 0; i < data.length; i++) {
            const close = data[i].close

            if (i === 0) {
              ema12.push(close)
              ema26.push(close)
            } else {
              ema12.push((close * 2 + ema12[i - 1] * 11) / 13)
              ema26.push((close * 2 + ema26[i - 1] * 25) / 27)
            }

            // DIF = EMA12 - EMA26
            dif.push(ema12[i] - ema26[i])

            // DEA = EMA(DIF, 9)
            if (i === 0) {
              dea.push(dif[i])
            } else {
              dea.push((dif[i] * 2 + dea[i - 1] * 8) / 10)
            }

            // MACD = (DIF - DEA) * 2
            macd.push((dif[i] - dea[i]) * 2)
          }

          return { dif, dea, macd }
        }

        const { dif, dea, macd } = calculateMACD()

        option = {
          title: {
            text: 'MACD指标',
            left: 0,
            textStyle: {
              fontSize: 14,
              fontWeight: 'normal'
            }
          },
          tooltip: {
            trigger: 'axis',
            formatter: function (params: any) {
              let result = `${params[0].axisValue}<br/>`
              params.forEach((param: any) => {
                result += `${param.seriesName}: ${param.value?.toFixed(4) || '--'}<br/>`
              })
              return result
            }
          },
          legend: {
            data: ['DIF', 'DEA', 'MACD'],
            top: 25,
            textStyle: {
              fontSize: 12
            }
          },
          grid: {
            left: '10%',
            right: '10%',
            bottom: '15%',
            top: '20%'
          },
          xAxis: {
            type: 'category',
            data: dates,
            axisLine: { show: false },
            axisTick: { show: false },
            axisLabel: { show: false }
          },
          yAxis: {
            type: 'value'
          },
          series: [
            {
              name: 'DIF',
              type: 'line',
              data: dif.map(v => v.toFixed(4)),
              lineStyle: { color: '#1890ff', width: 1 },
              itemStyle: { color: '#1890ff' }
            },
            {
              name: 'DEA',
              type: 'line',
              data: dea.map(v => v.toFixed(4)),
              lineStyle: { color: '#fa8c16', width: 1 },
              itemStyle: { color: '#fa8c16' }
            },
            {
              name: 'MACD',
              type: 'bar',
              data: macd.map((value, index) => ({
                value: value.toFixed(4),
                itemStyle: {
                  color: value >= 0 ? '#f5222d' : '#52c41a'
                }
              })),
              barWidth: '60%'
            }
          ]
        }
        break

      default:
        option = {}
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
  }, [data, type])

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

export default TechnicalIndicators
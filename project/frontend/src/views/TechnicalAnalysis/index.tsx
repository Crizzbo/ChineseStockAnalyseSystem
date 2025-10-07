import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Select, Spin, Typography, Tabs, Space, Tag, Button, message } from 'antd'
import { LineChartOutlined, BarChartOutlined, TrendingUpOutlined, InfoCircleOutlined } from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import StockChart from '@components/charts/StockChart'
import TechnicalIndicators from '@components/charts/TechnicalIndicators'
import { stockService } from '@services/stock'
import './TechnicalAnalysis.scss'

const { Title, Text } = Typography
const { Option } = Select
const { TabPane } = Tabs

interface StockData {
  symbol: string
  name: string
  currentPrice: number
  change: number
  changePercent: number
  volume: number
  high: number
  low: number
  open: number
  preClose: number
}

interface TechnicalData {
  ma5: number
  ma10: number
  ma20: number
  ma60: number
  rsi: number
  volume_ratio: number
}

const TechnicalAnalysis: React.FC = () => {
  const { symbol: urlSymbol } = useParams<{ symbol: string }>()
  const navigate = useNavigate()
  const [selectedStock, setSelectedStock] = useState<string>(urlSymbol || '000001')
  const [stockData, setStockData] = useState<StockData | null>(null)
  const [technicalData, setTechnicalData] = useState<TechnicalData | null>(null)
  const [priceHistory, setPriceHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [chartType, setChartType] = useState<'line' | 'candlestick'>('candlestick')

  // 加载股票数据
  const loadStockData = async (symbol: string) => {
    setLoading(true)
    try {
      // 并行加载多个数据
      const [basicInfo, technical, history] = await Promise.all([
        stockService.getStockInfo(symbol),
        stockService.getTechnicalIndicators(symbol),
        stockService.getStockHistory(symbol, 'daily', 100)
      ])

      setStockData(basicInfo)
      setTechnicalData(technical)
      setPriceHistory(history)
    } catch (error) {
      console.error('加载股票数据失败:', error)
      message.error('加载股票数据失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (selectedStock) {
      loadStockData(selectedStock)
    }
  }, [selectedStock])

  // 股票选择器
  const [stockOptions, setStockOptions] = useState([
    { value: '000001', label: '000001 平安银行' },
    { value: '000002', label: '000002 万科A' },
    { value: '000858', label: '000858 五粮液' },
    { value: '600519', label: '600519 贵州茅台' },
    { value: '000651', label: '000651 格力电器' },
    { value: '601318', label: '601318 中国平安' },
    { value: '600036', label: '600036 招商银行' },
    { value: '002415', label: '002415 海康威视' },
    { value: '300750', label: '300750 宁德时代' },
    { value: '002594', label: '002594 比亚迪' }
  ])

  const handleStockChange = (value: string) => {
    setSelectedStock(value)
    navigate(`/analysis/technical/${value}`)
  }

  const renderStockBasicInfo = () => {
    if (!stockData) return null

    const isPositive = stockData.change >= 0

    return (
      <Card title="股票基本信息" size="small">
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Space size="large">
              <div>
                <Text strong style={{ fontSize: 18 }}>{stockData.name}</Text>
                <br />
                <Text type="secondary">{stockData.symbol}</Text>
              </div>
              <div>
                <Text strong style={{ fontSize: 24, color: isPositive ? '#f5222d' : '#52c41a' }}>
                  ¥{stockData.currentPrice.toFixed(2)}
                </Text>
                <br />
                <Text style={{ color: isPositive ? '#f5222d' : '#52c41a' }}>
                  {isPositive ? '+' : ''}{stockData.change.toFixed(2)} ({isPositive ? '+' : ''}{stockData.changePercent.toFixed(2)}%)
                </Text>
              </div>
            </Space>
          </Col>
          <Col span={6}>
            <Text type="secondary">开盘</Text>
            <br />
            <Text strong>¥{stockData.open.toFixed(2)}</Text>
          </Col>
          <Col span={6}>
            <Text type="secondary">最高</Text>
            <br />
            <Text strong>¥{stockData.high.toFixed(2)}</Text>
          </Col>
          <Col span={6}>
            <Text type="secondary">最低</Text>
            <br />
            <Text strong>¥{stockData.low.toFixed(2)}</Text>
          </Col>
          <Col span={6}>
            <Text type="secondary">昨收</Text>
            <br />
            <Text strong>¥{stockData.preClose.toFixed(2)}</Text>
          </Col>
        </Row>
      </Card>
    )
  }

  const renderTechnicalIndicators = () => {
    if (!technicalData) return null

    return (
      <Card title="技术指标" size="small">
        <Row gutter={[16, 16]}>
          <Col span={6}>
            <div className="indicator-item">
              <Text type="secondary">MA5</Text>
              <br />
              <Text strong>¥{technicalData.ma5?.toFixed(2) || '--'}</Text>
            </div>
          </Col>
          <Col span={6}>
            <div className="indicator-item">
              <Text type="secondary">MA10</Text>
              <br />
              <Text strong>¥{technicalData.ma10?.toFixed(2) || '--'}</Text>
            </div>
          </Col>
          <Col span={6}>
            <div className="indicator-item">
              <Text type="secondary">MA20</Text>
              <br />
              <Text strong>¥{technicalData.ma20?.toFixed(2) || '--'}</Text>
            </div>
          </Col>
          <Col span={6}>
            <div className="indicator-item">
              <Text type="secondary">MA60</Text>
              <br />
              <Text strong>¥{technicalData.ma60?.toFixed(2) || '--'}</Text>
            </div>
          </Col>
          <Col span={6}>
            <div className="indicator-item">
              <Text type="secondary">RSI</Text>
              <br />
              <Text strong style={{
                color: technicalData.rsi > 70 ? '#f5222d' : technicalData.rsi < 30 ? '#52c41a' : '#1890ff'
              }}>
                {technicalData.rsi?.toFixed(2) || '--'}
              </Text>
            </div>
          </Col>
          <Col span={6}>
            <div className="indicator-item">
              <Text type="secondary">量比</Text>
              <br />
              <Text strong style={{
                color: technicalData.volume_ratio > 2 ? '#f5222d' : '#1890ff'
              }}>
                {technicalData.volume_ratio?.toFixed(2) || '--'}
              </Text>
            </div>
          </Col>
        </Row>
      </Card>
    )
  }

  return (
    <div className="technical-analysis">
      <div className="page-header">
        <Title level={2}>
          <TrendingUpOutlined style={{ marginRight: 12 }} />
          技术分析
        </Title>
        <Space>
          <Select
            style={{ width: 300 }}
            placeholder="选择股票"
            value={selectedStock}
            onChange={handleStockChange}
            showSearch
            filterOption={(input, option) =>
              option?.label?.toLowerCase().includes(input.toLowerCase()) ?? false
            }
            options={stockOptions}
          />
          <Select
            style={{ width: 120 }}
            value={chartType}
            onChange={setChartType}
          >
            <Option value="line">线图</Option>
            <Option value="candlestick">K线图</Option>
          </Select>
        </Space>
      </div>

      <Spin spinning={loading}>
        <Row gutter={[24, 24]}>
          {/* 股票基本信息 */}
          <Col span={24}>
            {renderStockBasicInfo()}
          </Col>

          {/* 技术指标 */}
          <Col span={24}>
            {renderTechnicalIndicators()}
          </Col>

          {/* 主图表 */}
          <Col span={24}>
            <Card
              title={
                <Space>
                  <LineChartOutlined />
                  <span>价格走势图</span>
                </Space>
              }
              extra={
                <Space>
                  <Button size="small" onClick={() => loadStockData(selectedStock)}>
                    刷新
                  </Button>
                </Space>
              }
            >
              <StockChart
                data={priceHistory}
                type={chartType}
                height={400}
                symbol={selectedStock}
              />
            </Card>
          </Col>

          {/* 技术指标图表 */}
          <Col span={24}>
            <Tabs defaultActiveKey="volume">
              <TabPane
                tab={
                  <span>
                    <BarChartOutlined />
                    成交量
                  </span>
                }
                key="volume"
              >
                <TechnicalIndicators
                  data={priceHistory}
                  type="volume"
                  height={200}
                />
              </TabPane>
              <TabPane
                tab={
                  <span>
                    <LineChartOutlined />
                    RSI
                  </span>
                }
                key="rsi"
              >
                <TechnicalIndicators
                  data={priceHistory}
                  type="rsi"
                  height={200}
                />
              </TabPane>
              <TabPane
                tab={
                  <span>
                    <TrendingUpOutlined />
                    MACD
                  </span>
                }
                key="macd"
              >
                <TechnicalIndicators
                  data={priceHistory}
                  type="macd"
                  height={200}
                />
              </TabPane>
            </Tabs>
          </Col>

          {/* 分析建议 */}
          <Col span={24}>
            <Card
              title={
                <Space>
                  <InfoCircleOutlined />
                  <span>技术分析建议</span>
                </Space>
              }
              size="small"
            >
              {technicalData && (
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text strong>趋势分析：</Text>
                    <Space wrap style={{ marginLeft: 8 }}>
                      {technicalData.ma5 > technicalData.ma10 && (
                        <Tag color="red">短期上涨趋势</Tag>
                      )}
                      {technicalData.ma5 < technicalData.ma10 && (
                        <Tag color="green">短期下跌趋势</Tag>
                      )}
                      {technicalData.ma20 > technicalData.ma60 && (
                        <Tag color="red">中长期上涨趋势</Tag>
                      )}
                      {technicalData.ma20 < technicalData.ma60 && (
                        <Tag color="green">中长期下跌趋势</Tag>
                      )}
                    </Space>
                  </div>

                  <div>
                    <Text strong>超买超卖：</Text>
                    <Space wrap style={{ marginLeft: 8 }}>
                      {technicalData.rsi > 70 && (
                        <Tag color="red">RSI超买区域</Tag>
                      )}
                      {technicalData.rsi < 30 && (
                        <Tag color="green">RSI超卖区域</Tag>
                      )}
                      {technicalData.rsi >= 30 && technicalData.rsi <= 70 && (
                        <Tag color="blue">RSI正常区域</Tag>
                      )}
                    </Space>
                  </div>

                  <div>
                    <Text strong>成交量：</Text>
                    <Space wrap style={{ marginLeft: 8 }}>
                      {technicalData.volume_ratio > 2 && (
                        <Tag color="red">成交量放大</Tag>
                      )}
                      {technicalData.volume_ratio < 0.5 && (
                        <Tag color="green">成交量萎缩</Tag>
                      )}
                      {technicalData.volume_ratio >= 0.5 && technicalData.volume_ratio <= 2 && (
                        <Tag color="blue">成交量正常</Tag>
                      )}
                    </Space>
                  </div>
                </Space>
              )}
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  )
}

export default TechnicalAnalysis
import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Typography, Tabs, Space, Tag, Statistic, Alert, Spin } from 'antd'
import { useParams, useNavigate } from 'react-router-dom'
import { RiseOutlined, FallOutlined, DollarOutlined, BarChartOutlined } from '@ant-design/icons'
import StockSearch from '@components/business/StockSearch'
import StockChart from '@components/business/StockChart'
import type { StockInfo } from '@store/modules/stocks'
import type { StockPriceData } from '@components/business/StockChart'
import { stocksService } from '@services/stocks'
import { analysisService } from '@services/analysis'
import './StockAnalysis.scss'

const { Title, Text } = Typography

interface StockDetail extends StockInfo {
  open: number
  high: number
  low: number
  previousClose: number
  turnoverRate: number
  totalShares: number
  floatingShares: number
}

const StockAnalysis: React.FC = () => {
  const { symbol } = useParams<{ symbol: string }>()
  const navigate = useNavigate()

  const [currentStock, setCurrentStock] = useState<StockDetail | null>(null)
  const [priceData, setPriceData] = useState<StockPriceData[]>([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')
  const [analysisData, setAnalysisData] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (symbol) {
      loadStockData(symbol)
    }
  }, [symbol])

  const loadStockData = async (stockSymbol: string) => {
    setLoading(true)
    setError(null)
    try {
      // 并行获取股票基本信息和历史数据
      const [stockInfo, historyData] = await Promise.all([
        stocksService.getStockInfo(stockSymbol),
        stocksService.getStockHistory(stockSymbol, { period: 'daily', limit: 60 })
      ])

      if (stockInfo.stock) {
        // 构建详细股票信息
        const stockDetail: StockDetail = {
          ...stockInfo.stock,
          open: stockInfo.stock.open || stockInfo.stock.currentPrice,
          high: stockInfo.stock.high || stockInfo.stock.currentPrice,
          low: stockInfo.stock.low || stockInfo.stock.currentPrice,
          previousClose: stockInfo.stock.preClose || stockInfo.stock.currentPrice,
          turnoverRate: stockInfo.stock.turnover ?
            (stockInfo.stock.turnover / (stockInfo.stock.currentPrice * stockInfo.stock.volume)) * 100 : 0.85,
          totalShares: stockInfo.stock.marketCap ?
            Math.floor(stockInfo.stock.marketCap / stockInfo.stock.currentPrice) : 0,
          floatingShares: stockInfo.stock.marketCap ?
            Math.floor(stockInfo.stock.marketCap / stockInfo.stock.currentPrice) : 0
        }

        setCurrentStock(stockDetail)
      } else {
        setError('未找到股票信息')
      }

      if (historyData.data && historyData.data.length > 0) {
        setPriceData(historyData.data)
      } else {
        setError('暂无历史数据')
      }

      // 获取分析数据（在后台加载，不影响基本信息显示）
      try {
        const analysis = await analysisService.getComprehensiveAnalysis(stockSymbol)

        // 生成投资建议
        const recommendation = analysisService.generateInvestmentAdvice(analysis)

        setAnalysisData({
          ...analysis,
          recommendation
        })
      } catch (analysisError) {
        console.error('获取分析数据失败:', analysisError)
        // 分析数据获取失败不影响基本信息显示
      }

    } catch (error) {
      console.error('加载股票数据失败:', error)
      setError('加载股票数据失败，请检查股票代码')
    } finally {
      setLoading(false)
    }
  }

  const handleStockSelect = (stock: StockInfo) => {
    navigate(`/analysis/${stock.symbol}`)
  }

  const formatNumber = (num: number, unit?: string) => {
    if (num >= 100000000) {
      return `${(num / 100000000).toFixed(2)}${unit ? unit : ''}亿`
    } else if (num >= 10000) {
      return `${(num / 10000).toFixed(2)}${unit ? unit : ''}万`
    }
    return num.toLocaleString()
  }

  const getChangeColor = (change: number) => change >= 0 ? '#ff4d4f' : '#52c41a'
  const getChangeIcon = (change: number) => change >= 0 ? <RiseOutlined /> : <FallOutlined />

  const tabItems = [
    {
      key: 'overview',
      label: '股票概览',
      children: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="价格走势">
              <StockChart
                title={currentStock ? `${currentStock.name} (${currentStock.symbol})` : '股票走势'}
                data={priceData}
                height={500}
              />
            </Card>
          </Col>
        </Row>
      )
    },
    {
      key: 'fundamental',
      label: '基本面分析',
      children: (
        <Row gutter={[16, 16]}>
          <Col span={24} lg={12}>
            <Card title="估值指标">
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic
                    title="市盈率(PE)"
                    value={currentStock?.pe || 0}
                    precision={2}
                    valueStyle={{ color: '#1890ff' }}
                    prefix={<BarChartOutlined />}
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="市净率(PB)"
                    value={currentStock?.pb || 0}
                    precision={2}
                    valueStyle={{ color: '#52c41a' }}
                    prefix={<BarChartOutlined />}
                  />
                </Col>
              </Row>
            </Card>
          </Col>
          <Col span={24} lg={12}>
            <Card title="市值信息">
              <Row gutter={16}>
                <Col span={24}>
                  <Statistic
                    title="总市值"
                    value={currentStock?.marketCap || 0}
                    formatter={(value) => formatNumber(Number(value))}
                    valueStyle={{ color: '#722ed1' }}
                    prefix={<DollarOutlined />}
                  />
                </Col>
              </Row>
            </Card>
          </Col>
          {analysisData?.fundamental && (
            <Col span={24}>
              <Card title="基本面评估">
                <Row gutter={[16, 16]}>
                  <Col span={24} lg={16}>
                    <div style={{ marginBottom: 16 }}>
                      <Text strong>估值水平：</Text>
                      <Tag
                        color={
                          analysisData.fundamental.analysis.valuation === 'undervalued' ? 'green' :
                          analysisData.fundamental.analysis.valuation === 'fair' ? 'blue' : 'red'
                        }
                        style={{ marginLeft: 8 }}
                      >
                        {
                          analysisData.fundamental.analysis.valuation === 'undervalued' ? '低估' :
                          analysisData.fundamental.analysis.valuation === 'fair' ? '合理' : '高估'
                        }
                      </Tag>
                    </div>
                    <div style={{ marginBottom: 16 }}>
                      <Text strong>基本面评分：</Text>
                      <span style={{
                        fontWeight: 'bold',
                        marginLeft: 8,
                        color: analysisData.fundamental.analysis.score >= 5 ? '#52c41a' :
                               analysisData.fundamental.analysis.score <= -5 ? '#ff4d4f' : '#1890ff'
                      }}>
                        {analysisData.fundamental.analysis.score}
                      </span>
                    </div>
                    <div>
                      <Text strong>分析要点：</Text>
                      {analysisData.fundamental.analysis.analysis_points.map((point: string, index: number) => (
                        <div key={index} style={{ marginTop: 8 }}>
                          <Text>• {point}</Text>
                        </div>
                      ))}
                    </div>
                  </Col>
                  <Col span={24} lg={8}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      {analysisData.fundamental.analysis.metrics.pe_ratio && (
                        <Statistic
                          title="市盈率(PE)"
                          value={analysisData.fundamental.analysis.metrics.pe_ratio}
                          precision={2}
                          valueStyle={{ fontSize: 14 }}
                        />
                      )}
                      {analysisData.fundamental.analysis.metrics.pb_ratio && (
                        <Statistic
                          title="市净率(PB)"
                          value={analysisData.fundamental.analysis.metrics.pb_ratio}
                          precision={2}
                          valueStyle={{ fontSize: 14 }}
                        />
                      )}
                      {analysisData.fundamental.analysis.metrics.market_cap && (
                        <Statistic
                          title="总市值"
                          value={analysisData.fundamental.analysis.metrics.market_cap}
                          formatter={(value) => formatNumber(Number(value))}
                          valueStyle={{ fontSize: 14 }}
                        />
                      )}
                    </Space>
                  </Col>
                </Row>
              </Card>
            </Col>
          )}
        </Row>
      )
    },
    {
      key: 'technical',
      label: '技术分析',
      children: (
        <Row gutter={[16, 16]}>
          {analysisData ? (
            <>
              <Col span={24} lg={12}>
                <Card title="技术指标">
                  <Row gutter={16}>
                    <Col span={12}>
                      <Statistic
                        title="RSI"
                        value={analysisData.technical?.technical_indicators?.rsi || 0}
                        precision={2}
                        valueStyle={{
                          color: analysisData.technical?.technical_indicators?.rsi > 70 ? '#ff4d4f' :
                                 analysisData.technical?.technical_indicators?.rsi < 30 ? '#52c41a' : '#1890ff'
                        }}
                        prefix={<BarChartOutlined />}
                      />
                    </Col>
                    <Col span={12}>
                      <Statistic
                        title="成交量比率"
                        value={analysisData.technical?.technical_indicators?.volume_ratio || 0}
                        precision={2}
                        valueStyle={{ color: '#722ed1' }}
                        prefix={<BarChartOutlined />}
                      />
                    </Col>
                  </Row>
                  <div style={{ marginTop: 16 }}>
                    <Row gutter={16}>
                      <Col span={6}>
                        <Statistic
                          title="MA5"
                          value={analysisData.technical?.technical_indicators?.ma5 || 0}
                          precision={2}
                          valueStyle={{ fontSize: 14 }}
                        />
                      </Col>
                      <Col span={6}>
                        <Statistic
                          title="MA20"
                          value={analysisData.technical?.technical_indicators?.ma20 || 0}
                          precision={2}
                          valueStyle={{ fontSize: 14 }}
                        />
                      </Col>
                      <Col span={6}>
                        <Statistic
                          title="MA60"
                          value={analysisData.technical?.technical_indicators?.ma60 || 0}
                          precision={2}
                          valueStyle={{ fontSize: 14 }}
                        />
                      </Col>
                      <Col span={6}>
                        <Statistic
                          title="MA10"
                          value={analysisData.technical?.technical_indicators?.ma10 || 0}
                          precision={2}
                          valueStyle={{ fontSize: 14 }}
                        />
                      </Col>
                    </Row>
                  </div>
                </Card>
              </Col>
              <Col span={24} lg={12}>
                <Card title="技术信号">
                  <div style={{ marginBottom: 16 }}>
                    <Text strong>综合评价：</Text>
                    <Tag
                      color={analysisData.technical?.analysis?.overall === 'bullish' ? 'error' :
                             analysisData.technical?.analysis?.overall === 'bearish' ? 'success' : 'default'}
                      style={{ marginLeft: 8 }}
                    >
                      {analysisData.technical?.analysis?.overall === 'bullish' ? '偏强' :
                       analysisData.technical?.analysis?.overall === 'bearish' ? '偏弱' : '中性'}
                    </Tag>
                  </div>
                  {analysisData.technical?.analysis?.signals?.map((signal: string, index: number) => (
                    <div key={index} style={{ marginBottom: 8 }}>
                      <Text>• {signal}</Text>
                    </div>
                  ))}
                  {analysisData.technical?.analysis?.recommendations?.length > 0 && (
                    <div style={{ marginTop: 16, padding: 12, backgroundColor: '#f6f8fa', borderRadius: 6 }}>
                      <Text strong>投资建议：</Text>
                      {analysisData.technical?.analysis?.recommendations?.map((rec: string, index: number) => (
                        <div key={index} style={{ marginTop: 4 }}>
                          <Text type="secondary">• {rec}</Text>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              </Col>
            </>
          ) : (
            <Col span={24}>
              <Alert
                message="技术分析"
                description="请先选择股票以查看技术分析数据"
                type="info"
                showIcon
              />
            </Col>
          )}
        </Row>
      )
    },
    {
      key: 'investment',
      label: '投资建议',
      children: (
        analysisData ? (
          <Row gutter={[16, 16]}>
            <Col span={24} lg={16}>
              <Card title="综合分析">
                <div style={{ marginBottom: 16 }}>
                  <Text strong>综合评分：</Text>
                  <span style={{
                    fontSize: 20,
                    fontWeight: 'bold',
                    marginLeft: 8,
                    color: analysisData.recommendation?.overall_score >= 10 ? '#52c41a' :
                           analysisData.recommendation?.overall_score <= -10 ? '#ff4d4f' : '#1890ff'
                  }}>
                    {analysisData.recommendation?.overall_score || 0}
                  </span>
                </div>

                <div style={{ marginBottom: 16 }}>
                  <Text strong>投资建议：</Text>
                  <Tag
                    color={
                      analysisData.recommendation?.recommendation === 'strong_buy' ? 'error' :
                      analysisData.recommendation?.recommendation === 'buy' ? 'orange' :
                      analysisData.recommendation?.recommendation === 'hold' ? 'blue' :
                      analysisData.recommendation?.recommendation === 'sell' ? 'purple' : 'red'
                    }
                    style={{ marginLeft: 8, fontSize: 14, padding: '4px 8px' }}
                  >
                    {
                      analysisData.recommendation?.recommendation === 'strong_buy' ? '强烈买入' :
                      analysisData.recommendation?.recommendation === 'buy' ? '买入' :
                      analysisData.recommendation?.recommendation === 'hold' ? '持有' :
                      analysisData.recommendation?.recommendation === 'sell' ? '卖出' : '强烈卖出'
                    }
                  </Tag>
                </div>

                <div style={{ marginBottom: 16 }}>
                  <Text strong>风险等级：</Text>
                  <Tag
                    color={
                      analysisData.recommendation?.risk_level === 'low' ? 'green' :
                      analysisData.recommendation?.risk_level === 'medium' ? 'blue' : 'red'
                    }
                    style={{ marginLeft: 8 }}
                  >
                    {
                      analysisData.recommendation?.risk_level === 'low' ? '低风险' :
                      analysisData.recommendation?.risk_level === 'medium' ? '中等风险' : '高风险'
                    }
                  </Tag>
                </div>

                <div style={{ marginBottom: 16 }}>
                  <Text strong>置信度：</Text>
                  <span style={{ marginLeft: 8, fontWeight: 'bold' }}>
                    {Math.round((analysisData.recommendation?.confidence || 0) * 100)}%
                  </span>
                </div>

                <div style={{ backgroundColor: '#f6f8fa', padding: 16, borderRadius: 6 }}>
                  <Text strong>分析摘要：</Text>
                  {analysisData.recommendation?.summary?.map((point: string, index: number) => (
                    <div key={index} style={{ marginTop: 8 }}>
                      <Text>• {point}</Text>
                    </div>
                  ))}
                </div>
              </Card>
            </Col>

            <Col span={24} lg={8}>
              <Card title="风险分析">
                {analysisData.risk?.risk_metrics && (
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Statistic
                      title="年化波动率"
                      value={analysisData.risk.risk_metrics.volatility}
                      precision={2}
                      suffix="%"
                      valueStyle={{ fontSize: 14 }}
                    />
                    <Statistic
                      title="最大回撤"
                      value={analysisData.risk.risk_metrics.max_drawdown}
                      precision={2}
                      suffix="%"
                      valueStyle={{ fontSize: 14, color: '#ff4d4f' }}
                    />
                    <Statistic
                      title="夏普比率"
                      value={analysisData.risk.risk_metrics.sharpe_ratio}
                      precision={2}
                      valueStyle={{ fontSize: 14 }}
                    />
                    <Statistic
                      title="VaR (95%)"
                      value={analysisData.risk.risk_metrics.var_95}
                      precision={2}
                      suffix="%"
                      valueStyle={{ fontSize: 14 }}
                    />
                  </Space>
                )}
              </Card>
            </Col>
          </Row>
        ) : (
          <Alert
            message="投资建议"
            description="请先选择股票以查看投资建议"
            type="info"
            showIcon
          />
        )
      )
    }
  ]

  return (
    <div className="stock-analysis">
      <div className="page-header">
        <Title level={2}>股票分析</Title>
        <div className="search-container">
          <StockSearch
            onSelect={handleStockSelect}
            placeholder="搜索股票进行分析..."
          />
        </div>
      </div>

      {loading ? (
        <div className="loading-container">
          <Spin size="large" />
          <Text style={{ marginTop: 16, display: 'block', textAlign: 'center' }}>
            加载股票数据中...
          </Text>
        </div>
      ) : currentStock ? (
        <>
          {/* 股票基本信息 */}
          <Card className="stock-info-card">
            <Row gutter={24} align="middle">
              <Col flex="1">
                <Space direction="vertical" size="small">
                  <div>
                    <Text strong style={{ fontSize: 18 }}>{currentStock.name}</Text>
                    <Text type="secondary" style={{ marginLeft: 12 }}>
                      {currentStock.symbol}
                    </Text>
                  </div>
                  <Space size="large">
                    <div>
                      <Text type="secondary">当前价格</Text>
                      <div>
                        <Text style={{ fontSize: 24, fontWeight: 'bold', fontFamily: 'monospace' }}>
                          ¥{currentStock.currentPrice.toFixed(2)}
                        </Text>
                      </div>
                    </div>
                    <div>
                      <Text type="secondary">涨跌额/涨跌幅</Text>
                      <div>
                        <Tag
                          color={currentStock.change >= 0 ? 'error' : 'success'}
                          icon={getChangeIcon(currentStock.change)}
                          style={{ fontSize: 14, padding: '4px 8px' }}
                        >
                          {currentStock.change >= 0 ? '+' : ''}{currentStock.change.toFixed(2)} (
                          {currentStock.change >= 0 ? '+' : ''}{currentStock.changePercent.toFixed(2)}%)
                        </Tag>
                      </div>
                    </div>
                  </Space>
                </Space>
              </Col>
              <Col>
                <Row gutter={24}>
                  <Col>
                    <Statistic
                      title="今开"
                      value={currentStock.open}
                      precision={2}
                      valueStyle={{ fontSize: 14 }}
                    />
                  </Col>
                  <Col>
                    <Statistic
                      title="最高"
                      value={currentStock.high}
                      precision={2}
                      valueStyle={{ fontSize: 14, color: '#ff4d4f' }}
                    />
                  </Col>
                  <Col>
                    <Statistic
                      title="最低"
                      value={currentStock.low}
                      precision={2}
                      valueStyle={{ fontSize: 14, color: '#52c41a' }}
                    />
                  </Col>
                  <Col>
                    <Statistic
                      title="成交量"
                      value={currentStock.volume}
                      formatter={(value) => formatNumber(Number(value))}
                      valueStyle={{ fontSize: 14 }}
                    />
                  </Col>
                  <Col>
                    <Statistic
                      title="换手率"
                      value={currentStock.turnoverRate}
                      precision={2}
                      suffix="%"
                      valueStyle={{ fontSize: 14 }}
                    />
                  </Col>
                </Row>
              </Col>
            </Row>
          </Card>

          {/* 详细分析标签页 */}
          <Card>
            <Tabs
              activeKey={activeTab}
              onChange={setActiveTab}
              items={tabItems}
              size="large"
            />
          </Card>
        </>
      ) : (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Text type="secondary" style={{ fontSize: 16 }}>
              请搜索并选择股票进行分析
            </Text>
          </div>
        </Card>
      )}
    </div>
  )
}

export default StockAnalysis
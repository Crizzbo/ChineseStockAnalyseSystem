import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Typography, Alert, List, Tag, Statistic, Space, Spin, Button } from 'antd'
import { RiseOutlined, FallOutlined, ReloadOutlined, ArrowUpOutlined, ArrowDownOutlined, MinusOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import UserInfo from '@components/UserInfo'
import { marketService, type MarketOverview } from '@services/market'
import type { MarketIndex } from '@services/api'

const { Title, Text } = Typography

interface DashboardData {
  marketOverview?: MarketOverview
  loading: boolean
  error: string | null
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const [data, setData] = useState<DashboardData>({
    loading: true,
    error: null
  })

  const loadDashboardData = async () => {
    setData(prev => ({ ...prev, loading: true, error: null }))

    try {
      // 获取市场概览数据
      const marketOverview = await marketService.getMarketOverview()

      setData({
        marketOverview,
        loading: false,
        error: null
      })
    } catch (error) {
      console.error('加载仪表盘数据失败:', error)
      setData(prev => ({
        ...prev,
        loading: false,
        error: '加载数据失败，请稍后重试'
      }))
    }
  }

  useEffect(() => {
    loadDashboardData()
  }, [])

  const getChangeColor = (change: number) => change >= 0 ? '#ff4d4f' : '#52c41a'
  const getChangeIcon = (change: number) => {
    if (change > 0) return <RiseOutlined />
    if (change < 0) return <FallOutlined />
    return <MinusOutlined />
  }

  const formatNumber = (num: number) => {
    if (num >= 100000000) {
      return `${(num / 100000000).toFixed(2)}亿`
    } else if (num >= 10000) {
      return `${(num / 10000).toFixed(2)}万`
    }
    return num.toLocaleString()
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <Title level={2}>仪表盘</Title>
        <Button
          icon={<ReloadOutlined />}
          onClick={loadDashboardData}
          loading={data.loading}
        >
          刷新数据
        </Button>
      </div>

      <Alert
        message="模拟登录系统已启用"
        description="当前使用模拟认证系统，测试账号请查看浏览器控制台。"
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Row gutter={[16, 16]}>
        <Col span={24} lg={8}>
          <UserInfo />
        </Col>

        <Col span={24} md={12} lg={8}>
          <Card
            title="市场概览"
            loading={data.loading}
            extra={data.marketOverview && (
              <Text type="secondary" style={{ fontSize: 12 }}>
                更新时间: {new Date(data.marketOverview.market_stats.update_time).toLocaleTimeString()}
              </Text>
            )}
          >
            {data.error ? (
              <Alert message={data.error} type="error" showIcon />
            ) : data.marketOverview ? (
              <div>
                {/* 市场统计 */}
                <Row gutter={16} style={{ marginBottom: 16 }}>
                  <Col span={8}>
                    <div style={{ textAlign: 'center' }}>
                      <ArrowUpOutlined style={{ color: '#ff4d4f', fontSize: 16 }} />
                      <div style={{ color: '#ff4d4f', fontSize: 14, fontWeight: 'bold' }}>
                        {data.marketOverview.market_stats.indices_rising || 0}
                      </div>
                      <Text type="secondary" style={{ fontSize: 12 }}>上涨</Text>
                    </div>
                  </Col>
                  <Col span={8}>
                    <div style={{ textAlign: 'center' }}>
                      <ArrowDownOutlined style={{ color: '#52c41a', fontSize: 16 }} />
                      <div style={{ color: '#52c41a', fontSize: 14, fontWeight: 'bold' }}>
                        {data.marketOverview.market_stats.indices_falling || 0}
                      </div>
                      <Text type="secondary" style={{ fontSize: 12 }}>下跌</Text>
                    </div>
                  </Col>
                  <Col span={8}>
                    <div style={{ textAlign: 'center' }}>
                      <MinusOutlined style={{ color: '#8c8c8c', fontSize: 16 }} />
                      <div style={{ color: '#8c8c8c', fontSize: 14, fontWeight: 'bold' }}>
                        {data.marketOverview.market_stats.indices_unchanged || 0}
                      </div>
                      <Text type="secondary" style={{ fontSize: 12 }}>平盘</Text>
                    </div>
                  </Col>
                </Row>

                {/* 主要指数 */}
                <List
                  size="small"
                  dataSource={data.marketOverview.indices.slice(0, 3)}
                  renderItem={(index: MarketIndex) => (
                    <List.Item style={{ padding: '8px 0' }}>
                      <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between' }}>
                        <div>
                          <Text strong style={{ fontSize: 12 }}>{index.name}</Text>
                          <br />
                          <Text style={{ fontSize: 12 }}>{index.currentPrice?.toFixed(2)}</Text>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <Tag
                            color={index.changePercent >= 0 ? 'error' : 'success'}
                            style={{ fontSize: 10, margin: 0 }}
                          >
                            {getChangeIcon(index.changePercent)}
                            {index.changePercent >= 0 ? '+' : ''}{index.changePercent?.toFixed(2)}%
                          </Tag>
                        </div>
                      </div>
                    </List.Item>
                  )}
                />

                <div style={{ textAlign: 'center', marginTop: 12 }}>
                  <Button
                    type="link"
                    size="small"
                    onClick={() => navigate('/sectors')}
                  >
                    查看更多 →
                  </Button>
                </div>
              </div>
            ) : null}
          </Card>
        </Col>

        <Col span={24} md={12} lg={8}>
          <Card title="热门股票" loading={data.loading}>
            {data.marketOverview?.hot_stocks ? (
              <>
                <List
                  size="small"
                  dataSource={data.marketOverview.hot_stocks.slice(0, 5)}
                  renderItem={(stock: any) => (
                    <List.Item
                      style={{ padding: '8px 0', cursor: 'pointer' }}
                      onClick={() => navigate(`/analysis/${stock.symbol}`)}
                    >
                      <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between' }}>
                        <div>
                          <Text strong style={{ fontSize: 12 }}>{stock.name}</Text>
                          <br />
                          <Text type="secondary" style={{ fontSize: 10 }}>{stock.symbol}</Text>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: 12 }}>¥{stock.currentPrice?.toFixed(2)}</div>
                          <Tag
                            color={stock.changePercent >= 0 ? 'error' : 'success'}
                            style={{ fontSize: 10, margin: 0 }}
                          >
                            {getChangeIcon(stock.changePercent)}
                            {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent?.toFixed(2)}%
                          </Tag>
                        </div>
                      </div>
                    </List.Item>
                  )}
                />
                <div style={{ textAlign: 'center', marginTop: 12 }}>
                  {data.marketOverview.hot_stocks.length > 5 && (
                    <Button
                      type="link"
                      size="small"
                      onClick={() => navigate('/hot-stocks')}
                      style={{ marginRight: 8 }}
                    >
                      查看更多 →
                    </Button>
                  )}
                  <Button
                    type="link"
                    size="small"
                    onClick={() => navigate('/search')}
                  >
                    股票搜索 →
                  </Button>
                </div>
              </>
            ) : (
              <>
                <div style={{ textAlign: 'center', padding: '20px 0' }}>
                  <Text type="secondary">暂无热门股票数据</Text>
                </div>
                <div style={{ textAlign: 'center', marginTop: 12 }}>
                  <Button
                    type="link"
                    size="small"
                    onClick={() => navigate('/search')}
                  >
                    股票搜索 →
                  </Button>
                </div>
              </>
            )}
          </Card>
        </Col>

        <Col span={24}>
          <Card title="快捷操作">
            <Row gutter={16}>
              <Col span={24} md={6}>
                <Button
                  type="primary"
                  size="large"
                  block
                  onClick={() => navigate('/analysis')}
                >
                  股票分析
                </Button>
              </Col>
              <Col span={24} md={6}>
                <Button
                  size="large"
                  block
                  onClick={() => navigate('/portfolio')}
                >
                  投资组合
                </Button>
              </Col>
              <Col span={24} md={6}>
                <Button
                  size="large"
                  block
                  onClick={() => navigate('/sectors')}
                >
                  板块行情
                </Button>
              </Col>
              <Col span={24} md={6}>
                <Button
                  size="large"
                  block
                  onClick={() => navigate('/ai-chat')}
                >
                  AI助手
                </Button>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
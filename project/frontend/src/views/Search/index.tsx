import React, { useState, useEffect } from 'react'
import { Row, Col, Typography, Card, List, Space, Tag, Avatar, Spin, Button } from 'antd'
import { useNavigate } from 'react-router-dom'
import { RiseOutlined, FallOutlined, StarOutlined, BarChartOutlined } from '@ant-design/icons'
import StockSearch from '@components/business/StockSearch'
import type { StockInfo } from '@store/modules/stocks'
import { marketService } from '@/services'
import { stocksService } from '@/services'
import type { MarketIndex } from '@/services'
import { searchHistoryService, type SearchHistoryItem } from '@utils/searchHistory'

const { Title, Text } = Typography

const Search: React.FC = () => {
  const navigate = useNavigate()
  const [recentSearches, setRecentSearches] = useState<SearchHistoryItem[]>([])
  const [hotStocks, setHotStocks] = useState<StockInfo[]>([])
  const [marketIndices, setMarketIndices] = useState<MarketIndex[]>([])
  const [loading, setLoading] = useState({
    hotStocks: true,
    marketIndices: true
  })
  const [error, setError] = useState<string | null>(null)

  // 获取热门股票数据
  const fetchHotStocks = async () => {
    try {
      setLoading(prev => ({ ...prev, hotStocks: true }))
      const response = await stocksService.getHotStocks(10)
      setHotStocks(response.stocks)
    } catch (err) {
      console.error('获取热门股票失败:', err)
      setError('获取热门股票数据失败')
    } finally {
      setLoading(prev => ({ ...prev, hotStocks: false }))
    }
  }

  // 获取市场指数数据
  const fetchMarketIndices = async () => {
    try {
      setLoading(prev => ({ ...prev, marketIndices: true }))
      const response = await marketService.getMarketIndices()
      setMarketIndices(response.indices)
    } catch (err) {
      console.error('获取市场指数失败:', err)
      setError('获取市场指数数据失败')
    } finally {
      setLoading(prev => ({ ...prev, marketIndices: false }))
    }
  }

  // 加载搜索历史
  const loadRecentSearches = () => {
    const history = searchHistoryService.getRecentSearches(5)
    setRecentSearches(history)
  }

  // 组件挂载时获取数据
  useEffect(() => {
    fetchHotStocks()
    fetchMarketIndices()
    loadRecentSearches()
  }, [])

  const handleStockSelect = (stock: StockInfo) => {
    // 添加到搜索历史
    searchHistoryService.addToSearchHistory(stock)
    // 更新搜索历史显示
    loadRecentSearches()
    // 导航到分析页面
    navigate(`/analysis/${stock.symbol}`)
  }

  const formatPrice = (price: number) => price.toFixed(2)
  const formatChange = (change: number) => (change >= 0 ? `+${change.toFixed(2)}` : change.toFixed(2))
  const formatPercent = (percent: number) => (percent >= 0 ? `+${percent.toFixed(2)}%` : `${percent.toFixed(2)}%`)

  const formatVolume = (volume: number) => {
    if (volume >= 100000000) {
      return `${(volume / 100000000).toFixed(2)}亿`
    } else if (volume >= 10000) {
      return `${(volume / 10000).toFixed(2)}万`
    }
    return volume.toLocaleString()
  }

  const getChangeIcon = (change: number) => change >= 0 ? <RiseOutlined /> : <FallOutlined />
  const getChangeColor = (change: number) => change >= 0 ? '#ff4d4f' : '#52c41a'
  const getChangeTagColor = (change: number) => change >= 0 ? 'error' : 'success'

  const renderStockItem = (stock: StockInfo) => (
    <List.Item
      key={stock.symbol}
      onClick={() => handleStockSelect(stock)}
      style={{ cursor: 'pointer' }}
      actions={[
        <Tag
          key="change"
          color={getChangeTagColor(stock.change)}
          icon={getChangeIcon(stock.change)}
        >
          {formatChange(stock.change)} ({formatPercent(stock.changePercent)})
        </Tag>
      ]}
    >
      <div style={{ width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <Avatar
              size="small"
              style={{
                backgroundColor: getChangeColor(stock.change),
                color: '#fff'
              }}
            >
              {stock.name.charAt(0)}
            </Avatar>
            <div style={{ marginLeft: 12 }}>
              <Text strong>{stock.name}</Text>
              <br />
              <Text type="secondary" style={{ fontSize: 12 }}>
                {stock.symbol}
              </Text>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <Text strong style={{ fontSize: 16, fontFamily: 'monospace' }}>
              ¥{formatPrice(stock.currentPrice)}
            </Text>
            <br />
            <Text type="secondary" style={{ fontSize: 12 }}>
              成交量: {formatVolume(stock.volume)}
            </Text>
          </div>
        </div>
      </div>
    </List.Item>
  )

  return (
    <div>
      <Title level={2}>股票搜索</Title>

      <Row gutter={[16, 16]}>
        {/* 搜索区域 */}
        <Col span={24}>
          <Card>
            <div style={{ maxWidth: 600, margin: '0 auto' }}>
              <StockSearch
                onSelect={handleStockSelect}
                placeholder="搜索股票代码、名称或拼音简写..."
                maxResults={8}
              />
            </div>
          </Card>
        </Col>

        {/* 最近搜索 */}
        <Col span={24} lg={12}>
          <Card
            title={
              <Space>
                <BarChartOutlined />
                <span>最近搜索</span>
              </Space>
            }
            extra={
              searchHistoryService.getSearchHistory().length > 5 && (
                <Button
                  type="link"
                  size="small"
                  onClick={() => navigate('/search-history')}
                >
                  查看更多 →
                </Button>
              )
            }
          >
            <List
              dataSource={recentSearches.slice(0, 5)}
              renderItem={renderStockItem}
              locale={{ emptyText: '暂无搜索历史' }}
            />
            {searchHistoryService.getSearchHistory().length > 5 && (
              <div style={{ textAlign: 'center', marginTop: 12 }}>
                <Button
                  type="link"
                  size="small"
                  onClick={() => navigate('/search-history')}
                >
                  查看全部 {searchHistoryService.getSearchHistory().length} 条搜索记录 →
                </Button>
              </div>
            )}
          </Card>
        </Col>

        {/* 热门股票 */}
        <Col span={24} lg={12}>
          <Card
            title={
              <Space>
                <StarOutlined />
                <span>热门股票</span>
              </Space>
            }
            extra={
              hotStocks.length > 5 && (
                <Button
                  type="link"
                  size="small"
                  onClick={() => navigate('/hot-stocks')}
                >
                  查看更多 →
                </Button>
              )
            }
          >
            <Spin spinning={loading.hotStocks}>
              <List
                dataSource={hotStocks.slice(0, 5)}
                renderItem={renderStockItem}
                locale={{ emptyText: error ? '数据加载失败' : '暂无数据' }}
              />
              {hotStocks.length > 5 && (
                <div style={{ textAlign: 'center', marginTop: 12 }}>
                  <Button
                    type="link"
                    size="small"
                    onClick={() => navigate('/hot-stocks')}
                  >
                    查看全部 {hotStocks.length} 只热门股票 →
                  </Button>
                </div>
              )}
            </Spin>
          </Card>
        </Col>

        {/* 市场概览 */}
        <Col span={24}>
          <Card title="市场概览">
            <Spin spinning={loading.marketIndices}>
              <Row gutter={16}>
                {marketIndices.map((index) => (
                  <Col span={24} md={8} key={index.symbol}>
                    <div style={{ textAlign: 'center', padding: '20px 0' }}>
                      <Text type="secondary">{index.name}</Text>
                      <br />
                      <Text
                        strong
                        style={{
                          fontSize: 20,
                          color: getChangeColor(index.change)
                        }}
                      >
                        {formatPrice(index.currentPrice)}
                      </Text>
                      <br />
                      <Tag
                        color={getChangeTagColor(index.change)}
                        icon={getChangeIcon(index.change)}
                      >
                        {formatPercent(index.changePercent)}
                      </Tag>
                    </div>
                  </Col>
                ))}
                {marketIndices.length === 0 && !loading.marketIndices && (
                  <Col span={24}>
                    <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
                      {error ? '数据加载失败' : '暂无市场指数数据'}
                    </div>
                  </Col>
                )}
              </Row>
            </Spin>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Search
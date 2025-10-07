import React, { useState, useEffect } from 'react'
import { Card, Row, Col, List, Typography, Tag, Spin, Space, Progress, Button, Input, Select } from 'antd'
import { RiseOutlined, FallOutlined, SearchOutlined, ReloadOutlined } from '@ant-design/icons'
import { sectorsService } from '@services/sectors'
import './Sectors.scss'

const { Title, Text } = Typography
const { Search } = Input
const { Option } = Select

export interface SectorInfo {
  code: string
  name: string
  currentPrice: number
  change: number
  changePercent: number
  volume: number
  turnover: number
  stockCount: number
  leadingStocks: string[]
  description?: string
}

export interface SectorStock {
  symbol: string
  name: string
  currentPrice: number
  change: number
  changePercent: number
  volume: number
  turnover: number
  marketCap: number
}

const Sectors: React.FC = () => {
  const [sectors, setSectors] = useState<SectorInfo[]>([])
  const [sectorStocks, setSectorStocks] = useState<{ [key: string]: SectorStock[] }>({})
  const [loading, setLoading] = useState(false)
  const [searchKeyword, setSearchKeyword] = useState('')
  const [sortBy, setSortBy] = useState<'change' | 'changePercent' | 'volume' | 'turnover'>('changePercent')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // 加载板块数据
  const loadSectors = async () => {
    try {
      setLoading(true)
      const response = await sectorsService.getSectors()
      setSectors(response.sectors || [])
    } catch (error) {
      console.error('获取板块数据失败:', error)
      setSectors([])
    } finally {
      setLoading(false)
    }
  }

  // 加载板块股票
  const loadSectorStocks = async (sectorCode: string) => {
    if (sectorStocks[sectorCode]) return

    try {
      const response = await sectorsService.getSectorStocks(sectorCode)
      setSectorStocks(prev => ({
        ...prev,
        [sectorCode]: response.stocks || []
      }))
    } catch (error) {
      console.error(`获取板块${sectorCode}股票失败:`, error)
      setSectorStocks(prev => ({
        ...prev,
        [sectorCode]: []
      }))
    }
  }

  useEffect(() => {
    loadSectors()
  }, [])

  // 格式化数字
  const formatPrice = (price: number) => price.toFixed(2)
  const formatChange = (change: number) => (change >= 0 ? `+${change.toFixed(2)}` : change.toFixed(2))
  const formatPercent = (percent: number) => (percent >= 0 ? `+${percent.toFixed(2)}%` : `${percent.toFixed(2)}%`)
  const formatVolume = (volume: number) => {
    if (volume >= 100000000) return `${(volume / 100000000).toFixed(2)}亿`
    if (volume >= 10000) return `${(volume / 10000).toFixed(2)}万`
    return volume.toString()
  }

  // 获取涨跌颜色
  const getChangeColor = (change: number) => change >= 0 ? '#ff4d4f' : '#52c41a'
  const getChangeTagColor = (change: number) => change >= 0 ? 'error' : 'success'
  const getChangeIcon = (change: number) => change >= 0 ? <RiseOutlined /> : <FallOutlined />

  // 过滤和排序板块
  const filteredAndSortedSectors = sectors
    .filter(sector =>
      sector.name.toLowerCase().includes(searchKeyword.toLowerCase()) ||
      sector.code.toLowerCase().includes(searchKeyword.toLowerCase())
    )
    .sort((a, b) => {
      const aValue = a[sortBy]
      const bValue = b[sortBy]
      return sortOrder === 'desc' ? bValue - aValue : aValue - bValue
    })

  return (
    <div className="sectors-container">
      <div className="sectors-header">
        <div className="header-title">
          <Title level={2}>板块行情</Title>
          <Text type="secondary">实时板块涨跌幅排行及成分股信息</Text>
        </div>

        <div className="header-actions">
          <Space size="middle">
            <Search
              placeholder="搜索板块名称或代码"
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              style={{ width: 240 }}
              prefix={<SearchOutlined />}
            />

            <Select
              value={sortBy}
              onChange={setSortBy}
              style={{ width: 120 }}
            >
              <Option value="changePercent">涨跌幅</Option>
              <Option value="change">涨跌额</Option>
              <Option value="volume">成交量</Option>
              <Option value="turnover">成交额</Option>
            </Select>

            <Select
              value={sortOrder}
              onChange={setSortOrder}
              style={{ width: 80 }}
            >
              <Option value="desc">降序</Option>
              <Option value="asc">升序</Option>
            </Select>

            <Button
              type="primary"
              icon={<ReloadOutlined />}
              onClick={loadSectors}
              loading={loading}
            >
              刷新
            </Button>
          </Space>
        </div>
      </div>

      <Spin spinning={loading}>
        {filteredAndSortedSectors.length > 0 ? (
          <Row gutter={[16, 16]}>
            {filteredAndSortedSectors.map((sector) => (
              <Col key={sector.code} xs={24} sm={12} lg={8} xl={6}>
                <Card
                  className="sector-card"
                  hoverable
                  onClick={() => loadSectorStocks(sector.code)}
                >
                  <div className="sector-header">
                    <div className="sector-info">
                      <Title level={4} className="sector-name">{sector.name}</Title>
                      <Text type="secondary" className="sector-code">{sector.code}</Text>
                    </div>
                    <div className="sector-price">
                      <Text className="current-price">
                        ¥{formatPrice(sector.currentPrice)}
                      </Text>
                      <Tag
                        color={getChangeTagColor(sector.change)}
                        icon={getChangeIcon(sector.change)}
                        className="change-tag"
                      >
                        {formatChange(sector.change)} ({formatPercent(sector.changePercent)})
                      </Tag>
                    </div>
                  </div>

                  <div className="sector-metrics">
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div className="metric-row">
                        <span>成交量</span>
                        <span>{formatVolume(sector.volume)}</span>
                      </div>
                      <div className="metric-row">
                        <span>成交额</span>
                        <span>¥{formatVolume(sector.turnover)}</span>
                      </div>
                      <div className="metric-row">
                        <span>股票数量</span>
                        <span>{sector.stockCount}只</span>
                      </div>
                    </Space>
                  </div>

                  {sector.leadingStocks && sector.leadingStocks.length > 0 && (
                    <div className="leading-stocks">
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        龙头股：{sector.leadingStocks.join('、')}
                      </Text>
                    </div>
                  )}

                  {sectorStocks[sector.code] && (
                    <div className="sector-stocks">
                      <List
                        size="small"
                        dataSource={sectorStocks[sector.code].slice(0, 5)}
                        renderItem={(stock) => (
                          <List.Item>
                            <div className="stock-item">
                              <div className="stock-name">
                                <Text strong>{stock.name}</Text>
                                <Text type="secondary" style={{ fontSize: 12 }}>
                                  {stock.symbol}
                                </Text>
                              </div>
                              <div className="stock-price">
                                <Text style={{ color: getChangeColor(stock.change) }}>
                                  ¥{formatPrice(stock.currentPrice)}
                                </Text>
                                <Text
                                  style={{
                                    color: getChangeColor(stock.change),
                                    fontSize: 12
                                  }}
                                >
                                  {formatPercent(stock.changePercent)}
                                </Text>
                              </div>
                            </div>
                          </List.Item>
                        )}
                      />
                      {sectorStocks[sector.code].length > 5 && (
                        <div className="more-stocks">
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            +{sectorStocks[sector.code].length - 5}只股票...
                          </Text>
                        </div>
                      )}
                    </div>
                  )}
                </Card>
              </Col>
            ))}
          </Row>
        ) : (
          <div className="empty-state">
            <Text type="secondary">暂无板块数据</Text>
          </div>
        )}
      </Spin>
    </div>
  )
}

export default Sectors
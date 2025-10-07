import React, { useState, useEffect } from 'react'
import { Row, Col, Typography, Card, List, Space, Tag, Avatar, Spin, Button, Select, Alert } from 'antd'
import { useNavigate } from 'react-router-dom'
import { RiseOutlined, FallOutlined, StarOutlined, ReloadOutlined, ArrowLeftOutlined } from '@ant-design/icons'
import type { StockInfo } from '@store/modules/stocks'
import { stocksService } from '@/services'

const { Title, Text } = Typography
const { Option } = Select

const HotStocks: React.FC = () => {
  const navigate = useNavigate()
  const [hotStocks, setHotStocks] = useState<StockInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [hotType, setHotType] = useState<string>('gainers')

  // 获取热门股票数据
  const fetchHotStocks = async (type: string = 'gainers') => {
    try {
      setLoading(true)
      setError(null)
      const response = await stocksService.getHotStocks(20, type)
      setHotStocks(response.stocks)
    } catch (err) {
      console.error('获取热门股票失败:', err)
      setError('获取热门股票数据失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  // 组件挂载时获取数据
  useEffect(() => {
    fetchHotStocks(hotType)
  }, [hotType])

  const handleStockSelect = (stock: StockInfo) => {
    navigate(`/analysis/${stock.symbol}`)
  }

  const handleRefresh = () => {
    fetchHotStocks(hotType)
  }

  const handleTypeChange = (value: string) => {
    setHotType(value)
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

  const formatTurnover = (turnover: number) => {
    if (turnover >= 100000000) {
      return `${(turnover / 100000000).toFixed(2)}亿`
    } else if (turnover >= 10000) {
      return `${(turnover / 10000).toFixed(2)}万`
    }
    return turnover.toLocaleString()
  }

  const getChangeIcon = (change: number) => change >= 0 ? <RiseOutlined /> : <FallOutlined />
  const getChangeColor = (change: number) => change >= 0 ? '#ff4d4f' : '#52c41a'
  const getChangeTagColor = (change: number) => change >= 0 ? 'error' : 'success'

  const getHotTypeTitle = (type: string) => {
    switch (type) {
      case 'gainers':
        return '涨幅榜'
      case 'volume':
        return '成交量榜'
      case 'turnover':
        return '换手率榜'
      default:
        return '热门股票'
    }
  }

  const renderStockItem = (stock: StockInfo, index: number) => (
    <List.Item
      key={stock.symbol}
      onClick={() => handleStockSelect(stock)}
      style={{ cursor: 'pointer', padding: '16px' }}
      className="stock-item"
    >
      <div style={{ width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* 排名和基本信息 */}
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: '50%',
                backgroundColor: index < 3 ? '#ff4d4f' : '#f0f0f0',
                color: index < 3 ? '#fff' : '#666',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 'bold',
                marginRight: 12
              }}
            >
              {index + 1}
            </div>
            <Avatar
              size="small"
              style={{
                backgroundColor: getChangeColor(stock.change),
                color: '#fff',
                marginRight: 12
              }}
            >
              {stock.name.charAt(0)}
            </Avatar>
            <div>
              <Text strong style={{ fontSize: 16 }}>{stock.name}</Text>
              <br />
              <Text type="secondary" style={{ fontSize: 12 }}>
                {stock.symbol}
              </Text>
            </div>
          </div>

          {/* 价格和涨跌信息 */}
          <div style={{ textAlign: 'right' }}>
            <Text strong style={{ fontSize: 18, fontFamily: 'monospace' }}>
              ¥{formatPrice(stock.currentPrice)}
            </Text>
            <br />
            <Tag
              color={getChangeTagColor(stock.change)}
              icon={getChangeIcon(stock.change)}
              style={{ fontSize: 12 }}
            >
              {formatChange(stock.change)} ({formatPercent(stock.changePercent)})
            </Tag>
          </div>
        </div>

        {/* 详细信息 */}
        <div style={{ marginTop: 12, display: 'flex', justifyContent: 'space-between', fontSize: 12, color: '#666' }}>
          <div>
            <Text type="secondary">成交量: {formatVolume(stock.volume)}</Text>
          </div>
          <div>
            <Text type="secondary">成交额: {formatTurnover(stock.turnover)}</Text>
          </div>
          {stock.turnoverRate && (
            <div>
              <Text type="secondary">换手率: {stock.turnoverRate.toFixed(2)}%</Text>
            </div>
          )}
          {stock.pe && (
            <div>
              <Text type="secondary">市盈率: {stock.pe.toFixed(2)}</Text>
            </div>
          )}
        </div>
      </div>
    </List.Item>
  )

  return (
    <div>
      {/* 页面头部 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(-1)}
            style={{ marginRight: 16 }}
          >
            返回
          </Button>
          <Title level={2} style={{ margin: 0 }}>
            <StarOutlined style={{ marginRight: 8 }} />
            {getHotTypeTitle(hotType)}
          </Title>
        </div>
        <Space>
          <Select
            value={hotType}
            onChange={handleTypeChange}
            style={{ width: 120 }}
          >
            <Option value="gainers">涨幅榜</Option>
            <Option value="volume">成交量榜</Option>
            <Option value="turnover">换手率榜</Option>
          </Select>
          <Button
            icon={<ReloadOutlined />}
            onClick={handleRefresh}
            loading={loading}
          >
            刷新
          </Button>
        </Space>
      </div>

      {/* 错误提示 */}
      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
          action={
            <Button size="small" onClick={handleRefresh}>
              重试
            </Button>
          }
        />
      )}

      {/* 热门股票列表 */}
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card
            title={
              <Space>
                <StarOutlined />
                <span>{getHotTypeTitle(hotType)}</span>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  (共{hotStocks.length}只股票)
                </Text>
              </Space>
            }
            extra={
              <Text type="secondary" style={{ fontSize: 12 }}>
                点击股票查看详细分析
              </Text>
            }
          >
            <Spin spinning={loading}>
              <List
                dataSource={hotStocks}
                renderItem={renderStockItem}
                locale={{ emptyText: error ? '数据加载失败' : '暂无数据' }}
                split={true}
              />
            </Spin>
          </Card>
        </Col>
      </Row>

      <style jsx>{`
        .stock-item:hover {
          background-color: #f5f5f5;
          border-radius: 8px;
        }
      `}</style>
    </div>
  )
}

export default HotStocks
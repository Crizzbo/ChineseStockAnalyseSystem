import React, { useState, useEffect } from 'react'
import { Row, Col, Typography, Card, List, Space, Tag, Avatar, Button, Empty, Popconfirm } from 'antd'
import { useNavigate } from 'react-router-dom'
import { RiseOutlined, FallOutlined, HistoryOutlined, ArrowLeftOutlined, DeleteOutlined, ClearOutlined } from '@ant-design/icons'
import { searchHistoryService, type SearchHistoryItem } from '@utils/searchHistory'

const { Title, Text } = Typography

const SearchHistory: React.FC = () => {
  const navigate = useNavigate()
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([])

  useEffect(() => {
    loadSearchHistory()
  }, [])

  const loadSearchHistory = () => {
    const history = searchHistoryService.getSearchHistory()
    setSearchHistory(history)
  }

  const handleStockSelect = (stock: SearchHistoryItem) => {
    navigate(`/analysis/${stock.symbol}`)
  }

  const handleRemoveItem = (symbol: string) => {
    searchHistoryService.removeFromSearchHistory(symbol)
    loadSearchHistory()
  }

  const handleClearAll = () => {
    searchHistoryService.clearSearchHistory()
    setSearchHistory([])
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

  const formatTime = (timestamp: number) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()

    if (diff < 60000) { // 1分钟内
      return '刚刚'
    } else if (diff < 3600000) { // 1小时内
      return `${Math.floor(diff / 60000)}分钟前`
    } else if (diff < 86400000) { // 24小时内
      return `${Math.floor(diff / 3600000)}小时前`
    } else if (diff < 604800000) { // 7天内
      return `${Math.floor(diff / 86400000)}天前`
    } else {
      return date.toLocaleDateString()
    }
  }

  const getChangeIcon = (change: number) => change >= 0 ? <RiseOutlined /> : <FallOutlined />
  const getChangeColor = (change: number) => change >= 0 ? '#ff4d4f' : '#52c41a'
  const getChangeTagColor = (change: number) => change >= 0 ? 'error' : 'success'

  const renderStockItem = (stock: SearchHistoryItem) => (
    <List.Item
      key={stock.symbol}
      onClick={() => handleStockSelect(stock)}
      style={{ cursor: 'pointer', padding: '16px' }}
      className="stock-item"
      actions={[
        <Popconfirm
          key="delete"
          title="确定要删除这条搜索记录吗？"
          onConfirm={(e) => {
            e?.stopPropagation()
            handleRemoveItem(stock.symbol)
          }}
          okText="确定"
          cancelText="取消"
        >
          <Button
            type="text"
            size="small"
            icon={<DeleteOutlined />}
            onClick={(e) => e.stopPropagation()}
            style={{ color: '#ff4d4f' }}
          />
        </Popconfirm>
      ]}
    >
      <div style={{ width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
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
                {stock.symbol} • {formatTime(stock.searchTime)}
              </Text>
            </div>
          </div>

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

        <div style={{ marginTop: 12, display: 'flex', justifyContent: 'space-between', fontSize: 12, color: '#666' }}>
          <div>
            <Text type="secondary">成交量: {formatVolume(stock.volume)}</Text>
          </div>
          {stock.turnover && (
            <div>
              <Text type="secondary">成交额: {formatVolume(stock.turnover)}</Text>
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
            <HistoryOutlined style={{ marginRight: 8 }} />
            搜索历史
          </Title>
        </div>
        {searchHistory.length > 0 && (
          <Popconfirm
            title="确定要清空所有搜索历史吗？"
            onConfirm={handleClearAll}
            okText="确定"
            cancelText="取消"
          >
            <Button
              icon={<ClearOutlined />}
              danger
            >
              清空历史
            </Button>
          </Popconfirm>
        )}
      </div>

      {/* 搜索历史列表 */}
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card
            title={
              <Space>
                <HistoryOutlined />
                <span>搜索历史</span>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  (共{searchHistory.length}条记录)
                </Text>
              </Space>
            }
            extra={
              <Text type="secondary" style={{ fontSize: 12 }}>
                点击股票查看详细分析
              </Text>
            }
          >
            {searchHistory.length > 0 ? (
              <List
                dataSource={searchHistory}
                renderItem={renderStockItem}
                split={true}
              />
            ) : (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="暂无搜索历史"
                style={{ padding: '40px 0' }}
              >
                <Button type="primary" onClick={() => navigate('/search')}>
                  开始搜索股票
                </Button>
              </Empty>
            )}
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

export default SearchHistory
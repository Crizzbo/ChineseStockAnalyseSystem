import React, { useState, useEffect, useRef } from 'react'
import { Input, List, Card, Tag, Typography, Space, Avatar, Spin, Progress } from 'antd'
import { SearchOutlined, RiseOutlined, FallOutlined, StarOutlined, StarFilled } from '@ant-design/icons'
import { useSelector, useDispatch } from 'react-redux'
import type { RootState, AppDispatch } from '@store/index'
import { searchStocks, clearSearchResults, addToWatchList, removeFromWatchList } from '@store/modules/stocks'
import type { StockInfo } from '@store/modules/stocks'
import { useStockPrice } from '@hooks/useWebSocket'
import { stocksService } from '@services/stocks'
import './StockSearch.scss'

const { Text } = Typography
const { Search } = Input

interface StockSearchProps {
  onSelect?: (stock: StockInfo) => void
  placeholder?: string
  showResults?: boolean
  maxResults?: number
}

const StockSearch: React.FC<StockSearchProps> = ({
  onSelect,
  placeholder = '搜索股票代码或名称',
  showResults = true,
  maxResults = 10
}) => {
  const dispatch = useDispatch<AppDispatch>()
  const { watchList } = useSelector((state: RootState) => state.stocks)
  const { allPrices, getPrice } = useStockPrice()

  const [searchValue, setSearchValue] = useState('')
  const [showDropdown, setShowDropdown] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [localSearchResults, setLocalSearchResults] = useState<StockInfo[]>([])
  const searchRef = useRef<HTMLDivElement>(null)
  const debounceRef = useRef<number | undefined>(undefined)

  // 搜索股票的函数
  const performSearch = async (keyword: string) => {
    if (!keyword.trim()) {
      setLocalSearchResults([])
      return
    }

    try {
      setIsSearching(true)
      const response = await stocksService.searchStocks({
        keyword: keyword.trim(),
        limit: maxResults
      })
      setLocalSearchResults(response.stocks || [])
    } catch (error) {
      console.error('搜索股票失败:', error)
      setLocalSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  const handleSearch = (value: string) => {
    setSearchValue(value)

    if (debounceRef.current) {
      window.clearTimeout(debounceRef.current)
    }

    if (!value.trim()) {
      setLocalSearchResults([])
      setShowDropdown(false)
      return
    }

    setShowDropdown(true)
    debounceRef.current = window.setTimeout(() => {
      performSearch(value)
    }, 500) // 增加防抖时间，减少API调用
  }

  const handleStockSelect = (stock: StockInfo) => {
    setShowDropdown(false)
    setSearchValue('')
    setLocalSearchResults([])
    onSelect?.(stock)
  }

  const toggleWatchList = (stock: StockInfo, event: React.MouseEvent) => {
    event.stopPropagation()

    if (watchList.includes(stock.symbol)) {
      dispatch(removeFromWatchList(stock.symbol))
    } else {
      dispatch(addToWatchList(stock.symbol))
    }
  }

  const formatPrice = (price: number) => price.toFixed(2)
  const formatChange = (change: number) => (change >= 0 ? `+${change.toFixed(2)}` : change.toFixed(2))
  const formatPercent = (percent: number) => (percent >= 0 ? `+${percent.toFixed(2)}%` : `${percent.toFixed(2)}%`)

  const getChangeColor = (change: number) => change >= 0 ? '#ff4d4f' : '#52c41a'
  const getChangeTagColor = (change: number) => change >= 0 ? 'error' : 'success'
  const getChangeIcon = (change: number) => change >= 0 ? <RiseOutlined /> : <FallOutlined />

  // 获取当前搜索的结果并更新实时价格
  const currentResults = localSearchResults.map(stock => {
    const realTimePrice = getPrice(stock.symbol)
    if (realTimePrice) {
      return {
        ...stock,
        currentPrice: realTimePrice.price,
        change: realTimePrice.change,
        changePercent: realTimePrice.changePercent,
        volume: realTimePrice.volume
      }
    }
    return stock
  })

  // 点击外部关闭下拉
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="stock-search" ref={searchRef}>
      <Search
        placeholder={placeholder}
        value={searchValue}
        onChange={(e) => handleSearch(e.target.value)}
        onFocus={() => searchValue.trim() && setShowDropdown(true)}
        prefix={<SearchOutlined />}
        loading={isSearching}
        size="large"
      />

      {showResults && showDropdown && (
        <Card className="search-results-dropdown" bodyStyle={{ padding: 0 }}>
          {isSearching ? (
            <div className="search-loading">
              <div style={{ padding: '16px', textAlign: 'center' }}>
                <Progress
                  type="line"
                  percent={100}
                  status="active"
                  showInfo={false}
                  strokeWidth={3}
                  style={{ marginBottom: 8 }}
                />
                <div>
                  <Spin size="small" />
                  <Text type="secondary" style={{ marginLeft: 8 }}>正在搜索股票数据...</Text>
                </div>
              </div>
            </div>
          ) : currentResults.length > 0 ? (
            <List
              dataSource={currentResults}
              renderItem={(stock) => {
                const isInWatchList = watchList.includes(stock.symbol)

                return (
                  <List.Item
                    className="search-result-item"
                    onClick={() => handleStockSelect(stock)}
                    actions={[
                      <button
                        key="watch"
                        className="watch-btn"
                        onClick={(e) => toggleWatchList(stock, e)}
                        title={isInWatchList ? '移出自选' : '加入自选'}
                      >
                        {isInWatchList ? <StarFilled style={{ color: '#faad14' }} /> : <StarOutlined />}
                      </button>
                    ]}
                  >
                    <div className="stock-item-content">
                      <div className="stock-basic-info">
                        <div className="stock-identity">
                          <Avatar
                            size="small"
                            style={{
                              backgroundColor: getChangeColor(stock.change),
                              color: '#fff'
                            }}
                          >
                            {stock.name.charAt(0)}
                          </Avatar>
                          <div className="stock-names">
                            <Text strong>{stock.name}</Text>
                            <Text type="secondary" className="stock-symbol">
                              {stock.symbol}
                            </Text>
                          </div>
                        </div>

                        <div className="stock-price-info">
                          <div className="price-main">
                            <Text className="current-price" style={{ fontSize: 16, fontWeight: 'bold' }}>
                              ¥{formatPrice(stock.currentPrice)}
                            </Text>
                          </div>

                          <div className="price-change">
                            <Tag
                              color={getChangeTagColor(stock.change)}
                              icon={getChangeIcon(stock.change)}
                              className="change-tag"
                            >
                              {formatChange(stock.change)} ({formatPercent(stock.changePercent)})
                            </Tag>
                          </div>
                        </div>
                      </div>

                      <div className="stock-metrics">
                        <Space size="large">
                          <div className="metric-item">
                            <Text type="secondary">成交量</Text>
                            <Text>{(stock.volume / 100000000).toFixed(2)}亿</Text>
                          </div>
                          {stock.pe && (
                            <div className="metric-item">
                              <Text type="secondary">PE</Text>
                              <Text>{stock.pe}</Text>
                            </div>
                          )}
                          {stock.pb && (
                            <div className="metric-item">
                              <Text type="secondary">PB</Text>
                              <Text>{stock.pb}</Text>
                            </div>
                          )}
                        </Space>
                      </div>
                    </div>
                  </List.Item>
                )
              }}
            />
          ) : searchValue.trim() ? (
            <div className="no-results">
              <Text type="secondary">未找到相关股票</Text>
            </div>
          ) : null}
        </Card>
      )}
    </div>
  )
}

export default StockSearch
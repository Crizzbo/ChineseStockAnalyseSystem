import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Typography, Button, Table, Space, Statistic, Tag, Progress, Modal, Form, Input, Select, message, Spin, AutoComplete } from 'antd'
import { useNavigate } from 'react-router-dom'
import { PlusOutlined, EditOutlined, DeleteOutlined, RiseOutlined, FallOutlined, PieChartOutlined, SearchOutlined } from '@ant-design/icons'
import { useSelector, useDispatch } from 'react-redux'
import type { RootState, AppDispatch } from '@store/index'
import type { StockInfo } from '@store/modules/stocks'
import { stocksService } from '@services/stocks'
import { portfolioService } from '@services/portfolio'
import './Portfolio.scss'

const { Title, Text } = Typography
const { Option } = Select

interface PortfolioStock {
  id: string
  symbol: string
  name: string
  shares: number
  avgCost: number
  currentPrice: number
  totalValue: number
  gainLoss: number
  gainLossPercent: number
  weight: number
}

interface Portfolio {
  id: string
  name: string
  description?: string
  totalValue: number
  totalCost: number
  totalGainLoss: number
  totalGainLossPercent: number
  stocks: PortfolioStock[]
  createdAt: string
  updatedAt: string
}

const Portfolio: React.FC = () => {
  const navigate = useNavigate()
  const dispatch = useDispatch<AppDispatch>()
  const { user } = useSelector((state: RootState) => state.auth)

  const [portfolios, setPortfolios] = useState<Portfolio[]>([])
  const [currentPortfolio, setCurrentPortfolio] = useState<Portfolio | null>(null)
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingStock, setEditingStock] = useState<PortfolioStock | null>(null)
  const [form] = Form.useForm()

  // 股票搜索相关状态
  const [stockSearchOptions, setStockSearchOptions] = useState<StockInfo[]>([])
  const [stockSearchLoading, setStockSearchLoading] = useState(false)
  const [selectedStock, setSelectedStock] = useState<StockInfo | null>(null)

  // 模拟投资组合数据
  const mockPortfolios: Portfolio[] = [
    {
      id: '1',
      name: '我的主要组合',
      description: '长期价值投资组合',
      totalValue: 125600,
      totalCost: 100000,
      totalGainLoss: 25600,
      totalGainLossPercent: 25.6,
      stocks: [
        {
          id: '1',
          symbol: '000001',
          name: '平安银行',
          shares: 2000,
          avgCost: 12.50,
          currentPrice: 12.45,
          totalValue: 24900,
          gainLoss: -100,
          gainLossPercent: -0.4,
          weight: 19.8
        },
        {
          id: '2',
          symbol: '600519',
          name: '贵州茅台',
          shares: 30,
          avgCost: 1600.00,
          currentPrice: 1650.00,
          totalValue: 49500,
          gainLoss: 1500,
          gainLossPercent: 3.1,
          weight: 39.4
        },
        {
          id: '3',
          symbol: '000858',
          name: '五粮液',
          shares: 300,
          avgCost: 165.00,
          currentPrice: 168.50,
          totalValue: 50550,
          gainLoss: 1050,
          gainLossPercent: 2.1,
          weight: 40.2
        }
      ],
      createdAt: '2024-01-15',
      updatedAt: '2024-01-20'
    }
  ]

  useEffect(() => {
    loadPortfolios()
  }, [])

  const loadPortfolios = async () => {
    setLoading(true)
    try {
      const response = await portfolioService.getPortfolios()

      // 将API数据转换为组件需要的格式
      const portfolioData = (response.data || []).map((portfolio: any) => ({
        id: portfolio.id.toString(),
        name: portfolio.name,
        description: portfolio.description || '',
        totalValue: portfolio.total_value || 0,
        totalCost: portfolio.total_cost || 0,
        totalGainLoss: portfolio.total_gain_loss || 0,
        totalGainLossPercent: portfolio.total_gain_loss_percent || 0,
        stocks: portfolio.stocks ? portfolio.stocks.map((stock: any) => ({
          id: stock.id.toString(),
          symbol: stock.symbol,
          name: stock.name,
          shares: stock.shares,
          avgCost: stock.avg_cost,
          currentPrice: stock.current_price || stock.avg_cost,
          totalValue: stock.shares * (stock.current_price || stock.avg_cost),
          gainLoss: stock.gain_loss || 0,
          gainLossPercent: stock.gain_loss_percent || 0,
          weight: stock.weight || 0
        })) : [],
        createdAt: portfolio.created_at,
        updatedAt: portfolio.updated_at
      }))

      setPortfolios(portfolioData)
      if (portfolioData.length > 0) {
        setCurrentPortfolio(portfolioData[0])
      }
    } catch (error) {
      console.error('加载投资组合失败:', error)
      message.error('加载投资组合失败，请稍后重试')

      // 如果API调用失败，使用模拟数据作为后备
      setPortfolios(mockPortfolios)
      if (mockPortfolios.length > 0) {
        setCurrentPortfolio(mockPortfolios[0])
      }
    } finally {
      setLoading(false)
    }
  }

  // 搜索股票
  const handleStockSearch = async (value: string) => {
    if (!value || value.length < 2) {
      setStockSearchOptions([])
      return
    }

    setStockSearchLoading(true)
    try {
      const response = await stocksService.searchStocks({
        keyword: value.trim(),
        limit: 10
      })
      setStockSearchOptions(response.stocks || [])
    } catch (error) {
      console.error('搜索股票失败:', error)
      setStockSearchOptions([])
    } finally {
      setStockSearchLoading(false)
    }
  }

  // 选择股票
  const handleStockSelect = (value: string) => {
    const stock = stockSearchOptions.find(s => s.symbol === value)
    if (stock) {
      setSelectedStock(stock)
      // 自动填入当前价格作为成本价的参考
      form.setFieldsValue({
        symbol: stock.symbol,
        avgCost: stock.currentPrice
      })
    }
  }

  const handleAddStock = () => {
    setEditingStock(null)
    setSelectedStock(null)
    setStockSearchOptions([])
    form.resetFields()
    setModalVisible(true)
  }

  const handleEditStock = (stock: PortfolioStock) => {
    setEditingStock(stock)
    form.setFieldsValue({
      symbol: stock.symbol,
      shares: stock.shares,
      avgCost: stock.avgCost
    })
    setModalVisible(true)
  }

  const handleDeleteStock = (stockId: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要从投资组合中删除这只股票吗？',
      okText: '确认',
      cancelText: '取消',
      async onOk() {
        try {
          if (!currentPortfolio) {
            message.error('请先选择投资组合')
            return
          }

          await portfolioService.removeStockFromPortfolio(
            parseInt(currentPortfolio.id),
            parseInt(stockId)
          )

          message.success('股票已从投资组合中删除')
          loadPortfolios() // 重新加载数据
        } catch (error) {
          console.error('删除股票失败:', error)
          message.error('删除失败，请重试')
        }
      }
    })
  }

  const handleSubmit = async (values: any) => {
    try {
      const stockData = {
        symbol: values.symbol,
        name: selectedStock?.name || values.symbol,
        shares: parseInt(values.shares),
        avgCost: parseFloat(values.avgCost),
        currentPrice: selectedStock?.currentPrice || 0
      }

      // 简单验证
      if (stockData.shares <= 0) {
        message.error('持股数量必须大于0')
        return
      }

      if (stockData.avgCost <= 0) {
        message.error('成本价必须大于0')
        return
      }

      // 检查是否重复添加
      if (!editingStock && currentPortfolio?.stocks.some(s => s.symbol === stockData.symbol)) {
        message.error('该股票已在投资组合中，请勿重复添加')
        return
      }

      if (!currentPortfolio) {
        message.error('请先选择投资组合')
        return
      }

      if (editingStock) {
        // 更新现有股票
        await portfolioService.updatePortfolioStock(
          parseInt(currentPortfolio.id),
          parseInt(editingStock.id),
          {
            shares: stockData.shares,
            avg_cost: stockData.avgCost
          }
        )
        message.success('股票信息已更新')
      } else {
        // 添加新股票
        await portfolioService.addStockToPortfolio(
          parseInt(currentPortfolio.id),
          {
            symbol: stockData.symbol,
            name: stockData.name,
            shares: stockData.shares,
            avg_cost: stockData.avgCost
          }
        )
        message.success('股票已添加到投资组合')
      }

      setModalVisible(false)
      setSelectedStock(null)
      setStockSearchOptions([])
      form.resetFields()
      loadPortfolios() // 重新加载数据
    } catch (error) {
      console.error('提交失败:', error)
      message.error('操作失败，请重试')
    }
  }

  const formatNumber = (num: number, precision: number = 2) => {
    return num.toLocaleString('zh-CN', {
      minimumFractionDigits: precision,
      maximumFractionDigits: precision
    })
  }

  const getChangeColor = (value: number) => value >= 0 ? '#ff4d4f' : '#52c41a'
  const getChangeIcon = (value: number) => value >= 0 ? <RiseOutlined /> : <FallOutlined />

  const columns = [
    {
      title: '股票',
      key: 'stock',
      render: (record: PortfolioStock) => (
        <div>
          <Text strong>{record.name}</Text>
          <br />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {record.symbol}
          </Text>
        </div>
      )
    },
    {
      title: '持股数量',
      dataIndex: 'shares',
      key: 'shares',
      render: (shares: number) => `${formatNumber(shares, 0)}股`
    },
    {
      title: '成本价',
      dataIndex: 'avgCost',
      key: 'avgCost',
      render: (price: number) => `¥${formatNumber(price)}`
    },
    {
      title: '现价',
      dataIndex: 'currentPrice',
      key: 'currentPrice',
      render: (price: number) => `¥${formatNumber(price)}`
    },
    {
      title: '市值',
      dataIndex: 'totalValue',
      key: 'totalValue',
      render: (value: number) => `¥${formatNumber(value)}`
    },
    {
      title: '盈亏',
      key: 'gainLoss',
      render: (record: PortfolioStock) => (
        <div>
          <Text style={{ color: getChangeColor(record.gainLoss) }}>
            {getChangeIcon(record.gainLoss)}
            ¥{formatNumber(Math.abs(record.gainLoss))}
          </Text>
          <br />
          <Text style={{ color: getChangeColor(record.gainLossPercent), fontSize: 12 }}>
            {record.gainLossPercent >= 0 ? '+' : ''}{formatNumber(record.gainLossPercent)}%
          </Text>
        </div>
      )
    },
    {
      title: '权重',
      dataIndex: 'weight',
      key: 'weight',
      render: (weight: number) => (
        <div>
          <Text>{formatNumber(weight)}%</Text>
          <Progress percent={weight} showInfo={false} size="small" />
        </div>
      )
    },
    {
      title: '操作',
      key: 'actions',
      render: (record: PortfolioStock) => (
        <Space>
          <Button
            type="text"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEditStock(record)}
          >
            编辑
          </Button>
          <Button
            type="text"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteStock(record.id)}
          >
            删除
          </Button>
        </Space>
      )
    }
  ]

  return (
    <div className="portfolio">
      <div className="page-header">
        <Title level={2}>投资组合</Title>
        <Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleAddStock}
          >
            添加股票
          </Button>
          <Button
            icon={<SearchOutlined />}
            onClick={() => navigate('/search')}
          >
            股票搜索
          </Button>
        </Space>
      </div>

      {currentPortfolio && (
        <Row gutter={[16, 16]}>
          {/* 投资组合总览 */}
          <Col span={24}>
            <Card
              title={
                <Space>
                  <PieChartOutlined />
                  <span>{currentPortfolio.name}</span>
                </Space>
              }
              extra={
                <Text type="secondary">
                  更新时间：{currentPortfolio.updatedAt}
                </Text>
              }
              className="portfolio-overview-card"
            >
              <Row gutter={24}>
                <Col span={24} md={6}>
                  <Statistic
                    title="总市值"
                    value={currentPortfolio.totalValue}
                    formatter={(value) => `¥${formatNumber(Number(value))}`}
                    valueStyle={{ fontSize: 20, fontWeight: 'bold' }}
                  />
                </Col>
                <Col span={24} md={6}>
                  <Statistic
                    title="总成本"
                    value={currentPortfolio.totalCost}
                    formatter={(value) => `¥${formatNumber(Number(value))}`}
                    valueStyle={{ fontSize: 16 }}
                  />
                </Col>
                <Col span={24} md={6}>
                  <Statistic
                    title="总盈亏"
                    value={currentPortfolio.totalGainLoss}
                    formatter={(value) => `¥${formatNumber(Number(value))}`}
                    valueStyle={{
                      color: getChangeColor(currentPortfolio.totalGainLoss),
                      fontSize: 16,
                      fontWeight: 'bold'
                    }}
                    prefix={getChangeIcon(currentPortfolio.totalGainLoss)}
                  />
                </Col>
                <Col span={24} md={6}>
                  <Statistic
                    title="总收益率"
                    value={currentPortfolio.totalGainLossPercent}
                    precision={2}
                    suffix="%"
                    valueStyle={{
                      color: getChangeColor(currentPortfolio.totalGainLossPercent),
                      fontSize: 16,
                      fontWeight: 'bold'
                    }}
                    prefix={getChangeIcon(currentPortfolio.totalGainLossPercent)}
                  />
                </Col>
              </Row>
            </Card>
          </Col>

          {/* 持股明细 */}
          <Col span={24}>
            <Card title="持股明细" className="portfolio-stocks-card">
              <Table
                columns={columns}
                dataSource={currentPortfolio.stocks}
                rowKey="id"
                loading={loading}
                pagination={{
                  showSizeChanger: false,
                  showQuickJumper: true,
                  showTotal: (total) => `共 ${total} 只股票`
                }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 添加/编辑股票弹窗 */}
      <Modal
        title={editingStock ? '编辑股票' : '添加股票'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            label="股票代码"
            name="symbol"
            rules={[{ required: true, message: '请选择股票' }]}
          >
            <Select
              showSearch
              placeholder="搜索股票代码或名称"
              loading={stockSearchLoading}
              onSearch={handleStockSearch}
              onSelect={handleStockSelect}
              notFoundContent={stockSearchLoading ? <Spin size="small" /> : '暂无数据'}
              filterOption={false}
              style={{ width: '100%' }}
            >
              {stockSearchOptions.map((stock) => (
                <Option key={stock.symbol} value={stock.symbol}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Text strong>{stock.name}</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        {stock.symbol}
                      </Text>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <Text>¥{stock.currentPrice.toFixed(2)}</Text>
                      <br />
                      <Text
                        style={{
                          color: stock.change >= 0 ? '#ff4d4f' : '#52c41a',
                          fontSize: 12
                        }}
                      >
                        {stock.change >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                      </Text>
                    </div>
                  </div>
                </Option>
              ))}
            </Select>
          </Form.Item>

          {/* 显示选中股票的详细信息 */}
          {selectedStock && (
            <Card
              size="small"
              title={
                <Space>
                  <Text strong>{selectedStock.name}</Text>
                  <Text type="secondary">({selectedStock.symbol})</Text>
                </Space>
              }
              style={{ marginBottom: 16 }}
            >
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic
                    title="当前价格"
                    value={selectedStock.currentPrice}
                    formatter={(value) => `¥${Number(value).toFixed(2)}`}
                    valueStyle={{ fontSize: 14 }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="涨跌额"
                    value={selectedStock.change}
                    formatter={(value) => `${Number(value) >= 0 ? '+' : ''}${Number(value).toFixed(2)}`}
                    valueStyle={{
                      fontSize: 14,
                      color: selectedStock.change >= 0 ? '#ff4d4f' : '#52c41a'
                    }}
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="涨跌幅"
                    value={selectedStock.changePercent}
                    suffix="%"
                    formatter={(value) => `${Number(value) >= 0 ? '+' : ''}${Number(value).toFixed(2)}`}
                    valueStyle={{
                      fontSize: 14,
                      color: selectedStock.changePercent >= 0 ? '#ff4d4f' : '#52c41a'
                    }}
                  />
                </Col>
              </Row>
            </Card>
          )}

          <Form.Item
            label="持股数量"
            name="shares"
            rules={[
              { required: true, message: '请输入持股数量' },
              { type: 'number', min: 1, message: '持股数量必须大于0' }
            ]}
            help={selectedStock ? `建议整百股购买（如100、200、300股）` : undefined}
          >
            <Input
              type="number"
              placeholder="请输入持股数量"
              addonAfter="股"
              min={1}
              step={100}
            />
          </Form.Item>

          <Form.Item
            label={
              <Space>
                <span>平均成本价</span>
                {selectedStock && (
                  <Text type="secondary" style={{ fontSize: 11 }}>
                    (当前价: ¥{selectedStock.currentPrice.toFixed(2)})
                  </Text>
                )}
              </Space>
            }
            name="avgCost"
            rules={[
              { required: true, message: '请输入平均成本价' },
              { type: 'number', min: 0.01, message: '成本价必须大于0' }
            ]}
            help="请输入您的实际买入成本价"
          >
            <Input
              type="number"
              placeholder="请输入平均成本价"
              addonBefore="¥"
              step={0.01}
              min={0.01}
            />
          </Form.Item>

          {/* 预估信息 */}
          <Form.Item shouldUpdate={(prevValues, currentValues) =>
            prevValues.shares !== currentValues.shares ||
            prevValues.avgCost !== currentValues.avgCost
          }>
            {({ getFieldValue }) => {
              const shares = getFieldValue('shares')
              const avgCost = getFieldValue('avgCost')
              const totalCost = shares && avgCost ? shares * avgCost : 0

              if (totalCost > 0) {
                return (
                  <Card size="small" style={{ backgroundColor: '#f6f8fa' }}>
                    <Row gutter={16}>
                      <Col span={12}>
                        <Statistic
                          title="总投入"
                          value={totalCost}
                          formatter={(value) => `¥${Number(value).toLocaleString()}`}
                          valueStyle={{ fontSize: 14 }}
                        />
                      </Col>
                      {selectedStock && (
                        <Col span={12}>
                          <Statistic
                            title="当前市值"
                            value={shares * selectedStock.currentPrice}
                            formatter={(value) => `¥${Number(value).toLocaleString()}`}
                            valueStyle={{
                              fontSize: 14,
                              color: (shares * selectedStock.currentPrice - totalCost) >= 0 ? '#ff4d4f' : '#52c41a'
                            }}
                          />
                        </Col>
                      )}
                    </Row>
                    {selectedStock && (
                      <div style={{ marginTop: 8, textAlign: 'center' }}>
                        <Text style={{
                          color: (shares * selectedStock.currentPrice - totalCost) >= 0 ? '#ff4d4f' : '#52c41a',
                          fontSize: 12
                        }}>
                          预估盈亏: {((shares * selectedStock.currentPrice - totalCost) >= 0 ? '+' : '')}
                          ¥{(shares * selectedStock.currentPrice - totalCost).toFixed(2)}
                        </Text>
                      </div>
                    )}
                  </Card>
                )
              }
              return null
            }}
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
              <Button onClick={() => setModalVisible(false)}>
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingStock ? '更新' : '添加'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default Portfolio
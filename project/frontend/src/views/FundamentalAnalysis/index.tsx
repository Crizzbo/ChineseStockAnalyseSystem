import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Table,
  Tag,
  Space,
  Button,
  Select,
  Input,
  message,
  Spin,
  Descriptions,
  Divider,
  Alert,
  Radio,
  Tabs
} from 'antd'
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  SearchOutlined,
  ReloadOutlined,
  RiseOutlined,
  FallOutlined,
  LineChartOutlined
} from '@ant-design/icons'
import api from '@/services/api'
import { BALANCE_SHEET_FIELDS, PROFIT_STATEMENT_FIELDS, CASHFLOW_STATEMENT_FIELDS } from '@/utils/financialStatementFields'
import './FundamentalAnalysis.scss'

const { Search } = Input
const { TabPane } = Tabs

interface FundamentalData {
  symbol: string
  name: string
  current_price: number
  profitability: any
  solvency: any
  growth: any
  valuation: any
  overall_score: any
  recommendation: any
  timestamp: string
}

const FundamentalAnalysis: React.FC = () => {
  const { symbol: urlSymbol } = useParams<{ symbol: string }>()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(false)
  const [searchSymbol, setSearchSymbol] = useState(urlSymbol || '')
  const [fundamentalData, setFundamentalData] = useState<FundamentalData | null>(null)
  const [statementType, setStatementType] = useState<'balance' | 'profit' | 'cashflow'>('balance')
  const [statementData, setStatementData] = useState<any[]>([])
  const [statementLoading, setStatementLoading] = useState(false)
  const [selectedPeriods, setSelectedPeriods] = useState<string[]>([])
  const [groupMode, setGroupMode] = useState<'period' | 'year' | 'quarter'>('period')

  useEffect(() => {
    if (urlSymbol) {
      setSearchSymbol(urlSymbol)
      fetchFundamentalData(urlSymbol)
      fetchStatementData(urlSymbol, statementType)
    }
  }, [urlSymbol])

  const fetchStatementData = async (symbol: string, type: 'balance' | 'profit' | 'cashflow') => {
    if (!symbol || symbol.trim() === '') {
      message.warning('请输入有效的股票代码')
      return
    }

    setStatementLoading(true)
    try {
      // 先尝试让后端按 groupMode 聚合（若后端支持）
      const res: any = await api.get(`/fundamental/${symbol.trim()}/financial-statements?type=${type}&group=${groupMode}`)
      const response = res?.data || res

      // 后端可能直接返回聚合后的 statements_aggregated 或 statements
      if (response.statements_aggregated && Array.isArray(response.statements_aggregated)) {
        setStatementData(response.statements_aggregated)
      } else {
        const stmts = response.statements || []
        if (stmts.length === 0) {
          message.warning('未找到该股票的财务报表数据')
          setStatementData([])
          return
        }
        // 如果后端没有聚合且用户请求了 year/quarter，则在前端进行聚合
        if (groupMode !== 'period') {
          const aggregated = aggregateStatements(groupMode, stmts)
          setStatementData(aggregated)
        } else {
          setStatementData(stmts)
        }
        // 默认选中最近 5 期（或全部小于5）
        const defaultCount = Math.min(5, stmts.length)
        setSelectedPeriods(Array.from({ length: defaultCount }).map((_, i) => String(i)))
      }
      message.success('财务报表数据加载成功')
    } catch (error: any) {
      console.error('获取财务报表数据失败:', error)
      message.error(error?.response?.data?.message || '获取财务报表数据失败')
      setStatementData([])
    } finally {
      setStatementLoading(false)
    }
  }

  // 前端聚合：将原始报告期按年份或季度汇总（简单相加数值字段）
  const aggregateStatements = (mode: 'year' | 'quarter', rawStatements: any[]) => {
    if (!rawStatements || rawStatements.length === 0) return []
    const map = new Map<string, any>()

    rawStatements.forEach((s) => {
      const rd = s.REPORT_DATE || ''
      // 解析分组键
      let bucketKey = ''
      let label = ''
      if (mode === 'year') {
        const year = typeof rd === 'string' && rd.length >= 4 ? rd.substring(0, 4) : (s.REPORT_DATE_NAME || '').match(/(\d{4})/)?.[1]
        bucketKey = String(year)
        label = `${year} 年报`
      } else {
        const year = typeof rd === 'string' && rd.length >= 4 ? rd.substring(0, 4) : (s.REPORT_DATE_NAME || '').match(/(\d{4})/)?.[1]
        const month = typeof rd === 'string' && rd.length >= 7 ? parseInt(rd.substring(5, 7), 10) : undefined
        const quarter = month ? Math.floor((month - 1) / 3) + 1 : ((s.REPORT_DATE_NAME || '').match(/Q(\d)/)?.[1] || '1')
        bucketKey = `${year}-Q${quarter}`
        label = `${year} Q${quarter}`
      }

      if (!map.has(bucketKey)) {
        map.set(bucketKey, { REPORT_DATE_NAME: label, REPORT_DATE: s.REPORT_DATE || '', __count: 0 })
      }

      const agg = map.get(bucketKey)
      agg.__count = (agg.__count || 0) + 1
      // 合并数值字段
      Object.keys(s).forEach((k) => {
        const v = s[k]
        if (typeof v === 'number') {
          agg[k] = (agg[k] || 0) + v
        } else if (agg[k] === undefined) {
          agg[k] = v
        }
      })
      // 保持最新的 REPORT_DATE 用于排序
      if (!agg._latestDate || (s.REPORT_DATE && s.REPORT_DATE > agg._latestDate)) {
        agg._latestDate = s.REPORT_DATE
      }
    })

    const arr = Array.from(map.values())
    // 按最近日期降序
    arr.sort((a, b) => (b._latestDate || '').localeCompare(a._latestDate || ''))
    return arr
  }

  const fetchFundamentalData = async (symbol: string) => {
    if (!symbol || symbol.trim() === '') {
      message.warning('请输入股票代码')
      return
    }

    setLoading(true)
    try {
      const res: any = await api.get(`/fundamental/${symbol.trim()}`)
      const response = res?.data || res
      setFundamentalData(response)
      message.success('基本面分析数据加载成功')
    } catch (error: any) {
      message.error(error?.response?.data?.message || '获取基本面分析数据失败')
      setFundamentalData(null)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (value: string) => {
    const symbol = value.trim()
    if (!symbol) {
      message.warning('请输入股票代码')
      return
    }
    // 简单的股票代码格式验证
    if (!/^\d{6}$/.test(symbol)) {
      message.warning('请输入正确格式的股票代码(6位数字)')
      return
    }
    navigate(`/fundamental/${symbol}`)
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a'
    if (score >= 60) return '#1890ff'
    if (score >= 40) return '#faad14'
    return '#f5222d'
  }

  const getRecommendationColor = (recommendation: string) => {
    if (recommendation === '买入') return 'success'
    if (recommendation === '观望') return 'warning'
    return 'error'
  }

  const handleStatementTypeChange = (type: string) => {
    const newType = type as 'balance' | 'profit' | 'cashflow'
    setStatementType(newType)
    if (!searchSymbol) {
      message.info('请先输入股票代码')
      return
    }
    fetchStatementData(searchSymbol, newType)
    message.info(`正在加载${newType === 'balance' ? '资产负债表' : newType === 'profit' ? '利润表' : '现金流量表'}数据...`)
  }

  const formatNumber = (value: any) => {
    if (value === null || value === undefined || value === '') return '--'
    const num = typeof value === 'number' ? value : parseFloat(value)
    if (isNaN(num)) return '--'
    // 转换为亿元并保留2位小数
    return (num / 100000000).toFixed(2)
  }

  const formatPeriodTitle = (statement: any, idx: number) => {
    const raw = statement.REPORT_DATE_NAME || statement.REPORT_DATE || ''
    if (statement.REPORT_DATE_NAME) return statement.REPORT_DATE_NAME
    if (typeof raw === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(raw)) {
      const year = raw.substring(0, 4)
      if (raw.endsWith('-12-31')) return `${year} 年报`
      const month = parseInt(raw.substring(5, 7), 10)
      const quarter = Math.floor((month - 1) / 3) + 1
      return `${year} Q${quarter}`
    }
    if (typeof raw === 'string' && /^(\d{4})Q(\d)$/.test(raw)) {
      const m = raw.match(/^(\d{4})Q(\d)$/)
      if (m) return `${m[1]} Q${m[2]}`
    }
    return `第${idx + 1}期`
  }

  // 构建不同分组模式下的期次选项
  const buildOptionsForMode = (mode: typeof groupMode) => {
    if (!statementData || statementData.length === 0) return []
    if (mode === 'period') {
      return statementData.map((s: any, idx: number) => ({ label: formatPeriodTitle(s, idx), value: String(idx) }))
    }

    if (mode === 'year') {
      // 只选年报（报告期为 12-31 或 REPORT_DATE_NAME 包含 年报）
      return statementData
        .map((s: any, idx: number) => ({ s, idx }))
        .filter(({ s }) => {
          const rd = s.REPORT_DATE || ''
          const rdn = s.REPORT_DATE_NAME || ''
          return (typeof rd === 'string' && rd.endsWith('-12-31')) || (typeof rdn === 'string' && rdn.includes('年报'))
        })
        .map(({ s, idx }) => ({ label: formatPeriodTitle(s, idx), value: String(idx) }))
    }

    // quarter 模式：排除年报，保留季度/非年报的项
    return statementData
      .map((s: any, idx: number) => ({ s, idx }))
      .filter(({ s }) => {
        const rd = s.REPORT_DATE || ''
        const rdn = s.REPORT_DATE_NAME || ''
        const isYearEnd = (typeof rd === 'string' && rd.endsWith('-12-31')) || (typeof rdn === 'string' && rdn.includes('年报'))
        return !isYearEnd
      })
      .map(({ s, idx }) => ({ label: formatPeriodTitle(s, idx), value: String(idx) }))
  }

  // 当 statementData 或 groupMode 变化时，若未选择任何期次则默认选择最近几项
  useEffect(() => {
    const opts = buildOptionsForMode(groupMode)
    if ((!selectedPeriods || selectedPeriods.length === 0) && opts.length > 0) {
      const defaultCount = Math.min(5, opts.length)
      setSelectedPeriods(opts.slice(0, defaultCount).map((o: any) => o.value))
    }
  }, [statementData, groupMode])

  const renderFinancialStatement = () => {
    let fields: any[] = []
    let title = ''

    if (statementType === 'balance') {
      title = '资产负债表'
      const { assets, liabilities, equity } = BALANCE_SHEET_FIELDS
      fields = [
        ...assets.map(f => ({ ...f, section: '资产' })),
        ...liabilities.map(f => ({ ...f, section: '负债' })),
        ...equity.map(f => ({ ...f, section: '所有者权益' }))
      ]
    } else if (statementType === 'profit') {
      title = '利润表'
      fields = PROFIT_STATEMENT_FIELDS
    } else {
      title = '现金流量表'
      fields = CASHFLOW_STATEMENT_FIELDS
    }

    // 构建表格列 - 科目名称 + 最多5个报告期
    const columns: any[] = [
      {
        title: '科目',
        dataIndex: 'label',
        key: 'label',
        fixed: 'left',
        width: 200,
        render: (text: string, record: any) => (
          <span style={{ fontWeight: record.isBold ? 'bold' : 'normal' }}>
            {text}
          </span>
        )
      }
    ]

    // 添加报告期列（使用用户选择的期次）
    if (statementData && statementData.length > 0) {
      // 如果用户没有选择任何期次，则默认使用最近 5 期
      const periodKeys = selectedPeriods && selectedPeriods.length > 0
        ? selectedPeriods
        : statementData.slice(0, 5).map((_: any, i: number) => String(i))

      periodKeys.forEach((k: string) => {
        const index = parseInt(k, 10)
        const statement = statementData[index]
        columns.push({
          title: formatPeriodTitle(statement, index),
          dataIndex: `period_${index}`,
          key: `period_${index}`,
          align: 'right',
          width: 120,
          render: (value: any, record: any) => (
            <span style={{ fontWeight: record.isBold ? 'bold' : 'normal' }}>
              {value}
            </span>
          )
        })
      })
    } else {
      // 没有数据时显示占位列
      for (let i = 0; i < 3; i++) {
        columns.push({
          title: `报告期${i + 1}`,
          dataIndex: `period_${i}`,
          key: `period_${i}`,
          align: 'right',
          width: 120
        })
      }
    }

    // 构建表格数据（支持分节显示）
    const dataSource: any[] = []
    let lastSection: string | undefined = undefined

    fields.forEach((field: any, index: number) => {
      const section = field.section || field.category

      // 在每个新节前插入一个节头行
      if (section && section !== lastSection) {
        dataSource.push({
          key: `section_${section}_${index}`,
          label: section,
          isSection: true,
        })
        lastSection = section
      }

      const row: any = {
        key: `row_${index}`,
        label: field.label,
        isBold: field.isBold,
        isTotal: field.isTotal
      }

      if (statementData && statementData.length > 0) {
        statementData.slice(0, 5).forEach((statement, periodIndex) => {
          row[`period_${periodIndex}`] = formatNumber(statement[field.key])
        })
      } else {
        for (let i = 0; i < 3; i++) {
          row[`period_${i}`] = '--'
        }
      }

      dataSource.push(row)
    })

    const extraEl = (
      <Space size={12}>
        <Tabs activeKey={statementType} onChange={handleStatementTypeChange} size="small">
          <Tabs.TabPane tab="资产负债表" key="balance" />
          <Tabs.TabPane tab="利润表" key="profit" />
          <Tabs.TabPane tab="现金流量表" key="cashflow" />
        </Tabs>
      </Space>
    )

    return (
      <Card
        title={title}
        className="financial-data-card"
        style={{ marginBottom: 16 }}
        extra={extraEl}
      >
        {!fundamentalData && (
          <Alert
            message="请输入股票代码查询财务报表数据"
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}
        {renderPeriodSelector()}
        <Spin spinning={statementLoading}>
          <div className="table-meta" style={{ marginBottom: 8, color: '#666', fontSize: 12 }}>
            单位：亿元（财务数据已换算）
          </div>
          <Table
            columns={columns}
            dataSource={dataSource}
            pagination={false}
            scroll={{ x: 'max-content', y: 600 }}
            size="small"
            bordered
            rowClassName={(record: any) => record.isSection ? 'section-row' : record.isTotal ? 'total-row' : ''}
            // 自定义渲染：当为节头行时，跨列显示更突出（通过样式控制）
            components={{
              body: {
                row: (props: any) => <tr {...props} />
              }
            }}
          />
        </Spin>
      </Card>
    )
  }

  // 渲染期次选择控件
  const renderPeriodSelector = () => {
    const opts = buildOptionsForMode(groupMode)
    const disabled = opts.length === 0

    return (
      <Space>
        <Radio.Group 
          value={groupMode} 
          onChange={(e) => {
            setGroupMode(e.target.value);
            if (searchSymbol) {
              fetchStatementData(searchSymbol, statementType);
              message.info(`正在按${e.target.value === 'period' ? '报告期' : e.target.value === 'year' ? '年份' : '季度'}重新加载数据...`);
            }
          }}
          size="small"
          optionType="button"
          buttonStyle="solid"
          disabled={!searchSymbol || loading}
        >
          <Radio.Button value="period">按报告期</Radio.Button>
          <Radio.Button value="year">按年份</Radio.Button>
          <Radio.Button value="quarter">按季度</Radio.Button>
        </Radio.Group>
        <Select
          mode="multiple"
          placeholder={disabled ? '请选择股票以加载期次' : '选择要显示的期次（可多选）'}
          value={selectedPeriods}
          onChange={(vals) => setSelectedPeriods(vals as string[])}
          options={opts}
          style={{ width: 240 }}
          maxTagCount={3}
          disabled={disabled}
          size="small"
        />
      </Space>
    )
  }

  const renderOverviewSection = () => {
    if (!fundamentalData) return null

    const { overall_score } = fundamentalData
    const totalScore = overall_score?.total_score || 0
    const dimensionScores = overall_score?.dimension_scores || {}

    return (
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <div className="score-item">
            <div className="score-label">综合评分</div>
            <Progress
              type="circle"
              percent={totalScore}
              strokeColor={getScoreColor(totalScore)}
              format={(percent) => `${percent}分`}
            />
            <div className="score-level">{overall_score?.level || '-'}</div>
          </div>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <div className="score-item">
            <div className="score-label">盈利能力</div>
            <Progress
              type="circle"
              percent={dimensionScores.profitability || 0}
              strokeColor={getScoreColor(dimensionScores.profitability || 0)}
            />
          </div>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <div className="score-item">
            <div className="score-label">偿债能力</div>
            <Progress
              type="circle"
              percent={dimensionScores.solvency || 0}
              strokeColor={getScoreColor(dimensionScores.solvency || 0)}
            />
          </div>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <div className="score-item">
            <div className="score-label">成长性</div>
            <Progress
              type="circle"
              percent={dimensionScores.growth || 0}
              strokeColor={getScoreColor(dimensionScores.growth || 0)}
            />
          </div>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <div className="score-item">
            <div className="score-label">估值</div>
            <Progress
              type="circle"
              percent={dimensionScores.valuation || 0}
              strokeColor={getScoreColor(dimensionScores.valuation || 0)}
            />
          </div>
        </Col>
      </Row>
    )
  }

  const renderProfitabilitySection = () => {
    if (!fundamentalData?.profitability) return null

    const { indicators, score, level, analysis } = fundamentalData.profitability

    return (
      <Card title="盈利能力分析" className="analysis-card">
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Alert message={analysis} type="info" showIcon />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="净资产收益率(ROE)"
              value={indicators?.roe || 0}
              suffix="%"
              precision={2}
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="总资产收益率(ROA)"
              value={indicators?.roa || 0}
              suffix="%"
              precision={2}
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="毛利率"
              value={indicators?.gross_margin || 0}
              suffix="%"
              precision={2}
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="净利率"
              value={indicators?.net_margin || 0}
              suffix="%"
              precision={2}
            />
          </Col>
          <Col span={24}>
            <div className="score-summary">
              <span>评分: </span>
              <Tag color={getScoreColor(score)}>{score}分 - {level}</Tag>
            </div>
          </Col>
        </Row>
      </Card>
    )
  }

  const renderSolvencySection = () => {
    if (!fundamentalData?.solvency) return null

    const { indicators, score, level, analysis } = fundamentalData.solvency

    return (
      <Card title="偿债能力分析" className="analysis-card">
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Alert message={analysis} type="info" showIcon />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="资产负债率"
              value={indicators?.debt_ratio || 0}
              suffix="%"
              precision={2}
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="总资产"
              value={indicators?.total_assets || 0}
              precision={0}
              suffix="亿"
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="总负债"
              value={indicators?.total_liabilities || 0}
              precision={0}
              suffix="亿"
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="净资产"
              value={indicators?.net_assets || 0}
              precision={0}
              suffix="亿"
            />
          </Col>
          <Col span={24}>
            <div className="score-summary">
              <span>评分: </span>
              <Tag color={getScoreColor(score)}>{score}分 - {level}</Tag>
            </div>
          </Col>
        </Row>
      </Card>
    )
  }

  const renderGrowthSection = () => {
    if (!fundamentalData?.growth) return null

    const { indicators, score, level, analysis } = fundamentalData.growth

    return (
      <Card title="成长性分析" className="analysis-card">
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Alert message={analysis} type="info" showIcon />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="营收增长率"
              value={indicators?.revenue_growth || 0}
              suffix="%"
              precision={2}
              prefix={indicators?.revenue_growth > 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              valueStyle={{ color: indicators?.revenue_growth > 0 ? '#3f8600' : '#cf1322' }}
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="利润增长率"
              value={indicators?.profit_growth || 0}
              suffix="%"
              precision={2}
              prefix={indicators?.profit_growth > 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              valueStyle={{ color: indicators?.profit_growth > 0 ? '#3f8600' : '#cf1322' }}
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="最新营收"
              value={indicators?.revenue_latest || 0}
              precision={0}
              suffix="亿"
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="最新利润"
              value={indicators?.profit_latest || 0}
              precision={0}
              suffix="亿"
            />
          </Col>
          <Col span={24}>
            <div className="score-summary">
              <span>评分: </span>
              <Tag color={getScoreColor(score)}>{score}分 - {level}</Tag>
            </div>
          </Col>
        </Row>
      </Card>
    )
  }

  const renderValuationSection = () => {
    if (!fundamentalData?.valuation) return null

    const { indicators, score, level, analysis } = fundamentalData.valuation

    return (
      <Card title="估值分析" className="analysis-card">
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Alert message={analysis} type="info" showIcon />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="市盈率(PE)"
              value={indicators?.pe || 0}
              precision={2}
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="市净率(PB)"
              value={indicators?.pb || 0}
              precision={2}
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="总市值"
              value={indicators?.market_cap || 0}
              precision={0}
              suffix="亿"
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="当前价格"
              value={indicators?.current_price || 0}
              precision={2}
              prefix="¥"
            />
          </Col>
          <Col span={24}>
            <div className="score-summary">
              <span>评分: </span>
              <Tag color={getScoreColor(score)}>{score}分 - {level}</Tag>
            </div>
          </Col>
        </Row>
      </Card>
    )
  }

  const renderRecommendationSection = () => {
    if (!fundamentalData?.recommendation) return null

    const { recommendation, confidence, reasons, risks, target_price_range } = fundamentalData.recommendation

    return (
      <Card title="投资建议" className="recommendation-card">
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12}>
            <div className="recommendation-item">
              <div className="label">投资建议:</div>
              <Tag color={getRecommendationColor(recommendation)} style={{ fontSize: '16px', padding: '4px 16px' }}>
                {recommendation}
              </Tag>
            </div>
          </Col>
          <Col xs={24} sm={12}>
            <div className="recommendation-item">
              <div className="label">置信度:</div>
              <Tag color={confidence === '高' ? 'success' : confidence === '中' ? 'warning' : 'default'}>
                {confidence}
              </Tag>
            </div>
          </Col>

          {target_price_range && (
            <Col span={24}>
              <Descriptions title="目标价格区间" bordered size="small">
                <Descriptions.Item label="低位">{target_price_range.low}</Descriptions.Item>
                <Descriptions.Item label="中位">{target_price_range.mid}</Descriptions.Item>
                <Descriptions.Item label="高位">{target_price_range.high}</Descriptions.Item>
              </Descriptions>
            </Col>
          )}

          {reasons && reasons.length > 0 && (
            <Col span={24}>
              <div className="reasons-section">
                <div className="section-title">主要理由:</div>
                <ul>
                  {reasons.map((reason: string, index: number) => (
                    <li key={index}>{reason}</li>
                  ))}
                </ul>
              </div>
            </Col>
          )}

          {risks && risks.length > 0 && (
            <Col span={24}>
              <div className="risks-section">
                <div className="section-title">主要风险:</div>
                <ul>
                  {risks.map((risk: string, index: number) => (
                    <li key={index}>{risk}</li>
                  ))}
                </ul>
              </div>
            </Col>
          )}
        </Row>
      </Card>
    )
  }

  return (
    <div className="fundamental-analysis-container">
      <div className="page-header">
        <h2>股票基本面分析</h2>
        <div className="search-bar">
          <Search
            placeholder="请输入股票代码(如: 000001)"
            value={searchSymbol}
            onChange={(e) => setSearchSymbol(e.target.value)}
            onSearch={handleSearch}
            enterButton={<SearchOutlined />}
            size="large"
            style={{ width: 400 }}
            loading={loading}
          />
          {fundamentalData && (
            <Button
              icon={<ReloadOutlined />}
              onClick={() => fetchFundamentalData(searchSymbol)}
              loading={loading}
              style={{ marginLeft: 8 }}
            >
              刷新
            </Button>
          )}
        </div>
      </div>

      {loading && (
        <div className="loading-container">
          <Spin size="large" tip="正在加载基本面数据..." />
        </div>
      )}

      {!loading && (
        <>
          {/* 股票信息卡片 */}
          {fundamentalData && (
            <Card className="stock-info-card" style={{ marginBottom: 16 }}>
              <Row>
                <Col>
                  <h3>{fundamentalData.name} ({fundamentalData.symbol})</h3>
                  <p style={{ color: '#888', marginTop: 8 }}>
                    当前价格: ¥{fundamentalData.current_price?.toFixed(2) || '-'}
                  </p>
                </Col>
              </Row>
            </Card>
          )}

          {/* 主要内容区域 - 左右布局 */}
          <Row gutter={16}>
            {/* 左侧：财务报表原始数据 */}
            <Col xs={24} lg={10}>
              {renderFinancialStatement()}
            </Col>

            {/* 右侧：基本面分析结果 */}
            <Col xs={24} lg={14}>
              {/* 综合评分区域 */}
              <Card title="基本面综合评分" className="overview-card">
                {fundamentalData ? (
                  <>
                    {renderOverviewSection()}
                  </>
                ) : (
                  <Row gutter={[16, 16]}>
                    <Col xs={24} sm={12} md={6}>
                      <div className="score-item">
                        <div className="score-label">综合评分</div>
                        <Progress
                          type="circle"
                          percent={0}
                          strokeColor="#d9d9d9"
                          format={() => '--'}
                        />
                        <div className="score-level">待分析</div>
                      </div>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <div className="score-item">
                        <div className="score-label">盈利能力</div>
                        <Progress type="circle" percent={0} strokeColor="#d9d9d9" format={() => '--'} />
                      </div>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <div className="score-item">
                        <div className="score-label">偿债能力</div>
                        <Progress type="circle" percent={0} strokeColor="#d9d9d9" format={() => '--'} />
                      </div>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <div className="score-item">
                        <div className="score-label">成长性</div>
                        <Progress type="circle" percent={0} strokeColor="#d9d9d9" format={() => '--'} />
                      </div>
                    </Col>
                    <Col xs={24} sm={12} md={6}>
                      <div className="score-item">
                        <div className="score-label">估值</div>
                        <Progress type="circle" percent={0} strokeColor="#d9d9d9" format={() => '--'} />
                      </div>
                    </Col>
                  </Row>
                )}
              </Card>

              {/* 详细分析卡片 */}
              <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
                <Col xs={24} lg={12}>
                  {fundamentalData ? renderProfitabilitySection() : (
                    <Card title="盈利能力分析" className="analysis-card">
                      <Row gutter={[16, 16]}>
                        <Col span={24}>
                          <Alert message="请先选择股票进行分析" type="info" showIcon />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="净资产收益率(ROE)" value="--" suffix="%" />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="总资产收益率(ROA)" value="--" suffix="%" />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="毛利率" value="--" suffix="%" />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="净利率" value="--" suffix="%" />
                        </Col>
                      </Row>
                    </Card>
                  )}
                </Col>
                <Col xs={24} lg={12}>
                  {fundamentalData ? renderSolvencySection() : (
                    <Card title="偿债能力分析" className="analysis-card">
                      <Row gutter={[16, 16]}>
                        <Col span={24}>
                          <Alert message="请先选择股票进行分析" type="info" showIcon />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="资产负债率" value="--" suffix="%" />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="总资产" value="--" suffix="亿" />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="总负债" value="--" suffix="亿" />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="净资产" value="--" suffix="亿" />
                        </Col>
                      </Row>
                    </Card>
                  )}
                </Col>
                <Col xs={24} lg={12}>
                  {fundamentalData ? renderGrowthSection() : (
                    <Card title="成长性分析" className="analysis-card">
                      <Row gutter={[16, 16]}>
                        <Col span={24}>
                          <Alert message="请先选择股票进行分析" type="info" showIcon />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="营收增长率" value="--" suffix="%" />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="利润增长率" value="--" suffix="%" />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="最新营收" value="--" suffix="亿" />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="最新利润" value="--" suffix="亿" />
                        </Col>
                      </Row>
                    </Card>
                  )}
                </Col>
                <Col xs={24} lg={12}>
                  {fundamentalData ? renderValuationSection() : (
                    <Card title="估值分析" className="analysis-card">
                      <Row gutter={[16, 16]}>
                        <Col span={24}>
                          <Alert message="请先选择股票进行分析" type="info" showIcon />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="市盈率(PE)" value="--" />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="市净率(PB)" value="--" />
                        </Col>
                        <Col xs={12} sm={6}>
                          <Statistic title="总市值" value="--" suffix="亿" />
                        </Col>
                        <Col xs={24} sm={6}>
                          <Statistic title="当前价格" value="--" prefix="¥" />
                        </Col>
                      </Row>
                    </Card>
                  )}
                </Col>
              </Row>

              {/* 投资建议区域 */}
              <div style={{ marginTop: 16 }}>
                {fundamentalData ? renderRecommendationSection() : (
                  <Card title="投资建议" className="recommendation-card">
                    <Row gutter={[16, 16]}>
                      <Col span={24}>
                        <Alert
                          message="系统将基于多维度财务指标和市场估值,为您提供专业的投资建议"
                          description="请输入股票代码并完成分析后,这里将显示投资建议、目标价格区间、主要理由和风险提示"
                          type="info"
                          showIcon
                        />
                      </Col>
                      <Col xs={24} sm={12}>
                        <div className="recommendation-item">
                          <div className="label">投资建议:</div>
                          <Tag color="default" style={{ fontSize: '16px', padding: '4px 16px' }}>
                            待分析
                          </Tag>
                        </div>
                      </Col>
                      <Col xs={24} sm={12}>
                        <div className="recommendation-item">
                          <div className="label">置信度:</div>
                          <Tag color="default">--</Tag>
                        </div>
                      </Col>
                    </Row>
                  </Card>
                )}
              </div>
            </Col>
          </Row>
        </>
      )}
    </div>
  )
}

export default FundamentalAnalysis

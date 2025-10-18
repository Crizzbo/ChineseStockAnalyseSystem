/**
 * 财务报表字段映射配置
 * 由于AkShare返回的字段有300+,这里只映射最重要的科目
 */

// 资产负债表主要科目
export const BALANCE_SHEET_FIELDS = {
  // 资产类
  assets: [
    { key: 'MONETARYFUNDS', label: '货币资金' },
    { key: 'ACCOUNTS_RECE', label: '应收账款' },
    { key: 'NOTE_RECE', label: '应收票据' },
    { key: 'INVENTORY', label: '存货' },
    { key: 'TOTAL_CURRENT_ASSETS', label: '流动资产合计', isBold: true },
    { key: 'FIXED_ASSET', label: '固定资产' },
    { key: 'INTANGIBLE_ASSET', label: '无形资产' },
    { key: 'GOODWILL', label: '商誉' },
    { key: 'LONG_EQUITY_INVEST', label: '长期股权投资' },
    { key: 'TOTAL_NONCURRENT_ASSETS', label: '非流动资产合计', isBold: true },
    { key: 'TOTAL_ASSETS', label: '资产总计', isBold: true, isTotal: true },
  ],
  // 负债类
  liabilities: [
    { key: 'SHORT_LOAN', label: '短期借款' },
    { key: 'ACCOUNTS_PAYABLE', label: '应付账款' },
    { key: 'NOTE_PAYABLE', label: '应付票据' },
    { key: 'TOTAL_CURRENT_LIAB', label: '流动负债合计', isBold: true },
    { key: 'LONG_LOAN', label: '长期借款' },
    { key: 'BOND_PAYABLE', label: '应付债券' },
    { key: 'TOTAL_NONCURRENT_LIAB', label: '非流动负债合计', isBold: true },
    { key: 'TOTAL_LIABILITIES', label: '负债合计', isBold: true, isTotal: true },
  ],
  // 所有者权益类
  equity: [
    { key: 'SHARE_CAPITAL', label: '股本' },
    { key: 'CAPITAL_RESERVE', label: '资本公积' },
    { key: 'SURPLUS_RESERVE', label: '盈余公积' },
    { key: 'UNASSIGN_RPOFIT', label: '未分配利润' },
    { key: 'TOTAL_PARENT_EQUITY', label: '归属于母公司所有者权益合计', isBold: true },
    { key: 'MINORITY_EQUITY', label: '少数股东权益' },
    { key: 'TOTAL_EQUITY', label: '所有者权益合计', isBold: true, isTotal: true },
  ],
}

// 利润表主要科目
export const PROFIT_STATEMENT_FIELDS = [
  { key: 'TOTAL_OPERATE_INCOME', label: '营业总收入', isBold: true },
  { key: 'OPERATE_INCOME', label: '营业收入' },
  { key: 'TOTAL_OPERATE_COST', label: '营业总成本', isBold: true },
  { key: 'OPERATE_COST', label: '营业成本' },
  { key: 'SALE_EXPENSE', label: '销售费用' },
  { key: 'MANAGE_EXPENSE', label: '管理费用' },
  { key: 'RESEARCH_EXPENSE', label: '研发费用' },
  { key: 'FINANCE_EXPENSE', label: '财务费用' },
  { key: 'OPERATE_PROFIT', label: '营业利润', isBold: true },
  { key: 'NONBUSINESS_INCOME', label: '营业外收入' },
  { key: 'NONBUSINESS_EXPENSE', label: '营业外支出' },
  { key: 'TOTAL_PROFIT', label: '利润总额', isBold: true },
  { key: 'INCOME_TAX', label: '所得税费用' },
  { key: 'NETPROFIT', label: '净利润', isBold: true, isTotal: true },
  { key: 'PARENT_NETPROFIT', label: '归属于母公司所有者的净利润', isBold: true },
  { key: 'BASIC_EPS', label: '基本每股收益' },
  { key: 'DILUTED_EPS', label: '稀释每股收益' },
]

// 现金流量表主要科目
export const CASHFLOW_STATEMENT_FIELDS = [
  // 经营活动
  { key: 'SALES_SERVICES', label: '销售商品、提供劳务收到的现金', category: '经营活动' },
  { key: 'OPERATE_CASH_IN_OTHER', label: '经营活动现金流入小计', isBold: true },
  { key: 'BUY_SERVICES', label: '购买商品、接受劳务支付的现金' },
  { key: 'PAY_STAFF_CASH', label: '支付给职工以及为职工支付的现金' },
  { key: 'PAY_ALL_TAX', label: '支付的各项税费' },
  { key: 'OPERATE_CASH_OUT_OTHER', label: '经营活动现金流出小计', isBold: true },
  { key: 'NETCASH_OPERATE', label: '经营活动产生的现金流量净额', isBold: true, isTotal: true },

  // 投资活动
  { key: 'WITHDRAW_INVEST', label: '收回投资收到的现金', category: '投资活动' },
  { key: 'RECEIVE_INVEST_INCOME', label: '取得投资收益收到的现金' },
  { key: 'INVEST_CASH_IN_OTHER', label: '投资活动现金流入小计', isBold: true },
  { key: 'CONSTRUCT_LONG_ASSET', label: '购建固定资产、无形资产和其他长期资产支付的现金' },
  { key: 'INVEST_PAY_CASH', label: '投资支付的现金' },
  { key: 'INVEST_CASH_OUT_OTHER', label: '投资活动现金流出小计', isBold: true },
  { key: 'NETCASH_INVEST', label: '投资活动产生的现金流量净额', isBold: true, isTotal: true },

  // 筹资活动
  { key: 'ACCEPT_INVEST_CASH', label: '吸收投资收到的现金', category: '筹资活动' },
  { key: 'RECEIVE_LOAN_CASH', label: '取得借款收到的现金' },
  { key: 'FINANCE_CASH_IN_OTHER', label: '筹资活动现金流入小计', isBold: true },
  { key: 'PAY_DEBT_CASH', label: '偿还债务支付的现金' },
  { key: 'ASSIGN_DIVIDEND_PORFIT', label: '分配股利、利润或偿付利息支付的现金' },
  { key: 'FINANCE_CASH_OUT_OTHER', label: '筹资活动现金流出小计', isBold: true },
  { key: 'NETCASH_FINANCE', label: '筹资活动产生的现金流量净额', isBold: true, isTotal: true },

  // 汇率变动
  { key: 'RATE_CHANGE_EFFECT', label: '汇率变动对现金的影响' },
  { key: 'CCE_ADD', label: '现金及现金等价物净增加额', isBold: true, isTotal: true },
]

export interface FinancialField {
  key: string
  label: string
  isBold?: boolean
  isTotal?: boolean
  category?: string
}

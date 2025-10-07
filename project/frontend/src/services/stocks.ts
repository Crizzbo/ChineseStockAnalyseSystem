/**
 * 股票数据相关API服务
 */
import api, { type StockInfo, type StockPriceData, type TechnicalIndicators, type MarketIndex } from './api'

export interface SearchStocksParams {
  keyword: string
  limit?: number
}

export interface StockHistoryParams {
  period?: 'daily' | 'weekly' | 'monthly'
  start_date?: string
  end_date?: string
  limit?: number
}

export interface BatchStockParams {
  symbols: string[]
}

export interface CompareStocksParams {
  symbols: string[]
}

export interface StockSearchResult {
  stocks: StockInfo[]
  total: number
  keyword: string
}

export interface StockHistoryResult {
  symbol: string
  period: string
  data: StockPriceData[]
  total: number
}

export interface StockTechnicalAnalysis {
  symbol: string
  period: string
  indicators: TechnicalIndicators
}

export interface BatchStockResult {
  stocks: StockInfo[]
  total: number
  failed_symbols: string[]
  success_count: number
  failed_count: number
}

export interface RealtimeQuotesResult {
  quotes: StockInfo[]
  total: number
  requested_symbols: string[]
  timestamp: string
}

export interface ComparisonData extends StockInfo {
  technical_indicators: TechnicalIndicators
}

export interface CompareStocksResult {
  comparison: ComparisonData[]
  total: number
  timestamp: string
}

class StocksService {
  /**
   * 搜索股票
   */
  async searchStocks(params: SearchStocksParams): Promise<StockSearchResult> {
    const queryParams = new URLSearchParams()
    queryParams.append('keyword', params.keyword)
    if (params.limit) {
      queryParams.append('limit', params.limit.toString())
    }

    return api.get(`/stocks/search?${queryParams}`)
  }

  /**
   * 获取股票基本信息
   */
  async getStockInfo(symbol: string): Promise<{ stock: StockInfo }> {
    return api.get(`/stocks/${symbol}`)
  }

  /**
   * 获取股票历史数据
   */
  async getStockHistory(symbol: string, params?: StockHistoryParams): Promise<StockHistoryResult> {
    const queryParams = new URLSearchParams()

    if (params?.period) {
      queryParams.append('period', params.period)
    }
    if (params?.start_date) {
      queryParams.append('start_date', params.start_date)
    }
    if (params?.end_date) {
      queryParams.append('end_date', params.end_date)
    }
    if (params?.limit) {
      queryParams.append('limit', params.limit.toString())
    }

    const queryString = queryParams.toString()
    const url = `/stocks/${symbol}/history${queryString ? `?${queryString}` : ''}`

    return api.get(url)
  }

  /**
   * 获取股票技术指标
   */
  async getTechnicalIndicators(symbol: string, period?: string): Promise<StockTechnicalAnalysis> {
    const queryParams = new URLSearchParams()
    if (period) {
      queryParams.append('period', period)
    }

    const queryString = queryParams.toString()
    const url = `/stocks/${symbol}/technical${queryString ? `?${queryString}` : ''}`

    return api.get(url)
  }

  /**
   * 获取热门股票
   */
  async getHotStocks(limit?: number): Promise<{ stocks: StockInfo[]; total: number }> {
    const queryParams = new URLSearchParams()
    if (limit) {
      queryParams.append('limit', limit.toString())
    }

    const queryString = queryParams.toString()
    const url = `/stocks/hot${queryString ? `?${queryString}` : ''}`

    return api.get(url)
  }

  /**
   * 批量获取股票信息
   */
  async getBatchStockInfo(params: BatchStockParams): Promise<BatchStockResult> {
    return api.post('/stocks/batch', params)
  }

  /**
   * 获取实时行情
   */
  async getRealtimeQuotes(symbols: string[]): Promise<RealtimeQuotesResult> {
    const symbolsStr = symbols.join(',')
    return api.get(`/stocks/realtime/${symbolsStr}`)
  }

  /**
   * 股票对比分析
   */
  async compareStocks(params: CompareStocksParams): Promise<CompareStocksResult> {
    return api.post('/stocks/compare', params)
  }
}

export const stocksService = new StocksService()
export default stocksService
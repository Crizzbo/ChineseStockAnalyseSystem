/**
 * 股票板块数据相关API服务
 */
import api from './api'

export interface SectorInfo {
  rank: number
  code: string
  name: string
  currentPrice: number
  change: number
  changePercent: number
  volume: number
  turnover: number
  totalTurnover: number
  turnoverRate: number
  stockCount: number
  upCount: number
  downCount: number
  leadingStock: string
  leadingStockChange: number
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
  marketCap: number | null
  pe?: number | null
  pb?: number | null
  turnoverRate?: number | null
  amplitude?: number | null
  highest?: number | null
  lowest?: number | null
}

export interface SectorsResult {
  sectors: SectorInfo[]
  total: number
  timestamp: string
}

export interface SectorStocksResult {
  sector_code: string
  sector_name?: string
  stocks: SectorStock[]
  total: number
  totalVolume: number
  totalTurnover: number
  timestamp: string | null
}

export interface SectorAnalysis {
  sector_code: string
  sector_name: string
  trend_analysis: {
    short_term: 'bullish' | 'bearish' | 'neutral'
    medium_term: 'bullish' | 'bearish' | 'neutral'
    long_term: 'bullish' | 'bearish' | 'neutral'
  }
  performance: {
    today: number
    week: number
    month: number
    quarter: number
    year: number
  }
  risk_level: 'low' | 'medium' | 'high'
  recommendation: string
}

class SectorsService {
  /**
   * 获取所有板块列表
   */
  async getSectors(limit?: number): Promise<SectorsResult> {
    const queryParams = new URLSearchParams()
    if (limit) {
      queryParams.append('limit', limit.toString())
    }

    const queryString = queryParams.toString()
    const url = `/sectors${queryString ? `?${queryString}` : ''}`

    return api.get(url)
  }

  /**
   * 获取板块详细信息
   */
  async getSectorInfo(sectorCode: string): Promise<{ sector: SectorInfo }> {
    return api.get(`/sectors/${sectorCode}`)
  }

  /**
   * 获取板块成分股
   */
  async getSectorStocks(sectorCode: string): Promise<SectorStocksResult> {
    return api.get(`/sectors/${sectorCode}/stocks`)
  }

  /**
   * 获取热门板块
   */
  async getHotSectors(limit?: number): Promise<{ sectors: SectorInfo[]; total: number }> {
    const queryParams = new URLSearchParams()
    if (limit) {
      queryParams.append('limit', limit.toString())
    }

    const queryString = queryParams.toString()
    const url = `/sectors/hot${queryString ? `?${queryString}` : ''}`

    return api.get(url)
  }

  /**
   * 搜索板块
   */
  async searchSectors(keyword: string, limit?: number): Promise<{ sectors: SectorInfo[]; total: number; keyword: string }> {
    const queryParams = new URLSearchParams()
    queryParams.append('keyword', keyword)
    if (limit) {
      queryParams.append('limit', limit.toString())
    }

    const url = `/sectors/search?${queryParams}`
    return api.get(url)
  }

  /**
   * 获取板块分析
   */
  async getSectorAnalysis(sectorCode: string): Promise<{ analysis: SectorAnalysis }> {
    return api.get(`/sectors/${sectorCode}/analysis`)
  }

  /**
   * 获取板块排行榜
   */
  async getSectorRanking(
    sortBy: 'changePercent' | 'change' | 'volume' | 'turnover' = 'changePercent',
    order: 'asc' | 'desc' = 'desc',
    limit?: number
  ): Promise<{ sectors: SectorInfo[]; total: number }> {
    const queryParams = new URLSearchParams()
    queryParams.append('sort_by', sortBy)
    queryParams.append('order', order)
    if (limit) {
      queryParams.append('limit', limit.toString())
    }

    const url = `/sectors/ranking?${queryParams}`
    return api.get(url)
  }
}

export const sectorsService = new SectorsService()
export default sectorsService
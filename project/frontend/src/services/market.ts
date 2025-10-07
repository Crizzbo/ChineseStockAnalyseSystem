/**
 * 市场数据相关API服务
 */
import api, { type MarketIndex } from './api'
import { apiCache, cacheWrapper } from '@utils/cache'
import { measureApiCall } from '@utils/performance'

export interface MarketOverview {
  indices: MarketIndex[]
  hot_stocks: any[]
  market_stats: {
    total_indices: number
    hot_stocks_count: number
    update_time: string
    indices_rising?: number
    indices_falling?: number
    indices_unchanged?: number
  }
}

export interface MarketSector {
  name: string
  code: string
  change_percent: number
  stocks_count: number
  market_cap: number
}

export interface MarketMover {
  type: 'gainers' | 'losers' | 'active'
  stocks: any[]
  total: number
  timestamp: string
}

export interface NewsItem {
  id: number
  title: string
  summary: string
  category: 'market' | 'policy' | 'company' | 'all'
  publish_time: string
  source: string
  url: string
}

export interface CalendarEvent {
  id: number
  date: string
  time: string
  event: string
  importance: 'high' | 'medium' | 'low'
  country: string
  forecast?: string
  previous?: string
}

class MarketService {
  /**
   * 获取主要市场指数
   */
  async getMarketIndices(): Promise<{ indices: MarketIndex[]; total: number; timestamp: string }> {
    return measureApiCall(
      'getMarketIndices',
      () => cacheWrapper(
        () => api.get('/market/indices'),
        apiCache,
        () => 'market:indices',
        60 * 1000 // 1分钟缓存
      )()
    )
  }

  /**
   * 获取市场概览
   */
  async getMarketOverview(): Promise<MarketOverview> {
    return measureApiCall(
      'getMarketOverview',
      () => cacheWrapper(
        () => api.get('/market/overview'),
        apiCache,
        () => 'market:overview',
        30 * 1000 // 30秒缓存
      )()
    )
  }

  /**
   * 获取行业板块数据
   */
  async getMarketSectors(): Promise<{ sectors: MarketSector[]; total: number; timestamp: string }> {
    return api.get('/market/sectors')
  }

  /**
   * 获取涨跌幅榜单
   */
  async getMarketMovers(type: 'gainers' | 'losers' | 'active' = 'gainers', limit = 20): Promise<MarketMover> {
    const queryParams = new URLSearchParams()
    queryParams.append('type', type)
    queryParams.append('limit', limit.toString())

    return api.get(`/market/movers?${queryParams}`)
  }

  /**
   * 获取市场新闻
   */
  async getMarketNews(limit = 10, category: 'all' | 'market' | 'policy' | 'company' = 'all'): Promise<{
    news: NewsItem[]
    total: number
    category: string
    timestamp: string
  }> {
    const queryParams = new URLSearchParams()
    queryParams.append('limit', limit.toString())
    queryParams.append('category', category)

    return api.get(`/market/news?${queryParams}`)
  }

  /**
   * 获取财经日历
   */
  async getMarketCalendar(date?: string): Promise<{
    date: string
    events: CalendarEvent[]
    total: number
  }> {
    const queryParams = new URLSearchParams()
    if (date) {
      queryParams.append('date', date)
    }

    const queryString = queryParams.toString()
    const url = `/market/calendar${queryString ? `?${queryString}` : ''}`

    return api.get(url)
  }
}

export const marketService = new MarketService()
export default marketService
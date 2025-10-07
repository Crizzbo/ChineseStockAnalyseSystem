/**
 * 投资组合相关API服务
 */
import api, { type Portfolio, type PortfolioStock, type PaginatedResponse } from './api'

export interface CreatePortfolioParams {
  name: string
  description?: string
}

export interface UpdatePortfolioParams {
  name?: string
  description?: string
}

export interface AddStockParams {
  symbol: string
  name: string
  shares: number
  avg_cost: number
}

export interface UpdateStockParams {
  shares?: number
  avg_cost?: number
}

export interface WatchList {
  id: number
  name: string
  description?: string
  user_id: number
  created_at: string
  updated_at: string
  stock_count: number
  stocks?: WatchStock[]
}

export interface WatchStock {
  id: number
  watchlist_id: number
  symbol: string
  name: string
  added_price?: number
  notes?: string
  created_at: string
}

export interface CreateWatchListParams {
  name: string
  description?: string
}

export interface AddWatchStockParams {
  symbol: string
  name: string
  notes?: string
}

class PortfolioService {
  /**
   * 获取投资组合列表
   */
  async getPortfolios(page = 1, per_page = 20): Promise<PaginatedResponse<Portfolio>> {
    const queryParams = new URLSearchParams()
    queryParams.append('page', page.toString())
    queryParams.append('per_page', per_page.toString())

    return api.get(`/portfolio/?${queryParams}`)
  }

  /**
   * 创建投资组合
   */
  async createPortfolio(params: CreatePortfolioParams): Promise<{ message: string; portfolio: Portfolio }> {
    return api.post('/portfolio/', params)
  }

  /**
   * 获取投资组合详情
   */
  async getPortfolio(portfolioId: number): Promise<{ portfolio: Portfolio }> {
    return api.get(`/portfolio/${portfolioId}`)
  }

  /**
   * 更新投资组合信息
   */
  async updatePortfolio(portfolioId: number, params: UpdatePortfolioParams): Promise<{ message: string; portfolio: Portfolio }> {
    return api.put(`/portfolio/${portfolioId}`, params)
  }

  /**
   * 删除投资组合
   */
  async deletePortfolio(portfolioId: number): Promise<{ message: string }> {
    return api.delete(`/portfolio/${portfolioId}`)
  }

  /**
   * 向投资组合添加股票
   */
  async addStockToPortfolio(portfolioId: number, params: AddStockParams): Promise<{ message: string; stock: PortfolioStock }> {
    return api.post(`/portfolio/${portfolioId}/stocks`, params)
  }

  /**
   * 更新投资组合中的股票信息
   */
  async updatePortfolioStock(portfolioId: number, stockId: number, params: UpdateStockParams): Promise<{ message: string; stock: PortfolioStock }> {
    return api.put(`/portfolio/${portfolioId}/stocks/${stockId}`, params)
  }

  /**
   * 从投资组合中删除股票
   */
  async removeStockFromPortfolio(portfolioId: number, stockId: number): Promise<{ message: string }> {
    return api.delete(`/portfolio/${portfolioId}/stocks/${stockId}`)
  }

  // ==================== 自选股管理 ====================

  /**
   * 获取自选股列表
   */
  async getWatchLists(): Promise<{ watchlists: WatchList[]; total: number }> {
    return api.get('/portfolio/watchlists')
  }

  /**
   * 创建自选股列表
   */
  async createWatchList(params: CreateWatchListParams): Promise<{ message: string; watchlist: WatchList }> {
    return api.post('/portfolio/watchlists', params)
  }

  /**
   * 向自选股列表添加股票
   */
  async addStockToWatchList(watchlistId: number, params: AddWatchStockParams): Promise<{ message: string; stock: WatchStock }> {
    return api.post(`/portfolio/watchlists/${watchlistId}/stocks`, params)
  }

  /**
   * 从自选股列表中删除股票
   */
  async removeStockFromWatchList(watchlistId: number, stockId: number): Promise<{ message: string }> {
    return api.delete(`/portfolio/watchlists/${watchlistId}/stocks/${stockId}`)
  }
}

export const portfolioService = new PortfolioService()
export default portfolioService
import type { StockInfo } from '@store/modules/stocks'

const SEARCH_HISTORY_KEY = 'stock_search_history'
const MAX_HISTORY_SIZE = 50

export interface SearchHistoryItem extends StockInfo {
  searchTime: number
}

class SearchHistoryService {
  getSearchHistory(): SearchHistoryItem[] {
    try {
      const history = localStorage.getItem(SEARCH_HISTORY_KEY)
      if (history) {
        return JSON.parse(history).sort((a: SearchHistoryItem, b: SearchHistoryItem) => b.searchTime - a.searchTime)
      }
      return []
    } catch (error) {
      console.error('获取搜索历史失败:', error)
      return []
    }
  }

  addToSearchHistory(stock: StockInfo): void {
    try {
      const history = this.getSearchHistory()

      const existingIndex = history.findIndex(item => item.symbol === stock.symbol)
      if (existingIndex > -1) {
        history.splice(existingIndex, 1)
      }

      const searchItem: SearchHistoryItem = {
        ...stock,
        searchTime: Date.now()
      }

      history.unshift(searchItem)

      if (history.length > MAX_HISTORY_SIZE) {
        history.splice(MAX_HISTORY_SIZE)
      }

      localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(history))
    } catch (error) {
      console.error('保存搜索历史失败:', error)
    }
  }

  clearSearchHistory(): void {
    try {
      localStorage.removeItem(SEARCH_HISTORY_KEY)
    } catch (error) {
      console.error('清除搜索历史失败:', error)
    }
  }

  removeFromSearchHistory(symbol: string): void {
    try {
      const history = this.getSearchHistory()
      const filtered = history.filter(item => item.symbol !== symbol)
      localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(filtered))
    } catch (error) {
      console.error('删除搜索历史失败:', error)
    }
  }

  getRecentSearches(limit: number = 5): SearchHistoryItem[] {
    return this.getSearchHistory().slice(0, limit)
  }
}

export const searchHistoryService = new SearchHistoryService()
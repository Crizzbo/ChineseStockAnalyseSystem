import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'

export interface StockInfo {
  symbol: string
  name: string
  currentPrice: number
  change: number
  changePercent: number
  volume: number
  marketCap?: number
  pe?: number
  pb?: number
}

export interface StockDetail extends StockInfo {
  open: number
  high: number
  low: number
  previousClose: number
  turnoverRate: number
  totalShares: number
  floatingShares: number
}

export interface PriceData {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface StocksState {
  currentStock: StockDetail | null
  stockList: StockInfo[]
  searchResults: StockInfo[]
  priceHistory: PriceData[]
  watchList: string[]
  loading: boolean
  error: string | null
}

const initialState: StocksState = {
  currentStock: null,
  stockList: [],
  searchResults: [],
  priceHistory: [],
  watchList: JSON.parse(localStorage.getItem('watchList') || '[]'),
  loading: false,
  error: null,
}

export const fetchStockList = createAsyncThunk(
  'stocks/fetchStockList',
  async () => {
    const response = await fetch('/api/v1/stocks')
    if (!response.ok) throw new Error('获取股票列表失败')
    return await response.json()
  }
)

export const fetchStockDetail = createAsyncThunk(
  'stocks/fetchStockDetail',
  async (symbol: string) => {
    const response = await fetch(`/api/v1/stocks/${symbol}`)
    if (!response.ok) throw new Error('获取股票详情失败')
    return await response.json()
  }
)

export const searchStocks = createAsyncThunk(
  'stocks/searchStocks',
  async (keyword: string) => {
    const response = await fetch(`/api/v1/stocks/search?q=${keyword}`)
    if (!response.ok) throw new Error('搜索股票失败')
    return await response.json()
  }
)

const stocksSlice = createSlice({
  name: 'stocks',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    addToWatchList: (state, action: PayloadAction<string>) => {
      if (!state.watchList.includes(action.payload)) {
        state.watchList.push(action.payload)
        localStorage.setItem('watchList', JSON.stringify(state.watchList))
      }
    },
    removeFromWatchList: (state, action: PayloadAction<string>) => {
      state.watchList = state.watchList.filter(symbol => symbol !== action.payload)
      localStorage.setItem('watchList', JSON.stringify(state.watchList))
    },
    clearSearchResults: (state) => {
      state.searchResults = []
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchStockList.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchStockList.fulfilled, (state, action) => {
        state.loading = false
        state.stockList = action.payload
      })
      .addCase(fetchStockList.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || '获取股票列表失败'
      })
      .addCase(fetchStockDetail.fulfilled, (state, action) => {
        state.currentStock = action.payload
      })
      .addCase(searchStocks.fulfilled, (state, action) => {
        state.searchResults = action.payload
      })
  },
})

export const { clearError, addToWatchList, removeFromWatchList, clearSearchResults } = stocksSlice.actions
export default stocksSlice.reducer
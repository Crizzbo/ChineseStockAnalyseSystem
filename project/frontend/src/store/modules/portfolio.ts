import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'

export interface Holding {
  symbol: string
  name: string
  quantity: number
  avgCost: number
  currentPrice: number
  totalValue: number
  totalCost: number
  profit: number
  profitRate: number
}

export interface Transaction {
  id: string
  symbol: string
  type: 'BUY' | 'SELL'
  quantity: number
  price: number
  amount: number
  date: string
  fee?: number
}

export interface PortfolioSummary {
  totalValue: number
  totalCost: number
  totalProfit: number
  totalProfitRate: number
  dayChange: number
  dayChangeRate: number
  holdingCount: number
}

interface PortfolioState {
  holdings: Holding[]
  transactions: Transaction[]
  summary: PortfolioSummary | null
  loading: boolean
  error: string | null
}

const initialState: PortfolioState = {
  holdings: [],
  transactions: [],
  summary: null,
  loading: false,
  error: null,
}

export const fetchPortfolio = createAsyncThunk(
  'portfolio/fetchPortfolio',
  async () => {
    const response = await fetch('/api/v1/portfolio')
    if (!response.ok) throw new Error('获取投资组合失败')
    return await response.json()
  }
)

export const addTransaction = createAsyncThunk(
  'portfolio/addTransaction',
  async (transaction: Omit<Transaction, 'id'>) => {
    const response = await fetch('/api/v1/portfolio/transactions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(transaction),
    })
    if (!response.ok) throw new Error('添加交易记录失败')
    return await response.json()
  }
)

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    updateHoldingPrice: (state, action: PayloadAction<{symbol: string, price: number}>) => {
      const holding = state.holdings.find(h => h.symbol === action.payload.symbol)
      if (holding) {
        holding.currentPrice = action.payload.price
        holding.totalValue = holding.quantity * action.payload.price
        holding.profit = holding.totalValue - holding.totalCost
        holding.profitRate = (holding.profit / holding.totalCost) * 100
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchPortfolio.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchPortfolio.fulfilled, (state, action) => {
        state.loading = false
        state.holdings = action.payload.holdings
        state.transactions = action.payload.transactions
        state.summary = action.payload.summary
      })
      .addCase(fetchPortfolio.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || '获取投资组合失败'
      })
      .addCase(addTransaction.fulfilled, (state, action) => {
        state.transactions.unshift(action.payload)
      })
  },
})

export const { clearError, updateHoldingPrice } = portfolioSlice.actions
export default portfolioSlice.reducer
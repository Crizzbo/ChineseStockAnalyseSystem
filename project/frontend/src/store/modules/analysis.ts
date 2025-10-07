import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

export interface AnalysisResult {
  symbol: string
  fundamentalScore: number
  technicalScore: number
  overallScore: number
  recommendation: 'BUY' | 'HOLD' | 'SELL'
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH'
  targetPrice?: number
  aiInsights: string[]
  lastUpdated: string
}

export interface FinancialMetrics {
  revenue: number
  netIncome: number
  eps: number
  roe: number
  roa: number
  debtToEquity: number
  currentRatio: number
  quickRatio: number
}

interface AnalysisState {
  currentAnalysis: AnalysisResult | null
  financialMetrics: FinancialMetrics | null
  analysisHistory: AnalysisResult[]
  loading: boolean
  error: string | null
}

const initialState: AnalysisState = {
  currentAnalysis: null,
  financialMetrics: null,
  analysisHistory: [],
  loading: false,
  error: null,
}

export const analyzeStock = createAsyncThunk(
  'analysis/analyzeStock',
  async (symbol: string) => {
    const response = await fetch(`/api/v1/analysis/${symbol}`)
    if (!response.ok) throw new Error('分析失败')
    return await response.json()
  }
)

export const fetchFinancialMetrics = createAsyncThunk(
  'analysis/fetchFinancialMetrics',
  async (symbol: string) => {
    const response = await fetch(`/api/v1/analysis/${symbol}/financial`)
    if (!response.ok) throw new Error('获取财务指标失败')
    return await response.json()
  }
)

const analysisSlice = createSlice({
  name: 'analysis',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    clearCurrentAnalysis: (state) => {
      state.currentAnalysis = null
      state.financialMetrics = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(analyzeStock.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(analyzeStock.fulfilled, (state, action) => {
        state.loading = false
        state.currentAnalysis = action.payload
        // 添加到历史记录
        const existingIndex = state.analysisHistory.findIndex(
          item => item.symbol === action.payload.symbol
        )
        if (existingIndex >= 0) {
          state.analysisHistory[existingIndex] = action.payload
        } else {
          state.analysisHistory.unshift(action.payload)
        }
      })
      .addCase(analyzeStock.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || '分析失败'
      })
      .addCase(fetchFinancialMetrics.fulfilled, (state, action) => {
        state.financialMetrics = action.payload
      })
  },
})

export const { clearError, clearCurrentAnalysis } = analysisSlice.actions
export default analysisSlice.reducer
import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'

interface UIState {
  theme: 'light' | 'dark' | 'auto'
  sidebarCollapsed: boolean
  loading: boolean
  notifications: Array<{
    id: string
    type: 'info' | 'success' | 'warning' | 'error'
    title: string
    message: string
    timestamp: number
  }>
  activeTab: string
  chartType: 'line' | 'candlestick'
  timeRange: '1D' | '5D' | '1M' | '3M' | '6M' | '1Y' | '5Y'
}

const initialState: UIState = {
  theme: (localStorage.getItem('theme') as 'light' | 'dark' | 'auto') || 'light',
  sidebarCollapsed: JSON.parse(localStorage.getItem('sidebarCollapsed') || 'false'),
  loading: false,
  notifications: [],
  activeTab: 'overview',
  chartType: 'candlestick',
  timeRange: '1M',
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'auto'>) => {
      state.theme = action.payload
      localStorage.setItem('theme', action.payload)
    },
    toggleSidebar: (state) => {
      state.sidebarCollapsed = !state.sidebarCollapsed
      localStorage.setItem('sidebarCollapsed', JSON.stringify(state.sidebarCollapsed))
    },
    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebarCollapsed = action.payload
      localStorage.setItem('sidebarCollapsed', JSON.stringify(action.payload))
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
    addNotification: (state, action: PayloadAction<{
      type: 'info' | 'success' | 'warning' | 'error'
      title: string
      message: string
    }>) => {
      const notification = {
        id: Date.now().toString(),
        ...action.payload,
        timestamp: Date.now(),
      }
      state.notifications.unshift(notification)
      // 最多保留50条通知
      if (state.notifications.length > 50) {
        state.notifications = state.notifications.slice(0, 50)
      }
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload)
    },
    clearNotifications: (state) => {
      state.notifications = []
    },
    setActiveTab: (state, action: PayloadAction<string>) => {
      state.activeTab = action.payload
    },
    setChartType: (state, action: PayloadAction<'line' | 'candlestick'>) => {
      state.chartType = action.payload
    },
    setTimeRange: (state, action: PayloadAction<'1D' | '5D' | '1M' | '3M' | '6M' | '1Y' | '5Y'>) => {
      state.timeRange = action.payload
    },
  },
})

export const {
  setTheme,
  toggleSidebar,
  setSidebarCollapsed,
  setLoading,
  addNotification,
  removeNotification,
  clearNotifications,
  setActiveTab,
  setChartType,
  setTimeRange,
} = uiSlice.actions

export default uiSlice.reducer
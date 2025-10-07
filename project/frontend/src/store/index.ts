import { configureStore } from '@reduxjs/toolkit'
import authSlice from './modules/auth'
import stocksSlice from './modules/stocks'
import analysisSlice from './modules/analysis'
import portfolioSlice from './modules/portfolio'
import uiSlice from './modules/ui'

export const store = configureStore({
  reducer: {
    auth: authSlice,
    stocks: stocksSlice,
    analysis: analysisSlice,
    portfolio: portfolioSlice,
    ui: uiSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
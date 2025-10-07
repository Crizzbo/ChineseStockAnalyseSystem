import { Routes, Route, Navigate } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import MainLayout from '@components/layout/MainLayout'
import ErrorBoundary from '@components/common/ErrorBoundary'
import PageLoading from '@components/common/PageLoading'

// 懒加载页面组件
const Dashboard = lazy(() => import('@views/Dashboard'))
const StockAnalysis = lazy(() => import('@views/StockAnalysis'))
const Portfolio = lazy(() => import('@views/Portfolio'))
const Search = lazy(() => import('@views/Search'))
const SearchHistory = lazy(() => import('@views/SearchHistory'))
const HotStocks = lazy(() => import('@views/HotStocks'))
const Sectors = lazy(() => import('@views/Sectors'))
const AIChat = lazy(() => import('@views/AIChat'))
const Settings = lazy(() => import('@views/Settings'))
const Login = lazy(() => import('@views/Auth/Login'))
const Register = lazy(() => import('@views/Auth/Register'))

const AppRouter = () => {
  return (
    <ErrorBoundary>
      <Suspense fallback={<PageLoading type="skeleton" />}>
      <Routes>
        {/* 认证路由 */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* 主应用路由 - 开发模式:无需登录 */}
        <Route
          path="/"
          element={<MainLayout />}
        >
          {/* 默认重定向到仪表盘 */}
          <Route index element={<Navigate to="/dashboard" replace />} />

          {/* 仪表盘 */}
          <Route path="dashboard" element={<Dashboard />} />

          {/* 股票分析 */}
          <Route path="analysis" element={<StockAnalysis />} />
          <Route path="analysis/:symbol" element={<StockAnalysis />} />

          {/* 投资组合 */}
          <Route path="portfolio" element={<Portfolio />} />

          {/* 股票搜索 */}
          <Route path="search" element={<Search />} />

          {/* 搜索历史 */}
          <Route path="search-history" element={<SearchHistory />} />

          {/* 热门股票 */}
          <Route path="hot-stocks" element={<HotStocks />} />

          {/* 板块行情 */}
          <Route path="sectors" element={<Sectors />} />

          {/* AI投资助手 */}
          <Route path="ai-chat" element={<AIChat />} />

          {/* 设置 */}
          <Route path="settings" element={<Settings />} />
        </Route>

        {/* 404 页面 */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
      </Suspense>
    </ErrorBoundary>
  )
}

export default AppRouter
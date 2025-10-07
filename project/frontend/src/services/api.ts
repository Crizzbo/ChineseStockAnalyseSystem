/**
 * API 服务配置和请求封装
 */
import axios, { type AxiosResponse, AxiosError } from 'axios'
import { message } from 'antd'

// API 基础配置
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001'

// 创建 axios 实例
const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 180000, // 3分钟超时
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    const { data } = response

    // 如果是成功响应，返回数据部分
    if (data.success) {
      return data.data
    }

    // 如果返回错误信息，显示错误消息
    if (data.message) {
      message.error(data.message)
    }

    return Promise.reject(new Error(data.message || '请求失败'))
  },
  (error: AxiosError<any>) => {
    // 处理HTTP错误
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          // 未授权，清除token并跳转登录
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
          break
        case 403:
          message.error('没有权限访问此资源')
          break
        case 404:
          message.error('请求的资源不存在')
          break
        case 500:
          message.error('服务器内部错误')
          break
        default:
          message.error(data?.message || '请求失败')
      }
    } else if (error.request) {
      message.error('网络连接失败，请检查网络')
    } else {
      message.error('请求配置错误')
    }

    return Promise.reject(error)
  }
)

export default api

// 统一的API响应类型
export interface ApiResponse<T = any> {
  code: number
  success: boolean
  message: string
  data: T
  timestamp?: string
}

// 分页响应类型
export interface PaginatedResponse<T = any> {
  items: T[]
  pagination: {
    total: number
    total_pages: number
    current_page: number
    per_page: number
    has_prev: boolean
    has_next: boolean
    prev_page: number | null
    next_page: number | null
  }
}

// 股票基本信息类型
export interface StockInfo {
  symbol: string
  name: string
  currentPrice: number
  change: number
  changePercent: number
  volume: number
  turnover?: number
  high: number
  low: number
  open: number
  preClose: number
  marketCap?: number
  pe?: number
  pb?: number
}

// 股票历史数据类型
export interface StockPriceData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  turnover?: number
}

// 投资组合类型
export interface Portfolio {
  id: number
  name: string
  description?: string
  user_id: number
  total_value: number
  total_cost: number
  total_gain_loss: number
  total_gain_loss_percent: number
  created_at: string
  updated_at: string
  stocks?: PortfolioStock[]
}

// 投资组合股票类型
export interface PortfolioStock {
  id: number
  portfolio_id: number
  symbol: string
  name: string
  shares: number
  avg_cost: number
  current_price: number
  total_value: number
  gain_loss: number
  gain_loss_percent: number
  weight: number
  created_at: string
  updated_at: string
}

// 市场指数类型
export interface MarketIndex {
  symbol: string
  name: string
  currentPrice: number
  change: number
  changePercent: number
  volume: number
  turnover: number
}

// 技术指标类型
export interface TechnicalIndicators {
  ma5?: number
  ma10?: number
  ma20?: number
  ma60?: number
  rsi?: number
  volume_ratio?: number
  [key: string]: number | undefined
}

// 分析结果类型
export interface AnalysisResult {
  score: number
  signals: string[]
  recommendations: string[]
  support_resistance?: {
    support: number
    resistance: number
  }
  overall?: 'bullish' | 'bearish' | 'neutral'
}

// 用户信息类型
export interface UserInfo {
  id: number
  username: string
  email?: string
  nickname: string
  avatar?: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  updated_at: string
  last_login?: string
}
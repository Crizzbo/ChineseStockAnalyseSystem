import { API_BASE_URL } from './api'

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto'
  language: 'zh' | 'en'
  notifications: {
    priceAlerts: boolean
    portfolioUpdates: boolean
    newsAlerts: boolean
    systemNotifications: boolean
  }
  display: {
    autoRefresh: boolean
    refreshInterval: number
    showPremarket: boolean
    showAfterHours: boolean
    defaultChartType: 'line' | 'candlestick'
    priceFormat: 'absolute' | 'percentage'
  }
  trading: {
    confirmOrders: boolean
    defaultOrderType: 'market' | 'limit'
    riskWarnings: boolean
  }
}

export interface UserProfile {
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

export interface UserResponse {
  user: UserProfile
  preferences: UserPreferences
  timestamp: string
}

class UserService {
  private baseUrl = `${API_BASE_URL}/user`

  async getUserPreferences(): Promise<UserPreferences> {
    try {
      const response = await fetch(`${this.baseUrl}/preferences`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      if (!data.success) {
        throw new Error(data.message || '获取用户偏好设置失败')
      }

      return data.data.preferences
    } catch (error) {
      console.error('获取用户偏好设置失败:', error)
      // 返回默认设置
      return {
        theme: 'light',
        language: 'zh',
        notifications: {
          priceAlerts: true,
          portfolioUpdates: true,
          newsAlerts: false,
          systemNotifications: true
        },
        display: {
          autoRefresh: true,
          refreshInterval: 30,
          showPremarket: false,
          showAfterHours: false,
          defaultChartType: 'candlestick',
          priceFormat: 'absolute'
        },
        trading: {
          confirmOrders: true,
          defaultOrderType: 'market',
          riskWarnings: true
        }
      }
    }
  }

  async updateUserPreferences(preferences: Partial<UserPreferences>): Promise<UserPreferences> {
    try {
      const response = await fetch(`${this.baseUrl}/preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(preferences),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      if (!data.success) {
        throw new Error(data.message || '更新用户偏好设置失败')
      }

      return data.data.preferences
    } catch (error) {
      console.error('更新用户偏好设置失败:', error)
      throw error
    }
  }

  async resetUserPreferences(): Promise<UserPreferences> {
    try {
      const response = await fetch(`${this.baseUrl}/preferences/reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      if (!data.success) {
        throw new Error(data.message || '重置用户偏好设置失败')
      }

      return data.data.preferences
    } catch (error) {
      console.error('重置用户偏好设置失败:', error)
      throw error
    }
  }

  async getUserProfile(): Promise<UserResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/profile`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      if (!data.success) {
        throw new Error(data.message || '获取用户信息失败')
      }

      return data.data
    } catch (error) {
      console.error('获取用户信息失败:', error)
      throw error
    }
  }

  async updateUserProfile(profile: Partial<UserProfile>): Promise<UserProfile> {
    try {
      const response = await fetch(`${this.baseUrl}/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profile),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      if (!data.success) {
        throw new Error(data.message || '更新用户信息失败')
      }

      return data.data.user
    } catch (error) {
      console.error('更新用户信息失败:', error)
      throw error
    }
  }

  // 本地存储方法（作为API的补充）
  saveToLocalStorage(preferences: UserPreferences): void {
    try {
      localStorage.setItem('userPreferences', JSON.stringify(preferences))
    } catch (error) {
      console.error('保存设置到本地存储失败:', error)
    }
  }

  loadFromLocalStorage(): UserPreferences | null {
    try {
      const saved = localStorage.getItem('userPreferences')
      return saved ? JSON.parse(saved) : null
    } catch (error) {
      console.error('从本地存储加载设置失败:', error)
      return null
    }
  }

  applyTheme(theme: 'light' | 'dark' | 'auto'): void {
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark')
    } else if (theme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light')
    } else {
      // 自动模式：根据系统偏好
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light')
    }
  }
}

export const userService = new UserService()
export default userService
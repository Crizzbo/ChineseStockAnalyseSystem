/**
 * 认证相关API服务
 */
import api, { type ApiResponse, type UserInfo } from './api'

export interface LoginParams {
  login: string  // 用户名或邮箱
  password: string
}

export interface RegisterParams {
  username: string
  email: string
  password: string
  nickname?: string
}

export interface AuthResponse {
  message: string
  user: UserInfo
  access_token: string
  refresh_token: string
}

export interface ChangePasswordParams {
  old_password: string
  new_password: string
}

export interface UpdateProfileParams {
  nickname?: string
  avatar?: string
}

class AuthService {
  /**
   * 用户登录
   */
  async login(params: LoginParams): Promise<AuthResponse> {
    const response = await api.post<ApiResponse<AuthResponse>>('/auth/login', params)
    const authData = response as unknown as AuthResponse

    // 保存token到本地存储
    if (authData.access_token) {
      localStorage.setItem('access_token', authData.access_token)
      localStorage.setItem('refresh_token', authData.refresh_token)
      localStorage.setItem('user_info', JSON.stringify(authData.user))
    }

    return authData
  }

  /**
   * 用户注册
   */
  async register(params: RegisterParams): Promise<AuthResponse> {
    const response = await api.post<ApiResponse<AuthResponse>>('/auth/register', params)
    const authData = response as unknown as AuthResponse

    // 注册成功后自动保存token
    if (authData.access_token) {
      localStorage.setItem('access_token', authData.access_token)
      localStorage.setItem('refresh_token', authData.refresh_token)
      localStorage.setItem('user_info', JSON.stringify(authData.user))
    }

    return authData
  }

  /**
   * 刷新访问令牌
   */
  async refreshToken(): Promise<{ access_token: string }> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      throw new Error('No refresh token available')
    }

    // 临时设置refresh token用于请求
    const response = await api.post('/auth/refresh', {}, {
      headers: {
        Authorization: `Bearer ${refreshToken}`
      }
    })

    // 更新access token
    const tokenData = response as unknown as { access_token: string }
    localStorage.setItem('access_token', tokenData.access_token)

    return tokenData
  }

  /**
   * 用户登出
   */
  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout')
    } catch (error) {
      // 即使请求失败也要清除本地数据
      console.error('Logout request failed:', error)
    } finally {
      // 清除本地存储
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
    }
  }

  /**
   * 获取用户信息
   */
  async getProfile(): Promise<{ user: UserInfo }> {
    return api.get('/auth/profile')
  }

  /**
   * 更新用户信息
   */
  async updateProfile(params: UpdateProfileParams): Promise<{ message: string; user: UserInfo }> {
    const response = await api.put('/auth/profile', params)
    const profileData = response as unknown as { message: string; user: UserInfo }

    // 更新本地存储的用户信息
    localStorage.setItem('user_info', JSON.stringify(profileData.user))

    return profileData
  }

  /**
   * 修改密码
   */
  async changePassword(params: ChangePasswordParams): Promise<{ message: string }> {
    return api.post('/auth/change-password', params)
  }

  /**
   * 验证令牌有效性
   */
  async verifyToken(): Promise<{ valid: boolean; user: UserInfo }> {
    return api.get('/auth/verify-token')
  }

  /**
   * 检查是否已登录
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token')
    return !!token
  }

  /**
   * 获取存储的用户信息
   */
  getCurrentUser(): UserInfo | null {
    const userInfo = localStorage.getItem('user_info')
    return userInfo ? JSON.parse(userInfo) : null
  }

  /**
   * 获取访问令牌
   */
  getAccessToken(): string | null {
    return localStorage.getItem('access_token')
  }

  /**
   * 获取刷新令牌
   */
  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token')
  }
}

export const authService = new AuthService()
export default authService
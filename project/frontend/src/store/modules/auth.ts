import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import { authService } from '@/services/auth'
import type { UserInfo } from '@/services/api'

export interface User {
  id: number
  username: string
  email: string
  nickname: string
  avatar?: string
}

interface AuthState {
  user: User | null
  token: string | null
  isLoggedIn: boolean
  loading: boolean
  error: string | null
  isInitialized: boolean
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('access_token'),
  isLoggedIn: false,
  loading: false,
  error: null,
  isInitialized: false,
}

// 异步actions
export const loginAsync = createAsyncThunk(
  'auth/login',
  async (credentials: { login: string; password: string }) => {
    try {
      const result = await authService.login(credentials)
      return {
        user: result.user,
        token: result.access_token
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || error.message || '登录失败')
    }
  }
)

export const registerAsync = createAsyncThunk(
  'auth/register',
  async (userData: { username: string; email: string; password: string; nickname?: string }) => {
    try {
      const result = await authService.register(userData)
      return {
        user: result.user,
        token: result.access_token
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || error.message || '注册失败')
    }
  }
)

export const initializeAuth = createAsyncThunk(
  'auth/initialize',
  async () => {
    const token = authService.getAccessToken()
    if (!token) {
      throw new Error('未登录')
    }

    try {
      const result = await authService.getProfile()
      return {
        user: result.user,
        token
      }
    } catch (error) {
      // Token无效,清除本地存储
      await authService.logout()
      throw new Error('登录状态已过期')
    }
  }
)

export const logoutAsync = createAsyncThunk('auth/logout', async () => {
  await authService.logout()
  return null
})

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload
      state.isLoggedIn = true
    },
  },
  extraReducers: (builder) => {
    builder
      // 初始化认证状态
      .addCase(initializeAuth.pending, (state) => {
        state.loading = true
      })
      .addCase(initializeAuth.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload.user as any
        state.token = action.payload.token
        state.isLoggedIn = true
        state.isInitialized = true
      })
      .addCase(initializeAuth.rejected, (state) => {
        state.loading = false
        state.user = null
        state.token = null
        state.isLoggedIn = false
        state.isInitialized = true
      })
      // 登录
      .addCase(loginAsync.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(loginAsync.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload.user as any
        state.token = action.payload.token
        state.isLoggedIn = true
      })
      .addCase(loginAsync.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || '登录失败'
      })
      // 注册
      .addCase(registerAsync.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(registerAsync.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload.user as any
        state.token = action.payload.token
        state.isLoggedIn = true
      })
      .addCase(registerAsync.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || '注册失败'
      })
      // 登出
      .addCase(logoutAsync.fulfilled, (state) => {
        state.user = null
        state.token = null
        state.isLoggedIn = false
      })
  },
})

export const { clearError, setUser } = authSlice.actions
export default authSlice.reducer

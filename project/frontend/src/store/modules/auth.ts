import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import { mockLogin, mockRegister, mockGetCurrentUser } from '@utils/mockAuth'
import type { MockUser } from '@utils/mockAuth'

export interface User {
  id: string
  username: string
  email: string
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
  token: localStorage.getItem('token'),
  isLoggedIn: false,
  loading: false,
  error: null,
  isInitialized: false,
}

// 异步actions
export const loginAsync = createAsyncThunk(
  'auth/login',
  async (credentials: { email: string; password: string }) => {
    try {
      const result = await mockLogin(credentials.email, credentials.password)
      localStorage.setItem('token', result.token)
      return result
    } catch (error) {
      localStorage.removeItem('token')
      throw error
    }
  }
)

export const registerAsync = createAsyncThunk(
  'auth/register',
  async (userData: { username: string; email: string; password: string }) => {
    try {
      const result = await mockRegister(userData)
      localStorage.setItem('token', result.token)
      return result
    } catch (error) {
      localStorage.removeItem('token')
      throw error
    }
  }
)

export const initializeAuth = createAsyncThunk(
  'auth/initialize',
  async () => {
    const user = await mockGetCurrentUser()
    if (!user) {
      localStorage.removeItem('token')
      throw new Error('无效的登录状态')
    }
    return { user, token: localStorage.getItem('token')! }
  }
)

export const logoutAsync = createAsyncThunk('auth/logout', async () => {
  localStorage.removeItem('token')
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
        state.user = action.payload.user
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
        state.user = action.payload.user
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
        state.user = action.payload.user
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
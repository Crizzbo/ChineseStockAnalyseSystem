import { useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { App as AntApp } from 'antd'
import type { RootState, AppDispatch } from '@store/index'
import { initializeAuth } from '@store/modules/auth'
import AppRouter from './router'

function App() {
  const { theme } = useSelector((state: RootState) => state.ui)
  const dispatch = useDispatch<AppDispatch>()

  useEffect(() => {
    // 初始化认证状态
    dispatch(initializeAuth())
  }, [dispatch])

  useEffect(() => {
    // 应用主题设置
    if (theme === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark')
    } else if (theme === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
    } else {
      document.documentElement.setAttribute('data-theme', 'light')
    }
  }, [theme])

  return (
    <AntApp>
      <AppRouter />
    </AntApp>
  )
}

export default App

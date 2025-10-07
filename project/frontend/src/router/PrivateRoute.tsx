import { Navigate, useLocation } from 'react-router-dom'
import { useSelector } from 'react-redux'
import type { RootState } from '@store/index'

interface PrivateRouteProps {
  children: React.ReactNode
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
  const location = useLocation()
  const { isLoggedIn, token } = useSelector((state: RootState) => state.auth)

  // 检查是否有有效的登录状态
  const isAuthenticated = isLoggedIn && token

  if (!isAuthenticated) {
    // 保存用户试图访问的页面，登录后重定向
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <>{children}</>
}

export default PrivateRoute
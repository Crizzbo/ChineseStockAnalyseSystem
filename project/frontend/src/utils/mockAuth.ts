// 临时模拟认证系统 - 仅用于开发测试
export interface MockUser {
  id: string
  username: string
  email: string
  avatar?: string
}

// 模拟用户数据（生产环境中应该从数据库获取）
const mockUsers: Array<MockUser & { password: string }> = [
  {
    id: '1',
    username: 'admin',
    email: 'admin@stock-analysis.com',
    password: 'admin123',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin'
  },
  {
    id: '2',
    username: 'demo',
    email: 'demo@example.com',
    password: 'demo123',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=demo'
  },
  {
    id: '3',
    username: 'investor',
    email: 'investor@example.com',
    password: 'investor123',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=investor'
  }
]

// 模拟登录验证
export const mockLogin = async (email: string, password: string): Promise<{
  user: MockUser
  token: string
}> => {
  // 模拟网络延迟
  await new Promise(resolve => setTimeout(resolve, 800))

  const user = mockUsers.find(u => u.email === email && u.password === password)

  if (!user) {
    throw new Error('邮箱或密码错误')
  }

  // 生成模拟JWT token
  const token = btoa(JSON.stringify({
    userId: user.id,
    email: user.email,
    exp: Date.now() + 24 * 60 * 60 * 1000 // 24小时过期
  }))

  return {
    user: {
      id: user.id,
      username: user.username,
      email: user.email,
      avatar: user.avatar
    },
    token: `mock_token_${token}`
  }
}

// 模拟注册
export const mockRegister = async (userData: {
  username: string
  email: string
  password: string
}): Promise<{
  user: MockUser
  token: string
}> => {
  // 模拟网络延迟
  await new Promise(resolve => setTimeout(resolve, 1000))

  // 检查邮箱是否已存在
  const existingUser = mockUsers.find(u => u.email === userData.email)
  if (existingUser) {
    throw new Error('该邮箱已被注册')
  }

  // 创建新用户
  const newUser: MockUser & { password: string } = {
    id: Date.now().toString(),
    username: userData.username,
    email: userData.email,
    password: userData.password,
    avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${userData.username}`
  }

  // 添加到模拟数据库
  mockUsers.push(newUser)

  // 生成token
  const token = btoa(JSON.stringify({
    userId: newUser.id,
    email: newUser.email,
    exp: Date.now() + 24 * 60 * 60 * 1000
  }))

  return {
    user: {
      id: newUser.id,
      username: newUser.username,
      email: newUser.email,
      avatar: newUser.avatar
    },
    token: `mock_token_${token}`
  }
}

// 验证token
export const mockVerifyToken = async (token: string): Promise<MockUser | null> => {
  if (!token || !token.startsWith('mock_token_')) {
    return null
  }

  try {
    const payload = JSON.parse(atob(token.replace('mock_token_', '')))

    // 检查是否过期
    if (Date.now() > payload.exp) {
      return null
    }

    // 查找用户
    const user = mockUsers.find(u => u.id === payload.userId)
    return user ? {
      id: user.id,
      username: user.username,
      email: user.email,
      avatar: user.avatar
    } : null
  } catch {
    return null
  }
}

// 获取当前用户信息
export const mockGetCurrentUser = async (): Promise<MockUser | null> => {
  const token = localStorage.getItem('token')
  if (!token) return null

  return await mockVerifyToken(token)
}

console.log('🎭 使用模拟认证系统')
console.log('📋 测试账号：')
console.log('1. admin@stock-analysis.com / admin123')
console.log('2. demo@example.com / demo123')
console.log('3. investor@example.com / investor123')
console.log('💡 您也可以注册新账号进行测试')
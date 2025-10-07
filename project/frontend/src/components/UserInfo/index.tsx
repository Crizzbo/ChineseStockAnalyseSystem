import React from 'react'
import { Card, Typography, Button, Space, Avatar, Descriptions } from 'antd'
import { UserOutlined, LogoutOutlined } from '@ant-design/icons'
import { useSelector, useDispatch } from 'react-redux'
import type { RootState, AppDispatch } from '@store/index'
import { logoutAsync } from '@store/modules/auth'
import { useNavigate } from 'react-router-dom'

const { Title, Text } = Typography

const UserInfo: React.FC = () => {
  const { user, isLoggedIn } = useSelector((state: RootState) => state.auth)
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await dispatch(logoutAsync())
    navigate('/login')
  }

  if (!isLoggedIn || !user) {
    return (
      <Card>
        <Text type="secondary">用户未登录</Text>
      </Card>
    )
  }

  return (
    <Card
      title={<Title level={4}>用户信息</Title>}
      extra={
        <Button
          type="text"
          icon={<LogoutOutlined />}
          onClick={handleLogout}
          danger
        >
          退出登录
        </Button>
      }
    >
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ textAlign: 'center' }}>
          <Avatar
            size={64}
            src={user.avatar}
            icon={<UserOutlined />}
            style={{ marginBottom: 16 }}
          />
          <Title level={3}>{user.username}</Title>
        </div>

        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="用户ID">
            {user.id}
          </Descriptions.Item>
          <Descriptions.Item label="用户名">
            {user.username}
          </Descriptions.Item>
          <Descriptions.Item label="邮箱">
            {user.email}
          </Descriptions.Item>
          <Descriptions.Item label="登录状态">
            <Text type="success">已登录</Text>
          </Descriptions.Item>
        </Descriptions>
      </Space>
    </Card>
  )
}

export default UserInfo
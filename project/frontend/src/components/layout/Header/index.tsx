import React from 'react'
import { Layout, Button, Dropdown, Avatar, Space, Badge, Typography } from 'antd'
import {
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  BellOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons'
import { useSelector, useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import type { MenuProps } from 'antd'
import type { RootState, AppDispatch } from '@store/index'
import { toggleSidebar } from '@store/modules/ui'
import { logoutAsync } from '@store/modules/auth'
import './Header.scss'

const { Header: AntHeader } = Layout
const { Text } = Typography

const Header: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate()
  const { sidebarCollapsed, notifications } = useSelector((state: RootState) => state.ui)
  const { user } = useSelector((state: RootState) => state.auth)

  const unreadCount = notifications.length

  const handleToggleSidebar = () => {
    dispatch(toggleSidebar())
  }

  const handleLogout = () => {
    dispatch(logoutAsync())
    navigate('/login')
  }

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
      onClick: () => navigate('/settings'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '系统设置',
      onClick: () => navigate('/settings'),
    },
    {
      type: 'divider',
    },
    {
      key: 'help',
      icon: <QuestionCircleOutlined />,
      label: '帮助中心',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: handleLogout,
    },
  ]

  const notificationMenuItems: MenuProps['items'] = notifications.slice(0, 5).map((notification) => ({
    key: notification.id,
    label: (
      <div className="notification-item">
        <div className="notification-title">{notification.title}</div>
        <div className="notification-message">{notification.message}</div>
        <div className="notification-time">
          {new Date(notification.timestamp).toLocaleString()}
        </div>
      </div>
    ),
  }))

  return (
    <AntHeader className="app-header">
      <div className="header-left">
        <Button
          type="text"
          icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={handleToggleSidebar}
          className="sidebar-trigger"
        />
        <div className="breadcrumb-container">
          <Text className="page-title">股票分析系统</Text>
        </div>
      </div>

      <div className="header-right">
        <Space size="middle">
          {/* 通知 */}
          <Dropdown
            menu={{ items: notificationMenuItems }}
            placement="bottomRight"
            arrow
            trigger={['click']}
          >
            <Badge count={unreadCount} size="small">
              <Button
                type="text"
                icon={<BellOutlined />}
                className="header-action"
              />
            </Badge>
          </Dropdown>

          {/* 用户菜单 */}
          <Dropdown
            menu={{ items: userMenuItems }}
            placement="bottomRight"
            arrow
            trigger={['click']}
          >
            <div className="user-info">
              <Avatar
                size="small"
                icon={<UserOutlined />}
                src={user?.avatar}
                className="user-avatar"
              />
              <span className="username">{user?.username || '用户'}</span>
            </div>
          </Dropdown>
        </Space>
      </div>
    </AntHeader>
  )
}

export default Header
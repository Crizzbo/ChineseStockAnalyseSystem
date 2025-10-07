import React from 'react'
import { Layout, Menu, Button } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  LineChartOutlined,
  PieChartOutlined,
  SearchOutlined,
  SettingOutlined,
  StockOutlined,
  FolderOutlined,
  AppstoreOutlined,
  RobotOutlined
} from '@ant-design/icons'
import type { MenuProps } from 'antd'
import './Sidebar.scss'

const { Sider } = Layout

interface SidebarProps {
  collapsed: boolean
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed }) => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems: MenuProps['items'] = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
      onClick: () => navigate('/dashboard'),
    },
    {
      key: '/analysis',
      icon: <LineChartOutlined />,
      label: '股票分析',
      onClick: () => navigate('/analysis'),
    },
    {
      key: '/portfolio',
      icon: <PieChartOutlined />,
      label: '投资组合',
      onClick: () => navigate('/portfolio'),
    },
    {
      key: '/search',
      icon: <SearchOutlined />,
      label: '股票搜索',
      onClick: () => navigate('/search'),
    },
    {
      key: '/sectors',
      icon: <AppstoreOutlined />,
      label: '板块行情',
      onClick: () => navigate('/sectors'),
    },
    {
      key: '/ai-chat',
      icon: <RobotOutlined />,
      label: 'AI投资助手',
      onClick: () => navigate('/ai-chat'),
    },
    {
      type: 'divider',
    },
    {
      key: 'tools',
      icon: <FolderOutlined />,
      label: '工具',
      children: [
        {
          key: '/watchlist',
          icon: <StockOutlined />,
          label: '自选股',
        },
        {
          key: '/calculator',
          icon: <LineChartOutlined />,
          label: '收益计算器',
        },
      ],
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '设置',
      onClick: () => navigate('/settings'),
    },
  ]

  // 获取当前选中的菜单项
  const getSelectedKeys = () => {
    const pathname = location.pathname
    if (pathname.startsWith('/analysis')) {
      return ['/analysis']
    }
    return [pathname]
  }

  return (
    <Sider
      className="app-sidebar"
      collapsible
      collapsed={collapsed}
      trigger={null}
      width={200}
      collapsedWidth={80}
      breakpoint="lg"
      theme="light"
    >
      <div className="sidebar-header">
        <div className="logo">
          <StockOutlined className="logo-icon" />
          {!collapsed && <span className="logo-text">股票分析</span>}
        </div>
      </div>

      <Menu
        mode="inline"
        selectedKeys={getSelectedKeys()}
        className="sidebar-menu"
        items={menuItems}
      />

      {!collapsed && (
        <div className="sidebar-footer">
          <div className="footer-info">
            <div className="version">v1.0.0</div>
          </div>
        </div>
      )}
    </Sider>
  )
}

export default Sidebar
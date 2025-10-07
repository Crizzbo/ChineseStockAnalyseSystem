import React from 'react'
import { Layout } from 'antd'
import { Outlet } from 'react-router-dom'
import { useSelector } from 'react-redux'
import type { RootState } from '@store/index'
import Header from '../Header'
import Sidebar from '../Sidebar'
import Footer from '../Footer'
import './MainLayout.scss'

const { Content } = Layout

const MainLayout: React.FC = () => {
  const { sidebarCollapsed } = useSelector((state: RootState) => state.ui)

  return (
    <Layout className="main-layout">
      <Sidebar collapsed={sidebarCollapsed} />
      <Layout className={`main-content ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <Header />
        <Content className="page-content">
          <div className="content-wrapper">
            <Outlet />
          </div>
        </Content>
        <Footer />
      </Layout>
    </Layout>
  )
}

export default MainLayout
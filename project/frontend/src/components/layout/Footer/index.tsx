import React from 'react'
import { Layout } from 'antd'
import './Footer.scss'

const { Footer: AntFooter } = Layout

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear()

  return (
    <AntFooter className="app-footer">
      <div className="footer-content">
        <div className="copyright">
          © {currentYear} 股票知识分析系统. All rights reserved.
        </div>
        <div className="footer-links">
          <a href="/privacy" target="_blank" rel="noopener noreferrer">
            隐私政策
          </a>
          <a href="/terms" target="_blank" rel="noopener noreferrer">
            服务条款
          </a>
          <a href="/help" target="_blank" rel="noopener noreferrer">
            帮助中心
          </a>
        </div>
      </div>
    </AntFooter>
  )
}

export default Footer
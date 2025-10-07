import React from 'react'
import { Spin, Skeleton, Card, Row, Col } from 'antd'
import { LoadingOutlined } from '@ant-design/icons'
import './PageLoading.scss'

interface PageLoadingProps {
  type?: 'spinner' | 'skeleton'
  size?: 'small' | 'default' | 'large'
  tip?: string
}

// 自定义加载图标
const customIcon = <LoadingOutlined style={{ fontSize: 24 }} spin />

// 骨架屏组件
const SkeletonLoading: React.FC = () => (
  <div className="skeleton-loading">
    <Row gutter={[16, 16]}>
      <Col span={24}>
        <Card>
          <Skeleton active paragraph={{ rows: 2 }} />
        </Card>
      </Col>
      <Col span={12}>
        <Card>
          <Skeleton active paragraph={{ rows: 4 }} />
        </Card>
      </Col>
      <Col span={12}>
        <Card>
          <Skeleton active paragraph={{ rows: 4 }} />
        </Card>
      </Col>
      <Col span={24}>
        <Card>
          <Skeleton active paragraph={{ rows: 6 }} />
        </Card>
      </Col>
    </Row>
  </div>
)

const PageLoading: React.FC<PageLoadingProps> = ({
  type = 'spinner',
  size = 'large',
  tip = '加载中...'
}) => {
  if (type === 'skeleton') {
    return <SkeletonLoading />
  }

  return (
    <div className="page-loading">
      <div className="loading-content">
        <Spin
          indicator={customIcon}
          size={size}
          tip={tip}
        />
      </div>
    </div>
  )
}

export default PageLoading
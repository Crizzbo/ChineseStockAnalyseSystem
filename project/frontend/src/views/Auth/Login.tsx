import React, { useState } from 'react'
import { Form, Input, Button, Card, Typography, Divider, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { useDispatch } from 'react-redux'
import type { AppDispatch } from '@store/index'
import { loginAsync } from '@store/modules/auth'
import './Auth.scss'

const { Title, Text } = Typography

const Login: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate()

  const onFinish = async (values: { email: string; password: string }) => {
    try {
      setLoading(true)
      await dispatch(loginAsync(values)).unwrap()
      message.success('登录成功')
      navigate('/dashboard')
    } catch (error) {
      message.error('登录失败，请检查用户名和密码')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <Card>
          <div className="auth-header">
            <Title level={2}>登录</Title>
            <Text type="secondary">欢迎使用股票知识分析系统</Text>
          </div>

          <Form
            name="login"
            onFinish={onFinish}
            size="large"
            autoComplete="off"
          >
            <Form.Item
              name="email"
              rules={[
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '邮箱格式不正确' },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="邮箱"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="密码"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
              >
                登录
              </Button>
            </Form.Item>
          </Form>

          <Divider>
            <Text type="secondary">还没有账号？</Text>
          </Divider>

          <div className="auth-footer">
            <Link to="/register">
              <Button block>注册账号</Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default Login
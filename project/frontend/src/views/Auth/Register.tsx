import React, { useState } from 'react'
import { Form, Input, Button, Card, Typography, Divider, message } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { useDispatch } from 'react-redux'
import type { AppDispatch } from '@store/index'
import { registerAsync } from '@store/modules/auth'
import './Auth.scss'

const { Title, Text } = Typography

const Register: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const dispatch = useDispatch<AppDispatch>()

  const onFinish = async (values: {
    username: string
    email: string
    password: string
    confirmPassword: string
  }) => {
    try {
      setLoading(true)
      await dispatch(registerAsync({
        username: values.username,
        email: values.email,
        password: values.password
      })).unwrap()
      message.success('注册成功，自动登录中...')
      navigate('/dashboard')
    } catch (error) {
      message.error(error instanceof Error ? error.message : '注册失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <Card>
          <div className="auth-header">
            <Title level={2}>注册</Title>
            <Text type="secondary">创建您的股票分析账号</Text>
          </div>

          <Form
            name="register"
            onFinish={onFinish}
            size="large"
            autoComplete="off"
          >
            <Form.Item
              name="username"
              rules={[
                { required: true, message: '请输入用户名' },
                { min: 3, message: '用户名至少3个字符' },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="用户名"
              />
            </Form.Item>

            <Form.Item
              name="email"
              rules={[
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '邮箱格式不正确' },
              ]}
            >
              <Input
                prefix={<MailOutlined />}
                placeholder="邮箱"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码至少6个字符' },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="密码"
              />
            </Form.Item>

            <Form.Item
              name="confirmPassword"
              dependencies={['password']}
              rules={[
                { required: true, message: '请确认密码' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve()
                    }
                    return Promise.reject(new Error('两次输入的密码不一致'))
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="确认密码"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
              >
                注册
              </Button>
            </Form.Item>
          </Form>

          <Divider>
            <Text type="secondary">已有账号？</Text>
          </Divider>

          <div className="auth-footer">
            <Link to="/login">
              <Button block>立即登录</Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  )
}

export default Register
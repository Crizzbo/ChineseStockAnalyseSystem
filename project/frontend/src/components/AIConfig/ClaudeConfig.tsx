import React, { useState, useEffect } from 'react'
import {
  Card,
  Form,
  Input,
  Button,
  Switch,
  Alert,
  Space,
  Typography,
  Divider,
  Select,
  message
} from 'antd'
import { SettingOutlined, EyeInvisibleOutlined, EyeTwoTone, CheckCircleOutlined } from '@ant-design/icons'

const { Title, Text, Paragraph } = Typography
const { Option } = Select

interface ClaudeConfig {
  apiKey: string
  enabled: boolean
  model: string
  maxTokens: number
  temperature: number
}

interface ClaudeConfigProps {
  onConfigChange?: (config: ClaudeConfig) => void
}

const ClaudeConfig: React.FC<ClaudeConfigProps> = ({ onConfigChange }) => {
  const [form] = Form.useForm()
  const [isTestingConnection, setIsTestingConnection] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'none' | 'success' | 'error'>('none')
  const [config, setConfig] = useState<ClaudeConfig>({
    apiKey: '',
    enabled: false,
    model: 'claude-3-sonnet-20240229',
    maxTokens: 4000,
    temperature: 0.7
  })

  // 加载配置
  useEffect(() => {
    const savedConfig = localStorage.getItem('claude_config')
    if (savedConfig) {
      try {
        const parsedConfig = JSON.parse(savedConfig)
        setConfig(parsedConfig)
        form.setFieldsValue(parsedConfig)
      } catch (error) {
        console.error('Failed to parse Claude config:', error)
      }
    }
  }, [form])

  // 保存配置
  const saveConfig = (newConfig: ClaudeConfig) => {
    localStorage.setItem('claude_config', JSON.stringify(newConfig))
    setConfig(newConfig)
    onConfigChange?.(newConfig)
  }

  // 测试连接
  const testConnection = async () => {
    const apiKey = form.getFieldValue('apiKey')

    if (!apiKey) {
      message.warning('请先输入API密钥')
      return
    }

    setIsTestingConnection(true)
    setConnectionStatus('none')

    try {
      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: config.model,
          max_tokens: 10,
          messages: [
            {
              role: 'user',
              content: 'Hello'
            }
          ]
        })
      })

      if (response.ok) {
        setConnectionStatus('success')
        message.success('Claude API连接测试成功！')
      } else {
        setConnectionStatus('error')
        const errorData = await response.json()
        message.error(`连接失败: ${errorData.error?.message || '未知错误'}`)
      }
    } catch (error) {
      setConnectionStatus('error')
      message.error('连接失败，请检查网络连接和API密钥')
      console.error('Claude API test failed:', error)
    } finally {
      setIsTestingConnection(false)
    }
  }

  // 表单提交
  const handleSubmit = (values: any) => {
    const newConfig: ClaudeConfig = {
      ...config,
      ...values
    }
    saveConfig(newConfig)
    message.success('Claude配置已保存')
  }

  // 重置配置
  const handleReset = () => {
    form.resetFields()
    const defaultConfig: ClaudeConfig = {
      apiKey: '',
      enabled: false,
      model: 'claude-3-sonnet-20240229',
      maxTokens: 4000,
      temperature: 0.7
    }
    saveConfig(defaultConfig)
    message.success('配置已重置')
  }

  return (
    <Card
      title={
        <Space>
          <SettingOutlined />
          <span>Claude API 配置</span>
        </Space>
      }
      className="claude-config-card"
    >
      <Alert
        message="Claude API 配置说明"
        description={
          <div>
            <Paragraph>
              Claude是Anthropic开发的先进AI助手。要使用Claude，您需要：
            </Paragraph>
            <ul>
              <li>在 <a href="https://console.anthropic.com/" target="_blank" rel="noopener noreferrer">Anthropic Console</a> 注册账号</li>
              <li>获取API密钥（API Key）</li>
              <li>确保账户有足够的配额</li>
            </ul>
          </div>
        }
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={config}
      >
        <Form.Item
          label="启用Claude"
          name="enabled"
          valuePropName="checked"
        >
          <Switch
            checkedChildren="启用"
            unCheckedChildren="禁用"
          />
        </Form.Item>

        <Form.Item
          label="API密钥"
          name="apiKey"
          rules={[
            { required: true, message: '请输入Claude API密钥' },
            { min: 10, message: 'API密钥长度不能少于10位' }
          ]}
        >
          <Input.Password
            placeholder="输入您的Claude API密钥"
            iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
          />
        </Form.Item>

        <Form.Item>
          <Space>
            <Button
              type="default"
              onClick={testConnection}
              loading={isTestingConnection}
            >
              测试连接
            </Button>
            {connectionStatus === 'success' && (
              <Text type="success">
                <CheckCircleOutlined /> 连接成功
              </Text>
            )}
            {connectionStatus === 'error' && (
              <Text type="danger">连接失败</Text>
            )}
          </Space>
        </Form.Item>

        <Divider>高级设置</Divider>

        <Form.Item
          label="模型版本"
          name="model"
          tooltip="选择要使用的Claude模型版本"
        >
          <Select>
            <Option value="claude-3-opus-20240229">Claude 3 Opus (最强性能)</Option>
            <Option value="claude-3-sonnet-20240229">Claude 3 Sonnet (平衡性能)</Option>
            <Option value="claude-3-haiku-20240307">Claude 3 Haiku (快速响应)</Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="最大令牌数"
          name="maxTokens"
          tooltip="单次对话的最大输出长度"
        >
          <Select>
            <Option value={1000}>1000 (简短回答)</Option>
            <Option value={2000}>2000 (中等长度)</Option>
            <Option value={4000}>4000 (详细回答)</Option>
            <Option value={8000}>8000 (最详细)</Option>
          </Select>
        </Form.Item>

        <Form.Item
          label="温度值"
          name="temperature"
          tooltip="控制回答的创造性，0.0-1.0之间，越高越有创造性"
        >
          <Select>
            <Option value={0.1}>0.1 (非常保守)</Option>
            <Option value={0.3}>0.3 (保守)</Option>
            <Option value={0.5}>0.5 (中等)</Option>
            <Option value={0.7}>0.7 (创造性)</Option>
            <Option value={0.9}>0.9 (非常有创造性)</Option>
          </Select>
        </Form.Item>

        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit">
              保存配置
            </Button>
            <Button onClick={handleReset}>
              重置
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  )
}

export default ClaudeConfig
import React, { useState, useEffect } from 'react'
import { Row, Col, Card, Typography, Form, Switch, Select, Button, Space, message, Divider, InputNumber, Radio, Modal } from 'antd'
import { useSelector, useDispatch } from 'react-redux'
import { SaveOutlined, ReloadOutlined, SettingOutlined, BellOutlined, EyeOutlined, GlobalOutlined, RobotOutlined, ThunderboltOutlined } from '@ant-design/icons'
import type { RootState, AppDispatch } from '@store/index'
import { userService, type UserPreferences } from '@services/user'
import ClaudeConfig from '@components/AIConfig/ClaudeConfig'
import { claudeChatService } from '@services/claudeChat'
import './Settings.scss'

const { Title, Text } = Typography
const { Option } = Select


const Settings: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>()
  const { user } = useSelector((state: RootState) => state.auth)
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [showClaudeConfig, setShowClaudeConfig] = useState(false)
  const [claudeConfigured, setClaudeConfigured] = useState(false)
  const [preferences, setPreferences] = useState<UserPreferences>({
    theme: 'light',
    language: 'zh',
    notifications: {
      priceAlerts: true,
      portfolioUpdates: true,
      newsAlerts: false,
      systemNotifications: true
    },
    display: {
      autoRefresh: true,
      refreshInterval: 30,
      showPremarket: false,
      showAfterHours: false,
      defaultChartType: 'candlestick',
      priceFormat: 'absolute'
    },
    trading: {
      confirmOrders: true,
      defaultOrderType: 'market',
      riskWarnings: true
    }
  })

  useEffect(() => {
    loadUserPreferences()
    // 检查Claude配置状态
    setClaudeConfigured(claudeChatService.isConfigured())
  }, [])

  const loadUserPreferences = async () => {
    try {
      // 从 API 加载用户偏好设置
      const preferences = await userService.getUserPreferences()
      setPreferences(preferences)
      form.setFieldsValue(preferences)

      // 应用主题设置
      userService.applyTheme(preferences.theme)
    } catch (error) {
      console.error('加载用户偏好设置失败:', error)
      // 如果API失败，尝试从localStorage加载
      const localPrefs = userService.loadFromLocalStorage()
      if (localPrefs) {
        setPreferences(localPrefs)
        form.setFieldsValue(localPrefs)
        userService.applyTheme(localPrefs.theme)
      }
    }
  }

  const handleSave = async (values: UserPreferences) => {
    setLoading(true)
    try {
      // 保存到 API
      const updatedPreferences = await userService.updateUserPreferences(values)
      setPreferences(updatedPreferences)

      // 同时保存到localStorage作为备份
      userService.saveToLocalStorage(updatedPreferences)

      // 应用主题设置
      userService.applyTheme(updatedPreferences.theme)

      message.success('设置保存成功')
    } catch (error) {
      message.error('保存设置失败，请重试')
      console.error('保存设置失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = async () => {
    try {
      setLoading(true)
      // 重置到默认设置
      const defaultPreferences = await userService.resetUserPreferences()
      setPreferences(defaultPreferences)
      form.setFieldsValue(defaultPreferences)

      // 应用主题设置
      userService.applyTheme(defaultPreferences.theme)

      message.success('设置已重置为默认值')
    } catch (error) {
      message.error('重置设置失败，请重试')
      console.error('重置设置失败:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="settings">
      <div className="page-header">
        <Title level={2}>
          <SettingOutlined style={{ marginRight: 12 }} />
          系统设置
        </Title>
        <Text type="secondary">个性化您的股票分析体验</Text>
      </div>

      <Form
        form={form}
        layout="vertical"
        initialValues={preferences}
        onFinish={handleSave}
        className="settings-form"
      >
        <Row gutter={[24, 24]}>
          {/* 外观设置 */}
          <Col span={24} lg={12}>
            <Card
              title={
                <Space>
                  <EyeOutlined />
                  <span>外观设置</span>
                </Space>
              }
              className="settings-card"
            >
              <Form.Item
                label="主题模式"
                name="theme"
                tooltip="选择您偏好的界面主题"
              >
                <Radio.Group>
                  <Radio.Button value="light">浅色</Radio.Button>
                  <Radio.Button value="dark">深色</Radio.Button>
                  <Radio.Button value="auto">跟随系统</Radio.Button>
                </Radio.Group>
              </Form.Item>

              <Form.Item
                label="语言设置"
                name="language"
                tooltip="选择界面显示语言"
              >
                <Select>
                  <Option value="zh">简体中文</Option>
                  <Option value="en">English</Option>
                </Select>
              </Form.Item>

              <Divider />

              <Form.Item
                label="默认图表类型"
                name={['display', 'defaultChartType']}
              >
                <Select>
                  <Option value="line">线图</Option>
                  <Option value="candlestick">K线图</Option>
                </Select>
              </Form.Item>

              <Form.Item
                label="价格显示格式"
                name={['display', 'priceFormat']}
              >
                <Radio.Group>
                  <Radio value="absolute">绝对价格</Radio>
                  <Radio value="percentage">百分比</Radio>
                </Radio.Group>
              </Form.Item>
            </Card>
          </Col>

          {/* 通知设置 */}
          <Col span={24} lg={12}>
            <Card
              title={
                <Space>
                  <BellOutlined />
                  <span>通知设置</span>
                </Space>
              }
              className="settings-card"
            >
              <Form.Item
                label="价格提醒"
                name={['notifications', 'priceAlerts']}
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                label="投资组合更新"
                name={['notifications', 'portfolioUpdates']}
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                label="新闻推送"
                name={['notifications', 'newsAlerts']}
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                label="系统通知"
                name={['notifications', 'systemNotifications']}
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
            </Card>
          </Col>

          {/* 数据刷新设置 */}
          <Col span={24} lg={12}>
            <Card
              title={
                <Space>
                  <GlobalOutlined />
                  <span>数据设置</span>
                </Space>
              }
              className="settings-card"
            >
              <Form.Item
                label="自动刷新"
                name={['display', 'autoRefresh']}
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                label="刷新间隔(秒)"
                name={['display', 'refreshInterval']}
                dependencies={[['display', 'autoRefresh']]}
              >
                {({ getFieldValue }) => (
                  <InputNumber
                    min={5}
                    max={300}
                    step={5}
                    disabled={!getFieldValue(['display', 'autoRefresh'])}
                    addonAfter="秒"
                    style={{ width: '100%' }}
                  />
                )}
              </Form.Item>

              <Form.Item
                label="显示盘前交易"
                name={['display', 'showPremarket']}
                valuePropName="checked"
              >
                <Switch checkedChildren="显示" unCheckedChildren="隐藏" />
              </Form.Item>

              <Form.Item
                label="显示盘后交易"
                name={['display', 'showAfterHours']}
                valuePropName="checked"
              >
                <Switch checkedChildren="显示" unCheckedChildren="隐藏" />
              </Form.Item>
            </Card>
          </Col>

          {/* 交易设置 */}
          <Col span={24} lg={12}>
            <Card
              title={
                <Space>
                  <SettingOutlined />
                  <span>交易设置</span>
                </Space>
              }
              className="settings-card"
            >
              <Form.Item
                label="订单确认"
                name={['trading', 'confirmOrders']}
                valuePropName="checked"
                tooltip="提交订单前显示确认对话框"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>

              <Form.Item
                label="默认订单类型"
                name={['trading', 'defaultOrderType']}
              >
                <Select>
                  <Option value="market">市价单</Option>
                  <Option value="limit">限价单</Option>
                </Select>
              </Form.Item>

              <Form.Item
                label="风险警告"
                name={['trading', 'riskWarnings']}
                valuePropName="checked"
                tooltip="在高风险操作时显示警告"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
            </Card>
          </Col>

          {/* AI设置 */}
          <Col span={24}>
            <Card
              title={
                <Space>
                  <RobotOutlined />
                  <span>AI助手设置</span>
                </Space>
              }
              className="settings-card"
            >
              <Row gutter={16}>
                <Col span={24} md={12}>
                  <div style={{ padding: '16px', border: '1px solid #d9d9d9', borderRadius: '6px' }}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Space>
                          <ThunderboltOutlined style={{ color: '#1890ff' }} />
                          <Text strong>Claude AI</Text>
                        </Space>
                        <Text type={claudeConfigured ? 'success' : 'secondary'} style={{ fontSize: 12 }}>
                          {claudeConfigured ? '✓ 已配置' : '未配置'}
                        </Text>
                      </div>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        Anthropic开发的先进AI助手，提供专业的投资分析和建议
                      </Text>
                      <Button
                        type={claudeConfigured ? 'default' : 'primary'}
                        size="small"
                        onClick={() => setShowClaudeConfig(true)}
                        style={{ width: 'fit-content' }}
                      >
                        {claudeConfigured ? '重新配置' : '立即配置'}
                      </Button>
                    </Space>
                  </div>
                </Col>
                <Col span={24} md={12}>
                  <div style={{ padding: '16px', border: '1px solid #d9d9d9', borderRadius: '6px', backgroundColor: '#f9f9f9' }}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Space>
                          <RobotOutlined style={{ color: '#52c41a' }} />
                          <Text strong>后端AI</Text>
                        </Space>
                        <Text type="success" style={{ fontSize: 12 }}>
                          ✓ 可用
                        </Text>
                      </div>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        系统内置的AI服务，无需额外配置
                      </Text>
                      <Button size="small" disabled style={{ width: 'fit-content' }}>
                        默认可用
                      </Button>
                    </Space>
                  </div>
                </Col>
              </Row>
            </Card>
          </Col>

          {/* 操作按钮 */}
          <Col span={24}>
            <Card className="settings-actions">
              <Space>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  icon={<SaveOutlined />}
                  size="large"
                >
                  保存设置
                </Button>
                <Button
                  onClick={handleReset}
                  loading={loading}
                  icon={<ReloadOutlined />}
                  size="large"
                >
                  重置设置
                </Button>
              </Space>
            </Card>
          </Col>
        </Row>
      </Form>

      {/* Claude配置模态框 */}
      <Modal
        title="Claude API 配置"
        open={showClaudeConfig}
        onCancel={() => setShowClaudeConfig(false)}
        footer={null}
        width={600}
        destroyOnClose
      >
        <ClaudeConfig
          onConfigChange={() => {
            setClaudeConfigured(claudeChatService.isConfigured())
            setShowClaudeConfig(false)
            message.success('Claude配置已更新')
          }}
        />
      </Modal>
    </div>
  )
}

export default Settings
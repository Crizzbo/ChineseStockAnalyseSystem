import React, { useState, useRef, useEffect } from 'react'
import { Card, Input, Button, List, Typography, Avatar, Space, Spin, message, Tag, Tooltip, Radio, Modal, Divider } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined, ClearOutlined, QuestionCircleOutlined, SettingOutlined, ThunderboltOutlined } from '@ant-design/icons'
import { aiChatService } from '@services/aiChat'
import { claudeChatService, type ClaudeMessage } from '@services/claudeChat'
import ClaudeConfig from '@components/AIConfig/ClaudeConfig'
import './AIChat.scss'

const { Text, Paragraph } = Typography
const { TextArea } = Input

export interface ChatMessage {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: string
  status?: 'sending' | 'success' | 'error'
  metadata?: {
    stocks_mentioned?: string[]
    suggestions?: string[]
  }
}

const AIChat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [aiService, setAiService] = useState<'backend' | 'claude'>('backend')
  const [showClaudeConfig, setShowClaudeConfig] = useState(false)
  const [claudeAvailable, setClaudeAvailable] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<any>(null)

  // 预设问题
  const presetQuestions = [
    '今天股市表现如何？',
    '推荐一些科技股',
    '如何分析股票技术指标？',
    '什么是市盈率和市净率？',
    '现在适合投资什么板块？',
    '如何控制投资风险？'
  ]

  // 检查Claude是否可用
  const checkClaudeAvailability = () => {
    const isAvailable = claudeChatService.isConfigured()
    setClaudeAvailable(isAvailable)
    return isAvailable
  }

  // 欢迎消息
  useEffect(() => {
    checkClaudeAvailability()

    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      type: 'assistant',
      content: '您好！我是您的股票投资AI助手，可以为您提供股票分析、市场资讯、投资建议等服务。请问有什么可以帮助您的吗？',
      timestamp: new Date().toISOString(),
      status: 'success',
      metadata: {
        suggestions: presetQuestions.slice(0, 3)
      }
    }
    setMessages([welcomeMessage])
  }, [])

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // 发送消息
  const handleSendMessage = async () => {
    const content = inputValue.trim()
    if (!content) {
      message.warning('请输入您的问题')
      return
    }

    if (isLoading) {
      message.warning('正在处理中，请稍候...')
      return
    }

    // 检查Claude配置
    if (aiService === 'claude' && !claudeAvailable) {
      message.warning('请先配置Claude API')
      setShowClaudeConfig(true)
      return
    }

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      type: 'user',
      content,
      timestamp: new Date().toISOString(),
      status: 'success'
    }

    // 添加用户消息
    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    // 添加AI回复的占位消息
    const aiMessageId = `ai_${Date.now()}`
    const aiMessage: ChatMessage = {
      id: aiMessageId,
      type: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      status: 'sending'
    }
    setMessages(prev => [...prev, aiMessage])

    try {
      let response: any

      if (aiService === 'claude') {
        // 构建Claude对话历史
        const conversationHistory: ClaudeMessage[] = messages
          .filter(msg => msg.type === 'user' || msg.type === 'assistant')
          .filter(msg => msg.content && msg.id !== 'welcome' && !msg.id.startsWith('welcome'))
          .map(msg => ({
            role: msg.type === 'user' ? 'user' : 'assistant',
            content: msg.content
          }))

        const claudeResponse = await claudeChatService.sendMessage({
          message: content,
          conversationHistory
        })

        response = {
          reply: claudeResponse.reply,
          stocks_mentioned: [],
          suggestions: await claudeChatService.generateStockQuestions()
        }
      } else {
        // 使用后端AI服务
        response = await aiChatService.sendMessage({
          message: content,
          conversation_id: 'default',
          include_context: true
        })
      }

      // 更新AI回复
      setMessages(prev => prev.map(msg =>
        msg.id === aiMessageId
          ? {
              ...msg,
              content: response.reply,
              status: 'success',
              metadata: {
                stocks_mentioned: response.stocks_mentioned,
                suggestions: response.suggestions
              }
            }
          : msg
      ))

    } catch (error) {
      console.error('AI聊天失败:', error)

      let errorMessage = 'AI服务暂时不可用，请稍后重试。'
      if (error instanceof Error) {
        errorMessage = error.message
      }

      // 更新为错误状态
      setMessages(prev => prev.map(msg =>
        msg.id === aiMessageId
          ? {
              ...msg,
              content: `抱歉，${errorMessage}`,
              status: 'error'
            }
          : msg
      ))

      message.error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  // 清空对话
  const handleClearChat = () => {
    const welcomeMessage: ChatMessage = {
      id: 'welcome_new',
      type: 'assistant',
      content: '对话已清空。有什么新的问题想要咨询吗？',
      timestamp: new Date().toISOString(),
      status: 'success',
      metadata: {
        suggestions: presetQuestions.slice(0, 3)
      }
    }
    setMessages([welcomeMessage])
  }

  // 使用预设问题
  const handlePresetQuestion = (question: string) => {
    setInputValue(question)
    inputRef.current?.focus()
  }

  // 处理回车发送
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // 渲染消息内容
  const renderMessageContent = (message: ChatMessage) => {
    return (
      <div className="message-content">
        <Paragraph className="message-text">
          {message.content}
        </Paragraph>

        {/* 显示相关股票 */}
        {message.metadata?.stocks_mentioned && message.metadata.stocks_mentioned.length > 0 && (
          <div className="message-stocks">
            <Text type="secondary" style={{ fontSize: 12 }}>相关股票：</Text>
            <Space wrap>
              {message.metadata.stocks_mentioned.map(stock => (
                <Tag key={stock} color="blue" style={{ fontSize: 11 }}>
                  {stock}
                </Tag>
              ))}
            </Space>
          </div>
        )}

        {/* 显示建议问题 */}
        {message.metadata?.suggestions && message.metadata.suggestions.length > 0 && (
          <div className="message-suggestions">
            <Text type="secondary" style={{ fontSize: 12 }}>您可能还想了解：</Text>
            <div className="suggestion-tags">
              {message.metadata.suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  type="link"
                  size="small"
                  onClick={() => handlePresetQuestion(suggestion)}
                  style={{ padding: '2px 4px', height: 'auto', fontSize: 11 }}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="ai-chat-container">
      <Card
        className="chat-card"
        title={
          <Space>
            <RobotOutlined style={{ color: '#1890ff' }} />
            <span>AI投资助手</span>
            <Tooltip title="专业的股票投资AI助手，为您提供实时市场分析和投资建议">
              <QuestionCircleOutlined style={{ color: '#8c8c8c' }} />
            </Tooltip>
          </Space>
        }
        extra={
          <Space>
            <Button
              type="text"
              icon={<SettingOutlined />}
              onClick={() => setShowClaudeConfig(true)}
              size="small"
            >
              Claude配置
            </Button>
            <Button
              type="text"
              icon={<ClearOutlined />}
              onClick={handleClearChat}
              size="small"
            >
              清空对话
            </Button>
          </Space>
        }
      >
        <div className="chat-content">
          {/* AI服务选择器 */}
          <div style={{ marginBottom: 16, padding: '12px', backgroundColor: '#f5f5f5', borderRadius: '6px' }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong style={{ fontSize: 12 }}>选择AI服务：</Text>
              <Radio.Group
                value={aiService}
                onChange={(e) => setAiService(e.target.value)}
                size="small"
              >
                <Radio.Button value="backend">
                  <Space>
                    <RobotOutlined />
                    Copilot AI
                  </Space>
                </Radio.Button>
                <Radio.Button value="claude" disabled={!claudeAvailable}>
                  <Space>
                    <ThunderboltOutlined />
                    Claude
                    {!claudeAvailable && <Text type="secondary" style={{ fontSize: 10 }}>(未配置)</Text>}
                  </Space>
                </Radio.Button>
              </Radio.Group>
              {aiService === 'backend' && (
                <Text type="success" style={{ fontSize: 11 }}>
                  ✓ Copilot AI已准备就绪
                </Text>
              )}
              {aiService === 'claude' && claudeAvailable && (
                <Text type="success" style={{ fontSize: 11 }}>
                  ✓ Claude已配置并可用
                </Text>
              )}
              {aiService === 'claude' && !claudeAvailable && (
                <Text type="warning" style={{ fontSize: 11 }}>
                  ⚠ 请先配置Claude API密钥
                </Text>
              )}
            </Space>
          </div>

          {/* 消息列表 */}
          <div className="messages-container">
            <List
              className="messages-list"
              itemLayout="vertical"
              dataSource={messages}
              renderItem={(message) => (
                <List.Item className={`message-item ${message.type}`}>
                  <div className="message-wrapper">
                    <Avatar
                      className="message-avatar"
                      icon={message.type === 'user' ? <UserOutlined /> : <RobotOutlined />}
                      style={{
                        backgroundColor: message.type === 'user' ? '#1890ff' : '#52c41a'
                      }}
                    />

                    <div className="message-bubble">
                      {message.status === 'sending' ? (
                        <div className="message-loading">
                          <Spin size="small" />
                          <Text type="secondary" style={{ marginLeft: 8 }}>正在思考中...</Text>
                        </div>
                      ) : (
                        renderMessageContent(message)
                      )}

                      <div className="message-time">
                        <Text type="secondary" style={{ fontSize: 11 }}>
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </Text>
                        {message.status === 'error' && (
                          <Text type="danger" style={{ fontSize: 11, marginLeft: 8 }}>
                            发送失败
                          </Text>
                        )}
                      </div>
                    </div>
                  </div>
                </List.Item>
              )}
            />
            <div ref={messagesEndRef} />
          </div>

          {/* 预设问题 */}
          <div className="preset-questions">
            <Text type="secondary" style={{ fontSize: 12 }}>常见问题：</Text>
            <Space wrap style={{ marginTop: 8 }}>
              {presetQuestions.map((question, index) => (
                <Button
                  key={index}
                  type="dashed"
                  size="small"
                  onClick={() => handlePresetQuestion(question)}
                  style={{ fontSize: 11 }}
                >
                  {question}
                </Button>
              ))}
            </Space>
          </div>

          {/* 输入区域 */}
          <div className="input-container">
            <div className="input-wrapper">
              <TextArea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="请输入您的问题，比如：今天科技股表现如何？"
                rows={2}
                className="chat-input"
                disabled={isLoading}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSendMessage}
                loading={isLoading}
                disabled={!inputValue.trim()}
                className="send-button"
              >
                发送
              </Button>
            </div>
          </div>
        </div>
      </Card>

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
            checkClaudeAvailability()
            setShowClaudeConfig(false)
          }}
        />
      </Modal>
    </div>
  )
}

export default AIChat
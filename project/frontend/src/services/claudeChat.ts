/**
 * Claude AI聊天服务
 */

export interface ClaudeConfig {
  apiKey: string
  enabled: boolean
  model: string
  maxTokens: number
  temperature: number
}

export interface ClaudeMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ClaudeChatRequest {
  message: string
  conversationHistory?: ClaudeMessage[]
  systemPrompt?: string
}

export interface ClaudeChatResponse {
  reply: string
  usage?: {
    input_tokens: number
    output_tokens: number
  }
  model: string
  stop_reason: string
}

class ClaudeChatService {
  private config: ClaudeConfig | null = null

  /**
   * 加载配置
   */
  loadConfig(): ClaudeConfig | null {
    try {
      const configStr = localStorage.getItem('claude_config')
      if (configStr) {
        this.config = JSON.parse(configStr)
        return this.config
      }
    } catch (error) {
      console.error('Failed to load Claude config:', error)
    }
    return null
  }

  /**
   * 检查配置是否有效
   */
  isConfigured(): boolean {
    const config = this.loadConfig()
    return !!(config?.enabled && config?.apiKey)
  }

  /**
   * 获取系统提示词
   */
  private getSystemPrompt(): string {
    return `你是一个专业的股票投资AI助手。你的职责是：

1. 为用户提供准确、客观的股票市场分析
2. 解答投资相关问题，包括技术分析、基本面分析等
3. 提供风险提示和投资建议
4. 保持中性立场，不做具体的买卖推荐
5. 用中文回答，语言简洁专业

重要提醒：
- 投资有风险，需谨慎决策
- 不要提供具体的买卖时点建议
- 强调做好风险管理
- 建议用户进行独立研究

请根据用户的问题提供有帮助的回答。`
  }

  /**
   * 发送消息给Claude
   */
  async sendMessage(request: ClaudeChatRequest): Promise<ClaudeChatResponse> {
    const config = this.loadConfig()

    if (!config?.enabled || !config?.apiKey) {
      throw new Error('Claude未配置或未启用，请先在设置中配置Claude API')
    }

    try {
      // 构建消息历史
      const messages: ClaudeMessage[] = []

      // 添加历史对话
      if (request.conversationHistory && request.conversationHistory.length > 0) {
        messages.push(...request.conversationHistory.slice(-10)) // 只保留最近10条消息
      }

      // 添加当前用户消息
      messages.push({
        role: 'user',
        content: request.message
      })

      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': config.apiKey,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: config.model,
          max_tokens: config.maxTokens,
          temperature: config.temperature,
          system: request.systemPrompt || this.getSystemPrompt(),
          messages: messages
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error?.message || `API请求失败: ${response.status}`)
      }

      const data = await response.json()

      return {
        reply: data.content[0].text,
        usage: data.usage,
        model: data.model,
        stop_reason: data.stop_reason
      }

    } catch (error) {
      console.error('Claude API Error:', error)

      if (error instanceof Error) {
        // 处理常见错误
        if (error.message.includes('rate_limit')) {
          throw new Error('请求频率过高，请稍后再试')
        } else if (error.message.includes('invalid_api_key')) {
          throw new Error('API密钥无效，请检查配置')
        } else if (error.message.includes('insufficient_quota')) {
          throw new Error('API配额不足，请检查账户余额')
        } else {
          throw error
        }
      }

      throw new Error('Claude服务暂时不可用，请稍后重试')
    }
  }

  /**
   * 生成股票相关的智能问题
   */
  async generateStockQuestions(symbol?: string): Promise<string[]> {
    const baseQuestions = [
      '今天股市表现如何？',
      '现在适合投资什么板块？',
      '如何分析股票的基本面？',
      '技术分析的关键指标有哪些？',
      '如何控制投资风险？',
      '什么是价值投资？'
    ]

    if (symbol) {
      const symbolQuestions = [
        `${symbol}这只股票怎么样？`,
        `${symbol}的技术面分析`,
        `${symbol}的基本面如何？`,
        `${symbol}适合长期投资吗？`
      ]
      return [...symbolQuestions, ...baseQuestions.slice(0, 2)]
    }

    return baseQuestions
  }

  /**
   * 获取投资建议
   */
  async getInvestmentAdvice(query: string): Promise<ClaudeChatResponse> {
    const investmentPrompt = `你是一个经验丰富的投资顾问。请基于以下查询提供专业的投资建议：

查询: ${query}

请提供：
1. 市场分析
2. 风险评估
3. 投资策略建议
4. 注意事项

记住要强调风险管理的重要性。`

    return this.sendMessage({
      message: query,
      systemPrompt: investmentPrompt
    })
  }

  /**
   * 股票技术分析
   */
  async analyzeStock(symbol: string, timeframe: string = '日线'): Promise<ClaudeChatResponse> {
    const analysisPrompt = `请对股票 ${symbol} 进行技术分析。

时间周期：${timeframe}

请分析：
1. 当前趋势方向
2. 关键技术指标
3. 支撑和阻力位
4. 交易量分析
5. 风险提示

注意：这只是技术分析参考，不构成投资建议。`

    return this.sendMessage({
      message: `请分析股票${symbol}的技术面`,
      systemPrompt: analysisPrompt
    })
  }

  /**
   * 市场概况分析
   */
  async getMarketOverview(): Promise<ClaudeChatResponse> {
    const marketPrompt = `请提供当前股票市场的概况分析，包括：

1. 主要指数表现
2. 热门板块动态
3. 市场情绪分析
4. 宏观经济影响因素
5. 短期展望

请保持客观中性的分析立场。`

    return this.sendMessage({
      message: '请分析当前股票市场的整体情况',
      systemPrompt: marketPrompt
    })
  }
}

export const claudeChatService = new ClaudeChatService()
export default claudeChatService
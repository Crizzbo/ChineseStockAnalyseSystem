/**
 * AI聊天服务API
 */
import api from './api'

export interface ChatMessage {
  message: string
  conversation_id?: string
  include_context?: boolean
  user_id?: string
}

export interface ChatResponse {
  reply: string
  conversation_id: string
  message_id: string
  stocks_mentioned?: string[]
  suggestions?: string[]
  confidence?: number
  sources?: Array<{
    type: string
    title: string
    url?: string
  }>
  timestamp: string
}

export interface ConversationHistory {
  conversation_id: string
  messages: Array<{
    role: 'user' | 'assistant'
    content: string
    timestamp: string
    metadata?: any
  }>
  created_at: string
  updated_at: string
}

export interface ChatAnalysis {
  conversation_id: string
  summary: string
  key_topics: string[]
  stocks_discussed: string[]
  investment_sentiment: 'bullish' | 'bearish' | 'neutral'
  risk_level: 'low' | 'medium' | 'high'
  recommendations: string[]
}

class AIChatService {
  /**
   * 发送消息给AI
   */
  async sendMessage(params: ChatMessage): Promise<ChatResponse> {
    return api.post('/ai/chat', params)
  }

  /**
   * 获取对话历史
   */
  async getConversationHistory(conversationId: string): Promise<{ conversation: ConversationHistory }> {
    return api.get(`/ai/conversations/${conversationId}`)
  }

  /**
   * 获取用户的所有对话
   */
  async getUserConversations(): Promise<{ conversations: ConversationHistory[] }> {
    return api.get('/ai/conversations')
  }

  /**
   * 创建新对话
   */
  async createConversation(title?: string): Promise<{ conversation: ConversationHistory }> {
    return api.post('/ai/conversations', { title })
  }

  /**
   * 删除对话
   */
  async deleteConversation(conversationId: string): Promise<{ success: boolean }> {
    return api.delete(`/ai/conversations/${conversationId}`)
  }

  /**
   * 获取对话分析
   */
  async getConversationAnalysis(conversationId: string): Promise<{ analysis: ChatAnalysis }> {
    return api.get(`/ai/conversations/${conversationId}/analysis`)
  }

  /**
   * 获取AI建议的问题
   */
  async getSuggestedQuestions(context?: string): Promise<{ questions: string[] }> {
    const params = context ? { context } : {}
    return api.get('/ai/suggestions', { params })
  }

  /**
   * 获取股票相关的智能问答
   */
  async getStockQA(symbol: string): Promise<{
    questions: string[]
    basic_info: any
    suggestions: string[]
  }> {
    return api.get(`/ai/stock-qa/${symbol}`)
  }

  /**
   * 批量分析多只股票
   */
  async analyzeStocks(symbols: string[], question: string): Promise<{
    analysis: Array<{
      symbol: string
      name: string
      analysis: string
      score: number
      recommendation: 'buy' | 'hold' | 'sell'
    }>
    summary: string
    comparison: string
  }> {
    return api.post('/ai/analyze-stocks', { symbols, question })
  }

  /**
   * 获取市场洞察
   */
  async getMarketInsights(timeframe?: 'today' | 'week' | 'month'): Promise<{
    insights: {
      market_summary: string
      key_trends: string[]
      sector_highlights: Array<{
        sector: string
        performance: number
        analysis: string
      }>
      risk_factors: string[]
      opportunities: string[]
    }
    timestamp: string
  }> {
    const params = timeframe ? { timeframe } : {}
    return api.get('/ai/market-insights', { params })
  }

  /**
   * 投资组合分析
   */
  async analyzePortfolio(holdings: Array<{
    symbol: string
    quantity: number
    average_cost: number
  }>): Promise<{
    analysis: {
      total_value: number
      total_return: number
      risk_score: number
      diversification_score: number
      sector_allocation: { [sector: string]: number }
      recommendations: string[]
      rebalancing_suggestions: Array<{
        action: 'buy' | 'sell' | 'hold'
        symbol: string
        reason: string
        priority: 'high' | 'medium' | 'low'
      }>
    }
  }> {
    return api.post('/ai/analyze-portfolio', { holdings })
  }

  /**
   * 风险评估
   */
  async assessRisk(
    portfolio: any,
    timeframe: number = 30
  ): Promise<{
    risk_assessment: {
      overall_risk: 'low' | 'medium' | 'high'
      var_95: number // Value at Risk (95% confidence)
      max_drawdown: number
      volatility: number
      correlation_risks: string[]
      concentration_risks: string[]
      recommendations: string[]
    }
  }> {
    return api.post('/ai/risk-assessment', { portfolio, timeframe })
  }
}

export const aiChatService = new AIChatService()
export default aiChatService
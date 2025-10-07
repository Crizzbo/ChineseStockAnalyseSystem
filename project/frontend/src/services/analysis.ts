/**
 * 股票分析相关API服务
 */
import api, { type StockInfo, type TechnicalIndicators, type AnalysisResult } from './api'

export interface TechnicalAnalysisResult {
  symbol: string
  period: string
  stock_info: StockInfo
  technical_indicators: TechnicalIndicators
  analysis: AnalysisResult
  timestamp: string
}

export interface FundamentalAnalysisResult {
  symbol: string
  stock_info: StockInfo
  analysis: {
    score: number
    metrics: {
      pe_ratio?: number
      pb_ratio?: number
      market_cap?: number
      [key: string]: number | undefined
    }
    analysis_points: string[]
    valuation: 'undervalued' | 'fair' | 'overvalued'
  }
  timestamp: string
}

export interface TrendAnalysisResult {
  symbol: string
  days: number
  analysis: {
    trend_direction: 'upward' | 'downward' | 'sideways'
    trend_strength: number
    price_change: number
    volatility: number
    analysis_points: string[]
  }
  timestamp: string
}

export interface CorrelationAnalysisParams {
  symbols: string[]
  days?: number
}

export interface CorrelationAnalysisResult {
  symbols: string[]
  days: number
  correlation_matrix: {
    [symbol: string]: {
      [symbol: string]: number
    }
  }
  analysis: string[]
  timestamp: string
}

export interface RiskAnalysisResult {
  symbol: string
  days: number
  risk_metrics: {
    volatility: number
    max_drawdown: number
    var_95: number
    sharpe_ratio: number
    risk_level: 'low' | 'medium' | 'high'
  }
  timestamp: string
}

class AnalysisService {
  /**
   * 获取技术分析
   */
  async getTechnicalAnalysis(symbol: string, period: 'daily' | 'weekly' | 'monthly' = 'daily'): Promise<TechnicalAnalysisResult> {
    const queryParams = new URLSearchParams()
    queryParams.append('period', period)

    return api.get(`/analysis/technical/${symbol}?${queryParams}`)
  }

  /**
   * 获取基本面分析
   */
  async getFundamentalAnalysis(symbol: string): Promise<FundamentalAnalysisResult> {
    return api.get(`/analysis/fundamental/${symbol}`)
  }

  /**
   * 获取趋势分析
   */
  async getTrendAnalysis(symbol: string, days = 30): Promise<TrendAnalysisResult> {
    const queryParams = new URLSearchParams()
    queryParams.append('days', days.toString())

    return api.get(`/analysis/trend/${symbol}?${queryParams}`)
  }

  /**
   * 获取相关性分析
   */
  async getCorrelationAnalysis(params: CorrelationAnalysisParams): Promise<CorrelationAnalysisResult> {
    return api.post('/analysis/correlation', params)
  }

  /**
   * 获取风险分析
   */
  async getRiskAnalysis(symbol: string, days = 60): Promise<RiskAnalysisResult> {
    const queryParams = new URLSearchParams()
    queryParams.append('days', days.toString())

    return api.get(`/analysis/risk/${symbol}?${queryParams}`)
  }

  /**
   * 获取综合分析（组合多个分析结果）
   */
  async getComprehensiveAnalysis(symbol: string): Promise<{
    technical: TechnicalAnalysisResult
    fundamental: FundamentalAnalysisResult
    trend: TrendAnalysisResult
    risk: RiskAnalysisResult
  }> {
    try {
      const [technical, fundamental, trend, risk] = await Promise.all([
        this.getTechnicalAnalysis(symbol),
        this.getFundamentalAnalysis(symbol),
        this.getTrendAnalysis(symbol),
        this.getRiskAnalysis(symbol)
      ])

      return {
        technical,
        fundamental,
        trend,
        risk
      }
    } catch (error) {
      console.error('获取综合分析失败:', error)
      throw error
    }
  }

  /**
   * 生成投资建议（基于多个分析结果）
   */
  generateInvestmentAdvice(analysisData: {
    technical: TechnicalAnalysisResult
    fundamental: FundamentalAnalysisResult
    trend: TrendAnalysisResult
    risk: RiskAnalysisResult
  }): {
    overall_score: number
    recommendation: 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell'
    summary: string[]
    risk_level: 'low' | 'medium' | 'high'
    confidence: number
  } {
    const { technical, fundamental, trend, risk } = analysisData

    let totalScore = 0
    let scoreCount = 0
    const summary: string[] = []

    // 技术面得分
    if (technical.analysis.score !== undefined) {
      totalScore += technical.analysis.score
      scoreCount++

      if (technical.analysis.overall) {
        const signals = {
          bullish: '技术面偏强',
          bearish: '技术面偏弱',
          neutral: '技术面中性'
        }
        summary.push(signals[technical.analysis.overall])
      }
    }

    // 基本面得分
    if (fundamental.analysis.score !== undefined) {
      totalScore += fundamental.analysis.score
      scoreCount++

      const valuations = {
        undervalued: '估值偏低',
        fair: '估值合理',
        overvalued: '估值偏高'
      }
      summary.push(valuations[fundamental.analysis.valuation])
    }

    // 趋势面得分
    let trendScore = 0
    if (trend.analysis.trend_direction === 'upward') {
      trendScore = 10
      summary.push('价格趋势向上')
    } else if (trend.analysis.trend_direction === 'downward') {
      trendScore = -10
      summary.push('价格趋势向下')
    } else {
      trendScore = 0
      summary.push('价格横盘整理')
    }
    totalScore += trendScore
    scoreCount++

    // 计算平均得分
    const averageScore = scoreCount > 0 ? totalScore / scoreCount : 0

    // 生成建议
    let recommendation: 'strong_buy' | 'buy' | 'hold' | 'sell' | 'strong_sell'
    let confidence = 0

    if (averageScore >= 15) {
      recommendation = 'strong_buy'
      confidence = 0.8
    } else if (averageScore >= 5) {
      recommendation = 'buy'
      confidence = 0.6
    } else if (averageScore >= -5) {
      recommendation = 'hold'
      confidence = 0.5
    } else if (averageScore >= -15) {
      recommendation = 'sell'
      confidence = 0.6
    } else {
      recommendation = 'strong_sell'
      confidence = 0.8
    }

    // 考虑风险调整建议
    if (risk.risk_metrics.risk_level === 'high') {
      if (recommendation === 'strong_buy') recommendation = 'buy'
      if (recommendation === 'buy') recommendation = 'hold'
      summary.push('风险水平较高，建议谨慎')
    }

    return {
      overall_score: Math.round(averageScore),
      recommendation,
      summary,
      risk_level: risk.risk_metrics.risk_level,
      confidence: Math.round(confidence * 100) / 100
    }
  }
}

export const analysisService = new AnalysisService()
export default analysisService
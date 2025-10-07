"""
股票分析系统主类
整合所有AKShare工具类，提供统一的股票分析接口
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime, timedelta

from .realtime_data_service import RealTimeDataService
from .historical_data_service import HistoricalDataService
from .fundamental_data_service import FundamentalDataService
from .market_analysis_service import MarketAnalysisService
from .data_cache_manager import DataCacheManager
from .utils.data_validator import DataValidator
from .utils.retry_decorator import api_monitor

logger = logging.getLogger(__name__)


class StockAnalysisSystem:
    """股票分析系统主类"""

    def __init__(self, enable_cache: bool = True, cache_config: Optional[Dict] = None):
        """
        初始化股票分析系统

        Args:
            enable_cache: 是否启用缓存
            cache_config: 缓存配置
        """
        self.logger = logger

        # 初始化各个服务
        self.realtime_service = RealTimeDataService()
        self.historical_service = HistoricalDataService()
        self.fundamental_service = FundamentalDataService()
        self.market_analysis_service = MarketAnalysisService()

        # 初始化缓存管理器
        self.cache_manager = None
        if enable_cache:
            cache_config = cache_config or {}
            self.cache_manager = DataCacheManager(**cache_config)

        # 初始化数据验证器
        self.validator = DataValidator()

        self.logger.info("股票分析系统初始化完成")

    def analyze_stock(self, symbol: str, analysis_type: str = 'comprehensive',
                     use_cache: bool = True) -> Dict[str, Any]:
        """
        综合股票分析

        Args:
            symbol: 股票代码
            analysis_type: 分析类型 ('basic', 'technical', 'fundamental', 'comprehensive')
            use_cache: 是否使用缓存

        Returns:
            Dict: 综合分析结果
        """
        try:
            self.logger.info(f"开始分析股票{symbol}，分析类型: {analysis_type}")

            analysis_result = {
                'symbol': symbol,
                'analysis_type': analysis_type,
                'analysis_time': datetime.now().isoformat(),
                'data_sources': [],
                'analysis_results': {}
            }

            # 根据分析类型执行不同的分析
            if analysis_type in ['basic', 'comprehensive']:
                analysis_result['analysis_results'].update(
                    self._perform_basic_analysis(symbol, use_cache)
                )

            if analysis_type in ['technical', 'comprehensive']:
                analysis_result['analysis_results'].update(
                    self._perform_technical_analysis(symbol, use_cache)
                )

            if analysis_type in ['fundamental', 'comprehensive']:
                analysis_result['analysis_results'].update(
                    self._perform_fundamental_analysis(symbol, use_cache)
                )

            # 生成综合评估
            if analysis_type == 'comprehensive':
                analysis_result['comprehensive_assessment'] = self._generate_comprehensive_assessment(
                    analysis_result['analysis_results']
                )

            # 添加风险评估
            analysis_result['risk_assessment'] = self._assess_risk(
                analysis_result['analysis_results']
            )

            # 生成投资建议
            analysis_result['investment_recommendation'] = self._generate_recommendation(
                analysis_result
            )

            self.logger.info(f"股票{symbol}分析完成")
            return analysis_result

        except Exception as e:
            self.logger.error(f"分析股票{symbol}失败: {str(e)}")
            raise

    def _perform_basic_analysis(self, symbol: str, use_cache: bool) -> Dict[str, Any]:
        """执行基本分析"""
        basic_analysis = {}

        try:
            # 获取实时数据
            cache_key = 'realtime' if use_cache and self.cache_manager else None
            realtime_data = self._get_cached_or_fetch(
                lambda: self.realtime_service.get_stock_realtime(symbol),
                symbol, 'realtime', use_cache
            )

            if realtime_data:
                basic_analysis['current_info'] = realtime_data
                basic_analysis['basic_metrics'] = self._extract_basic_metrics(realtime_data)

            # 获取最近30天历史数据
            recent_data = self._get_cached_or_fetch(
                lambda: self.historical_service.get_recent_data(symbol, 30),
                symbol, 'recent_30d', use_cache
            )

            if recent_data is not None and not recent_data.empty:
                basic_analysis['recent_performance'] = self._analyze_recent_performance(recent_data)

            # 获取市场概况
            market_summary = self._get_cached_or_fetch(
                lambda: self.realtime_service.get_market_summary(),
                'market', 'summary', use_cache
            )

            if market_summary:
                basic_analysis['market_context'] = market_summary

        except Exception as e:
            self.logger.warning(f"基本分析执行失败: {str(e)}")

        return basic_analysis

    def _perform_technical_analysis(self, symbol: str, use_cache: bool) -> Dict[str, Any]:
        """执行技术分析"""
        technical_analysis = {}

        try:
            # 获取技术指标
            technical_indicators = self._get_cached_or_fetch(
                lambda: self.market_analysis_service.get_technical_indicators(symbol, 60),
                symbol, 'technical_indicators', use_cache
            )

            if technical_indicators:
                technical_analysis['technical_indicators'] = technical_indicators

            # 获取成交量分析
            volume_analysis = self._get_cached_or_fetch(
                lambda: self.market_analysis_service.get_volume_analysis(symbol, 30),
                symbol, 'volume_analysis', use_cache
            )

            if volume_analysis:
                technical_analysis['volume_analysis'] = volume_analysis

            # 获取换手率分析
            turnover_analysis = self._get_cached_or_fetch(
                lambda: self.market_analysis_service.get_turnover_rate_analysis(symbol, 30),
                symbol, 'turnover_analysis', use_cache
            )

            if turnover_analysis:
                technical_analysis['turnover_analysis'] = turnover_analysis

            # 获取市场情绪
            market_sentiment = self._get_cached_or_fetch(
                lambda: self.market_analysis_service.get_market_sentiment(symbol),
                symbol, 'market_sentiment', use_cache
            )

            if market_sentiment:
                technical_analysis['market_sentiment'] = market_sentiment

        except Exception as e:
            self.logger.warning(f"技术分析执行失败: {str(e)}")

        return technical_analysis

    def _perform_fundamental_analysis(self, symbol: str, use_cache: bool) -> Dict[str, Any]:
        """执行基本面分析"""
        fundamental_analysis = {}

        try:
            # 获取综合财务数据
            financial_data = self._get_cached_or_fetch(
                lambda: self.fundamental_service.get_comprehensive_financial_data(symbol),
                symbol, 'comprehensive_financial', use_cache
            )

            if financial_data:
                fundamental_analysis['financial_data'] = financial_data

            # 计算财务比率
            financial_ratios = self._get_cached_or_fetch(
                lambda: self.fundamental_service.calculate_financial_ratios(symbol),
                symbol, 'financial_ratios', use_cache
            )

            if financial_ratios:
                fundamental_analysis['financial_ratios'] = financial_ratios

            # 获取公司基本信息
            company_profile = self._get_cached_or_fetch(
                lambda: self.fundamental_service.get_company_profile(symbol),
                symbol, 'company_profile', use_cache
            )

            if company_profile:
                fundamental_analysis['company_profile'] = company_profile

            # 获取分红数据
            dividend_data = self._get_cached_or_fetch(
                lambda: self.fundamental_service.get_dividend_data(symbol),
                symbol, 'dividend_data', use_cache
            )

            if dividend_data is not None:
                fundamental_analysis['dividend_analysis'] = self._analyze_dividend(dividend_data)

        except Exception as e:
            self.logger.warning(f"基本面分析执行失败: {str(e)}")

        return fundamental_analysis

    def _get_cached_or_fetch(self, fetch_func, symbol: str, data_type: str,
                           use_cache: bool, **kwargs) -> Any:
        """从缓存获取数据或重新获取"""
        if not use_cache or not self.cache_manager:
            return fetch_func()

        # 尝试从缓存获取
        cached_data = self.cache_manager.get_cached_data(symbol, data_type, **kwargs)
        if cached_data is not None:
            self.logger.debug(f"从缓存获取数据: {symbol}:{data_type}")
            return cached_data

        # 缓存中没有，重新获取
        data = fetch_func()
        if data is not None:
            # 缓存数据
            self.cache_manager.cache_data(symbol, data_type, data, **kwargs)

        return data

    def _extract_basic_metrics(self, realtime_data: Dict) -> Dict[str, Any]:
        """提取基本指标"""
        try:
            metrics = {}

            if 'current_price' in realtime_data:
                metrics['current_price'] = realtime_data['current_price']

            if 'change_percent' in realtime_data:
                metrics['change_percent'] = realtime_data['change_percent']

            if 'volume' in realtime_data:
                metrics['volume'] = realtime_data['volume']

            if 'market_cap' in realtime_data:
                metrics['market_cap'] = realtime_data['market_cap']

            if 'pe_ratio' in realtime_data:
                metrics['pe_ratio'] = realtime_data['pe_ratio']

            if 'pb_ratio' in realtime_data:
                metrics['pb_ratio'] = realtime_data['pb_ratio']

            return metrics

        except Exception as e:
            self.logger.warning(f"提取基本指标失败: {str(e)}")
            return {}

    def _analyze_recent_performance(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析近期表现"""
        try:
            if data.empty:
                return {}

            performance = {}

            # 价格表现
            start_price = float(data.iloc[0]['收盘'])
            end_price = float(data.iloc[-1]['收盘'])
            performance['price_change_percent'] = (end_price - start_price) / start_price * 100

            # 最高最低价
            performance['period_high'] = float(data['最高'].max())
            performance['period_low'] = float(data['最低'].min())

            # 平均成交量
            performance['avg_volume'] = int(data['成交量'].mean())

            # 波动率
            if '涨跌幅' in data.columns:
                performance['volatility'] = float(data['涨跌幅'].std())

            # 上涨天数和下跌天数
            if '涨跌幅' in data.columns:
                up_days = len(data[data['涨跌幅'] > 0])
                down_days = len(data[data['涨跌幅'] < 0])
                performance['up_days'] = up_days
                performance['down_days'] = down_days
                performance['up_down_ratio'] = up_days / down_days if down_days > 0 else float('inf')

            return performance

        except Exception as e:
            self.logger.warning(f"分析近期表现失败: {str(e)}")
            return {}

    def _analyze_dividend(self, dividend_data: pd.DataFrame) -> Dict[str, Any]:
        """分析分红数据"""
        try:
            if dividend_data.empty:
                return {'has_dividend': False}

            analysis = {'has_dividend': True}

            # 计算近年分红情况
            if '分红年度' in dividend_data.columns and '每股分红' in dividend_data.columns:
                recent_dividends = dividend_data.head(5)  # 最近5年
                analysis['recent_dividend_years'] = len(recent_dividends)
                analysis['avg_dividend_per_share'] = float(recent_dividends['每股分红'].mean())
                analysis['dividend_consistency'] = len(recent_dividends[recent_dividends['每股分红'] > 0])

            return analysis

        except Exception as e:
            self.logger.warning(f"分析分红数据失败: {str(e)}")
            return {'has_dividend': False}

    def _generate_comprehensive_assessment(self, analysis_results: Dict) -> Dict[str, Any]:
        """生成综合评估"""
        try:
            assessment = {
                'overall_score': 0.0,
                'strengths': [],
                'weaknesses': [],
                'key_metrics': {}
            }

            score_components = []

            # 基本面评分
            if 'financial_ratios' in analysis_results:
                ratios = analysis_results['financial_ratios']
                fundamental_score = self._score_fundamental_metrics(ratios)
                score_components.append(('fundamental', fundamental_score, 0.4))

            # 技术面评分
            if 'technical_indicators' in analysis_results:
                indicators = analysis_results['technical_indicators']
                technical_score = self._score_technical_metrics(indicators)
                score_components.append(('technical', technical_score, 0.3))

            # 市场情绪评分
            if 'market_sentiment' in analysis_results:
                sentiment = analysis_results['market_sentiment']
                sentiment_score = sentiment.get('sentiment_score', 0.5)
                score_components.append(('sentiment', sentiment_score, 0.3))

            # 计算加权总分
            if score_components:
                total_weight = sum([weight for _, _, weight in score_components])
                weighted_score = sum([score * weight for _, score, weight in score_components])
                assessment['overall_score'] = weighted_score / total_weight
                assessment['score_components'] = {
                    name: {'score': score, 'weight': weight}
                    for name, score, weight in score_components
                }

            # 确定优势和劣势
            assessment['strengths'], assessment['weaknesses'] = self._identify_strengths_weaknesses(
                analysis_results, assessment['overall_score']
            )

            return assessment

        except Exception as e:
            self.logger.warning(f"生成综合评估失败: {str(e)}")
            return {'overall_score': 0.5, 'strengths': [], 'weaknesses': []}

    def _score_fundamental_metrics(self, ratios: Dict) -> float:
        """评分基本面指标"""
        try:
            scores = []

            # ROE评分
            if 'roe' in ratios:
                roe = ratios['roe']
                if roe > 0.15:
                    scores.append(0.9)
                elif roe > 0.10:
                    scores.append(0.7)
                elif roe > 0.05:
                    scores.append(0.5)
                else:
                    scores.append(0.3)

            # 资产负债率评分
            if 'debt_to_asset_ratio' in ratios:
                debt_ratio = ratios['debt_to_asset_ratio']
                if debt_ratio < 0.3:
                    scores.append(0.9)
                elif debt_ratio < 0.5:
                    scores.append(0.7)
                elif debt_ratio < 0.7:
                    scores.append(0.5)
                else:
                    scores.append(0.3)

            # 流动比率评分
            if 'current_ratio' in ratios:
                current_ratio = ratios['current_ratio']
                if current_ratio > 2:
                    scores.append(0.9)
                elif current_ratio > 1.5:
                    scores.append(0.7)
                elif current_ratio > 1:
                    scores.append(0.5)
                else:
                    scores.append(0.3)

            return np.mean(scores) if scores else 0.5

        except Exception:
            return 0.5

    def _score_technical_metrics(self, indicators: Dict) -> float:
        """评分技术指标"""
        try:
            scores = []

            # RSI评分
            if 'rsi_14' in indicators:
                rsi = indicators['rsi_14']
                if 30 <= rsi <= 70:
                    scores.append(0.7)
                elif rsi < 30:
                    scores.append(0.9)  # 超卖，可能反弹
                elif rsi > 70:
                    scores.append(0.3)  # 超买，风险较高
                else:
                    scores.append(0.5)

            # 趋势评分
            if 'trend_analysis' in indicators:
                trend = indicators['trend_analysis']
                if trend.get('trend_consistency', False):
                    if trend.get('long_term') == 'upward':
                        scores.append(0.8)
                    elif trend.get('long_term') == 'sideways':
                        scores.append(0.5)
                    else:
                        scores.append(0.3)

            return np.mean(scores) if scores else 0.5

        except Exception:
            return 0.5

    def _identify_strengths_weaknesses(self, analysis_results: Dict,
                                     overall_score: float) -> Tuple[List[str], List[str]]:
        """识别优势和劣势"""
        strengths = []
        weaknesses = []

        try:
            # 基于基本面
            if 'financial_ratios' in analysis_results:
                ratios = analysis_results['financial_ratios']
                if ratios.get('roe', 0) > 0.15:
                    strengths.append('净资产收益率较高')
                elif ratios.get('roe', 0) < 0.05:
                    weaknesses.append('净资产收益率偏低')

                if ratios.get('debt_to_asset_ratio', 1) < 0.3:
                    strengths.append('负债率较低，财务稳健')
                elif ratios.get('debt_to_asset_ratio', 0) > 0.7:
                    weaknesses.append('负债率较高，财务风险大')

            # 基于技术面
            if 'market_sentiment' in analysis_results:
                sentiment = analysis_results['market_sentiment']
                if sentiment.get('overall_sentiment') == 'bullish':
                    strengths.append('市场情绪乐观')
                elif sentiment.get('overall_sentiment') == 'bearish':
                    weaknesses.append('市场情绪悲观')

            # 基于成交量
            if 'volume_analysis' in analysis_results:
                volume_analysis = analysis_results['volume_analysis']
                if volume_analysis.get('volume_trend') == 'upward':
                    strengths.append('成交量呈上升趋势')
                elif volume_analysis.get('volume_trend') == 'downward':
                    weaknesses.append('成交量呈下降趋势')

            return strengths, weaknesses

        except Exception as e:
            self.logger.warning(f"识别优势劣势失败: {str(e)}")
            return [], []

    def _assess_risk(self, analysis_results: Dict) -> Dict[str, Any]:
        """评估投资风险"""
        try:
            risk_assessment = {
                'overall_risk_level': 'medium',
                'risk_factors': [],
                'risk_score': 0.5
            }

            risk_factors = []

            # 基于波动率的风险
            if 'recent_performance' in analysis_results:
                performance = analysis_results['recent_performance']
                if performance.get('volatility', 0) > 5:
                    risk_factors.append('股价波动率较高')

            # 基于财务风险
            if 'financial_ratios' in analysis_results:
                ratios = analysis_results['financial_ratios']
                if ratios.get('debt_to_asset_ratio', 0) > 0.7:
                    risk_factors.append('负债率过高')

            # 基于市场情绪风险
            if 'market_sentiment' in analysis_results:
                sentiment = analysis_results['market_sentiment']
                if sentiment.get('overall_sentiment') == 'bearish':
                    risk_factors.append('市场情绪偏悲观')

            risk_assessment['risk_factors'] = risk_factors

            # 计算风险评分
            risk_score = len(risk_factors) * 0.2
            risk_assessment['risk_score'] = min(risk_score, 1.0)

            # 确定风险等级
            if risk_assessment['risk_score'] < 0.3:
                risk_assessment['overall_risk_level'] = 'low'
            elif risk_assessment['risk_score'] < 0.7:
                risk_assessment['overall_risk_level'] = 'medium'
            else:
                risk_assessment['overall_risk_level'] = 'high'

            return risk_assessment

        except Exception as e:
            self.logger.warning(f"风险评估失败: {str(e)}")
            return {'overall_risk_level': 'medium', 'risk_factors': [], 'risk_score': 0.5}

    def _generate_recommendation(self, analysis_result: Dict) -> Dict[str, Any]:
        """生成投资建议"""
        try:
            recommendation = {
                'action': 'hold',
                'confidence': 0.5,
                'reasoning': [],
                'target_price': None,
                'time_horizon': 'medium_term'
            }

            overall_score = analysis_result.get('comprehensive_assessment', {}).get('overall_score', 0.5)
            risk_level = analysis_result.get('risk_assessment', {}).get('overall_risk_level', 'medium')

            # 基于综合评分和风险水平生成建议
            if overall_score > 0.7 and risk_level != 'high':
                recommendation['action'] = 'buy'
                recommendation['confidence'] = 0.8
                recommendation['reasoning'].append('综合评分较高且风险可控')
            elif overall_score < 0.3 or risk_level == 'high':
                recommendation['action'] = 'sell'
                recommendation['confidence'] = 0.7
                recommendation['reasoning'].append('综合评分较低或风险较高')
            else:
                recommendation['action'] = 'hold'
                recommendation['confidence'] = 0.6
                recommendation['reasoning'].append('综合评分中等，建议观望')

            # 基于技术指标调整建议
            technical_indicators = analysis_result.get('analysis_results', {}).get('technical_indicators', {})
            if technical_indicators:
                rsi = technical_indicators.get('rsi_14')
                if rsi and rsi < 30:
                    recommendation['reasoning'].append('RSI显示超卖，可能存在反弹机会')
                elif rsi and rsi > 70:
                    recommendation['reasoning'].append('RSI显示超买，存在回调风险')

            return recommendation

        except Exception as e:
            self.logger.warning(f"生成投资建议失败: {str(e)}")
            return {
                'action': 'hold',
                'confidence': 0.5,
                'reasoning': ['分析数据不足，建议谨慎观望'],
                'target_price': None,
                'time_horizon': 'medium_term'
            }

    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        try:
            stats = {
                'api_monitor': api_monitor.get_statistics(),
                'cache_stats': self.cache_manager.get_cache_stats() if self.cache_manager else {},
                'services_status': {
                    'realtime_service': 'active',
                    'historical_service': 'active',
                    'fundamental_service': 'active',
                    'market_analysis_service': 'active'
                }
            }

            return stats

        except Exception as e:
            self.logger.error(f"获取系统统计失败: {str(e)}")
            return {}

    def cleanup_cache(self) -> Dict[str, int]:
        """清理缓存"""
        if not self.cache_manager:
            return {'cleared_items': 0, 'expired_items': 0}

        try:
            cleared_items = self.cache_manager.clear_cache()
            expired_items = self.cache_manager.cleanup_expired_cache()

            return {
                'cleared_items': cleared_items,
                'expired_items': expired_items
            }

        except Exception as e:
            self.logger.error(f"清理缓存失败: {str(e)}")
            return {'cleared_items': 0, 'expired_items': 0}
"""
市场分析数据服务模块
提供股票市场分析相关数据获取功能
"""

import akshare as ak
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, List
import logging
from .utils.retry_decorator import retry_on_failure

logger = logging.getLogger(__name__)


class MarketAnalysisService:
    """市场分析数据服务"""

    def __init__(self):
        self.logger = logger

    @retry_on_failure(max_retries=3)
    def get_turnover_rate_analysis(self, symbol: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """
        获取换手率分析数据

        Args:
            symbol: 股票代码
            days: 分析天数

        Returns:
            Dict: 换手率分析结果
        """
        try:
            from .historical_data_service import HistoricalDataService

            self.logger.info(f"正在分析股票{symbol}的换手率数据...")

            historical_service = HistoricalDataService()
            data = historical_service.get_recent_data(symbol, days)

            if data is None or data.empty:
                self.logger.warning(f"股票{symbol}历史数据为空，无法分析换手率")
                return None

            if '换手率' not in data.columns:
                self.logger.warning(f"股票{symbol}数据中没有换手率信息")
                return None

            turnover_rates = data['换手率'].dropna()

            analysis = {
                'symbol': symbol,
                'period_days': days,
                'current_turnover_rate': float(turnover_rates.iloc[-1]) if len(turnover_rates) > 0 else None,
                'avg_turnover_rate': float(turnover_rates.mean()),
                'max_turnover_rate': float(turnover_rates.max()),
                'min_turnover_rate': float(turnover_rates.min()),
                'turnover_volatility': float(turnover_rates.std()),
                'high_turnover_days': int((turnover_rates > turnover_rates.mean() + turnover_rates.std()).sum()),
                'low_turnover_days': int((turnover_rates < turnover_rates.mean() - turnover_rates.std()).sum()),
                'turnover_trend': self._calculate_trend(turnover_rates)
            }

            # 活跃度评级
            analysis['activity_level'] = self._evaluate_activity_level(analysis['avg_turnover_rate'])

            self.logger.info(f"成功分析股票{symbol}换手率数据")
            return analysis

        except Exception as e:
            self.logger.error(f"分析股票{symbol}换手率失败: {str(e)}")
            raise

    @retry_on_failure(max_retries=3)
    def get_volume_analysis(self, symbol: str, days: int = 30) -> Optional[Dict[str, Any]]:
        """
        获取成交量分析数据

        Args:
            symbol: 股票代码
            days: 分析天数

        Returns:
            Dict: 成交量分析结果
        """
        try:
            from .historical_data_service import HistoricalDataService

            self.logger.info(f"正在分析股票{symbol}的成交量数据...")

            historical_service = HistoricalDataService()
            data = historical_service.get_recent_data(symbol, days)

            if data is None or data.empty:
                self.logger.warning(f"股票{symbol}历史数据为空，无法分析成交量")
                return None

            volumes = data['成交量'].dropna()
            prices = data['收盘'].dropna()

            analysis = {
                'symbol': symbol,
                'period_days': days,
                'current_volume': int(volumes.iloc[-1]) if len(volumes) > 0 else None,
                'avg_volume': int(volumes.mean()),
                'max_volume': int(volumes.max()),
                'min_volume': int(volumes.min()),
                'volume_volatility': float(volumes.std()),
                'volume_trend': self._calculate_trend(volumes),
                'price_volume_correlation': float(np.corrcoef(prices, volumes[:len(prices)])[0, 1]) if len(prices) > 1 else None
            }

            # 量价关系分析
            analysis['volume_price_relationship'] = self._analyze_volume_price_relationship(data)

            # 成交量异常检测
            analysis['volume_anomalies'] = self._detect_volume_anomalies(volumes)

            self.logger.info(f"成功分析股票{symbol}成交量数据")
            return analysis

        except Exception as e:
            self.logger.error(f"分析股票{symbol}成交量失败: {str(e)}")
            raise

    @retry_on_failure(max_retries=3)
    def get_money_flow(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        获取资金流向数据

        Args:
            symbol: 股票代码

        Returns:
            pd.DataFrame: 资金流向数据
        """
        try:
            self.logger.info(f"正在获取股票{symbol}资金流向数据...")
            data = ak.stock_individual_fund_flow(stock=symbol)

            if data is None or data.empty:
                self.logger.warning(f"股票{symbol}资金流向数据为空")
                return None

            self.logger.info(f"成功获取股票{symbol}资金流向数据，共{len(data)}条记录")
            return data
        except Exception as e:
            self.logger.error(f"获取股票{symbol}资金流向数据失败: {str(e)}")
            raise

    def get_technical_indicators(self, symbol: str, days: int = 60) -> Optional[Dict[str, Any]]:
        """
        计算技术指标

        Args:
            symbol: 股票代码
            days: 计算天数

        Returns:
            Dict: 技术指标数据
        """
        try:
            from .historical_data_service import HistoricalDataService

            self.logger.info(f"正在计算股票{symbol}技术指标...")

            historical_service = HistoricalDataService()
            data = historical_service.get_recent_data(symbol, days)

            if data is None or data.empty:
                self.logger.warning(f"股票{symbol}历史数据为空，无法计算技术指标")
                return None

            indicators = {
                'symbol': symbol,
                'calculation_date': data.iloc[-1]['日期'].strftime('%Y-%m-%d') if '日期' in data.columns else None,
                'sma_5': self._calculate_sma(data['收盘'], 5),
                'sma_10': self._calculate_sma(data['收盘'], 10),
                'sma_20': self._calculate_sma(data['收盘'], 20),
                'sma_60': self._calculate_sma(data['收盘'], 60),
                'ema_12': self._calculate_ema(data['收盘'], 12),
                'ema_26': self._calculate_ema(data['收盘'], 26),
                'rsi_14': self._calculate_rsi(data['收盘'], 14),
                'macd': self._calculate_macd(data['收盘']),
                'bollinger_bands': self._calculate_bollinger_bands(data['收盘'], 20),
                'support_resistance': self._identify_support_resistance(data)
            }

            # 趋势判断
            indicators['trend_analysis'] = self._analyze_trend(data)

            self.logger.info(f"成功计算股票{symbol}技术指标")
            return indicators

        except Exception as e:
            self.logger.error(f"计算股票{symbol}技术指标失败: {str(e)}")
            raise

    def get_market_sentiment(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取市场情绪分析

        Args:
            symbol: 股票代码

        Returns:
            Dict: 市场情绪分析结果
        """
        try:
            self.logger.info(f"正在分析股票{symbol}市场情绪...")

            # 获取各种数据进行情绪分析
            turnover_analysis = self.get_turnover_rate_analysis(symbol, 10)
            volume_analysis = self.get_volume_analysis(symbol, 10)
            money_flow = self.get_money_flow(symbol)

            sentiment = {
                'symbol': symbol,
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.0,
                'indicators': {}
            }

            # 基于换手率的情绪分析
            if turnover_analysis:
                turnover_score = self._score_turnover_sentiment(turnover_analysis)
                sentiment['indicators']['turnover_sentiment'] = turnover_score

            # 基于成交量的情绪分析
            if volume_analysis:
                volume_score = self._score_volume_sentiment(volume_analysis)
                sentiment['indicators']['volume_sentiment'] = volume_score

            # 基于资金流向的情绪分析
            if money_flow is not None and not money_flow.empty:
                flow_score = self._score_money_flow_sentiment(money_flow)
                sentiment['indicators']['money_flow_sentiment'] = flow_score

            # 综合情绪评分
            sentiment_scores = [score for score in sentiment['indicators'].values() if score is not None]
            if sentiment_scores:
                sentiment['sentiment_score'] = np.mean(sentiment_scores)
                sentiment['overall_sentiment'] = self._classify_sentiment(sentiment['sentiment_score'])

            self.logger.info(f"成功分析股票{symbol}市场情绪")
            return sentiment

        except Exception as e:
            self.logger.error(f"分析股票{symbol}市场情绪失败: {str(e)}")
            raise

    def _calculate_trend(self, series: pd.Series) -> str:
        """计算趋势方向"""
        if len(series) < 2:
            return 'insufficient_data'

        # 使用线性回归计算趋势
        x = np.arange(len(series))
        coefficients = np.polyfit(x, series, 1)
        slope = coefficients[0]

        if slope > 0.01:
            return 'upward'
        elif slope < -0.01:
            return 'downward'
        else:
            return 'sideways'

    def _evaluate_activity_level(self, avg_turnover_rate: float) -> str:
        """评估交易活跃度"""
        if avg_turnover_rate >= 10:
            return 'very_high'
        elif avg_turnover_rate >= 5:
            return 'high'
        elif avg_turnover_rate >= 2:
            return 'moderate'
        elif avg_turnover_rate >= 0.5:
            return 'low'
        else:
            return 'very_low'

    def _analyze_volume_price_relationship(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析量价关系"""
        try:
            if '涨跌幅' not in data.columns or '成交量' not in data.columns:
                return {}

            # 获取最近几天的数据
            recent_data = data.tail(5)

            # 上涨日成交量
            up_days = recent_data[recent_data['涨跌幅'] > 0]
            # 下跌日成交量
            down_days = recent_data[recent_data['涨跌幅'] < 0]

            analysis = {
                'up_volume_avg': float(up_days['成交量'].mean()) if not up_days.empty else 0,
                'down_volume_avg': float(down_days['成交量'].mean()) if not down_days.empty else 0,
                'up_days_count': len(up_days),
                'down_days_count': len(down_days)
            }

            # 判断量价配合情况
            if analysis['up_volume_avg'] > analysis['down_volume_avg'] * 1.2:
                analysis['relationship'] = 'price_up_volume_up'  # 价升量增
            elif analysis['down_volume_avg'] > analysis['up_volume_avg'] * 1.2:
                analysis['relationship'] = 'price_down_volume_up'  # 价跌量增
            else:
                analysis['relationship'] = 'neutral'

            return analysis

        except Exception as e:
            self.logger.warning(f"分析量价关系失败: {str(e)}")
            return {}

    def _detect_volume_anomalies(self, volumes: pd.Series) -> List[Dict[str, Any]]:
        """检测成交量异常"""
        try:
            anomalies = []
            mean_volume = volumes.mean()
            std_volume = volumes.std()

            # 异常阈值（超过2个标准差）
            threshold = mean_volume + 2 * std_volume

            for i, volume in enumerate(volumes):
                if volume > threshold:
                    anomalies.append({
                        'index': i,
                        'volume': int(volume),
                        'deviation_ratio': float(volume / mean_volume),
                        'type': 'high_volume'
                    })

            return anomalies

        except Exception as e:
            self.logger.warning(f"检测成交量异常失败: {str(e)}")
            return []

    def _calculate_sma(self, prices: pd.Series, period: int) -> Optional[float]:
        """计算简单移动平均"""
        if len(prices) < period:
            return None
        return float(prices.tail(period).mean())

    def _calculate_ema(self, prices: pd.Series, period: int) -> Optional[float]:
        """计算指数移动平均"""
        if len(prices) < period:
            return None
        return float(prices.ewm(span=period).mean().iloc[-1])

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """计算RSI指标"""
        if len(prices) < period + 1:
            return None

        deltas = prices.diff()
        gains = deltas.where(deltas > 0, 0)
        losses = -deltas.where(deltas < 0, 0)

        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()

        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))

        return float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else None

    def _calculate_macd(self, prices: pd.Series) -> Optional[Dict[str, float]]:
        """计算MACD指标"""
        if len(prices) < 26:
            return None

        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal_line

        return {
            'macd': float(macd_line.iloc[-1]),
            'signal': float(signal_line.iloc[-1]),
            'histogram': float(histogram.iloc[-1])
        }

    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> Optional[Dict[str, float]]:
        """计算布林带"""
        if len(prices) < period:
            return None

        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()

        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)

        return {
            'upper': float(upper_band.iloc[-1]),
            'middle': float(sma.iloc[-1]),
            'lower': float(lower_band.iloc[-1]),
            'current_price': float(prices.iloc[-1])
        }

    def _identify_support_resistance(self, data: pd.DataFrame) -> Dict[str, Any]:
        """识别支撑阻力位"""
        try:
            highs = data['最高'].tail(30)
            lows = data['最低'].tail(30)

            # 简单的支撑阻力识别
            resistance = float(highs.quantile(0.9))  # 90分位数作为阻力位
            support = float(lows.quantile(0.1))      # 10分位数作为支撑位

            current_price = float(data.iloc[-1]['收盘'])

            return {
                'resistance': resistance,
                'support': support,
                'current_price': current_price,
                'distance_to_resistance': (resistance - current_price) / current_price * 100,
                'distance_to_support': (current_price - support) / current_price * 100
            }

        except Exception as e:
            self.logger.warning(f"识别支撑阻力位失败: {str(e)}")
            return {}

    def _analyze_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析价格趋势"""
        try:
            prices = data['收盘'].tail(20)

            # 短期趋势（5天）
            short_trend = self._calculate_trend(prices.tail(5))

            # 中期趋势（10天）
            medium_trend = self._calculate_trend(prices.tail(10))

            # 长期趋势（20天）
            long_trend = self._calculate_trend(prices)

            return {
                'short_term': short_trend,
                'medium_term': medium_trend,
                'long_term': long_trend,
                'trend_consistency': short_trend == medium_trend == long_trend
            }

        except Exception as e:
            self.logger.warning(f"分析趋势失败: {str(e)}")
            return {}

    def _score_turnover_sentiment(self, turnover_analysis: Dict) -> Optional[float]:
        """基于换手率评分情绪"""
        try:
            activity_scores = {
                'very_high': 0.8,
                'high': 0.6,
                'moderate': 0.5,
                'low': 0.3,
                'very_low': 0.1
            }

            activity_score = activity_scores.get(turnover_analysis.get('activity_level'), 0.5)

            # 考虑趋势
            trend = turnover_analysis.get('turnover_trend')
            if trend == 'upward':
                activity_score += 0.1
            elif trend == 'downward':
                activity_score -= 0.1

            return max(0.0, min(1.0, activity_score))

        except Exception:
            return None

    def _score_volume_sentiment(self, volume_analysis: Dict) -> Optional[float]:
        """基于成交量评分情绪"""
        try:
            current_volume = volume_analysis.get('current_volume', 0)
            avg_volume = volume_analysis.get('avg_volume', 1)

            # 当前成交量与平均成交量的比率
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

            if volume_ratio > 2:
                score = 0.8  # 高成交量
            elif volume_ratio > 1.5:
                score = 0.7
            elif volume_ratio > 1.2:
                score = 0.6
            elif volume_ratio > 0.8:
                score = 0.5
            else:
                score = 0.3  # 低成交量

            return score

        except Exception:
            return None

    def _score_money_flow_sentiment(self, money_flow: pd.DataFrame) -> Optional[float]:
        """基于资金流向评分情绪"""
        try:
            if money_flow.empty:
                return None

            # 获取最新的资金流向数据
            latest = money_flow.iloc[-1]

            # 假设数据包含主力净流入等字段
            if '主力净流入' in money_flow.columns:
                net_inflow = latest['主力净流入']
                if net_inflow > 0:
                    return 0.7  # 资金流入
                else:
                    return 0.3  # 资金流出

            return 0.5  # 中性

        except Exception:
            return None

    def _classify_sentiment(self, score: float) -> str:
        """将情绪评分转换为分类"""
        if score >= 0.7:
            return 'bullish'
        elif score >= 0.6:
            return 'moderately_bullish'
        elif score >= 0.4:
            return 'neutral'
        elif score >= 0.3:
            return 'moderately_bearish'
        else:
            return 'bearish'
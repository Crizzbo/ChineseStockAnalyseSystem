"""
股票基本面分析服务 - 基于AkShare
"""
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
import time
import threading
from app.utils.data_cache_manager import cache_manager

logger = logging.getLogger(__name__)

class FundamentalAnalysisService:
    """股票基本面分析服务类"""

    def __init__(self):
        self._cache = {}
        self._cache_duration = 3600  # 缓存1小时

    def _retry_akshare_call(self, func, max_retries: int = 3, delay: int = 1, timeout: int = 30):
        """重试AkShare调用，带超时控制"""
        for attempt in range(max_retries):
            try:
                result = [None]
                exception = [None]

                def target():
                    try:
                        result[0] = func()
                    except Exception as e:
                        exception[0] = e

                thread = threading.Thread(target=target)
                thread.daemon = True
                thread.start()
                thread.join(timeout=timeout)

                if thread.is_alive():
                    logger.warning(f"API调用超时 ({timeout}秒)")
                    raise TimeoutError(f"API调用超时 ({timeout}秒)")

                if exception[0]:
                    raise exception[0]

                return result[0]

            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logger.warning(f"AkShare调用失败，重试 {attempt + 1}/{max_retries}: {e}")
                time.sleep(delay * (attempt + 1))

    def _safe_float(self, value, default=0.0):
        """安全转换为浮点数"""
        try:
            if value is None or value == '-' or value == '' or pd.isna(value):
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

    def get_financial_indicators(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票财务指标
        包括：营业收入、净利润、资产负债、现金流等
        """
        def fetch_data():
            try:
                df = self._retry_akshare_call(
                    lambda: ak.stock_financial_analysis_indicator(symbol=symbol),
                    max_retries=3,
                    delay=2
                )
                if df is None or df.empty:
                    logger.warning(f"未获取到财务指标数据: {symbol}")
                    return None
                return df
            except Exception as e:
                logger.error(f"获取财务指标失败 {symbol}: {e}")
                return None

        # 使用缓存管理器
        df = cache_manager.get_or_update(
            data_type='financial_indicators',
            identifier=symbol,
            data_fetcher=fetch_data,
            max_age_hours=24  # 24小时更新一次
        )

        if df is None or df.empty:
            return {}

        # 取最近一期数据
        latest = df.iloc[-1] if not df.empty else None
        if latest is None:
            return {}

        indicators = {
            'date': str(latest.get('日期', '')),
            'revenue': self._safe_float(latest.get('营业收入', 0)),
            'net_profit': self._safe_float(latest.get('净利润', 0)),
            'total_assets': self._safe_float(latest.get('总资产', 0)),
            'total_liabilities': self._safe_float(latest.get('总负债', 0)),
            'net_assets': self._safe_float(latest.get('净资产', 0)),
            'operating_cash_flow': self._safe_float(latest.get('经营现金流', 0)),
            'roe': self._safe_float(latest.get('净资产收益率', 0)),
            'roa': self._safe_float(latest.get('总资产收益率', 0)),
            'gross_margin': self._safe_float(latest.get('销售毛利率', 0)),
            'net_margin': self._safe_float(latest.get('销售净利率', 0)),
        }

        return indicators

    def get_profitability_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        获取盈利能力分析
        指标：净利率、ROE、ROA、毛利率
        """
        try:
            indicators = self.get_financial_indicators(symbol)

            if not indicators:
                return {}

            # 计算盈利能力评分 (0-100)
            profitability_score = 0

            # ROE评分 (>15%优秀, >10%良好, >5%一般)
            roe = indicators.get('roe', 0)
            if roe > 15:
                roe_score = 100
            elif roe > 10:
                roe_score = 75
            elif roe > 5:
                roe_score = 50
            else:
                roe_score = 25

            # 毛利率评分
            gross_margin = indicators.get('gross_margin', 0)
            if gross_margin > 40:
                margin_score = 100
            elif gross_margin > 30:
                margin_score = 75
            elif gross_margin > 20:
                margin_score = 50
            else:
                margin_score = 25

            # 净利率评分
            net_margin = indicators.get('net_margin', 0)
            if net_margin > 20:
                net_margin_score = 100
            elif net_margin > 10:
                net_margin_score = 75
            elif net_margin > 5:
                net_margin_score = 50
            else:
                net_margin_score = 25

            profitability_score = (roe_score * 0.4 + margin_score * 0.3 + net_margin_score * 0.3)

            return {
                'indicators': {
                    'roe': roe,
                    'roa': indicators.get('roa', 0),
                    'gross_margin': gross_margin,
                    'net_margin': net_margin,
                },
                'score': round(profitability_score, 2),
                'level': self._get_score_level(profitability_score),
                'analysis': self._generate_profitability_analysis(indicators)
            }

        except Exception as e:
            logger.error(f"获取盈利能力分析失败 {symbol}: {e}")
            return {}

    def get_solvency_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        获取偿债能力分析
        指标：流动比率、速动比率、资产负债率
        """
        try:
            indicators = self.get_financial_indicators(symbol)

            if not indicators:
                return {}

            # 计算偿债能力指标
            total_assets = indicators.get('total_assets', 0)
            total_liabilities = indicators.get('total_liabilities', 0)
            net_assets = indicators.get('net_assets', 0)

            # 资产负债率
            debt_ratio = (total_liabilities / total_assets * 100) if total_assets > 0 else 0

            # 偿债能力评分
            solvency_score = 0

            # 资产负债率评分 (越低越好, <40%优秀, <60%良好, <80%一般)
            if debt_ratio < 40:
                debt_score = 100
            elif debt_ratio < 60:
                debt_score = 75
            elif debt_ratio < 80:
                debt_score = 50
            else:
                debt_score = 25

            solvency_score = debt_score

            return {
                'indicators': {
                    'debt_ratio': round(debt_ratio, 2),
                    'total_assets': total_assets,
                    'total_liabilities': total_liabilities,
                    'net_assets': net_assets,
                },
                'score': round(solvency_score, 2),
                'level': self._get_score_level(solvency_score),
                'analysis': self._generate_solvency_analysis(debt_ratio)
            }

        except Exception as e:
            logger.error(f"获取偿债能力分析失败 {symbol}: {e}")
            return {}

    def get_growth_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        获取成长性分析
        指标：营业收入增长率、净利润增长率
        """
        try:
            # 获取财务指标历史数据
            def get_financial_data():
                return ak.stock_financial_analysis_indicator(symbol=symbol)

            df = self._retry_akshare_call(get_financial_data, max_retries=3, delay=2)

            if df is None or df.empty or len(df) < 2:
                logger.warning(f"未获取到足够的历史数据: {symbol}")
                return {}

            # 取最近两期数据
            latest = df.iloc[-1]
            previous = df.iloc[-2]

            # 计算增长率
            revenue_latest = self._safe_float(latest.get('营业收入', 0))
            revenue_previous = self._safe_float(previous.get('营业收入', 0))
            revenue_growth = ((revenue_latest - revenue_previous) / revenue_previous * 100) if revenue_previous > 0 else 0

            profit_latest = self._safe_float(latest.get('净利润', 0))
            profit_previous = self._safe_float(previous.get('净利润', 0))
            profit_growth = ((profit_latest - profit_previous) / profit_previous * 100) if profit_previous > 0 else 0

            # 成长性评分
            growth_score = 0

            # 收入增长评分
            if revenue_growth > 30:
                revenue_score = 100
            elif revenue_growth > 20:
                revenue_score = 80
            elif revenue_growth > 10:
                revenue_score = 60
            elif revenue_growth > 0:
                revenue_score = 40
            else:
                revenue_score = 20

            # 利润增长评分
            if profit_growth > 30:
                profit_score = 100
            elif profit_growth > 20:
                profit_score = 80
            elif profit_growth > 10:
                profit_score = 60
            elif profit_growth > 0:
                profit_score = 40
            else:
                profit_score = 20

            growth_score = (revenue_score * 0.5 + profit_score * 0.5)

            return {
                'indicators': {
                    'revenue_growth': round(revenue_growth, 2),
                    'profit_growth': round(profit_growth, 2),
                    'revenue_latest': revenue_latest,
                    'profit_latest': profit_latest,
                },
                'score': round(growth_score, 2),
                'level': self._get_score_level(growth_score),
                'analysis': self._generate_growth_analysis(revenue_growth, profit_growth)
            }

        except Exception as e:
            logger.error(f"获取成长性分析失败 {symbol}: {e}")
            return {}

    def get_valuation_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        获取估值分析
        指标：PE、PB、市值
        """
        try:
            # 获取实时股票数据
            def get_stock_data():
                return ak.stock_zh_a_spot_em()

            spot_df = self._retry_akshare_call(get_stock_data, max_retries=3, delay=1)

            if spot_df is None or spot_df.empty:
                return {}

            # 查找指定股票
            stock_data = spot_df[spot_df['代码'] == symbol]

            if stock_data.empty:
                return {}

            row = stock_data.iloc[0]

            pe = self._safe_float(row.get('市盈率-动态', 0))
            pb = self._safe_float(row.get('市净率', 0))
            market_cap = self._safe_float(row.get('总市值', 0))
            current_price = self._safe_float(row.get('最新价', 0))

            # 估值评分 (PE和PB越低越好,但要合理)
            valuation_score = 0

            # PE评分 (10-20合理, <10可能低估, >30可能高估)
            if 10 <= pe <= 20:
                pe_score = 100
            elif 5 <= pe < 10 or 20 < pe <= 30:
                pe_score = 75
            elif 0 < pe < 5 or 30 < pe <= 50:
                pe_score = 50
            else:
                pe_score = 25

            # PB评分 (1-3合理, <1可能低估, >5可能高估)
            if 1 <= pb <= 3:
                pb_score = 100
            elif 0.5 <= pb < 1 or 3 < pb <= 5:
                pb_score = 75
            elif pb < 0.5 or 5 < pb <= 8:
                pb_score = 50
            else:
                pb_score = 25

            valuation_score = (pe_score * 0.5 + pb_score * 0.5)

            return {
                'indicators': {
                    'pe': pe,
                    'pb': pb,
                    'market_cap': market_cap,
                    'current_price': current_price,
                },
                'score': round(valuation_score, 2),
                'level': self._get_score_level(valuation_score),
                'analysis': self._generate_valuation_analysis(pe, pb)
            }

        except Exception as e:
            logger.error(f"获取估值分析失败 {symbol}: {e}")
            return {}

    def calculate_fundamental_score(self, symbol: str) -> Dict[str, Any]:
        """
        计算基本面综合评分
        综合盈利能力、偿债能力、成长性、估值等维度
        """
        try:
            # 获取各维度分析
            profitability = self.get_profitability_analysis(symbol)
            solvency = self.get_solvency_analysis(symbol)
            growth = self.get_growth_analysis(symbol)
            valuation = self.get_valuation_analysis(symbol)

            # 计算综合评分 (各维度权重)
            weights = {
                'profitability': 0.3,  # 盈利能力权重30%
                'solvency': 0.2,       # 偿债能力权重20%
                'growth': 0.3,         # 成长性权重30%
                'valuation': 0.2,      # 估值权重20%
            }

            total_score = 0
            dimension_scores = {}

            if profitability and 'score' in profitability:
                score = profitability['score']
                total_score += score * weights['profitability']
                dimension_scores['profitability'] = score

            if solvency and 'score' in solvency:
                score = solvency['score']
                total_score += score * weights['solvency']
                dimension_scores['solvency'] = score

            if growth and 'score' in growth:
                score = growth['score']
                total_score += score * weights['growth']
                dimension_scores['growth'] = score

            if valuation and 'score' in valuation:
                score = valuation['score']
                total_score += score * weights['valuation']
                dimension_scores['valuation'] = score

            return {
                'total_score': round(total_score, 2),
                'level': self._get_score_level(total_score),
                'dimension_scores': dimension_scores,
                'weights': weights
            }

        except Exception as e:
            logger.error(f"计算基本面评分失败 {symbol}: {e}")
            return {}

    def get_investment_recommendation(self, symbol: str) -> Dict[str, Any]:
        """
        生成投资建议
        基于基本面综合评分和当前估值
        """
        try:
            # 获取综合评分
            score_result = self.calculate_fundamental_score(symbol)
            valuation = self.get_valuation_analysis(symbol)

            if not score_result or not valuation:
                return {}

            total_score = score_result.get('total_score', 0)
            pe = valuation.get('indicators', {}).get('pe', 0)
            pb = valuation.get('indicators', {}).get('pb', 0)

            # 生成投资建议
            recommendation = '观望'
            reasons = []
            risks = []

            # 基本面评分判断
            if total_score >= 70:
                if pe < 20 and pb < 3:
                    recommendation = '买入'
                    reasons.append(f'基本面优秀(评分{total_score}分),估值合理')
                else:
                    recommendation = '观望'
                    reasons.append(f'基本面优秀(评分{total_score}分),但估值偏高')
                    risks.append('当前估值较高,建议等待回调')
            elif total_score >= 50:
                if pe < 15 and pb < 2:
                    recommendation = '买入'
                    reasons.append(f'基本面良好(评分{total_score}分),估值较低')
                else:
                    recommendation = '观望'
                    reasons.append(f'基本面一般(评分{total_score}分)')
            else:
                recommendation = '回避'
                reasons.append(f'基本面较弱(评分{total_score}分)')
                risks.append('公司基本面存在问题,建议谨慎')

            # 添加具体维度的建议
            dimension_scores = score_result.get('dimension_scores', {})

            if dimension_scores.get('profitability', 0) < 50:
                risks.append('盈利能力较弱')

            if dimension_scores.get('solvency', 0) < 50:
                risks.append('偿债能力需关注')

            if dimension_scores.get('growth', 0) > 70:
                reasons.append('成长性良好')

            return {
                'recommendation': recommendation,
                'confidence': self._get_confidence_level(total_score),
                'reasons': reasons,
                'risks': risks,
                'target_price_range': self._calculate_target_price(valuation),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"生成投资建议失败 {symbol}: {e}")
            return {}

    def get_fundamental_analysis(self, symbol: str) -> Dict[str, Any]:
        """
        获取完整的基本面分析报告
        """
        try:
            # 获取股票基本信息
            def get_stock_info():
                spot_df = ak.stock_zh_a_spot_em()
                stock_data = spot_df[spot_df['代码'] == symbol]
                if stock_data.empty:
                    return None
                return stock_data.iloc[0]

            stock_info = self._retry_akshare_call(get_stock_info, max_retries=3, delay=1)

            if stock_info is None:
                return {}

            # 获取各项分析
            profitability = self.get_profitability_analysis(symbol)
            solvency = self.get_solvency_analysis(symbol)
            growth = self.get_growth_analysis(symbol)
            valuation = self.get_valuation_analysis(symbol)
            score = self.calculate_fundamental_score(symbol)
            recommendation = self.get_investment_recommendation(symbol)

            return {
                'symbol': symbol,
                'name': str(stock_info.get('名称', '')),
                'current_price': self._safe_float(stock_info.get('最新价', 0)),
                'profitability': profitability,
                'solvency': solvency,
                'growth': growth,
                'valuation': valuation,
                'overall_score': score,
                'recommendation': recommendation,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"获取基本面分析失败 {symbol}: {e}")
            return {}

    def _get_score_level(self, score: float) -> str:
        """根据分数获取等级"""
        if score >= 80:
            return '优秀'
        elif score >= 60:
            return '良好'
        elif score >= 40:
            return '一般'
        else:
            return '较差'

    def _get_confidence_level(self, score: float) -> str:
        """根据分数获取置信度"""
        if score >= 70:
            return '高'
        elif score >= 50:
            return '中'
        else:
            return '低'

    def _generate_profitability_analysis(self, indicators: Dict) -> str:
        """生成盈利能力分析文本"""
        roe = indicators.get('roe', 0)
        gross_margin = indicators.get('gross_margin', 0)

        analysis = []
        if roe > 15:
            analysis.append('净资产收益率优秀')
        elif roe > 10:
            analysis.append('净资产收益率良好')
        else:
            analysis.append('净资产收益率偏低')

        if gross_margin > 30:
            analysis.append('毛利率较高,盈利能力强')
        elif gross_margin > 20:
            analysis.append('毛利率正常')
        else:
            analysis.append('毛利率偏低,需关注成本控制')

        return '; '.join(analysis)

    def _generate_solvency_analysis(self, debt_ratio: float) -> str:
        """生成偿债能力分析文本"""
        if debt_ratio < 40:
            return '资产负债率较低,财务风险小'
        elif debt_ratio < 60:
            return '资产负债率适中,财务状况良好'
        elif debt_ratio < 80:
            return '资产负债率偏高,需关注偿债压力'
        else:
            return '资产负债率过高,财务风险较大'

    def _generate_growth_analysis(self, revenue_growth: float, profit_growth: float) -> str:
        """生成成长性分析文本"""
        analysis = []

        if revenue_growth > 20:
            analysis.append('营收增长迅速')
        elif revenue_growth > 10:
            analysis.append('营收稳定增长')
        elif revenue_growth > 0:
            analysis.append('营收小幅增长')
        else:
            analysis.append('营收出现下滑')

        if profit_growth > 20:
            analysis.append('利润增长强劲')
        elif profit_growth > 10:
            analysis.append('利润稳定增长')
        elif profit_growth > 0:
            analysis.append('利润小幅增长')
        else:
            analysis.append('利润出现下滑')

        return '; '.join(analysis)

    def _generate_valuation_analysis(self, pe: float, pb: float) -> str:
        """生成估值分析文本"""
        analysis = []

        if 10 <= pe <= 20:
            analysis.append('市盈率合理')
        elif pe < 10:
            analysis.append('市盈率较低,可能被低估')
        elif pe > 30:
            analysis.append('市盈率偏高,估值较高')

        if 1 <= pb <= 3:
            analysis.append('市净率合理')
        elif pb < 1:
            analysis.append('市净率较低,可能被低估')
        elif pb > 5:
            analysis.append('市净率偏高')

        return '; '.join(analysis)

    def _calculate_target_price(self, valuation: Dict) -> Dict[str, float]:
        """计算目标价格区间"""
        indicators = valuation.get('indicators', {})
        current_price = indicators.get('current_price', 0)

        if current_price == 0:
            return {'low': 0, 'mid': 0, 'high': 0}

        # 简单的目标价格区间估算 (±20%)
        return {
            'low': round(current_price * 0.8, 2),
            'mid': round(current_price, 2),
            'high': round(current_price * 1.2, 2)
        }

    def get_financial_statements(self, symbol: str, statement_type: str = 'balance', group: str = 'period') -> Optional[List[Dict[str, Any]]]:
        """
        获取三大财务报表数据

        Args:
            symbol: 股票代码
            statement_type: 报表类型 - balance(资产负债表), profit(利润表), cashflow(现金流量表)

        Returns:
            财务报表数据列表,按时间倒序排列
        """
        try:
            # 转换股票代码格式
            if len(symbol) == 6:
                if symbol.startswith('6'):
                    ak_symbol = f'SH{symbol}'
                else:
                    ak_symbol = f'SZ{symbol}'
            else:
                ak_symbol = symbol

            logger.info(f'获取{statement_type}财务报表: {ak_symbol}')

            def fetch_data():
                try:
                    # 根据报表类型调用不同的API
                    if statement_type == 'balance':
                        df = self._retry_akshare_call(
                            lambda: ak.stock_balance_sheet_by_report_em(symbol=ak_symbol)
                        )
                    elif statement_type == 'profit':
                        df = self._retry_akshare_call(
                            lambda: ak.stock_profit_sheet_by_report_em(symbol=ak_symbol)
                        )
                    elif statement_type == 'cashflow':
                        df = self._retry_akshare_call(
                            lambda: ak.stock_cash_flow_sheet_by_report_em(symbol=ak_symbol)
                        )
                    else:
                        logger.error(f'未知的报表类型: {statement_type}')
                        return None

                    if df is None or df.empty:
                        logger.warning(f'未获取到{statement_type}财务报表数据')
                        return None
                    return df
                except Exception as e:
                    logger.error(f'获取{statement_type}财务报表失败 {symbol}: {str(e)}')
                    return None

            # 使用缓存管理器
            df = cache_manager.get_or_update(
                data_type=f'financial_statement_{statement_type}',
                identifier=symbol,
                data_fetcher=fetch_data,
                max_age_hours=24  # 24小时更新一次
            )

            if df is None or df.empty:
                return None

            # 转换为字典列表
            all_rows = []
            for idx, row in df.iterrows():
                row_dict = row.to_dict()
                row_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
                all_rows.append(row_dict)

            # 如果请求按 period（默认），返回最近5期
            if group == 'period' or not group:
                result = all_rows[:5]
                logger.info(f'成功获取{len(result)}期{statement_type}财务报表数据 (period)')
                return result

            # 否则按 year 或 quarter 聚合
            aggregated = self._aggregate_statements(group, all_rows)
            logger.info(f'成功获取聚合后的{len(aggregated)}期{statement_type}财务报表数据 (group={group})')
            return aggregated

        except Exception as e:
            logger.error(f'获取{statement_type}财务报表失败 {symbol}: {str(e)}')
            return None

    def _aggregate_statements(self, group: str, raw_statements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将原始报表按年份或季度聚合（数值字段求和）。
        group: 'year' 或 'quarter'
        """
        if not raw_statements:
            return []

        buckets = {}

        for s in raw_statements:
            rd = s.get('REPORT_DATE') or s.get('REPORT_DATE_NAME') or ''
            year = None
            quarter = None

            # 尝试从 REPORT_DATE (YYYY-MM-DD) 提取
            if isinstance(rd, str) and len(rd) >= 7 and '-' in rd:
                try:
                    year = rd[0:4]
                    month = int(rd[5:7])
                    quarter = (month - 1) // 3 + 1
                except Exception:
                    year = None
            else:
                # 从 REPORT_DATE_NAME 中尝试匹配
                import re
                m = re.search(r"(\d{4})", str(rd))
                if m:
                    year = m.group(1)
                    mq = re.search(r"Q(\d)", str(rd))
                    if mq:
                        quarter = int(mq.group(1))

            if group == 'year':
                key = year or str(rd)
                label = f"{key} 年报"
            else:
                key = f"{year}-Q{quarter}" if year and quarter else str(rd)
                label = f"{year} Q{quarter}" if year and quarter else str(rd)

            if key not in buckets:
                buckets[key] = {**{'REPORT_DATE_NAME': label, 'REPORT_DATE': s.get('REPORT_DATE')}, '__count': 0}

            agg = buckets[key]
            agg['__count'] += 1

            for k, v in s.items():
                if isinstance(v, (int, float)) and v is not None:
                    agg[k] = agg.get(k, 0) + v
                else:
                    if k not in agg:
                        agg[k] = v

            # track latest date for sorting
            if s.get('REPORT_DATE'):
                if not agg.get('_latestDate') or s.get('REPORT_DATE') > agg.get('_latestDate'):
                    agg['_latestDate'] = s.get('REPORT_DATE')

        result = list(buckets.values())
        # sort by latest date desc
        result.sort(key=lambda x: x.get('_latestDate') or '', reverse=True)
        return result


# 创建全局实例
fundamental_service = FundamentalAnalysisService()

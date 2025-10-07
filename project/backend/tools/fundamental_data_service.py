"""
基本面数据服务模块
提供股票基本面分析数据获取功能
"""

import akshare as ak
import pandas as pd
from typing import Optional, Dict, Any, List
import logging
from .utils.retry_decorator import retry_on_failure

logger = logging.getLogger(__name__)


class FundamentalDataService:
    """基本面数据服务"""

    def __init__(self):
        self.logger = logger

    @retry_on_failure(max_retries=3)
    def get_financial_summary(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        获取财务摘要数据

        Args:
            symbol: 股票代码

        Returns:
            pd.DataFrame: 财务摘要数据
        """
        try:
            self.logger.info(f"正在获取股票{symbol}财务摘要...")
            data = ak.stock_financial_abstract(stock=symbol)

            if data is None or data.empty:
                self.logger.warning(f"股票{symbol}财务摘要数据为空")
                return None

            self.logger.info(f"成功获取股票{symbol}财务摘要，共{len(data)}条记录")
            return data
        except Exception as e:
            self.logger.error(f"获取股票{symbol}财务摘要失败: {str(e)}")
            raise

    @retry_on_failure(max_retries=3)
    def get_balance_sheet(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        获取资产负债表

        Args:
            symbol: 股票代码

        Returns:
            pd.DataFrame: 资产负债表数据
        """
        try:
            self.logger.info(f"正在获取股票{symbol}资产负债表...")
            data = ak.stock_balance_sheet_by_report_em(symbol=symbol)

            if data is None or data.empty:
                self.logger.warning(f"股票{symbol}资产负债表数据为空")
                return None

            self.logger.info(f"成功获取股票{symbol}资产负债表，共{len(data)}条记录")
            return data
        except Exception as e:
            self.logger.error(f"获取股票{symbol}资产负债表失败: {str(e)}")
            raise

    @retry_on_failure(max_retries=3)
    def get_income_statement(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        获取利润表

        Args:
            symbol: 股票代码

        Returns:
            pd.DataFrame: 利润表数据
        """
        try:
            self.logger.info(f"正在获取股票{symbol}利润表...")
            data = ak.stock_profit_sheet_by_report_em(symbol=symbol)

            if data is None or data.empty:
                self.logger.warning(f"股票{symbol}利润表数据为空")
                return None

            self.logger.info(f"成功获取股票{symbol}利润表，共{len(data)}条记录")
            return data
        except Exception as e:
            self.logger.error(f"获取股票{symbol}利润表失败: {str(e)}")
            raise

    @retry_on_failure(max_retries=3)
    def get_cash_flow(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        获取现金流量表

        Args:
            symbol: 股票代码

        Returns:
            pd.DataFrame: 现金流量表数据
        """
        try:
            self.logger.info(f"正在获取股票{symbol}现金流量表...")
            data = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)

            if data is None or data.empty:
                self.logger.warning(f"股票{symbol}现金流量表数据为空")
                return None

            self.logger.info(f"成功获取股票{symbol}现金流量表，共{len(data)}条记录")
            return data
        except Exception as e:
            self.logger.error(f"获取股票{symbol}现金流量表失败: {str(e)}")
            raise

    @retry_on_failure(max_retries=3)
    def get_financial_indicators(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        获取财务指标数据

        Args:
            symbol: 股票代码

        Returns:
            pd.DataFrame: 财务指标数据
        """
        try:
            self.logger.info(f"正在获取股票{symbol}财务指标...")
            data = ak.stock_financial_analysis_indicator(symbol=symbol)

            if data is None or data.empty:
                self.logger.warning(f"股票{symbol}财务指标数据为空")
                return None

            self.logger.info(f"成功获取股票{symbol}财务指标，共{len(data)}条记录")
            return data
        except Exception as e:
            self.logger.error(f"获取股票{symbol}财务指标失败: {str(e)}")
            raise

    def get_comprehensive_financial_data(self, symbol: str) -> Dict[str, Any]:
        """
        获取综合财务数据

        Args:
            symbol: 股票代码

        Returns:
            Dict: 包含各种财务数据的字典
        """
        try:
            self.logger.info(f"正在获取股票{symbol}综合财务数据...")

            result = {
                'symbol': symbol,
                'financial_summary': None,
                'balance_sheet': None,
                'income_statement': None,
                'cash_flow': None,
                'financial_indicators': None,
                'analysis_summary': None
            }

            # 获取各种财务数据
            try:
                result['financial_summary'] = self.get_financial_summary(symbol)
            except Exception as e:
                self.logger.warning(f"获取财务摘要失败: {str(e)}")

            try:
                result['balance_sheet'] = self.get_balance_sheet(symbol)
            except Exception as e:
                self.logger.warning(f"获取资产负债表失败: {str(e)}")

            try:
                result['income_statement'] = self.get_income_statement(symbol)
            except Exception as e:
                self.logger.warning(f"获取利润表失败: {str(e)}")

            try:
                result['cash_flow'] = self.get_cash_flow(symbol)
            except Exception as e:
                self.logger.warning(f"获取现金流量表失败: {str(e)}")

            try:
                result['financial_indicators'] = self.get_financial_indicators(symbol)
            except Exception as e:
                self.logger.warning(f"获取财务指标失败: {str(e)}")

            # 生成分析摘要
            result['analysis_summary'] = self._generate_analysis_summary(result)

            self.logger.info(f"成功获取股票{symbol}综合财务数据")
            return result

        except Exception as e:
            self.logger.error(f"获取股票{symbol}综合财务数据失败: {str(e)}")
            raise

    def calculate_financial_ratios(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        计算重要财务比率

        Args:
            symbol: 股票代码

        Returns:
            Dict: 财务比率字典
        """
        try:
            self.logger.info(f"正在计算股票{symbol}财务比率...")

            # 获取财务数据
            balance_sheet = self.get_balance_sheet(symbol)
            income_statement = self.get_income_statement(symbol)

            if balance_sheet is None or income_statement is None:
                self.logger.warning(f"股票{symbol}财务数据不完整，无法计算比率")
                return None

            # 获取最新一期数据
            latest_balance = balance_sheet.iloc[0] if len(balance_sheet) > 0 else None
            latest_income = income_statement.iloc[0] if len(income_statement) > 0 else None

            if latest_balance is None or latest_income is None:
                return None

            ratios = {}

            # 资产负债率
            if '总负债' in latest_balance and '总资产' in latest_balance:
                total_debt = float(latest_balance['总负债'])
                total_assets = float(latest_balance['总资产'])
                if total_assets != 0:
                    ratios['debt_to_asset_ratio'] = total_debt / total_assets

            # 流动比率
            if '流动资产合计' in latest_balance and '流动负债合计' in latest_balance:
                current_assets = float(latest_balance['流动资产合计'])
                current_liabilities = float(latest_balance['流动负债合计'])
                if current_liabilities != 0:
                    ratios['current_ratio'] = current_assets / current_liabilities

            # 净资产收益率
            if '净利润' in latest_income and '股东权益合计' in latest_balance:
                net_profit = float(latest_income['净利润'])
                shareholders_equity = float(latest_balance['股东权益合计'])
                if shareholders_equity != 0:
                    ratios['roe'] = net_profit / shareholders_equity

            # 毛利率
            if '营业收入' in latest_income and '营业成本' in latest_income:
                revenue = float(latest_income['营业收入'])
                cost = float(latest_income['营业成本'])
                if revenue != 0:
                    ratios['gross_margin'] = (revenue - cost) / revenue

            # 净利润率
            if '净利润' in latest_income and '营业收入' in latest_income:
                net_profit = float(latest_income['净利润'])
                revenue = float(latest_income['营业收入'])
                if revenue != 0:
                    ratios['net_margin'] = net_profit / revenue

            self.logger.info(f"成功计算股票{symbol}财务比率，共{len(ratios)}个指标")
            return ratios

        except Exception as e:
            self.logger.error(f"计算股票{symbol}财务比率失败: {str(e)}")
            raise

    def get_dividend_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        获取分红数据

        Args:
            symbol: 股票代码

        Returns:
            pd.DataFrame: 分红数据
        """
        try:
            self.logger.info(f"正在获取股票{symbol}分红数据...")
            data = ak.stock_dividend_detail(symbol=symbol)

            if data is None or data.empty:
                self.logger.warning(f"股票{symbol}分红数据为空")
                return None

            self.logger.info(f"成功获取股票{symbol}分红数据，共{len(data)}条记录")
            return data
        except Exception as e:
            self.logger.error(f"获取股票{symbol}分红数据失败: {str(e)}")
            return None

    def get_company_profile(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取公司基本信息

        Args:
            symbol: 股票代码

        Returns:
            Dict: 公司基本信息
        """
        try:
            self.logger.info(f"正在获取股票{symbol}公司信息...")
            data = ak.stock_individual_info_em(symbol=symbol)

            if data is None or data.empty:
                self.logger.warning(f"股票{symbol}公司信息为空")
                return None

            # 转换为字典格式
            profile = {}
            for _, row in data.iterrows():
                profile[row['item']] = row['value']

            self.logger.info(f"成功获取股票{symbol}公司信息")
            return profile
        except Exception as e:
            self.logger.error(f"获取股票{symbol}公司信息失败: {str(e)}")
            return None

    def _generate_analysis_summary(self, financial_data: Dict) -> Dict[str, Any]:
        """
        生成财务分析摘要

        Args:
            financial_data: 财务数据字典

        Returns:
            Dict: 分析摘要
        """
        try:
            summary = {
                'data_completeness': {},
                'key_metrics': {},
                'risk_indicators': {},
                'growth_indicators': {}
            }

            # 数据完整性检查
            summary['data_completeness'] = {
                'has_financial_summary': financial_data['financial_summary'] is not None,
                'has_balance_sheet': financial_data['balance_sheet'] is not None,
                'has_income_statement': financial_data['income_statement'] is not None,
                'has_cash_flow': financial_data['cash_flow'] is not None,
                'has_indicators': financial_data['financial_indicators'] is not None
            }

            # 计算关键指标
            if financial_data['income_statement'] is not None and not financial_data['income_statement'].empty:
                income_data = financial_data['income_statement'].iloc[0]
                if '净利润' in income_data:
                    summary['key_metrics']['latest_net_profit'] = float(income_data['净利润'])
                if '营业收入' in income_data:
                    summary['key_metrics']['latest_revenue'] = float(income_data['营业收入'])

            # 计算财务比率
            ratios = self.calculate_financial_ratios(financial_data['symbol'])
            if ratios:
                summary['key_metrics'].update(ratios)

            return summary

        except Exception as e:
            self.logger.warning(f"生成分析摘要失败: {str(e)}")
            return {}
"""
历史数据服务模块
提供股票历史价格数据获取功能
"""

import akshare as ak
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging
from .utils.retry_decorator import retry_on_failure

logger = logging.getLogger(__name__)


class HistoricalDataService:
    """历史数据服务"""

    def __init__(self):
        self.logger = logger

    @retry_on_failure(max_retries=3)
    def get_historical_prices(self, symbol: str, start_date: str, end_date: str,
                            adjust: str = "qfq") -> Optional[pd.DataFrame]:
        """
        获取历史价格数据

        Args:
            symbol: 股票代码，如 "000001"
            start_date: 开始日期，格式 "20240101"
            end_date: 结束日期，格式 "20241201"
            adjust: 复权类型，'qfq'前复权, 'hfq'后复权, ''不复权

        Returns:
            pd.DataFrame: 历史价格数据
        """
        try:
            self.logger.info(f"正在获取股票{symbol}历史数据({start_date}~{end_date}), 复权方式:{adjust}")

            data = ak.stock_zh_a_hist(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )

            if data is None or data.empty:
                self.logger.warning(f"股票{symbol}在指定日期范围内无数据")
                return None

            # 数据清洗和格式化
            data = self._format_historical_data(data)

            self.logger.info(f"成功获取股票{symbol}历史数据，共{len(data)}条记录")
            return data

        except Exception as e:
            self.logger.error(f"获取股票{symbol}历史数据失败: {str(e)}")
            raise

    @retry_on_failure(max_retries=3)
    def get_minute_data(self, symbol: str, period: str = "1") -> Optional[pd.DataFrame]:
        """
        获取分钟级数据

        Args:
            symbol: 股票代码
            period: 时间周期 "1", "5", "15", "30", "60"

        Returns:
            pd.DataFrame: 分钟级价格数据
        """
        try:
            self.logger.info(f"正在获取股票{symbol}的{period}分钟数据...")

            data = ak.stock_zh_a_hist_min_em(
                symbol=symbol,
                period=period
            )

            if data is None or data.empty:
                self.logger.warning(f"股票{symbol}无{period}分钟数据")
                return None

            self.logger.info(f"成功获取股票{symbol}的{period}分钟数据，共{len(data)}条记录")
            return data

        except Exception as e:
            self.logger.error(f"获取股票{symbol}分钟数据失败: {str(e)}")
            raise

    def get_recent_data(self, symbol: str, days: int = 30,
                       adjust: str = "qfq") -> Optional[pd.DataFrame]:
        """
        获取最近N天的数据

        Args:
            symbol: 股票代码
            days: 天数
            adjust: 复权类型

        Returns:
            pd.DataFrame: 最近N天的数据
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            start_str = start_date.strftime("%Y%m%d")
            end_str = end_date.strftime("%Y%m%d")

            return self.get_historical_prices(symbol, start_str, end_str, adjust)

        except Exception as e:
            self.logger.error(f"获取股票{symbol}最近{days}天数据失败: {str(e)}")
            raise

    def get_year_data(self, symbol: str, year: int,
                     adjust: str = "qfq") -> Optional[pd.DataFrame]:
        """
        获取指定年份的数据

        Args:
            symbol: 股票代码
            year: 年份
            adjust: 复权类型

        Returns:
            pd.DataFrame: 指定年份的数据
        """
        try:
            start_date = f"{year}0101"
            end_date = f"{year}1231"

            return self.get_historical_prices(symbol, start_date, end_date, adjust)

        except Exception as e:
            self.logger.error(f"获取股票{symbol}{year}年数据失败: {str(e)}")
            raise

    def get_weekly_data(self, symbol: str, start_date: str, end_date: str,
                       adjust: str = "qfq") -> Optional[pd.DataFrame]:
        """
        获取周线数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            adjust: 复权类型

        Returns:
            pd.DataFrame: 周线数据
        """
        try:
            self.logger.info(f"正在获取股票{symbol}周线数据...")

            # 先获取日线数据
            daily_data = self.get_historical_prices(symbol, start_date, end_date, adjust)

            if daily_data is None or daily_data.empty:
                return None

            # 转换为周线数据
            daily_data['日期'] = pd.to_datetime(daily_data['日期'])
            daily_data.set_index('日期', inplace=True)

            # 按周重采样
            weekly_data = daily_data.resample('W').agg({
                '开盘': 'first',
                '最高': 'max',
                '最低': 'min',
                '收盘': 'last',
                '成交量': 'sum',
                '成交额': 'sum'
            }).dropna()

            weekly_data.reset_index(inplace=True)

            self.logger.info(f"成功获取股票{symbol}周线数据，共{len(weekly_data)}条记录")
            return weekly_data

        except Exception as e:
            self.logger.error(f"获取股票{symbol}周线数据失败: {str(e)}")
            raise

    def get_monthly_data(self, symbol: str, start_date: str, end_date: str,
                        adjust: str = "qfq") -> Optional[pd.DataFrame]:
        """
        获取月线数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            adjust: 复权类型

        Returns:
            pd.DataFrame: 月线数据
        """
        try:
            self.logger.info(f"正在获取股票{symbol}月线数据...")

            # 先获取日线数据
            daily_data = self.get_historical_prices(symbol, start_date, end_date, adjust)

            if daily_data is None or daily_data.empty:
                return None

            # 转换为月线数据
            daily_data['日期'] = pd.to_datetime(daily_data['日期'])
            daily_data.set_index('日期', inplace=True)

            # 按月重采样
            monthly_data = daily_data.resample('M').agg({
                '开盘': 'first',
                '最高': 'max',
                '最低': 'min',
                '收盘': 'last',
                '成交量': 'sum',
                '成交额': 'sum'
            }).dropna()

            monthly_data.reset_index(inplace=True)

            self.logger.info(f"成功获取股票{symbol}月线数据，共{len(monthly_data)}条记录")
            return monthly_data

        except Exception as e:
            self.logger.error(f"获取股票{symbol}月线数据失败: {str(e)}")
            raise

    def get_price_statistics(self, symbol: str, start_date: str, end_date: str,
                           adjust: str = "qfq") -> Optional[Dict[str, Any]]:
        """
        获取价格统计信息

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            adjust: 复权类型

        Returns:
            Dict: 价格统计信息
        """
        try:
            data = self.get_historical_prices(symbol, start_date, end_date, adjust)

            if data is None or data.empty:
                return None

            stats = {
                'period_start': start_date,
                'period_end': end_date,
                'trading_days': len(data),
                'highest_price': float(data['最高'].max()),
                'lowest_price': float(data['最低'].min()),
                'avg_price': float(data['收盘'].mean()),
                'start_price': float(data.iloc[0]['开盘']),
                'end_price': float(data.iloc[-1]['收盘']),
                'total_return': float((data.iloc[-1]['收盘'] - data.iloc[0]['开盘']) / data.iloc[0]['开盘'] * 100),
                'max_single_day_gain': float(data['涨跌幅'].max()) if '涨跌幅' in data.columns else None,
                'max_single_day_loss': float(data['涨跌幅'].min()) if '涨跌幅' in data.columns else None,
                'avg_volume': float(data['成交量'].mean()),
                'total_volume': float(data['成交量'].sum()),
                'avg_turnover': float(data['成交额'].mean()),
                'total_turnover': float(data['成交额'].sum())
            }

            # 计算波动率
            if '涨跌幅' in data.columns:
                stats['volatility'] = float(data['涨跌幅'].std())

            self.logger.info(f"成功计算股票{symbol}价格统计信息")
            return stats

        except Exception as e:
            self.logger.error(f"计算股票{symbol}价格统计信息失败: {str(e)}")
            raise

    def get_multiple_stocks_data(self, symbols: List[str], start_date: str,
                               end_date: str, adjust: str = "qfq") -> Dict[str, pd.DataFrame]:
        """
        批量获取多只股票的历史数据

        Args:
            symbols: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期
            adjust: 复权类型

        Returns:
            Dict: 股票代码->历史数据的字典
        """
        results = {}

        for symbol in symbols:
            try:
                data = self.get_historical_prices(symbol, start_date, end_date, adjust)
                if data is not None:
                    results[symbol] = data
                else:
                    self.logger.warning(f"股票{symbol}数据获取失败")
            except Exception as e:
                self.logger.error(f"获取股票{symbol}数据时发生错误: {str(e)}")
                continue

        self.logger.info(f"批量获取完成，成功获取{len(results)}/{len(symbols)}只股票数据")
        return results

    def _format_historical_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        格式化历史数据

        Args:
            data: 原始数据

        Returns:
            pd.DataFrame: 格式化后的数据
        """
        try:
            # 确保数据类型正确
            if '日期' in data.columns:
                data['日期'] = pd.to_datetime(data['日期'])

            # 确保数值列为数值类型
            numeric_columns = ['开盘', '收盘', '最高', '最低', '成交量', '成交额']
            for col in numeric_columns:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce')

            # 计算涨跌幅（如果没有的话）
            if '涨跌幅' not in data.columns and '收盘' in data.columns:
                data = data.sort_values('日期')
                data['涨跌幅'] = data['收盘'].pct_change() * 100

            # 计算涨跌额（如果没有的话）
            if '涨跌额' not in data.columns and '收盘' in data.columns:
                data = data.sort_values('日期')
                data['涨跌额'] = data['收盘'].diff()

            # 删除空行
            data = data.dropna(subset=['开盘', '收盘', '最高', '最低'])

            return data

        except Exception as e:
            self.logger.error(f"格式化历史数据失败: {str(e)}")
            return data
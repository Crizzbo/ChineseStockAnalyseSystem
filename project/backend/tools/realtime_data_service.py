"""
实时行情数据服务模块
提供A股实时行情数据获取功能
"""

import akshare as ak
import pandas as pd
from typing import Optional, Dict, Any
import logging
from .utils.retry_decorator import retry_on_failure

logger = logging.getLogger(__name__)


class RealTimeDataService:
    """实时行情数据服务"""

    def __init__(self):
        self.logger = logger

    @retry_on_failure(max_retries=3)
    def get_a_share_spot(self) -> Optional[pd.DataFrame]:
        """
        获取A股实时行情数据

        Returns:
            pd.DataFrame: A股实时行情数据，包含股票代码、名称、价格等信息
        """
        try:
            self.logger.info("正在获取A股实时行情数据...")
            data = ak.stock_zh_a_spot_em()
            self.logger.info(f"成功获取A股实时行情数据，共{len(data)}条记录")
            return data
        except Exception as e:
            self.logger.error(f"获取A股实时行情数据失败: {str(e)}")
            raise

    @retry_on_failure(max_retries=3)
    def get_stock_realtime(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取单只股票实时数据

        Args:
            symbol: 股票代码，如 "000001"

        Returns:
            Dict: 单只股票的实时数据
        """
        try:
            self.logger.info(f"正在获取股票{symbol}实时数据...")
            all_data = ak.stock_zh_a_spot_em()

            # 根据股票代码筛选数据
            stock_data = all_data[all_data['代码'] == symbol]

            if stock_data.empty:
                self.logger.warning(f"未找到股票代码{symbol}的数据")
                return None

            # 转换为字典格式
            result = stock_data.iloc[0].to_dict()
            self.logger.info(f"成功获取股票{symbol}实时数据")
            return result

        except Exception as e:
            self.logger.error(f"获取股票{symbol}实时数据失败: {str(e)}")
            raise

    @retry_on_failure(max_retries=3)
    def get_market_indices(self) -> Optional[pd.DataFrame]:
        """
        获取主要指数实时数据

        Returns:
            pd.DataFrame: 主要指数实时数据
        """
        try:
            self.logger.info("正在获取主要指数实时数据...")
            data = ak.stock_zh_index_spot_em()
            self.logger.info(f"成功获取主要指数实时数据，共{len(data)}条记录")
            return data
        except Exception as e:
            self.logger.error(f"获取主要指数实时数据失败: {str(e)}")
            raise

    @retry_on_failure(max_retries=3)
    def get_stock_basic_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            Dict: 股票基本信息
        """
        try:
            self.logger.info(f"正在获取股票{symbol}基本信息...")
            realtime_data = self.get_stock_realtime(symbol)

            if not realtime_data:
                return None

            basic_info = {
                'code': realtime_data.get('代码'),
                'name': realtime_data.get('名称'),
                'current_price': realtime_data.get('最新价'),
                'change_percent': realtime_data.get('涨跌幅'),
                'change_amount': realtime_data.get('涨跌额'),
                'volume': realtime_data.get('成交量'),
                'turnover': realtime_data.get('成交额'),
                'market_cap': realtime_data.get('总市值'),
                'pe_ratio': realtime_data.get('市盈率-动态'),
                'pb_ratio': realtime_data.get('市净率')
            }

            self.logger.info(f"成功获取股票{symbol}基本信息")
            return basic_info

        except Exception as e:
            self.logger.error(f"获取股票{symbol}基本信息失败: {str(e)}")
            raise

    @retry_on_failure(max_retries=3)
    def get_top_gainers(self, limit: int = 20) -> Optional[pd.DataFrame]:
        """
        获取涨幅榜

        Args:
            limit: 返回记录数量限制

        Returns:
            pd.DataFrame: 涨幅榜数据
        """
        try:
            self.logger.info(f"正在获取涨幅榜前{limit}名...")
            all_data = ak.stock_zh_a_spot_em()

            # 按涨跌幅排序，取前limit名
            top_gainers = all_data.nlargest(limit, '涨跌幅')

            self.logger.info(f"成功获取涨幅榜前{limit}名")
            return top_gainers

        except Exception as e:
            self.logger.error(f"获取涨幅榜失败: {str(e)}")
            raise

    @retry_on_failure(max_retries=3)
    def get_top_losers(self, limit: int = 20) -> Optional[pd.DataFrame]:
        """
        获取跌幅榜

        Args:
            limit: 返回记录数量限制

        Returns:
            pd.DataFrame: 跌幅榜数据
        """
        try:
            self.logger.info(f"正在获取跌幅榜前{limit}名...")
            all_data = ak.stock_zh_a_spot_em()

            # 按涨跌幅排序，取后limit名
            top_losers = all_data.nsmallest(limit, '涨跌幅')

            self.logger.info(f"成功获取跌幅榜前{limit}名")
            return top_losers

        except Exception as e:
            self.logger.error(f"获取跌幅榜失败: {str(e)}")
            raise

    def get_market_summary(self) -> Dict[str, Any]:
        """
        获取市场概况

        Returns:
            Dict: 市场概况数据
        """
        try:
            self.logger.info("正在获取市场概况...")

            # 获取A股数据
            a_share_data = self.get_a_share_spot()
            if a_share_data is None or a_share_data.empty:
                return {}

            # 获取指数数据
            index_data = self.get_market_indices()

            # 统计市场概况
            total_stocks = len(a_share_data)
            rising_stocks = len(a_share_data[a_share_data['涨跌幅'] > 0])
            falling_stocks = len(a_share_data[a_share_data['涨跌幅'] < 0])
            unchanged_stocks = total_stocks - rising_stocks - falling_stocks

            summary = {
                'total_stocks': total_stocks,
                'rising_stocks': rising_stocks,
                'falling_stocks': falling_stocks,
                'unchanged_stocks': unchanged_stocks,
                'rising_ratio': round(rising_stocks / total_stocks * 100, 2),
                'falling_ratio': round(falling_stocks / total_stocks * 100, 2),
                'avg_change': round(a_share_data['涨跌幅'].mean(), 2),
                'total_turnover': a_share_data['成交额'].sum()
            }

            # 添加主要指数信息
            if index_data is not None and not index_data.empty:
                # 查找上证指数
                sz_index = index_data[index_data['代码'].str.contains('000001', na=False)]
                if not sz_index.empty:
                    summary['sh_index'] = {
                        'code': sz_index.iloc[0]['代码'],
                        'name': sz_index.iloc[0]['名称'],
                        'current': sz_index.iloc[0]['最新价'],
                        'change_percent': sz_index.iloc[0]['涨跌幅']
                    }

            self.logger.info("成功获取市场概况")
            return summary

        except Exception as e:
            self.logger.error(f"获取市场概况失败: {str(e)}")
            return {}
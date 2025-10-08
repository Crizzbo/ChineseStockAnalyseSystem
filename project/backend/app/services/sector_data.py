"""
板块数据服务 - 基于AkShare
"""
import akshare as ak
try:
    import pandas as pd
except ImportError:
    pd = None
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from app import redis_client
import json

logger = logging.getLogger(__name__)

class SectorDataService:
    """板块数据服务类"""

    def __init__(self):
        # 禁用Redis缓存
        pass

    def _get_cache(self, key: str, expire_seconds: int = 300) -> Optional[Any]:
        """缓存功能已禁用，直接返回None"""
        return None

    def _set_cache(self, key: str, data: Any, expire_seconds: int = 300) -> None:
        """缓存功能已禁用，不做任何操作"""
        pass

    def _retry_akshare_call(self, func, max_retries: int = 3, delay: int = 1):
        """重试AkShare调用"""
        import time

        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logger.warning(f"AkShare调用失败，重试 {attempt + 1}/{max_retries}: {e}")
                time.sleep(delay * (attempt + 1))

    def get_sectors(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取板块列表 - 使用AkShare真实数据"""
        try:

            def get_sector_data():
                return ak.stock_board_industry_name_em()

            # 获取真实板块数据
            sector_df = self._retry_akshare_call(get_sector_data, max_retries=3, delay=1)

            results = []
            if sector_df is not None and not sector_df.empty:
                logger.info(f"成功获取板块数据，共 {len(sector_df)} 条记录")
                for _, row in sector_df.head(limit).iterrows():
                    try:
                        # 计算成分股数量 = 上涨家数 + 下跌家数
                        up_count = int(row['上涨家数']) if '上涨家数' in row and row['上涨家数'] != '-' else 0
                        down_count = int(row['下跌家数']) if '下跌家数' in row and row['下跌家数'] != '-' else 0
                        stock_count = up_count + down_count

                        # 获取领涨股票信息
                        leading_stock = str(row['领涨股票']) if '领涨股票' in row and row['领涨股票'] and row['领涨股票'] != '-' else ''
                        leading_stock_change = float(row['领涨股票-涨跌幅']) if '领涨股票-涨跌幅' in row and row['领涨股票-涨跌幅'] != '-' else 0.0

                        results.append({
                            'rank': int(row['排名']) if '排名' in row and row['排名'] != '-' else 0,
                            'code': row['板块代码'] if '板块代码' in row else row['板块名称'],
                            'name': row['板块名称'],
                            'currentPrice': float(row['最新价']) if '最新价' in row else 0.0,
                            'change': float(row['涨跌额']) if '涨跌额' in row else 0.0,
                            'changePercent': float(row['涨跌幅']) if '涨跌幅' in row else 0.0,
                            'volume': 0,  # 暂不计算,需要时通过成分股累加
                            'turnover': float(row['总市值']) if '总市值' in row and row['总市值'] != '-' else 0.0,
                            'totalTurnover': 0.0,  # 暂不计算,需要时通过成分股累加
                            'turnoverRate': float(row['换手率']) if '换手率' in row and row['换手率'] != '-' else 0.0,
                            'stockCount': stock_count,
                            'upCount': up_count,
                            'downCount': down_count,
                            'leadingStock': leading_stock,
                            'leadingStockChange': leading_stock_change,
                            'leadingStocks': [leading_stock] if leading_stock else []  # 保持兼容性
                        })
                    except Exception as parse_error:
                        logger.warning(f"解析板块数据失败: {parse_error}")
                        continue

            logger.info(f"成功处理 {len(results)} 个板块")
            return results

        except Exception as e:
            logger.error(f"获取板块列表失败: {e}")
            return []

    def get_sector_info(self, sector_code: str) -> Optional[Dict[str, Any]]:
        """获取板块详细信息"""
        try:

            # 从板块列表中查找对应板块
            sectors = self.get_sectors()
            for sector in sectors:
                if sector['code'] == sector_code or sector['name'] == sector_code:
                    return sector

            return None

        except Exception as e:
            logger.error(f"获取板块信息失败 {sector_code}: {e}")
            return None

    def get_sector_stocks(self, sector_code: str) -> List[Dict[str, Any]]:
        """获取板块成分股 - 使用AkShare真实数据"""
        try:

            def get_constituent_stocks():
                return ak.stock_board_industry_cons_em(symbol=sector_code)

            # 获取板块成分股数据
            stocks_df = self._retry_akshare_call(get_constituent_stocks, max_retries=3, delay=1)

            results = []
            if stocks_df is not None and not stocks_df.empty:
                logger.info(f"成功获取板块 {sector_code} 成分股数据，共 {len(stocks_df)} 条记录")
                for _, row in stocks_df.iterrows():
                    try:
                        results.append({
                            'symbol': row['代码'],
                            'name': row['名称'],
                            'currentPrice': float(row['最新价']),
                            'change': float(row['涨跌额']),
                            'changePercent': float(row['涨跌幅']),
                            'volume': int(row['成交量']) if row['成交量'] != '-' else 0,
                            'turnover': float(row['成交额']) if row['成交额'] != '-' else 0.0,
                            'marketCap': None,  # 成分股API不提供总市值字段
                            'pe': float(row['市盈率-动态']) if '市盈率-动态' in row and row['市盈率-动态'] != '-' else None,
                            'pb': float(row['市净率']) if '市净率' in row and row['市净率'] != '-' else None,
                            'turnoverRate': float(row['换手率']) if '换手率' in row and row['换手率'] != '-' else None,
                            'amplitude': float(row['振幅']) if '振幅' in row and row['振幅'] != '-' else None,
                            'highest': float(row['最高']) if '最高' in row and row['最高'] != '-' else None,
                            'lowest': float(row['最低']) if '最低' in row and row['最低'] != '-' else None
                        })
                    except Exception as parse_error:
                        logger.warning(f"解析成分股数据失败: {parse_error}")
                        continue

            logger.info(f"成功处理板块 {sector_code} 的 {len(results)} 只成分股")
            return results

        except Exception as e:
            logger.error(f"获取板块成分股失败 {sector_code}: {e}")
            return []

    def get_hot_sectors(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取热门板块（按涨跌幅排序）"""
        try:

            # 获取所有板块，按涨跌幅排序
            sectors = self.get_sectors()
            if not sectors:
                return []

            # 按涨跌幅降序排序
            hot_sectors = sorted(sectors, key=lambda x: x['changePercent'], reverse=True)[:limit]

            return hot_sectors

        except Exception as e:
            logger.error(f"获取热门板块失败: {e}")
            return []

    def search_sectors(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索板块"""
        try:

            sectors = self.get_sectors()
            if not sectors:
                return []

            keyword_lower = keyword.lower()
            results = []

            for sector in sectors:
                if (keyword_lower in sector['name'].lower() or
                    keyword_lower in sector['code'].lower()):
                    results.append(sector)

                    if len(results) >= limit:
                        break

            return results

        except Exception as e:
            logger.error(f"搜索板块失败: {e}")
            return []

    def get_sector_ranking(self, sort_by: str = 'changePercent', order: str = 'desc', limit: int = 50) -> List[Dict[str, Any]]:
        """获取板块排行榜"""
        try:

            sectors = self.get_sectors()
            if not sectors:
                return []

            # 确保排序字段存在
            valid_sort_fields = ['changePercent', 'change', 'volume', 'turnover', 'stockCount']
            if sort_by not in valid_sort_fields:
                sort_by = 'changePercent'

            # 排序
            reverse = order == 'desc'
            ranked_sectors = sorted(sectors, key=lambda x: x.get(sort_by, 0), reverse=reverse)[:limit]

            return ranked_sectors

        except Exception as e:
            logger.error(f"获取板块排行榜失败: {e}")
            return []


# 创建全局实例
sector_service = SectorDataService()
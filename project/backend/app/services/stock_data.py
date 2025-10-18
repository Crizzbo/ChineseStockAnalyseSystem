"""
股票数据服务 - 基于AkShare
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
import time
import threading
from functools import wraps
import sys

logger = logging.getLogger(__name__)

class StockDataService:
    """股票数据服务类"""

    def __init__(self):
        # 禁用Redis缓存
        self._cached_spot_data = None
        self._cache_time = None
        self._cache_duration = 60  # 缓存60秒

    def _get_cache(self, key: str, expire_seconds: int = 300) -> Optional[Any]:
        """缓存功能已禁用，直接返回None"""
        return None

    def _set_cache(self, key: str, data: Any, expire_seconds: int = 300) -> None:
        """缓存功能已禁用，不做任何操作"""
        pass

    def _retry_akshare_call(self, func, max_retries: int = 2, delay: int = 1, timeout: int = 15):
        """重试AkShare调用，带超时控制"""
        for attempt in range(max_retries):
            try:
                # 使用线程实现超时控制
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
                    # 线程仍在运行，表示超时
                    logger.warning(f"API调用超时 ({timeout}秒)")
                    raise TimeoutError(f"API调用超时 ({timeout}秒)")

                if exception[0]:
                    raise exception[0]

                return result[0]

            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logger.warning(f"AkShare调用失败，重试 {attempt + 1}/{max_retries}: {e}")
                time.sleep(delay * (attempt + 1))  # 递增延迟

    def _safe_float(self, value, default=0.0):
        """安全转换为浮点数"""
        try:
            if value is None or value == '-' or value == '':
                return default
            return float(value)
        except (ValueError, TypeError):
            return default

    def _safe_int(self, value, default=0):
        """安全转换为整数"""
        try:
            if value is None or value == '-' or value == '':
                return default
            return int(float(value))
        except (ValueError, TypeError):
            return default

    def _safe_str(self, value, default=''):
        """安全转换为字符串"""
        try:
            if value is None:
                return default
            return str(value)
        except (ValueError, TypeError):
            return default


    def _get_cached_spot_data(self):
        """获取缓存的实时股票数据"""
        current_time = time.time()

        # 检查缓存是否有效
        if (self._cached_spot_data is not None and
            self._cache_time is not None and
            current_time - self._cache_time < self._cache_duration):
            return self._cached_spot_data

        # 缓存失效，重新获取数据
        try:
            def get_stock_data():
                return ak.stock_zh_a_spot_em()

            spot_df = self._retry_akshare_call(get_stock_data, max_retries=2, delay=1, timeout=15)

            if spot_df is not None and not spot_df.empty:
                self._cached_spot_data = spot_df
                self._cache_time = current_time
                logger.info(f"成功获取股票数据，共{len(spot_df)}只股票")
                return spot_df
            else:
                logger.warning("获取到空的股票数据")
                return None

        except Exception as e:
            logger.error(f"获取股票数据失败: {e}")
            # 如果有旧缓存，使用旧缓存
            if self._cached_spot_data is not None:
                logger.info("使用过期缓存数据")
                return self._cached_spot_data

            # 不使用模拟数据，返回None
            return None

    def search_stocks(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索股票 - 使用AkShare真实数据"""
        try:
            results = []

            # 使用缓存的股票数据
            spot_df = self._get_cached_spot_data()

            if spot_df is not None and not spot_df.empty:
                # 搜索匹配的股票
                keyword_lower = keyword.lower()

                # 在代码和名称中搜索
                matched_stocks = spot_df[
                    (spot_df['代码'].str.contains(keyword, case=False, na=False)) |
                    (spot_df['名称'].str.contains(keyword, case=False, na=False))
                ].head(limit)

                for _, row in matched_stocks.iterrows():
                    try:
                        results.append({
                            'symbol': self._safe_str(row['代码']),
                            'name': self._safe_str(row['名称']),
                            'currentPrice': self._safe_float(row['最新价']),
                            'change': self._safe_float(row['涨跌额']),
                            'changePercent': self._safe_float(row['涨跌幅']),
                            'volume': self._safe_int(row['成交量']),
                            'turnover': self._safe_float(row['成交额']),
                            'high': self._safe_float(row['最高']),
                            'low': self._safe_float(row['最低']),
                            'open': self._safe_float(row['今开']),
                            'preClose': self._safe_float(row['昨收']),
                            'marketCap': self._safe_float(row['总市值']) if '总市值' in row else None,
                            'pe': self._safe_float(row['市盈率-动态']) if '市盈率-动态' in row else None,
                            'pb': self._safe_float(row['市净率']) if '市净率' in row else None
                        })
                    except Exception as e:
                        logger.warning(f"解析搜索结果失败: {e}")
                        continue

            return results

        except Exception as e:
            logger.error(f"搜索股票失败: {e}")
            return []

    def get_stock_basic_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取股票基本信息 - 使用AkShare实时数据"""
        try:
            # 获取实时股票数据
            def get_stock_data():
                return ak.stock_zh_a_spot_em()

            spot_df = self._retry_akshare_call(get_stock_data, max_retries=3, delay=1)

            if spot_df is not None and not spot_df.empty:
                # 查找指定股票
                stock_data = spot_df[spot_df['代码'] == symbol]

                if not stock_data.empty:
                    row = stock_data.iloc[0]

                    return {
                        'symbol': self._safe_str(row['代码']),
                        'name': self._safe_str(row['名称']),
                        'currentPrice': self._safe_float(row['最新价']),
                        'change': self._safe_float(row['涨跌额']),
                        'changePercent': self._safe_float(row['涨跌幅']),
                        'volume': self._safe_int(row['成交量']),
                        'turnover': self._safe_float(row['成交额']),
                        'high': self._safe_float(row['最高']),
                        'low': self._safe_float(row['最低']),
                        'open': self._safe_float(row['今开']),
                        'preClose': self._safe_float(row['昨收']),
                        'marketCap': self._safe_float(row['总市值']) if '总市值' in row else None,
                        'pe': self._safe_float(row['市盈率-动态']) if '市盈率-动态' in row else None,
                        'pb': self._safe_float(row['市净率']) if '市净率' in row else None,
                        'turnoverRate': self._safe_float(row['换手率']) if '换手率' in row else None,
                        'volumeRatio': self._safe_float(row['量比']) if '量比' in row else None
                    }

            return None

        except Exception as e:
            logger.error(f"获取股票基本信息失败 {symbol}: {e}")
            return None

    def get_stock_price_history(self, symbol: str, period: str = "daily",
                              start_date: str = None, end_date: str = None,
                              limit: int = 250) -> List[Dict[str, Any]]:
        """获取股票历史价格数据"""
        try:

            # 设置默认日期范围
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            if not start_date:
                start_dt = datetime.strptime(end_date, '%Y%m%d') - timedelta(days=250)
                start_date = start_dt.strftime('%Y%m%d')

            # 根据周期获取数据，使用重试机制
            def get_history_data():
                if period == "daily":
                    return ak.stock_zh_a_hist(symbol=symbol, period="daily",
                                           start_date=start_date, end_date=end_date, adjust="")
                elif period == "weekly":
                    return ak.stock_zh_a_hist(symbol=symbol, period="weekly",
                                           start_date=start_date, end_date=end_date, adjust="")
                elif period == "monthly":
                    return ak.stock_zh_a_hist(symbol=symbol, period="monthly",
                                           start_date=start_date, end_date=end_date, adjust="")
                else:
                    return ak.stock_zh_a_hist(symbol=symbol, period="daily",
                                           start_date=start_date, end_date=end_date, adjust="")

            df = self._retry_akshare_call(get_history_data, max_retries=10, delay=3)

            if df.empty:
                return []

            # 转换数据格式
            price_data = []
            for _, row in df.tail(limit).iterrows():
                price_data.append({
                    'date': row['日期'].strftime('%Y-%m-%d'),
                    'open': float(row['开盘']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'close': float(row['收盘']),
                    'volume': int(row['成交量']),
                    'turnover': float(row['成交额'])
                })

            return price_data

        except Exception as e:
            logger.error(f"获取股票历史数据失败 {symbol}: {e}")
            return []

    def get_index_data(self, index_category: str = None):
        """获取指数数据，使用重试机制"""
        try:
            def get_data():
                if index_category:
                    return ak.stock_zh_index_spot_em(symbol=index_category)
                else:
                    # 获取所有指数数据
                    return ak.stock_zh_index_spot_em()

            return self._retry_akshare_call(get_data, max_retries=3, delay=1)
        except Exception as e:
            logger.error(f"获取指数数据失败: {e}")
            return pd.DataFrame()

    def get_market_indices(self) -> List[Dict[str, Any]]:
        """获取主要市场指数"""
        try:
            indices_data = []

            # 获取主要指数类别
            index_categories = [
                "沪深重要指数",
                "上证系列指数",
                "深证系列指数"
            ]

            for category in index_categories:
                try:
                    index_df = self.get_index_data(category)

                    if index_df is not None and not index_df.empty:
                        # 只取前几个重要指数
                        for _, row in index_df.head(5).iterrows():
                            try:
                                indices_data.append({
                                    'symbol': self._safe_str(row['代码']),
                                    'name': self._safe_str(row['名称']),
                                    'currentPrice': self._safe_float(row['最新价']),
                                    'change': self._safe_float(row['涨跌额']),
                                    'changePercent': self._safe_float(row['涨跌幅']),
                                    'volume': self._safe_int(row['成交量']) if '成交量' in row else 0,
                                    'turnover': self._safe_float(row['成交额']) if '成交额' in row else 0.0,
                                    'high': self._safe_float(row['最高']) if '最高' in row else None,
                                    'low': self._safe_float(row['最低']) if '最低' in row else None,
                                    'open': self._safe_float(row['今开']) if '今开' in row else None,
                                    'preClose': self._safe_float(row['昨收']) if '昨收' in row else None
                                })
                            except Exception as e:
                                logger.warning(f"解析指数数据失败: {e}")
                                continue

                except Exception as e:
                    logger.warning(f"获取{category}数据失败: {e}")
                    continue

            # 如果上面的方法失败，尝试获取特定的主要指数
            if not indices_data:
                try:
                    # 直接获取一些主要指数
                    main_indices = ['000001', '399001', '399006']  # 上证指数、深证成指、创业板指

                    all_indices_df = self.get_index_data()
                    if all_indices_df is not None and not all_indices_df.empty:
                        for index_code in main_indices:
                            index_data = all_indices_df[all_indices_df['代码'].astype(str) == index_code]
                            if not index_data.empty:
                                row = index_data.iloc[0]
                                indices_data.append({
                                    'symbol': self._safe_str(row['代码']),
                                    'name': self._safe_str(row['名称']),
                                    'currentPrice': self._safe_float(row['最新价']),
                                    'change': self._safe_float(row['涨跌额']),
                                    'changePercent': self._safe_float(row['涨跌幅']),
                                    'volume': self._safe_int(row['成交量']) if '成交量' in row else 0,
                                    'turnover': self._safe_float(row['成交额']) if '成交额' in row else 0.0
                                })
                except Exception as e:
                    logger.warning(f"获取主要指数失败: {e}")

            return indices_data[:10]  # 限制返回数量

        except Exception as e:
            logger.error(f"获取市场指数失败: {e}")
            return []

    def get_hot_stocks(self, limit: int = 20, hot_type: str = "gainers") -> List[Dict[str, Any]]:
        """获取热门股票 - 使用AkShare真实数据"""
        try:
            hot_stocks = []

            # 尝试多种方式获取热门股票
            if hot_type == "gainers":
                # 获取涨幅榜
                hot_stocks = self._get_gainers(limit)
            elif hot_type == "volume":
                # 获取成交量排行榜
                hot_stocks = self._get_volume_leaders(limit)
            elif hot_type == "turnover":
                # 获取换手率排行榜
                hot_stocks = self._get_turnover_leaders(limit)
            else:
                # 默认获取涨幅榜
                hot_stocks = self._get_gainers(limit)

            # 如果主要方法失败，尝试备用方法
            if not hot_stocks:
                hot_stocks = self._get_hot_stocks_fallback(limit)

            return hot_stocks

        except Exception as e:
            logger.error(f"获取热门股票失败: {e}")
            return []

    def _get_gainers(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取涨幅榜股票"""
        try:
            # 使用缓存的股票数据
            spot_df = self._get_cached_spot_data()

            if spot_df is not None and not spot_df.empty:
                # 按涨跌幅排序，过滤掉ST股票和涨停股票
                filtered_df = spot_df[
                    (~spot_df['名称'].str.contains('ST', na=False)) &
                    (spot_df['涨跌幅'] > 0) &
                    (spot_df['涨跌幅'] < 9.8)  # 过滤掉接近涨停的股票
                ].sort_values('涨跌幅', ascending=False)

                return self._format_stock_data(filtered_df.head(limit))

        except Exception as e:
            logger.warning(f"获取涨幅榜失败: {e}")
            return []

    def _get_volume_leaders(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取成交量排行榜股票"""
        try:
            # 使用缓存的股票数据
            spot_df = self._get_cached_spot_data()

            if spot_df is not None and not spot_df.empty:
                # 按成交量排序，过滤掉价格过低的股票
                filtered_df = spot_df[
                    (spot_df['最新价'] > 2.0) &  # 过滤掉低价股
                    (~spot_df['名称'].str.contains('ST', na=False))
                ].sort_values('成交量', ascending=False)

                return self._format_stock_data(filtered_df.head(limit))

        except Exception as e:
            logger.warning(f"获取成交量排行榜失败: {e}")
            return []

    def _get_turnover_leaders(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取换手率排行榜股票"""
        try:
            # 使用缓存的股票数据
            spot_df = self._get_cached_spot_data()

            if spot_df is not None and not spot_df.empty and '换手率' in spot_df.columns:
                # 按换手率排序
                filtered_df = spot_df[
                    (spot_df['最新价'] > 2.0) &  # 过滤掉低价股
                    (~spot_df['名称'].str.contains('ST', na=False)) &
                    (spot_df['换手率'] > 0)
                ].sort_values('换手率', ascending=False)

                return self._format_stock_data(filtered_df.head(limit))

        except Exception as e:
            logger.warning(f"获取换手率排行榜失败: {e}")
            return []

    def _get_hot_stocks_fallback(self, limit: int = 20) -> List[Dict[str, Any]]:
        """备用热门股票获取方法"""
        try:
            # 使用缓存的股票数据
            spot_df = self._get_cached_spot_data()

            if spot_df is not None and not spot_df.empty:
                # 综合排序：考虑涨跌幅和成交量
                spot_df['热度分数'] = (spot_df['涨跌幅'] * 0.6 +
                                 (spot_df['成交量'] / spot_df['成交量'].max() * 10) * 0.4)

                filtered_df = spot_df[
                    (spot_df['最新价'] > 2.0) &
                    (~spot_df['名称'].str.contains('ST', na=False))
                ].sort_values('热度分数', ascending=False)

                return self._format_stock_data(filtered_df.head(limit))

        except Exception as e:
            logger.warning(f"备用热门股票获取失败: {e}")
            return []

    def _format_stock_data(self, df) -> List[Dict[str, Any]]:
        """格式化股票数据"""
        stocks = []
        for _, row in df.iterrows():
            try:
                stocks.append({
                    'symbol': self._safe_str(row['代码']),
                    'name': self._safe_str(row['名称']),
                    'currentPrice': self._safe_float(row['最新价']),
                    'change': self._safe_float(row['涨跌额']),
                    'changePercent': self._safe_float(row['涨跌幅']),
                    'volume': self._safe_int(row['成交量']),
                    'turnover': self._safe_float(row['成交额']),
                    'high': self._safe_float(row['最高']),
                    'low': self._safe_float(row['最低']),
                    'open': self._safe_float(row['今开']),
                    'preClose': self._safe_float(row['昨收']),
                    'marketCap': self._safe_float(row['总市值']) if '总市值' in row else None,
                    'pe': self._safe_float(row['市盈率-动态']) if '市盈率-动态' in row else None,
                    'pb': self._safe_float(row['市净率']) if '市净率' in row else None,
                    'turnoverRate': self._safe_float(row['换手率']) if '换手率' in row else None,
                    'volumeRatio': self._safe_float(row['量比']) if '量比' in row else None
                })
            except Exception as e:
                logger.warning(f"格式化股票数据失败: {e}")
                continue
        return stocks

    def get_stock_technical_indicators(self, symbol: str, period: str = "daily") -> Dict[str, Any]:
        """获取股票技术指标"""
        try:

            # 获取历史数据用于计算技术指标
            price_data = self.get_stock_price_history(symbol, period, limit=100)

            if not price_data:
                return {}

            # 转换为DataFrame
            df = pd.DataFrame(price_data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

            indicators = {}

            # 计算移动平均线
            for period in [5, 10, 20, 60]:
                ma_key = f'ma{period}'
                indicators[ma_key] = float(df['close'].rolling(window=period).mean().iloc[-1])

            # 计算RSI (简化版本)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            indicators['rsi'] = float(100 - (100 / (1 + rs.iloc[-1])))

            # 计算成交量变化
            indicators['volume_ratio'] = float(df['volume'].iloc[-1] / df['volume'].rolling(window=5).mean().iloc[-1])

            return indicators

        except Exception as e:
            logger.error(f"获取技术指标失败 {symbol}: {e}")
            return {}

    def get_market_overview(self) -> Dict[str, Any]:
        """获取市场概览数据"""
        try:
            # 使用缓存的股票数据
            spot_df = self._get_cached_spot_data()

            if spot_df is not None and not spot_df.empty:
                total_stocks = len(spot_df)
                rising_stocks = len(spot_df[spot_df['涨跌幅'] > 0])
                falling_stocks = len(spot_df[spot_df['涨跌幅'] < 0])
                unchanged_stocks = len(spot_df[spot_df['涨跌幅'] == 0])

                total_volume = self._safe_int(spot_df['成交量'].sum())
                total_turnover = self._safe_float(spot_df['成交额'].sum())

                avg_change = self._safe_float(spot_df['涨跌幅'].mean())

                return {
                    'totalStocks': total_stocks,
                    'risingStocks': rising_stocks,
                    'fallingStocks': falling_stocks,
                    'unchangedStocks': unchanged_stocks,
                    'risingRatio': self._safe_float(rising_stocks / total_stocks * 100),
                    'fallingRatio': self._safe_float(falling_stocks / total_stocks * 100),
                    'totalVolume': total_volume,
                    'totalTurnover': total_turnover,
                    'averageChange': avg_change,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"获取市场概览失败: {e}")
            return {}

    def get_gainers_losers(self, limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """获取涨跌排行榜"""
        try:
            def get_data():
                return ak.stock_zh_a_spot_em()

            spot_df = self._retry_akshare_call(get_data, max_retries=3, delay=1)

            if spot_df is not None and not spot_df.empty:
                # 过滤掉ST股票
                filtered_df = spot_df[~spot_df['名称'].str.contains('ST', na=False)]

                # 涨幅榜
                gainers_df = filtered_df[
                    (filtered_df['涨跌幅'] > 0) &
                    (filtered_df['涨跌幅'] < 9.8)
                ].sort_values('涨跌幅', ascending=False).head(limit)

                # 跌幅榜
                losers_df = filtered_df[
                    filtered_df['涨跌幅'] < 0
                ].sort_values('涨跌幅', ascending=True).head(limit)

                return {
                    'gainers': self._format_stock_data(gainers_df),
                    'losers': self._format_stock_data(losers_df)
                }

        except Exception as e:
            logger.error(f"获取涨跌排行榜失败: {e}")
            return {'gainers': [], 'losers': []}

    def get_volume_leaders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取成交量排行榜"""
        try:
            return self._get_volume_leaders(limit)
        except Exception as e:
            logger.error(f"获取成交量排行榜失败: {e}")
            return []

    def get_turnover_leaders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取换手率排行榜"""
        try:
            return self._get_turnover_leaders(limit)
        except Exception as e:
            logger.error(f"获取换手率排行榜失败: {e}")
            return []

    def get_sector_performance(self) -> List[Dict[str, Any]]:
        """获取行业板块表现"""
        try:
            def get_data():
                return ak.stock_board_industry_name_em()

            board_df = self._retry_akshare_call(get_data, max_retries=3, delay=1)

            if board_df is not None and not board_df.empty:
                sectors = []
                for _, row in board_df.head(20).iterrows():
                    try:
                        sectors.append({
                            'name': self._safe_str(row['板块名称']) if '板块名称' in row else self._safe_str(row.iloc[0]),
                            'changePercent': self._safe_float(row['涨跌幅']) if '涨跌幅' in row else 0.0,
                            'leadingStock': self._safe_str(row['领涨股票']) if '领涨股票' in row else '',
                            'stockCount': self._safe_int(row['股票数量']) if '股票数量' in row else 0
                        })
                    except Exception as e:
                        logger.warning(f"解析板块数据失败: {e}")
                        continue

                return sorted(sectors, key=lambda x: x['changePercent'], reverse=True)

        except Exception as e:
            logger.error(f"获取板块表现失败: {e}")
            return []

    def search_stocks_advanced(self, keyword: str, limit: int = 10,
                             filter_st: bool = True, min_price: float = 0.0) -> List[Dict[str, Any]]:
        """高级股票搜索"""
        try:
            def get_stock_data():
                return ak.stock_zh_a_spot_em()

            spot_df = self._retry_akshare_call(get_stock_data, max_retries=3, delay=1)

            if spot_df is not None and not spot_df.empty:
                # 应用过滤条件
                filtered_df = spot_df.copy()

                if filter_st:
                    filtered_df = filtered_df[~filtered_df['名称'].str.contains('ST', na=False)]

                if min_price > 0:
                    filtered_df = filtered_df[filtered_df['最新价'] >= min_price]

                # 搜索匹配的股票
                matched_stocks = filtered_df[
                    (filtered_df['代码'].str.contains(keyword, case=False, na=False)) |
                    (filtered_df['名称'].str.contains(keyword, case=False, na=False))
                ].head(limit)

                return self._format_stock_data(matched_stocks)

        except Exception as e:
            logger.error(f"高级股票搜索失败: {e}")
            return []

# 创建全局实例
stock_service = StockDataService()
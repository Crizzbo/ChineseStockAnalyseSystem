"""
AKShare工具包
为股票分析系统提供完整的AKShare数据获取和分析功能
"""

from .stock_analysis_system import StockAnalysisSystem
from .realtime_data_service import RealTimeDataService
from .historical_data_service import HistoricalDataService
from .fundamental_data_service import FundamentalDataService
from .market_analysis_service import MarketAnalysisService
from .data_cache_manager import DataCacheManager
from .utils.data_validator import DataValidator
from .utils.retry_decorator import retry_on_failure, api_monitor

__version__ = "1.0.0"
__author__ = "Stock Analysis Team"

# 导出主要类
__all__ = [
    'StockAnalysisSystem',
    'RealTimeDataService',
    'HistoricalDataService',
    'FundamentalDataService',
    'MarketAnalysisService',
    'DataCacheManager',
    'DataValidator',
    'retry_on_failure',
    'api_monitor'
]

# 默认配置
DEFAULT_CONFIG = {
    'cache': {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0,
        'enable_file_cache': True,
        'file_cache_dir': './cache'
    },
    'retry': {
        'max_retries': 3,
        'delay': 1,
        'backoff_factor': 2.0
    },
    'timeout': {
        'api_timeout': 30,
        'connection_timeout': 10
    }
}

def create_analysis_system(config=None, enable_cache=True):
    """
    创建股票分析系统实例

    Args:
        config: 配置字典，可选
        enable_cache: 是否启用缓存

    Returns:
        StockAnalysisSystem: 分析系统实例
    """
    if config is None:
        config = DEFAULT_CONFIG.copy()

    cache_config = config.get('cache', {}) if enable_cache else None
    return StockAnalysisSystem(enable_cache=enable_cache, cache_config=cache_config)
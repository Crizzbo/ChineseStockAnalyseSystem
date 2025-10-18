from app.utils.data_cache_manager import cache_manager
import akshare as ak
import pandas as pd

def get_stock_financial_data(stock_code):
    """获取股票财务数据
    
    Args:
        stock_code (str): 股票代码
        
    Returns:
        pd.DataFrame: 财务数据
    """
    def fetch_from_akshare():
        """从 AkShare 获取数据"""
        try:
            # 这里替换为实际的 AkShare 接口调用
            data = ak.stock_financial_abstract(symbol=stock_code)
            return data
        except Exception as e:
            print(f"从 AkShare 获取数据失败: {e}")
            return None
    
    # 使用缓存管理器获取或更新数据
    return cache_manager.get_or_update(
        data_type='financial',
        identifier=stock_code,
        data_fetcher=fetch_from_akshare,
        max_age_hours=24  # 缓存 24 小时
    )

def get_stock_daily_data(stock_code, start_date=None, end_date=None):
    """获取股票日线数据
    
    Args:
        stock_code (str): 股票代码
        start_date (str): 开始日期，格式：YYYYMMDD
        end_date (str): 结束日期，格式：YYYYMMDD
        
    Returns:
        pd.DataFrame: 日线数据
    """
    def fetch_from_akshare():
        """从 AkShare 获取数据"""
        try:
            data = ak.stock_zh_a_hist(
                symbol=stock_code,
                start_date=start_date,
                end_date=end_date,
                adjust=""
            )
            return data
        except Exception as e:
            print(f"从 AkShare 获取数据失败: {e}")
            return None
    
    # 使用缓存管理器获取或更新数据
    return cache_manager.get_or_update(
        data_type='daily',
        identifier=f"{stock_code}_{start_date}_{end_date}",
        data_fetcher=fetch_from_akshare,
        max_age_hours=24  # 缓存 24 小时
    )

def get_stock_realtime_data(stock_code):
    """获取股票实时数据
    
    Args:
        stock_code (str): 股票代码
        
    Returns:
        pd.DataFrame: 实时数据
    """
    def fetch_from_akshare():
        """从 AkShare 获取数据"""
        try:
            data = ak.stock_zh_a_spot_em()  # 获取所有股票实时数据
            # 筛选指定股票的数据
            if data is not None:
                return data[data['代码'] == stock_code]
            return None
        except Exception as e:
            print(f"从 AkShare 获取数据失败: {e}")
            return None
    
    # 实时数据缓存时间较短
    return cache_manager.get_or_update(
        data_type='realtime',
        identifier=stock_code,
        data_fetcher=fetch_from_akshare,
        max_age_hours=0.1  # 缓存 6 分钟
    )
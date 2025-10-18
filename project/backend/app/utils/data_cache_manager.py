import os
import pandas as pd
from datetime import datetime, timedelta
import logging

class DataCacheManager:
    """数据缓存管理器
    负责管理股票数据的本地缓存，包括读取、写入和更新
    """
    
    def __init__(self, cache_dir='cache'):
        """初始化缓存管理器
        
        Args:
            cache_dir (str): 缓存目录的路径
        """
        self.cache_dir = cache_dir
        self._ensure_cache_dir()
        
    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def _get_cache_path(self, data_type, identifier):
        """获取缓存文件路径
        
        Args:
            data_type (str): 数据类型，如 'financial', 'daily', 'real_time'
            identifier (str): 数据标识符，如股票代码
            
        Returns:
            str: 缓存文件的完整路径
        """
        filename = f"{data_type}_{identifier}.csv"
        return os.path.join(self.cache_dir, filename)
        
    def is_cache_valid(self, cache_path, max_age_hours=24):
        """检查缓存是否有效
        
        Args:
            cache_path (str): 缓存文件路径
            max_age_hours (int): 缓存最大有效时间（小时）
            
        Returns:
            bool: 如果缓存有效返回True，否则返回False
        """
        if not os.path.exists(cache_path):
            return False
            
        # 获取文件最后修改时间
        file_mtime = datetime.fromtimestamp(os.path.getmtime(cache_path))
        age = datetime.now() - file_mtime
        
        return age.total_seconds() < max_age_hours * 3600
        
    def read_cache(self, data_type, identifier):
        """读取缓存数据
        
        Args:
            data_type (str): 数据类型
            identifier (str): 数据标识符
            
        Returns:
            pd.DataFrame: 缓存的数据，如果缓存不存在返回None
        """
        cache_path = self._get_cache_path(data_type, identifier)
        
        if not os.path.exists(cache_path):
            return None
            
        try:
            return pd.read_csv(cache_path)
        except Exception as e:
            logging.error(f"读取缓存文件失败: {e}")
            return None
            
    def write_cache(self, data_type, identifier, data):
        """写入数据到缓存
        
        Args:
            data_type (str): 数据类型
            identifier (str): 数据标识符
            data (pd.DataFrame): 要缓存的数据
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data must be a pandas DataFrame")
            
        cache_path = self._get_cache_path(data_type, identifier)
        
        try:
            data.to_csv(cache_path, index=False)
        except Exception as e:
            logging.error(f"写入缓存文件失败: {e}")
            
    def get_or_update(self, data_type, identifier, data_fetcher, max_age_hours=24):
        """获取数据，如果缓存无效则更新
        
        Args:
            data_type (str): 数据类型
            identifier (str): 数据标识符
            data_fetcher (callable): 获取新数据的函数
            max_age_hours (int): 缓存最大有效时间（小时）
            
        Returns:
            pd.DataFrame: 数据内容
        """
        cache_path = self._get_cache_path(data_type, identifier)
        
        # 检查缓存是否有效
        if self.is_cache_valid(cache_path, max_age_hours):
            cached_data = self.read_cache(data_type, identifier)
            if cached_data is not None:
                return cached_data
                
        # 获取新数据并缓存
        try:
            new_data = data_fetcher()
            if new_data is not None:
                self.write_cache(data_type, identifier, new_data)
                return new_data
        except Exception as e:
            logging.error(f"获取新数据失败: {e}")
            # 如果获取新数据失败，尝试返回过期的缓存数据
            return self.read_cache(data_type, identifier)
            
        return None

# 创建全局缓存管理器实例
cache_manager = DataCacheManager()
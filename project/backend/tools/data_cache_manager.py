"""
数据缓存管理器
用于管理股票数据的缓存，提高数据访问效率
"""

import json
import redis
import pickle
import hashlib
import pandas as pd
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)


class DataCacheManager:
    """数据缓存管理器"""

    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379,
                 redis_db: int = 0, redis_password: Optional[str] = None,
                 enable_file_cache: bool = True, file_cache_dir: str = './cache'):
        """
        初始化缓存管理器

        Args:
            redis_host: Redis主机地址
            redis_port: Redis端口
            redis_db: Redis数据库编号
            redis_password: Redis密码
            enable_file_cache: 是否启用文件缓存作为备选
            file_cache_dir: 文件缓存目录
        """
        self.logger = logger
        self.enable_file_cache = enable_file_cache
        self.file_cache_dir = file_cache_dir

        # 缓存过期时间配置（秒）
        self.cache_config = {
            'realtime': 30,          # 实时数据缓存30秒
            'daily': 3600,           # 日线数据缓存1小时
            'weekly': 7200,          # 周线数据缓存2小时
            'monthly': 14400,        # 月线数据缓存4小时
            'fundamental': 86400,    # 基本面数据缓存1天
            'financial': 86400,      # 财务数据缓存1天
            'technical': 1800,       # 技术指标缓存30分钟
            'market_analysis': 1800, # 市场分析缓存30分钟
            'default': 3600          # 默认缓存1小时
        }

        # 初始化Redis连接
        self.redis_client = None
        self.redis_available = False
        self._init_redis(redis_host, redis_port, redis_db, redis_password)

        # 初始化文件缓存
        if self.enable_file_cache:
            self._init_file_cache()

    def _init_redis(self, host: str, port: int, db: int, password: Optional[str]):
        """初始化Redis连接"""
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=False,  # 保持二进制模式以支持pickle
                socket_timeout=5,
                socket_connect_timeout=5
            )

            # 测试连接
            self.redis_client.ping()
            self.redis_available = True
            self.logger.info(f"Redis连接成功: {host}:{port}")

        except Exception as e:
            self.logger.warning(f"Redis连接失败: {str(e)}, 将使用文件缓存")
            self.redis_available = False
            self.enable_file_cache = True

    def _init_file_cache(self):
        """初始化文件缓存目录"""
        try:
            if not os.path.exists(self.file_cache_dir):
                os.makedirs(self.file_cache_dir, exist_ok=True)
            self.logger.info(f"文件缓存目录初始化成功: {self.file_cache_dir}")
        except Exception as e:
            self.logger.error(f"文件缓存目录初始化失败: {str(e)}")

    def _generate_cache_key(self, symbol: str, data_type: str, **kwargs) -> str:
        """
        生成缓存键

        Args:
            symbol: 股票代码
            data_type: 数据类型
            **kwargs: 其他参数

        Returns:
            str: 缓存键
        """
        # 创建基础键
        base_key = f"stock:{symbol}:{data_type}"

        # 添加额外参数
        if kwargs:
            # 将参数按键排序并转换为字符串
            sorted_params = sorted(kwargs.items())
            params_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            base_key += f":{params_str}"

        # 对长键进行MD5哈希以避免键过长
        if len(base_key) > 200:
            hash_obj = hashlib.md5(base_key.encode())
            return f"stock:hash:{hash_obj.hexdigest()}"

        return base_key

    def get_cached_data(self, symbol: str, data_type: str, **kwargs) -> Optional[Any]:
        """
        获取缓存数据

        Args:
            symbol: 股票代码
            data_type: 数据类型
            **kwargs: 其他参数

        Returns:
            缓存的数据，如果不存在或已过期则返回None
        """
        cache_key = self._generate_cache_key(symbol, data_type, **kwargs)

        try:
            # 首先尝试从Redis获取
            if self.redis_available:
                cached_data = self._get_from_redis(cache_key)
                if cached_data is not None:
                    return cached_data

            # 如果Redis不可用或没有找到，尝试文件缓存
            if self.enable_file_cache:
                cached_data = self._get_from_file(cache_key)
                if cached_data is not None:
                    return cached_data

            return None

        except Exception as e:
            self.logger.error(f"获取缓存数据失败 {cache_key}: {str(e)}")
            return None

    def cache_data(self, symbol: str, data_type: str, data: Any, **kwargs) -> bool:
        """
        缓存数据

        Args:
            symbol: 股票代码
            data_type: 数据类型
            data: 要缓存的数据
            **kwargs: 其他参数

        Returns:
            bool: 缓存是否成功
        """
        cache_key = self._generate_cache_key(symbol, data_type, **kwargs)
        expire_time = self.cache_config.get(data_type, self.cache_config['default'])

        success = False

        try:
            # 尝试缓存到Redis
            if self.redis_available:
                if self._cache_to_redis(cache_key, data, expire_time):
                    success = True

            # 如果启用文件缓存，也缓存到文件
            if self.enable_file_cache:
                if self._cache_to_file(cache_key, data, expire_time):
                    success = True

            if success:
                self.logger.debug(f"数据缓存成功: {cache_key}")
            else:
                self.logger.warning(f"数据缓存失败: {cache_key}")

            return success

        except Exception as e:
            self.logger.error(f"缓存数据失败 {cache_key}: {str(e)}")
            return False

    def _get_from_redis(self, cache_key: str) -> Optional[Any]:
        """从Redis获取数据"""
        try:
            cached_bytes = self.redis_client.get(cache_key)
            if cached_bytes:
                return pickle.loads(cached_bytes)
            return None
        except Exception as e:
            self.logger.warning(f"从Redis获取数据失败 {cache_key}: {str(e)}")
            return None

    def _cache_to_redis(self, cache_key: str, data: Any, expire_time: int) -> bool:
        """缓存数据到Redis"""
        try:
            serialized_data = pickle.dumps(data)
            self.redis_client.setex(cache_key, expire_time, serialized_data)
            return True
        except Exception as e:
            self.logger.warning(f"缓存数据到Redis失败 {cache_key}: {str(e)}")
            return False

    def _get_from_file(self, cache_key: str) -> Optional[Any]:
        """从文件获取数据"""
        try:
            # 生成文件名
            safe_key = cache_key.replace(':', '_').replace('/', '_')
            file_path = os.path.join(self.file_cache_dir, f"{safe_key}.cache")

            if not os.path.exists(file_path):
                return None

            # 检查文件是否过期
            file_mtime = os.path.getmtime(file_path)
            current_time = datetime.now().timestamp()

            # 读取过期时间（存储在文件的第一行）
            with open(file_path, 'rb') as f:
                expire_timestamp = pickle.load(f)
                if current_time > expire_timestamp:
                    # 文件已过期，删除文件
                    os.remove(file_path)
                    return None

                # 读取实际数据
                data = pickle.load(f)
                return data

        except Exception as e:
            self.logger.warning(f"从文件获取数据失败 {cache_key}: {str(e)}")
            return None

    def _cache_to_file(self, cache_key: str, data: Any, expire_time: int) -> bool:
        """缓存数据到文件"""
        try:
            safe_key = cache_key.replace(':', '_').replace('/', '_')
            file_path = os.path.join(self.file_cache_dir, f"{safe_key}.cache")

            # 计算过期时间戳
            expire_timestamp = datetime.now().timestamp() + expire_time

            # 写入文件
            with open(file_path, 'wb') as f:
                pickle.dump(expire_timestamp, f)
                pickle.dump(data, f)

            return True

        except Exception as e:
            self.logger.warning(f"缓存数据到文件失败 {cache_key}: {str(e)}")
            return False

    def clear_cache(self, pattern: Optional[str] = None) -> int:
        """
        清理缓存

        Args:
            pattern: 缓存键模式，如 "stock:000001:*"

        Returns:
            int: 清理的缓存数量
        """
        cleared_count = 0

        try:
            # 清理Redis缓存
            if self.redis_available:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        cleared_count += self.redis_client.delete(*keys)
                else:
                    # 清理所有股票相关缓存
                    keys = self.redis_client.keys("stock:*")
                    if keys:
                        cleared_count += self.redis_client.delete(*keys)

            # 清理文件缓存
            if self.enable_file_cache:
                cleared_count += self._clear_file_cache(pattern)

            self.logger.info(f"清理缓存完成，共清理{cleared_count}个缓存项")
            return cleared_count

        except Exception as e:
            self.logger.error(f"清理缓存失败: {str(e)}")
            return 0

    def _clear_file_cache(self, pattern: Optional[str] = None) -> int:
        """清理文件缓存"""
        try:
            if not os.path.exists(self.file_cache_dir):
                return 0

            cleared_count = 0
            for filename in os.listdir(self.file_cache_dir):
                if filename.endswith('.cache'):
                    file_path = os.path.join(self.file_cache_dir, filename)

                    # 如果指定了模式，进行模式匹配
                    if pattern:
                        # 简单的模式匹配（将Redis模式转换为文件名模式）
                        file_pattern = pattern.replace(':', '_').replace('*', '')
                        if file_pattern not in filename:
                            continue

                    try:
                        os.remove(file_path)
                        cleared_count += 1
                    except Exception:
                        continue

            return cleared_count

        except Exception as e:
            self.logger.warning(f"清理文件缓存失败: {str(e)}")
            return 0

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            Dict: 缓存统计信息
        """
        stats = {
            'redis_available': self.redis_available,
            'file_cache_enabled': self.enable_file_cache,
            'cache_config': self.cache_config,
            'redis_stats': {},
            'file_cache_stats': {}
        }

        try:
            # Redis统计
            if self.redis_available:
                info = self.redis_client.info()
                stats['redis_stats'] = {
                    'used_memory': info.get('used_memory_human'),
                    'connected_clients': info.get('connected_clients'),
                    'total_keys': len(self.redis_client.keys("stock:*"))
                }

            # 文件缓存统计
            if self.enable_file_cache and os.path.exists(self.file_cache_dir):
                cache_files = [f for f in os.listdir(self.file_cache_dir) if f.endswith('.cache')]
                total_size = sum(
                    os.path.getsize(os.path.join(self.file_cache_dir, f))
                    for f in cache_files
                )
                stats['file_cache_stats'] = {
                    'total_files': len(cache_files),
                    'total_size_mb': round(total_size / 1024 / 1024, 2),
                    'cache_dir': self.file_cache_dir
                }

        except Exception as e:
            self.logger.error(f"获取缓存统计失败: {str(e)}")

        return stats

    def cleanup_expired_cache(self) -> int:
        """
        清理过期的缓存项

        Returns:
            int: 清理的缓存数量
        """
        cleaned_count = 0

        try:
            # 清理过期的文件缓存
            if self.enable_file_cache and os.path.exists(self.file_cache_dir):
                current_time = datetime.now().timestamp()

                for filename in os.listdir(self.file_cache_dir):
                    if not filename.endswith('.cache'):
                        continue

                    file_path = os.path.join(self.file_cache_dir, filename)
                    try:
                        with open(file_path, 'rb') as f:
                            expire_timestamp = pickle.load(f)
                            if current_time > expire_timestamp:
                                os.remove(file_path)
                                cleaned_count += 1
                    except Exception:
                        # 如果文件损坏，也删除它
                        try:
                            os.remove(file_path)
                            cleaned_count += 1
                        except Exception:
                            continue

            self.logger.info(f"清理过期缓存完成，共清理{cleaned_count}个文件")
            return cleaned_count

        except Exception as e:
            self.logger.error(f"清理过期缓存失败: {str(e)}")
            return 0
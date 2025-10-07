"""
重试装饰器工具
用于AKShare API调用的错误处理和重试机制
"""

import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries: int = 3, delay: int = 1, backoff_factor: float = 2.0):
    """
    重试装饰器，用于处理API调用失败的重试逻辑

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff_factor: 退避因子，每次重试延迟时间的倍数

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == max_retries:
                        # 最后一次重试失败，抛出异常
                        logger.error(f"函数 {func.__name__} 重试{max_retries}次后仍然失败: {str(e)}")
                        raise e

                    # 计算延迟时间（指数退避）
                    current_delay = delay * (backoff_factor ** attempt)
                    logger.warning(f"函数 {func.__name__} 第{attempt + 1}次调用失败: {str(e)}, "
                                 f"{current_delay}秒后重试...")

                    time.sleep(current_delay)

            # 这行代码理论上不会执行到
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


class RetryConfig:
    """重试配置类"""

    def __init__(self, max_retries: int = 3, delay: int = 1,
                 backoff_factor: float = 2.0, max_delay: int = 60):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay

    def create_decorator(self):
        """创建带配置的装饰器"""
        return retry_on_failure(
            max_retries=self.max_retries,
            delay=self.delay,
            backoff_factor=self.backoff_factor
        )


# 预定义的重试配置
QUICK_RETRY = RetryConfig(max_retries=2, delay=0.5, backoff_factor=1.5)
STANDARD_RETRY = RetryConfig(max_retries=3, delay=1, backoff_factor=2.0)
AGGRESSIVE_RETRY = RetryConfig(max_retries=5, delay=2, backoff_factor=2.0)


def retry_with_config(config: RetryConfig):
    """使用指定配置的重试装饰器"""
    return config.create_decorator()


class APICallMonitor:
    """API调用监控器"""

    def __init__(self):
        self.call_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_retry_count = 0

    def record_call(self, success: bool, retry_count: int = 0):
        """记录API调用结果"""
        self.call_count += 1
        self.total_retry_count += retry_count

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

    def get_statistics(self) -> dict:
        """获取统计信息"""
        if self.call_count == 0:
            return {
                'total_calls': 0,
                'success_rate': 0.0,
                'failure_rate': 0.0,
                'avg_retry_count': 0.0
            }

        return {
            'total_calls': self.call_count,
            'successful_calls': self.success_count,
            'failed_calls': self.failure_count,
            'success_rate': self.success_count / self.call_count,
            'failure_rate': self.failure_count / self.call_count,
            'total_retries': self.total_retry_count,
            'avg_retry_count': self.total_retry_count / self.call_count
        }

    def reset_statistics(self):
        """重置统计信息"""
        self.call_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_retry_count = 0


# 全局监控器实例
api_monitor = APICallMonitor()


def monitored_retry(max_retries: int = 3, delay: int = 1, backoff_factor: float = 2.0):
    """
    带监控功能的重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间
        backoff_factor: 退避因子
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retry_count = 0
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    # 记录成功调用
                    api_monitor.record_call(success=True, retry_count=retry_count)
                    return result

                except Exception as e:
                    last_exception = e
                    retry_count += 1

                    if attempt == max_retries:
                        # 记录失败调用
                        api_monitor.record_call(success=False, retry_count=retry_count)
                        logger.error(f"函数 {func.__name__} 重试{max_retries}次后仍然失败: {str(e)}")
                        raise e

                    current_delay = min(delay * (backoff_factor ** attempt), 60)  # 最大延迟60秒
                    logger.warning(f"函数 {func.__name__} 第{attempt + 1}次调用失败: {str(e)}, "
                                 f"{current_delay}秒后重试...")

                    time.sleep(current_delay)

            if last_exception:
                raise last_exception

        return wrapper
    return decorator
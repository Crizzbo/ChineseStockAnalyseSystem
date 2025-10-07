"""
定时任务调度器
"""
from celery import Celery
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def make_celery(app):
    """创建Celery实例"""
    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    )

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# 这个函数需要在应用初始化时调用
celery = None

def init_scheduler(app):
    """初始化任务调度器"""
    global celery
    celery = make_celery(app)

    # 配置定时任务
    celery.conf.beat_schedule = {
        # 每30秒更新股票数据
        'update-stock-data': {
            'task': 'app.tasks.scheduler.update_stock_data_task',
            'schedule': 30.0,
        },
        # 每分钟更新市场指数
        'update-market-data': {
            'task': 'app.tasks.scheduler.update_market_data_task',
            'schedule': 60.0,
        },
        # 每小时清理缓存
        'cleanup-cache': {
            'task': 'app.tasks.scheduler.cleanup_cache_task',
            'schedule': 3600.0,
        }
    }

    celery.conf.timezone = 'Asia/Shanghai'
    return celery

@celery.task
def update_stock_data_task():
    """更新股票数据的定时任务"""
    try:
        from app.websocket.events import push_stock_updates
        push_stock_updates()
        logger.info('股票数据更新任务完成')
    except Exception as e:
        logger.error(f'股票数据更新任务失败: {e}')

@celery.task
def update_market_data_task():
    """更新市场数据的定时任务"""
    try:
        from app.websocket.events import push_market_updates
        push_market_updates()
        logger.info('市场数据更新任务完成')
    except Exception as e:
        logger.error(f'市场数据更新任务失败: {e}')

@celery.task
def cleanup_cache_task():
    """清理缓存的定时任务"""
    try:
        from app import redis_client
        if redis_client:
            # 这里可以添加缓存清理逻辑
            # 比如清理过期的JWT黑名单等
            logger.info('缓存清理任务完成')
    except Exception as e:
        logger.error(f'缓存清理任务失败: {e}')

# 手动触发的任务
@celery.task
def refresh_all_stock_data():
    """手动刷新所有股票数据"""
    try:
        from app.services.stock_data import stock_service
        # 这里可以添加批量刷新逻辑
        logger.info('手动刷新股票数据任务完成')
    except Exception as e:
        logger.error(f'手动刷新股票数据任务失败: {e}')

@celery.task
def generate_daily_report():
    """生成日报的任务"""
    try:
        # 这里可以添加生成报表的逻辑
        logger.info('日报生成任务完成')
    except Exception as e:
        logger.error(f'日报生成任务失败: {e}')
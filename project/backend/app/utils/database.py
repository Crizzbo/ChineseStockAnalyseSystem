"""
数据库工具函数
"""
from app import db
from flask import current_app
import os

def init_database():
    """初始化数据库"""
    try:
        # 创建所有表
        db.create_all()
        current_app.logger.info("数据库表创建成功")
        return True
    except Exception as e:
        current_app.logger.error(f"数据库初始化失败: {e}")
        return False

def reset_database():
    """重置数据库（删除所有表并重新创建）"""
    try:
        # 删除所有表
        db.drop_all()
        current_app.logger.info("删除所有数据库表")

        # 重新创建表
        db.create_all()
        current_app.logger.info("重新创建数据库表")
        return True
    except Exception as e:
        current_app.logger.error(f"数据库重置失败: {e}")
        return False

def create_sample_data():
    """创建示例数据"""
    try:
        from app.models.user import User
        from app.models.portfolio import Portfolio, PortfolioStock
        from app.models.watchlist import WatchList, WatchListStock

        # 检查是否已有数据
        if User.query.first():
            current_app.logger.info("数据库中已有数据，跳过示例数据创建")
            return True

        # 创建示例用户
        user = User(
            username='demo',
            email='demo@example.com',
            password='password123',
            nickname='演示用户'
        )
        db.session.add(user)
        db.session.flush()  # 获取用户ID

        # 创建示例投资组合
        portfolio = Portfolio(
            name='我的主要组合',
            user_id=user.id,
            description='长期价值投资组合'
        )
        db.session.add(portfolio)
        db.session.flush()

        # 添加示例股票
        stocks_data = [
            {'symbol': '000001', 'name': '平安银行', 'shares': 2000, 'avg_cost': 12.50},
            {'symbol': '600519', 'name': '贵州茅台', 'shares': 30, 'avg_cost': 1600.00},
            {'symbol': '000858', 'name': '五粮液', 'shares': 300, 'avg_cost': 165.00}
        ]

        for stock_data in stocks_data:
            portfolio_stock = PortfolioStock(
                portfolio_id=portfolio.id,
                **stock_data
            )
            db.session.add(portfolio_stock)

        # 创建示例自选股列表
        watchlist = WatchList(
            name='我的自选股',
            user_id=user.id,
            description='重点关注的股票'
        )
        db.session.add(watchlist)
        db.session.flush()

        # 添加示例自选股
        watch_stocks = [
            {'symbol': '600036', 'name': '招商银行', 'notes': '银行股龙头'},
            {'symbol': '000002', 'name': '万科A', 'notes': '地产龙头'}
        ]

        for watch_data in watch_stocks:
            watchlist_stock = WatchListStock(
                watchlist_id=watchlist.id,
                **watch_data
            )
            db.session.add(watchlist_stock)

        db.session.commit()
        current_app.logger.info("示例数据创建成功")
        return True

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建示例数据失败: {e}")
        return False

def check_database_connection():
    """检查数据库连接"""
    try:
        # 尝试执行一个简单的查询
        db.session.execute('SELECT 1')
        current_app.logger.info("数据库连接正常")
        return True
    except Exception as e:
        current_app.logger.error(f"数据库连接失败: {e}")
        return False

def get_database_info():
    """获取数据库信息"""
    try:
        from sqlalchemy import text

        info = {}

        # 获取数据库版本
        result = db.session.execute(text("SELECT version()"))
        version = result.scalar()
        info['version'] = version

        # 获取表信息
        from app.models.user import User
        from app.models.portfolio import Portfolio, PortfolioStock
        from app.models.watchlist import WatchList, WatchListStock

        info['tables'] = {
            'users': User.query.count(),
            'portfolios': Portfolio.query.count(),
            'portfolio_stocks': PortfolioStock.query.count(),
            'watchlists': WatchList.query.count(),
            'watchlist_stocks': WatchListStock.query.count()
        }

        return info
    except Exception as e:
        current_app.logger.error(f"获取数据库信息失败: {e}")
        return None
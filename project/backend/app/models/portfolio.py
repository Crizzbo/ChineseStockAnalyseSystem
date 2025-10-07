"""
投资组合模型
"""
from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

class Portfolio(db.Model):
    """投资组合模型"""
    __tablename__ = 'portfolios'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    total_cost = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系定义
    stocks = relationship('PortfolioStock', backref='portfolio', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, name, user_id, description=None):
        self.name = name
        self.user_id = user_id
        self.description = description

    def calculate_metrics(self, stock_prices=None):
        """计算投资组合指标"""
        if not stock_prices:
            stock_prices = {}

        total_value = 0.0
        total_cost = 0.0

        for stock in self.stocks:
            current_price = stock_prices.get(stock.symbol, stock.avg_cost)
            stock_value = stock.shares * current_price
            stock_cost = stock.shares * stock.avg_cost

            total_value += stock_value
            total_cost += stock_cost

        self.total_cost = total_cost
        total_gain_loss = total_value - total_cost
        total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0

        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_gain_loss': total_gain_loss,
            'total_gain_loss_percent': total_gain_loss_percent
        }

    def to_dict(self, include_stocks=True, stock_prices=None):
        """转换为字典"""
        metrics = self.calculate_metrics(stock_prices)

        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            **metrics
        }

        if include_stocks:
            data['stocks'] = [stock.to_dict(stock_prices) for stock in self.stocks]

        return data

    def __repr__(self):
        return f'<Portfolio {self.name}>'


class PortfolioStock(db.Model):
    """投资组合股票模型"""
    __tablename__ = 'portfolio_stocks'

    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    shares = Column(Integer, nullable=False)
    avg_cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, portfolio_id, symbol, name, shares, avg_cost):
        self.portfolio_id = portfolio_id
        self.symbol = symbol
        self.name = name
        self.shares = shares
        self.avg_cost = avg_cost

    def calculate_metrics(self, current_price=None):
        """计算股票持仓指标"""
        if current_price is None:
            current_price = self.avg_cost

        total_cost = self.shares * self.avg_cost
        total_value = self.shares * current_price
        gain_loss = total_value - total_cost
        gain_loss_percent = (gain_loss / total_cost * 100) if total_cost > 0 else 0

        return {
            'current_price': current_price,
            'total_cost': total_cost,
            'total_value': total_value,
            'gain_loss': gain_loss,
            'gain_loss_percent': gain_loss_percent
        }

    def to_dict(self, stock_prices=None):
        """转换为字典"""
        current_price = None
        if stock_prices and self.symbol in stock_prices:
            current_price = stock_prices[self.symbol]

        metrics = self.calculate_metrics(current_price)

        # 计算权重需要投资组合总值
        portfolio_metrics = self.portfolio.calculate_metrics(stock_prices)
        weight = (metrics['total_value'] / portfolio_metrics['total_value'] * 100) if portfolio_metrics['total_value'] > 0 else 0

        return {
            'id': self.id,
            'portfolio_id': self.portfolio_id,
            'symbol': self.symbol,
            'name': self.name,
            'shares': self.shares,
            'avg_cost': self.avg_cost,
            'weight': weight,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            **metrics
        }

    def __repr__(self):
        return f'<PortfolioStock {self.symbol} {self.shares}>'
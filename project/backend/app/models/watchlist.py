"""
自选股模型
"""
from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

class WatchList(db.Model):
    """自选股列表模型"""
    __tablename__ = 'watchlists'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系定义
    stocks = relationship('WatchListStock', backref='watchlist', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, name, user_id, description=None):
        self.name = name
        self.user_id = user_id
        self.description = description

    def to_dict(self, include_stocks=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'stock_count': self.stocks.count()
        }

        if include_stocks:
            data['stocks'] = [stock.to_dict() for stock in self.stocks]

        return data

    def __repr__(self):
        return f'<WatchList {self.name}>'


class WatchListStock(db.Model):
    """自选股股票模型"""
    __tablename__ = 'watchlist_stocks'

    id = Column(Integer, primary_key=True)
    watchlist_id = Column(Integer, ForeignKey('watchlists.id'), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    added_price = Column(String(20), nullable=True)  # 添加时的价格（用于参考）
    notes = Column(Text, nullable=True)  # 备注
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, watchlist_id, symbol, name, added_price=None, notes=None):
        self.watchlist_id = watchlist_id
        self.symbol = symbol
        self.name = name
        self.added_price = added_price
        self.notes = notes

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'watchlist_id': self.watchlist_id,
            'symbol': self.symbol,
            'name': self.name,
            'added_price': float(self.added_price) if self.added_price else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<WatchListStock {self.symbol}>'
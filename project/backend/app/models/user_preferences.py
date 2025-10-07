"""
用户偏好设置模型
"""
from app import db
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

class UserPreferences(db.Model):
    """用户偏好设置模型"""
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True, index=True)

    # 外观设置
    theme = Column(String(20), default='light', nullable=False)  # light, dark, auto
    language = Column(String(10), default='zh', nullable=False)  # zh, en

    # 通知设置
    notifications = Column(JSON, default=lambda: {
        'priceAlerts': True,
        'portfolioUpdates': True,
        'newsAlerts': False,
        'systemNotifications': True
    }, nullable=False)

    # 显示设置
    display_settings = Column(JSON, default=lambda: {
        'autoRefresh': True,
        'refreshInterval': 30,
        'showPremarket': False,
        'showAfterHours': False,
        'defaultChartType': 'candlestick',
        'priceFormat': 'absolute'
    }, nullable=False)

    # 交易设置
    trading_settings = Column(JSON, default=lambda: {
        'confirmOrders': True,
        'defaultOrderType': 'market',
        'riskWarnings': True
    }, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关系定义
    user = relationship('User', backref='preferences')

    def __init__(self, user_id, **kwargs):
        self.user_id = user_id

        # 设置默认值
        self.theme = kwargs.get('theme', 'light')
        self.language = kwargs.get('language', 'zh')
        self.notifications = kwargs.get('notifications', {
            'priceAlerts': True,
            'portfolioUpdates': True,
            'newsAlerts': False,
            'systemNotifications': True
        })
        self.display_settings = kwargs.get('display_settings', {
            'autoRefresh': True,
            'refreshInterval': 30,
            'showPremarket': False,
            'showAfterHours': False,
            'defaultChartType': 'candlestick',
            'priceFormat': 'absolute'
        })
        self.trading_settings = kwargs.get('trading_settings', {
            'confirmOrders': True,
            'defaultOrderType': 'market',
            'riskWarnings': True
        })

    def update_preferences(self, preferences_data):
        """更新用户偏好设置"""
        if 'theme' in preferences_data:
            self.theme = preferences_data['theme']
        if 'language' in preferences_data:
            self.language = preferences_data['language']
        if 'notifications' in preferences_data:
            self.notifications = preferences_data['notifications']
        if 'display' in preferences_data:
            self.display_settings = preferences_data['display']
        if 'trading' in preferences_data:
            self.trading_settings = preferences_data['trading']

        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'theme': self.theme,
            'language': self.language,
            'notifications': self.notifications,
            'display': self.display_settings,
            'trading': self.trading_settings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_or_create_for_user(cls, user_id):
        """获取或创建用户偏好设置"""
        preferences = cls.query.filter_by(user_id=user_id).first()
        if not preferences:
            preferences = cls(user_id=user_id)
            db.session.add(preferences)
            db.session.commit()
        return preferences

    def __repr__(self):
        return f'<UserPreferences user_id={self.user_id}>'
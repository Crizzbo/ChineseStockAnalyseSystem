"""
WebSocket事件处理
"""
from flask import request
from flask_socketio import emit, join_room, leave_room, disconnect
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from datetime import datetime
import json
import logging

from app import socketio, redis_client
from app.services.stock_data import stock_service

logger = logging.getLogger(__name__)

# 存储连接的客户端信息
connected_clients = {}

@socketio.on('connect')
def handle_connect(auth=None):
    """客户端连接事件"""
    try:
        client_id = request.sid
        logger.info(f'客户端连接: {client_id}')

        # 验证JWT令牌（可选）
        user_id = None
        if auth and 'token' in auth:
            try:
                # 这里需要手动验证JWT，因为SocketIO的认证机制与Flask-JWT不同
                # 实际应用中可能需要更复杂的认证逻辑
                pass
            except Exception as e:
                logger.warning(f'WebSocket认证失败: {e}')

        # 存储客户端信息
        connected_clients[client_id] = {
            'user_id': user_id,
            'connected_at': datetime.now().isoformat(),
            'subscriptions': set()
        }

        # 发送连接成功消息
        emit('connection_status', {
            'status': 'connected',
            'client_id': client_id,
            'timestamp': datetime.now().isoformat()
        })

        logger.info(f'客户端 {client_id} 连接成功')

    except Exception as e:
        logger.error(f'处理连接事件失败: {e}')
        disconnect()

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接事件"""
    try:
        client_id = request.sid
        logger.info(f'客户端断开连接: {client_id}')

        # 清理客户端信息
        if client_id in connected_clients:
            client_info = connected_clients[client_id]

            # 离开所有订阅的房间
            for subscription in client_info['subscriptions']:
                leave_room(subscription)

            # 删除客户端记录
            del connected_clients[client_id]

        logger.info(f'客户端 {client_id} 断开连接处理完成')

    except Exception as e:
        logger.error(f'处理断开连接事件失败: {e}')

@socketio.on('subscribe_stock')
def handle_subscribe_stock(data):
    """订阅股票实时数据"""
    try:
        client_id = request.sid
        symbols = data.get('symbols', [])

        if not symbols or not isinstance(symbols, list):
            emit('error', {'message': '股票代码列表不能为空'})
            return

        if len(symbols) > 20:
            emit('error', {'message': '最多支持订阅20只股票'})
            return

        # 验证股票代码
        valid_symbols = []
        for symbol in symbols:
            if isinstance(symbol, str) and symbol.strip():
                valid_symbols.append(symbol.strip())

        if not valid_symbols:
            emit('error', {'message': '没有有效的股票代码'})
            return

        # 加入股票数据房间
        for symbol in valid_symbols:
            room_name = f'stock_{symbol}'
            join_room(room_name)

            # 记录订阅信息
            if client_id in connected_clients:
                connected_clients[client_id]['subscriptions'].add(room_name)

        # 立即推送当前数据
        current_data = {}
        for symbol in valid_symbols:
            stock_info = stock_service.get_stock_basic_info(symbol)
            if stock_info:
                current_data[symbol] = stock_info

        emit('stock_data', {
            'type': 'current',
            'data': current_data,
            'timestamp': datetime.now().isoformat()
        })

        emit('subscription_status', {
            'status': 'subscribed',
            'symbols': valid_symbols,
            'timestamp': datetime.now().isoformat()
        })

        logger.info(f'客户端 {client_id} 订阅股票: {valid_symbols}')

    except Exception as e:
        logger.error(f'处理股票订阅失败: {e}')
        emit('error', {'message': '订阅失败，请重试'})

@socketio.on('unsubscribe_stock')
def handle_unsubscribe_stock(data):
    """取消订阅股票实时数据"""
    try:
        client_id = request.sid
        symbols = data.get('symbols', [])

        if not symbols or not isinstance(symbols, list):
            emit('error', {'message': '股票代码列表不能为空'})
            return

        # 离开股票数据房间
        unsubscribed_symbols = []
        for symbol in symbols:
            if isinstance(symbol, str) and symbol.strip():
                symbol = symbol.strip()
                room_name = f'stock_{symbol}'
                leave_room(room_name)
                unsubscribed_symbols.append(symbol)

                # 更新订阅信息
                if client_id in connected_clients:
                    connected_clients[client_id]['subscriptions'].discard(room_name)

        emit('subscription_status', {
            'status': 'unsubscribed',
            'symbols': unsubscribed_symbols,
            'timestamp': datetime.now().isoformat()
        })

        logger.info(f'客户端 {client_id} 取消订阅股票: {unsubscribed_symbols}')

    except Exception as e:
        logger.error(f'处理取消订阅失败: {e}')
        emit('error', {'message': '取消订阅失败，请重试'})

@socketio.on('subscribe_market')
def handle_subscribe_market(data):
    """订阅市场指数数据"""
    try:
        client_id = request.sid
        room_name = 'market_indices'

        # 加入市场指数房间
        join_room(room_name)

        # 记录订阅信息
        if client_id in connected_clients:
            connected_clients[client_id]['subscriptions'].add(room_name)

        # 立即推送当前市场数据
        market_data = stock_service.get_market_indices()
        emit('market_data', {
            'type': 'current',
            'data': market_data,
            'timestamp': datetime.now().isoformat()
        })

        emit('subscription_status', {
            'status': 'subscribed',
            'type': 'market',
            'timestamp': datetime.now().isoformat()
        })

        logger.info(f'客户端 {client_id} 订阅市场数据')

    except Exception as e:
        logger.error(f'处理市场数据订阅失败: {e}')
        emit('error', {'message': '订阅市场数据失败，请重试'})

@socketio.on('unsubscribe_market')
def handle_unsubscribe_market():
    """取消订阅市场指数数据"""
    try:
        client_id = request.sid
        room_name = 'market_indices'

        # 离开市场指数房间
        leave_room(room_name)

        # 更新订阅信息
        if client_id in connected_clients:
            connected_clients[client_id]['subscriptions'].discard(room_name)

        emit('subscription_status', {
            'status': 'unsubscribed',
            'type': 'market',
            'timestamp': datetime.now().isoformat()
        })

        logger.info(f'客户端 {client_id} 取消订阅市场数据')

    except Exception as e:
        logger.error(f'处理取消市场数据订阅失败: {e}')
        emit('error', {'message': '取消订阅失败，请重试'})

@socketio.on('get_client_info')
def handle_get_client_info():
    """获取客户端信息"""
    try:
        client_id = request.sid
        client_info = connected_clients.get(client_id, {})

        emit('client_info', {
            'client_id': client_id,
            'connected_at': client_info.get('connected_at'),
            'subscriptions': list(client_info.get('subscriptions', [])),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f'获取客户端信息失败: {e}')
        emit('error', {'message': '获取客户端信息失败'})

@socketio.on('ping')
def handle_ping():
    """处理ping消息（心跳检测）"""
    try:
        emit('pong', {'timestamp': datetime.now().isoformat()})
    except Exception as e:
        logger.error(f'处理ping失败: {e}')

# 后台任务：定期推送数据更新
def push_stock_updates():
    """推送股票数据更新（由后台任务调用）"""
    try:
        # 获取所有需要更新的股票代码
        subscribed_stocks = set()
        for client_info in connected_clients.values():
            for subscription in client_info['subscriptions']:
                if subscription.startswith('stock_'):
                    symbol = subscription[6:]  # 移除 'stock_' 前缀
                    subscribed_stocks.add(symbol)

        # 推送每只股票的更新数据
        for symbol in subscribed_stocks:
            stock_info = stock_service.get_stock_basic_info(symbol)
            if stock_info:
                socketio.emit('stock_data', {
                    'type': 'update',
                    'data': {symbol: stock_info},
                    'timestamp': datetime.now().isoformat()
                }, room=f'stock_{symbol}')

        logger.debug(f'推送股票数据更新，涉及股票: {len(subscribed_stocks)}只')

    except Exception as e:
        logger.error(f'推送股票数据更新失败: {e}')

def push_market_updates():
    """推送市场数据更新（由后台任务调用）"""
    try:
        # 检查是否有客户端订阅了市场数据
        has_market_subscribers = any(
            'market_indices' in client_info['subscriptions']
            for client_info in connected_clients.values()
        )

        if has_market_subscribers:
            market_data = stock_service.get_market_indices()
            socketio.emit('market_data', {
                'type': 'update',
                'data': market_data,
                'timestamp': datetime.now().isoformat()
            }, room='market_indices')

            logger.debug('推送市场数据更新')

    except Exception as e:
        logger.error(f'推送市场数据更新失败: {e}')

def get_connected_clients_count():
    """获取连接的客户端数量"""
    return len(connected_clients)

def get_subscription_stats():
    """获取订阅统计信息"""
    stats = {
        'total_clients': len(connected_clients),
        'stock_subscriptions': {},
        'market_subscribers': 0
    }

    for client_info in connected_clients.values():
        for subscription in client_info['subscriptions']:
            if subscription.startswith('stock_'):
                symbol = subscription[6:]
                stats['stock_subscriptions'][symbol] = stats['stock_subscriptions'].get(symbol, 0) + 1
            elif subscription == 'market_indices':
                stats['market_subscribers'] += 1

    return stats
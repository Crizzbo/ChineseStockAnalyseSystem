"""
测试API
"""
from flask import Blueprint
from app.utils.response import success_response

test_bp = Blueprint('test', __name__)

@test_bp.route('/ping', methods=['GET'])
def ping():
    """简单的ping测试"""
    return success_response({
        'message': 'pong',
        'status': 'ok'
    })

@test_bp.route('/mock-data', methods=['GET'])
def mock_data():
    """返回模拟数据"""
    from app.services.mock_data import get_mock_market_indices, get_mock_hot_stocks

    return success_response({
        'indices': get_mock_market_indices(),
        'hot_stocks': get_mock_hot_stocks(5)
    })
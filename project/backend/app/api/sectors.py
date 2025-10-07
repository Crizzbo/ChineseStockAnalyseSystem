"""
板块相关API路由
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.sector_data import sector_service
from app.utils.response import success_response, error_response
from app.utils.cors import add_cors_headers
# from app.utils.validators import validate_pagination
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
sectors_bp = Blueprint('sectors', __name__)

@sectors_bp.route('', methods=['GET', 'OPTIONS'])
@add_cors_headers
def get_sectors():
    """
    获取板块列表
    Query Parameters:
    - limit: 限制数量，默认100
    """
    try:
        # 获取参数
        limit = request.args.get('limit', 100, type=int)

        # 参数验证
        if limit <= 0 or limit > 200:
            return error_response("limit参数无效，应在1-200之间", 400)

        # 获取板块数据
        sectors = sector_service.get_sectors(limit=limit)

        return success_response(
            data={
                'sectors': sectors,
                'total': len(sectors),
                'timestamp': None
            },
            message="获取板块列表成功"
        )

    except Exception as e:
        logger.error(f"获取板块列表失败: {e}")
        return error_response("获取板块列表失败", 500)

@sectors_bp.route('/<string:sector_code>', methods=['GET'])
@jwt_required(optional=True)
def get_sector_info(sector_code: str):
    """
    获取板块详细信息
    Path Parameters:
    - sector_code: 板块代码或名称
    """
    try:
        if not sector_code:
            return error_response("板块代码不能为空", 400)

        # 获取板块信息
        sector_info = sector_service.get_sector_info(sector_code)

        if not sector_info:
            return error_response("未找到指定板块", 404)

        return success_response(
            data={
                'sector': sector_info,
                'timestamp': None
            },
            message="获取板块信息成功"
        )

    except Exception as e:
        logger.error(f"获取板块信息失败 {sector_code}: {e}")
        return error_response("获取板块信息失败", 500)

@sectors_bp.route('/<string:sector_code>/stocks', methods=['GET'])
@jwt_required(optional=True)
def get_sector_stocks(sector_code: str):
    """
    获取板块成分股
    Path Parameters:
    - sector_code: 板块代码或名称
    """
    try:
        if not sector_code:
            return error_response("板块代码不能为空", 400)

        # 获取成分股数据
        stocks = sector_service.get_sector_stocks(sector_code)

        return success_response(
            data={
                'sector_code': sector_code,
                'stocks': stocks,
                'total': len(stocks),
                'timestamp': None
            },
            message="获取板块成分股成功"
        )

    except Exception as e:
        logger.error(f"获取板块成分股失败 {sector_code}: {e}")
        return error_response("获取板块成分股失败", 500)

@sectors_bp.route('/hot', methods=['GET'])
@jwt_required(optional=True)
def get_hot_sectors():
    """
    获取热门板块
    Query Parameters:
    - limit: 限制数量，默认20
    """
    try:
        # 获取参数
        limit = request.args.get('limit', 20, type=int)

        # 参数验证
        if limit <= 0 or limit > 100:
            return error_response("limit参数无效，应在1-100之间", 400)

        # 获取热门板块
        hot_sectors = sector_service.get_hot_sectors(limit=limit)

        return success_response(
            data={
                'sectors': hot_sectors,
                'total': len(hot_sectors),
                'timestamp': None
            },
            message="获取热门板块成功"
        )

    except Exception as e:
        logger.error(f"获取热门板块失败: {e}")
        return error_response("获取热门板块失败", 500)

@sectors_bp.route('/search', methods=['GET'])
@jwt_required(optional=True)
def search_sectors():
    """
    搜索板块
    Query Parameters:
    - keyword: 搜索关键词
    - limit: 限制数量，默认10
    """
    try:
        # 获取参数
        keyword = request.args.get('keyword', '').strip()
        limit = request.args.get('limit', 10, type=int)

        # 参数验证
        if not keyword:
            return error_response("搜索关键词不能为空", 400)

        if limit <= 0 or limit > 50:
            return error_response("limit参数无效，应在1-50之间", 400)

        # 搜索板块
        sectors = sector_service.search_sectors(keyword, limit=limit)

        return success_response(
            data={
                'sectors': sectors,
                'total': len(sectors),
                'keyword': keyword,
                'timestamp': None
            },
            message="搜索板块成功"
        )

    except Exception as e:
        logger.error(f"搜索板块失败: {e}")
        return error_response("搜索板块失败", 500)

@sectors_bp.route('/ranking', methods=['GET'])
@jwt_required(optional=True)
def get_sector_ranking():
    """
    获取板块排行榜
    Query Parameters:
    - sort_by: 排序字段 (changePercent, change, volume, turnover, stockCount)，默认changePercent
    - order: 排序顺序 (asc, desc)，默认desc
    - limit: 限制数量，默认50
    """
    try:
        # 获取参数
        sort_by = request.args.get('sort_by', 'changePercent')
        order = request.args.get('order', 'desc')
        limit = request.args.get('limit', 50, type=int)

        # 参数验证
        valid_sort_fields = ['changePercent', 'change', 'volume', 'turnover', 'stockCount']
        if sort_by not in valid_sort_fields:
            return error_response(f"sort_by参数无效，支持: {', '.join(valid_sort_fields)}", 400)

        if order not in ['asc', 'desc']:
            return error_response("order参数无效，支持: asc, desc", 400)

        if limit <= 0 or limit > 100:
            return error_response("limit参数无效，应在1-100之间", 400)

        # 获取排行榜数据
        ranked_sectors = sector_service.get_sector_ranking(
            sort_by=sort_by,
            order=order,
            limit=limit
        )

        return success_response(
            data={
                'sectors': ranked_sectors,
                'total': len(ranked_sectors),
                'sort_by': sort_by,
                'order': order,
                'timestamp': None
            },
            message="获取板块排行榜成功"
        )

    except Exception as e:
        logger.error(f"获取板块排行榜失败: {e}")
        return error_response("获取板块排行榜失败", 500)

@sectors_bp.route('/<string:sector_code>/analysis', methods=['GET'])
@jwt_required(optional=True)
def get_sector_analysis(sector_code: str):
    """
    获取板块分析（暂时返回基础信息）
    Path Parameters:
    - sector_code: 板块代码或名称
    """
    try:
        if not sector_code:
            return error_response("板块代码不能为空", 400)

        # 获取板块基础信息
        sector_info = sector_service.get_sector_info(sector_code)

        if not sector_info:
            return error_response("未找到指定板块", 404)

        # 构建简单分析数据
        change_percent = sector_info.get('changePercent', 0)

        # 根据涨跌幅判断趋势
        if change_percent > 3:
            trend = 'bullish'
        elif change_percent < -3:
            trend = 'bearish'
        else:
            trend = 'neutral'

        # 根据涨跌幅判断风险等级
        if abs(change_percent) > 5:
            risk_level = 'high'
        elif abs(change_percent) > 2:
            risk_level = 'medium'
        else:
            risk_level = 'low'

        analysis = {
            'sector_code': sector_code,
            'sector_name': sector_info.get('name', ''),
            'trend_analysis': {
                'short_term': trend,
                'medium_term': 'neutral',  # 需要更多历史数据
                'long_term': 'neutral'     # 需要更多历史数据
            },
            'performance': {
                'today': change_percent,
                'week': 0,    # 需要历史数据
                'month': 0,   # 需要历史数据
                'quarter': 0, # 需要历史数据
                'year': 0     # 需要历史数据
            },
            'risk_level': risk_level,
            'recommendation': f"当前板块涨跌幅为{change_percent:.2f}%，建议根据个人风险承受能力谨慎投资。"
        }

        return success_response(
            data={
                'analysis': analysis,
                'timestamp': None
            },
            message="获取板块分析成功"
        )

    except Exception as e:
        logger.error(f"获取板块分析失败 {sector_code}: {e}")
        return error_response("获取板块分析失败", 500)
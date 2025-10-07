"""
股票数据API
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from datetime import datetime, timedelta

from app.services.stock_data import stock_service
from app.utils.response import success_response, error_response, paginated_response

stocks_bp = Blueprint('stocks', __name__)

# 请求验证模式
class StockSearchSchema(Schema):
    keyword = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    limit = fields.Int(load_default=10, validate=lambda x: 1 <= x <= 50)

class StockHistorySchema(Schema):
    symbol = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    period = fields.Str(load_default="daily", validate=lambda x: x in ["daily", "weekly", "monthly"])
    start_date = fields.Str(load_default=None)
    end_date = fields.Str(load_default=None)
    limit = fields.Int(load_default=250, validate=lambda x: 1 <= x <= 1000)

class StockListSchema(Schema):
    page = fields.Int(load_default=1, validate=lambda x: x >= 1)
    per_page = fields.Int(load_default=20, validate=lambda x: 1 <= x <= 100)
    market = fields.Str(load_default=None, validate=lambda x: x in ["sh", "sz", "all"] if x else True)
    sector = fields.Str(load_default=None)

@stocks_bp.route('/search', methods=['GET'])
def search_stocks():
    """搜索股票"""
    try:
        # 验证请求参数
        schema = StockSearchSchema()
        args = schema.load(request.args)

        # 调用股票数据服务
        results = stock_service.search_stocks(
            keyword=args['keyword'].strip(),
            limit=args['limit']
        )

        return success_response({
            'stocks': results,
            'total': len(results),
            'keyword': args['keyword']
        })

    except ValidationError as e:
        return error_response(f'参数验证失败: {e.messages}', 400)
    except Exception as e:
        current_app.logger.error(f'搜索股票失败: {str(e)}')
        return error_response('搜索失败，请稍后重试', 500)

@stocks_bp.route('/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    """获取股票基本信息"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()
        stock_info = stock_service.get_stock_basic_info(symbol)

        if not stock_info:
            return error_response('股票不存在或数据获取失败', 404)

        return success_response({'stock': stock_info})

    except Exception as e:
        current_app.logger.error(f'获取股票信息失败 {symbol}: {str(e)}')
        return error_response('获取股票信息失败', 500)

@stocks_bp.route('/<symbol>/history', methods=['GET'])
def get_stock_history(symbol):
    """获取股票历史数据"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        # 验证请求参数
        schema = StockHistorySchema()
        args = dict(request.args)
        args['symbol'] = symbol.strip()
        data = schema.load(args)

        # 调用股票数据服务
        history_data = stock_service.get_stock_price_history(
            symbol=data['symbol'],
            period=data['period'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            limit=data['limit']
        )

        if not history_data:
            return error_response('暂无历史数据', 404)

        return success_response({
            'symbol': data['symbol'],
            'period': data['period'],
            'data': history_data,
            'total': len(history_data)
        })

    except ValidationError as e:
        return error_response(f'参数验证失败: {e.messages}', 400)
    except Exception as e:
        current_app.logger.error(f'获取股票历史数据失败 {symbol}: {str(e)}')
        return error_response('获取历史数据失败', 500)

@stocks_bp.route('/<symbol>/technical', methods=['GET'])
def get_stock_technical_indicators(symbol):
    """获取股票技术指标"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()
        period = request.args.get('period', 'daily')

        if period not in ['daily', 'weekly', 'monthly']:
            return error_response('时间周期参数错误', 400)

        # 获取技术指标
        indicators = stock_service.get_stock_technical_indicators(symbol, period)

        if not indicators:
            return error_response('暂无技术指标数据', 404)

        return success_response({
            'symbol': symbol,
            'period': period,
            'indicators': indicators
        })

    except Exception as e:
        current_app.logger.error(f'获取技术指标失败 {symbol}: {str(e)}')
        return error_response('获取技术指标失败', 500)

@stocks_bp.route('/hot', methods=['GET'])
def get_hot_stocks():
    """获取热门股票"""
    try:
        limit = request.args.get('limit', 20, type=int)

        if limit < 1 or limit > 100:
            return error_response('数量限制必须在1-100之间', 400)

        hot_stocks = stock_service.get_hot_stocks(limit)

        return success_response({
            'stocks': hot_stocks,
            'total': len(hot_stocks)
        })

    except Exception as e:
        current_app.logger.error(f'获取热门股票失败: {str(e)}')
        return error_response('获取热门股票失败', 500)

@stocks_bp.route('/batch', methods=['POST'])
def get_batch_stock_info():
    """批量获取股票信息"""
    try:
        data = request.json
        if not data or 'symbols' not in data:
            return error_response('请提供股票代码列表', 400)

        symbols = data.get('symbols', [])
        if not isinstance(symbols, list):
            return error_response('股票代码必须是数组格式', 400)

        if len(symbols) == 0:
            return error_response('股票代码列表不能为空', 400)

        if len(symbols) > 50:
            return error_response('最多支持50只股票的批量查询', 400)

        # 批量获取股票信息
        results = []
        failed_symbols = []

        for symbol in symbols:
            if not symbol or len(symbol.strip()) == 0:
                continue

            symbol = symbol.strip()
            stock_info = stock_service.get_stock_basic_info(symbol)

            if stock_info:
                results.append(stock_info)
            else:
                failed_symbols.append(symbol)

        return success_response({
            'stocks': results,
            'total': len(results),
            'failed_symbols': failed_symbols,
            'success_count': len(results),
            'failed_count': len(failed_symbols)
        })

    except Exception as e:
        current_app.logger.error(f'批量获取股票信息失败: {str(e)}')
        return error_response('批量获取股票信息失败', 500)

@stocks_bp.route('/realtime/<symbols>', methods=['GET'])
def get_realtime_quotes(symbols):
    """获取实时行情（支持多个股票代码，用逗号分隔）"""
    try:
        if not symbols or len(symbols.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol_list = [s.strip() for s in symbols.split(',') if s.strip()]

        if len(symbol_list) == 0:
            return error_response('股票代码格式错误', 400)

        if len(symbol_list) > 20:
            return error_response('最多支持20只股票的实时行情查询', 400)

        # 获取实时行情
        results = []
        for symbol in symbol_list:
            stock_info = stock_service.get_stock_basic_info(symbol)
            if stock_info:
                results.append(stock_info)

        return success_response({
            'quotes': results,
            'total': len(results),
            'requested_symbols': symbol_list,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'获取实时行情失败 {symbols}: {str(e)}')
        return error_response('获取实时行情失败', 500)

@stocks_bp.route('/compare', methods=['POST'])
def compare_stocks():
    """股票对比分析"""
    try:
        data = request.json
        if not data or 'symbols' not in data:
            return error_response('请提供股票代码列表', 400)

        symbols = data.get('symbols', [])
        if not isinstance(symbols, list) or len(symbols) < 2:
            return error_response('至少需要2只股票进行对比', 400)

        if len(symbols) > 5:
            return error_response('最多支持5只股票的对比', 400)

        # 获取股票基本信息和技术指标
        comparison_data = []
        for symbol in symbols:
            if not symbol or len(symbol.strip()) == 0:
                continue

            symbol = symbol.strip()

            # 获取基本信息
            stock_info = stock_service.get_stock_basic_info(symbol)
            if not stock_info:
                continue

            # 获取技术指标
            indicators = stock_service.get_stock_technical_indicators(symbol)

            # 合并数据
            stock_data = {**stock_info, 'technical_indicators': indicators}
            comparison_data.append(stock_data)

        if len(comparison_data) < 2:
            return error_response('对比股票数据不足', 400)

        return success_response({
            'comparison': comparison_data,
            'total': len(comparison_data),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'股票对比失败: {str(e)}')
        return error_response('股票对比失败', 500)
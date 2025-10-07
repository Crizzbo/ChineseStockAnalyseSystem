"""
投资组合API
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from datetime import datetime

from app import db
from app.models.portfolio import Portfolio, PortfolioStock
from app.models.watchlist import WatchList, WatchListStock
from app.services.stock_data import stock_service
from app.utils.response import success_response, error_response

portfolio_bp = Blueprint('portfolio', __name__)

# 请求验证模式
class CreatePortfolioSchema(Schema):
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0 and len(x.strip()) <= 100)
    description = fields.Str(load_default=None, validate=lambda x: len(x) <= 500 if x else True)

class UpdatePortfolioSchema(Schema):
    name = fields.Str(load_default=None, validate=lambda x: len(x.strip()) > 0 and len(x.strip()) <= 100 if x else True)
    description = fields.Str(load_default=None, validate=lambda x: len(x) <= 500 if x else True)

class AddStockSchema(Schema):
    symbol = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    shares = fields.Int(required=True, validate=lambda x: x > 0)
    avg_cost = fields.Float(required=True, validate=lambda x: x > 0)

class UpdateStockSchema(Schema):
    shares = fields.Int(load_default=None, validate=lambda x: x > 0 if x is not None else True)
    avg_cost = fields.Float(load_default=None, validate=lambda x: x > 0 if x is not None else True)

class CreateWatchListSchema(Schema):
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0 and len(x.strip()) <= 100)
    description = fields.Str(load_default=None, validate=lambda x: len(x) <= 500 if x else True)

class AddWatchStockSchema(Schema):
    symbol = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    name = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    notes = fields.Str(load_default=None, validate=lambda x: len(x) <= 500 if x else True)

# ==================== 投资组合管理 ====================

@portfolio_bp.route('/', methods=['GET'])
@jwt_required()
def get_portfolios():
    """获取用户的投资组合列表"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        # 查询用户的投资组合
        portfolios_query = Portfolio.query.filter_by(user_id=current_user_id)
        portfolios_pagination = portfolios_query.paginate(
            page=page, per_page=per_page, error_out=False
        )

        # 获取当前股价用于计算
        stock_prices = {}
        for portfolio in portfolios_pagination.items:
            for stock in portfolio.stocks:
                if stock.symbol not in stock_prices:
                    stock_info = stock_service.get_stock_basic_info(stock.symbol)
                    if stock_info:
                        stock_prices[stock.symbol] = stock_info['currentPrice']

        # 转换为字典格式
        portfolios_data = [portfolio.to_dict(stock_prices=stock_prices)
                          for portfolio in portfolios_pagination.items]

        # 返回适配前端的格式
        return success_response({
            'data': portfolios_data,
            'total': portfolios_pagination.total,
            'page': page,
            'per_page': per_page
        }, message="获取投资组合成功")

    except Exception as e:
        current_app.logger.error(f'获取投资组合失败: {str(e)}')
        return error_response('获取投资组合失败', 500)

@portfolio_bp.route('/', methods=['POST'])
@jwt_required()
def create_portfolio():
    """创建新的投资组合"""
    try:
        current_user_id = get_jwt_identity()

        # 验证请求数据
        schema = CreatePortfolioSchema()
        data = schema.load(request.json)

        # 检查是否已存在同名投资组合
        existing = Portfolio.query.filter_by(
            user_id=current_user_id,
            name=data['name']
        ).first()

        if existing:
            return error_response('已存在同名的投资组合', 409)

        # 创建新投资组合
        portfolio = Portfolio(
            name=data['name'],
            user_id=current_user_id,
            description=data.get('description')
        )

        db.session.add(portfolio)
        db.session.commit()

        return success_response({
            'message': '投资组合创建成功',
            'portfolio': portfolio.to_dict()
        }, 201)

    except ValidationError as e:
        return error_response(f'数据验证失败: {e.messages}', 400)
    except Exception as e:
        current_app.logger.error(f'创建投资组合失败: {str(e)}')
        return error_response('创建投资组合失败', 500)

@portfolio_bp.route('/<int:portfolio_id>', methods=['GET'])
@jwt_required()
def get_portfolio(portfolio_id):
    """获取指定投资组合详情"""
    try:
        current_user_id = get_jwt_identity()

        portfolio = Portfolio.query.filter_by(
            id=portfolio_id,
            user_id=current_user_id
        ).first()

        if not portfolio:
            return error_response('投资组合不存在', 404)

        # 获取当前股价
        stock_prices = {}
        for stock in portfolio.stocks:
            stock_info = stock_service.get_stock_basic_info(stock.symbol)
            if stock_info:
                stock_prices[stock.symbol] = stock_info['currentPrice']

        return success_response({
            'portfolio': portfolio.to_dict(stock_prices=stock_prices)
        })

    except Exception as e:
        current_app.logger.error(f'获取投资组合详情失败: {str(e)}')
        return error_response('获取投资组合详情失败', 500)

@portfolio_bp.route('/<int:portfolio_id>', methods=['PUT'])
@jwt_required()
def update_portfolio(portfolio_id):
    """更新投资组合信息"""
    try:
        current_user_id = get_jwt_identity()

        portfolio = Portfolio.query.filter_by(
            id=portfolio_id,
            user_id=current_user_id
        ).first()

        if not portfolio:
            return error_response('投资组合不存在', 404)

        # 验证请求数据
        schema = UpdatePortfolioSchema()
        data = schema.load(request.json)

        # 检查是否存在同名投资组合（排除当前组合）
        if 'name' in data and data['name']:
            existing = Portfolio.query.filter(
                Portfolio.user_id == current_user_id,
                Portfolio.name == data['name'],
                Portfolio.id != portfolio_id
            ).first()

            if existing:
                return error_response('已存在同名的投资组合', 409)

            portfolio.name = data['name']

        if 'description' in data:
            portfolio.description = data['description']

        db.session.commit()

        return success_response({
            'message': '投资组合更新成功',
            'portfolio': portfolio.to_dict()
        })

    except ValidationError as e:
        return error_response(f'数据验证失败: {e.messages}', 400)
    except Exception as e:
        current_app.logger.error(f'更新投资组合失败: {str(e)}')
        return error_response('更新投资组合失败', 500)

@portfolio_bp.route('/<int:portfolio_id>', methods=['DELETE'])
@jwt_required()
def delete_portfolio(portfolio_id):
    """删除投资组合"""
    try:
        current_user_id = get_jwt_identity()

        portfolio = Portfolio.query.filter_by(
            id=portfolio_id,
            user_id=current_user_id
        ).first()

        if not portfolio:
            return error_response('投资组合不存在', 404)

        db.session.delete(portfolio)
        db.session.commit()

        return success_response({'message': '投资组合删除成功'})

    except Exception as e:
        current_app.logger.error(f'删除投资组合失败: {str(e)}')
        return error_response('删除投资组合失败', 500)

# ==================== 投资组合股票管理 ====================

@portfolio_bp.route('/<int:portfolio_id>/stocks', methods=['POST'])
@jwt_required()
def add_stock_to_portfolio(portfolio_id):
    """向投资组合添加股票"""
    try:
        current_user_id = get_jwt_identity()

        # 验证投资组合存在
        portfolio = Portfolio.query.filter_by(
            id=portfolio_id,
            user_id=current_user_id
        ).first()

        if not portfolio:
            return error_response('投资组合不存在', 404)

        # 验证请求数据
        schema = AddStockSchema()
        data = schema.load(request.json)

        # 验证股票是否存在
        stock_info = stock_service.get_stock_basic_info(data['symbol'])
        if not stock_info:
            return error_response('股票代码不存在', 400)

        # 检查是否已添加该股票
        existing_stock = PortfolioStock.query.filter_by(
            portfolio_id=portfolio_id,
            symbol=data['symbol']
        ).first()

        if existing_stock:
            return error_response('该股票已在投资组合中', 409)

        # 创建新的持仓记录
        portfolio_stock = PortfolioStock(
            portfolio_id=portfolio_id,
            symbol=data['symbol'],
            name=data['name'],
            shares=data['shares'],
            avg_cost=data['avg_cost']
        )

        db.session.add(portfolio_stock)
        db.session.commit()

        return success_response({
            'message': '股票添加成功',
            'stock': portfolio_stock.to_dict({data['symbol']: stock_info['currentPrice']})
        }, 201)

    except ValidationError as e:
        return error_response(f'数据验证失败: {e.messages}', 400)
    except Exception as e:
        current_app.logger.error(f'添加股票到投资组合失败: {str(e)}')
        return error_response('添加股票失败', 500)

@portfolio_bp.route('/<int:portfolio_id>/stocks/<int:stock_id>', methods=['PUT'])
@jwt_required()
def update_portfolio_stock(portfolio_id, stock_id):
    """更新投资组合中的股票信息"""
    try:
        current_user_id = get_jwt_identity()

        # 验证投资组合和股票存在
        portfolio = Portfolio.query.filter_by(
            id=portfolio_id,
            user_id=current_user_id
        ).first()

        if not portfolio:
            return error_response('投资组合不存在', 404)

        stock = PortfolioStock.query.filter_by(
            id=stock_id,
            portfolio_id=portfolio_id
        ).first()

        if not stock:
            return error_response('股票不存在', 404)

        # 验证请求数据
        schema = UpdateStockSchema()
        data = schema.load(request.json)

        # 更新股票信息
        if 'shares' in data and data['shares'] is not None:
            stock.shares = data['shares']
        if 'avg_cost' in data and data['avg_cost'] is not None:
            stock.avg_cost = data['avg_cost']

        db.session.commit()

        # 获取当前股价
        stock_info = stock_service.get_stock_basic_info(stock.symbol)
        current_price = stock_info['currentPrice'] if stock_info else stock.avg_cost

        return success_response({
            'message': '股票信息更新成功',
            'stock': stock.to_dict({stock.symbol: current_price})
        })

    except ValidationError as e:
        return error_response(f'数据验证失败: {e.messages}', 400)
    except Exception as e:
        current_app.logger.error(f'更新投资组合股票失败: {str(e)}')
        return error_response('更新股票信息失败', 500)

@portfolio_bp.route('/<int:portfolio_id>/stocks/<int:stock_id>', methods=['DELETE'])
@jwt_required()
def remove_stock_from_portfolio(portfolio_id, stock_id):
    """从投资组合中删除股票"""
    try:
        current_user_id = get_jwt_identity()

        # 验证投资组合和股票存在
        portfolio = Portfolio.query.filter_by(
            id=portfolio_id,
            user_id=current_user_id
        ).first()

        if not portfolio:
            return error_response('投资组合不存在', 404)

        stock = PortfolioStock.query.filter_by(
            id=stock_id,
            portfolio_id=portfolio_id
        ).first()

        if not stock:
            return error_response('股票不存在', 404)

        db.session.delete(stock)
        db.session.commit()

        return success_response({'message': '股票删除成功'})

    except Exception as e:
        current_app.logger.error(f'删除投资组合股票失败: {str(e)}')
        return error_response('删除股票失败', 500)

# ==================== 自选股管理 ====================

@portfolio_bp.route('/watchlists', methods=['GET'])
@jwt_required()
def get_watchlists():
    """获取用户的自选股列表"""
    try:
        current_user_id = get_jwt_identity()

        watchlists = WatchList.query.filter_by(user_id=current_user_id).all()
        watchlists_data = [watchlist.to_dict() for watchlist in watchlists]

        return success_response({
            'watchlists': watchlists_data,
            'total': len(watchlists_data)
        })

    except Exception as e:
        current_app.logger.error(f'获取自选股列表失败: {str(e)}')
        return error_response('获取自选股列表失败', 500)

@portfolio_bp.route('/watchlists', methods=['POST'])
@jwt_required()
def create_watchlist():
    """创建新的自选股列表"""
    try:
        current_user_id = get_jwt_identity()

        # 验证请求数据
        schema = CreateWatchListSchema()
        data = schema.load(request.json)

        # 检查是否已存在同名自选股列表
        existing = WatchList.query.filter_by(
            user_id=current_user_id,
            name=data['name']
        ).first()

        if existing:
            return error_response('已存在同名的自选股列表', 409)

        # 创建新自选股列表
        watchlist = WatchList(
            name=data['name'],
            user_id=current_user_id,
            description=data.get('description')
        )

        db.session.add(watchlist)
        db.session.commit()

        return success_response({
            'message': '自选股列表创建成功',
            'watchlist': watchlist.to_dict()
        }, 201)

    except ValidationError as e:
        return error_response(f'数据验证失败: {e.messages}', 400)
    except Exception as e:
        current_app.logger.error(f'创建自选股列表失败: {str(e)}')
        return error_response('创建自选股列表失败', 500)

@portfolio_bp.route('/watchlists/<int:watchlist_id>/stocks', methods=['POST'])
@jwt_required()
def add_stock_to_watchlist(watchlist_id):
    """向自选股列表添加股票"""
    try:
        current_user_id = get_jwt_identity()

        # 验证自选股列表存在
        watchlist = WatchList.query.filter_by(
            id=watchlist_id,
            user_id=current_user_id
        ).first()

        if not watchlist:
            return error_response('自选股列表不存在', 404)

        # 验证请求数据
        schema = AddWatchStockSchema()
        data = schema.load(request.json)

        # 验证股票是否存在
        stock_info = stock_service.get_stock_basic_info(data['symbol'])
        if not stock_info:
            return error_response('股票代码不存在', 400)

        # 检查是否已添加该股票
        existing_stock = WatchListStock.query.filter_by(
            watchlist_id=watchlist_id,
            symbol=data['symbol']
        ).first()

        if existing_stock:
            return error_response('该股票已在自选股列表中', 409)

        # 创建新的自选股记录
        watchlist_stock = WatchListStock(
            watchlist_id=watchlist_id,
            symbol=data['symbol'],
            name=data['name'],
            added_price=stock_info['currentPrice'],
            notes=data.get('notes')
        )

        db.session.add(watchlist_stock)
        db.session.commit()

        return success_response({
            'message': '股票添加成功',
            'stock': watchlist_stock.to_dict()
        }, 201)

    except ValidationError as e:
        return error_response(f'数据验证失败: {e.messages}', 400)
    except Exception as e:
        current_app.logger.error(f'添加股票到自选股失败: {str(e)}')
        return error_response('添加股票失败', 500)

@portfolio_bp.route('/watchlists/<int:watchlist_id>/stocks/<int:stock_id>', methods=['DELETE'])
@jwt_required()
def remove_stock_from_watchlist(watchlist_id, stock_id):
    """从自选股列表中删除股票"""
    try:
        current_user_id = get_jwt_identity()

        # 验证自选股列表和股票存在
        watchlist = WatchList.query.filter_by(
            id=watchlist_id,
            user_id=current_user_id
        ).first()

        if not watchlist:
            return error_response('自选股列表不存在', 404)

        stock = WatchListStock.query.filter_by(
            id=stock_id,
            watchlist_id=watchlist_id
        ).first()

        if not stock:
            return error_response('股票不存在', 404)

        db.session.delete(stock)
        db.session.commit()

        return success_response({'message': '股票删除成功'})

    except Exception as e:
        current_app.logger.error(f'删除自选股股票失败: {str(e)}')
        return error_response('删除股票失败', 500)
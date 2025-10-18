"""
股票基本面分析API
"""
from flask import Blueprint, request, jsonify, current_app
from marshmallow import Schema, fields, ValidationError
from datetime import datetime

from app.services.fundamental_analysis import fundamental_service
from app.utils.response import success_response, error_response

fundamental_bp = Blueprint('fundamental', __name__)

# 请求验证模式
class FundamentalAnalysisSchema(Schema):
    symbol = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)

@fundamental_bp.route('/<symbol>', methods=['GET'])
def get_fundamental_analysis(symbol):
    """获取股票基本面分析"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()

        # 获取基本面分析数据
        analysis_result = fundamental_service.get_fundamental_analysis(symbol)

        if not analysis_result:
            return error_response('无法获取基本面数据,可能原因: 1) 股票代码不正确(需6位数字,如000001) 2) 数据源暂时不可用 3) 网络连接问题,请稍后重试', 404)

        return success_response(analysis_result)

    except Exception as e:
        current_app.logger.error(f'获取基本面分析失败 {symbol}: {str(e)}')
        # 如果是连接错误,返回更友好的提示
        if 'Connection' in str(e) or 'aborted' in str(e):
            return error_response('数据源连接失败,请稍后重试', 503)
        return error_response(f'获取基本面分析失败,请检查股票代码是否正确(需6位数字)', 500)

@fundamental_bp.route('/<symbol>/financial-indicators', methods=['GET'])
def get_financial_indicators(symbol):
    """获取财务指标"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()

        # 获取财务指标数据
        indicators = fundamental_service.get_financial_indicators(symbol)

        if not indicators:
            return error_response('无法获取财务指标', 404)

        return success_response({
            'symbol': symbol,
            'indicators': indicators,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'获取财务指标失败 {symbol}: {str(e)}')
        return error_response(f'获取财务指标失败: {str(e)}', 500)

@fundamental_bp.route('/<symbol>/profitability', methods=['GET'])
def get_profitability_analysis(symbol):
    """获取盈利能力分析"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()

        # 获取盈利能力分析
        profitability = fundamental_service.get_profitability_analysis(symbol)

        if not profitability:
            return error_response('无法获取盈利能力数据', 404)

        return success_response({
            'symbol': symbol,
            'profitability': profitability,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'获取盈利能力分析失败 {symbol}: {str(e)}')
        return error_response(f'获取盈利能力分析失败: {str(e)}', 500)

@fundamental_bp.route('/<symbol>/solvency', methods=['GET'])
def get_solvency_analysis(symbol):
    """获取偿债能力分析"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()

        # 获取偿债能力分析
        solvency = fundamental_service.get_solvency_analysis(symbol)

        if not solvency:
            return error_response('无法获取偿债能力数据', 404)

        return success_response({
            'symbol': symbol,
            'solvency': solvency,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'获取偿债能力分析失败 {symbol}: {str(e)}')
        return error_response(f'获取偿债能力分析失败: {str(e)}', 500)

@fundamental_bp.route('/<symbol>/growth', methods=['GET'])
def get_growth_analysis(symbol):
    """获取成长性分析"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()

        # 获取成长性分析
        growth = fundamental_service.get_growth_analysis(symbol)

        if not growth:
            return error_response('无法获取成长性数据', 404)

        return success_response({
            'symbol': symbol,
            'growth': growth,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'获取成长性分析失败 {symbol}: {str(e)}')
        return error_response(f'获取成长性分析失败: {str(e)}', 500)

@fundamental_bp.route('/<symbol>/valuation', methods=['GET'])
def get_valuation_analysis(symbol):
    """获取估值分析"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()

        # 获取估值分析
        valuation = fundamental_service.get_valuation_analysis(symbol)

        if not valuation:
            return error_response('无法获取估值数据', 404)

        return success_response({
            'symbol': symbol,
            'valuation': valuation,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'获取估值分析失败 {symbol}: {str(e)}')
        return error_response(f'获取估值分析失败: {str(e)}', 500)

@fundamental_bp.route('/<symbol>/score', methods=['GET'])
def get_fundamental_score(symbol):
    """获取基本面综合评分"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()

        # 获取基本面评分
        score_result = fundamental_service.calculate_fundamental_score(symbol)

        if not score_result:
            return error_response('无法计算基本面评分', 404)

        return success_response({
            'symbol': symbol,
            'score': score_result,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'计算基本面评分失败 {symbol}: {str(e)}')
        return error_response(f'计算基本面评分失败: {str(e)}', 500)

@fundamental_bp.route('/<symbol>/recommendation', methods=['GET'])
def get_investment_recommendation(symbol):
    """获取投资建议"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()

        # 获取投资建议
        recommendation = fundamental_service.get_investment_recommendation(symbol)

        if not recommendation:
            return error_response('无法生成投资建议', 404)

        return success_response({
            'symbol': symbol,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'生成投资建议失败 {symbol}: {str(e)}')
        return error_response(f'生成投资建议失败: {str(e)}', 500)

@fundamental_bp.route('/<symbol>/financial-statements', methods=['GET'])
def get_financial_statements(symbol):
    """获取三大财务报表数据"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()

        # 获取报表类型参数,默认为资产负债表
        statement_type = request.args.get('type', 'balance')  # balance, profit, cashflow

        # 获取分组参数（period/year/quarter），默认为 period（按报告期）
        group = request.args.get('group', 'period')

        # 获取财务报表数据（支持后端聚合）
        statements = fundamental_service.get_financial_statements(symbol, statement_type, group)

        if not statements:
            return error_response(f'无法获取{statement_type}财务报表数据', 404)

        return success_response({
            'symbol': symbol,
            'type': statement_type,
            'statements': statements,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'获取财务报表失败 {symbol}: {str(e)}')
        if 'Connection' in str(e) or 'aborted' in str(e):
            return error_response('数据源连接失败,请稍后重试', 503)
        return error_response(f'获取财务报表失败: {str(e)}', 500)

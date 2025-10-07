"""
股票分析API
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from datetime import datetime, timedelta
try:
    import pandas as pd
except ImportError:
    pd = None

from app.services.stock_data import stock_service
from app.utils.response import success_response, error_response

analysis_bp = Blueprint('analysis', __name__)

# 请求验证模式
class TechnicalAnalysisSchema(Schema):
    symbol = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    period = fields.Str(load_default="daily", validate=lambda x: x in ["daily", "weekly", "monthly"])
    indicators = fields.List(fields.Str(), load_default=None)

class FundamentalAnalysisSchema(Schema):
    symbol = fields.Str(required=True, validate=lambda x: len(x.strip()) > 0)
    year = fields.Int(load_default=None, validate=lambda x: x >= 2000 if x else True)

@analysis_bp.route('/technical/<symbol>', methods=['GET'])
def get_technical_analysis(symbol):
    """获取技术分析"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()
        period = request.args.get('period', 'daily')

        if period not in ['daily', 'weekly', 'monthly']:
            return error_response('时间周期参数错误', 400)

        # 获取股票基本信息
        stock_info = stock_service.get_stock_basic_info(symbol)
        if not stock_info:
            return error_response('股票不存在', 404)

        # 获取历史数据
        history_data = stock_service.get_stock_price_history(symbol, period, limit=100)
        if not history_data:
            return error_response('暂无历史数据', 404)

        # 获取技术指标
        technical_indicators = stock_service.get_stock_technical_indicators(symbol, period)

        # 生成技术分析建议
        analysis_result = generate_technical_analysis(stock_info, history_data, technical_indicators)

        return success_response({
            'symbol': symbol,
            'period': period,
            'stock_info': stock_info,
            'technical_indicators': technical_indicators,
            'analysis': analysis_result,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'技术分析失败 {symbol}: {str(e)}')
        return error_response('技术分析失败', 500)

@analysis_bp.route('/fundamental/<symbol>', methods=['GET'])
def get_fundamental_analysis(symbol):
    """获取基本面分析"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()

        # 获取股票基本信息
        stock_info = stock_service.get_stock_basic_info(symbol)
        if not stock_info:
            return error_response('股票不存在', 404)

        # 生成基本面分析（使用现有数据）
        fundamental_analysis = generate_fundamental_analysis(stock_info)

        return success_response({
            'symbol': symbol,
            'stock_info': stock_info,
            'analysis': fundamental_analysis,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'基本面分析失败 {symbol}: {str(e)}')
        return error_response('基本面分析失败', 500)

@analysis_bp.route('/trend/<symbol>', methods=['GET'])
def get_trend_analysis(symbol):
    """获取趋势分析"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()
        days = request.args.get('days', 30, type=int)

        if days < 5 or days > 365:
            return error_response('天数范围必须在5-365之间', 400)

        # 获取历史数据
        history_data = stock_service.get_stock_price_history(symbol, limit=days + 50)
        if not history_data:
            return error_response('暂无历史数据', 404)

        # 生成趋势分析
        trend_analysis = generate_trend_analysis(history_data, days)

        return success_response({
            'symbol': symbol,
            'days': days,
            'analysis': trend_analysis,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'趋势分析失败 {symbol}: {str(e)}')
        return error_response('趋势分析失败', 500)

@analysis_bp.route('/correlation', methods=['POST'])
def get_correlation_analysis():
    """获取相关性分析"""
    try:
        data = request.json
        if not data or 'symbols' not in data:
            return error_response('请提供股票代码列表', 400)

        symbols = data.get('symbols', [])
        if not isinstance(symbols, list) or len(symbols) < 2:
            return error_response('至少需要2只股票进行相关性分析', 400)

        if len(symbols) > 10:
            return error_response('最多支持10只股票的相关性分析', 400)

        days = data.get('days', 60)
        if days < 10 or days > 250:
            return error_response('分析天数必须在10-250之间', 400)

        # 获取所有股票的历史数据
        stocks_data = {}
        for symbol in symbols:
            if not symbol or len(symbol.strip()) == 0:
                continue

            symbol = symbol.strip()
            history = stock_service.get_stock_price_history(symbol, limit=days + 10)
            if history:
                stocks_data[symbol] = history

        if len(stocks_data) < 2:
            return error_response('有效股票数据不足，无法进行相关性分析', 400)

        # 计算相关性
        correlation_result = calculate_correlation(stocks_data, days)

        return success_response({
            'symbols': list(stocks_data.keys()),
            'days': days,
            'correlation_matrix': correlation_result['matrix'],
            'analysis': correlation_result['analysis'],
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'相关性分析失败: {str(e)}')
        return error_response('相关性分析失败', 500)

@analysis_bp.route('/risk/<symbol>', methods=['GET'])
def get_risk_analysis(symbol):
    """获取风险分析"""
    try:
        if not symbol or len(symbol.strip()) == 0:
            return error_response('股票代码不能为空', 400)

        symbol = symbol.strip()
        days = request.args.get('days', 60, type=int)

        if days < 10 or days > 250:
            return error_response('分析天数必须在10-250之间', 400)

        # 获取历史数据
        history_data = stock_service.get_stock_price_history(symbol, limit=days + 20)
        if not history_data:
            return error_response('暂无历史数据', 404)

        # 计算风险指标
        risk_analysis = calculate_risk_metrics(history_data, days)

        return success_response({
            'symbol': symbol,
            'days': days,
            'risk_metrics': risk_analysis,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'风险分析失败 {symbol}: {str(e)}')
        return error_response('风险分析失败', 500)

def generate_technical_analysis(stock_info, history_data, indicators):
    """生成技术分析结果"""
    analysis = {
        'score': 0,
        'signals': [],
        'recommendations': [],
        'support_resistance': {}
    }

    try:
        current_price = stock_info.get('currentPrice', 0)

        # 移动平均线分析
        ma5 = indicators.get('ma5', 0)
        ma20 = indicators.get('ma20', 0)
        ma60 = indicators.get('ma60', 0)

        if ma5 and ma20 and ma60:
            if current_price > ma5 > ma20 > ma60:
                analysis['signals'].append('多头排列，趋势向上')
                analysis['score'] += 20
            elif current_price < ma5 < ma20 < ma60:
                analysis['signals'].append('空头排列，趋势向下')
                analysis['score'] -= 20

        # RSI分析
        rsi = indicators.get('rsi', 50)
        if rsi:
            if rsi > 70:
                analysis['signals'].append('RSI超买，可能回调')
                analysis['score'] -= 10
            elif rsi < 30:
                analysis['signals'].append('RSI超卖，可能反弹')
                analysis['score'] += 10

        # 成交量分析
        volume_ratio = indicators.get('volume_ratio', 1)
        if volume_ratio > 2:
            analysis['signals'].append('成交量放大，关注资金动向')

        # 生成建议
        if analysis['score'] >= 15:
            analysis['recommendations'].append('技术面偏强，可考虑买入')
            analysis['overall'] = 'bullish'
        elif analysis['score'] <= -15:
            analysis['recommendations'].append('技术面偏弱，注意风险')
            analysis['overall'] = 'bearish'
        else:
            analysis['recommendations'].append('技术面中性，观望为主')
            analysis['overall'] = 'neutral'

        # 支撑阻力位（简化计算）
        if len(history_data) >= 20:
            recent_prices = [item['close'] for item in history_data[-20:]]
            analysis['support_resistance'] = {
                'support': min(recent_prices),
                'resistance': max(recent_prices)
            }

    except Exception as e:
        current_app.logger.warning(f'技术分析计算错误: {str(e)}')

    return analysis

def generate_fundamental_analysis(stock_info):
    """生成基本面分析结果"""
    analysis = {
        'score': 0,
        'metrics': {},
        'analysis_points': [],
        'valuation': 'fair'
    }

    try:
        # 估值分析
        pe = stock_info.get('pe')
        pb = stock_info.get('pb')

        if pe:
            analysis['metrics']['pe_ratio'] = pe
            if pe < 15:
                analysis['analysis_points'].append('市盈率较低，估值合理')
                analysis['score'] += 10
            elif pe > 30:
                analysis['analysis_points'].append('市盈率较高，估值偏贵')
                analysis['score'] -= 10

        if pb:
            analysis['metrics']['pb_ratio'] = pb
            if pb < 1:
                analysis['analysis_points'].append('市净率小于1，可能存在价值')
                analysis['score'] += 5
            elif pb > 3:
                analysis['analysis_points'].append('市净率较高，需关注成长性')

        # 市值分析
        market_cap = stock_info.get('marketCap')
        if market_cap:
            analysis['metrics']['market_cap'] = market_cap
            if market_cap > 100000000000:  # 1000亿以上
                analysis['analysis_points'].append('大盘股，稳定性较好')
            elif market_cap < 10000000000:  # 100亿以下
                analysis['analysis_points'].append('小盘股，成长空间较大但风险也高')

        # 综合评估
        if analysis['score'] >= 10:
            analysis['valuation'] = 'undervalued'
        elif analysis['score'] <= -10:
            analysis['valuation'] = 'overvalued'

    except Exception as e:
        current_app.logger.warning(f'基本面分析计算错误: {str(e)}')

    return analysis

def generate_trend_analysis(history_data, days):
    """生成趋势分析结果"""
    analysis = {
        'trend_direction': 'sideways',
        'trend_strength': 0,
        'price_change': 0,
        'volatility': 0,
        'analysis_points': []
    }

    try:
        if len(history_data) < days:
            days = len(history_data)

        recent_data = history_data[-days:]

        if len(recent_data) >= 2:
            start_price = recent_data[0]['close']
            end_price = recent_data[-1]['close']
            price_change = (end_price - start_price) / start_price * 100

            analysis['price_change'] = round(price_change, 2)

            # 趋势方向判断
            if price_change > 5:
                analysis['trend_direction'] = 'upward'
                analysis['analysis_points'].append(f'近{days}日上涨{abs(price_change):.2f}%，趋势向上')
            elif price_change < -5:
                analysis['trend_direction'] = 'downward'
                analysis['analysis_points'].append(f'近{days}日下跌{abs(price_change):.2f}%，趋势向下')
            else:
                analysis['analysis_points'].append(f'近{days}日波动{abs(price_change):.2f}%，横盘整理')

            # 计算波动率
            daily_returns = []
            for i in range(1, len(recent_data)):
                daily_return = (recent_data[i]['close'] - recent_data[i-1]['close']) / recent_data[i-1]['close']
                daily_returns.append(daily_return)

            if daily_returns:
                volatility = pd.Series(daily_returns).std() * 100
                analysis['volatility'] = round(volatility, 2)

                if volatility > 3:
                    analysis['analysis_points'].append('波动率较高，风险较大')
                elif volatility < 1:
                    analysis['analysis_points'].append('波动率较低，走势稳定')

    except Exception as e:
        current_app.logger.warning(f'趋势分析计算错误: {str(e)}')

    return analysis

def calculate_correlation(stocks_data, days):
    """计算股票相关性"""
    result = {
        'matrix': {},
        'analysis': []
    }

    try:
        # 准备数据
        price_data = {}
        symbols = list(stocks_data.keys())

        for symbol, history in stocks_data.items():
            if len(history) >= days:
                prices = [item['close'] for item in history[-days:]]
                price_data[symbol] = prices

        # 计算相关系数矩阵
        df = pd.DataFrame(price_data)
        correlation_matrix = df.corr()

        # 转换为字典格式
        for i, symbol1 in enumerate(symbols):
            result['matrix'][symbol1] = {}
            for j, symbol2 in enumerate(symbols):
                if symbol1 in correlation_matrix.index and symbol2 in correlation_matrix.columns:
                    corr_value = correlation_matrix.loc[symbol1, symbol2]
                    result['matrix'][symbol1][symbol2] = round(corr_value, 3) if pd.notna(corr_value) else 0

        # 分析相关性
        for i, symbol1 in enumerate(symbols):
            for j, symbol2 in enumerate(symbols[i+1:], i+1):
                if symbol1 in correlation_matrix.index and symbol2 in correlation_matrix.columns:
                    corr = correlation_matrix.loc[symbol1, symbol2]
                    if pd.notna(corr):
                        if corr > 0.7:
                            result['analysis'].append(f'{symbol1}与{symbol2}高度正相关({corr:.3f})')
                        elif corr < -0.7:
                            result['analysis'].append(f'{symbol1}与{symbol2}高度负相关({corr:.3f})')

    except Exception as e:
        current_app.logger.warning(f'相关性计算错误: {str(e)}')

    return result

def calculate_risk_metrics(history_data, days):
    """计算风险指标"""
    metrics = {
        'volatility': 0,
        'max_drawdown': 0,
        'var_95': 0,  # 95%置信度的风险价值
        'sharpe_ratio': 0,
        'risk_level': 'medium'
    }

    try:
        if len(history_data) < days:
            days = len(history_data)

        recent_data = history_data[-days:]

        # 计算日收益率
        daily_returns = []
        for i in range(1, len(recent_data)):
            daily_return = (recent_data[i]['close'] - recent_data[i-1]['close']) / recent_data[i-1]['close']
            daily_returns.append(daily_return)

        if daily_returns:
            returns_series = pd.Series(daily_returns)

            # 波动率（年化）
            volatility = returns_series.std() * (252 ** 0.5) * 100
            metrics['volatility'] = round(volatility, 2)

            # 最大回撤
            cumulative_returns = (1 + returns_series).cumprod()
            running_max = cumulative_returns.cummax()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min() * 100
            metrics['max_drawdown'] = round(abs(max_drawdown), 2)

            # VaR (95%置信度)
            var_95 = returns_series.quantile(0.05) * 100
            metrics['var_95'] = round(abs(var_95), 2)

            # 夏普比率（简化计算，假设无风险利率为3%）
            excess_returns = returns_series.mean() - 0.03/252
            if returns_series.std() > 0:
                sharpe_ratio = excess_returns / returns_series.std() * (252 ** 0.5)
                metrics['sharpe_ratio'] = round(sharpe_ratio, 2)

            # 风险等级评估
            if volatility > 30 or max_drawdown > 20:
                metrics['risk_level'] = 'high'
            elif volatility < 15 and max_drawdown < 10:
                metrics['risk_level'] = 'low'

    except Exception as e:
        current_app.logger.warning(f'风险指标计算错误: {str(e)}')

    return metrics
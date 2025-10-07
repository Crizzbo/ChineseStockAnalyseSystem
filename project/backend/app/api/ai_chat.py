"""
AI聊天相关API路由
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ai_chat import ai_chat_service
from app.utils.response import success_response, error_response
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/chat', methods=['POST'])
@jwt_required(optional=True)
def chat():
    """
    AI聊天接口
    Body:
    - message: 用户消息
    - conversation_id: 对话ID（可选）
    - include_context: 是否包含上下文（可选）
    """
    try:
        data = request.get_json()

        # 参数验证
        if not data:
            return error_response("请求数据不能为空", 400)

        message = data.get('message', '').strip()
        if not message:
            return error_response("消息内容不能为空", 400)

        conversation_id = data.get('conversation_id', 'default')
        include_context = data.get('include_context', True)

        # 处理消息
        response = ai_chat_service.process_message(
            message=message,
            conversation_id=conversation_id,
            include_context=include_context
        )

        return success_response(
            data=response,
            message="AI回复生成成功"
        )

    except Exception as e:
        logger.error(f"AI聊天失败: {e}")
        return error_response("AI服务暂时不可用", 500)

@ai_bp.route('/suggestions', methods=['GET'])
@jwt_required(optional=True)
def get_suggestions():
    """
    获取建议问题
    Query Parameters:
    - context: 上下文（可选）
    """
    try:
        context = request.args.get('context', '')

        # 根据上下文返回建议问题
        if '股票' in context or '分析' in context:
            questions = [
                "今天哪些股票表现最好？",
                "如何分析股票的技术指标？",
                "推荐一些价值投资标的",
                "现在适合抄底吗？"
            ]
        elif '市场' in context or '行情' in context:
            questions = [
                "今天大盘走势如何？",
                "哪些板块值得关注？",
                "市场风险如何评估？",
                "下周市场预测"
            ]
        else:
            questions = [
                "今天股市表现如何？",
                "推荐一些科技股",
                "如何控制投资风险？",
                "什么是价值投资？",
                "如何看懂K线图？",
                "新手应该买什么股票？"
            ]

        return success_response(
            data={'questions': questions},
            message="获取建议问题成功"
        )

    except Exception as e:
        logger.error(f"获取建议问题失败: {e}")
        return error_response("获取建议失败", 500)

@ai_bp.route('/stock-qa/<string:symbol>', methods=['GET'])
@jwt_required(optional=True)
def get_stock_qa(symbol: str):
    """
    获取股票相关的智能问答
    Path Parameters:
    - symbol: 股票代码
    """
    try:
        if not symbol:
            return error_response("股票代码不能为空", 400)

        # 生成针对该股票的常见问题
        questions = [
            f"{symbol}这只股票怎么样？",
            f"分析一下{symbol}的投资价值",
            f"{symbol}的技术指标如何？",
            f"{symbol}适合长期持有吗？",
            f"{symbol}的风险评级是多少？"
        ]

        # 获取基本信息（如果可用）
        try:
            from app.services.stock_data import stock_service
            basic_info = stock_service.get_stock_basic_info(symbol)
        except Exception as e:
            logger.warning(f"获取股票基本信息失败: {e}")
            basic_info = None

        suggestions = [
            "查看同行业其他股票",
            "了解该股票的财务指标",
            "分析技术走势图",
            "评估投资风险"
        ]

        return success_response(
            data={
                'questions': questions,
                'basic_info': basic_info,
                'suggestions': suggestions
            },
            message="获取股票问答成功"
        )

    except Exception as e:
        logger.error(f"获取股票问答失败 {symbol}: {e}")
        return error_response("获取股票问答失败", 500)

@ai_bp.route('/market-insights', methods=['GET'])
@jwt_required(optional=True)
def get_market_insights():
    """
    获取市场洞察
    Query Parameters:
    - timeframe: 时间范围（today/week/month）
    """
    try:
        timeframe = request.args.get('timeframe', 'today')

        # 获取市场数据
        try:
            from app.services.stock_data import stock_service
            indices = stock_service.get_market_indices()
            hot_stocks = stock_service.get_hot_stocks(limit=10)
        except Exception as e:
            logger.warning(f"获取市场数据失败: {e}")
            indices = []
            hot_stocks = []

        # 生成市场洞察
        market_summary = "当前市场整体表现"
        if indices:
            total_change = sum(idx['changePercent'] for idx in indices[:3]) / 3
            if total_change > 1:
                market_summary += "较为活跃，主要指数普遍上涨。"
            elif total_change < -1:
                market_summary += "相对谨慎，主要指数出现调整。"
            else:
                market_summary += "相对平稳，指数窄幅震荡。"

        key_trends = [
            "科技股持续受到关注",
            "新能源板块表现活跃",
            "金融股估值优势明显",
            "消费板块分化显著"
        ]

        sector_highlights = [
            {
                "sector": "科技",
                "performance": 2.3,
                "analysis": "人工智能和芯片概念持续活跃"
            },
            {
                "sector": "新能源",
                "performance": 1.8,
                "analysis": "政策利好推动板块上涨"
            },
            {
                "sector": "金融",
                "performance": -0.5,
                "analysis": "银行股估值较低，具有配置价值"
            }
        ]

        risk_factors = [
            "宏观经济不确定性",
            "地缘政治风险",
            "流动性变化风险",
            "估值泡沫风险"
        ]

        opportunities = [
            "低估值蓝筹股机会",
            "科技创新主题投资",
            "结构性行情机会",
            "分红价值投资机会"
        ]

        insights = {
            'market_summary': market_summary,
            'key_trends': key_trends,
            'sector_highlights': sector_highlights,
            'risk_factors': risk_factors,
            'opportunities': opportunities
        }

        return success_response(
            data={
                'insights': insights,
                'timestamp': current_app.utils.get_current_timestamp() if hasattr(current_app, 'utils') else None
            },
            message="获取市场洞察成功"
        )

    except Exception as e:
        logger.error(f"获取市场洞察失败: {e}")
        return error_response("获取市场洞察失败", 500)

@ai_bp.route('/analyze-stocks', methods=['POST'])
@jwt_required(optional=True)
def analyze_stocks():
    """
    批量分析多只股票
    Body:
    - symbols: 股票代码列表
    - question: 分析问题
    """
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        symbols = data.get('symbols', [])
        question = data.get('question', '').strip()

        if not symbols:
            return error_response("股票代码列表不能为空", 400)

        if len(symbols) > 10:
            return error_response("最多支持同时分析10只股票", 400)

        # 分析每只股票
        analysis_results = []
        for symbol in symbols:
            try:
                # 这里应该调用实际的股票分析逻辑
                # 由于没有真实的AI模型，这里返回模拟分析结果
                score = 75  # 模拟评分
                recommendation = 'hold' if 60 <= score <= 80 else ('buy' if score > 80 else 'sell')

                analysis_results.append({
                    'symbol': symbol,
                    'name': f'股票{symbol}',  # 实际应该获取真实名称
                    'analysis': f'基于当前市场环境和{question}，该股票表现{["一般", "良好", "优秀"][score//30]}。',
                    'score': score,
                    'recommendation': recommendation
                })
            except Exception as e:
                logger.warning(f"分析股票{symbol}失败: {e}")
                continue

        # 生成综合分析
        avg_score = sum(item['score'] for item in analysis_results) / len(analysis_results) if analysis_results else 0
        summary = f"根据分析，{len(analysis_results)}只股票的平均评分为{avg_score:.1f}分。"

        comparison = "在对比分析中，建议重点关注评分较高的股票，同时注意风险控制。"

        return success_response(
            data={
                'analysis': analysis_results,
                'summary': summary,
                'comparison': comparison
            },
            message="股票分析完成"
        )

    except Exception as e:
        logger.error(f"批量分析股票失败: {e}")
        return error_response("批量分析失败", 500)

@ai_bp.route('/analyze-portfolio', methods=['POST'])
@jwt_required(optional=True)
def analyze_portfolio():
    """
    投资组合分析
    Body:
    - holdings: 持仓信息列表
    """
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        holdings = data.get('holdings', [])
        if not holdings:
            return error_response("持仓信息不能为空", 400)

        # 计算组合指标（模拟）
        total_value = sum(holding['quantity'] * 50 for holding in holdings)  # 模拟当前价值
        total_cost = sum(holding['quantity'] * holding['average_cost'] for holding in holdings)
        total_return = total_value - total_cost

        # 风险评分（简化）
        risk_score = min(len(holdings) * 10, 100)  # 股票数量越多风险越分散

        # 多样化评分
        diversification_score = min(len(set(h['symbol'][:2] for h in holdings)) * 20, 100)

        # 行业分配（模拟）
        sector_allocation = {
            '科技': 40,
            '金融': 30,
            '消费': 20,
            '其他': 10
        }

        recommendations = [
            "建议进一步分散投资组合",
            "关注高质量蓝筹股",
            "定期调整仓位配比",
            "设置止损保护机制"
        ]

        rebalancing_suggestions = [
            {
                'action': 'buy',
                'symbol': '000001',
                'reason': '增加金融板块配置',
                'priority': 'medium'
            },
            {
                'action': 'sell',
                'symbol': '000002',
                'reason': '减少集中度风险',
                'priority': 'low'
            }
        ]

        analysis = {
            'total_value': total_value,
            'total_return': total_return,
            'risk_score': risk_score,
            'diversification_score': diversification_score,
            'sector_allocation': sector_allocation,
            'recommendations': recommendations,
            'rebalancing_suggestions': rebalancing_suggestions
        }

        return success_response(
            data={'analysis': analysis},
            message="投资组合分析完成"
        )

    except Exception as e:
        logger.error(f"投资组合分析失败: {e}")
        return error_response("投资组合分析失败", 500)

@ai_bp.route('/risk-assessment', methods=['POST'])
@jwt_required(optional=True)
def assess_risk():
    """
    风险评估
    Body:
    - portfolio: 投资组合信息
    - timeframe: 评估时间范围（天数）
    """
    try:
        data = request.get_json()
        if not data:
            return error_response("请求数据不能为空", 400)

        portfolio = data.get('portfolio', {})
        timeframe = data.get('timeframe', 30)

        if not portfolio:
            return error_response("投资组合信息不能为空", 400)

        # 风险评估（模拟计算）
        overall_risk = 'medium'  # 根据实际情况计算
        var_95 = 0.15  # 95%置信度的风险价值
        max_drawdown = 0.08  # 最大回撤
        volatility = 0.25  # 波动率

        correlation_risks = [
            "同行业股票相关性较高",
            "市场系统性风险较大"
        ]

        concentration_risks = [
            "单一股票持仓过重",
            "板块集中度较高"
        ]

        recommendations = [
            "建议分散投资降低风险",
            "增加债券等低风险资产配置",
            "定期监控投资组合表现",
            "设置合理的风控机制"
        ]

        risk_assessment = {
            'overall_risk': overall_risk,
            'var_95': var_95,
            'max_drawdown': max_drawdown,
            'volatility': volatility,
            'correlation_risks': correlation_risks,
            'concentration_risks': concentration_risks,
            'recommendations': recommendations
        }

        return success_response(
            data={'risk_assessment': risk_assessment},
            message="风险评估完成"
        )

    except Exception as e:
        logger.error(f"风险评估失败: {e}")
        return error_response("风险评估失败", 500)
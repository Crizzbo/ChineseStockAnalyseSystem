"""
AI聊天服务 - 股票投资助手
"""
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.services.stock_data import stock_service
from app.services.sector_data import sector_service
import logging

logger = logging.getLogger(__name__)

class AIChatService:
    """AI聊天服务类"""

    def __init__(self):
        # 股票相关关键词
        self.stock_keywords = [
            '股票', '股价', '涨跌', '买入', '卖出', '持有', '投资', '收益',
            '亏损', '风险', '回报', '市盈率', 'PE', '市净率', 'PB', '成交量'
        ]

        # 板块相关关键词
        self.sector_keywords = [
            '板块', '行业', '概念股', '题材', '龙头股', '科技股', '金融股',
            '医药股', '消费股', '新能源', '人工智能', '芯片'
        ]

        # 预设回复模板
        self.response_templates = {
            'greeting': [
                '您好！我是您的AI投资助手，很高兴为您服务！',
                '欢迎使用AI投资助手！我可以为您提供股票分析、投资建议等服务。',
                '您好！有什么股票投资问题需要咨询吗？'
            ],
            'market_general': [
                '让我为您查询最新的市场数据...',
                '我来为您分析当前的市场情况...',
                '正在获取实时市场信息，请稍候...'
            ],
            'stock_analysis': [
                '正在为您分析该股票的表现...',
                '让我查看这只股票的技术指标和基本面数据...',
                '我来为您解读这只股票的投资价值...'
            ],
            'investment_advice': [
                '基于当前市场数据，我的建议是...',
                '从风险收益角度来看...',
                '考虑到您的投资目标，建议您...'
            ],
            'error': [
                '抱歉，我无法获取相关数据，请稍后再试。',
                '系统暂时无法处理您的请求，请稍候重试。',
                '抱歉，遇到了一些技术问题，请稍后再试。'
            ]
        }

    def process_message(self, message: str, conversation_id: str = None,
                       include_context: bool = True) -> Dict[str, Any]:
        """处理用户消息并生成回复"""
        try:
            # 消息预处理
            processed_message = self._preprocess_message(message)

            # 识别意图
            intent = self._identify_intent(processed_message)

            # 提取实体（股票代码、板块名称等）
            entities = self._extract_entities(processed_message)

            # 生成回复
            reply = self._generate_reply(intent, entities, processed_message)

            # 获取相关建议
            suggestions = self._get_suggestions(intent, entities)

            return {
                'reply': reply,
                'conversation_id': conversation_id or f"conv_{int(datetime.now().timestamp())}",
                'message_id': f"msg_{int(datetime.now().timestamp())}",
                'stocks_mentioned': entities.get('stocks', []),
                'suggestions': suggestions,
                'confidence': 0.8,  # 模拟置信度
                'sources': self._get_sources(intent, entities),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"AI聊天处理失败: {e}")
            return {
                'reply': '抱歉，处理您的消息时遇到了问题，请稍后重试。',
                'conversation_id': conversation_id or 'default',
                'message_id': f"msg_{int(datetime.now().timestamp())}",
                'stocks_mentioned': [],
                'suggestions': ['今天股市表现如何？', '推荐一些优质股票'],
                'confidence': 0.1,
                'sources': [],
                'timestamp': datetime.now().isoformat()
            }

    def _preprocess_message(self, message: str) -> str:
        """预处理用户消息"""
        # 转换为小写
        message = message.lower()

        # 移除多余空格
        message = re.sub(r'\s+', ' ', message).strip()

        return message

    def _identify_intent(self, message: str) -> str:
        """识别用户意图"""
        # 问候意图
        if any(word in message for word in ['你好', '您好', '嗨', 'hello', 'hi']):
            return 'greeting'

        # 市场查询意图
        if any(word in message for word in ['市场', '大盘', '指数', '行情', '今天', '股市']):
            return 'market_query'

        # 股票分析意图
        if any(word in message for word in ['分析', '怎么样', '如何', '评价', '建议']):
            return 'stock_analysis'

        # 投资建议意图
        if any(word in message for word in ['推荐', '买什么', '投资', '选股']):
            return 'investment_advice'

        # 技术指标咨询
        if any(word in message for word in ['技术指标', 'ma', 'rsi', '移动平均', '相对强弱']):
            return 'technical_analysis'

        # 风险评估
        if any(word in message for word in ['风险', '安全', '亏损', '止损']):
            return 'risk_assessment'

        return 'general_query'

    def _extract_entities(self, message: str) -> Dict[str, List[str]]:
        """提取消息中的实体"""
        entities = {
            'stocks': [],
            'sectors': [],
            'numbers': []
        }

        # 提取股票代码（6位数字）
        stock_codes = re.findall(r'\b\d{6}\b', message)
        entities['stocks'].extend(stock_codes)

        # 提取板块名称（简单匹配）
        sector_patterns = [
            '科技', '金融', '医药', '消费', '地产', '新能源', '电子', '汽车',
            '人工智能', 'ai', '芯片', '半导体', '5g', '新基建'
        ]
        for pattern in sector_patterns:
            if pattern in message:
                entities['sectors'].append(pattern)

        # 提取数字
        numbers = re.findall(r'\b\d+\.?\d*\b', message)
        entities['numbers'].extend(numbers)

        return entities

    def _generate_reply(self, intent: str, entities: Dict[str, Any], message: str) -> str:
        """生成回复"""
        try:
            if intent == 'greeting':
                return self._handle_greeting()

            elif intent == 'market_query':
                return self._handle_market_query()

            elif intent == 'stock_analysis':
                return self._handle_stock_analysis(entities)

            elif intent == 'investment_advice':
                return self._handle_investment_advice(entities)

            elif intent == 'technical_analysis':
                return self._handle_technical_analysis()

            elif intent == 'risk_assessment':
                return self._handle_risk_assessment()

            else:
                return self._handle_general_query(message)

        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            return "抱歉，我现在无法处理您的请求，请稍后再试。"

    def _handle_greeting(self) -> str:
        """处理问候"""
        return """您好！我是您的AI投资助手 🤖

我可以帮您：
• 📊 分析股票和市场行情
• 💡 提供投资建议和策略
• 📈 解读技术指标和基本面
• ⚠️ 评估投资风险
• 🔍 推荐优质投资标的

请问今天有什么投资问题需要咨询吗？"""

    def _handle_market_query(self) -> str:
        """处理市场查询"""
        try:
            # 获取市场指数数据
            indices = stock_service.get_market_indices()

            if indices:
                market_summary = "📊 **今日市场概况**\n\n"
                for index in indices[:3]:  # 显示前3个主要指数
                    change_emoji = "📈" if index['change'] >= 0 else "📉"
                    market_summary += f"{change_emoji} **{index['name']}**: {index['currentPrice']:.2f} "
                    market_summary += f"({index['change']:+.2f}, {index['changePercent']:+.2f}%)\n"

                market_summary += "\n💡 **投资建议**: 请根据市场趋势和个人风险偏好做出投资决策。建议分散投资，控制仓位。"
                return market_summary
            else:
                return "抱歉，暂时无法获取市场数据。建议您稍后再试或查看其他财经资讯平台。"

        except Exception as e:
            logger.error(f"处理市场查询失败: {e}")
            return "市场数据暂时不可用，请稍后再试。您可以询问其他投资相关问题。"

    def _handle_stock_analysis(self, entities: Dict[str, Any]) -> str:
        """处理股票分析"""
        stocks = entities.get('stocks', [])

        if not stocks:
            return """📈 **股票分析服务**

要分析具体股票，请提供股票代码，例如：
• "分析一下000001"
• "600036怎么样"
• "请评价002415这只股票"

我可以为您分析：
• 基本面指标（PE、PB、市值等）
• 技术面走势
• 投资价值评估
• 风险提示"""

        # 分析第一只股票
        stock_code = stocks[0]
        try:
            stock_info = stock_service.get_stock_basic_info(stock_code)

            if stock_info:
                analysis = f"📊 **{stock_info['name']} ({stock_code}) 分析报告**\n\n"
                analysis += f"💰 **当前价格**: ¥{stock_info['currentPrice']:.2f}\n"

                change_emoji = "📈" if stock_info['change'] >= 0 else "📉"
                analysis += f"{change_emoji} **今日涨跌**: {stock_info['change']:+.2f} ({stock_info['changePercent']:+.2f}%)\n\n"

                analysis += f"📈 **技术指标**:\n"
                analysis += f"• 成交量: {stock_info['volume']:,}手\n"
                analysis += f"• 成交额: ¥{stock_info['turnover']:,.0f}万\n"

                if stock_info.get('pe'):
                    analysis += f"• 市盈率: {stock_info['pe']:.2f}\n"
                if stock_info.get('pb'):
                    analysis += f"• 市净率: {stock_info['pb']:.2f}\n"

                analysis += f"\n💡 **投资建议**: 请结合公司基本面、行业前景和技术走势进行综合判断。建议关注公司财报和重要公告。"

                return analysis
            else:
                return f"抱歉，无法获取股票 {stock_code} 的数据。请检查代码是否正确，或稍后重试。"

        except Exception as e:
            logger.error(f"股票分析失败 {stock_code}: {e}")
            return f"分析股票 {stock_code} 时遇到问题，请稍后重试。"

    def _handle_investment_advice(self, entities: Dict[str, Any]) -> str:
        """处理投资建议"""
        sectors = entities.get('sectors', [])

        if sectors:
            sector_name = sectors[0]
            return f"""💡 **{sector_name}板块投资建议**

基于当前市场环境，{sector_name}板块值得关注：

📊 **板块特点**:
• 成长性较好，未来发展空间大
• 政策支持力度较强
• 技术创新驱动明显

⚠️ **风险提示**:
• 板块波动性较大
• 估值可能偏高
• 需关注政策变化

🎯 **投资策略**:
• 建议分批建仓，控制仓位
• 选择龙头企业优先
• 关注财报和业绩表现
• 设置合理的止盈止损点"""

        return """💡 **通用投资建议**

🎯 **投资原则**:
1. **分散投资**: 不要把鸡蛋放在一个篮子里
2. **长期持有**: 优质股票适合长期投资
3. **风险控制**: 设置合理的止损点
4. **定期评估**: 定期检查投资组合表现

📈 **选股建议**:
• 关注基本面良好的公司
• 选择行业龙头企业
• 考虑估值合理性
• 关注公司治理结构

⚠️ **风险提示**: 股市有风险，投资需谨慎。建议根据自身风险承受能力进行投资。"""

    def _handle_technical_analysis(self) -> str:
        """处理技术分析咨询"""
        return """📈 **技术分析指导**

🔍 **常用技术指标**:
• **MA(移动平均线)**: 判断趋势方向
• **RSI(相对强弱指数)**: 判断超买超卖
• **MACD**: 判断买卖信号
• **布林带**: 判断价格区间

📊 **分析方法**:
1. **趋势分析**: 确定主要趋势方向
2. **支撑阻力**: 寻找关键价位
3. **成交量**: 确认价格走势
4. **形态识别**: 识别经典图形

💡 **使用建议**:
• 结合多个指标综合判断
• 技术分析要结合基本面
• 注意指标的滞后性
• 设置合理的止损位

需要分析具体股票的技术指标吗？请提供股票代码。"""

    def _handle_risk_assessment(self) -> str:
        """处理风险评估"""
        return """⚠️ **投资风险评估指南**

🎯 **风险类型**:
• **市场风险**: 整体市场波动
• **个股风险**: 单一股票风险
• **行业风险**: 特定行业风险
• **流动性风险**: 买卖困难风险

📊 **风险控制策略**:
1. **仓位控制**: 单只股票不超过20%
2. **分散投资**: 多个行业分散配置
3. **止损设置**: 设定合理止损点
4. **定期调整**: 定期重新评估

🔍 **风险评估方法**:
• 分析公司财务状况
• 关注行业发展趋势
• 评估估值合理性
• 考虑宏观经济环境

💡 **建议**: 根据个人风险承受能力，选择合适的投资策略。保守型投资者建议选择蓝筹股和指数基金。"""

    def _handle_general_query(self, message: str) -> str:
        """处理一般查询"""
        return """🤖 我是您的AI投资助手，专注于股票投资咨询。

📋 **我可以帮您**:
• 股票分析和评价
• 市场行情解读
• 投资建议和策略
• 技术指标分析
• 风险评估建议

💬 **使用示例**:
• "今天股市表现如何？"
• "分析一下000001这只股票"
• "推荐一些科技股"
• "如何控制投资风险？"

请告诉我您的具体需求，我会尽力为您提供专业的投资建议！"""

    def _get_suggestions(self, intent: str, entities: Dict[str, Any]) -> List[str]:
        """获取相关建议问题"""
        if intent == 'greeting':
            return [
                "今天股市表现如何？",
                "推荐一些优质股票",
                "如何控制投资风险？"
            ]
        elif intent == 'market_query':
            return [
                "哪些板块今天表现最好？",
                "推荐一些抗跌股票",
                "现在适合买入吗？"
            ]
        elif intent == 'stock_analysis':
            return [
                "这只股票的风险如何？",
                "有什么类似的股票推荐？",
                "技术指标怎么看？"
            ]
        else:
            return [
                "分析一下热门股票",
                "当前市场趋势如何？",
                "投资新手应该注意什么？"
            ]

    def _get_sources(self, intent: str, entities: Dict[str, Any]) -> List[Dict[str, str]]:
        """获取信息来源"""
        sources = [
            {
                "type": "实时数据",
                "title": "实时股票行情数据",
                "url": None
            }
        ]

        if intent == 'market_query':
            sources.append({
                "type": "市场分析",
                "title": "主要指数实时数据",
                "url": None
            })

        return sources

# 创建全局实例
ai_chat_service = AIChatService()
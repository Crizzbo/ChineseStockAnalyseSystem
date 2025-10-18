"""
Copilot AI 配置文件
"""

# Copilot AI 服务配置
COPILOT_AI_CONFIG = {
    'model_name': 'gpt-4',  # 使用的模型名称
    'max_tokens': 2000,     # 最大token数
    'temperature': 0.7,     # 温度参数（创造性）
    'top_p': 0.95,         # 核采样参数
    'request_timeout': 60,  # 请求超时时间（秒）
    
    # 默认系统提示语
    'system_prompt': '''你是一个专业的股票投资分析助手，擅长：
1. 股票基本面分析
2. 技术指标解读
3. 市场趋势分析
4. 投资风险评估
5. 投资策略建议

请基于专业知识为用户提供客观、理性的投资建议。
始终提醒用户：股市有风险，投资需谨慎。
''',
    
    # 响应格式设置
    'response_format': {
        'use_markdown': True,   # 使用Markdown格式
        'include_sources': True # 包含信息来源
    }
}
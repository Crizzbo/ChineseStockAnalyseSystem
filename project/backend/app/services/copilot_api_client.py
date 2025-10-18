"""
Copilot API 客户端
"""
import os
import aiohttp
import json
import logging
from typing import Dict, Any, List, Optional
from app.config.copilot_config import COPILOT_AI_CONFIG

logger = logging.getLogger(__name__)

class CopilotClient:
    """GitHub Copilot API 客户端"""
    
    def __init__(self):
        self.api_key = os.getenv('GITHUB_COPILOT_TOKEN')
        self.api_endpoint = "https://api.github.com/copilot/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "OpenAI-Organization": "github-copilot",
            "User-Agent": "StockAnalysisSystem/1.0"
        }
        self.config = COPILOT_AI_CONFIG

    async def get_completion(self, 
                           messages: List[Dict[str, str]], 
                           temperature: Optional[float] = None,
                           max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        从Copilot获取补全
        """
        try:
            # 使用配置值或默认值
            temperature = temperature or self.config['temperature']
            max_tokens = max_tokens or self.config['max_tokens']

            payload = {
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "model": self.config['model_name'],
                "n": 1,
                "stream": False
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=self.config['request_timeout']
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            'success': True,
                            'content': result['choices'][0]['message']['content'],
                            'finish_reason': result['choices'][0]['finish_reason'],
                            'usage': result.get('usage', {})
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Copilot API错误: {response.status} - {error_text}")
                        return {
                            'success': False,
                            'error': f"API错误: {response.status}",
                            'details': error_text
                        }

        except Exception as e:
            logger.error(f"调用Copilot API时出错: {str(e)}")
            return {
                'success': False,
                'error': "API调用失败",
                'details': str(e)
            }

    async def generate_stock_analysis(self, stock_code: str, stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成股票分析
        """
        system_prompt = self.config['system_prompt']
        
        # 构建上下文消息
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user", 
                "content": f"请分析股票 {stock_code} 的投资价值。以下是基本数据：\n{json.dumps(stock_info, ensure_ascii=False, indent=2)}"
            }
        ]
        
        return await self.get_completion(messages)

    async def analyze_market_trend(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析市场趋势
        """
        system_prompt = self.config['system_prompt']
        
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"请分析当前市场趋势。以下是市场数据：\n{json.dumps(market_data, ensure_ascii=False, indent=2)}"
            }
        ]
        
        return await self.get_completion(messages)

    async def provide_investment_advice(self, 
                                     user_query: str,
                                     portfolio: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        提供投资建议
        """
        system_prompt = self.config['system_prompt']
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        if portfolio:
            messages.append({
                "role": "user",
                "content": f"考虑我当前的投资组合：\n{json.dumps(portfolio, ensure_ascii=False, indent=2)}"
            })
        
        return await self.get_completion(messages)

    async def technical_analysis(self, 
                               stock_code: str, 
                               technical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        技术分析
        """
        system_prompt = self.config['system_prompt']
        
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"请对股票 {stock_code} 进行技术分析。以下是技术指标数据：\n{json.dumps(technical_data, ensure_ascii=False, indent=2)}"
            }
        ]
        
        return await self.get_completion(messages)

    async def risk_assessment(self, 
                            stock_code: str, 
                            risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        风险评估
        """
        system_prompt = self.config['system_prompt']
        
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"请评估股票 {stock_code} 的投资风险。以下是风险相关数据：\n{json.dumps(risk_data, ensure_ascii=False, indent=2)}"
            }
        ]
        
        return await self.get_completion(messages)

# 创建全局实例
copilot_client = CopilotClient()
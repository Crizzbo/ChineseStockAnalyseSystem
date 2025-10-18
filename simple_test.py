#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的AkShare工具测试
"""
import sys
import os
from typing import Any, Dict, List
import akshare as ak

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project', 'backed'))

def get_index_data(symbol: str):
    return ak.stock_zh_index_spot_em(symbol)
    
def get_market_indices():
    """获取主要市场指数"""
    try:
        indices_name = (
            "沪深重要指数", 
            "上证系列指数", 
            "深证系列指数", 
            "指数成份", 
            "中证系列指数"
        )
        indices_data = []
        for name in indices_name:
            index_data = get_index_data(name)
            # print(index_data)    
            for _ , row in index_data.iterrows():
                
                indices_data.append({
                    'symbol': float(row['代码']),
                    'name': str(row['名称']),
                    'currentPrice': float(row['最新价']),
                    'change': float(row['涨跌额']),
                    'changePercent': float(row['涨跌幅']),
                    'volume': int(row['成交量']) if row['成交量'] != '-' else 0,
                    'turnover': float(row['成交额']) if row['成交额'] != '-' else 0.0
                })

        return indices_data
            
    except Exception as e:
        print(f"获取市场指数失败: {e}")
        return []
    
if __name__ == "__main__":
    print(get_market_indices())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
填充缓存数据 - 用于在AkShare API不可用时提供备用数据
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project', 'backend'))

from app.services.sector_data import sector_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_cache():
    """尝试获取并缓存板块数据"""
    try:
        logger.info("开始获取板块数据...")
        sectors = sector_service.get_sectors(limit=100)

        if sectors:
            logger.info(f"成功获取 {len(sectors)} 个板块，已保存到缓存")

            # 获取前10个板块的成分股
            logger.info("开始获取板块成分股数据...")
            for sector in sectors[:10]:
                try:
                    stocks = sector_service.get_sector_stocks(sector['name'])
                    if stocks:
                        logger.info(f"成功获取板块 {sector['name']} 的 {len(stocks)} 只成分股")
                except Exception as e:
                    logger.error(f"获取板块 {sector['name']} 成分股失败: {e}")
                    continue
        else:
            logger.warning("未能获取板块数据")

    except Exception as e:
        logger.error(f"填充缓存失败: {e}")

if __name__ == "__main__":
    populate_cache()

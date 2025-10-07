#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AkShare 函数测试脚本
参照官方文档测试所有核心 AkShare 函数调用
"""

import akshare as ak
import pandas as pd
import time
import warnings
warnings.filterwarnings('ignore')

def test_with_retry(func, func_name, max_retries=3, delay=5):
    """带重试机制的测试函数"""
    for attempt in range(max_retries):
        try:
            print(f"\n{'='*50}")
            print(f"测试 {func_name} (尝试 {attempt + 1}/{max_retries})")
            print(f"{'='*50}")

            start_time = time.time()
            result = func()
            end_time = time.time()

            if result is not None and not result.empty:
                print(f"SUCCESS {func_name} 成功!")
                print(f"耗时: {end_time - start_time:.2f}秒")
                print(f"数据形状: {result.shape}")
                print(f"列名: {list(result.columns)}")
                print("前3行数据:")
                print(result.head(3))
                return result
            else:
                print(f"WARNING {func_name} 返回空数据")

        except Exception as e:
            print(f"ERROR {func_name} 失败 (尝试 {attempt + 1}): {str(e)}")
            if attempt < max_retries - 1:
                print(f"等待 {delay} 秒后重试...")
                time.sleep(delay)
                delay *= 1.5  # 指数退避

    print(f"FAILED {func_name} 最终失败!")
    return None

def test_stock_spot():
    """测试A股实时行情"""
    def get_data():
        return ak.stock_zh_a_spot_em()

    return test_with_retry(get_data, "A股实时行情 (stock_zh_a_spot_em)")

def test_sector_list():
    """测试板块列表"""
    def get_data():
        return ak.stock_board_industry_name_em()

    return test_with_retry(get_data, "板块列表 (stock_board_industry_name_em)")

def test_sector_stocks():
    """测试板块成分股"""
    def get_data():
        # 使用常见板块名称
        return ak.stock_board_industry_cons_em(symbol="电子信息")

    return test_with_retry(get_data, "板块成分股 (stock_board_industry_cons_em)")

def test_stock_history():
    """测试历史股票数据"""
    def get_data():
        return ak.stock_zh_a_hist(
            symbol="000001",
            period="daily",
            start_date="20240901",
            end_date="20240930",
            adjust=""
        )

    return test_with_retry(get_data, "股票历史数据 (stock_zh_a_hist)")

def test_index_spot():
    """测试指数实时数据"""
    def get_data():
        return ak.stock_zh_index_spot_em()

    return test_with_retry(get_data, "指数实时数据 (stock_zh_index_spot_em)")

def test_alternative_apis():
    """测试备用API"""
    print(f"\n============================================================")
    print("测试备用API接口")
    print(f"============================================================")

    # 测试新浪财经API
    def test_sina():
        return ak.stock_zh_a_spot()

    sina_result = test_with_retry(test_sina, "新浪财经A股数据 (stock_zh_a_spot)")

    # 测试东财备用接口
    def test_em_backup():
        return ak.stock_board_concept_name_em()

    em_result = test_with_retry(test_em_backup, "东财概念板块 (stock_board_concept_name_em)")

    return sina_result, em_result

def main():
    """主测试函数"""
    print("开始 AkShare 函数测试")
    print(f"AkShare 版本: {ak.__version__}")

    # 存储测试结果
    results = {}

    # 测试核心API
    print("\n测试核心股票和板块API...")

    results['stock_spot'] = test_stock_spot()
    time.sleep(3)  # 避免请求过于频繁

    results['sector_list'] = test_sector_list()
    time.sleep(3)

    results['sector_stocks'] = test_sector_stocks()
    time.sleep(3)

    results['stock_history'] = test_stock_history()
    time.sleep(3)

    results['index_spot'] = test_index_spot()
    time.sleep(3)

    # 测试备用API
    sina_result, em_result = test_alternative_apis()
    results['sina_backup'] = sina_result
    results['em_backup'] = em_result

    # 总结测试结果
    print(f"\n============================================================")
    print("测试结果总结")
    print(f"============================================================")

    success_count = 0
    total_count = len(results)

    for name, result in results.items():
        status = "SUCCESS" if result is not None and not result.empty else "FAILED"
        print(f"{name}: {status}")
        if result is not None and not result.empty:
            success_count += 1

    success_rate = (success_count / total_count) * 100
    print(f"\n成功率: {success_count}/{total_count} ({success_rate:.1f}%)")

    if success_count > 0:
        print("有可用的API接口!")
        print("建议使用成功的接口更新后端代码")
    else:
        print("所有API接口都失败!")
        print("建议检查网络连接或使用备用数据源")

    return results

if __name__ == "__main__":
    main()
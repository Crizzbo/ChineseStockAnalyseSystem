"""
AKShare工具使用示例
演示如何使用股票分析系统进行股票分析
"""

import logging
from stock_analysis_system import StockAnalysisSystem
from tools.utils.data_validator import DataValidator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def basic_usage_example():
    """基本使用示例"""
    print("=== 基本使用示例 ===")

    # 创建分析系统实例
    system = StockAnalysisSystem(enable_cache=True)

    # 分析股票（以平安银行 000001 为例）
    symbol = "000001"

    try:
        # 执行基本分析
        result = system.analyze_stock(symbol, analysis_type='basic')

        print(f"\n股票{symbol}基本分析结果:")
        print(f"分析时间: {result['analysis_time']}")

        # 显示当前信息
        current_info = result['analysis_results'].get('current_info', {})
        if current_info:
            print(f"当前价格: {current_info.get('current_price', 'N/A')}")
            print(f"涨跌幅: {current_info.get('change_percent', 'N/A')}%")
            print(f"成交量: {current_info.get('volume', 'N/A')}")

        # 显示近期表现
        recent_performance = result['analysis_results'].get('recent_performance', {})
        if recent_performance:
            print(f"\n近期表现:")
            print(f"期间涨跌幅: {recent_performance.get('price_change_percent', 'N/A'):.2f}%")
            print(f"期间最高价: {recent_performance.get('period_high', 'N/A')}")
            print(f"期间最低价: {recent_performance.get('period_low', 'N/A')}")

        print("\n基本分析完成!")

    except Exception as e:
        print(f"分析失败: {str(e)}")

def comprehensive_analysis_example():
    """综合分析示例"""
    print("\n=== 综合分析示例 ===")

    system = StockAnalysisSystem(enable_cache=True)
    symbol = "000001"

    try:
        # 执行综合分析
        result = system.analyze_stock(symbol, analysis_type='comprehensive')

        print(f"\n股票{symbol}综合分析结果:")

        # 显示综合评估
        assessment = result.get('comprehensive_assessment', {})
        if assessment:
            print(f"综合评分: {assessment.get('overall_score', 0):.2f}")

            strengths = assessment.get('strengths', [])
            if strengths:
                print("优势:")
                for strength in strengths:
                    print(f"  - {strength}")

            weaknesses = assessment.get('weaknesses', [])
            if weaknesses:
                print("劣势:")
                for weakness in weaknesses:
                    print(f"  - {weakness}")

        # 显示风险评估
        risk_assessment = result.get('risk_assessment', {})
        if risk_assessment:
            print(f"\n风险评估:")
            print(f"风险等级: {risk_assessment.get('overall_risk_level', 'N/A')}")
            print(f"风险评分: {risk_assessment.get('risk_score', 0):.2f}")

            risk_factors = risk_assessment.get('risk_factors', [])
            if risk_factors:
                print("风险因素:")
                for factor in risk_factors:
                    print(f"  - {factor}")

        # 显示投资建议
        recommendation = result.get('investment_recommendation', {})
        if recommendation:
            print(f"\n投资建议:")
            print(f"建议操作: {recommendation.get('action', 'N/A')}")
            print(f"信心度: {recommendation.get('confidence', 0):.2f}")

            reasoning = recommendation.get('reasoning', [])
            if reasoning:
                print("建议理由:")
                for reason in reasoning:
                    print(f"  - {reason}")

        print("\n综合分析完成!")

    except Exception as e:
        print(f"综合分析失败: {str(e)}")

def service_usage_examples():
    """各个服务的使用示例"""
    print("\n=== 各服务使用示例 ===")

    system = StockAnalysisSystem(enable_cache=True)
    symbol = "000001"

    # 实时数据服务示例
    print("\n1. 实时数据服务:")
    try:
        realtime_data = system.realtime_service.get_stock_realtime(symbol)
        if realtime_data:
            print(f"股票名称: {realtime_data.get('name', 'N/A')}")
            print(f"最新价: {realtime_data.get('current_price', 'N/A')}")
    except Exception as e:
        print(f"获取实时数据失败: {str(e)}")

    # 历史数据服务示例
    print("\n2. 历史数据服务:")
    try:
        historical_data = system.historical_service.get_recent_data(symbol, 5)
        if historical_data is not None and not historical_data.empty:
            print(f"获取到{len(historical_data)}天的历史数据")
            print("最近5天收盘价:")
            for _, row in historical_data.tail().iterrows():
                print(f"  {row['日期']}: {row['收盘']}")
    except Exception as e:
        print(f"获取历史数据失败: {str(e)}")

    # 基本面数据服务示例
    print("\n3. 基本面数据服务:")
    try:
        financial_ratios = system.fundamental_service.calculate_financial_ratios(symbol)
        if financial_ratios:
            print("主要财务比率:")
            for ratio_name, ratio_value in financial_ratios.items():
                print(f"  {ratio_name}: {ratio_value:.4f}")
    except Exception as e:
        print(f"获取基本面数据失败: {str(e)}")

def data_validation_example():
    """数据验证示例"""
    print("\n=== 数据验证示例 ===")

    system = StockAnalysisSystem(enable_cache=True)
    validator = DataValidator()
    symbol = "000001"

    try:
        # 获取历史数据并验证
        historical_data = system.historical_service.get_recent_data(symbol, 30)

        if historical_data is not None:
            # 验证数据质量
            validation_result = validator.validate_stock_data(historical_data, 'historical')

            print(f"数据验证结果:")
            print(f"验证状态: {'通过' if validation_result['is_valid'] else '失败'}")
            print(f"数据行数: {validation_result['data_info']['total_rows']}")
            print(f"数据列数: {validation_result['data_info']['total_columns']}")

            # 显示错误和警告
            errors = validation_result.get('errors', [])
            if errors:
                print("错误:")
                for error in errors:
                    print(f"  - {error}")

            warnings = validation_result.get('warnings', [])
            if warnings:
                print("警告:")
                for warning in warnings:
                    print(f"  - {warning}")

            # 生成数据质量报告
            report = validator.generate_data_quality_report(validation_result)
            print(f"\n数据质量报告:\n{report}")

    except Exception as e:
        print(f"数据验证失败: {str(e)}")

def cache_usage_example():
    """缓存使用示例"""
    print("\n=== 缓存使用示例 ===")

    system = StockAnalysisSystem(enable_cache=True)

    try:
        # 获取缓存统计
        stats = system.get_system_stats()
        cache_stats = stats.get('cache_stats', {})

        print("缓存统计信息:")
        print(f"Redis可用: {cache_stats.get('redis_available', False)}")
        print(f"文件缓存启用: {cache_stats.get('file_cache_enabled', False)}")

        # 清理缓存
        cleanup_result = system.cleanup_cache()
        print(f"\n缓存清理结果:")
        print(f"清理项目: {cleanup_result.get('cleared_items', 0)}")
        print(f"过期项目: {cleanup_result.get('expired_items', 0)}")

    except Exception as e:
        print(f"缓存操作失败: {str(e)}")

def main():
    """主函数"""
    print("AKShare股票分析工具使用示例\n")

    # 运行各种示例
    basic_usage_example()
    comprehensive_analysis_example()
    service_usage_examples()
    data_validation_example()
    cache_usage_example()

    print("\n=== 所有示例运行完成 ===")

if __name__ == "__main__":
    main()
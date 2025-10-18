"""
缓存预热脚本 - 用于初始化或更新数据缓存
"""
import akshare as ak
import pandas as pd
from app.utils.data_cache_manager import cache_manager
import logging
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_all_stocks():
    """获取所有A股股票列表"""
    try:
        df = ak.stock_zh_a_spot_em()
        return df['代码'].tolist() if df is not None and not df.empty else []
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}")
        return []

def warm_stock_data(symbol: str):
    """预热单个股票的数据"""
    try:
        # 获取财务指标数据
        df = ak.stock_financial_analysis_indicator(symbol=symbol)
        if df is not None and not df.empty:
            cache_manager.write_cache('financial_indicators', symbol, df)
            logger.info(f"更新财务指标缓存: {symbol}")

        # 获取资产负债表
        df = ak.stock_balance_sheet_by_report_em(symbol=symbol)
        if df is not None and not df.empty:
            cache_manager.write_cache('financial_statement_balance', symbol, df)
            logger.info(f"更新资产负债表缓存: {symbol}")

        # 获取利润表
        df = ak.stock_profit_sheet_by_report_em(symbol=symbol)
        if df is not None and not df.empty:
            cache_manager.write_cache('financial_statement_profit', symbol, df)
            logger.info(f"更新利润表缓存: {symbol}")

        # 获取现金流量表
        df = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
        if df is not None and not df.empty:
            cache_manager.write_cache('financial_statement_cashflow', symbol, df)
            logger.info(f"更新现金流量表缓存: {symbol}")

        return True
    except Exception as e:
        logger.error(f"更新股票 {symbol} 缓存失败: {e}")
        return False

def warm_cache(max_workers=5):
    """预热所有股票数据的缓存"""
    start_time = time.time()
    logger.info("开始预热数据缓存...")

    # 获取所有股票代码
    symbols = get_all_stocks()
    if not symbols:
        logger.error("获取股票列表失败")
        return

    logger.info(f"共找到 {len(symbols)} 只股票")
    success_count = 0
    failed_count = 0

    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_symbol = {executor.submit(warm_stock_data, symbol): symbol 
                          for symbol in symbols}
        
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                success = future.result()
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"处理股票 {symbol} 时出错: {e}")
                failed_count += 1

    end_time = time.time()
    duration = end_time - start_time

    logger.info(f"""
缓存预热完成:
- 总用时: {duration:.2f} 秒
- 成功: {success_count} 只
- 失败: {failed_count} 只
- 总计: {len(symbols)} 只
""")

def update_realtime_cache():
    """更新实时数据缓存"""
    try:
        df = ak.stock_zh_a_spot_em()
        if df is not None and not df.empty:
            # 按股票代码分组存储
            for symbol, group in df.groupby('代码'):
                cache_manager.write_cache('stock_spot', symbol, group)
            logger.info(f"更新实时行情缓存: {len(df)} 只股票")
            return True
    except Exception as e:
        logger.error(f"更新实时行情缓存失败: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="数据缓存预热工具")
    parser.add_argument("--type", choices=['all', 'realtime'], 
                    default='all', help="预热类型: all=所有数据, realtime=仅实时数据")
    parser.add_argument("--workers", type=int, default=5,
                    help="并行处理的线程数")
    args = parser.parse_args()

    if args.type == 'all':
        warm_cache(max_workers=args.workers)
    else:
        update_realtime_cache()
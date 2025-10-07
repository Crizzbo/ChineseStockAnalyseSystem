import akshare as ak

class Akshare:
    
    def parse_to_csv(data,csv_name):
        data.to_csv(csv_name, index=False)

#上海证券交易所-股票数据总貌
#限量: 单次返回最近交易日的股票数据总貌(当前交易日的数据需要交易所收盘后统计)
#接口: stock_sse_summary
#目标地址: http://www.sse.com.cn/market/stockdata/statistic/
    def get_stock_sse_summary():
        stock_sse_summary_df = ak.stock_sse_summary()
        return stock_sse_summary_df
    
# 接口: stock_szse_summary

# 目标地址: http://www.szse.cn/market/overview/index.html

# 描述: 深圳证券交易所-市场总貌-证券类别统计

# 限量: 单次返回指定 date 的市场总貌数据-证券类别统计(当前交易日的数据需要交易所收盘后统计)
    def get_stock_szse_summary(date):
        stock_zsse_summary_df = ak.stock_szse_summary(date)
        return stock_zsse_summary_df

# 接口: stock_szse_sector_summary

# 目标地址: http://docs.static.szse.cn/www/market/periodical/month/W020220511355248518608.html

# 描述: 深圳证券交易所-统计资料-股票行业成交数据

# 限量: 单次返回指定 symbol 和 date 的统计资料-股票行业成交数据
# symbol="当月"; choice of {"当月", "当年"}   
# date="202501"; 年月
    def get_stock_szse_sector_summary(symbol,date):
        stock_szse_sector_summary_df = ak.stock_szse_sector_summary(symbol, date)
        return stock_szse_sector_summary_df
    
# 上海证券交易所-每日概况
# 接口: stock_sse_deal_daily

# 目标地址: http://www.sse.com.cn/market/stockdata/overview/day/

# 描述: 上海证券交易所-数据-股票数据-成交概况-股票成交概况-每日股票情况

# 限量: 单次返回指定日期的每日概况数据, 当前交易日数据需要在收盘后获取; 注意仅支持获取在 20211227（包含）之后的数据    
    def get_stock_sse_deal_daily(date):
        stock_sse_deal_daily_df = ak.stock_sse_deal_daily(date)
        return stock_sse_deal_daily_df
    

# 个股信息查询-东财
# 接口: stock_individual_info_em

# 目标地址: http://quote.eastmoney.com/concept/sh603777.html?from=classic

# 描述: 东方财富-个股-股票信息

# 限量: 单次返回指定 symbol 的个股信息    
    def get_stock_individual_info_em(symbol,timeout):
        stock_individual_info_em_df = ak.stock_individual_info_em(symbol,timeout)
        return stock_individual_info_em_df

# 个股信息查询-雪球
# 接口: stock_individual_basic_info_xq

# 目标地址: https://xueqiu.com/snowman/S/SH601127/detail#/GSJJ

# 描述: 雪球财经-个股-公司概况-公司简介

# 限量: 单次返回指定 symbol 的个股信息  
    def get_stock_individual_basic_info_xq_df(symbol):
        stock_individual_basic_info_xq_df = ak.stock_individual_basic_info_xq(symbol)
        return stock_individual_basic_info_xq_df
    
# 行情报价
# 接口: stock_bid_ask_em

# 目标地址: https://quote.eastmoney.com/sz000001.html

# 描述: 东方财富-行情报价

# 限量: 单次返回指定股票的行情报价数据
    def get_stock_bid_ask_em_df(symbol):
        stock_bid_ask_em_df = ak.stock_bid_ask_em(symbol)
        return stock_bid_ask_em_df
    
# 实时行情数据-东财
# 沪深京 A 股
# 接口: stock_zh_a_spot_em

# 目标地址: https://quote.eastmoney.com/center/gridlist.html#hs_a_board

# 描述: 东方财富网-沪深京 A 股-实时行情数据

# 限量: 单次返回所有沪深京 A 股上市公司的实时行情数据
    def get_stock_zh_a_spot_em_df():
        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        return stock_zh_a_spot_em_df

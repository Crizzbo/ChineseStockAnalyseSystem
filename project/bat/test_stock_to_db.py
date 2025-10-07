from stock_to_db import Akshare as stock

a = stock.get_stock_bid_ask_em_df("601933")
a.to_csv('所有沪深京 A 股上市公司的实时行情数据.csv', index=False)
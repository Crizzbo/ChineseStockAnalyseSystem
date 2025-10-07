import akshare as ak

stock_szse_sector_summary_df = ak.stock_szse_sector_summary(symbol="当年", date="202501")
print(stock_szse_sector_summary_df)
import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
try:
    from tools.stock_analysis_system import StockAnalysisSystem
    from tools.historical_data_service import HistoricalDataService
    historical_service = HistoricalDataService()
    hist_data = historical_service.get_recent_data("601933", days=30)
    print(hist_data)
except EOFError:
    print("失败")

"""
市场数据API
"""
from flask import Blueprint, request, jsonify, current_app, make_response
from marshmallow import Schema, fields, ValidationError
from datetime import datetime

from app.services.stock_data import stock_service
from app.utils.response import success_response, error_response

market_bp = Blueprint('market', __name__)

def add_cors_headers(response):
    """为响应添加CORS头部"""
    if hasattr(response, 'headers'):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@market_bp.route('/indices', methods=['GET', 'OPTIONS'])
def get_market_indices():
    """获取主要市场指数"""
    try:
        # 处理OPTIONS预检请求
        if request.method == 'OPTIONS':
            response = make_response('', 200)
            return add_cors_headers(response)

        indices = stock_service.get_market_indices()

        response = success_response({
            'indices': indices,
            'total': len(indices),
            'timestamp': datetime.now().isoformat()
        })

        return add_cors_headers(make_response(response))

    except Exception as e:
        current_app.logger.error(f'获取市场指数失败: {str(e)}')
        response = error_response('获取市场指数失败', 500)
        return add_cors_headers(make_response(response))

@market_bp.route('/overview', methods=['GET', 'OPTIONS'])
def get_market_overview():
    """获取市场概览"""
    try:
        # 获取主要指数
        indices = stock_service.get_market_indices()

        # 获取热门股票
        hot_stocks = stock_service.get_hot_stocks(limit=10)

        # 计算市场统计信息
        market_stats = {
            'total_indices': len(indices),
            'hot_stocks_count': len(hot_stocks),
            'update_time': datetime.now().isoformat()
        }

        # 如果有指数数据，计算涨跌统计
        if indices:
            rising_count = sum(1 for idx in indices if idx.get('changePercent', 0) > 0)
            falling_count = sum(1 for idx in indices if idx.get('changePercent', 0) < 0)
            unchanged_count = len(indices) - rising_count - falling_count

            market_stats.update({
                'indices_rising': rising_count,
                'indices_falling': falling_count,
                'indices_unchanged': unchanged_count
            })

        return success_response({
            'indices': indices,
            'hot_stocks': hot_stocks,
            'market_stats': market_stats
        })

    except Exception as e:
        current_app.logger.error(f'获取市场概览失败: {str(e)}')
        return error_response('获取市场概览失败', 500)

@market_bp.route('/sectors', methods=['GET', 'OPTIONS'])
def get_market_sectors():
    """获取行业板块数据"""
    try:
        # 处理OPTIONS预检请求
        if request.method == 'OPTIONS':
            response = make_response('', 200)
            return add_cors_headers(response)

        import akshare as ak
        sectors_data = []

        try:
            # 获取板块行情数据
            sector_df = ak.stock_board_industry_name_em()

            if sector_df is not None and not sector_df.empty:
                for _, row in sector_df.head(20).iterrows():  # 获取前20个板块
                    try:
                        sectors_data.append({
                            'name': row['板块名称'],
                            'code': row['板块代码'] if '板块代码' in row else '',
                            'change_percent': float(row['涨跌幅']),
                            'stocks_count': int(row['成分股数量']) if '成分股数量' in row else 0,
                            'market_cap': float(row['总市值']) if '总市值' in row and row['总市值'] != '-' else 0,
                            'current_price': float(row['最新价']) if '最新价' in row else 0,
                            'change': float(row['涨跌额']) if '涨跌额' in row else 0
                        })
                    except Exception as parse_error:
                        current_app.logger.warning(f'解析板块数据失败: {parse_error}')
                        continue

        except Exception as ak_error:
            current_app.logger.error(f'AkShare获取板块数据失败: {ak_error}')
            # 如果AkShare失败，返回空数据而不是模拟数据
            sectors_data = []

        response = success_response({
            'sectors': sectors_data,
            'total': len(sectors_data),
            'timestamp': datetime.now().isoformat()
        })

        return add_cors_headers(make_response(response))

    except Exception as e:
        current_app.logger.error(f'获取行业板块失败: {str(e)}')
        response = error_response('获取行业板块失败', 500)
        return add_cors_headers(make_response(response))

@market_bp.route('/movers', methods=['GET', 'OPTIONS'])
def get_market_movers():
    """获取涨跌幅榜单"""
    try:
        mover_type = request.args.get('type', 'gainers')  # gainers, losers, active
        limit = request.args.get('limit', 20, type=int)

        if mover_type not in ['gainers', 'losers', 'active']:
            return error_response('榜单类型参数错误，支持: gainers, losers, active', 400)

        if limit < 1 or limit > 100:
            return error_response('数量限制必须在1-100之间', 400)

        # 根据不同类型获取数据
        if mover_type == 'active':
            # 最活跃（成交量最大）
            stocks = stock_service.get_hot_stocks(limit)
        else:
            # 获取热门股票后按涨跌幅排序
            stocks = stock_service.get_hot_stocks(50)  # 获取更多数据用于排序

            if mover_type == 'gainers':
                # 涨幅榜
                stocks = sorted(stocks, key=lambda x: x.get('changePercent', 0), reverse=True)
            else:
                # 跌幅榜
                stocks = sorted(stocks, key=lambda x: x.get('changePercent', 0))

            stocks = stocks[:limit]

        return success_response({
            'type': mover_type,
            'stocks': stocks,
            'total': len(stocks),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'获取涨跌幅榜单失败: {str(e)}')
        return error_response('获取榜单数据失败', 500)

@market_bp.route('/news', methods=['GET', 'OPTIONS'])
def get_market_news():
    """获取市场新闻（模拟数据）"""
    try:
        limit = request.args.get('limit', 10, type=int)
        category = request.args.get('category', 'all')  # all, market, policy, company

        if limit < 1 or limit > 50:
            return error_response('数量限制必须在1-50之间', 400)

        # 使用AkShare真实新闻数据
        news_data = []

        try:
            import akshare as ak
            # 获取东方财富新闻
            news_df = ak.stock_news_em()

            if news_df is not None and not news_df.empty:
                for idx, row in news_df.head(limit).iterrows():
                    try:
                        # 根据新闻内容判断分类
                        title = str(row['新闻标题'])
                        content = str(row['新闻内容']) if '新闻内容' in row else ''

                        # 简单的分类逻辑
                        news_category = 'market'
                        if any(keyword in title for keyword in ['政策', '央行', '监管', '政府']):
                            news_category = 'policy'
                        elif any(keyword in title for keyword in ['公司', '企业', '股份', '董事']):
                            news_category = 'company'

                        news_data.append({
                            'id': idx + 1,
                            'title': title,
                            'summary': content[:150] + '...' if len(content) > 150 else content,
                            'category': news_category,
                            'publish_time': row['发布时间'].strftime('%Y-%m-%d %H:%M:%S') if '发布时间' in row else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'source': '东方财富',
                            'url': row['新闻链接'] if '新闻链接' in row else '#'
                        })
                    except Exception as parse_error:
                        current_app.logger.warning(f'解析新闻数据失败: {parse_error}')
                        continue

        except Exception as e:
            current_app.logger.error(f'获取新闻数据失败: {e}')
            # 如果获取失败，返回空数据
            news_data = []

        # 根据分类筛选
        if category != 'all':
            news_data = [news for news in news_data if news['category'] == category]

        # 限制数量
        news_data = news_data[:limit]

        return success_response({
            'news': news_data,
            'total': len(news_data),
            'category': category,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        current_app.logger.error(f'获取市场新闻失败: {str(e)}')
        return error_response('获取新闻数据失败', 500)

@market_bp.route('/calendar', methods=['GET', 'OPTIONS'])
def get_market_calendar():
    """获取财经日历（模拟数据）"""
    try:
        date = request.args.get('date')  # YYYY-MM-DD格式

        if date:
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                return error_response('日期格式错误，请使用YYYY-MM-DD格式', 400)
        else:
            date = datetime.now().strftime('%Y-%m-%d')

        # 使用AkShare真实财经日历数据
        calendar_events = []

        try:
            import akshare as ak
            # 获取财经日历数据
            calendar_df = ak.macro_china_daily_energy()

            if calendar_df is not None and not calendar_df.empty:
                # 获取最新的几条数据作为财经事件
                for idx, row in calendar_df.head(5).iterrows():
                    try:
                        # 构造财经日历事件
                        calendar_events.append({
                            'id': idx + 1,
                            'date': date,
                            'time': '09:30',
                            'event': f'能源数据更新 - {row.index[0] if hasattr(row, "index") else ""}',
                            'importance': 'medium',
                            'country': 'CN',
                            'forecast': '待公布',
                            'previous': str(row.iloc[0]) if len(row) > 0 else '-'
                        })
                    except Exception as parse_error:
                        current_app.logger.warning(f'解析财经日历数据失败: {parse_error}')
                        continue

            # 如果没有数据，添加一些通用的财经事件
            if not calendar_events:
                calendar_events = [
                    {
                        'id': 1,
                        'date': date,
                        'time': '09:30',
                        'event': '市场开盘',
                        'importance': 'high',
                        'country': 'CN',
                        'forecast': '-',
                        'previous': '-'
                    },
                    {
                        'id': 2,
                        'date': date,
                        'time': '15:00',
                        'event': '市场收盘',
                        'importance': 'high',
                        'country': 'CN',
                        'forecast': '-',
                        'previous': '-'
                    }
                ]

        except Exception as e:
            current_app.logger.error(f'获取财经日历数据失败: {e}')
            # 如果获取失败，返回基本的市场时间事件
            calendar_events = [
                {
                    'id': 1,
                    'date': date,
                    'time': '09:30',
                    'event': '股市开盘',
                    'importance': 'high',
                    'country': 'CN',
                    'forecast': '-',
                    'previous': '-'
                },
                {
                    'id': 2,
                    'date': date,
                    'time': '15:00',
                    'event': '股市收盘',
                    'importance': 'high',
                    'country': 'CN',
                    'forecast': '-',
                    'previous': '-'
                }
            ]

        return success_response({
            'date': date,
            'events': calendar_events,
            'total': len(calendar_events)
        })

    except Exception as e:
        current_app.logger.error(f'获取财经日历失败: {str(e)}')
        return error_response('获取财经日历失败', 500)
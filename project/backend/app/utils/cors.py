"""
CORS工具函数
"""
from functools import wraps
from flask import make_response, jsonify

def add_cors_headers(f):
    """为路由添加CORS头部的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 处理OPTIONS预检请求
        from flask import request
        if request.method == 'OPTIONS':
            response = make_response('', 200)
        else:
            result = f(*args, **kwargs)
            if hasattr(result, 'get_json'):
                # 如果是Flask响应对象
                response = result
            else:
                # 如果是普通返回值，创建响应
                response = make_response(result)

        # 添加CORS头部
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    return decorated_function
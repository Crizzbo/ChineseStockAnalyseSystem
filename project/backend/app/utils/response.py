"""
统一响应格式
"""
from flask import jsonify
from typing import Any, Dict, Optional

def success_response(data: Any = None, status_code: int = 200, message: str = "操作成功") -> tuple:
    """成功响应"""
    response_data = {
        "code": 0,
        "success": True,
        "message": message,
        "data": data,
        "timestamp": None
    }

    if isinstance(data, dict) and 'message' in data:
        response_data['message'] = data['message']

    return jsonify(response_data), status_code

def error_response(message: str, status_code: int = 400, error_code: str = None, data: Any = None) -> tuple:
    """错误响应"""
    response_data = {
        "code": error_code or status_code,
        "success": False,
        "message": message,
        "data": data,
        "timestamp": None
    }

    return jsonify(response_data), status_code

def paginated_response(items: list, total: int, page: int, per_page: int,
                      message: str = "获取数据成功") -> tuple:
    """分页响应"""
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages

    data = {
        "items": items,
        "pagination": {
            "total": total,
            "total_pages": total_pages,
            "current_page": page,
            "per_page": per_page,
            "has_prev": has_prev,
            "has_next": has_next,
            "prev_page": page - 1 if has_prev else None,
            "next_page": page + 1 if has_next else None
        }
    }

    return success_response(data, message=message)

# HTTP状态码常量
class StatusCode:
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500

# 错误码常量
class ErrorCode:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
"""
全局错误处理器
"""
from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException
from marshmallow import ValidationError
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import JWTExtendedException
import traceback

def register_error_handlers(app):
    """注册全局错误处理器"""

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        """处理数据验证错误"""
        return jsonify({
            "code": 400,
            "success": False,
            "message": "数据验证失败",
            "errors": e.messages,
            "timestamp": None
        }), 400

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_exceptions(error):
        """处理JWT相关错误"""
        return jsonify({
            "code": 401,
            "success": False,
            "message": "认证失败: " + str(error),
            "timestamp": None
        }), 401

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """处理HTTP异常"""
        return jsonify({
            "code": e.code,
            "success": False,
            "message": e.description,
            "timestamp": None
        }), e.code

    @app.errorhandler(404)
    def handle_not_found(e):
        """处理404错误"""
        return jsonify({
            "code": 404,
            "success": False,
            "message": "请求的资源不存在",
            "timestamp": None
        }), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        """处理方法不允许错误"""
        return jsonify({
            "code": 405,
            "success": False,
            "message": "请求方法不被允许",
            "timestamp": None
        }), 405

    @app.errorhandler(500)
    def handle_internal_server_error(e):
        """处理内部服务器错误"""
        # 记录详细错误信息到日志
        current_app.logger.error(f'服务器内部错误: {str(e)}')
        current_app.logger.error(traceback.format_exc())

        return jsonify({
            "code": 500,
            "success": False,
            "message": "服务器内部错误，请稍后重试",
            "timestamp": None
        }), 500

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        """处理其他未捕获的异常"""
        # 记录异常详情
        current_app.logger.error(f'未处理的异常: {str(e)}')
        current_app.logger.error(traceback.format_exc())

        # 在开发环境下显示详细错误信息
        if app.debug:
            return jsonify({
                "code": 500,
                "success": False,
                "message": f"服务器错误: {str(e)}",
                "traceback": traceback.format_exc(),
                "timestamp": None
            }), 500

        return jsonify({
            "code": 500,
            "success": False,
            "message": "服务器内部错误，请稍后重试",
            "timestamp": None
        }), 500
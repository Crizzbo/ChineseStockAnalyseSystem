"""
用户相关API
"""
from flask import Blueprint, request, jsonify, current_app, make_response
from marshmallow import Schema, fields, ValidationError
from datetime import datetime

from app.models.user import User
from app.models.user_preferences import UserPreferences
from app.utils.response import success_response, error_response
from app import db

user_bp = Blueprint('user', __name__)

def add_cors_headers(response):
    """为响应添加CORS头部"""
    if hasattr(response, 'headers'):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

class UserPreferencesSchema(Schema):
    """用户偏好设置验证模式"""
    theme = fields.Str(required=False, validate=lambda x: x in ['light', 'dark', 'auto'])
    language = fields.Str(required=False, validate=lambda x: x in ['zh', 'en'])
    notifications = fields.Dict(required=False)
    display = fields.Dict(required=False)
    trading = fields.Dict(required=False)

@user_bp.route('/preferences', methods=['GET', 'OPTIONS'])
def get_user_preferences():
    """获取用户偏好设置"""
    try:
        # 处理OPTIONS预检请求
        if request.method == 'OPTIONS':
            response = make_response('', 200)
            return add_cors_headers(response)

        # 模拟用户ID (在实际应用中应该从JWT或session中获取)
        user_id = 1

        # 获取或创建用户偏好设置
        preferences = UserPreferences.get_or_create_for_user(user_id)

        response = success_response({
            'preferences': preferences.to_dict(),
            'timestamp': datetime.now().isoformat()
        })

        return add_cors_headers(make_response(response))

    except Exception as e:
        current_app.logger.error(f'获取用户偏好设置失败: {str(e)}')
        response = error_response('获取用户偏好设置失败', 500)
        return add_cors_headers(make_response(response))

@user_bp.route('/preferences', methods=['POST', 'PUT'])
def update_user_preferences():
    """更新用户偏好设置"""
    try:
        # 验证请求数据
        schema = UserPreferencesSchema()
        try:
            validated_data = schema.load(request.json or {})
        except ValidationError as err:
            return add_cors_headers(make_response(error_response('数据验证失败', 400, err.messages)))

        # 模拟用户ID (在实际应用中应该从JWT或session中获取)
        user_id = 1

        # 获取或创建用户偏好设置
        preferences = UserPreferences.get_or_create_for_user(user_id)

        # 更新偏好设置
        preferences.update_preferences(validated_data)

        try:
            db.session.commit()
        except Exception as db_error:
            db.session.rollback()
            current_app.logger.error(f'数据库更新失败: {str(db_error)}')
            response = error_response('保存设置失败', 500)
            return add_cors_headers(make_response(response))

        response = success_response({
            'preferences': preferences.to_dict(),
            'message': '设置保存成功',
            'timestamp': datetime.now().isoformat()
        })

        return add_cors_headers(make_response(response))

    except Exception as e:
        current_app.logger.error(f'更新用户偏好设置失败: {str(e)}')
        response = error_response('更新用户偏好设置失败', 500)
        return add_cors_headers(make_response(response))

@user_bp.route('/preferences/reset', methods=['POST', 'OPTIONS'])
def reset_user_preferences():
    """重置用户偏好设置为默认值"""
    try:
        # 处理OPTIONS预检请求
        if request.method == 'OPTIONS':
            response = make_response('', 200)
            return add_cors_headers(response)

        # 模拟用户ID (在实际应用中应该从JWT或session中获取)
        user_id = 1

        # 获取用户偏好设置
        preferences = UserPreferences.query.filter_by(user_id=user_id).first()

        if preferences:
            # 删除现有设置
            db.session.delete(preferences)

        # 创建新的默认设置
        new_preferences = UserPreferences(user_id=user_id)
        db.session.add(new_preferences)

        try:
            db.session.commit()
        except Exception as db_error:
            db.session.rollback()
            current_app.logger.error(f'数据库重置失败: {str(db_error)}')
            response = error_response('重置设置失败', 500)
            return add_cors_headers(make_response(response))

        response = success_response({
            'preferences': new_preferences.to_dict(),
            'message': '设置已重置为默认值',
            'timestamp': datetime.now().isoformat()
        })

        return add_cors_headers(make_response(response))

    except Exception as e:
        current_app.logger.error(f'重置用户偏好设置失败: {str(e)}')
        response = error_response('重置用户偏好设置失败', 500)
        return add_cors_headers(make_response(response))

@user_bp.route('/profile', methods=['GET', 'OPTIONS'])
def get_user_profile():
    """获取用户基本信息"""
    try:
        # 处理OPTIONS预检请求
        if request.method == 'OPTIONS':
            response = make_response('', 200)
            return add_cors_headers(response)

        # 模拟用户ID (在实际应用中应该从JWT或session中获取)
        user_id = 1

        # 获取用户信息
        user = User.query.get(user_id)
        if not user:
            response = error_response('用户不存在', 404)
            return add_cors_headers(make_response(response))

        # 获取用户偏好设置
        preferences = UserPreferences.get_or_create_for_user(user_id)

        response = success_response({
            'user': user.to_dict(),
            'preferences': preferences.to_dict(),
            'timestamp': datetime.now().isoformat()
        })

        return add_cors_headers(make_response(response))

    except Exception as e:
        current_app.logger.error(f'获取用户信息失败: {str(e)}')
        response = error_response('获取用户信息失败', 500)
        return add_cors_headers(make_response(response))

@user_bp.route('/profile', methods=['PUT'])
def update_user_profile():
    """更新用户基本信息"""
    try:
        # 模拟用户ID (在实际应用中应该从JWT或session中获取)
        user_id = 1

        # 获取用户信息
        user = User.query.get(user_id)
        if not user:
            response = error_response('用户不存在', 404)
            return add_cors_headers(make_response(response))

        # 获取请求数据
        data = request.json or {}

        # 更新用户信息
        if 'nickname' in data:
            user.nickname = data['nickname']
        if 'avatar' in data:
            user.avatar = data['avatar']

        user.updated_at = datetime.utcnow()

        try:
            db.session.commit()
        except Exception as db_error:
            db.session.rollback()
            current_app.logger.error(f'数据库更新失败: {str(db_error)}')
            response = error_response('更新用户信息失败', 500)
            return add_cors_headers(make_response(response))

        response = success_response({
            'user': user.to_dict(),
            'message': '用户信息更新成功',
            'timestamp': datetime.now().isoformat()
        })

        return add_cors_headers(make_response(response))

    except Exception as e:
        current_app.logger.error(f'更新用户信息失败: {str(e)}')
        response = error_response('更新用户信息失败', 500)
        return add_cors_headers(make_response(response))
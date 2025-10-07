"""
用户认证API
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from werkzeug.exceptions import BadRequest
from marshmallow import Schema, fields, ValidationError
from datetime import timedelta
import re

from app import db, jwt
from app.models.user import User
from app.utils.response import success_response, error_response

auth_bp = Blueprint('auth', __name__)

# JWT黑名单存储
blacklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """检查JWT是否在黑名单中"""
    jti = jwt_payload['jti']
    return jti in blacklist

# 请求验证模式
class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=lambda x: len(x) >= 3 and len(x) <= 20)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 6)
    nickname = fields.Str(allow_none=True, validate=lambda x: len(x) <= 50 if x else True)

class LoginSchema(Schema):
    login = fields.Str(required=True)  # 可以是用户名或邮箱
    password = fields.Str(required=True)

class ChangePasswordSchema(Schema):
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=lambda x: len(x) >= 6)

class UpdateProfileSchema(Schema):
    nickname = fields.Str(load_default=None, validate=lambda x: len(x) <= 50 if x else True)
    avatar = fields.Url(load_default=None)

# 工具函数
def validate_password(password):
    """密码强度验证"""
    if len(password) < 6:
        return False, "密码长度至少6位"

    # 检查是否包含至少一个数字和一个字母
    if not re.search(r'\d', password) or not re.search(r'[a-zA-Z]', password):
        return False, "密码必须包含至少一个数字和一个字母"

    return True, ""

def validate_username(username):
    """用户名验证"""
    if len(username) < 3 or len(username) > 20:
        return False, "用户名长度必须在3-20个字符之间"

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "用户名只能包含字母、数字和下划线"

    return True, ""

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        # 验证请求数据
        schema = RegisterSchema()
        data = schema.load(request.json)

        # 额外验证
        username_valid, username_msg = validate_username(data['username'])
        if not username_valid:
            return error_response(username_msg, 400)

        password_valid, password_msg = validate_password(data['password'])
        if not password_valid:
            return error_response(password_msg, 400)

        # 检查用户名和邮箱是否已存在
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()

        if existing_user:
            if existing_user.username == data['username']:
                return error_response('用户名已存在', 409)
            else:
                return error_response('邮箱已被注册', 409)

        # 创建新用户
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            nickname=data.get('nickname')
        )

        db.session.add(user)
        db.session.commit()

        # 创建JWT令牌
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )

        return success_response({
            'message': '注册成功',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 201)

    except ValidationError as e:
        return error_response(f'数据验证失败: {e.messages}', 400)
    except Exception as e:
        current_app.logger.error(f'注册失败: {str(e)}')
        return error_response('注册失败，请稍后重试', 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        # 验证请求数据
        schema = LoginSchema()
        data = schema.load(request.json)

        # 查找用户（支持用户名或邮箱登录）
        login_field = data['login']
        user = User.query.filter(
            (User.username == login_field) | (User.email == login_field)
        ).first()

        if not user or not user.check_password(data['password']):
            return error_response('用户名/邮箱或密码错误', 401)

        if not user.is_active:
            return error_response('账户已被禁用', 403)

        # 更新最后登录时间
        user.update_last_login()

        # 创建JWT令牌
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )

        return success_response({
            'message': '登录成功',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        })

    except ValidationError as e:
        return error_response(f'数据验证失败: {e.messages}', 400)
    except Exception as e:
        current_app.logger.error(f'登录失败: {str(e)}')
        return error_response('登录失败，请稍后重试', 500)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return error_response('用户不存在或已被禁用', 403)

        # 创建新的访问令牌
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )

        return success_response({
            'access_token': access_token
        })

    except Exception as e:
        current_app.logger.error(f'刷新令牌失败: {str(e)}')
        return error_response('刷新令牌失败', 500)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出"""
    try:
        jti = get_jwt()['jti']  # JWT ID

        # 将令牌加入黑名单
        blacklist.add(jti)

        # 如果有Redis，也存储到Redis中
        if redis_client:
            redis_client.setex(f"jwt_blacklist:{jti}", 86400, "true")  # 24小时过期

        return success_response({'message': '登出成功'})

    except Exception as e:
        current_app.logger.error(f'登出失败: {str(e)}')
        return error_response('登出失败', 500)

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户信息"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return error_response('用户不存在', 404)

        return success_response({
            'user': user.to_dict(include_sensitive=True)
        })

    except Exception as e:
        current_app.logger.error(f'获取用户信息失败: {str(e)}')
        return error_response('获取用户信息失败', 500)

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """更新用户信息"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return error_response('用户不存在', 404)

        # 验证请求数据
        schema = UpdateProfileSchema()
        data = schema.load(request.json)

        # 更新用户信息
        if 'nickname' in data and data['nickname'] is not None:
            user.nickname = data['nickname']
        if 'avatar' in data and data['avatar'] is not None:
            user.avatar = data['avatar']

        db.session.commit()

        return success_response({
            'message': '用户信息更新成功',
            'user': user.to_dict(include_sensitive=True)
        })

    except ValidationError as e:
        return error_response(f'数据验证失败: {e.messages}', 400)
    except Exception as e:
        current_app.logger.error(f'更新用户信息失败: {str(e)}')
        return error_response('更新用户信息失败', 500)

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return error_response('用户不存在', 404)

        # 验证请求数据
        schema = ChangePasswordSchema()
        data = schema.load(request.json)

        # 验证旧密码
        if not user.check_password(data['old_password']):
            return error_response('原密码错误', 400)

        # 验证新密码强度
        password_valid, password_msg = validate_password(data['new_password'])
        if not password_valid:
            return error_response(password_msg, 400)

        # 更新密码
        user.set_password(data['new_password'])
        db.session.commit()

        return success_response({'message': '密码修改成功'})

    except ValidationError as e:
        return error_response(f'数据验证失败: {e.messages}', 400)
    except Exception as e:
        current_app.logger.error(f'修改密码失败: {str(e)}')
        return error_response('修改密码失败', 500)

@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    """验证令牌有效性"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_active:
            return error_response('令牌无效', 401)

        return success_response({
            'valid': True,
            'user': user.to_dict()
        })

    except Exception as e:
        return error_response('令牌验证失败', 401)
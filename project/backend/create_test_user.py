#!/usr/bin/env python3
"""
创建测试用户脚本
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User

def create_test_user():
    """创建测试用户"""
    app = create_app()

    with app.app_context():
        try:
            # 检查是否已存在测试用户
            existing_user = User.query.filter_by(username='test').first()
            if existing_user:
                print(f"测试用户已存在:")
                print(f"用户名: {existing_user.username}")
                print(f"邮箱: {existing_user.email}")
                print(f"密码: test123")
                return

            # 创建测试用户
            test_user = User(
                username='test',
                email='test@example.com',
                password='test123',
                nickname='测试用户'
            )
            test_user.is_verified = True  # 设置为已验证

            db.session.add(test_user)
            db.session.commit()

            print("测试用户创建成功!")
            print(f"用户名: test")
            print(f"邮箱: test@example.com")
            print(f"密码: test123")
            print(f"昵称: 测试用户")

        except Exception as e:
            print(f"创建用户失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_test_user()
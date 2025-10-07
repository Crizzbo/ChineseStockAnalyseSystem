"""
Flask应用启动文件
"""
import os
from app import create_app, socketio
from app.utils.database import init_database, create_sample_data

# 创建应用实例
app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.cli.command()
def init_db():
    """初始化数据库"""
    if init_database():
        print("数据库初始化成功")
    else:
        print("数据库初始化失败")

@app.cli.command()
def create_sample():
    """创建示例数据"""
    if create_sample_data():
        print("示例数据创建成功")
    else:
        print("示例数据创建失败")

@app.cli.command()
def reset_db():
    """重置数据库"""
    from app.utils.database import reset_database
    if reset_database():
        print("数据库重置成功")
        if create_sample_data():
            print("示例数据创建成功")
    else:
        print("数据库重置失败")

if __name__ == '__main__':
    # 在开发环境中直接运行
    socketio.run(app,
                debug=app.config.get('DEBUG', False),
                host='0.0.0.0',
                port=5000,
                allow_unsafe_werkzeug=True)
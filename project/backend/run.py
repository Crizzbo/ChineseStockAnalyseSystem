#!/usr/bin/env python
"""
简化的启动脚本
"""
from app import create_app, socketio
import os

app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    socketio.run(
        app,
        debug=app.config.get('DEBUG', False),
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        allow_unsafe_werkzeug=True
    )
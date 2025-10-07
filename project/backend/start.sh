#!/bin/bash

echo "启动股票分析系统后端服务..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装/更新依赖包..."
pip install -r requirements.txt

# 设置环境变量
if [ ! -f ".env" ]; then
    echo "复制环境配置文件..."
    cp .env.example .env
    echo "请编辑 .env 文件配置数据库等连接信息"
    read -p "按 Enter 继续..."
fi

# 初始化数据库
echo "初始化数据库..."
python -c "from app.utils.database import init_database; init_database()"

# 创建示例数据
echo "创建示例数据..."
python -c "from app.utils.database import create_sample_data; create_sample_data()"

# 启动服务
echo "启动Flask应用..."
python run.py
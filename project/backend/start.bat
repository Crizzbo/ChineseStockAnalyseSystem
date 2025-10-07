@echo off
echo 启动股票分析系统后端服务...

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装/更新依赖包...
pip install -r requirements.txt

REM 设置环境变量
if not exist ".env" (
    echo 复制环境配置文件...
    copy .env.example .env
    echo 请编辑 .env 文件配置数据库等连接信息
    pause
)

REM 初始化数据库
echo 初始化数据库...
python -c "from app.utils.database import init_database; init_database()"

REM 创建示例数据
echo 创建示例数据...
python -c "from app.utils.database import create_sample_data; create_sample_data()"

REM 启动服务
echo 启动Flask应用...
python run.py

pause
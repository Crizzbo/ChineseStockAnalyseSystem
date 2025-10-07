# 股票分析系统 - 后端

基于 Python Flask + AkShare 构建的股票分析系统后端服务，提供股票数据获取、用户认证、投资组合管理和实时数据推送功能。

## 主要功能

- 🔐 **用户认证系统**：JWT 令牌认证，支持注册、登录、刷新令牌
- 📊 **股票数据服务**：基于 AkShare 的实时股票数据获取
- 💼 **投资组合管理**：创建和管理个人投资组合，跟踪收益
- ⭐ **自选股功能**：股票收藏和分组管理
- 📈 **技术分析**：股票技术指标计算和分析建议
- 🔄 **实时数据推送**：WebSocket 实时股价和市场数据推送
- 🎯 **市场数据**：主要指数、热门股票、板块数据

## 技术栈

- **框架**：Flask 2.3.3
- **数据库**：SQLAlchemy + PostgreSQL/SQLite
- **缓存**：Redis
- **认证**：Flask-JWT-Extended
- **实时通信**：Flask-SocketIO
- **数据源**：AkShare（中国股票数据）
- **任务队列**：Celery
- **数据分析**：pandas, numpy, TA-Lib

## 项目结构

```
backend/
├── app/                    # 应用主目录
│   ├── __init__.py        # 应用工厂
│   ├── api/               # API 蓝图
│   │   ├── auth.py        # 用户认证
│   │   ├── stocks.py      # 股票数据
│   │   ├── portfolio.py   # 投资组合
│   │   ├── analysis.py    # 股票分析
│   │   └── market.py      # 市场数据
│   ├── models/            # 数据模型
│   │   ├── user.py        # 用户模型
│   │   ├── portfolio.py   # 投资组合模型
│   │   └── watchlist.py   # 自选股模型
│   ├── services/          # 业务逻辑
│   │   └── stock_data.py  # 股票数据服务
│   ├── utils/             # 工具函数
│   │   ├── response.py    # 统一响应格式
│   │   ├── database.py    # 数据库工具
│   │   └── error_handlers.py # 错误处理
│   ├── websocket/         # WebSocket 事件
│   │   └── events.py      # Socket.IO 事件处理
│   └── tasks/             # 后台任务
│       └── scheduler.py   # Celery 任务调度
├── migrations/            # 数据库迁移文件
├── config.py             # 配置文件
├── requirements.txt      # 项目依赖
├── app.py               # 应用启动文件
└── .env.example         # 环境变量示例
```

## 快速开始

### 1. 环境准备

确保已安装：
- Python 3.8+
- Redis 服务器
- PostgreSQL（生产环境）

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\\Scripts\\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 环境配置

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，配置数据库和 Redis 连接
```

### 4. 初始化数据库

```bash
# 初始化数据库迁移
flask db init

# 生成迁移文件
flask db migrate -m "Initial migration"

# 执行迁移
flask db upgrade

# 创建示例数据（可选）
flask create-sample
```

### 5. 启动服务

```bash
# 启动 Redis 服务器（如果未运行）
redis-server

# 启动 Flask 应用
python app.py

# 或使用 Gunicorn（生产环境）
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 --bind 0.0.0.0:5000 app:app
```

### 6. 启动后台任务（可选）

```bash
# 启动 Celery worker
celery -A app.celery worker --loglevel=info

# 启动 Celery beat（定时任务调度）
celery -A app.celery beat --loglevel=info
```

## API 文档

### 认证接口

- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新令牌
- `POST /api/v1/auth/logout` - 用户登出
- `GET /api/v1/auth/profile` - 获取用户信息

### 股票数据接口

- `GET /api/v1/stocks/search?keyword=股票名称` - 搜索股票
- `GET /api/v1/stocks/{symbol}` - 获取股票基本信息
- `GET /api/v1/stocks/{symbol}/history` - 获取历史价格数据
- `GET /api/v1/stocks/{symbol}/technical` - 获取技术指标
- `GET /api/v1/stocks/hot` - 获取热门股票
- `POST /api/v1/stocks/batch` - 批量获取股票信息

### 投资组合接口

- `GET /api/v1/portfolio/` - 获取投资组合列表
- `POST /api/v1/portfolio/` - 创建投资组合
- `GET /api/v1/portfolio/{id}` - 获取投资组合详情
- `POST /api/v1/portfolio/{id}/stocks` - 添加股票到组合
- `PUT /api/v1/portfolio/{id}/stocks/{stock_id}` - 更新持仓信息

### 市场数据接口

- `GET /api/v1/market/indices` - 获取主要指数
- `GET /api/v1/market/overview` - 获取市场概览
- `GET /api/v1/market/movers` - 获取涨跌幅榜单

### WebSocket 事件

客户端可以通过 WebSocket 连接获取实时数据：

```javascript
// 连接到 WebSocket
const socket = io('http://localhost:5000');

// 订阅股票实时数据
socket.emit('subscribe_stock', {
  symbols: ['000001', '600519']
});

// 监听股票数据更新
socket.on('stock_data', (data) => {
  console.log('股票数据更新:', data);
});

// 订阅市场指数
socket.emit('subscribe_market');

// 监听市场数据更新
socket.on('market_data', (data) => {
  console.log('市场数据更新:', data);
});
```

## 数据模型

### 用户模型（User）
- id, username, email, password_hash
- nickname, avatar, is_active, is_verified
- created_at, updated_at, last_login

### 投资组合模型（Portfolio）
- id, name, description, user_id
- total_cost, created_at, updated_at

### 投资组合股票模型（PortfolioStock）
- id, portfolio_id, symbol, name
- shares, avg_cost, created_at, updated_at

### 自选股列表模型（WatchList）
- id, name, description, user_id
- created_at, updated_at

## 部署说明

### Docker 部署

```bash
# 构建镜像
docker build -t stock-analysis-backend .

# 运行容器
docker run -d \
  --name stock-backend \
  -p 5000:5000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/stockdb \
  -e REDIS_URL=redis://redis:6379/0 \
  stock-analysis-backend
```

### 生产环境配置

1. 使用 PostgreSQL 数据库
2. 配置 Redis 集群
3. 使用 Nginx 作为反向代理
4. 配置 SSL 证书
5. 设置日志轮转
6. 配置监控和告警

## 开发说明

### 添加新的 API 接口

1. 在 `app/api/` 目录下创建或编辑蓝图文件
2. 定义请求验证 Schema
3. 实现接口处理函数
4. 在 `app/__init__.py` 中注册蓝图

### 添加新的数据模型

1. 在 `app/models/` 目录下创建模型文件
2. 定义 SQLAlchemy 模型类
3. 生成数据库迁移文件：`flask db migrate`
4. 执行迁移：`flask db upgrade`

### 添加新的后台任务

1. 在 `app/tasks/scheduler.py` 中定义任务函数
2. 配置任务调度时间
3. 重启 Celery 服务

## 常见问题

**Q: AkShare 数据获取失败怎么办？**
A: 检查网络连接，AkShare 依赖于外部数据源，可能存在访问限制。

**Q: Redis 连接失败？**
A: 确保 Redis 服务器正在运行，检查连接配置。

**Q: 数据库连接错误？**
A: 检查数据库配置和连接字符串，确保数据库服务正常运行。

**Q: WebSocket 连接失败？**
A: 确保防火墙允许 WebSocket 连接，检查 CORS 配置。

## 许可证

MIT License

## 贡献

欢迎提交 Pull Request 和 Issue！
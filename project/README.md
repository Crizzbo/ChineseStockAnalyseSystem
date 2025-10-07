# 股票分析系统

一个基于 React + Flask 的现代化股票分析系统，提供实时股票数据、技术分析、投资组合管理和市场资讯等功能。

![系统架构](docs/images/architecture.png)

## ✨ 主要功能

### 📊 股票数据与分析
- **实时股票数据**：基于 AkShare 的中国 A 股实时行情数据
- **历史数据查询**：支持日线、周线、月线等不同周期的历史数据
- **技术分析**：MA、RSI、成交量等多种技术指标分析
- **基本面分析**：PE、PB、市值等基本面指标分析
- **趋势分析**：价格趋势、波动率、风险评估
- **相关性分析**：股票间相关性计算和可视化

### 💼 投资组合管理
- **多投资组合支持**：创建和管理多个投资组合
- **持仓跟踪**：实时计算投资收益和风险指标
- **自选股管理**：股票收藏和分组功能
- **收益分析**：投资组合历史收益分析和可视化

### 🔍 市场数据
- **主要指数**：上证指数、深证成指、创业板指等主要指数
- **热门股票**：基于成交量的热门股票排行
- **涨跌幅榜**：实时涨跌幅排行榜
- **板块行情**：行业板块实时涨跌幅排行和分析
- **板块成分股**：板块内股票列表和表现数据
- **板块搜索**：支持板块名称和代码搜索

### 🎯 实时数据推送
- **WebSocket 实时推送**：股价、指数实时数据推送
- **订阅管理**：灵活的数据订阅和取消订阅
- **多设备同步**：支持多设备同时连接

### 👤 用户管理
- **用户认证**：JWT 令牌认证系统
- **个人资料**：用户信息管理
- **数据持久化**：用户数据云端存储

### 🤖 AI投资助手
- **智能对话**：基于自然语言的股票投资咨询
- **股票分析**：AI驱动的个股分析和投资建议
- **市场洞察**：实时市场趋势分析和解读
- **投资组合优化**：AI辅助的资产配置建议
- **风险评估**：智能风险分析和预警
- **学习指导**：投资知识问答和教学

## 🏗️ 技术架构

### 前端技术栈
- **React 18** + **TypeScript** - 现代化前端框架
- **Vite** - 快速构建工具
- **Ant Design** - 企业级 UI 组件库
- **Redux Toolkit** - 状态管理
- **React Router** - 路由管理
- **ECharts** - 数据可视化
- **Socket.IO Client** - WebSocket 实时通信
- **Axios** - HTTP 客户端

### 后端技术栈
- **Python Flask** - 轻量级 Web 框架
- **SQLAlchemy** - ORM 数据库操作
- **PostgreSQL/SQLite** - 关系型数据库
- **Redis** - 缓存和会话存储
- **Flask-JWT-Extended** - JWT 认证
- **Flask-SocketIO** - WebSocket 实时通信
- **AkShare** - 中国股票数据源
- **Celery** - 异步任务队列
- **pandas + numpy** - 数据分析

### 数据源
- **AkShare** - 提供中国 A 股市场数据
- **实时行情数据** - 股价、成交量、市值等
- **历史数据** - 支持多种时间周期
- **基本面数据** - 财务指标、估值指标

## 🚀 快速开始

### 系统要求
- Node.js 16+
- Python 3.8+
- Redis 服务器
- PostgreSQL（生产环境推荐）

### 1. 克隆项目
```bash
git clone https://github.com/your-username/stock-analysis-system.git
cd stock-analysis-system
```

### 2. 启动后端服务
```bash
cd backend

# Windows
start.bat

# Linux/macOS
chmod +x start.sh
./start.sh
```

### 3. 启动前端服务
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用
- 前端地址：http://localhost:5173
- 后端API：http://localhost:5000
- API文档：http://localhost:5000/docs（如果配置了）

## 📁 项目结构

```
stock-analysis-system/
├── frontend/                 # 前端React应用
│   ├── src/
│   │   ├── components/       # 可复用组件
│   │   ├── views/           # 页面视图
│   │   ├── services/        # API服务层
│   │   ├── store/           # Redux状态管理
│   │   ├── hooks/           # 自定义Hooks
│   │   └── utils/           # 工具函数
│   ├── public/              # 静态资源
│   └── package.json
├── backend/                  # 后端Flask应用
│   ├── app/
│   │   ├── api/             # API蓝图
│   │   ├── models/          # 数据模型
│   │   ├── services/        # 业务逻辑
│   │   ├── utils/           # 工具函数
│   │   └── websocket/       # WebSocket事件
│   ├── migrations/          # 数据库迁移
│   ├── config.py            # 配置文件
│   └── requirements.txt     # Python依赖
├── docs/                    # 项目文档
├── docker-compose.yml       # Docker编排
└── README.md               # 项目说明
```

## 🔧 配置说明

### 环境变量配置

#### 前端配置（.env）
```env
VITE_API_BASE_URL=http://localhost:5000
VITE_WS_URL=http://localhost:5000
VITE_APP_TITLE=股票分析系统
```

#### 后端配置（.env）
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///stock_analysis.db
REDIS_URL=redis://localhost:6379/0
```

## 📊 功能截图

### 股票搜索与分析
![股票搜索](docs/images/stock-search.png)

### 投资组合管理
![投资组合](docs/images/portfolio.png)

### 技术分析图表
![技术分析](docs/images/technical-analysis.png)

### 市场概览
![市场概览](docs/images/market-overview.png)

## 🧪 测试

### 前端测试
```bash
cd frontend
npm run test
```

### 后端测试
```bash
cd backend
python -m pytest
```

## 📦 部署

### Docker 部署
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 生产环境部署
详见 [部署文档](docs/deployment.md)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📝 开发指南

### 添加新功能
1. **前端组件**：在 `frontend/src/components/` 下创建组件
2. **API 接口**：在 `frontend/src/services/` 下添加服务函数
3. **后端接口**：在 `backend/app/api/` 下添加蓝图路由
4. **数据模型**：在 `backend/app/models/` 下定义模型

### 代码规范
- **前端**：使用 ESLint + Prettier
- **后端**：使用 Black + Flake8
- **提交**：使用 Conventional Commits 规范

## ⚠️ 注意事项

1. **数据源限制**：AkShare 数据源可能存在访问频率限制
2. **网络环境**：部分数据源需要良好的网络环境
3. **生产环境**：生产环境建议使用 PostgreSQL 数据库
4. **安全配置**：生产环境请修改默认的密钥配置

## 🐛 常见问题

**Q: AkShare 数据获取失败？**
A: 检查网络连接和防火墙设置，AkShare 需要访问外部数据源。

**Q: WebSocket 连接失败？**
A: 确认后端服务正常启动，检查端口是否被占用。

**Q: 数据库连接错误？**
A: 检查数据库配置和连接字符串，确保数据库服务正常运行。

更多问题请查看 [FAQ文档](docs/faq.md)

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 🙏 致谢

- [AkShare](https://github.com/akfamily/akshare) - 提供中国股票数据
- [Ant Design](https://ant.design/) - 优秀的UI组件库
- [ECharts](https://echarts.apache.org/) - 强大的数据可视化库
- [Flask](https://flask.palletsprojects.com/) - 简洁的Python Web框架

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 项目 Issues: [GitHub Issues](https://github.com/your-username/stock-analysis-system/issues)
- 邮箱: your-email@example.com

---

⭐ 如果这个项目对你有帮助，请给个星标支持一下！
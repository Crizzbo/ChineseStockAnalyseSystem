# API接口规范 - 实际实现版本

> **说明**: 本文档仅包含已实现的API接口,与实际后端代码保持一致

## 1. 通用响应格式

### 1.1 成功响应
```json
{
  "code": 0,
  "success": true,
  "message": "操作成功",
  "data": { },
  "timestamp": null
}
```

### 1.2 错误响应
```json
{
  "code": 400,
  "success": false,
  "message": "错误信息",
  "data": null,
  "timestamp": null
}
```

## 2. 认证接口 (`/api/v1/auth`)

### 2.1 用户注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "nickname": "测试用户"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "nickname": "测试用户"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

### 2.2 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "password123"
}
```

### 2.3 刷新Token
```http
POST /api/v1/auth/refresh
Authorization: Bearer {refresh_token}
```

### 2.4 用户登出
```http
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

### 2.5 获取当前用户信息
```http
GET /api/v1/auth/me
Authorization: Bearer {access_token}
```

## 3. 股票数据接口 (`/api/v1/stocks`)

### 3.1 股票搜索
```http
GET /api/v1/stocks/search?keyword={keyword}&limit={limit}
```

**Parameters:**
- `keyword` (required): 搜索关键词
- `limit` (optional): 返回数量,默认10,最大50

**Response:**
```json
{
  "success": true,
  "data": {
    "stocks": [
      {
        "symbol": "000001",
        "name": "平安银行",
        "currentPrice": 12.34,
        "change": 0.29,
        "changePercent": 2.41
      }
    ],
    "total": 1,
    "keyword": "平安"
  }
}
```

### 3.2 获取股票基本信息
```http
GET /api/v1/stocks/{symbol}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "stock": {
      "symbol": "000001",
      "name": "平安银行",
      "currentPrice": 12.34,
      "change": 0.29,
      "changePercent": 2.41,
      "volume": 58293847,
      "high": 12.45,
      "low": 11.98,
      "open": 12.05
    }
  }
}
```

### 3.3 获取股票历史数据
```http
GET /api/v1/stocks/{symbol}/history?period={period}&start_date={start}&end_date={end}&limit={limit}
```

**Parameters:**
- `period`: daily | weekly | monthly (默认daily)
- `start_date`: 开始日期 YYYY-MM-DD
- `end_date`: 结束日期 YYYY-MM-DD
- `limit`: 数据条数 (默认250,最大1000)

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "000001",
    "period": "daily",
    "data": [
      {
        "date": "2024-01-15",
        "open": 12.05,
        "high": 12.45,
        "low": 11.98,
        "close": 12.34,
        "volume": 58293847
      }
    ],
    "total": 30
  }
}
```

### 3.4 获取技术指标
```http
GET /api/v1/stocks/{symbol}/technical?period={period}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "symbol": "000001",
    "period": "daily",
    "indicators": {
      "ma5": 12.25,
      "ma10": 12.18,
      "rsi": 62.34
    }
  }
}
```

### 3.5 获取热门股票
```http
GET /api/v1/stocks/hot?limit={limit}
```

### 3.6 批量获取股票信息
```http
POST /api/v1/stocks/batch
Content-Type: application/json

{
  "symbols": ["000001", "600036", "000002"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "stocks": [...],
    "total": 3,
    "failed_symbols": [],
    "success_count": 3,
    "failed_count": 0
  }
}
```

### 3.7 获取实时行情
```http
GET /api/v1/stocks/realtime/{symbols}
```
**说明**: symbols用逗号分隔,如 `000001,600036`

### 3.8 股票对比
```http
POST /api/v1/stocks/compare
Content-Type: application/json

{
  "symbols": ["000001", "600036"]
}
```

## 4. 投资组合接口 (`/api/v1/portfolio`)

### 4.1 获取投资组合列表
```http
GET /api/v1/portfolio/?page={page}&per_page={per_page}
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "data": [
      {
        "id": 1,
        "name": "我的投资组合",
        "description": "长期价值投资",
        "user_id": 1,
        "total_value": 125600,
        "total_cost": 100000,
        "total_gain_loss": 25600,
        "total_gain_loss_percent": 25.6,
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-20T15:45:00",
        "stocks": [...]
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 20
  }
}
```

### 4.2 创建投资组合
```http
POST /api/v1/portfolio/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "我的投资组合",
  "description": "长期价值投资"
}
```

### 4.3 获取投资组合详情
```http
GET /api/v1/portfolio/{portfolio_id}
Authorization: Bearer {access_token}
```

### 4.4 更新投资组合
```http
PUT /api/v1/portfolio/{portfolio_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "新名称",
  "description": "新描述"
}
```

### 4.5 删除投资组合
```http
DELETE /api/v1/portfolio/{portfolio_id}
Authorization: Bearer {access_token}
```

### 4.6 向投资组合添加股票
```http
POST /api/v1/portfolio/{portfolio_id}/stocks
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "symbol": "000001",
  "name": "平安银行",
  "shares": 1000,
  "avg_cost": 12.50
}
```

### 4.7 更新投资组合中的股票
```http
PUT /api/v1/portfolio/{portfolio_id}/stocks/{stock_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "shares": 1500,
  "avg_cost": 12.30
}
```

### 4.8 从投资组合中删除股票
```http
DELETE /api/v1/portfolio/{portfolio_id}/stocks/{stock_id}
Authorization: Bearer {access_token}
```

## 5. 自选股接口 (`/api/v1/portfolio/watchlists`)

### 5.1 获取自选股列表
```http
GET /api/v1/portfolio/watchlists
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "watchlists": [
      {
        "id": 1,
        "name": "我的自选",
        "description": "重点关注",
        "stock_count": 5,
        "stocks": [...]
      }
    ],
    "total": 1
  }
}
```

### 5.2 创建自选股列表
```http
POST /api/v1/portfolio/watchlists
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "我的自选",
  "description": "重点关注"
}
```

### 5.3 向自选股添加股票
```http
POST /api/v1/portfolio/watchlists/{watchlist_id}/stocks
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "symbol": "000001",
  "name": "平安银行",
  "notes": "关注买入时机"
}
```

### 5.4 从自选股删除股票
```http
DELETE /api/v1/portfolio/watchlists/{watchlist_id}/stocks/{stock_id}
Authorization: Bearer {access_token}
```

## 6. 市场数据接口 (`/api/v1/market`)

### 6.1 获取市场概况
```http
GET /api/v1/market/summary
```

**Response:**
```json
{
  "success": true,
  "data": {
    "indices": [
      {
        "code": "000001",
        "name": "上证指数",
        "value": 3021.45,
        "change": 15.67,
        "changePercent": 0.52
      }
    ],
    "stats": {
      "total_stocks": 5234,
      "rising": 2876,
      "falling": 1998,
      "unchanged": 360
    }
  }
}
```

### 6.2 获取涨跌幅榜
```http
GET /api/v1/market/ranking?type={type}&limit={limit}
```

**Parameters:**
- `type`: gainers | losers | volume | turnover
- `limit`: 返回数量 (默认20,最大100)

## 7. 板块数据接口 (`/api/v1/sectors`)

### 7.1 获取板块列表
```http
GET /api/v1/sectors
```

### 7.2 获取板块详情
```http
GET /api/v1/sectors/{sector_code}
```

### 7.3 获取板块成分股
```http
GET /api/v1/sectors/{sector_code}/stocks?page={page}&per_page={per_page}
```

## 8. AI聊天接口 (`/api/v1/ai`)

### 8.1 发送聊天消息
```http
POST /api/v1/ai/chat
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "message": "分析一下平安银行",
  "context": {
    "stock_symbol": "000001"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "基于最新数据分析...",
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### 8.2 获取聊天历史
```http
GET /api/v1/ai/history?page={page}&per_page={per_page}
Authorization: Bearer {access_token}
```

## 9. 用户设置接口 (`/api/v1/user`)

### 9.1 获取用户偏好设置
```http
GET /api/v1/user/preferences
Authorization: Bearer {access_token}
```

### 9.2 更新用户偏好设置
```http
PUT /api/v1/user/preferences
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "theme": "dark",
  "language": "zh-CN",
  "notifications": {
    "price_alert": true,
    "news_alert": false
  }
}
```

### 9.3 更新用户资料
```http
PUT /api/v1/user/profile
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "nickname": "新昵称",
  "email": "newemail@example.com"
}
```

### 9.4 修改密码
```http
PUT /api/v1/user/password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "old_password": "old123",
  "new_password": "new456"
}
```

## 10. 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/Token无效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 409 | 资源冲突 (如重名) |
| 500 | 服务器内部错误 |

## 11. 请求头规范

所有需要认证的请求必须携带:
```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

---

*本文档与实际后端实现保持一致,更新日期: 2025-10-07*

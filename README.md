# AI 掘金头条新闻系统

全栈新闻资讯 App，支持新闻浏览、搜索、收藏、历史记录及用户管理。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.11+、FastAPI、SQLAlchemy（异步）、MySQL、Redis |
| 前端 | Vue 3、TypeScript、Pinia、Vue Router、Vite |

## 项目结构

```
News_APP/
├── backend-FastAPI/       # 后端
│   ├── config/            # 数据库、Redis、环境变量配置
│   ├── crud/              # 数据库操作层
│   ├── migrations/        # 数据库迁移脚本
│   ├── models/            # SQLAlchemy ORM 模型
│   ├── routers/           # 路由层（接口定义）
│   ├── schemas/           # Pydantic 请求/响应模型
│   ├── static/            # 静态文件（用户头像等）
│   ├── utils/             # 工具函数（鉴权、限流、统一响应）
│   ├── main.py            # 应用入口
│   ├── requirements.txt   # 依赖列表
│   └── .env.example       # 环境变量模板
└── frontend-Vue/          # 前端
    ├── src/
    │   ├── api/           # API 请求封装
    │   ├── stores/        # Pinia 状态管理
    │   ├── views/         # 页面组件
    │   └── router/        # 路由配置
    └── .env.example       # 前端环境变量模板
```

## 本地运行

### 前置条件

- Python 3.11+
- Node.js 18+（pnpm）
- MySQL 8.0+
- Redis 6+（可选，缓存功能，不启动时自动降级）

### 1. 克隆项目

```bash
git clone https://github.com/your-username/News_APP.git
cd News_APP
```

### 2. 配置后端环境变量

```bash
cd backend-FastAPI
cp .env.example .env
# 编辑 .env，填入你的数据库密码和相关配置
```

`.env` 关键配置项：

```env
DATABASE_URL=mysql+aiomysql://root:your_password@localhost:3306/news_app?charset=utf8mb4
REDIS_HOST=localhost
REDIS_PORT=6379
ALLOWED_ORIGINS=http://localhost:5173
BASE_URL=http://localhost:8000
```

### 3. 初始化数据库

```bash
# 在 MySQL 中创建数据库
mysql -u root -p -e "CREATE DATABASE news_app CHARACTER SET utf8mb4;"

# 执行迁移（建表）
python migrations/migrate.py

# 查看迁移状态
python migrations/migrate.py --status
```

### 4. 启动后端

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务（默认 8000 端口）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

接口文档：http://localhost:8000/docs

### 5. 配置并启动前端

```bash
cd ../frontend-Vue
cp .env.example .env

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

前端地址：http://localhost:5173

## 主要接口

| 模块 | 方法 | 路径 | 说明 |
|---|---|---|---|
| 用户 | POST | /api/user/register | 注册 |
| 用户 | POST | /api/user/login | 登录 |
| 用户 | POST | /api/user/logout | 登出 |
| 用户 | GET | /api/user/info | 获取当前用户信息 |
| 用户 | PUT | /api/user/update | 修改用户信息 |
| 用户 | PUT | /api/user/password | 修改密码 |
| 用户 | POST | /api/user/avatar | 上传头像 |
| 新闻 | GET | /api/news/categories | 新闻分类列表 |
| 新闻 | GET | /api/news/list | 新闻列表（分页） |
| 新闻 | GET | /api/news/detail | 新闻详情 |
| 新闻 | GET | /api/news/search | 关键词搜索 |
| 收藏 | GET/POST/DELETE | /api/favorite/\* | 收藏管理 |
| 历史 | GET/POST/DELETE | /api/history/\* | 浏览历史管理 |

## 安全说明

- 登录/注册接口有限流保护（每 IP 每分钟最多 10 次）
- 密码使用 bcrypt 哈希存储
- Token 登出后立即失效
- 敏感配置全部通过 `.env` 管理，不进入版本控制

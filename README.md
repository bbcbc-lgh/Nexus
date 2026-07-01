# Nexus AI 新闻聚合系统

Nexus 是一个面向 AI 与技术资讯阅读场景的新闻聚合系统。系统由 FastAPI 后端和 Vue 3 前端组成，支持多来源资讯采集、中文字段处理、新闻检索、收藏、稍后阅读、评论、投票、阅读统计和作者关注等功能。

当前仓库已经精简为可运行的前后端源码，不再包含历史迁移脚本、后端设计文档、后端测试用例、示例 SQL 数据文件和独立的前端 README。数据库结构需要使用现有环境中的数据库，或根据 `backend/models/` 中的 SQLAlchemy ORM 模型在外部维护。

## 功能特性

- 多源资讯采集：支持 RSS、arXiv、Hacker News JSON API 和 GitHub API。
- 新闻入库与展示：后端提供列表、详情、搜索、作者文章、推荐和手动刷新接口。
- 中文阅读体验：模型字段支持中文标题、摘要和正文，前端优先展示适合中文用户阅读的内容。
- 用户体系：支持注册、登录、资料更新、密码修改、头像上传和退出登录。
- 阅读互动：支持收藏文件夹、稍后阅读、阅读历史、阅读进度、评论、投票和阅读统计。
- 个性化能力：结合阅读行为、主题标签和作者关注提供推荐与发现入口。
- 自动采集任务：后端启动时可按 `ENABLE_AUTO_FETCH` 控制是否开启后台采集。

## 技术栈

后端：

- Python
- FastAPI
- SQLAlchemy Async
- aiomysql / PyMySQL
- MySQL
- httpx
- feedparser
- Redis 可选配置

前端：

- Vue 3
- TypeScript
- Vite
- Pinia
- Vue Router

## 项目结构

```text
.
├── backend/
│   ├── config/              # 数据库、环境变量和缓存配置
│   ├── crawler/             # RSS、Hacker News、arXiv、GitHub 采集器
│   ├── crud/                # 数据访问逻辑
│   ├── models/              # SQLAlchemy ORM 模型
│   ├── routers/             # FastAPI 路由
│   ├── schemas/             # Pydantic Schema
│   ├── utils/               # 响应、鉴权、翻译和内容处理工具
│   ├── requirements.txt
│   └── main.py              # FastAPI 应用入口
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/             # 前端 API client
│   │   ├── assets/          # 全局样式和静态资源
│   │   ├── router/          # 页面路由
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── utils/           # 来源元信息等工具
│   │   └── views/           # 页面视图
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 本地运行

### 1. 准备数据库

创建 MySQL 数据库，例如：

```sql
CREATE DATABASE nexus_ai_news DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

当前仓库不再提供 `backend/migrations/` 和 `backend/data.sql`。请确保目标数据库中已经存在与 `backend/models/` 匹配的表结构，或在部署流程中用外部脚本维护表结构。

### 2. 配置后端环境变量

复制并填写 `backend/.env.example`：

```powershell
cd backend
copy .env.example .env
```

关键配置：

```env
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/nexus_ai_news?charset=utf8mb4
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8100
ENABLE_AUTO_FETCH=false
BASE_URL=http://localhost:8000
```

说明：

- `DATABASE_URL` 用于后端连接 MySQL。
- `ENABLE_AUTO_FETCH=false` 适合本地调试，可避免启动时立即执行后台采集。
- `ALLOWED_ORIGINS` 需要包含前端开发服务器地址。
- `BASE_URL` 用于生成头像等静态资源的完整访问地址。

### 3. 启动后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
$env:ENABLE_AUTO_FETCH = "false"
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

接口文档地址：

```text
http://127.0.0.1:8000/docs
```

### 4. 启动前端

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

前端地址：

```text
http://127.0.0.1:5173
```

开发环境下，Vite 会把 `/api` 和 `/static` 代理到 `VITE_API_TARGET`，默认是 `http://localhost:8000`。如需指定后端地址，可在 `frontend/.env` 中配置：

```env
VITE_API_TARGET=http://127.0.0.1:8000
VITE_API_BASE_URL=
```

## 常用接口

新闻与搜索：

```text
GET  /api/news/categories
GET  /api/news/list
GET  /api/news/detail?id=1
GET  /api/news/search
POST /api/news/refresh
GET  /api/news/author/{author_name}
GET  /api/news/recommend
```

用户与互动：

```text
POST /api/user/register
POST /api/user/login
GET  /api/user/info
PUT  /api/user/update
PUT  /api/user/password
POST /api/user/logout
POST /api/user/avatar

POST   /api/favorite/add
GET    /api/favorite/list
DELETE /api/favorite/remove

POST   /api/queue/add
GET    /api/queue/list
DELETE /api/queue/remove

GET  /api/reading/stats
POST /api/reading/behavior

GET    /api/comments
POST   /api/comments
DELETE /api/comments/{comment_id}

POST /api/news/{news_id}/vote
GET  /api/news/{news_id}/vote
```

## 构建与基础验证

后端语法检查：

```powershell
cd backend
python -m py_compile main.py
```

前端生产构建：

```powershell
cd frontend
npm run build
```

运行级验证可以启动后端和前端后访问：

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/openapi.json
http://127.0.0.1:8000/api/news/categories
http://127.0.0.1:5173/
```

`npm run build` 会生成 `frontend/dist/`，后端启动可能生成 `backend/static/` 和 `__pycache__/`。这些都是运行或构建产物，已在 `.gitignore` 中忽略。

## 维护说明

- 当前仓库以应用源码为主，数据库迁移、初始化数据和自动化测试目录已从仓库中移除。
- 如后续重新引入迁移或测试，请同步恢复 README 中的初始化和测试说明。
- 后端模块按路由、Schema、ORM、CRUD、采集器和工具层拆分，新增功能时优先沿用现有目录边界。
- 前端路由集中在 `frontend/src/router/index.ts`，接口封装集中在 `frontend/src/api/`。

# Nexus AI 新闻聚合系统

Nexus 是一个面向技术资讯阅读场景的 AI 新闻聚合系统。系统会从 OpenAI News、arXiv、Hacker News、GitHub AI、InfoQ 等多个来源采集 AI/科技资讯，完成清洗、去重、中文翻译、全文搜索、推荐分发和用户互动，帮助用户高效浏览持续更新的技术内容。

项目采用 FastAPI + MySQL + Vue 3 + TypeScript 构建，后端负责采集、翻译、入库、检索和用户相关 API，前端提供新闻列表、详情阅读、搜索筛选、收藏、稍后阅读、评论、投票、阅读统计和作者关注等功能。

## 功能特性

- 多源资讯采集：支持 RSS、arXiv、Hacker News JSON API 和 GitHub API。
- 入库清洗去重：基于 `source_url`、标题 hash 和标题归一化策略减少重复内容。
- AI 中文翻译：入库时生成中文标题、摘要和正文，并对翻译失败、空正文、异常响应做降级处理。
- 新闻阅读体验：支持来源切换、分页加载、详情阅读、原文链接、相关新闻和阅读进度。
- 搜索与发现：支持 MySQL 全文索引搜索、搜索历史、搜索建议和高级筛选。
- 个性化能力：结合阅读历史、收藏行为、主题标签和作者关注提供推荐内容。
- 用户互动：支持注册登录、收藏文件夹、稍后阅读、评论、点赞/点踩和阅读统计。
- 自动采集任务：应用启动后可按固定间隔后台采集，也支持通过接口手动触发刷新。

## 技术栈

后端：

- Python
- FastAPI
- SQLAlchemy Async
- aiomysql / PyMySQL
- MySQL
- httpx
- feedparser
- pytest

前端：

- Vue 3
- TypeScript
- Vite
- Pinia
- Vue Router

外部服务：

- Anthropic/OpenAI 兼容翻译接口
- RSS / arXiv / Hacker News / GitHub API
- Redis（可选，用于扩展采集调度或缓存能力）

## 数据源

当前项目支持的数据源包括：

| 来源标识 | 名称 | 类型 |
|---|---|---|
| `openai` | OpenAI News | RSS |
| `google_ai` | Google AI Blog | RSS |
| `huggingface` | Hugging Face Blog | RSS |
| `arxiv_ai` | arXiv AI | API / RSS |
| `techcrunch_ai` | TechCrunch AI | RSS |
| `mit` | MIT Technology Review | RSS |
| `infoq_cn` | InfoQ 中文 | RSS |
| `hackernews` | Hacker News | JSON API |
| `github_ai` | GitHub AI | GitHub API |

数据源配置存储在 `news_source` 表中，前端通过 `/api/news/categories` 获取启用来源。

## 项目结构

```text
.
├── backend/
│   ├── config/              # 数据库、环境变量和缓存配置
│   ├── crawler/             # RSS、Hacker News、arXiv、GitHub 采集器
│   ├── crud/                # 数据访问逻辑
│   ├── docs/                # 后端与接口设计文档
│   ├── migrations/          # 数据库迁移脚本
│   ├── models/              # SQLAlchemy ORM 模型
│   ├── routers/             # FastAPI 路由
│   ├── schemas/             # Pydantic Schema
│   ├── tests/               # pytest 测试
│   ├── utils/               # 响应、鉴权、翻译和内容清洗工具
│   ├── requirements.txt
│   └── main.py              # FastAPI 应用入口
└── frontend/
    ├── src/
    │   ├── api/             # 前端 API client
    │   ├── router/          # 页面路由
    │   ├── stores/          # Pinia 状态管理
    │   ├── utils/           # 来源元信息等工具
    │   └── views/           # 页面视图
    └── package.json
```

## 本地运行

### 1. 准备数据库

创建 MySQL 数据库，例如：

```sql
CREATE DATABASE nexus_ai_news DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 配置后端环境变量

在 `backend/.env` 中配置：

```env
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/nexus_ai_news?charset=utf8mb4
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8100
ENABLE_AUTO_FETCH=true

ANTHROPIC_API_KEY=
ANTHROPIC_BASE_URL=

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

说明：

- `DATABASE_URL` 是必需配置，用于后端和迁移脚本连接 MySQL。
- `ANTHROPIC_API_KEY` 和 `ANTHROPIC_BASE_URL` 用于翻译链路；未配置时，翻译相关能力会受限。
- `ENABLE_AUTO_FETCH=false` 可关闭应用启动后的自动采集任务。

### 3. 安装并启动后端

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python migrations\migrate.py
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端接口文档：

```text
http://localhost:8000/docs
```

### 4. 安装并启动前端

```powershell
cd frontend
pnpm install
pnpm run dev
```

前端默认地址：

```text
http://localhost:5173
```

如需指定后端地址，可在 `frontend/.env` 中配置：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 常用接口

新闻与搜索：

```text
GET  /api/news/categories
GET  /api/news/list
GET  /api/news/detail
GET  /api/news/search
POST /api/news/refresh
GET  /api/news/recommend
```

用户与互动：

```text
POST /api/user/register
POST /api/user/login
GET  /api/user/info
POST /api/favorite/add
GET  /api/favorite/list
POST /api/queue/add
GET  /api/queue/list
GET  /api/reading/stats
POST /api/comments
POST /api/news/{news_id}/vote
```

## 手动采集

应用启动后会根据 `ENABLE_AUTO_FETCH` 决定是否自动采集。也可以通过接口手动触发：

```text
POST /api/news/refresh
```

如果需要在命令行直接执行采集逻辑，可以参考 `backend/crawler/` 中的各类采集器实现。

## 测试与构建

后端测试：

```powershell
cd backend
.\.venv\Scripts\activate
python -m pytest
```

前端构建：

```powershell
cd frontend
pnpm run build
```

## 设计要点

- 后端模块按路由、Schema、ORM、CRUD、采集器和工具层拆分，方便扩展新数据源或新交互模块。
- 采集链路包含失败重试、内容过滤和翻译降级，避免异常数据直接影响展示体验。
- 搜索优先使用 MySQL 全文索引，在不可用时可降级到普通匹配逻辑。
- 前端以移动端阅读体验为优先，同时适配桌面端列表和详情阅读场景。

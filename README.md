# Nexus AI 新闻系统

一个个人自用的 AI 资讯聚合 App。后端使用 FastAPI + MySQL，前端使用 Vue 3 + TypeScript + Pinia + Vite。系统会定时采集多个 AI/科技信息源，入库时翻译为中文，并提供阅读、搜索、收藏、稍后阅读、评论、投票、阅读统计等功能。

## 当前状态

- 项目定位：单人自用，不走多人产品化和 PR 流程。
- 后端：FastAPI 异步接口，MySQL 持久化，轻量迁移脚本。
- 前端：移动端优先，同时适配桌面侧边栏。
- 采集：应用启动后自动后台采集，每 2 小时运行一次，也支持手动触发。
- 翻译：入库时调用 Haiku 模型翻译，已加入翻译前言/模型自言自语过滤。
- 搜索：MySQL 全文索引优先，LIKE 降级。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python、FastAPI、SQLAlchemy Async、aiomysql、MySQL |
| 前端 | Vue 3、TypeScript、Pinia、Vue Router、Vite |
| 采集 | httpx、feedparser、asyncio 后台任务 |
| 翻译 | Haiku 兼容接口，使用 httpx 直连代理 |
| 测试 | pytest、FastAPI 集成测试 |

## 数据源

数据源配置存放在 `news_source` 表，接口 `/api/news/categories` 会读取启用源。当前已支持：

| source_platform | 名称 | 类型 |
|---|---|---|
| `openai` | OpenAI News | RSS |
| `google_ai` | Google AI Blog | RSS |
| `huggingface` | Hugging Face Blog | RSS |
| `arxiv_ai` | arXiv AI | API/RSS |
| `techcrunch_ai` | TechCrunch AI | RSS |
| `mit` | MIT Tech Review | RSS |
| `infoq_cn` | InfoQ 中文 | RSS |
| `hackernews` | Hacker News | JSON API |
| `github_ai` | GitHub AI | GitHub API |

## 目录结构

```text
News_APP/
├── backend/
│   ├── config/              # 数据库、环境变量等配置
│   ├── crawler/             # RSS/HN/arXiv/GitHub 采集器
│   ├── crud/                # 数据库访问逻辑
│   ├── migrations/          # 轻量迁移器与版本脚本
│   ├── models/              # SQLAlchemy ORM 模型
│   ├── routers/             # FastAPI 路由
│   ├── schemas/             # Pydantic schema
│   ├── tests/               # pytest 测试
│   ├── utils/               # 响应、安全、翻译、内容清洗
│   └── main.py              # FastAPI 入口，含定时采集任务
├── frontend/
│   ├── src/api/             # API client
│   ├── src/router/          # 路由
│   ├── src/stores/          # Pinia store
│   ├── src/utils/           # 来源元信息等工具
│   └── src/views/           # 页面
├── UpGrade.md               # 功能升级路线图与暂缓记录
└── README.md
```

## 本地运行

### 1. 后端环境

```powershell
cd E:\News_APP\backend
.venv\Scripts\activate
pip install -r requirements.txt
```

后端配置来自 `backend/.env`。不要把 `.env` 提交进仓库。常用配置：

```env
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/news_app?charset=utf8mb4
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:8100
ENABLE_AUTO_FETCH=true
ANTHROPIC_API_KEY=your_key
ANTHROPIC_BASE_URL=https://your-proxy.example.com/v1
```

注意：翻译代理的 `base_url` 如果已经包含 `/v1`，代码会按当前项目逻辑处理；不要改用 Anthropic SDK，避免重复拼接 `/v1`。

### 2. 数据库迁移

```powershell
cd E:\News_APP\backend
python migrations\migrate.py
```

迁移脚本规则见 [backend/migrations/README.md](backend/migrations/README.md)。

### 3. 启动后端

```powershell
cd E:\News_APP\backend
.venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

接口文档：http://localhost:8000/docs

### 4. 启动前端

```powershell
cd E:\News_APP\frontend
pnpm install
pnpm run dev
```

前端地址：http://localhost:5173

## 手动采集

应用启动后会自动采集。如果想手动触发全部采集：

```powershell
cd E:\News_APP\backend
.venv\Scripts\activate
@'
import asyncio
from config.database_conf import AsyncSessionLocal
from crawler.rss_fetcher import fetch_all_rss
from crawler.hn_fetcher import fetch_hn
from crawler.arxiv_fetcher import fetch_arxiv
from crawler.github_fetcher import fetch_github_ai

async def main():
    async with AsyncSessionLocal() as db:
        await fetch_all_rss(db)
        await fetch_hn(db)
        await fetch_arxiv(db)
        await fetch_github_ai(db)

asyncio.run(main())
'@ | python -
```

也可以在前端点击刷新按钮，调用 `/api/news/refresh` 后台触发。

## 常用命令

```powershell
# 后端测试
cd E:\News_APP\backend
.venv\Scripts\activate
python -m pytest

# 前端生产构建
cd E:\News_APP\frontend
pnpm run build

# 查看数据库迁移状态
cd E:\News_APP\backend
python migrations\migrate.py --status
```

## 主要能力

- 新闻列表：按来源切换、分页加载、搜索与筛选。
- 新闻详情：中文优先展示、原文链接、相关推荐、阅读进度、字号调节。
- 用户系统：注册、登录、资料更新、头像上传、退出后 token 失效。
- 收藏系统：收藏、取消收藏、收藏文件夹、清空当前文件夹。
- 稍后阅读：加入队列、移出队列。
- 搜索：搜索历史、搜索建议、高级筛选。
- 个性化：阅读行为统计、标签、作者关注、基础推荐。
- 互动：评论、点赞/踩。

## 重要注意事项

- 不要提交 `.env`。
- 不要在代码里硬编码数据库密码、API key 或 token。
- MySQL `ADD COLUMN` 不支持 `IF NOT EXISTS`，迁移脚本要查 `information_schema`。
- `user.id` 与 `news.id` 是 `INT UNSIGNED`，新增外键字段必须保持同类型。
- `source_platform` 是来源标识，前端颜色与标签映射在 `frontend/src/utils/sourceMeta.ts`。
- 当前是个人项目，很多面向多人协作、外部部署、灰度发布、Sentry/CDN 的能力在 `UpGrade.md` 中继续暂缓。

## Git 工作流

当前项目直接使用 `master`：

```powershell
git add <指定文件>
git commit -m "type: 中文说明"
git push origin master
```

不要使用 `git add .`，避免把 `.env` 或临时文件带进提交。

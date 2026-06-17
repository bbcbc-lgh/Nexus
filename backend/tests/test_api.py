"""
核心 API 集成测试
覆盖：新闻列表/详情/搜索、用户注册/登录/信息、收藏、稍后阅读
"""
import asyncio
import sys
import pytest

# Windows proactor event loop 与 aiomysql 不兼容，强制用 SelectorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

pytestmark = pytest.mark.asyncio

CODE_OK = 200  # success_response 使用 code=200 表示成功


# ── 新闻 API ──────────────────────────────────────────────────────────────────

async def test_news_categories(client):
    resp = await client.get("/api/news/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == CODE_OK
    assert isinstance(data["data"], list)


async def test_news_list_default(client):
    resp = await client.get("/api/news/list")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == CODE_OK
    assert "list" in data["data"]
    assert "total" in data["data"]


async def test_news_list_pagination(client):
    resp = await client.get("/api/news/list?page=1&pageSize=5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == CODE_OK
    assert len(data["data"]["list"]) <= 5


async def test_news_list_by_source(client):
    resp = await client.get("/api/news/list?source=hackernews&page=1&pageSize=5")
    assert resp.status_code == 200
    assert resp.json()["code"] == CODE_OK


async def test_news_detail_not_found(client):
    resp = await client.get("/api/news/detail?id=999999999")
    # 404 或 code != 200
    if resp.status_code == 200:
        assert resp.json()["code"] != CODE_OK
    else:
        assert resp.status_code == 404


async def test_news_search_with_query(client):
    resp = await client.get("/api/news/search?keyword=AI")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == CODE_OK
    assert "list" in data["data"]


async def test_news_author_not_found(client):
    resp = await client.get("/api/news/author/nonexistent_author_xyz_99999")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == CODE_OK
    assert data["data"]["total"] == 0


# ── 用户 API ──────────────────────────────────────────────────────────────────

async def test_register_and_login(auth_client):
    resp = await auth_client.get("/api/user/info")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == CODE_OK
    assert "username" in data["data"]


async def test_register_duplicate_username(client):
    import uuid
    from tests.conftest import TEST_PREFIX, cleanup_test_users
    username = f"{TEST_PREFIX}{uuid.uuid4().hex[:8]}"

    await client.post("/api/user/register", json={"username": username, "password": "Test1234!"})
    resp = await client.post("/api/user/register", json={"username": username, "password": "Test1234!"})

    # 重复注册应该失败
    if resp.status_code == 200:
        assert resp.json()["code"] != CODE_OK
    else:
        assert resp.status_code in (400, 409)

    await cleanup_test_users(username)


async def test_login_wrong_password(client):
    import uuid
    from tests.conftest import TEST_PREFIX, cleanup_test_users
    username = f"{TEST_PREFIX}{uuid.uuid4().hex[:8]}"

    await client.post("/api/user/register", json={"username": username, "password": "Test1234!"})
    resp = await client.post("/api/user/login", json={"username": username, "password": "wrongpass"})

    if resp.status_code == 200:
        assert resp.json()["code"] != CODE_OK
    else:
        assert resp.status_code in (401, 400)

    await cleanup_test_users(username)


async def test_me_unauthenticated(client):
    resp = await client.get("/api/user/info")
    # 没有 Authorization header 时 FastAPI 返回 422（必填参数缺失）或 401
    assert resp.status_code in (401, 403, 422)


# ── 收藏 API ──────────────────────────────────────────────────────────────────

async def test_favorite_requires_auth(client):
    # 没有 Authorization header，FastAPI 返回 422
    resp = await client.get("/api/favorite/list")
    assert resp.status_code in (401, 403, 422)


async def test_favorite_flow(auth_client):
    news_resp = await auth_client.get("/api/news/list?page=1&pageSize=1")
    news_list = news_resp.json()["data"]["list"]
    if not news_list:
        pytest.skip("没有新闻数据，跳过收藏测试")

    news_id = news_list[0]["id"]

    # 检查收藏状态
    check = await auth_client.get(f"/api/favorite/check?newsId={news_id}")
    assert check.json()["code"] == CODE_OK

    # 添加收藏
    add = await auth_client.post("/api/favorite/add", json={"newsId": news_id})
    assert add.status_code == 200
    assert add.json()["code"] == CODE_OK

    # 收藏列表包含该新闻
    lst = await auth_client.get("/api/favorite/list")
    ids = [item["id"] for item in lst.json()["data"]["list"]]
    assert news_id in ids

    # 取消收藏
    remove = await auth_client.delete("/api/favorite/remove", params={"newsId": news_id})
    assert remove.status_code == 200


# ── 稍后阅读 API ──────────────────────────────────────────────────────────────

async def test_queue_flow(auth_client):
    news_resp = await auth_client.get("/api/news/list?page=1&pageSize=1")
    news_list = news_resp.json()["data"]["list"]
    if not news_list:
        pytest.skip("没有新闻数据，跳过稍后阅读测试")

    news_id = news_list[0]["id"]

    add = await auth_client.post("/api/queue/add", json={"newsId": news_id})
    assert add.status_code == 200

    lst = await auth_client.get("/api/queue/list")
    ids = [item["id"] for item in lst.json()["data"]["list"]]
    assert news_id in ids

    remove = await auth_client.delete("/api/queue/remove", params={"newsId": news_id})
    assert remove.status_code == 200


# ── 搜索历史 API ──────────────────────────────────────────────────────────────

async def test_search_history_flow(auth_client):
    add = await auth_client.post("/api/search/history", json={"query": "test_query_integration"})
    assert add.status_code == 200

    lst = await auth_client.get("/api/search/history")
    queries = [h["query"] for h in lst.json()["data"]["list"]]
    assert "test_query_integration" in queries

    clear = await auth_client.delete("/api/search/history")
    assert clear.status_code == 200


async def test_search_suggestions(client):
    resp = await client.get("/api/search/history/suggestions?q=AI")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == CODE_OK
    assert isinstance(data["data"], list)


# ── 扩展功能 API ─────────────────────────────────────────────────────────────

async def _first_news(auth_client):
    news_resp = await auth_client.get("/api/news/list?page=1&pageSize=1")
    news_list = news_resp.json()["data"]["list"]
    if not news_list:
        pytest.skip("没有新闻数据，跳过依赖新闻的测试")
    return news_list[0]


async def test_vote_flow(auth_client):
    news_id = (await _first_news(auth_client))["id"]

    add = await auth_client.post(f"/api/news/{news_id}/vote", json={"value": 1})
    assert add.status_code == 200
    assert add.json()["code"] == CODE_OK
    assert add.json()["data"]["userVote"] == 1

    state = await auth_client.get(f"/api/news/{news_id}/vote")
    assert state.json()["data"]["userVote"] == 1

    remove = await auth_client.post(f"/api/news/{news_id}/vote", json={"value": 0})
    assert remove.status_code == 200


async def test_comment_flow(auth_client):
    news_id = (await _first_news(auth_client))["id"]

    created = await auth_client.post("/api/comments", json={"news_id": news_id, "content": "integration comment"})
    assert created.status_code == 200
    assert created.json()["code"] == CODE_OK
    comment_id = created.json()["data"]["id"]

    listing = await auth_client.get("/api/comments", params={"news_id": news_id})
    ids = [item["id"] for item in listing.json()["data"]["list"]]
    assert comment_id in ids

    deleted = await auth_client.delete(f"/api/comments/{comment_id}")
    assert deleted.status_code == 200


async def test_reading_progress_flow(auth_client):
    news_id = (await _first_news(auth_client))["id"]

    saved = await auth_client.post("/api/reading-progress", json={
        "news_id": news_id,
        "progress": 42,
        "last_position": 360,
    })
    assert saved.status_code == 200

    progress = await auth_client.get(f"/api/reading-progress/{news_id}")
    data = progress.json()["data"]
    assert data["progress"] == 42
    assert data["lastPosition"] == 360


async def test_tags_and_recommend(auth_client):
    tags = await auth_client.get("/api/tags")
    assert tags.status_code == 200
    assert isinstance(tags.json(), list)

    rec = await auth_client.get("/api/news/recommend?limit=3")
    assert rec.status_code == 200
    assert rec.json()["code"] == CODE_OK
    assert isinstance(rec.json()["data"], list)


async def test_update_profile_allows_empty_fields(auth_client):
    resp = await auth_client.put("/api/user/update", json={"nickname": "", "bio": "", "gender": "unknown"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["nickname"] == ""
    assert data["bio"] == ""


# ── 关注作者 API ─────────────────────────────────────────────────────────────

async def test_follow_author_flow(auth_client):
    news_resp = await auth_client.get("/api/news/list?page=1&pageSize=10")
    news_list = news_resp.json()["data"]["list"]
    target = next((item for item in news_list if item.get("author")), None)
    if not target:
        pytest.skip("没有可关注的作者")

    author = target["author"]

    check = await auth_client.get("/api/follow/author/check", params={"author": author})
    assert check.json()["code"] == CODE_OK

    add = await auth_client.post("/api/follow/author", json={"author": author})
    assert add.status_code == 200
    assert add.json()["code"] == CODE_OK

    lst = await auth_client.get("/api/follow/authors")
    authors = [h["author"] for h in lst.json()["data"]["list"]]
    assert author in authors

    remove = await auth_client.delete("/api/follow/author", params={"author": author})
    assert remove.status_code == 200

    lst2 = await auth_client.get("/api/follow/authors")
    authors2 = [h["author"] for h in lst2.json()["data"]["list"]]
    assert author not in authors2

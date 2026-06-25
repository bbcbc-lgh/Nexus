"""
Extend news_source with metadata needed for scalable source management.
"""
import sqlalchemy as sa


async def _column_exists(conn, column: str) -> bool:
    result = await conn.execute(sa.text("""
        SELECT COUNT(*)
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'news_source'
          AND COLUMN_NAME = :column
    """), {"column": column})
    return result.scalar() > 0


async def _add_column(conn, column: str, ddl: str):
    if not await _column_exists(conn, column):
        await conn.execute(sa.text(f"ALTER TABLE news_source ADD COLUMN {ddl}"))


async def upgrade(conn):
    await conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS news_source (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            platform VARCHAR(50) NOT NULL,
            feed_url VARCHAR(500) NOT NULL,
            fetch_interval INT DEFAULT 120,
            enabled TINYINT DEFAULT 1,
            last_fetched_at DATETIME NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """))

    await _add_column(conn, "source_type", "source_type VARCHAR(20) NOT NULL DEFAULT 'rss' COMMENT 'rss/api/arxiv/community'")
    await _add_column(conn, "source_group", "source_group VARCHAR(30) NOT NULL DEFAULT 'media' COMMENT 'official/media/research/community'")
    await _add_column(conn, "trust_tier", "trust_tier TINYINT NOT NULL DEFAULT 2 COMMENT '1=highest trust'")
    await _add_column(conn, "language", "language VARCHAR(10) NOT NULL DEFAULT 'en'")
    await _add_column(conn, "region", "region VARCHAR(20) NOT NULL DEFAULT 'global'")
    await _add_column(conn, "requires_ai_filter", "requires_ai_filter TINYINT NOT NULL DEFAULT 0")
    await _add_column(conn, "error_count", "error_count INT NOT NULL DEFAULT 0")
    await _add_column(conn, "last_error", "last_error VARCHAR(500) NULL")
    await _add_column(conn, "updated_at", "updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")

    await conn.execute(sa.text("""
        UPDATE news_source
        SET source_type = CASE WHEN platform = 'hackernews' THEN 'api' ELSE 'rss' END,
            source_group = CASE
                WHEN platform IN ('openai', 'google_ai') THEN 'official'
                WHEN platform = 'hackernews' THEN 'community'
                ELSE 'media'
            END,
            trust_tier = CASE
                WHEN platform IN ('openai', 'google_ai') THEN 1
                WHEN platform = 'mit' THEN 2
                ELSE 3
            END,
            language = 'en',
            region = 'global',
            requires_ai_filter = CASE WHEN platform = 'mit' THEN 1 ELSE 0 END
    """))

    result = await conn.execute(sa.text("""
        SELECT COUNT(*)
        FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'news_source'
          AND INDEX_NAME = 'uk_news_source_platform'
    """))
    if result.scalar() == 0:
        await conn.execute(sa.text("ALTER TABLE news_source ADD UNIQUE KEY uk_news_source_platform (platform)"))

    await conn.execute(sa.text("""
        INSERT INTO news_source
            (name, platform, feed_url, source_type, source_group, trust_tier,
             language, region, fetch_interval, enabled, requires_ai_filter)
        VALUES
            ('Hacker News', 'hackernews', 'https://hacker-news.firebaseio.com/v0', 'api', 'community', 3, 'en', 'global', 60, 1, 0),
            ('OpenAI News', 'openai', 'https://openai.com/news/rss.xml', 'rss', 'official', 1, 'en', 'global', 120, 1, 0),
            ('Google AI Blog', 'google_ai', 'https://blog.google/technology/ai/rss/', 'rss', 'official', 1, 'en', 'global', 120, 1, 0),
            ('Hugging Face Blog', 'huggingface', 'https://huggingface.co/blog/feed.xml', 'rss', 'official', 1, 'en', 'global', 120, 1, 0),
            ('TechCrunch AI', 'techcrunch_ai', 'https://techcrunch.com/category/artificial-intelligence/feed/', 'rss', 'media', 2, 'en', 'global', 90, 1, 0),
            ('MIT Tech Review', 'mit', 'https://www.technologyreview.com/feed/', 'rss', 'media', 2, 'en', 'global', 120, 1, 1)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            feed_url = VALUES(feed_url),
            source_type = VALUES(source_type),
            source_group = VALUES(source_group),
            trust_tier = VALUES(trust_tier),
            language = VALUES(language),
            region = VALUES(region),
            fetch_interval = VALUES(fetch_interval),
            enabled = VALUES(enabled),
            requires_ai_filter = VALUES(requires_ai_filter)
    """))


async def downgrade(conn):
    for column in (
        "updated_at",
        "last_error",
        "error_count",
        "requires_ai_filter",
        "region",
        "language",
        "trust_tier",
        "source_group",
        "source_type",
    ):
        if await _column_exists(conn, column):
            await conn.execute(sa.text(f"ALTER TABLE news_source DROP COLUMN {column}"))

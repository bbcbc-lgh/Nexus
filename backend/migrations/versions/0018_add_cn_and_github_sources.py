"""
Add vetted Chinese RSS and GitHub official API sources.
"""
import sqlalchemy as sa


async def upgrade(conn):
    await conn.execute(sa.text("""
        INSERT INTO news_source
            (name, platform, feed_url, source_type, source_group, trust_tier,
             language, region, fetch_interval, enabled, requires_ai_filter)
        VALUES
            ('InfoQ 中文', 'infoq_cn', 'https://www.infoq.cn/feed', 'rss', 'media', 2, 'zh', 'china', 120, 1, 1),
            ('GitHub AI', 'github_ai', 'https://api.github.com/search/repositories', 'api', 'community', 3, 'en', 'global', 360, 1, 0)
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
    await conn.execute(sa.text("DELETE FROM news_source WHERE platform IN ('infoq_cn', 'github_ai')"))

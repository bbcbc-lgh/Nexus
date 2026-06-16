"""
迁移 0013：新增 comment 评论表，news 表增加 comment_count 字段
"""
import sqlalchemy as sa


async def upgrade(conn):
    # news 表增加 comment_count 字段
    exists = await conn.execute(sa.text("""
        SELECT COUNT(*) FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'news'
          AND COLUMN_NAME = 'comment_count'
    """))
    if exists.scalar() == 0:
        await conn.execute(sa.text(
            "ALTER TABLE news ADD COLUMN comment_count INT UNSIGNED DEFAULT 0 COMMENT '评论数'"
        ))

    await conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS comment (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            news_id INT UNSIGNED NOT NULL,
            user_id INT UNSIGNED NOT NULL,
            parent_id INT UNSIGNED NULL COMMENT '父评论ID，NULL表示顶级',
            content VARCHAR(1000) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_news_time (news_id, created_at),
            INDEX idx_user (user_id),
            FOREIGN KEY (news_id) REFERENCES news(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_id) REFERENCES comment(id) ON DELETE CASCADE
        ) COMMENT='文章评论表';
    """))


async def downgrade(conn):
    await conn.execute(sa.text("DROP TABLE IF EXISTS comment"))

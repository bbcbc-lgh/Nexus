"""
迁移 0007：新增 reading_queue 稍后阅读队列表
"""
import sqlalchemy as sa


async def upgrade(conn):
    await conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS reading_queue (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNSIGNED NOT NULL,
            news_id INT UNSIGNED NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uq_user_news (user_id, news_id),
            INDEX idx_queue_user (user_id),
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
            FOREIGN KEY (news_id) REFERENCES news(id) ON DELETE CASCADE
        ) COMMENT='用户稍后阅读队列表';
    """))


async def downgrade(conn):
    await conn.execute(sa.text("DROP TABLE IF EXISTS reading_queue"))

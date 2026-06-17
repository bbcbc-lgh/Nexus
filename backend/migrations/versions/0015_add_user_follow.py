"""
迁移 0015：新增 user_follow 作者关注表
"""
import sqlalchemy as sa


async def upgrade(conn):
    await conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS user_follow (
            id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
            user_id INT UNSIGNED NOT NULL,
            follow_type VARCHAR(20) NOT NULL,
            follow_value VARCHAR(100) NOT NULL,
            created_at DATETIME DEFAULT NOW(),
            UNIQUE KEY uk_user_follow_value (user_id, follow_type, follow_value),
            INDEX idx_user_follow_type (user_id, follow_type),
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
        )
    """))


async def downgrade(conn):
    await conn.execute(sa.text("DROP TABLE IF EXISTS user_follow"))

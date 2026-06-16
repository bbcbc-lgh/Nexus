"""
迁移 0008：新增 favorite_folder 表，并为 favorite 表添加 folder_id 外键列
"""
import sqlalchemy as sa


async def upgrade(conn):
    # 1. 先建文件夹表
    await conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS favorite_folder (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNSIGNED NOT NULL,
            name VARCHAR(100) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_folder_user (user_id),
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
        ) COMMENT='用户收藏文件夹表';
    """))

    # 2. 给 favorite 表添加 folder_id 列（用 information_schema 检查，MySQL 不支持 ADD COLUMN IF NOT EXISTS）
    result = await conn.execute(sa.text(
        "SELECT COUNT(*) FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'favorite' AND COLUMN_NAME = 'folder_id'"
    ))
    if result.scalar() == 0:
        await conn.execute(sa.text(
            "ALTER TABLE favorite ADD COLUMN folder_id INT UNSIGNED NULL DEFAULT NULL COMMENT '所属文件夹ID'"
        ))
        try:
            await conn.execute(sa.text(
                "ALTER TABLE favorite ADD INDEX idx_favorite_folder (folder_id)"
            ))
        except Exception:
            pass
        try:
            await conn.execute(sa.text(
                "ALTER TABLE favorite ADD CONSTRAINT fk_favorite_folder "
                "FOREIGN KEY (folder_id) REFERENCES favorite_folder(id) ON DELETE SET NULL"
            ))
        except Exception:
            pass


async def downgrade(conn):
    try:
        await conn.execute(sa.text("ALTER TABLE favorite DROP FOREIGN KEY fk_favorite_folder"))
    except Exception:
        pass
    try:
        await conn.execute(sa.text("ALTER TABLE favorite DROP COLUMN folder_id"))
    except Exception:
        pass
    await conn.execute(sa.text("DROP TABLE IF EXISTS favorite_folder"))

"""
迁移 0010：新增 topic_tag + news_topic_tag 主题标签表，并预置常用标签
"""
import sqlalchemy as sa


async def upgrade(conn):
    await conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS topic_tag (
            id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            slug VARCHAR(50) NOT NULL,
            color VARCHAR(7) DEFAULT '#C8860A',
            UNIQUE KEY uq_name (name),
            UNIQUE KEY uq_slug (slug)
        ) COMMENT='主题标签';
    """))

    await conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS news_topic_tag (
            news_id INT UNSIGNED NOT NULL,
            tag_id  INT UNSIGNED NOT NULL,
            PRIMARY KEY (news_id, tag_id),
            FOREIGN KEY (news_id) REFERENCES news(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id)  REFERENCES topic_tag(id) ON DELETE CASCADE
        ) COMMENT='新闻-标签关联';
    """))

    # 预置标签
    tags = [
        ('LLM',         'llm',         '#7C3AED'),
        ('GPT',         'gpt',         '#0D8A6A'),
        ('开源',        'open-source', '#E05D00'),
        ('安全',        'security',    '#C0364D'),
        ('机器人',      'robotics',    '#1A73E8'),
        ('图像生成',    'image-gen',   '#DB2777'),
        ('代码',        'code',        '#047857'),
        ('搜索',        'search',      '#B45309'),
        ('推理',        'reasoning',   '#6D28D9'),
        ('数据集',      'dataset',     '#0369A1'),
        ('硬件',        'hardware',    '#78350F'),
        ('政策监管',    'policy',      '#991B1B'),
        ('创业融资',    'startup',     '#065F46'),
        ('研究论文',    'research',    '#1E3A5F'),
        ('产品发布',    'release',     '#C8860A'),
    ]
    for name, slug, color in tags:
        await conn.execute(sa.text(
            "INSERT IGNORE INTO topic_tag (name, slug, color) VALUES (:name, :slug, :color)"
        ), {"name": name, "slug": slug, "color": color})


async def downgrade(conn):
    await conn.execute(sa.text("DROP TABLE IF EXISTS news_topic_tag"))
    await conn.execute(sa.text("DROP TABLE IF EXISTS topic_tag"))

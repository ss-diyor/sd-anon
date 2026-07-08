import asyncpg
from config import DATABASE_URL

_pool: asyncpg.Pool | None = None


async def init_db_pool() -> asyncpg.Pool:
    """Bot ishga tushganda bir marta chaqiriladi."""
    global _pool
    _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    await _create_tables(_pool)
    return _pool


def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("DB pool hali ishga tushmagan. init_db_pool() ni avval chaqiring.")
    return _pool


async def close_db_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def _create_tables(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id SERIAL PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                label TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_source_code TEXT,
                first_seen_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                sender_telegram_id BIGINT NOT NULL,
                sender_username TEXT,
                sender_first_name TEXT,
                source_code TEXT,
                user_message_id BIGINT NOT NULL,
                owner_message_id BIGINT,
                content_preview TEXT,
                sent_at TIMESTAMPTZ DEFAULT NOW(),
                replied BOOLEAN DEFAULT FALSE
            );
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_owner_msg_id
            ON messages (owner_message_id);
        """)

        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_sender
            ON messages (sender_telegram_id);
        """)

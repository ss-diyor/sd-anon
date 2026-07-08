from database.db import get_pool


# ---------- SOURCES ----------

async def create_source(code: str, label: str) -> bool:
    """Yangi manba (link) yaratadi. Agar kod band bo'lsa False qaytaradi."""
    pool = get_pool()
    try:
        await pool.execute(
            "INSERT INTO sources (code, label) VALUES ($1, $2)", code, label
        )
        return True
    except Exception:
        return False


async def get_source(code: str):
    pool = get_pool()
    return await pool.fetchrow("SELECT * FROM sources WHERE code = $1", code)


async def list_sources_with_stats():
    """Har bir manba va undan kelgan xabarlar sonini qaytaradi."""
    pool = get_pool()
    return await pool.fetch("""
        SELECT s.code, s.label, s.created_at, COUNT(m.id) AS message_count
        FROM sources s
        LEFT JOIN messages m ON m.source_code = s.code
        GROUP BY s.code, s.label, s.created_at
        ORDER BY message_count DESC
    """)


# ---------- USERS ----------

async def upsert_user(telegram_id: int, username: str | None, first_name: str | None, source_code: str | None):
    pool = get_pool()
    await pool.execute("""
        INSERT INTO users (telegram_id, username, first_name, last_source_code)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (telegram_id)
        DO UPDATE SET
            username = EXCLUDED.username,
            first_name = EXCLUDED.first_name,
            last_source_code = COALESCE(EXCLUDED.last_source_code, users.last_source_code)
    """, telegram_id, username, first_name, source_code)


async def get_user_last_source(telegram_id: int) -> str | None:
    pool = get_pool()
    row = await pool.fetchrow("SELECT last_source_code FROM users WHERE telegram_id = $1", telegram_id)
    return row["last_source_code"] if row else None


# ---------- MESSAGES ----------

async def save_message(
    sender_telegram_id: int,
    sender_username: str | None,
    sender_first_name: str | None,
    source_code: str | None,
    user_message_id: int,
    owner_message_id: int,
    content_preview: str,
) -> int:
    pool = get_pool()
    row = await pool.fetchrow("""
        INSERT INTO messages
            (sender_telegram_id, sender_username, sender_first_name,
             source_code, user_message_id, owner_message_id, content_preview)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id
    """, sender_telegram_id, sender_username, sender_first_name,
         source_code, user_message_id, owner_message_id, content_preview)
    return row["id"]


async def get_message_by_owner_msg_id(owner_message_id: int):
    """Owner reply qilganda, qaysi xabarga reply qilganini shu orqali topamiz."""
    pool = get_pool()
    return await pool.fetchrow(
        "SELECT * FROM messages WHERE owner_message_id = $1", owner_message_id
    )


async def mark_replied(message_id: int):
    pool = get_pool()
    await pool.execute("UPDATE messages SET replied = TRUE WHERE id = $1", message_id)


async def get_stats_summary():
    pool = get_pool()
    total = await pool.fetchval("SELECT COUNT(*) FROM messages")
    replied = await pool.fetchval("SELECT COUNT(*) FROM messages WHERE replied = TRUE")
    unique_senders = await pool.fetchval("SELECT COUNT(DISTINCT sender_telegram_id) FROM messages")
    return {"total": total, "replied": replied, "unique_senders": unique_senders}

import aiosqlite
from datetime import datetime

DB_PATH = "clients.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                username TEXT,
                full_name TEXT,
                category TEXT,
                quantity TEXT,
                task TEXT,
                marketplace TEXT,
                phone TEXT,
                status TEXT DEFAULT 'new',
                category_tag TEXT DEFAULT NULL,
                reject_reason TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        await db.commit()


async def save_client_data(
    telegram_id: int,
    username: str,
    full_name: str,
    category: str,
    quantity: str,
    task: str,
    marketplace: str,
    phone: str,
):
    """
    Сохраняем новую заявку клиента.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO clients (
                telegram_id, username, full_name,
                category, quantity, task, marketplace, phone, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'new')
            """,
            (
                telegram_id,
                username,
                full_name,
                category,
                quantity,
                task,
                marketplace,
                phone,
            ),
        )
        await db.commit()


async def get_client_data(telegram_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM clients WHERE telegram_id = ? ORDER BY created_at DESC LIMIT 1",
            (telegram_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


# ===== ФУНКЦИИ ДЛЯ АДМИНКИ =====


async def get_requests_for_admin(
    status: str | None = None, category_tag: str | None = None, limit: int = 20
):
    """
    Получить список заявок для админа.
    """
    query = "SELECT * FROM clients"
    params = []
    conditions = []

    if status:
        conditions.append("status = ?")
        params.append(status)
    if category_tag:
        conditions.append("category_tag = ?")
        params.append(category_tag)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def update_request_status(request_id: int, status: str, reject_reason: str | None = None):
    """
    Обновить статус заявки.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        if reject_reason is not None:
            await db.execute(
                "UPDATE clients SET status = ?, reject_reason = ? WHERE id = ?",
                (status, reject_reason, request_id),
            )
        else:
            await db.execute(
                "UPDATE clients SET status = ?, reject_reason = NULL WHERE id = ?",
                (status, request_id),
            )
        await db.commit()


async def update_request_category_tag(request_id: int, category_tag: str | None):
    """
    Обновить 'папку' заявки (категория для админа).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE clients SET category_tag = ? WHERE id = ?",
            (category_tag, request_id),
        )
        await db.commit()

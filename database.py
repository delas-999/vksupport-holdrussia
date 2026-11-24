import aiomysql
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

async def get_db():
    return await aiomysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, autocommit=True)

# --- ТИКЕТЫ ---
async def create_ticket(vk_id: int, username: str):
    conn = await get_db()
    async with conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO support_tickets (tg_id, username, status) VALUES (%s, %s, 'open')",
            (vk_id, username)
        )
        ticket_id = cur.lastrowid
    conn.close()
    return ticket_id

async def add_message(ticket_id: int, sender: str, text: str):
    conn = await get_db()
    async with conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO support_messages (ticket_id, sender, message_text) VALUES (%s, %s, %s)",
            (ticket_id, sender, text)
        )
    conn.close()

async def get_open_ticket(vk_id: int):
    conn = await get_db()
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT id FROM support_tickets WHERE tg_id = %s AND status = 'open' ORDER BY id DESC LIMIT 1",
            (vk_id,)
        )
        row = await cur.fetchone()
    conn.close()
    return row[0] if row else None

async def close_ticket(ticket_id: int):
    conn = await get_db()
    async with conn.cursor() as cur:
        await cur.execute("UPDATE support_tickets SET status = 'closed' WHERE id = %s", (ticket_id,))
    conn.close()

# --- БАГ-РЕПОРТЫ ---
async def save_bug_report(vk_id: int, nickname: str, description: str, media_id: str = "Нет"):
    conn = await get_db()
    async with conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO bug_reports (tg_id, nickname, description, media_id) VALUES (%s, %s, %s, %s)",
            (vk_id, nickname, description, media_id)
        )
    conn.close()

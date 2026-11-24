import asyncio
import os
from aiohttp import web
from vkbottle.bot import Bot, Message
from config import VK_TOKEN, GROUP_ID
from database import *
from keyboards import get_main_kb

bot = Bot(token=VK_TOKEN)

# Хранилище состояний (какой игрок на каком шаге)
user_states = {}

# --- МИНИ-СЕРВЕР ДЛЯ RENDER ---
async def start_web_server():
    async def health(request):
        return web.Response(text="VK Support Bot is running")
    app = web.Application()
    app.router.add_get('/', health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Веб-сервер запущен на порту {port}")

# --- ОБРАБОТЧИКИ ---
@bot.on.message(text=["начать", "start"])
async def start_handler(message: Message):
    user_states.pop(message.from_id, None)
    await message.answer(
        "👋 Добро пожаловать в службу поддержки HOLD RUSSIA!\n\n"
        "Здесь вы можете найти ответы на частые вопросы, создать тикет или сообщить о баге.\n\n"
        "Выберите действие:",
        keyboard=get_main_kb()
    )

@bot.on.message(text="❓ Частые вопросы")
async def faq_handler(message: Message):
    await message.answer(
        "Выберите вопрос:\n\n"
        "1. Не заходит на сервер\n"
        "2. Не пришел донат\n"
        "3. Ошибки лаунчера\n"
        "4. Забыл пароль\n"
        "5. Пропало имущество\n\n"
        "Напишите номер вопроса (например, 1).",
        keyboard=get_main_kb()
    )

@bot.on.message(text="📩 Создать тикет")
async def create_ticket_handler(message: Message):
    existing = await get_open_ticket(message.from_id)
    if existing:
        await message.answer(f"У вас уже есть открытый тикет #{existing}. Напишите ваш вопрос, и оператор ответит.")
        return
    
    ticket_id = await create_ticket(message.from_id, f"vk_{message.from_id}")
    await message.answer(f"✅ Тикет #{ticket_id} создан!\nОпишите вашу проблему одним сообщением.")
    user_states[message.from_id] = {"action": "ticket", "ticket_id": ticket_id}

@bot.on.message(text="📂 Мои тикеты")
async def my_tickets_handler(message: Message):
    await message.answer("У вас пока нет созданных тикетов (или список будет здесь).")

@bot.on.message(text="❌ Закрыть тикет")
async def close_ticket_handler(message: Message):
    existing = await get_open_ticket(message.from_id)
    if not existing:
        await message.answer("У вас нет открытых тикетов.")
        return
    await close_ticket(existing)
    await message.answer(f"✅ Тикет #{existing} закрыт. Спасибо за обращение!")

# --- БАГ-РЕПОРТЫ ---
@bot.on.message(text="🐞 Сообщить о баге")
async def start_bug_handler(message: Message):
    await message.answer("🐞 Шаг 1 из 3. Введите ваш игровой никнейм:")
    user_states[message.from_id] = {"action": "bug", "step": "nickname"}

# --- ОБРАБОТКА СОСТОЯНИЙ (СООБЩЕНИЙ) ---
@bot.on.message()
async def handle_state(message: Message):
    state = user_states.get(message.from_id)
    if not state:
        return

    action = state.get("action")

    if action == "ticket":
        ticket_id = state["ticket_id"]
        text = message.text or "Медиафайл"
        await add_message(ticket_id, "user", text)
        await message.answer("✅ Ваше сообщение добавлено в тикет. Ожидайте ответа оператора.")
        user_states.pop(message.from_id, None)
        return

    if action == "bug":
        step = state.get("step")
        
        if step == "nickname":
            state["nickname"] = message.text
            state["step"] = "description"
            await message.answer("Шаг 2 из 3. Опишите баг или недоработку как можно подробнее:")
            
        elif step == "description":
            state["description"] = message.text
            state["step"] = "media"
            await message.answer("Шаг 3 из 3. Прикрепите фото/видео или напишите «Нет»:")
            
        elif step == "media":
            media_id = "Нет"
            if message.attachments and message.attachments[0].photo:
                media_id = message.attachments[0].photo.sizes[-1].url
            
            await save_bug_report(message.from_id, state["nickname"], state["description"], media_id)
            await message.answer("✅ Спасибо! Ваш отчет отправлен разработчикам.", keyboard=get_main_kb())
            user_states.pop(message.from_id, None)

# --- ЗАПУСК ---
async def main():
    await start_web_server()
    print("VK Support Bot запущен...")
    await bot.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

import os
import json
import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiohttp import web # Добавили это
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

# --- НАСТРОЙКИ ---
API_TOKEN = '8777068569:AAE5iGFl9_EViPqopOoCCDDIleWPepXdG6M'
SMTP_USER = 'playerok.messagerobot@gmail.com'
SMTP_PASS = 'zpmjyqkmrnshvvln' 
URL_WEB_APP = 'https://fikostrimit.github.io/bot1/' 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- СЕКЦИЯ ДЛЯ RENDER (ОБМАН ПОРТА) ---
async def handle(request):
    return web.Response(text="Bot is Alive!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Берем порт, который дает Render, или 8080 по умолчанию
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Web server started on port {port}")

# --- ТВОЯ ЛОГИКА БОТА ---
def get_html_template(seller, amount, item, buyer):
    return f"""
    <div style="background-color:#0d1117; padding:20px; font-family:sans-serif; color:white; max-width:450px; margin:0 auto; border-radius:20px;">
        <div style="background:linear-gradient(90deg, #3586ff 0%, #00c2ff 100%); border-radius:15px; padding:25px; color:white; margin-bottom:15px;">
            <div style="float:right; background:white; color:black; padding:5px 10px; border-radius:8px; font-weight:900;">Player<span style="color:#3586ff;">ok</span></div>
            <h2 style="margin:0; color:white;">Оплата подтверждена</h2>
        </div>
        <div style="background-color:#161b22; border-radius:15px; padding:20px; margin-bottom:10px;">
            <h1 style="color:#2ecc71; margin:5px 0;">{amount} ₽</h1>
        </div>
        <div style="background-color:#161b22; border-radius:15px; padding:20px;">
            <p>Товар: <b>{item}</b></p>
            <p>Продавец: <b>@{seller}</b></p>
            <p>Покупатель: <b>@{buyer}</b></p>
        </div>
    </div>
    """

def send_email(to_email, seller, amount, item, buyer):
    msg = MIMEMultipart()
    msg['Subject'] = "Playerok • Оплата подтверждена"
    msg['From'] = f"Playerok Support <{SMTP_USER}>"
    msg['To'] = to_email
    msg.attach(MIMEText(get_html_template(seller, amount, item, buyer), 'html'))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🎁 Создать письмо", web_app=WebAppInfo(url=URL_WEB_APP))]
    ], resize_keyboard=True)
    await message.answer("✅ Бот запущен на Render!\nНажми кнопку:", reply_markup=kb)

@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        send_email(data['email'], data['seller'], data['amount'], data['item'], data['buyer'])
        await message.answer(f"✅ Отправлено на {data['email']}")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

async def main():
    logging.basicConfig(level=logging.INFO)
    # Запускаем "обманку" для Render
    asyncio.create_task(start_web_server())
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

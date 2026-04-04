import os
import json
import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiohttp import web
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

# --- СЕРВЕР ДЛЯ RENDER (ЧТОБЫ НЕ БЫЛО ОШИБКИ ПОРТА) ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- ШАБЛОН ПИСЬМА (ТВОЙ ДИЗАЙН) ---
def get_html_template(seller, amount, item, buyer):
    # Используем двойные {{ }} для CSS, чтобы Python не ругался
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="background-color: #0a0a0a; color: #ffffff; font-family: sans-serif; margin: 0; padding: 20px;">
        <div style="max-width: 420px; margin: 0 auto;">
            <div style="background: linear-gradient(90deg, #3291ff 0%, #00c2ff 100%); border-radius: 20px 20px 10px 10px; padding: 24px; margin-bottom: 12px;">
                <div style="background: white; color: black; padding: 8px 12px; border-radius: 6px; font-weight: 900; float: right;">Player<span style="color:#3586ff;">ok</span></div>
                <h2 style="margin:0; font-size:21px; color:white;">Playerok • Сделка</h2>
                <p style="margin:8px 0 0 0; font-size:12px; opacity:0.9; color:white;">Оплата подтверждена внутри платформы</p>
            </div>

            <div style="background-color: #141414; border-radius: 22px; padding: 20px; margin-bottom: 12px; border: 1px solid #262626;">
                <div style="font-weight:700;">Здравствуйте, @{seller} <span style="background:#2a2444; color:#9a8cff; padding:4px 10px; border-radius:10px; font-size:11px; margin-left:10px;">Seller</span></div>
            </div>

            <div style="background-color: #141414; border-radius: 22px; padding: 20px; margin-bottom: 12px; border: 1px solid #262626;">
                <div style="color: #828282; font-size: 13px; margin-bottom: 8px;">Статус</div>
                <div style="background-color: #1a8944; color: white; padding: 7px 14px; border-radius: 10px; font-size: 13px; font-weight: 800; display: inline-block; margin-bottom: 15px;">ОПЛАТА ПОДТВЕРЖДЕНА</div>
                <div style="color: #00a651; font-size: 28px; font-weight: 800; margin: 0 0 15px 0;">{amount} ₽</div>
                <p style="color: #828282; font-size: 14px;">Оплата по сделке зафиксирована системой. Передайте товар покупателю.</p>
            </div>

            <div style="background-color: #141414; border-radius: 22px; padding: 20px; margin-bottom: 12px; border: 1px solid #262626;">
                <p style="margin:0 0 10px 0; color:#828282;">Товар: <b style="color:white;">{item}</b></p>
                <p style="margin:0; color:#828282;">Покупатель: <b style="color:white;">@{buyer}</b></p>
            </div>

            <div style="background-color: #1c1814; border-left: 4px solid #d29922; border-radius: 10px; padding: 15px;">
                <div style="color:#e19d55; font-weight:800; font-size:11px; text-transform:uppercase;">Действие сейчас</div>
                <p style="font-size:13px; margin:5px 0; color:white;">Передайте товар покупателю: <b>@{buyer}</b></p>
            </div>

            <p style="text-align:center; color:#828282; font-size:11px; margin-top:20px;">© 2026 Playerok Support</p>
        </div>
    </body>
    </html>
    """

def send_email(to_email, seller, amount, item, buyer):
    msg = MIMEMultipart()
    msg['Subject'] = "Playerok • Оплата подтверждена"
    msg['From'] = f"Playerok Support <{SMTP_USER}>"
    msg['To'] = to_email
    
    html_body = get_html_template(seller, amount, item, buyer)
    msg.attach(MIMEText(html_body, 'html'))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🎁 Создать письмо", web_app=WebAppInfo(url=URL_WEB_APP))]
    ], resize_keyboard=True)
    await message.answer("Бот готов к работе. Нажми на кнопку ниже, чтобы открыть панель:", reply_markup=kb)

@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        
        email = data.get('email')
        seller = data.get('seller')
        amount = data.get('amount')
        item = data.get('item')
        buyer = data.get('buyer')

        await message.answer("⏳ Отправляю письмо с вашим дизайном...")
        send_email(email, seller, amount, item, buyer)
        await message.answer(f"✅ Готово! Письмо отправлено на {email}")
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

async def main():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(start_web_server())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

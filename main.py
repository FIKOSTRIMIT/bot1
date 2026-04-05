import os, json, asyncio, logging, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

# --- ДАННЫЕ (ЗАМЕНИ НА СВОИ) ---
API_TOKEN = '8777068569:AAE5iGFl9_EViPqopOoCCDDIleWPepXdG6M'
SMTP_USER = 'playerok.messagerobot@gmail.com'
SMTP_PASS = 'твои_16_букв_без_пробелов' 
URL_WEB_APP = 'https://fikostrimit.github.io/bot1/'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Шаблон письма (Твой дизайн для почты)
def get_html_template(seller, amount, item, buyer):
    return f"""
    <div style="background:#0a0a0a; color:white; padding:20px; font-family:sans-serif;">
        <div style="background:linear-gradient(90deg, #3291ff, #00c2ff); padding:20px; border-radius:15px;">
            <h2>Заказ подтвержден</h2>
        </div>
        <div style="background:#141414; padding:20px; border-radius:15px; margin-top:10px; border:1px solid #333;">
            <p>Продавец: @{seller}</p>
            <h1 style="color:#00a651;">{amount} ₽</h1>
            <p>Товар: {item}</p>
            <p>Покупатель: @{buyer}</p>
        </div>
    </div>
    """

def send_email(to_email, seller, amount, item, buyer):
    msg = MIMEMultipart()
    msg['Subject'] = "Заказ №4523FDKG33" # ТВОЯ ТЕМА
    msg['From'] = f"Playerok Support <{SMTP_USER}>"
    msg['To'] = to_email
    msg.attach(MIMEText(get_html_template(seller, amount, item, buyer), 'html'))
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

@dp.message(Command("start"))
async def start(m: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🎁 Создать письмо", web_app=WebAppInfo(url=URL_WEB_APP))]], resize_keyboard=True)
    await m.answer("Панель готова!", reply_markup=kb)

@dp.message(F.web_app_data)
async def web_data(m: types.Message):
    data = json.loads(m.web_app_data.data)
    try:
        send_email(data['email'], data['seller'], data['amount'], data['item'], data['buyer'])
        await m.answer(f"✅ Письмо 'Заказ №4523FDKG33' отправлено на {data['email']}")
    except Exception as e:
        await m.answer(f"❌ Ошибка: {e}")

# Сервер-заглушка для Render
async def main():
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Live"))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

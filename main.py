import json
import asyncio
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

# --- НАСТРОЙКИ ---
API_TOKEN = '8777068569:AAE5iGFl9_EViPqopOoCCDDIleWPepXdG6M'
SMTP_USER = 'playerok.messagerobot@gmail.com'
SMTP_PASS = 'zpmjyqkmrnshvvln' 
# Ссылка на твой GitHub Pages (где лежит index.html)
URL_WEB_APP = 'https://ТВОЙ-НИК.github.io/РЕПОЗИТОРИЙ/' 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def get_html_template(seller, amount, item, buyer):
    return f"""
    <div style="background-color:#0d1117; padding:20px; font-family:sans-serif; color:white; max-width:450px; margin:0 auto; border-radius:20px;">
        <div style="background:linear-gradient(90deg, #3586ff 0%, #00c2ff 100%); border-radius:15px; padding:25px; color:white; margin-bottom:15px;">
            <div style="float:right; background:white; color:black; padding:5px 10px; border-radius:8px; font-weight:900;">Player<span style="color:#3586ff;">ok</span></div>
            <h2 style="margin:0; color:white;">Оплата подтверждена</h2>
            <p style="margin:5px 0 0 0; font-size:12px; opacity:0.8; color:white;">Системное уведомление</p>
        </div>
        <div style="background-color:#161b22; border-radius:15px; padding:20px; margin-bottom:10px;">
            <p style="color:#8b949e; margin:0; font-size:14px;">Сумма сделки</p>
            <h1 style="color:#2ecc71; margin:5px 0; font-size:32px;">{amount} ₽</h1>
        </div>
        <div style="background-color:#161b22; border-radius:15px; padding:20px;">
            <p style="margin:0 0 8px 0; color:#8b949e;">Товар: <span style="color:white; font-weight:bold;">{item}</span></p>
            <p style="margin:0 0 8px 0; color:#8b949e;">Продавец: <span style="color:white; font-weight:bold;">@{seller}</span></p>
            <p style="margin:0; color:#8b949e;">Покупатель: <span style="color:white; font-weight:bold;">@{buyer}</span></p>
        </div>
        <p style="text-align:center; color:#8b949e; font-size:11px; margin-top:20px;">© 2026 Playerok Support • Работает через Web App</p>
    </div>
    """

def send_email(to_email, seller, amount, item, buyer):
    msg = MIMEMultipart()
    msg['Subject'] = "Playerok • Оплата подтверждена"
    msg['From'] = f"Playerok Support <{SMTP_USER}>"
    msg['To'] = to_email
    
    body = get_html_template(seller, amount, item, buyer)
    msg.attach(MIMEText(body, 'html'))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

@dp.message(Command("start"))
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🎁 Создать письмо", web_app=WebAppInfo(url=URL_WEB_APP))]
    ], resize_keyboard=True)
    await message.answer("✅ Бот запущен через VS Code!\nНажми кнопку, чтобы открыть форму:", reply_markup=kb)

@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        await message.answer("⏳ Отправляю письмо...")
        
        send_email(
            data.get('email'),
            data.get('seller'),
            data.get('amount'),
            data.get('item'),
            data.get('buyer')
        )
        
        await message.answer(f"✅ Письмо успешно отправлено на {data.get('email')}!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
        print(f"DEBUG ERROR: {e}")

async def main():

    URL_WEB_APP = 'https://fikostrimit.github.io/bot1/'
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)
URL_WEB_APP = 'https://fikostrimit.github.io/bot1/'

if __name__ == "__main__":
    asyncio.run(main())

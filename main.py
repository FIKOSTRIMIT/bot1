import os, asyncio, logging, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# --- НАСТРОЙКИ (ВСЁ УЖЕ ВПИСАНО) ---
API_TOKEN = '8777068569:AAE5iGFl9_EViPqopOoCCDDIleWPepXdG6M'
SMTP_USER = 'playerok.messagerobot@gmail.com'
SMTP_PASS = 'zpmjyqkmrnshvvln' 

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class OrderState(StatesGroup):
    waiting_email = State()
    waiting_seller = State()
    waiting_amount = State()
    waiting_item = State()
    waiting_buyer = State()

# --- ТВОЙ ДИЗАЙН ИЗ ПИСЬМА ---
def get_html_template(seller, amount, item, buyer):
    return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ background-color: #0a0a0a; color: #ffffff; font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        .wrapper {{ max-width: 420px; margin: 0 auto; }}
        .header {{ background: linear-gradient(90deg, #3291ff 0%, #00c2ff 100%); border-radius: 20px 20px 10px 10px; padding: 24px; }}
        .logo {{ background: white; color: black; padding: 5px 10px; border-radius: 6px; font-weight: 900; float: right; margin-top: -30px; }}
        .card {{ background-color: #141414; border-radius: 22px; padding: 20px; margin-top: 12px; border: 1px solid #262626; }}
        .status-confirmed {{ background-color: #1a8944; color: white; padding: 7px 14px; border-radius: 10px; font-size: 13px; font-weight: 800; display: inline-block; }}
        .price {{ color: #00a651; font-size: 28px; font-weight: 800; margin: 15px 0; }}
        .label {{ color: #828282; font-size: 13px; margin-bottom: 5px; }}
        .val {{ font-weight: 700; color: white; }}
        .action-card {{ background-color: #1c1814; border-left: 4px solid #d29922; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
<div class="wrapper">
    <div class="header">
        <h2 style="margin:0; color:white;">Playerok • Сделка</h2>
        <p style="margin:5px 0 0 0; font-size:12px; color:white; opacity:0.8;">Оплата подтверждена внутри платформы</p>
        <div class="logo">Player<span style="color:#3586ff">ok</span></div>
    </div>
    <div class="card">
        <div style="font-weight: 700; font-size: 17px;">👋 Здравствуйте, @{seller}</div>
    </div>
    <div class="card">
        <div class="label">Статус</div>
        <div class="status-confirmed">✅ ОПЛАТА ПОДТВЕРЖДЕНА</div>
        <div class="price">{amount} ₽</div>
        <div style="color:#828282; font-size:14px;">Передайте товар покупателю и дождитесь подтверждения.</div>
    </div>
    <div class="card">
        <div class="label">Товар: <span class="val">{item}</span></div>
        <div class="label">Покупатель: <span class="val">@{buyer}</span></div>
    </div>
    <div class="card action-card">
        <b style="color:#e19d55;">ДЕЙСТВИЕ СЕЙЧАС</b>
        <p style="margin:5px 0; font-size:14px;">Передайте товар: <b>@{buyer}</b></p>
    </div>
</div>
</body>
</html>
    """

def send_email(to_email, seller, amount, item, buyer):
    msg = MIMEMultipart()
    msg['Subject'] = "Заказ №4523FDKG33"
    msg['From'] = f"Playerok Support <{SMTP_USER}>"
    msg['To'] = to_email
    msg.attach(MIMEText(get_html_template(seller, amount, item, buyer), 'html'))
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

# --- ЛОГИКА ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    welcome = (
        "🤖 **Playerok Seller Panel готова к работе!**\n\n"
        "Эта панель создана для генерации официальных уведомлений о подтверждении оплаты.\n\n"
        "🚀 **Начинаем настройку:**\n"
        "1️⃣ Шаг: Введите **Email** получателя:"
    )
    await message.answer(welcome, parse_mode="Markdown")
    await state.set_state(OrderState.waiting_email)

@dp.message(OrderState.waiting_email)
async def get_email(m: types.Message, state: FSMContext):
    await state.update_data(email=m.text)
    await m.answer("2️⃣ Шаг: Введите **Ник продавца**:")
    await state.set_state(OrderState.waiting_seller)

@dp.message(OrderState.waiting_seller)
async def get_seller(m: types.Message, state: FSMContext):
    await state.update_data(seller=m.text)
    await m.answer("3️⃣ Шаг: Введите **Сумму**:")
    await state.set_state(OrderState.waiting_amount)

@dp.message(OrderState.waiting_amount)
async def get_amount(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text)
    await m.answer("4️⃣ Шаг: Введите **Название товара**:")
    await state.set_state(OrderState.waiting_item)

@dp.message(OrderState.waiting_item)
async def get_item(m: types.Message, state: FSMContext):
    await state.update_data(item=m.text)
    await m.answer("5️⃣ Шаг: Введите **Ник покупателя**:")
    await state.set_state(OrderState.waiting_buyer)

@dp.message(OrderState.waiting_buyer)
async def final(m: types.Message, state: FSMContext):
    d = await state.get_data()
    try:
        send_email(d['email'], d['seller'], d['amount'], d['item'], m.text)
        await m.answer(f"✅ **Письмо отправлено!**\nТема: Заказ №4523FDKG33")
    except Exception as e:
        await m.answer(f"❌ Ошибка: {e}")
    await state.clear()

async def main():
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Bot is Live"))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

import os, asyncio, logging, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# --- НАСТРОЙКИ ---
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

# --- ШАБЛОН ПИСЬМА ---
def get_html_template(seller, amount, item, buyer):
    return f"""
    <div style="background-color:#0a0a0a; color:#ffffff; padding:20px; font-family:Arial;">
        <div style="background:linear-gradient(90deg, #3291ff, #00c2ff); padding:20px; border-radius:15px;">
            <h2 style="margin:0;">Playerok • Сделка</h2>
        </div>
        <div style="background:#141414; padding:20px; border-radius:15px; margin-top:10px; border:1px solid #262626;">
            <p>👋 Здравствуйте, @{seller}</p>
            <h1 style="color:#00a651;">{amount} ₽</h1>
            <p>Товар: <b>{item}</b></p>
            <p>Покупатель: <b>@{buyer}</b></p>
        </div>
    </div>
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

# --- ЛОГИКА ОПРОСА ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear() # Сбрасываем старые данные
    await message.answer("🤖 **Панель Playerok готова!**\n\n1️⃣ Введите **Email** получателя:")
    await state.set_state(OrderState.waiting_email)

@dp.message(OrderState.waiting_email)
async def step1(m: types.Message, state: FSMContext):
    await state.update_data(email=m.text)
    await m.answer("2️⃣ Введите **Ник продавца**:")
    await state.set_state(OrderState.waiting_seller)

@dp.message(OrderState.waiting_seller)
async def step2(m: types.Message, state: FSMContext):
    await state.update_data(seller=m.text)
    await m.answer("3️⃣ Введите **Сумму**:")
    await state.set_state(OrderState.waiting_amount)

@dp.message(OrderState.waiting_amount)
async def step3(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text)
    await m.answer("4️⃣ Введите **Название товара**:")
    await state.set_state(OrderState.waiting_item)

@dp.message(OrderState.waiting_item)
async def step4(m: types.Message, state: FSMContext):
    await state.update_data(item=m.text)
    await m.answer("5️⃣ Введите **Ник покупателя**:")
    await state.set_state(OrderState.waiting_buyer)

@dp.message(OrderState.waiting_buyer)
async def step5_final(m: types.Message, state: FSMContext):
    buyer_nick = m.text
    data = await state.get_data()
    
    await m.answer("⏳ **Отправляю письмо...**")
    
    try:
        send_email(data['email'], data['seller'], data['amount'], data['item'], buyer_nick)
        await m.answer(f"✅ **Письмо успешно отправлено!**\n\nТема: `Заказ №4523FDKG33`\nПолучатель: `{data['email']}`")
    except Exception as e:
        await m.answer(f"❌ **Ошибка:** {e}")
    
    await state.clear() # Завершаем работу

# Запуск сервера
async def main():
    logging.basicConfig(level=logging.INFO)
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Live"))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

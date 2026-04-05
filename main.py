import os, asyncio, logging, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- НАСТРОЙКИ ---
API_TOKEN = '8777068569:AAE5iGFl9_EViPqopOoCCDDIleWPepXdG6M'
SMTP_USER = 'playerok.messagerobot@gmail.com'
SMTP_PASS = 'zpmjyqkmrnshvvln' 
ACCESS_CODE = "0000"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
authorized_users = set()

class OrderState(StatesGroup):
    auth = State()
    waiting_email = State()
    waiting_seller = State()
    waiting_amount = State()
    waiting_item = State()
    waiting_buyer = State()

# --- ШАБЛОН ПИСЬМА (HTML) ---
def get_html_template(seller, amount, item, buyer):
    # Очищаем ники от лишних @, если они есть
    s = seller.replace("@", "")
    b = buyer.replace("@", "")
    return f"""
    <div style="background:#0a0a0a; color:white; padding:20px; font-family:sans-serif; max-width:420px; margin:0 auto; border-radius:20px;">
        <div style="background:linear-gradient(90deg, #3291ff, #00c2ff); padding:20px; border-radius:15px;">
            <h2 style="margin:0; color:white;">Playerok • Сделка</h2>
        </div>
        <div style="background:#141414; padding:20px; border-radius:15px; margin-top:10px; border:1px solid #262626;">
            <p style="color:#828282;">Здравствуйте, @{s}</p>
            <h1 style="color:#00a651; font-size:32px;">{amount} ₽</h1>
            <p>Товар: <b style="color:white;">{item}</b></p>
            <p>Покупатель: <b style="color:white;">@{b}</b></p>
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

def get_back_kb(step):
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data=f"back_{step}")
    return kb.as_markup()

# --- ЛОГИКА ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id not in authorized_users:
        await message.answer("🔒 Введите пароль доступа:")
        await state.set_state(OrderState.auth)
    else:
        kb = InlineKeyboardBuilder()
        kb.button(text="🚀 Начать создание письма", callback_data="start_order")
        await message.answer("✅ Панель готова к работе.", reply_markup=kb.as_markup())

@dp.message(OrderState.auth)
async def check_auth(message: types.Message, state: FSMContext):
    if message.text == ACCESS_CODE:
        authorized_users.add(message.from_user.id)
        kb = InlineKeyboardBuilder()
        kb.button(text="🚀 Начать создание письма", callback_data="start_order")
        await message.answer("🔓 Доступ разрешен!", reply_markup=kb.as_markup())
        await state.clear()
    else:
        await message.answer("❌ Неверно. Еще раз:")

@dp.callback_query(F.data == "start_order")
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("1️⃣ Введите **Email** получателя:")
    await state.set_state(OrderState.waiting_email)
    await callback.answer()

@dp.message(OrderState.waiting_email)
async def step1(m: types.Message, state: FSMContext):
    await state.update_data(email=m.text)
    await m.answer(f"✅ Email принят.\n2️⃣ Введите **Ник продавца**:", reply_markup=get_back_kb("email"))
    await state.set_state(OrderState.waiting_seller)

@dp.message(OrderState.waiting_seller)
async def step2(m: types.Message, state: FSMContext):
    await state.update_data(seller=m.text)
    await m.answer(f"✅ Продавец зафиксирован.\n3️⃣ Введите **Сумму**:", reply_markup=get_back_kb("seller"))
    await state.set_state(OrderState.waiting_amount)

@dp.message(OrderState.waiting_amount)
async def step3(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text)
    await m.answer(f"✅ Сумма: {m.text} ₽\n4️⃣ Введите **Название товара**:", reply_markup=get_back_kb("amount"))
    await state.set_state(OrderState.waiting_item)

@dp.message(OrderState.waiting_item)
async def step4(m: types.Message, state: FSMContext):
    await state.update_data(item=m.text)
    await m.answer(f"✅ Товар принят.\n5️⃣ Введите **Ник покупателя**:", reply_markup=get_back_kb("item"))
    await state.set_state(OrderState.waiting_buyer)

@dp.message(OrderState.waiting_buyer)
async def step5_final(m: types.Message, state: FSMContext):
    data = await state.get_data()
    buyer_clean = m.text # Очистится в функции шаблона
    await m.answer("⏳ **Отправка письма...**")
    try:
        send_email(data['email'], data['seller'], data['amount'], data['item'], buyer_clean)
        await m.answer(f"✅ **Успешно отправлено!**\n\nТема: `Заказ №4523FDKG33` на `{data['email']}`")
    except Exception as e:
        await m.answer(f"❌ Ошибка отправки: {e}")
    await state.clear()

@dp.callback_query(F.data.startswith("back_"))
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    step = callback.data.split("_")[1]
    if step == "email":
        await callback.message.answer("1️⃣ Введите **Email** получателя:")
        await state.set_state(OrderState.waiting_email)
    elif step == "seller":
        await callback.message.answer("2️⃣ Введите **Ник продавца**:")
        await state.set_state(OrderState.waiting_seller)
    # ... (остальные шаги назад аналогично)
    await callback.answer()

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

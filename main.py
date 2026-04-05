import asyncio, logging, aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8777068569:AAE5iGFl9_EViPqopOoCCDDIleWPepXdG6M'
GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwpIshcyQXZUWnrQvDukQ8K2KLfwoMB5sINRtx5BYn6Z69gSbWrOz5bmzcBL5EqUJEQ/exec'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class OrderState(StatesGroup):
    waiting_email = State()
    waiting_seller = State()
    waiting_amount = State()
    waiting_item = State()
    waiting_buyer = State()

def get_html_template(seller, amount, item, buyer):
    s = seller.replace("@", ""); b = buyer.replace("@", "")
    return f"""
    <div style="background:#0a0a0a; color:white; padding:20px; font-family:sans-serif; max-width:400px; margin:0 auto; border-radius:20px; border: 1px solid #262626;">
        <div style="background:linear-gradient(90deg, #3291ff, #00c2ff); padding:20px; border-radius:15px; text-align:center;">
            <h2 style="margin:0; color:white;">Playerok • Сделка</h2>
        </div>
        <div style="background:#141414; padding:20px; border-radius:15px; margin-top:10px; border:1px solid #262626;">
            <p style="color:#828282;">Здравствуйте, @{s}</p>
            <div style="color:#00a651; font-size:32px; font-weight:bold; margin:15px 0;">{amount} ₽</div>
            <p>Товар: <b style="color:white;">{item}</b></p>
            <p>Покупатель: <b style="color:white;">@{b}</b></p>
        </div>
    </div>
    """

async def send_via_google(email, body):
    async with aiohttp.ClientSession() as session:
        payload = {"email": email, "body": body}
        async with session.post(GOOGLE_SCRIPT_URL, json=payload, timeout=30) as resp:
            return await resp.text()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardBuilder().button(text="🚀 Создать уведомление", callback_data="start_order").as_markup()
    await message.answer("✅ Бот запущен на Render (без прокси).", reply_markup=kb)

@dp.callback_query(F.data == "start_order")
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("1️⃣ Введите **Email** получателя:")
    await state.set_state(OrderState.waiting_email)
    await callback.answer()

@dp.message(OrderState.waiting_email)
async def step1(m: types.Message, state: FSMContext):
    await state.update_data(email=m.text)
    await m.answer(f"✅ Email: {m.text}\n2️⃣ Ник продавца:")
    await state.set_state(OrderState.waiting_seller)

@dp.message(OrderState.waiting_seller)
async def step2(m: types.Message, state: FSMContext):
    await state.update_data(seller=m.text)
    await m.answer(f"✅ Продавец: {m.text}\n3️⃣ Сумма:")
    await state.set_state(OrderState.waiting_amount)

@dp.message(OrderState.waiting_amount)
async def step3(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text)
    await m.answer(f"✅ Сумма: {m.text} ₽\n4️⃣ Товар:")
    await state.set_state(OrderState.waiting_item)

@dp.message(OrderState.waiting_item)
async def step4(m: types.Message, state: FSMContext):
    await state.update_data(item=m.text)
    await m.answer("5️⃣ Ник покупателя:")
    await state.set_state(OrderState.waiting_buyer)

@dp.message(OrderState.waiting_buyer)
async def step5_final(m: types.Message, state: FSMContext):
    data = await state.get_data()
    await m.answer("⏳ **Отправка через Google...**")
    try:
        html_body = get_html_template(data['seller'], data['amount'], data['item'], m.text)
        result = await send_via_google(data['email'], html_body)
        await m.answer(f"✅ **Результат:** {result}")
    except Exception as e:
        await m.answer(f"❌ Ошибка: {e}")
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

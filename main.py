import asyncio, logging, aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8777068569:AAE5iGFl9_EViPqopOoCCDDIleWPepXdG6M'
# Твоя новая рабочая ссылка Google Script
GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwApBf3F8gJ34BGN5zvIlX_hPYkEz5K7aKDeoDH0pdE-I9TjCE-r2690IuTpl4OaJ9q/exec'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния для пошагового ввода данных
class OrderState(StatesGroup):
    waiting_email = State()
    waiting_seller = State()
    waiting_amount = State()
    waiting_item = State()
    waiting_buyer = State()

# Красивый HTML-шаблон письма (Playerok Style)
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

# Функция для отправки данных в Google
async def send_via_google(email, body):
    async with aiohttp.ClientSession() as session:
        payload = {"email": email, "body": body}
        # Отправляем POST запрос к Google Script
        async with session.post(GOOGLE_SCRIPT_URL, json=payload, timeout=30) as resp:
            return await resp.text()

# --- ОБРАБОТЧИКИ ТЕЛЕГРАМ ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardBuilder().button(text="🚀 Создать уведомление", callback_data="start_order").as_markup()
    await message.answer("✅ Бот готов к работе на Render.\nНажми кнопку ниже, чтобы начать.", reply_markup=kb)

@dp.callback_query(F.data == "start_order")
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("1️⃣ Введите **Email** получателя:")
    await state.set_state(OrderState.waiting_email)
    await callback.answer()

@dp.message(OrderState.waiting_email)
async def step1(m: types.Message, state: FSMContext):
    await state.update_data(email=m.text)
    await m.answer(f"✅ Email: {m.text}\n2️⃣ Введите ник **продавца**:")
    await state.set_state(OrderState.waiting_seller)

@dp.message(OrderState.waiting_seller)
async def step2(m: types.Message, state: FSMContext):
    await state.update_data(seller=m.text)
    await m.answer(f"✅ Продавец: {m.text}\n3️⃣ Введите **сумму** (только цифры):")
    await state.set_state(OrderState.waiting_amount)

@dp.message(OrderState.waiting_amount)
async def step3(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text)
    await m.answer(f"✅ Сумма: {m.text} ₽\n4️⃣ Введите название **товара**:")
    await state.set_state(OrderState.waiting_item)

@dp.message(OrderState.waiting_item)
async def step4(m: types.Message, state: FSMContext):
    await state.update_data(item=m.text)
    await m.answer("5️⃣ Введите ник **покупателя**:")
    await state.set_state(OrderState.waiting_buyer)

@dp.message(OrderState.waiting_buyer)
async def step5_final(m: types.Message, state: FSMContext):
    data = await state.get_data()
    buyer = m.text
    await m.answer("⏳ **Отправка письма через Google...**")
    
    try:
        # Генерируем HTML-код письма
        html_body = get_html_template(data['seller'], data['amount'], data['item'], buyer)
        
        # Отправляем в Google
        result = await send_via_google(data['email'], html_body)
        
        # Если Google ответил Success, значит всё круто
        if "Success" in result:
            await m.answer(f"✅ **Успешно отправлено!**\nПроверьте почту {data['email']}")
        else:
            await m.answer(f"❌ Ошибка от Google:\n`{result}`", parse_mode="Markdown")
            
    except Exception as e:
        await m.answer(f"❌ Системная ошибка:\n`{str(e)}`", parse_mode="Markdown")
        
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

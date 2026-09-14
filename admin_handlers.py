import requests
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database.queries as db
from config import ADMIN_ID

admin_router = Router()

# Foydalanuvchi asosiy menyusi klaviaturasi (Loyihangizdagi nomga qarab moslashtiring)
user_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛒 Buyurtma berish"), KeyboardButton(text="👤 Kabinet")],
        [KeyboardButton(text="💰 Balans to'ldirish"), KeyboardButton(text="📊 Xizmatlar")],
        [KeyboardButton(text="🛠 Admin Panel")]
    ],
    resize_keyboard=True
)

# Admin panel klaviaturasi
admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 User Qidirish"), KeyboardButton(text="📊 Bot statistikasi")],
        [KeyboardButton(text="➕ Balans qo'shish"), KeyboardButton(text="➖ Balans ayirish")],
        [KeyboardButton(text="🚫 Userni Bloklash"), KeyboardButton(text="💳 API Balans")],
        [KeyboardButton(text="⚙️ API Sozlamalari"), KeyboardButton(text="📈 Ustama Foizi (Natsenka)")],
        [KeyboardButton(text="💳 Karta Sozlamalari"), KeyboardButton(text="📢 Xabar Tarqatish")],
        [KeyboardButton(text="🎁 Promokod Yaratish"), KeyboardButton(text="🔎 Buyurtmani tekshirish")],
        [KeyboardButton(text="💸 Pulni qaytarish (Refund)"), KeyboardButton(text="🛠 Texnik rejim")],
        [KeyboardButton(text="⬅️ Bosh menyu")]
    ],
    resize_keyboard=True
)

class AdminStates(StatesGroup):
    waiting_search_user = State()
    waiting_add_bal_user = State()
    waiting_add_bal_amount = State()
    waiting_deduct_bal_user = State()
    waiting_deduct_bal_amount = State()
    waiting_ban_user = State()
    waiting_api_url = State()
    waiting_api_key = State()
    waiting_markup_percent = State()
    waiting_card_number = State()
    waiting_card_name = State()
    waiting_broadcast_msg = State()
    waiting_promo_code = State()
    waiting_promo_amount = State()
    waiting_order_check_id = State()
    waiting_refund_order_id = State()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

# ⬅️ Bosh menyu (Foydalanuvchining asosiy menyusiga qaytaradi va barcha state'larni tozalaydi)
@admin_router.message(State("*"), F.text == "⬅️ Bosh menyu")
async def back_to_main_menu(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.clear()
    await message.answer(
        "🏠 <b>Asosiy menyudasiz:</b>",
        reply_markup=user_main_keyboard,
        parse_mode="HTML"
    )

# Admin panel menyusini chiqarish
@admin_router.message(State("*"), F.text.in_({"🛠 Admin Panel", "🧑‍💻 Admin Panel", "👨‍💻 Admin Panel", "🔑 Admin Panel", "Admin Panel"}))
async def open_admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.clear()
    await message.answer(
        "🛠 <b>Kengaytirilgan Admin Panel:</b>",
        reply_markup=admin_keyboard,
        parse_mode="HTML"
    )

# 1. 📊 Bot statistikasi
@admin_router.message(State("*"), F.text == "📊 Bot statistikasi")
async def admin_stats(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.clear()
    users_count = db.get_total_users_count()
    total_balance = db.get_total_users_balance()
    orders_count = db.get_total_orders_count()
    
    text = (
        f"📊 <b>Bot statistikasi:</b>\n\n"
        f"👥 Barcha foydalanuvchilar: <b>{users_count} ta</b>\n"
        f"💰 Jami balanslar: <b>{total_balance:.2f} so'm</b>\n"
        f"🛒 Jami buyurtmalar: <b>{orders_count} ta</b>"
    )
    await message.answer(text, parse_mode="HTML")

# 2. 🔍 User Qidirish
@admin_router.message(State("*"), F.text == "🔍 User Qidirish")
async def start_user_search(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.set_state(AdminStates.waiting_search_user)
    await message.answer("🔍 Qidirilayotgan foydalanuvchining ID raqami yoki Username'ini kiriting:")

@admin_router.message(AdminStates.waiting_search_user)
async def process_user_search(message: Message, state: FSMContext):
    user_data = db.find_user(message.text.strip())
    if user_data:
        username = f"@{user_data['username']}" if user_data.get('username') else "Mavjud emas"
        text = (
            f"👤 <b>Foydalanuvchi ma'lumotlari:</b>\n\n"
            f"🆔 ID: <code>{user_data['id']}</code>\n"
            f"👤 Username: {username}\n"
            f"💰 Balans: <b>{user_data['balance']} so'm</b>\n"
            f"🚫 Holati: <b>{'Bloklangan' if user_data.get('is_banned') else 'Faol'}</b>"
        )
    else:
        text = "❌ Foydalanuvchi topilmadi."
    await message.answer(text, parse_mode="HTML")
    await state.clear()

# 3. ➕ Balans qo'shish
@admin_router.message(State("*"), F.text == "➕ Balans qo'shish")
async def start_add_bal(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.set_state(AdminStates.waiting_add_bal_user)
    await message.answer("➕ Balans qo'shish uchun foydalanuvchi ID sini kiriting:")

@admin_router.message(AdminStates.waiting_add_bal_user)
async def process_add_bal_user(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Noto'g'ri ID. Faqat raqam kiriting:")
        return
    await state.update_data(target_user_id=int(message.text))
    await state.set_state(AdminStates.waiting_add_bal_amount)
    await message.answer("💰 Qo'shiladigan summa miqdorini kiriting (so'mda):")

@admin_router.message(AdminStates.waiting_add_bal_amount)
async def process_add_bal_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("❌ Noto'g'ri summa format. Qayta kiriting (Masalan: 5000 yoki 5000.5):")
        return

    data = await state.get_data()
    target_id = data.get("target_user_id")
    
    db.update_user_balance(target_id, amount)
    await message.answer(f"✅ User <code>{target_id}</code> balansiga <b>{amount} so'm</b> qo'shildi!", parse_mode="HTML")
    try:
        await message.bot.send_message(target_id, f"🎉 Admin tomonidan balansingizga <b>{amount} so'm</b> qo'shildi!", parse_mode="HTML")
    except Exception:
        pass
    await state.clear()

# 4. ➖ Balans ayirish
@admin_router.message(State("*"), F.text == "➖ Balans ayirish")
async def start_deduct_bal(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.set_state(AdminStates.waiting_deduct_bal_user)
    await message.answer("➖ Balans ayirish uchun foydalanuvchi ID sini kiriting:")

@admin_router.message(AdminStates.waiting_deduct_bal_user)
async def process_deduct_bal_user(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Noto'g'ri ID. Faqat raqam kiriting:")
        return
    await state.update_data(target_user_id=int(message.text))
    await state.set_state(AdminStates.waiting_deduct_bal_amount)
    await message.answer("💰 Ayiriladigan summa miqdorini kiriting:")

@admin_router.message(AdminStates.waiting_deduct_bal_amount)
async def process_deduct_bal_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("❌ Noto'g'ri summa. Qayta kiriting:")
        return

    data = await state.get_data()
    target_id = data.get("target_user_id")
    
    db.update_user_balance(target_id, -amount)
    await message.answer(f"✅ User <code>{target_id}</code> balansidan <b>{amount} so'm</b> ayirildi!", parse_mode="HTML")
    await state.clear()

# 5. 🚫 Userni Bloklash
@admin_router.message(State("*"), F.text == "🚫 Userni Bloklash")
async def ban_user_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.set_state(AdminStates.waiting_ban_user)
    await message.answer("Bloklanadigan foydalanuvchi ID sini kiriting:")

@admin_router.message(AdminStates.waiting_ban_user)
async def process_ban_user(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Noto'g'ri ID. Faqat raqam kiriting:")
        return
    user_id = int(message.text)
    db.set_user_ban_status(user_id, True)
    await message.answer(f"🚫 Foydalanuvchi <code>{user_id}</code> bloklandi.", parse_mode="HTML")
    await state.clear()

# 6. 💳 API Balans
@admin_router.message(State("*"), F.text == "💳 API Balans")
async def check_api_balance(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.clear()
    api_url = db.get_setting("smm_api_url")
    api_key = db.get_setting("smm_api_key")
    
    try:
        res = requests.post(api_url, data={"key": api_key, "action": "balance"}, timeout=10).json()
        bal = res.get("balance", "Noma'lum")
        curr = res.get("currency", "USD")
        await message.answer(f"💳 <b>SMM Panel API Balansingiz:</b> {bal} {curr}", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ API balansni olishda xatolik: {e}")

# 7. ⚙️ API Sozlamalari
@admin_router.message(State("*"), F.text == "⚙️ API Sozlamalari")
async def api_settings_menu(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.clear()
    url = db.get_setting("smm_api_url")
    key = db.get_setting("smm_api_key")
    await message.answer(f"⚙️ <b>Hozirgi API URL:</b> <code>{url}</code>\n🔑 <b>API Key:</b> <code>{key}</code>", parse_mode="HTML")

# 8. 📈 Ustama foizi (Natsenka)
@admin_router.message(State("*"), F.text == "📈 Ustama Foizi (Natsenka)")
async def start_set_markup(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    current_markup = db.get_setting("markup_percent") or "0"
    await state.set_state(AdminStates.waiting_markup_percent)
    await message.answer(f"📈 Hozirgi ustama foizi: <b>{current_markup}%</b>\n\nYangi foizni kiriting (Masalan: 20):", parse_mode="HTML")

@admin_router.message(AdminStates.waiting_markup_percent)
async def process_set_markup(message: Message, state: FSMContext):
    db.set_setting("markup_percent", message.text.strip())
    await message.answer(f"✅ Ustama foizi <b>{message.text.strip()}%</b> ga o'zgartirildi!", parse_mode="HTML")
    await state.clear()

# 9. 💳 Karta Sozlamalari
@admin_router.message(State("*"), F.text == "💳 Karta Sozlamalari")
async def set_card_details(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.set_state(AdminStates.waiting_card_number)
    await message.answer("💳 Yangi karta raqamini kiriting:")

@admin_router.message(AdminStates.waiting_card_number)
async def process_card_number(message: Message, state: FSMContext):
    db.set_setting("card_number", message.text.strip())
    await state.set_state(AdminStates.waiting_card_name)
    await message.answer("👤 Karta egasining ism-sharifini kiriting:")

@admin_router.message(AdminStates.waiting_card_name)
async def process_card_name(message: Message, state: FSMContext):
    db.set_setting("card_holder", message.text.strip())
    await message.answer("✅ Karta rekvizitlari muvaffaqiyatli yangilandi!", parse_mode="HTML")
    await state.clear()

# 10. 📢 Xabar Tarqatish
@admin_router.message(State("*"), F.text == "📢 Xabar Tarqatish")
async def start_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.set_state(AdminStates.waiting_broadcast_msg)
    await message.answer("📢 Tarqatiladigan xabarni (matn, rasm yoki forward) yuboring:")

@admin_router.message(AdminStates.waiting_broadcast_msg)
async def process_broadcast(message: Message, state: FSMContext):
    users = db.get_all_user_ids()
    count = 0
    await message.answer("🚀 Xabar tarqatish boshlandi...")
    for uid in users:
        try:
            await message.copy_to(chat_id=uid)
            count += 1
        except Exception:
            continue
    await message.answer(f"✅ Xabar <b>{count} ta</b> foydalanuvchiga yetkazildi!", parse_mode="HTML")
    await state.clear()

# 11. 🎁 Promokod Yaratish
@admin_router.message(State("*"), F.text == "🎁 Promokod Yaratish")
async def start_create_promo(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.set_state(AdminStates.waiting_promo_code)
    await message.answer("🎁 Yangi promokod nomini kiriting (Masalan: BONUS2026):")

@admin_router.message(AdminStates.waiting_promo_code)
async def process_promo_code(message: Message, state: FSMContext):
    await state.update_data(promo_name=message.text.strip().upper())
    await state.set_state(AdminStates.waiting_promo_amount)
    await message.answer("💰 Promokod qiymatini (so'mda) kiriting:")

@admin_router.message(AdminStates.waiting_promo_amount)
async def process_promo_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("❌ Noto'g'ri summa. Qayta kiriting:")
        return

    data = await state.get_data()
    promo_name = data.get("promo_name")
    
    db.add_promo_code(promo_name, amount)
    await message.answer(f"✅ Promokod yaratildi:\n🔑 Kod: <code>{promo_name}</code>\n💰 Summa: <b>{amount} so'm</b>", parse_mode="HTML")
    await state.clear()

# 12. 🔎 Buyurtmani tekshirish
@admin_router.message(State("*"), F.text == "🔎 Buyurtmani tekshirish")
async def start_check_order(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.set_state(AdminStates.waiting_order_check_id)
    await message.answer("🔎 SMM Panel buyurtma ID raqamini kiriting:")

@admin_router.message(AdminStates.waiting_order_check_id)
async def process_check_order(message: Message, state: FSMContext):
    order_id = message.text.strip()
    api_url = db.get_setting("smm_api_url")
    api_key = db.get_setting("smm_api_key")
    
    try:
        res = requests.post(api_url, data={"key": api_key, "action": "status", "order": order_id}, timeout=10).json()
        status = res.get("status", "Topilmadi")
        remains = res.get("remains", "0")
        await message.answer(f"📦 Buyurtma ID: <code>{order_id}</code>\n📊 Holati: <b>{status}</b>\n📉 Qolgan miqdor: {remains}", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Tekshirishda xatolik: {e}")
    await state.clear()

# 13. 💸 Pulni qaytarish (Refund)
@admin_router.message(State("*"), F.text == "💸 Pulni qaytarish (Refund)")
async def start_refund(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.set_state(AdminStates.waiting_refund_order_id)
    await message.answer("💸 Bekor qilinadigan buyurtma ID va summa miqdorini quyidagicha kiriting:\n\n<code>USER_ID SUMMA</code> (Masalan: <code>6911619468 5000</code>)")

@admin_router.message(AdminStates.waiting_refund_order_id)
async def process_refund(message: Message, state: FSMContext):
    try:
        parts = message.text.split()
        if len(parts) != 2:
            raise ValueError("Ikkita qiymat kiritilishi shart")
        
        user_id = int(parts[0])
        amount = float(parts[1])
        
        db.update_user_balance(user_id, amount)
        await message.answer(f"✅ User <code>{user_id}</code> ga <b>{amount} so'm</b> qaytarildi!", parse_mode="HTML")
        try:
            await message.bot.send_message(user_id, f"💸 Bekor qilingan buyurtma uchun balansingizga <b>{amount} so'm</b> qaytarildi!", parse_mode="HTML")
        except Exception:
            pass
        await state.clear()
    except Exception as e:
        await message.answer(f"❌ Xato format. Namuna: <code>6911619468 5000</code>\nQaytadan kiriting:", parse_mode="HTML")

# 14. 🛠 Texnik rejim
@admin_router.message(State("*"), F.text == "🛠 Texnik rejim")
async def toggle_maintenance(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): 
        return
    await state.clear()
    current = db.get_setting("maintenance_mode") or "off"
    new_status = "on" if current == "off" else "off"
    db.set_setting("maintenance_mode", new_status)
    await message.answer(f"🛠 Texnik rejim <b>{new_status.upper()}</b> holatiga o'tkazildi!", parse_mode="HTML")
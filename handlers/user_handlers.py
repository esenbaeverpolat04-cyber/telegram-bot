import requests
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database.queries as db
from config import ADMIN_ID

router = Router()

class OrderState(StatesGroup):
    waiting_quantity = State()
    waiting_link = State()

class DepositState(StatesGroup):
    waiting_amount = State()
    waiting_receipt = State()

# 🔘 Asosiy menyular
user_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📲 Pul kiritsh"), KeyboardButton(text="🌐 Xizmatlar")],
        [KeyboardButton(text="💳 Hisobim"), KeyboardButton(text="🛒 Buyurtmalarim")],
        [KeyboardButton(text="👤 Foydali bo'lim")]
    ],
    resize_keyboard=True
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📲 Pul kiritsh"), KeyboardButton(text="🌐 Xizmatlar")],
        [KeyboardButton(text="💳 Hisobim"), KeyboardButton(text="🛒 Buyurtmalarim")],
        [KeyboardButton(text="👤 Foydali bo'lim")],
        [KeyboardButton(text="👨‍💻 Admin Panel")]
    ],
    resize_keyboard=True
)

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username
    db.add_user(user_id, username)
    kb = admin_kb if user_id == ADMIN_ID else user_kb

    await message.answer(
        f"<b>Foydali xizmatlarimizni tanlaganingizdan mamnunmiz!</b>\n"
        f"Siz uchun sifatli, ishonchli va qulay xizmatlarni taqdim etamiz.\n\n"
        f"👇 Davom etish uchun kerakli xizmatni tanlang.",
        reply_markup=kb,
        parse_mode="HTML"
    )

@router.message(F.text == "⬅️ Bosh menyu")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    kb = admin_kb if message.from_user.id == ADMIN_ID else user_kb
    await message.answer("Asosiy menyudasiz:", reply_markup=kb)

# 💳 Hisobim bo'limi
@router.message(F.text == "💳 Hisobim")
async def balance_handler(message: Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    balance = user[2] if user else 0

    text = (
        f"🆔 <b>ID raqamingiz:</b> <code>{user_id}</code> ❞\n\n"
        f"💵 <b>Balansingiz:</b> {balance} so'm ❞\n\n"
        f"🌐 <b>Buyurtmalaringiz:</b> 0 ta ❞\n\n"
        f"👤 <b>Takliflaringiz soni:</b> 0 ta ❞\n\n"
        f"🎁 <b>Chegirmangiz foizi:</b> 0% ❞\n\n"
        f"💳 <b>Kiritgan pullaringiz:</b> 0 so'm ❞\n\n"
        f"🎉 <b>Siz shu kungacha 0 so'm keshbek olgansiz</b> ❞"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Hisobni To'ldirish", callback_data="deposit_menu")],
        [InlineKeyboardButton(text="🔄 Pul o'tkazish", callback_data="transfer_money")]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

# 📲 To'lov usulini tanlash menyusi
@router.message(F.text == "📲 Pul kiritsh")
@router.callback_query(F.data == "deposit_menu")
async def deposit_menu_handler(event: Message | CallbackQuery):
    user_id = event.from_user.id
    text = (
        f"Botimizdan hisobingizni to'ldirib bot xizmatlaridan to'liq foydalanishingiz mumkin, "
        f"botda hisobni to'ldirish qulay va 100% xafsiz sanaladi ✅\n\n"
        f"🆔 <b>ID raqamingiz:</b> <code>{user_id}</code>"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 KARTA ORQALI TO'LOV", callback_data="pay_card")],
        [InlineKeyboardButton(text="💵 Pul kiritish [ avto ]", callback_data="pay_auto")],
        [InlineKeyboardButton(text="🔴 Click [AVTO]", callback_data="pay_click")],
        [InlineKeyboardButton(text="🔵 Payme [ avto ]", callback_data="pay_payme")],
        [InlineKeyboardButton(text="🌐 Сбер Банк", callback_data="pay_sber")],
        [InlineKeyboardButton(text="⭐ Stars orqali [ Avto ]", callback_data="pay_stars")],
        [InlineKeyboardButton(text="☎️ Admin yordamida", callback_data="pay_admin")]
    ])

    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await event.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await event.answer()

# 💳 Karta orqali to'lov rekvizitlari
@router.callback_query(F.data == "pay_card")
async def pay_card_handler(callback: CallbackQuery):
    text = (
        f"💳 <b>Hamyon, karta</b> 👈\n"
        f"<code>9860196601822980</code> ❞\n"
        f"<b>Nishanov.Sh</b>\n\n"
        f"🤝 <b>Hisobingizni muvaffaqiyatli to'ldirish uchun quyidagi harakatlarni amalga oshiring:</b> 👈\n\n"
        f"1) Pul miqdorini tepadagi Hamyonga tashlang.\n"
        f"2) « ✅ To'lov qildim » tugmasini bosing;\n"
        f"4) Qancha pul miqdori yuborganingizni kiriting;\n"
        f"5) To'lov haqidagi suratni botga yuboring;\n"
        f"6) Operator tomonidan to'lov tasdiqlanishini kuting! Uzog'i 30-40minutda tasdiqlanadi.\n\n"
        f"🔹 <b>Minimal:</b> 500 so'm\n"
        f"🔹 <b>Maksimal:</b> 1,000,000 so'm"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ To'lov qildim", callback_data="confirm_card_payment")],
        [InlineKeyboardButton(text="↔️ Orqaga", callback_data="deposit_menu")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()

# 📄 To'lov miqdorini so'rash FSM
@router.callback_query(F.data == "confirm_card_payment")
async def ask_deposit_amount(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DepositState.waiting_amount)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏩ Orqaga", callback_data="deposit_menu")]
    ])

    await callback.message.edit_text(
        "📄 <b>To'lov miqdorini kiriting:</b>\n\n"
        "🔹 Minimal: 500 so'm\n"
        "🔹 Maksimal: 1000000 so'm",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(DepositState.waiting_amount)
async def process_deposit_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Iltimos, faqat raqam kiriting (masalan: 5000):")
        return

    amount = int(message.text)
    if amount < 500 or amount > 1000000:
        await message.answer("❌ Miqdor 500 so'm va 1 000 000 so'm orasida bo'lishi kerak.")
        return

    await state.update_data(deposit_amount=amount)
    await state.set_state(DepositState.waiting_receipt)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏩ Orqaga", callback_data="deposit_menu")]
    ])

    await message.answer(
        "📄 <b>To'lov uchun chek rasmini yuboring:</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# 📄 Chek rasmini qabul qilish va Adminga yuborish
@router.message(DepositState.waiting_receipt, F.photo)
async def process_deposit_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    amount = data.get("deposit_amount")
    photo_id = message.photo[-1].file_id
    user_id = message.from_user.id
    username = message.from_user.username or "Mavjud emas"

    # Admin uchun tasdiqlash tugmalari
    admin_confirm_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_dep_{user_id}_{amount}")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_dep_{user_id}")]
    ])

    # Adminga yuborish
    await message.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_id,
        caption=(
            f"📥 <b>Yangi to'lov cheki!</b>\n\n"
            f"👤 Foydalanuvchi: @{username} (<code>{user_id}</code>)\n"
            f"💰 Summa: <b>{amount} so'm</b>"
        ),
        reply_markup=admin_confirm_kb,
        parse_mode="HTML"
    )

    await message.answer("✅ <b>Chek adminga yuborildi. Tekshiruvdan so'ng hisobingiz to'ldiriladi!</b>", parse_mode="HTML")
    await state.clear()

# Admin to'lovni tasdiqlashi/rad etishi
@router.callback_query(F.data.startswith("approve_dep_"))
async def approve_deposit(callback: CallbackQuery):
    parts = callback.data.split("_")
    user_id = int(parts[2])
    amount = float(parts[3])

    db.update_user_balance(user_id, amount)
    
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ <b>To'lov tasdiqlandi va balans to'ldirildi!</b>", parse_mode="HTML")
    await callback.bot.send_message(user_id, f"🎉 Hisobingiz muvaffaqiyatli <b>{amount} so'm</b>ga to'ldirildi!", parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("reject_dep_"))
async def reject_deposit(callback: CallbackQuery):
    parts = callback.data.split("_")
    user_id = int(parts[2])

    await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ <b>To'lov rad etildi!</b>", parse_mode="HTML")
    await callback.bot.send_message(user_id, "❌ Siz yuborgan to'lov cheki rad etildi.", parse_mode="HTML")
    await callback.answer()

# 🌐 1-bosqich: Platformalar menyusi
@router.message(F.text == "🌐 Xizmatlar")
@router.callback_query(F.data == "main_services")
async def show_main_services(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 TELEGRAM 🔵", callback_data="platform_telegram")],
        [InlineKeyboardButton(text="🔴 INSTAGRAM 🔴", callback_data="platform_instagram")],
        [InlineKeyboardButton(text="⚫️ TIK TOK ⚫️", callback_data="platform_tiktok")],
        [InlineKeyboardButton(text="🟣 YOU TUBE 🟣", callback_data="platform_youtube")]
    ])
    text = "💎 <b>Foydali xizmatlarimizni tanlaganingizdan mamnunmiz!</b>\n\n👇 Davom etish uchun kerakli xizmatni tanlang:"
    if isinstance(event, Message):
        await event.answer(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await event.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
        await event.answer()

# 🌐 2-bosqich: Platformaga tegishli kategoriyalar ro'yxati
@router.callback_query(F.data.startswith("platform_"))
async def platform_selected(callback: CallbackQuery):
    platform = callback.data.split("_")[1].upper()
    api_url = db.get_setting("smm_api_url")
    api_key = db.get_setting("smm_api_key")
    
    platform_headers = {
        "TELEGRAM": "💙 TELEGRAM 💙 bo'limiga xush kelibsiz!\n📋 Kerakli xizmat turini tanlang",
        "INSTAGRAM": "❤️ INSTAGRAM ❤️ bo'limiga xush kelibsiz!\n📋 Kerakli xizmat turini tanlang",
        "TIKTOK": "🖤 TIK TOK 🖤 bo'limiga xush kelibsiz!\n📋 Kerakli xizmat turini tanlang",
        "YOUTUBE": "💗 YOU TUBE 💗 bo'limiga xush kelibsiz!\n📋 Kerakli xizmat turini tanlang"
    }
    header_text = platform_headers.get(platform, f"🔹 <b>{platform}</b> bo'limi:")

    search_terms = {
        "TELEGRAM": ["TELEGRAM", "TG"],
        "INSTAGRAM": ["INSTAGRAM", "INSTA"],
        "TIKTOK": ["TIK TOK", "TIKTOK", "TT"],
        "YOUTUBE": ["YOU TUBE", "YOUTUBE", "YT"]
    }
    terms = search_terms.get(platform, [platform])

    try:
        response = requests.post(api_url, data={"key": api_key, "action": "services"}, timeout=10).json()
        if isinstance(response, list):
            categories = []
            for s in response:
                cat = s.get('category', '')
                cat_upper = cat.upper()
                if any(term in cat_upper for term in terms) and cat not in categories:
                    categories.append(cat)
            
            if not categories:
                for s in response:
                    cat = s.get('category', '')
                    if cat not in categories:
                        categories.append(cat)

            inline_keyboard = []
            for index, cat in enumerate(categories):
                inline_keyboard.append([InlineKeyboardButton(text=cat, callback_data=f"cat_{index}_{platform}")])
            
            inline_keyboard.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="main_services")])
            keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
            
            await callback.message.edit_text(header_text, reply_markup=keyboard, parse_mode="HTML")
            await callback.answer()
    except Exception as e:
        await callback.answer(f"Xatolik: {e}", show_alert=True)

# 🌐 3-bosqich: Tariflar ro'yxati
@router.callback_query(F.data.startswith("cat_"))
async def category_callback(callback: CallbackQuery):
    parts = callback.data.split("_")
    cat_index = int(parts[1])
    platform = parts[2]
    
    api_url = db.get_setting("smm_api_url")
    api_key = db.get_setting("smm_api_key")

    search_terms = {
        "TELEGRAM": ["TELEGRAM", "TG"],
        "INSTAGRAM": ["INSTAGRAM", "INSTA"],
        "TIKTOK": ["TIK TOK", "TIKTOK", "TT"],
        "YOUTUBE": ["YOU TUBE", "YOUTUBE", "YT"]
    }
    terms = search_terms.get(platform, [platform])
    
    try:
        response = requests.post(api_url, data={"key": api_key, "action": "services"}, timeout=10).json()
        if isinstance(response, list):
            categories = []
            for s in response:
                cat = s.get('category', '')
                cat_upper = cat.upper()
                if any(term in cat_upper for term in terms) and cat not in categories:
                    categories.append(cat)
            
            if not categories or cat_index >= len(categories):
                categories = []
                for s in response:
                    cat = s.get('category', '')
                    if cat not in categories:
                        categories.append(cat)

            selected_category = categories[cat_index]
            inline_keyboard = []
            
            for s in response:
                if s.get('category') == selected_category:
                    s_id = s.get('service')
                    s_name = s.get('name')
                    s_rate = s.get('rate')
                    inline_keyboard.append([InlineKeyboardButton(
                        text=f"{s_name} - {s_rate} so'm", 
                        callback_data=f"srv_{s_id}"
                    )])
            
            inline_keyboard.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data=f"platform_{platform.lower()}")])
            keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
            
            await callback.message.edit_text(
                f"📋 <b>Quyidagi tariflardan birini tanlang!</b>\nNarxlar 1000 tasi uchun berilgan.", 
                reply_markup=keyboard, 
                parse_mode="HTML"
            )
            await callback.answer()
    except Exception as e:
        await callback.answer(f"Xatolik: {e}", show_alert=True)

# 🌐 4-bosqich: Xizmat tavsifi
@router.callback_query(F.data.startswith("srv_"))
async def service_detail_callback(callback: CallbackQuery, state: FSMContext):
    service_id = callback.data.split("_")[1]
    api_url = db.get_setting("smm_api_url")
    api_key = db.get_setting("smm_api_key")
    
    try:
        response = requests.post(api_url, data={"key": api_key, "action": "services"}, timeout=10).json()
        target_service = None
        if isinstance(response, list):
            for s in response:
                if str(s.get('service')) == str(service_id):
                    target_service = s
                    break
        
        if target_service:
            await state.update_data(selected_service=target_service, active_service_id=str(service_id))
            
            rate = float(target_service.get('rate', 0))
            min_val = target_service.get('min', 10)
            max_val = target_service.get('max', 100000)
            name = target_service.get('name')
            
            text = (
                f"📌 <b>Xizmat nomi: {name}</b>\n"
                f"🔑 Xizmat IDsi: <code>{service_id}</code>\n"
                f"💵 Narxi (1000 ta): {rate} so'm\n\n"
                f"📋 <b>Xizmat haqida ma'lumotlar:</b>\n"
                f"🔹 Sifatli xizmat ko'rsatish 🚀\n\n"
                f"🔻 Minimal: {min_val} ta\n"
                f"🔺 Maksimal: {max_val} ta"
            )
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Buyurtma berish", callback_data=f"order_{service_id}")],
                [InlineKeyboardButton(text="◀️ Orqaga", callback_data="main_services")]
            ])
            
            await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
            await callback.answer()
    except Exception as e:
        await callback.answer(f"Xatolik: {e}", show_alert=True)

# 🌐 5-bosqich: Miqdorni so'rash
@router.callback_query(F.data.startswith("order_"))
async def start_order(callback: CallbackQuery, state: FSMContext):
    service_id = callback.data.split("_")[1]
    await state.update_data(active_service_id=str(service_id))
    await state.set_state(OrderState.waiting_quantity)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="main_services")]
    ])
    
    await callback.message.edit_text(
        "⬇️ <b>Kerakli buyurtma miqdorini kiriting:</b>\n\nNa'muna: <code>1500</code>", 
        reply_markup=keyboard, 
        parse_mode="HTML"
    )
    await callback.answer()

# 🌐 6-bosqich: Miqdorni tekshirish
@router.message(OrderState.waiting_quantity)
async def process_quantity(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Iltimos, faqat raqam kiriting (masalan: 1500):")
        return

    quantity = int(message.text)
    data = await state.get_data()
    service = data.get("selected_service")
    
    if not service:
        await message.answer("❌ Xatolik yuz berdi. Qaytatdan boshlang.")
        await state.clear()
        return

    rate = float(service.get('rate', 0))
    total_price = (quantity / 1000) * rate
    
    user = db.get_user(message.from_user.id)
    user_balance = float(user[2]) if user else 0.0

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="main_services")]
    ])

    if user_balance < total_price:
        await message.answer(
            f"❌ <b>Yetarli mablag' mavjud emas</b>\n\n"
            f"💰 Buyurtma narxi: <b>{total_price:.2f} so'm</b>\n"
            f"💳 Sizning balans: <b>{user_balance:.2f} so'm</b>\n\n"
            f"👇 Boshqa miqdor kiritib ko'ring:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await state.update_data(quantity=quantity, total_price=total_price)
        await state.set_state(OrderState.waiting_link)
        await message.answer(
            f"✅ Miqdor qabul qilindi ({quantity} ta).\n"
            f"💰 Jami narx: <b>{total_price:.2f} so'm</b>\n\n"
            f"🔗 Endi buyurtma uchun havola (link)ni yuboring:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )

# 🌐 7-bosqich: Linkni qabul qilish va API'ga yuborish
@router.message(OrderState.waiting_link)
async def process_link(message: Message, state: FSMContext):
    link = message.text.strip()
    data = await state.get_data()
    
    service = data.get("selected_service", {})
    quantity = data.get("quantity")
    total_price = data.get("total_price")
    service_id = data.get("active_service_id") or service.get('service')
    
    user_id = message.from_user.id
    
    api_url = db.get_setting("smm_api_url")
    api_key = db.get_setting("smm_api_key")
    
    try:
        payload = {
            "key": api_key,
            "action": "add",
            "service": int(service_id) if str(service_id).isdigit() else service_id,
            "link": link,
            "quantity": int(quantity)
        }
        response = requests.post(api_url, data=payload, timeout=15).json()
        
        if isinstance(response, dict) and "order" in response:
            order_id = response["order"]
            db.update_user_balance(user_id, -total_price)
            
            await message.answer(
                f"✅ <b>Buyurtmangiz muvaffaqiyatli qabul qilindi!</b>\n\n"
                f"🆔 Buyurtma ID: <code>{order_id}</code>\n"
                f"📌 Xizmat: {service.get('name', 'SMM Xizmat')}\n"
                f"🔢 Miqdor: {quantity} ta\n"
                f"🔗 Havola: {link}\n"
                f"💰 Yechildi: <b>{total_price:.2f} so'm</b>",
                parse_mode="HTML"
            )
            await state.clear()
        else:
            error_msg = response.get("error", "Noma'lum xatolik") if isinstance(response, dict) else str(response)
            await message.answer(f"❌ <b>API Xatolik:</b> {error_msg}\n\nIltimos, qaytadan urinib ko'ring.")
            await state.clear()

    except Exception as e:
        await message.answer(f"❌ Buyurtma yuborishda xatolik yuz berdi: {e}")
        await state.clear()

@router.message(F.text == "🛒 Buyurtmalarim")
async def my_orders_handler(message: Message):
    await message.answer("🛒 Sizda hozircha faol buyurtmalar yo'q.", parse_mode="HTML")

@router.message(F.text == "👤 Foydali bo'lim")
async def useful_section_handler(message: Message):
    await message.answer("ℹ️ Bu yerda foydali ma'lumotlar va ko'rsatmalar bo'ladi.", parse_mode="HTML")
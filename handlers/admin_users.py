from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database.queries as db
from config import ADMIN_ID

router = Router()

class UserManageStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_balance_change = State()

def user_action_kb(user_id: int, is_banned: int) -> InlineKeyboardMarkup:
    ban_btn_text = "🟢 Blokdan chiqarish" if is_banned else "🔴 Bloklash (Ban)"
    keyboard = [
        [InlineKeyboardButton(text="💵 Balansni o'zgartirish", callback_data=f"change_bal_{user_id}")],
        [InlineKeyboardButton(text=ban_btn_text, callback_data=f"toggle_ban_{user_id}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(F.text == "🔍 User Qidirish")
async def start_user_search(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(UserManageStates.waiting_for_user_id)
    await message.answer("🔎 Foydalanuvchi Telegram ID raqamini kiriting:")

@router.message(UserManageStates.waiting_for_user_id)
async def process_user_search(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("⚠️ Iltimos, faqat raqam kiriting.")
        return
    
    target_id = int(message.text)
    user = db.get_user(target_id)
    
    if not user:
        await message.answer("❌ Foydalanuvchi bazadan topilmadi.")
        await state.clear()
        return

    status_str = "🔴 Bloklangan" if user[4] else "🟢 Faol"
    info_text = (
        f"👤 <b>Foydalanuvchi:</b>\n\n"
        f"🆔 ID: <code>{user[0]}</code>\n"
        f"👤 Username: @{user[1] if user[1] else 'Mavjud emas'}\n"
        f"💰 Balans: <b>{user[2]} so'm</b>\n"
        f"📌 Holati: {status_str}"
    )
    await message.answer(info_text, reply_markup=user_action_kb(user[0], user[4]))
    await state.clear()

@router.callback_query(F.data.startswith("toggle_ban_"))
async def handle_toggle_ban(callback: CallbackQuery):
    target_id = int(callback.data.split("_")[2])
    user = db.get_user(target_id)
    new_ban_status = 0 if user[4] else 1
    
    db.set_ban_status(target_id, new_ban_status)
    action_msg = "bloklandi" if new_ban_status else "blokdan chiqarildi"
    await callback.answer(f"Foydalanuvchi {action_msg}!", show_alert=True)

@router.callback_query(F.data.startswith("change_bal_"))
async def handle_change_balance_start(callback: CallbackQuery, state: FSMContext):
    target_id = int(callback.data.split("_")[2])
    await state.set_state(UserManageStates.waiting_for_balance_change)
    await state.update_data(target_id=target_id)
    await callback.message.answer("Qo'shish uchun masalan `10000`, ayirish uchun `-5000` kiriting:")
    await callback.answer()

@router.message(UserManageStates.waiting_for_balance_change)
async def process_balance_change(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("⚠️ Faqat raqam kiriting.")
        return

    data = await state.get_data()
    db.update_user_balance(data["target_id"], amount)
    await message.answer("✅ Balans muvaffaqiyatli o'zgartirildi!")
    await state.clear()
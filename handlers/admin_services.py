import requests
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database.queries as db
from config import ADMIN_ID

router = Router()

class ServiceManageStates(StatesGroup):
    waiting_api_key = State()
    waiting_broadcast_text = State()



@router.message(F.text == "⚙️ API Sozlamalari")
async def smm_api_settings(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    api_url = db.get_setting("smm_api_url")
    api_key = db.get_setting("smm_api_key")
    await message.answer(
        f"🛠 <b>SMM API Sozlamalari:</b>\n\n"
        f"🌐 API URL: <code>{api_url}</code>\n"
        f"🔑 API KEY: <code>{api_key}</code>"
    )

@router.message(F.text == "💳 API Balans")
async def check_api_balance(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    api_url = db.get_setting("smm_api_url")
    api_key = db.get_setting("smm_api_key")
    try:
        response = requests.post(api_url, data={"key": api_key, "action": "balance"}, timeout=10).json()
        if "balance" in response:
            await message.answer(f"💰 <b>SMM Saytdagi Balans:</b> {response['balance']} {response.get('currency', 'USD')}")
        else:
            await message.answer("❌ API Key xato yoki javob olinmadi.")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

@router.message(F.text == "🔑 API Keyni o'zgartirish")
async def change_api_key_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(ServiceManageStates.waiting_api_key)
    await message.answer("Yangi SMM API Keyni kiriting:")

@router.message(ServiceManageStates.waiting_api_key)
async def change_api_key_finish(message: Message, state: FSMContext):
    db.update_setting("smm_api_key", message.text.strip())
    await message.answer("✅ API Key yangilandi!", reply_markup=admin_full_kb)
    await state.clear()

@router.message(F.text == "📦 Xizmatlar ro'yxati")
async def fetch_smm_services(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    api_url = db.get_setting("smm_api_url")
    api_key = db.get_setting("smm_api_key")
    try:
        response = requests.post(api_url, data={"key": api_key, "action": "services"}, timeout=10).json()
        if isinstance(response, list) and len(response) > 0:
            text = "📦 <b>API dagi ba'zi xizmatlar:</b>\n\n"
            for s in response[:15]: # Faqat dastlabki 15 tasini ko'rsatamiz
                text.escape() if hasattr(text, 'escape') else None
                text += f"🆔 ID: <b>{s.get('service')}</b> | {s.get('name')[:30]}... | 💵 Rate: {s.get('rate')}\n"
            await message.answer(text)
        else:
            await message.answer("❌ Xizmatlar ro'yxatini olishda xatolik yuz berdi yoki bo'sh.")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")

@router.message(F.text == "📢 Xabar yuborish")
async def broadcast_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(ServiceManageStates.waiting_broadcast_text)
    await message.answer("📢 Barcha foydalanuvchilarga yuborish uchun matn yoki rasm yuboring:")

@router.message(ServiceManageStates.waiting_broadcast_text)
async def broadcast_finish(message: Message, state: FSMContext):
    # Bu yerda bazadagi barcha foydalanuvchilarga xabar tarqatish mantiigini yozamiz
    await message.answer("✅ Xabar tarqatish boshlandi (hozircha test rejimida).", reply_markup=admin_full_kb)
    await state.clear()
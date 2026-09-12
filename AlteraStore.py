import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
import os
import asyncio
import aiosqlite
import logging
import aiohttp
from aiohttp import web
import html
import re
import time



import json
import base64
import hashlib
import secrets
import pyotp
from contextvars import ContextVar



from urllib.parse import quote  # Понадобится для безопасного кодирования текста ссылки
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Dict, Optional, Tuple, List, Any
from contextlib import asynccontextmanager
from asyncio import Semaphore
from functools import lru_cache, wraps
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, BotCommand, FSInputFile, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, LabeledPrice, LinkPreviewOptions, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import hbold, hcode, hlink
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter

BOT_TOKEN = '8758197515:AAH_t6JAkbgUFLJua91kTr1OHJCCF7naCMM'
XROCKET_PAY_TOKEN = '3b1dafa8033b841c69982b273'
ADMIN_ID = 8564318687
# Telegram Stars are charged as an integer amount; keep the business balance in USDT.
STAR_USDT_RATE = float(os.getenv("STAR_USDT_RATE", "100"))

# Константы
PAYMENT_CHECK_INTERVAL = 15
PAYMENT_CHECK_ATTEMPTS = 60
MAX_PAYMENT_WAIT_TIME = PAYMENT_CHECK_INTERVAL * PAYMENT_CHECK_ATTEMPTS
MAX_QUANTITY_PER_PURCHASE = 100
# Used by legacy admin/database handlers kept for compatibility with old records.
MIN_PREORDER_QUANTITY = 5
MAX_PROMO_ATTEMPTS = 5
PROMO_BLOCK_TIME = 1800
RATE_LIMIT = 2
CLEANUP_INTERVAL = 1800
MAX_CONCURRENT_PAYMENT_CHECKS = 15
DB_VERSION = 2
MAX_BULK_ADD = 5000

AGREEMENT_URL = "https://telegra.ph/Polzovatelskoe-soglashenie-Telegram-bota-AlteraStoreBot-09-07"
PRIVACY_POLICY_URL = "https://telegra.ph/Politika-konfidencialnosti-Telegram-bota-AlteraStoreBot-09-07"
SUPPORT_URL = "https://t.me/EleghantHelpBot"
SUPPORT_ACCOUNT_URL = "https://t.me/EleghantSupport"
WEB_APP_URL = os.getenv("ALTERA_WEB_APP_URL", "").strip()

# --- РЕЖИМ ТЕХ. РАБОТ ---
MAINTENANCE_MODE = False

# --- КАСТОМНЫЕ ЭМОДЗИ (ПРЕМИУМ) ---
class CustomEmoji:
    CATALOG = "5431646131941556182"
    DISCOUNT = "5242602592357345985"
    PROFILE = "5275979556308674886"
    DEPOSIT = "5276398496008663230"
    HELP = "5276240711795107620"
    PZB = "5278753302023004775"
    PPZ = "5276240711795107620"
    PPA = "5278411813468269386"
    ACCEPT = "5206607081334906820"
    BACK = "5215248628548931525"
    START = "6035130900075777681"
    XROCKET_PAY = "5379612946747921985"
    BALANCE_PAY = "5276398496008663230"
    CHECKMARK = "5278411813468269386"
    GY = "5343742152985839675"
    GY_EMOJI = "5438434014220264821"
    MTS = "5262690652616931769"
    MEGAFON = "5470134961673612788"
    BEELINE = "5469796926272580161"
    YOTA = "5469769180783849063"
    T2 = "5440552665752820072"
    GUN = "5278753302023004775"
    PROFILE_EMOJI = "5213373634806061405"
    REGISTRATION = "5890937706803894250"
    CHECKPAY = "4924819078817777378"
    SHIELD = "5213464941515808062"
    CHECK = "5213056077809099062"
    LOCK = "4927470722906850798"
    UP = "4925115139503455129"
    TROPHY = "5278613311858959074"
    USER = "5278305362703835500"
    PLUS = "5397916757333654639"
    PROMO = "5276422526350681413"
    LINK = "5271604874419647061"
    MONEY = "5255933397750014894"
    WARNING = "5206702193385700709"
    QUESTION = "5242205011529719330"
    SHARE = "5213121284002583929"
    DIAMOND = "4924802255430880504"
    PIN = "5213301161527909232"
    SUPPORT = "5276240711795107620"
    TIME = "5316575093269214796"
    HISTORY = "5395444784611480792"
    SUB = "5278528159837348960"
    OK = "5276395476646653290"
    PIN_EMOJI = "5895440460322706085"
    BUYKB = "5312057711091813718"
    WITHDRAW = "5276398496008663230"
    BUYTAG = "5278613311858959074"
    EDIT = "5276395476646653290"
    SUPPORTlife = "5213218839889745971"
    SUPPORTbot = "5213281821290173707"
    SUPPORT_HEADER = "5213357627462947650"
    STARS_PAY = "5206476089127372379"
    TBANK = "5231008469875706287"
    CREATE_MIRROR = "5213464610803323563"
    REVIEW = "5213354182899179724"
    REF_WITHDRAW = "4924819078817777378"
    PROMO_CODE = "4924874531140535819"
    PURCHASE_HISTORY = "4925045788666496523"
    REFERRAL = "5213121284002583929"
    RATING = "5213085536989780516"
    PRICE = "4927200457794782747"
    STOCK = "4925163749943281335"
    EMPTY_HISTORY = "4925225477213259152"
    REFERRAL_LINK = "5213218839889745971"
    REFERRAL_USER = "5215340326100703398"
    REFERRAL_EARNINGS = "5213138867598694100"
    # Kept as visual fallbacks for historical records and migrated callbacks.
    PREORDER = "5278540791336165644"
    PREORDER_CLOCK = "4925068229870618117"
    PREORDER_CHECK = "5895713431264170680"
    PREORDER_BOX = "5278613311858959074"
    PREORDER_SETTINGS = "5902432207519093015"
    PREORDER_COMPLETED = "5895514131896733546"
    PREORDERCHECK = "5278540791336165644"
    TOTP = "5276220667182736079"
    ADDTOTP = "5278602437001767574"
    MYKEY = "5278227821364275264"
    BACKTOTP = "5278413853577734640"

PRODUCT_CATEGORY_EMOJIS = {
    1: "5312126452043363774",
    2: "5229218997521631084",
    3: "5280919528908267119",
    4: "5280716016177915458",
    5: "5244453379664534900",
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# The dispatcher injects the bot that received an update.  Keep it available to
# helper functions that historically used the module-level main bot.
_active_bot: ContextVar[Optional[Bot]] = ContextVar("active_bot", default=None)

def get_active_bot() -> Bot:
    return _active_bot.get() or bot

class BotContextMiddleware:
    async def __call__(self, handler, event: types.Update, data: dict):
        token = _active_bot.set(data.get("bot", bot))
        try:
            return await handler(event, data)
        finally:
            _active_bot.reset(token)

dp.update.outer_middleware(BotContextMiddleware())

# These commands are applied to the main bot and every mirror bot.
BOT_COMMANDS = [
    BotCommand(command="start", description="Запустить бота"),
    BotCommand(command="help", description="Поддержка"),
    BotCommand(command="profile", description="Мой профиль"),
    BotCommand(command="deposit", description="Пополнить баланс"),
    BotCommand(command="invoice", description="Создать счёт xRocket"),
    BotCommand(command="webapp", description="Открыть каталог"),
    BotCommand(command="cancel", description="Отменить действие"),
    BotCommand(command="admintools", description="Панель администратора"),
    BotCommand(command="userstats", description="Статистика бота (админ)"),
    BotCommand(command="userinfo", description="Информация о пользователе (админ)"),
    BotCommand(command="addstock", description="Добавить товар (админ)"),
    BotCommand(command="withdraws", description="Заявки на вывод (админ)"),
]

mirror_bots: Dict[int, Bot] = {}
mirror_polling_tasks: Dict[int, asyncio.Task] = {}

# --- MIDDLEWARE ДЛЯ ОТСЛЕЖИВАНИЯ ПОЛЬЗОВАТЕЛЕЙ ---

class ActivityTrackingMiddleware:
    async def __call__(self, handler, event: types.Update, data: dict):
        user_id = None
        if event.message and event.message.from_user:
            user_id = event.message.from_user.id
        elif event.callback_query and event.callback_query.from_user:
            user_id = event.callback_query.from_user.id
        
        if user_id:
            try:
                # Обновляем время последней активности
                await execute_query(
                    "UPDATE users SET last_activity = ? WHERE id = ?",
                    (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), user_id),
                    commit=True
                )
            except Exception as e:
                # Игнорируем ошибки, чтобы они не мешали работе бота
                logger.debug(f"Ошибка обновления активности: {e}")
        
        return await handler(event, data)

class UserTrackingMiddleware:
    async def __call__(self, handler, event: types.Update, data: dict):
        user_info = None
        event_type = "unknown"

        if event.message and event.message.from_user:
            user_info = event.message.from_user
            event_type = "message"
        elif event.callback_query and event.callback_query.from_user:
            user_info = event.callback_query.from_user
            event_type = "callback_query"
        elif event.inline_query and event.inline_query.from_user:
            user_info = event.inline_query.from_user
            event_type = "inline_query"
        elif event.chosen_inline_result and event.chosen_inline_result.from_user:
            user_info = event.chosen_inline_result.from_user
            event_type = "chosen_inline_result"

        if user_info:
            user_display = self._format_user_info(user_info)
            action_info = self._get_action_info(event, event_type)

            logger.info(f"\n{'='*80}\n"
                       f"👤 ПОЛЬЗОВАТЕЛЬ ВЗАИМОДЕЙСТВУЕТ С БОТОМ\n"
                       f"{'='*80}\n"
                       f"{user_display}\n"
                       f"📱 Тип события: {event_type.upper()}\n"
                       f"🎯 Действие: {action_info}\n"
                       f"{'='*80}\n")

            await self._save_user_interaction(user_info, event_type, action_info)

        return await handler(event, data)

    def _format_user_info(self, user: types.User) -> str:
        info = []
        info.append(f"🆔 ID: {user.id}")
        if user.first_name:
            info.append(f"📛 Имя: {user.first_name}")
        if user.last_name:
            info.append(f"🏷 Фамилия: {user.last_name}")
        if user.username:
            info.append(f"🔗 Username: @{user.username}")
        if user.language_code:
            info.append(f"🌐 Язык: {user.language_code}")
        if user.is_premium:
            info.append(f"⭐ Премиум: Да")
        if user.username:
            info.append(f"🔗 Ссылка: https://t.me/{user.username}")
        else:
            info.append(f"🔗 Ссылка: tg://user?id={user.id}")
        return "\n".join(info)

    def _get_action_info(self, event: types.Update, event_type: str) -> str:
        if event_type == "message" and event.message:
            msg = event.message
            if msg.text:
                action = f"Текст: {msg.text[:100]}{'...' if len(msg.text) > 100 else ''}"
            elif msg.photo:
                action = "Отправил фото"
            elif msg.video:
                action = "Отправил видео"
            elif msg.document:
                action = f"Отправил документ: {msg.document.file_name if msg.document.file_name else 'без имени'}"
            elif msg.sticker:
                action = f"Отправил стикер: {msg.sticker.emoji if msg.sticker.emoji else 'без эмодзи'}"
            elif msg.voice:
                action = "Отправил голосовое сообщение"
            elif msg.contact:
                action = f"Отправил контакт: {msg.contact.first_name}"
            elif msg.location:
                action = "Отправил геолокацию"
            else:
                action = f"Отправил {msg.content_type}"
            if msg.text and msg.text.startswith('/'):
                action += " (команда)"
            return action
        elif event_type == "callback_query" and event.callback_query:
            cb = event.callback_query
            action = f"Нажал на кнопку: {cb.data[:100]}{'...' if len(cb.data) > 100 else ''}"
            if cb.message:
                action += f"\n   📍 В сообщении: {cb.message.text[:50] if cb.message.text else 'без текста'}"
            return action
        elif event_type == "inline_query" and event.inline_query:
            return f"Inline запрос: {event.inline_query.query[:100]}"
        return "Неизвестное действие"

    async def _save_user_interaction(self, user: types.User, event_type: str, action_info: str):
        try:
            log_dir = "user_interactions"
            os.makedirs(log_dir, exist_ok=True)
            all_logs_file = os.path.join(log_dir, "all_interactions.log")
            user_log_file = os.path.join(log_dir, f"user_{user.id}.log")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = (
                f"[{timestamp}] "
                f"User: {user.id} (@{user.username if user.username else 'no_username'}) "
                f"| {user.first_name or ''} {user.last_name or ''} "
                f"| Type: {event_type} "
                f"| Action: {action_info}\n"
            )
            with open(all_logs_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
            with open(user_log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            logger.error(f"Ошибка при сохранении лога взаимодействия: {e}")

dp.update.middleware(UserTrackingMiddleware())
dp.update.middleware(ActivityTrackingMiddleware())

class UserMessageCleanupMiddleware:
    async def __call__(self, handler, event: types.Update, data: dict):
        message = event.message
        if message and message.from_user and message.from_user.id != ADMIN_ID:
            try:
                await get_active_bot().delete_message(
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                )
                logger.info(
                    "Сообщение пользователя удалено: user=%s chat=%s message=%s",
                    message.from_user.id,
                    message.chat.id,
                    message.message_id,
                )
            except TelegramAPIError as exc:
                logger.warning(
                    "Telegram не удалил сообщение пользователя: user=%s chat=%s message=%s error=%s",
                    message.from_user.id,
                    message.chat.id,
                    message.message_id,
                    exc,
                )
        return await handler(event, data)

dp.update.outer_middleware(UserMessageCleanupMiddleware())

FAQ_KEYS = ("faq_offer", "faq_verified", "faq_warranty", "faq_support")

class FAQAccessMiddleware:
    async def __call__(self, handler, event: types.Update, data: dict):
        user = None
        message = event.message
        callback = event.callback_query
        inline_query = event.inline_query
        onboarding_action = False
        if message:
            user = message.from_user
            allowed = bool(message.text and (message.text.startswith("/start") or message.text == "FAQ"))
        elif callback:
            user = callback.from_user
            onboarding_action = callback.data in {
                "onboarding_agreement",
                "accept_agreement",
                "accept_privacy",
            }
            allowed = bool(
                callback.data
                and (
                    callback.data.startswith("faq_")
                    or callback.data.startswith("create_check_")
                    or callback.data in {
                        "back_to_faq",
                        "onboarding_agreement",
                    }
                )
            )
        elif inline_query:
            user = inline_query.from_user
            # Inline queries do not expose bot content and are needed for
            # creating balance checks before the user opens the bot in private chat.
            allowed = True
        else:
            return await handler(event, data)
        if not user or user.id == ADMIN_ID or allowed:
            return await handler(event, data)
        if onboarding_action and await faq_access_granted(user.id):
            return await handler(event, data)
        completed_registration = await fetchone(
            "SELECT accepted, privacy_accepted FROM users WHERE id = ?",
            (user.id,)
        )
        if (
            completed_registration
            and completed_registration[0]
            and completed_registration[1] in (None, 1)
        ):
            return await handler(event, data)
        if await faq_access_granted(user.id):
            user_row = await fetchone(
                "SELECT accepted, privacy_accepted FROM users WHERE id = ?",
                (user.id,)
            )
            if user_row and user_row[0] and user_row[1] is None:
                return await handler(event, data)
            if user_row and user_row[0] and onboarding_action:
                return await handler(event, data)
            if user_row and user_row[0]:
                if callback:
                    await callback.answer("Сначала ознакомьтесь с политикой конфиденциальности.", show_alert=True)
                else:
                    await show_privacy_policy(message)
            elif callback:
                await callback.answer("Сначала примите пользовательское соглашение.", show_alert=True)
            else:
                await show_agreement(message)
            return
        if callback:
            await callback.answer()
        else:
            return
        return

dp.update.middleware(FAQAccessMiddleware())

def parse_referrer_id(message: types.Message) -> Optional[int]:
    args = message.text.split() if message.text else []
    if len(args) < 2 or not args[1].startswith("ref_"):
        return None
    try:
        referrer_id = int(args[1][4:])
    except ValueError:
        return None
    return referrer_id if referrer_id != message.from_user.id else None

@dp.message(Command("start_old_disabled"))
async def start_handler(message: types.Message, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    referrer_id = parse_referrer_id(message)
    
    # ✅ ВСЕГДА сохраняем пользователя при первом /start
    existing = await fetchone("SELECT id, accepted FROM users WHERE id = ?", (user_id,))
    if not existing:
        await save_user(username, user_id, referrer_id)
        logger.info(f"Новый пользователь сохранен: {user_id} (@{username})")
    else:
        # Обновляем username на случай, если он изменился
        await execute_query(
            "UPDATE users SET username = ?, created_at = COALESCE(created_at, ?) WHERE id = ?",
            (username, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), user_id),
            commit=True
        )
    
    # 🔔 Отправляем уведомление админу о новом пользователе (опционально)
    if not existing:
        try:
            await bot.send_message(
                ADMIN_ID,
                f"🆕 <b>Новый пользователь!</b>\n\n"
                f"🆔 ID: <code>{user_id}</code>\n"
                f"👤 Username: @{username if username else '—'}\n"
                f"📅 Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
                f"🔗 Ссылка: tg://user?id={user_id}",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Не удалось уведомить админа: {e}")
    
    await show_required_faq(message)

# --- MIDDLEWARE ТЕХ. РАБОТ ---
class MaintenanceMiddleware:
    async def __call__(self, handler, event: types.Update, data: dict):
        global MAINTENANCE_MODE
        if not MAINTENANCE_MODE:
            return await handler(event, data)

        user_id = None
        if event.message and event.message.from_user:
            user_id = event.message.from_user.id
        elif event.callback_query and event.callback_query.from_user:
            user_id = event.callback_query.from_user.id

        if user_id == ADMIN_ID:
            return await handler(event, data)

        maintenance_text = (
            '<b><tg-emoji emoji-id="4924762355184699046">🛠</tg-emoji> Технические работы</b>\n\n'
            '<blockquote><b>В данный момент ведутся работы.\n'
            'Попробуйте зайти позже.</b></blockquote>'
        )
        kb = InlineKeyboardBuilder()
        kb.button(
            text="Поддержка",
            url="https://t.me/EleghantHelpBot",
            icon_custom_emoji_id="5213445605573039632",
            style="primary",
        )
        kb.button(
            text="Пользовательское соглашение",
            url=AGREEMENT_URL,
            icon_custom_emoji_id="5213301161527909232",
            style="primary",
        )
        kb.button(
            text="Политика конфиденциальности",
            url=PRIVACY_POLICY_URL,
            icon_custom_emoji_id="5213301161527909232",
            style="primary",
        )
        kb.adjust(1)

        if event.callback_query:
            try:
                await event.callback_query.answer(
                    "🛠 Ведутся тех. работы. Попробуйте позже.", show_alert=True
                )
            except Exception:
                pass
            try:
                await event.callback_query.message.answer(
                    maintenance_text, parse_mode="HTML", reply_markup=kb.as_markup()
                )
            except Exception:
                pass
        elif event.message:
            try:
                await event.message.answer(
                    maintenance_text, parse_mode="HTML", reply_markup=kb.as_markup()
                )
            except Exception:
                pass
        return

dp.update.middleware(MaintenanceMiddleware())

pending_payments: Dict[int, Dict] = {}
pending_balance_payments: Dict[int, Dict] = {}
pending_inline_checks: Dict[str, Dict[str, Any]] = {}
user_promo_attempts: Dict[int, Tuple[int, float]] = {}

payment_check_semaphore = Semaphore(MAX_CONCURRENT_PAYMENT_CHECKS)
db_connection = None

# --- СОСТОЯНИЯ ---
class ShopState(StatesGroup):
    waiting_for_quantity = State()
    waiting_for_custom_quantity = State()
    waiting_for_payment_method = State()
    waiting_for_deposit_provider = State()
    waiting_for_deposit_amount = State()
    waiting_for_promo_code = State()
    waiting_for_preorder_category = State()
    waiting_for_preorder_quantity = State()
    waiting_for_preorder_provider = State()
    waiting_for_withdraw_amount = State()
    waiting_for_withdraw_confirm = State()
    waiting_for_mirror_token = State()
    waiting_for_review_rating = State()
    waiting_for_review_text = State()
    # Legacy states are retained only so old persisted updates can be drained safely.
    waiting_for_totp_name = State()
    waiting_for_totp_secret = State()

class AdminState(StatesGroup):
    broadcast_text = State()
    broadcast_with_image = State()
    broadcast_image = State()
    broadcast_ask_button = State()   
    broadcast_button_text = State()
    broadcast_button_url = State()
    broadcast_button_emoji = State()
    broadcast_button_style = State()
    broadcast_more_buttons = State()
    give_balance_user_id = State()
    give_balance_amount = State()
    add_stock_cat_id = State()
    add_stock_count = State()
    add_stock_data = State()
    add_stock_current = State()
    add_stock_txt_cat_id = State()
    add_stock_txt_file = State()
    create_promo_code = State()
    create_promo_type = State()
    create_promo_value = State()
    create_promo_limit = State()
    change_price_category = State()
    change_price_value = State()
    withdraw_reject_reason = State()
    change_desc_category = State()
    change_desc_value = State()
    search_user_username = State()
    ban_user_id = State()
    ban_user_reason = State()
    unban_user_id = State()
    give_reviews_category = State()
    give_reviews_count = State()
    give_reviews_rating = State()
    give_reviews_text = State()

# --- КЛАВИАТУРА ГЛАВНОГО МЕНЮ ---
def main_keyboard() -> ReplyKeyboardMarkup:
    catalog_btn = KeyboardButton(text="Ассортимент", icon_custom_emoji_id="4924802255430880504", style='success')
    profile_btn = KeyboardButton(text="Профиль", icon_custom_emoji_id="5213043033993421435", style='primary')
    deposit_btn = KeyboardButton(text="Пополнить баланс", icon_custom_emoji_id="4924714844256470686")
    help_btn = KeyboardButton(text="Поддержка", icon_custom_emoji_id="5213021000811189009", style='danger')
    faq_btn = KeyboardButton(text="FAQ", icon_custom_emoji_id="5212948901195190028")
    kb = [
        [catalog_btn],
        [help_btn, profile_btn],
        [deposit_btn, faq_btn]
    ]
    if WEB_APP_URL:
        kb.insert(1, [KeyboardButton(
            text="Открыть в WebApp",
            web_app=WebAppInfo(url=WEB_APP_URL),
            style="success",
        )])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- УНИВЕРСАЛЬНАЯ ФУНКЦИЯ ДЛЯ ОТПРАВКИ С КАРТИНКОЙ ---
async def send_with_image(message: types.Message, image_name: str, text: str, reply_markup=None):
    try:
        if os.path.exists(f'{image_name}.jpg'):
            photo = FSInputFile(f'{image_name}.jpg')
            await message.answer_photo(photo=photo, caption=text, parse_mode="HTML", reply_markup=reply_markup)
        elif os.path.exists(f'{image_name}.png'):
            photo = FSInputFile(f'{image_name}.png')
            await message.answer_photo(photo=photo, caption=text, parse_mode="HTML", reply_markup=reply_markup)
        else:
            await message.answer(text, parse_mode="HTML", reply_markup=reply_markup)
            logger.warning(f"Картинка {image_name} не найдена")
    except Exception as e:
        logger.error(f"Ошибка при отправке картинки {image_name}: {e}")
        await message.answer(text, parse_mode="HTML", reply_markup=reply_markup)

# --- БАЗА ДАННЫХ ---
async def get_db():
    global db_connection
    if db_connection is None:
        db_connection = await aiosqlite.connect('shop.db')
        await db_connection.execute("PRAGMA foreign_keys = ON")
    return db_connection

async def close_db():
    global db_connection
    if db_connection:
        await db_connection.close()
        db_connection = None

async def execute_query(sql: str, params: tuple = (), commit: bool = False):
    conn = await get_db()
    cursor = await conn.execute(sql, params)
    if commit:
        await conn.commit()
    return cursor

async def fetchone(sql: str, params: tuple = ()):
    cursor = await execute_query(sql, params)
    return await cursor.fetchone()

async def fetchall(sql: str, params: tuple = ()):
    cursor = await execute_query(sql, params)
    return await cursor.fetchall()

async def executemany(sql: str, params: List[tuple], commit: bool = True):
    conn = await get_db()
    await conn.executemany(sql, params)
    if commit:
        await conn.commit()

async def transaction():
    conn = await get_db()
    await conn.execute("BEGIN IMMEDIATE")
    return conn

# --- ИНИЦИАЛИЗАЦИЯ БД ---
async def init_db():
    conn = await get_db()
    await conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY, accepted INTEGER DEFAULT 0, total INTEGER DEFAULT 0,
        username TEXT, referrer_id INTEGER DEFAULT NULL, is_banned INTEGER DEFAULT 0,
        ban_reason TEXT DEFAULT NULL, banned_at TEXT DEFAULT NULL,
        privacy_accepted INTEGER DEFAULT 0, welcome_sent INTEGER DEFAULT 0
    )''')
    await conn.execute('''CREATE TABLE IF NOT EXISTS faq_progress (
        user_id INTEGER NOT NULL,
        faq_key TEXT NOT NULL,
        completed_at TEXT NOT NULL,
        PRIMARY KEY (user_id, faq_key)
    )''')
    for col, definition in [
        ("is_banned", "INTEGER DEFAULT 0"),
        ("ban_reason", "TEXT DEFAULT NULL"),
        ("banned_at", "TEXT DEFAULT NULL"),
        ("created_at", "TEXT DEFAULT NULL"),
        ("accepted_at", "TEXT DEFAULT NULL"),
        ("privacy_accepted", "INTEGER DEFAULT NULL"),
        ("welcome_sent", "INTEGER DEFAULT 0"),
        ("last_activity", "TEXT DEFAULT NULL"),
    ]:
        try:
            await conn.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")
        except Exception:
            pass
    await conn.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, desc TEXT, price REAL,
        cat_group TEXT DEFAULT '', maintenance INTEGER DEFAULT 0
    )''')
    try:
        await conn.execute("ALTER TABLE categories ADD COLUMN maintenance INTEGER DEFAULT 0")
    except Exception:
        pass
    await conn.execute('''CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT, cat_id INTEGER, data TEXT
    )''')
    await conn.execute('''CREATE TABLE IF NOT EXISTS preorders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, cat_id INTEGER, quantity INTEGER,
        total REAL, status TEXT DEFAULT 'pending', created_at TEXT, paid_at TEXT DEFAULT NULL
    )''')
    await conn.execute('''CREATE TABLE IF NOT EXISTS balances (
        user_id INTEGER PRIMARY KEY, balance REAL DEFAULT 0.0
    )''')
    await conn.execute('''CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item_data TEXT, date TEXT
    )''')
    try:
        await conn.execute("ALTER TABLE history ADD COLUMN created_at TEXT")
    except Exception:
        pass
    try:
        await conn.execute("ALTER TABLE history ADD COLUMN cat_id INTEGER")
    except Exception:
        pass
    await conn.execute('''CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER, referral_id INTEGER UNIQUE, date TEXT
    )''')
    await conn.execute('''CREATE TABLE IF NOT EXISTS referral_earnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER, amount REAL, from_user_id INTEGER, date TEXT
    )''')
    await conn.execute('''CREATE TABLE IF NOT EXISTS promo_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        amount REAL,
        promo_type TEXT DEFAULT 'fixed',
        max_uses INTEGER,
        used INTEGER DEFAULT 0
    )''')
    try:
        await conn.execute("ALTER TABLE promo_codes ADD COLUMN promo_type TEXT DEFAULT 'fixed'")
    except Exception:
        pass
    await conn.execute('''CREATE TABLE IF NOT EXISTS promo_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        user_id INTEGER,
        username TEXT,
        used_at TEXT
    )''')
    await conn.execute('''CREATE TABLE IF NOT EXISTS balance_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, amount REAL, operation TEXT, date TEXT, admin_id INTEGER DEFAULT NULL
    )''')
    await conn.execute('''CREATE TABLE IF NOT EXISTS balance_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_hash TEXT NOT NULL UNIQUE,
        creator_id INTEGER NOT NULL,
        amount REAL NOT NULL CHECK(amount > 0),
        status TEXT NOT NULL DEFAULT 'active',
        claimed_by INTEGER DEFAULT NULL,
        created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        claimed_at TEXT DEFAULT NULL,
        refunded_at TEXT DEFAULT NULL,
        FOREIGN KEY (creator_id) REFERENCES users(id)
    )''')
    for col, definition in [
        ("total_amount", "REAL"),
        ("max_claims", "INTEGER DEFAULT 1"),
        ("claimed_count", "INTEGER DEFAULT 0"),
        ("comment", "TEXT DEFAULT NULL"),
        ("recipient_username", "TEXT DEFAULT NULL"),
        ("recipient_id", "INTEGER DEFAULT NULL"),
    ]:
        try:
            await conn.execute(f"ALTER TABLE balance_checks ADD COLUMN {col} {definition}")
        except Exception:
            pass
    await conn.execute(
        "UPDATE balance_checks SET total_amount = amount, max_claims = 1, claimed_count = 0 "
        "WHERE total_amount IS NULL"
    )
    await conn.execute('''CREATE TABLE IF NOT EXISTS withdraw_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        amount REAL,
        status TEXT DEFAULT 'pending',
        created_at TEXT,
        processed_at TEXT DEFAULT NULL,
        admin_note TEXT DEFAULT NULL
    )''')
    await conn.execute('''CREATE TABLE IF NOT EXISTS user_mirrors (
        user_id INTEGER PRIMARY KEY, bot_token TEXT NOT NULL, bot_username TEXT,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    await conn.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, cat_id INTEGER NOT NULL,
        rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5), text TEXT DEFAULT '',
        created_at TEXT NOT NULL, UNIQUE(user_id, cat_id)
    )''')
    # Таблица для TOTP-ключей
    await conn.execute('''CREATE TABLE IF NOT EXISTS totp_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        secret TEXT,
        created_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    await conn.commit()
    try:
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_inventory_cat_id ON inventory(cat_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_history_user_id ON history(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_referrals_referrer_id ON referrals(referrer_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_preorders_user_id ON preorders(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_withdraw_user_id ON withdraw_requests(user_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_balance_checks_creator_id ON balance_checks(creator_id)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_balance_checks_expires_at ON balance_checks(expires_at)")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_promo_usage_code ON promo_usage(code)")
        await conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_promo_usage_code_user "
            "ON promo_usage(code, user_id)"
        )
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_reviews_cat_id ON reviews(cat_id)")
        await conn.commit()
    except Exception:
        pass
    logger.info("Database initialized")

async def update_catalog_descriptions():
    descriptions = {
        "MTS 1952-2008R": '<tg-emoji emoji-id="5312126452043363774">📞</tg-emoji> <b>MTS 1952-2008R</b>\n\n<tg-emoji emoji-id="5895440460322706085">📌</tg-emoji> <b>Описание товара:</b>\nMTS - без TOTP, ВП, отчеканный на ФССП',
        "MEGAFON 1952-2008R": '<tg-emoji emoji-id="5229218997521631084">📞</tg-emoji> <b>MEGAFON 1952-2008R</b>\n\n<tg-emoji emoji-id="5895440460322706085">📌</tg-emoji> <b>Описание товара:</b>\nMEGAFON - без TOTP, ВП, отчеканный на ФССП',
        "BEELINE 1952-2008R": '<tg-emoji emoji-id="5280919528908267119">📞</tg-emoji> <b>BEELINE 1952-2008R</b>\n\n<tg-emoji emoji-id="5895440460322706085">📌</tg-emoji> <b>Описание товара:</b>\nBEELINE - без TOTP, ВП, отчеканный на ФССП',
        "YOTA 1952-2008R": '<tg-emoji emoji-id="5280716016177915458">📞</tg-emoji> <b>YOTA 1952-2008R</b>\n\n<tg-emoji emoji-id="5895440460322706085">📌</tg-emoji> <b>Описание товара:</b>\nYOTA - без TOTP, ВП, отчеканный на ФССП',
        "TELE2 ALL REG 1952-2008R": '<tg-emoji emoji-id="5244453379664534900">📞</tg-emoji> <b>TELE2 ALL REG 1952-2008R</b>\n\n<tg-emoji emoji-id="5895440460322706085">📌</tg-emoji> <b>Описание товара:</b>\nTELE2 - без TOTP, ВП, отчеканный на ФССП',
        "Госуслуги 1960-1979R": '<tg-emoji emoji-id="5343742152985839675">🏦</tg-emoji> <b>Госуслуги 1960-1979R</b>',
        "Госуслуги под гк 1960-1979R": '<tg-emoji emoji-id="5456232070932090258">🔑</tg-emoji> <b>Госуслуги под гк 1960-1979R</b>',
        "Госуслуги 1980-2008R": '<tg-emoji emoji-id="5343742152985839675">🏦</tg-emoji> <b>Госуслуги 1980-2008R</b>',
        "Госуслуги под гк 1980-2008R": '<tg-emoji emoji-id="5456232070932090258">🔑</tg-emoji> <b>Госуслуги под гк 1980-2008R</b>',
        "Госуслуги отработанные 1980-2008R": '<tg-emoji emoji-id="5343742152985839675">🏦</tg-emoji> <b>Госуслуги отработанные 1980-2008R</b>',
        "Личный кабинет ТБанка": (
            "В данной категории предоставляется доступ к личному кабинету Т-Банка с данными, успешно прошедшими проверку.\n\n"
            "Предусмотрена возможность полноценного использования личного кабинета в рамках доступного функционала: "
            "проведение личных переводов, работа с банковскими операциями и другие стандартные возможности.\n\n"
            "Процесс регистрации занимает около 5 минут: необходимо предоставить требуемые данные и номер телефона, "
            "после чего подтвердить несколько кодов. После завершения процедуры личный кабинет готов к использованию."
        ),
    }
    prices = {
        "MTS 1952-2008R": 4.5, "MEGAFON 1952-2008R": 4.0, "BEELINE 1952-2008R": 3.5,
        "YOTA 1952-2008R": 3.5, "TELE2 ALL REG 1952-2008R": 4.0,
        "Госуслуги 1960-1979R": 25.0, "Госуслуги под гк 1960-1979R": 18.0,
        "Госуслуги 1980-2008R": 25.0, "Госуслуги под гк 1980-2008R": 18.0,
        "Госуслуги отработанные 1980-2008R": 5.0,
        "Личный кабинет ТБанка": 25.0,
    }
    cat_groups = {
        "MTS 1952-2008R": "l0gu_1970", "MEGAFON 1952-2008R": "l0gu_1970",
        "BEELINE 1952-2008R": "l0gu_1970", "YOTA 1952-2008R": "l0gu_1970",
        "TELE2 ALL REG 1952-2008R": "l0gu_1970",
        "Госуслуги 1960-1979R": "gy_1970", "Госуслуги под гк 1960-1979R": "gy_1970",
        "Госуслуги 1980-2008R": "gy_1970", "Госуслуги под гк 1980-2008R": "gy_1970",
        "Госуслуги отработанные 1980-2008R": "gy_1970",
        "Личный кабинет ТБанка": "tbank",
    }
    for name, desc in descriptions.items():
        legacy_name = name.replace("1952-2008R", "1952-2006R")
        if name == "TELE2 ALL REG 1952-2008R":
            legacy_name = "T2 SMENA MIKS 1952-2006R"
        legacy_names = {
            "Госуслуги 1960-1979R": "Чистые ГУ 1960-1969",
            "Госуслуги под гк 1960-1979R": "ГУ под ГК 1960-1969",
            "Госуслуги 1980-2008R": "Чистые ГУ 1980-2006",
            "Госуслуги под гк 1980-2008R": "ГУ под ГК 1980-2006",
            "Госуслуги отработанные 1980-2008R": "GY 1980+ отработки",
        }
        legacy_name = legacy_names.get(name, legacy_name)
        await execute_query(
            "UPDATE categories SET name = ? WHERE name = ?",
            (name, legacy_name),
            commit=True
        )
        existing = await fetchone("SELECT id FROM categories WHERE name = ?", (name,))
        price = prices.get(name, 0)
        cat_group = cat_groups.get(name, "")
        if existing:
            await execute_query(
                "UPDATE categories SET desc = ?, price = ?, cat_group = ? WHERE name = ?",
                (desc, price, cat_group, name), commit=True
            )
        else:
            await execute_query(
                "INSERT INTO categories (name, desc, price, cat_group) VALUES (?, ?, ?, ?)",
                (name, desc, price, cat_group), commit=True
            )
    logger.info("Catalog descriptions updated")

async def setup_catalog():
    await update_catalog_descriptions()

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
async def get_balance(user_id: int) -> float:
    bal = await fetchone("SELECT balance FROM balances WHERE user_id = ?", (user_id,))
    return bal[0] if bal else 0.0

async def update_balance(user_id: int, amount: float, operation: str = "unknown", admin_id: int = None):
    current_balance = await get_balance(user_id)
    new_balance = current_balance + amount
    if new_balance < 0 and operation not in ["admin_give"]:
        logger.warning(f"Attempt to set negative balance for user {user_id}: {new_balance}")
        return False
    await execute_query("INSERT INTO balances (user_id, balance) VALUES (?, ?) "
                       "ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?",
                       (user_id, amount, amount), commit=True)
    await execute_query("INSERT INTO balance_history (user_id, amount, operation, date, admin_id) VALUES (?, ?, ?, ?, ?)",
                       (user_id, amount, operation, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), admin_id), commit=True)
    return True

def parse_check_amount(value: str) -> Optional[float]:
    try:
        normalized = value.strip().upper().replace(",", ".")
        if normalized.startswith("$"):
            normalized = normalized[1:].strip()
        if normalized.endswith("USDT"):
            normalized = normalized[:-4].strip()
        amount = Decimal(normalized)
    except (InvalidOperation, AttributeError):
        return None
    if amount <= 0 or amount > Decimal("1000000") or amount.as_tuple().exponent < -2:
        return None
    return float(amount.quantize(Decimal("0.01")))

def parse_check_spec(args: List[str]) -> Optional[Tuple[float, int, Optional[str], str]]:
    if len(args) < 1:
        return None
    total = parse_check_amount(args[0])
    if total is None:
        return None
    claims = 1
    index = 1
    if len(args) > 1 and args[1].isdigit():
        claims = int(args[1])
        index = 2
    if claims < 1 or claims > 100:
        return None
    recipient = None
    if index < len(args) and args[index].startswith("@"):
        recipient = args[index][1:].lower()
        index += 1
    comment = " ".join(args[index:]).strip()
    if round(total / claims, 2) * claims != round(total, 2):
        return None
    return total, claims, recipient, comment

async def resolve_username(username: str) -> Optional[Tuple[int, str]]:
    normalized = username.removeprefix("@").strip().lower()
    row = await fetchone(
        "SELECT id, username FROM users WHERE lower(username) = ?",
        (normalized,),
    )
    return (row[0], row[1]) if row else None

async def transfer_balance(sender_id: int, recipient_id: int, amount: float) -> bool:
    if sender_id == recipient_id:
        return False
    conn = await transaction()
    try:
        cursor = await conn.execute(
            "UPDATE balances SET balance = balance - ? WHERE user_id = ? AND balance >= ?",
            (amount, sender_id, amount),
        )
        if cursor.rowcount != 1:
            await conn.rollback()
            return False
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        await conn.execute(
            "INSERT INTO balances (user_id, balance) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?",
            (recipient_id, amount, amount),
        )
        await conn.executemany(
            "INSERT INTO balance_history (user_id, amount, operation, date, admin_id) VALUES (?, ?, ?, ?, ?)",
            [
                (sender_id, -amount, "transfer", now, recipient_id),
                (recipient_id, amount, "transfer", now, sender_id),
            ],
        )
        await conn.commit()
        return True
    except Exception:
        await conn.rollback()
        raise

def _check_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

async def create_balance_check(
    user_id: int,
    total_amount: float,
    max_claims: int = 1,
    comment: str = "",
    recipient_username: Optional[str] = None,
    recipient_id: Optional[int] = None,
) -> Optional[str]:
    if max_claims < 1 or max_claims > 100:
        return None
    claim_amount = round(total_amount / max_claims, 2)
    if claim_amount * max_claims != round(total_amount, 2):
        return None
    token = secrets.token_urlsafe(24)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=24)
    conn = await transaction()
    try:
        cursor = await conn.execute(
            "UPDATE balances SET balance = balance - ? WHERE user_id = ? AND balance >= ?",
            (total_amount, user_id, total_amount),
        )
        if cursor.rowcount != 1:
            await conn.rollback()
            return None
        await conn.execute(
            "INSERT INTO balance_checks "
            "(token_hash, creator_id, amount, total_amount, max_claims, claimed_count, "
            "comment, recipient_username, recipient_id, created_at, expires_at) "
            "VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?)",
            (
                _check_token_hash(token),
                user_id,
                claim_amount,
                total_amount,
                max_claims,
                comment[:500] or None,
                recipient_username,
                recipient_id,
                now.isoformat(),
                expires_at.isoformat(),
            ),
        )
        await conn.execute(
            "INSERT INTO balance_history (user_id, amount, operation, date) VALUES (?, ?, ?, ?)",
            (user_id, -total_amount, "check_create", now.strftime("%Y-%m-%d %H:%M:%S")),
        )
        await conn.commit()
        return token
    except Exception:
        await conn.rollback()
        raise

async def claim_balance_check(
    token: str, claimant_id: int
) -> Tuple[str, Optional[float], Optional[int], Optional[str]]:
    now = datetime.now(timezone.utc)
    conn = await transaction()
    try:
        row = await (await conn.execute(
            "SELECT id, creator_id, amount, total_amount, max_claims, claimed_count, "
            "status, expires_at, comment, recipient_id "
            "FROM balance_checks WHERE token_hash = ?",
            (_check_token_hash(token),),
        )).fetchone()
        if not row:
            await conn.rollback()
            return "not_found", None, None, None
        check_id, creator_id, amount, total_amount, max_claims, claimed_count, status, expires_at, comment, recipient_id = row
        if status != "active" or claimed_count >= max_claims:
            await conn.rollback()
            return f"already_{status}", amount, creator_id, comment
        if recipient_id is not None and recipient_id != claimant_id:
            await conn.rollback()
            return "wrong_recipient", amount, creator_id, comment
        if datetime.fromisoformat(expires_at) <= now:
            refund_amount = round(amount * max(0, max_claims - claimed_count), 2)
            await conn.execute(
                "UPDATE balance_checks SET status = 'expired', refunded_at = ? "
                "WHERE id = ? AND status = 'active'",
                (now.isoformat(), check_id),
            )
            await conn.execute(
                "INSERT INTO balances (user_id, balance) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?",
                (creator_id, refund_amount, refund_amount),
            )
            await conn.execute(
                "INSERT INTO balance_history (user_id, amount, operation, date) VALUES (?, ?, ?, ?)",
                (creator_id, refund_amount, "check_refund", now.strftime("%Y-%m-%d %H:%M:%S")),
            )
            await conn.commit()
            return "expired", amount, creator_id, comment
        new_claimed_count = claimed_count + 1
        new_status = "claimed" if new_claimed_count >= max_claims else "active"
        await conn.execute(
            "UPDATE balance_checks SET status = ?, claimed_by = ?, claimed_at = ?, claimed_count = ? "
            "WHERE id = ? AND status = 'active'",
            (new_status, claimant_id, now.isoformat(), new_claimed_count, check_id),
        )
        await conn.execute(
            "INSERT INTO balances (user_id, balance) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?",
            (claimant_id, amount, amount),
        )
        await conn.execute(
            "INSERT INTO balance_history (user_id, amount, operation, date) VALUES (?, ?, ?, ?)",
            (claimant_id, amount, "check_claim", now.strftime("%Y-%m-%d %H:%M:%S")),
        )
        await conn.commit()
        return "claimed", amount, creator_id, comment
    except Exception:
        await conn.rollback()
        raise

async def expire_balance_checks():
    now = datetime.now(timezone.utc)
    conn = await transaction()
    try:
        rows = await (await conn.execute(
            "SELECT id, creator_id, amount, max_claims, claimed_count FROM balance_checks "
            "WHERE status = 'active' AND expires_at <= ?",
            (now.isoformat(),),
        )).fetchall()
        for check_id, creator_id, amount, max_claims, claimed_count in rows:
            refund_amount = round(amount * max(0, max_claims - claimed_count), 2)
            await conn.execute(
                "UPDATE balance_checks SET status = 'expired', refunded_at = ? "
                "WHERE id = ? AND status = 'active'",
                (now.isoformat(), check_id),
            )
            await conn.execute(
                "INSERT INTO balances (user_id, balance) VALUES (?, ?) "
                "ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?",
                (creator_id, refund_amount, refund_amount),
            )
            await conn.execute(
                "INSERT INTO balance_history (user_id, amount, operation, date) VALUES (?, ?, ?, ?)",
                (creator_id, refund_amount, "check_refund", now.strftime("%Y-%m-%d %H:%M:%S")),
            )
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise

async def add_referral_earning(referrer_id: int, amount: float, from_user_id: int):
    await execute_query("INSERT INTO referral_earnings (referrer_id, amount, from_user_id, date) VALUES (?, ?, ?, ?)",
                       (referrer_id, amount, from_user_id, datetime.now(timezone.utc).strftime("%d.%m %H:%M")), commit=True)
    await update_balance(referrer_id, amount, "referral")

async def get_referral_info(user_id: int) -> Tuple[int, float]:
    count = await fetchone("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
    earnings = await fetchone("SELECT SUM(amount) FROM referral_earnings WHERE referrer_id = ?", (user_id,))
    return count[0] if count else 0, earnings[0] if earnings and earnings[0] else 0.0

async def save_user(username: str, user_id: int, referrer_id: int = None):
    await execute_query("UPDATE users SET username = ? WHERE id = ?", (username, user_id), commit=True)
    existing = await fetchone("SELECT id FROM users WHERE id = ?", (user_id,))
    if not existing:
        if referrer_id:
            referrer = await fetchone("SELECT id FROM users WHERE id = ?", (referrer_id,))
            if not referrer:
                referrer_id = None
        await execute_query(
            "INSERT INTO users (id, username, referrer_id, created_at) VALUES (?, ?, ?, ?)",
            (user_id, username, referrer_id,
             datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")),
            commit=True
        )
        await execute_query("INSERT INTO balances (user_id, balance) VALUES (?, ?)", (user_id, 0.0), commit=True)
        if referrer_id:
            await execute_query("INSERT INTO referrals (referrer_id, referral_id, date) VALUES (?, ?, ?)",
                               (referrer_id, user_id, datetime.now(timezone.utc).strftime("%d.%m %H:%M")), commit=True)

async def is_user_banned(user_id: int) -> bool:
    row = await fetchone("SELECT is_banned FROM users WHERE id = ?", (user_id,))
    return bool(row and row[0])

# --- MIDDLEWARE ДЛЯ БАНА ---
class BanCheckMiddleware:
    async def __call__(self, handler, event: types.Update, data: dict):
        user_id = None
        if event.message and event.message.from_user:
            user_id = event.message.from_user.id
        elif event.callback_query and event.callback_query.from_user:
            user_id = event.callback_query.from_user.id

        if user_id and user_id != ADMIN_ID:
            if await is_user_banned(user_id):
                ban_info = await fetchone("SELECT ban_reason FROM users WHERE id = ?", (user_id,))
                reason = ban_info[0] if ban_info and ban_info[0] else "Причина не указана"
                ban_text = (
                    f'🚫 <b>Вы заблокированы</b>\n\n'
                    f'Причина: {reason}\n\n'
                    f'Для обжалования обратитесь в поддержку.'
                )
                if event.callback_query:
                    try:
                        await event.callback_query.answer("🚫 Вы заблокированы.", show_alert=True)
                    except Exception:
                        pass
                elif event.message:
                    try:
                        await event.message.answer(ban_text, parse_mode="HTML")
                    except Exception:
                        pass
                return
        return await handler(event, data)

dp.update.middleware(BanCheckMiddleware())

# --- ФУНКЦИЯ ПОКУПКИ С ТРАНЗАКЦИЕЙ ---
async def buy_items_with_transaction(cat_id: int, quantity: int, user_id: int, total: float) -> Optional[List[tuple]]:
    stock = await fetchone("SELECT COUNT(*) FROM inventory WHERE cat_id = ?", (cat_id,))
    stock_count = stock[0] if stock else 0
    if stock_count < quantity:
        return None
    if total > 0:
        balance = await get_balance(user_id)
        if balance < total:
            return None
    conn = await transaction()
    try:
        cursor = await conn.execute("SELECT id, data FROM inventory WHERE cat_id = ? LIMIT ?", (cat_id, quantity))
        items = await cursor.fetchall()
        if len(items) < quantity:
            await conn.rollback()
            return None
        ids = [item[0] for item in items]
        placeholders = ','.join('?' * len(ids))
        await conn.execute(f"DELETE FROM inventory WHERE id IN ({placeholders})", ids)
        now = datetime.now(timezone.utc)
        now_str = now.strftime("%d.%m %H:%M")      # для старого поля date
        now_iso = now.isoformat()                  # для нового поля created_at
        history_data = [(user_id, cat_id, item[1], now_str, now_iso) for item in items]
        await conn.executemany(
            "INSERT INTO history (user_id, cat_id, item_data, date, created_at) VALUES (?, ?, ?, ?, ?)",
            history_data
        )
        await conn.execute("UPDATE users SET total = total + ? WHERE id = ?", (quantity, user_id))
        if total > 0:
            balance_cursor = await conn.execute(
                "UPDATE balances SET balance = balance - ? WHERE user_id = ? AND balance >= ?",
                (total, user_id, total)
            )
            if balance_cursor.rowcount != 1:
                await conn.rollback()
                return None
        await conn.commit()
        return items
    except Exception as e:
        await conn.rollback()
        logger.error(f"Transaction error: {e}")
        raise

# --- XROCKET PAY API ---
XROCKET_API_URL = "https://pay.xrocket.tg"

async def xrocket_request(method: str, path: str, json_data: dict = None, params: dict = None) -> dict:
    headers = {"Rocket-Pay-Key": XROCKET_PAY_TOKEN}
    url = f"{XROCKET_API_URL}/{path}"
    timeout = aiohttp.ClientTimeout(total=30)
    for attempt in range(3):
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(method, url, json=json_data, params=params, headers=headers) as resp:
                    try:
                        result = await resp.json()
                    except Exception:
                        raw_text = await resp.text()
                        logger.error(f"xRocket API: не удалось распарсить JSON, status={resp.status}, body={raw_text[:500]}")
                        if attempt == 2:
                            return {"ok": False, "description": f"Invalid JSON response (status {resp.status})"}
                        await asyncio.sleep(2 ** attempt)
                        continue
                    if resp.status >= 400 or result.get('errors') or result.get('error'):
                        err_msg = result.get('error') or (result.get('errors') or [{}])[0].get('error', 'Unknown error') if isinstance(result, dict) else 'Unknown error'
                        logger.warning(f"xRocket API error on {path}: {err_msg} | raw={result}")
                        if attempt == 2:
                            return {"ok": False, "description": err_msg, "raw": result}
                    else:
                        logger.info(f"xRocket API raw response for {path}: {result}")
                        return {"ok": True, "raw": result}
        except Exception as e:
            if attempt == 2:
                return {"ok": False, "description": str(e)}
        await asyncio.sleep(2 ** attempt)
    return {"ok": False, "description": "Max retries exceeded"}

def _xrocket_extract_invoice(raw: dict) -> dict:
    obj = raw.get('data', raw) if isinstance(raw, dict) else raw
    if not isinstance(obj, dict):
        return {}
    invoice_id = obj.get('id') or obj.get('invoiceId') or obj.get('invoice_id')
    pay_link = (
        obj.get('link') or obj.get('payLink') or obj.get('pay_url')
        or obj.get('url') or obj.get('miniAppInvoiceUrl') or obj.get('webAppInvoiceUrl')
    )
    status = obj.get('status') or obj.get('invoiceStatus')
    paid_amount = obj.get('paidAmount') or obj.get('paid_amount') or 0
    return {
        'id': invoice_id,
        'link': pay_link,
        'status': status,
        'paid_amount': paid_amount,
        'raw': obj,
    }

async def xrocket_create_invoice(amount: float, description: str, expired_in: int = 1800) -> dict:
    res = await xrocket_request("POST", "tg-invoices", json_data={
        "amount": amount,
        "numPayments": 1,
        "currency": "USDT",
        "description": description,
        "expiredIn": expired_in,
    })
    if not res.get('ok'):
        return {"ok": False, "description": res.get('description', 'Unknown error')}
    parsed = _xrocket_extract_invoice(res['raw'])
    if not parsed.get('id') or not parsed.get('link'):
        logger.error(f"xRocket: не удалось извлечь id/link из ответа createInvoice: {res['raw']}")
        return {"ok": False, "description": "Не удалось получить ссылку на оплату от xRocket. Проверьте логи (raw response)."}
    return {"ok": True, **parsed}

async def xrocket_get_invoice(invoice_id: str) -> dict:
    res = await xrocket_request("GET", f"tg-invoices/{invoice_id}")
    if not res.get('ok'):
        return {"ok": False, "description": res.get('description', 'Unknown error')}
    parsed = _xrocket_extract_invoice(res['raw'])
    return {"ok": True, **parsed}

def _xrocket_is_paid(status: Optional[str], paid_amount) -> bool:
    if status and str(status).lower() == 'paid':
        return True
    try:
        return float(paid_amount or 0) > 0
    except (TypeError, ValueError):
        return False

def _xrocket_is_expired(status: Optional[str]) -> bool:
    return bool(status) and str(status).lower() in ('expired', 'cancelled', 'canceled')

# --- ПРОВЕРКА ОПЛАТЫ ---
async def check_deposit_payment(invoice_id, user_id: int, amount: float, msg_to_edit: types.Message, provider: str = "xrocket"):
    async with payment_check_semaphore:
        for attempt in range(PAYMENT_CHECK_ATTEMPTS):
            await asyncio.sleep(PAYMENT_CHECK_INTERVAL)
            if invoice_id not in pending_balance_payments:
                return
            if provider == "xrocket":
                inv = await xrocket_get_invoice(str(invoice_id))
                if not inv.get('ok'):
                    continue
                is_paid = _xrocket_is_paid(inv.get('status'), inv.get('paid_amount'))
                is_expired = _xrocket_is_expired(inv.get('status'))
            if is_paid:
                await update_balance(user_id, amount, "deposit")
                del pending_balance_payments[invoice_id]
                await get_active_bot().send_message(user_id, f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CHECK}">✅</tg-emoji> Баланс успешно пополнен на {amount} USDT!', parse_mode="HTML")
                try:
                    await msg_to_edit.delete()
                except Exception:
                    pass
                return
            elif is_expired:
                await msg_to_edit.edit_text(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Счет просрочен. Попробуйте снова.', parse_mode="HTML")
                del pending_balance_payments[invoice_id]
                return
        if invoice_id in pending_balance_payments:
            await msg_to_edit.edit_text(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Время ожидания истекло. Если вы оплатили, обратитесь в поддержку.', parse_mode="HTML")
            del pending_balance_payments[invoice_id]

async def auto_check_payment(invoice_id, user_id: int, cat_id: int, quantity: int,
                            msg_to_edit: types.Message, total_cost: float, provider: str = "xrocket"):
    async with payment_check_semaphore:
        for attempt in range(PAYMENT_CHECK_ATTEMPTS):
            await asyncio.sleep(PAYMENT_CHECK_INTERVAL)
            if invoice_id not in pending_payments:
                return
            if provider == "xrocket":
                inv = await xrocket_get_invoice(str(invoice_id))
                if not inv.get('ok'):
                    continue
                is_paid = _xrocket_is_paid(inv.get('status'), inv.get('paid_amount'))
                is_expired = _xrocket_is_expired(inv.get('status'))
            if is_paid:
                items = await buy_items_with_transaction(cat_id, quantity, user_id, total_cost)
                if not items:
                    await get_active_bot().send_message(user_id, f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Товар закончился во время оплаты. Обратитесь в поддержку.', parse_mode="HTML")
                    del pending_payments[invoice_id]
                    return
                res_text = f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CHECK}">✅</tg-emoji> Оплата подтверждена!\n\n<tg-emoji emoji-id="{CustomEmoji.PREORDER_BOX}">🎁</tg-emoji> Ваш товар:\n'
                for _, i_data in items:
                    res_text += f"• `{i_data}`\n"
                await get_active_bot().send_message(
                    user_id,
                    res_text,
                    parse_mode="Markdown",
                    reply_markup=purchase_review_keyboard(cat_id).as_markup(),
                )
                try:
                    await msg_to_edit.delete()
                except Exception:
                    pass
                referrer = await fetchone("SELECT referrer_id FROM users WHERE id = ?", (user_id,))
                if referrer and referrer[0]:
                    ref_bonus = round(total_cost * 0.1, 2)
                    await add_referral_earning(referrer[0], ref_bonus, user_id)
                    await get_active_bot().send_message(referrer[0], f'<tg-emoji emoji-id="{CustomEmoji.MONEY}">💰</tg-emoji> Вы получили {ref_bonus} USDT (10%) от покупки!', parse_mode="HTML")
                del pending_payments[invoice_id]
                return
            elif is_expired:
                await msg_to_edit.edit_text(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Счет просрочен. Создайте новый заказ.', parse_mode="HTML")
                del pending_payments[invoice_id]
                return
        if invoice_id in pending_payments:
            await msg_to_edit.edit_text(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Время автоматической проверки истекло. Обратитесь в поддержку.', parse_mode="HTML")
            del pending_payments[invoice_id]

# --- ФОНОВАЯ ЗАДАЧА ---
async def cleanup_old_payments():
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        now = datetime.now()
        expired = [inv_id for inv_id, data in pending_payments.items()
                   if 'created_at' in data and now - data['created_at'] > timedelta(hours=1)]
        for inv_id in expired:
            del pending_payments[inv_id]
        expired = [inv_id for inv_id, data in pending_balance_payments.items()
                   if 'created_at' in data and now - data['created_at'] > timedelta(hours=1)]
        for inv_id in expired:
            del pending_balance_payments[inv_id]
        current_time = time.time()
        expired_users = [uid for uid, (attempts, last_attempt) in user_promo_attempts.items()
                         if current_time - last_attempt > PROMO_BLOCK_TIME]
        for uid in expired_users:
            del user_promo_attempts[uid]
        expired_inline = [
            key for key, draft in pending_inline_checks.items()
            if current_time - draft["created_at"] > 1800
        ]
        for key in expired_inline:
            del pending_inline_checks[key]
        await expire_balance_checks()
        logger.info("Cleanup completed")

# --- ФУНКЦИЯ ДЛЯ ПОКАЗА КАТЕГОРИЙ ГРУППЫ ---
async def show_categories_group(call: types.CallbackQuery, group_key: str):
    if group_key == "l0gu":
        cat_group = "l0gu_1970"
        emoji_ids = [CustomEmoji.MTS, CustomEmoji.MEGAFON, CustomEmoji.BEELINE, CustomEmoji.YOTA, CustomEmoji.T2]
        image_name = 'EleghantLOGI'   # картинка для Л0гu
    elif group_key == "gy":
        cat_group = "gy_1970"
        emoji_ids = [CustomEmoji.GY, CustomEmoji.GY_EMOJI, CustomEmoji.GY, CustomEmoji.GY_EMOJI, "5343742152985839675"]
        image_name = 'EleghantGY'      # картинка для GY
    elif group_key == "tbank":
        cat_group = "tbank"
        emoji_ids = [CustomEmoji.TBANK]
        image_name = 'EleghantBalance'
    else:
        await call.answer("Неизвестная группа")
        return
    cats = await fetchall("SELECT id, name FROM categories WHERE cat_group = ?", (cat_group,))
    if not cats:
        await call.message.answer(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❗️</tg-emoji> В этом разделе пока нет товаров.', parse_mode="HTML")
        await call.answer()
        return
    kb = InlineKeyboardBuilder()
    for idx, (cid, name) in enumerate(cats):
        category_emoji_id = PRODUCT_CATEGORY_EMOJIS.get(cid)
        if category_emoji_id:
            kb.button(text=name, callback_data=f"view_{cid}", icon_custom_emoji_id=category_emoji_id, style="SUCCESS")
        elif idx < len(emoji_ids):
            kb.button(text=name, callback_data=f"view_{cid}", icon_custom_emoji_id=emoji_ids[idx], style="SUCCESS")
        else:
            kb.button(text=name, callback_data=f"view_{cid}", style="SUCCESS")
    kb.button(text="Назад к разделам", callback_data="back_to_main_catalog", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    kb.adjust(1)
    text = (
        '<blockquote><b><tg-emoji emoji-id="4924866615515809418">❓</tg-emoji> '
        'Выберите интересующую Вас категорию:</b></blockquote>'
    )
    await call.message.delete()
    await send_with_image(call.message, image_name, text, kb.as_markup())
    await call.answer()

# --- ПОКАЗ КНОПОК ВЫБОРА КОЛИЧЕСТВА ---
@dp.inline_query(F.query == "")
async def inline_handler(query: InlineQuery):
    user_id = query.from_user.id

    ref_link = f"https://t.me/{(await get_active_bot().get_me()).username}?start=ref_{user_id}"

    kb = InlineKeyboardBuilder()
    kb.button(text="Запуск", url=ref_link, icon_custom_emoji_id="START", style="success")

    message_content = InputTextMessageContent(
        message_text="💠 ALTERA - качество, стабильность и мгновенная выдача."
    )

    result = InlineQueryResultArticle(
        id="1",
        title="Отправить приглашение в ALTERA",
        description="Со своей реферальной ссылкой",
        thumbnail_url="https://example.com/your_thumb.png",
        input_message_content=message_content,
        reply_markup=kb.as_markup(),
    )

    await query.answer(
        results=[result],
        cache_time=1,
        is_personal=True,
    )

async def show_quantity_keyboard(message: types.Message, cid: int, cat_name: str, price: float, stock_count: int):
    presets = [1, 3, 5, 10]
    kb = InlineKeyboardBuilder()
    for qty in presets:
        total = price * qty
        if qty >= 10:
            total = total * 0.8  # оптовая скидка 20%
        total = round(total, 2)
        btn_text = f"{qty} шт. — ${total}"
        if qty >= 10:
            btn_text += " (скидка 20%)"
        kb.button(text=btn_text, callback_data=f"qty_{cid}_{qty}")
    kb.button(text="Ввести своё число", callback_data=f"qty_custom_{cid}", icon_custom_emoji_id="5213347787692876346", style='primary')
    kb.button(text="Назад", callback_data=f"view_{cid}", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    kb.adjust(2, 2, 1, 1)
    text = (
        '<b><tg-emoji emoji-id="4925115139503455129">❓</tg-emoji> Выберите количество:</b>\n\n'
        '<blockquote><b>'
        f'<tg-emoji emoji-id="4924866615515809418">📦</tg-emoji> Товар: {cat_name}\n'
        f'<tg-emoji emoji-id="4927470722906850798">💵</tg-emoji> Цена: {price} USDT/шт\n'
        f'<tg-emoji emoji-id="4924769914327140083">📦</tg-emoji> В наличии: {stock_count} шт.'
        '</b></blockquote>\n\n'
        '<b><tg-emoji emoji-id="4927416619203823091">🎉</tg-emoji> '
        'При заказах от 10 шт. действует скидка 20%</b>'
    )
    await message.answer(text, parse_mode="HTML", reply_markup=kb.as_markup())

# ═══════════════════════════════════════════════════════════════════════════════
# ОБРАБОТЧИКИ СООБЩЕНИЙ
# ═══════════════════════════════════════════════════════════════════════════════

@dp.message(F.text == "Ассортимент")
async def text_catalog(message: types.Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardBuilder()
    kb.button(text="Госуслуги 1960-2008R",callback_data="group_gy",icon_custom_emoji_id=CustomEmoji.GY,style="SUCCESS")
    kb.button(text="ТБанк", callback_data="group_tbank", icon_custom_emoji_id=CustomEmoji.TBANK, style="SUCCESS")
    kb.button(text="Логи 1952-2008R", callback_data="group_l0gu", icon_custom_emoji_id="5312126452043363774", style="SUCCESS")
    kb.adjust(1)
    text = (
        '<b><tg-emoji emoji-id="4924866615515809418">❓</tg-emoji> Ассортимент товаров</b>\n\n'
        '<blockquote><b><tg-emoji emoji-id="5213359409874377109">❓</tg-emoji> '
        'Выберите интересующий вас раздел:</b></blockquote>'
    )
    await send_with_image(message, 'AlteraStore', text, kb.as_markup())

@dp.message(F.text == "Профиль")
async def text_profile(message: types.Message, state: FSMContext):
    await state.clear()
    await show_profile_with_image(message.from_user.id, message)

@dp.message(F.text == "Пополнить баланс")
async def text_deposit(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(ShopState.waiting_for_deposit_provider)
    kb = InlineKeyboardBuilder()
    kb.button(text="@xRocket", callback_data="deposit_provider_xrocket", icon_custom_emoji_id=CustomEmoji.XROCKET_PAY, style='primary')
    kb.button(text="Telegram Stars", callback_data="deposit_provider_stars", icon_custom_emoji_id="5213085536989780516", style='primary')
    kb.adjust(1)
    text = '<b><tg-emoji emoji-id="4924714844256470686">💰</tg-emoji> Пополнение баланса ALTERA</b>\n\n<blockquote><b><tg-emoji emoji-id="5213359409874377109">❓</tg-emoji> Выберите удобный для Вас способ оплаты:</b></blockquote>'
    await send_with_image(message, 'EleghantBalance', text, kb.as_markup())

@dp.message(F.text == "FAQ")
async def text_faq(message: types.Message, user_id: Optional[int] = None, state: FSMContext = None):
    if state is not None:
        await state.clear()
    user_id = user_id or message.from_user.id
    completed_rows = await fetchall(
        "SELECT faq_key FROM faq_progress WHERE user_id = ?",
        (user_id,)
    )
    completed_keys = {row[0] for row in completed_rows}
    kb = InlineKeyboardBuilder()
    for text, key, emoji_id in (
        ("Что мы предоставляем?", "faq_offer", "5472197417854052950"),
        ("Подтвержденная УЗ, это?", "faq_verified", "5472261026319707797"),
        ("Применение гарантии", "faq_warranty", "5474428378486417299"),
        ("Поддержка", "faq_support", "5474354466394219119"),
    ):
        kb.button(
            text=text,
            callback_data=key,
            icon_custom_emoji_id=emoji_id,
            style="success" if key in completed_keys else "danger"
        )
    kb.adjust(1)
    progress = len(completed_keys.intersection(FAQ_KEYS))
    footer = (
        f'<blockquote><b><tg-emoji emoji-id="5215194567795575965">📖</tg-emoji> Прочитано: {progress} из {len(FAQ_KEYS)}</b></blockquote>'
        if progress < len(FAQ_KEYS)
        else "<blockquote><b>Выберите вопрос:</b></blockquote>"
    )
    await message.answer(
        f'<tg-emoji emoji-id="5212948901195190028">⭐️</tg-emoji> '
        '<b>FAQ</b> — раздел с ответами на наиболее распространённые вопросы пользователей. '
        'Рекомендуем ознакомиться с ним перед обращением в службу поддержки.\n\n'
        f'{footer}',
        parse_mode="HTML",
        reply_markup=kb.as_markup(),
    )

async def faq_access_granted(user_id: int) -> bool:
    row = await fetchone(
        "SELECT COUNT(*) FROM faq_progress WHERE user_id = ?",
        (user_id,)
    )
    return bool(row and row[0] >= len(FAQ_KEYS))

async def show_required_faq(message: types.Message):
    await message.answer(
        "<b>Перед использованием бота ознакомьтесь со всеми пунктами FAQ.</b>",
        parse_mode="HTML"
    )
    await text_faq(message)

async def show_agreement(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Пользовательское соглашение",
        url=AGREEMENT_URL,
        icon_custom_emoji_id="4925077425395599901",
        style="primary",
    )
    kb.button(
        text="Принять соглашение",
        callback_data="accept_agreement",
        icon_custom_emoji_id="5213056077809099062",
        style="success",
    )
    kb.adjust(1)
    await message.answer(
        '<tg-emoji emoji-id="5213301161527909232">📄</tg-emoji> '
        "<b>Ознакомьтесь с пользовательским соглашением.</b>\n\n"
        '<blockquote><b><tg-emoji emoji-id="4927376474144507529">➡️</tg-emoji> '
        "Для продолжения откройте документ и подтвердите принятие соглашения.</b></blockquote>",
        parse_mode="HTML",
        reply_markup=kb.as_markup(),
    )

async def show_privacy_policy(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Политика конфиденциальности",
        url=PRIVACY_POLICY_URL,
        icon_custom_emoji_id="4925077425395599901",
        style="primary",
    )
    kb.button(
        text="Принять политику",
        callback_data="accept_privacy",
        icon_custom_emoji_id="5213056077809099062",
        style="success",
    )
    kb.adjust(1)
    await message.answer(
        '<tg-emoji emoji-id="5213301161527909232">📄</tg-emoji> '
        "<b>Ознакомьтесь с политикой конфиденциальности.</b>\n\n"
        '<blockquote><b><tg-emoji emoji-id="4927376474144507529">➡️</tg-emoji> '
        "Для продолжения откройте документ и подтвердите ознакомление.</b></blockquote>",
        parse_mode="HTML",
        reply_markup=kb.as_markup(),
    )

@dp.callback_query(F.data.startswith("faq_"))
async def faq_item_cb(call: types.CallbackQuery):
    faq_key = call.data
    if faq_key.startswith("faq_next_"):
        faq_key = faq_key[len("faq_next_"):]
    elif faq_key.startswith("faq_prev_"):
        faq_key = faq_key[len("faq_prev_"):]
    answers = {
        "faq_offer": """<tg-emoji emoji-id="5463289097336405244">⭐️</tg-emoji> <b>Информация о нас</b>

Наш сервис позволяет быстро и автоматически получить подтверждённую учётную запись Госуслуг.

<tg-emoji emoji-id="5440410042773824003">🔗</tg-emoji> <b>Принцип работы:</b>
Для оформления требуется только номер телефона. После этого система автоматически создаёт новый профиль и проходит процедуру его подтверждения.

<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> <b>Обратите внимание:</b>
Услуга предназначена для регистрации новой учётной записи и не включает перенос или перепривязку уже существующего аккаунта.

<tg-emoji emoji-id="5461009483314517035">🎯</tg-emoji> <b>Основные преимущества:</b>
• Полностью автоматический процесс
• Моментальное получение доступа
• Официальный механизм регистрации
• Подтверждённый аккаунт
• Полный доступ ко всем возможностям Госуслуг""",
        "faq_verified": """<tg-emoji emoji-id="5372917041193828849">🚀</tg-emoji> <b>Подтверждённая учётная запись ГУ</b>

Верифицированный аккаунт на портале Госуслуг, который включает:

<tg-emoji emoji-id="5332724926216428039">📇</tg-emoji> <b>Проверенные паспортные данные</b>
→ Все сведения актуальны и прошли подтверждение

<tg-emoji emoji-id="5312361253610475399">🛒</tg-emoji> <b>Отсутствие ограничений в течение 72 часов</b>
→ Профиль готов к использованию сразу после получения

<tg-emoji emoji-id="5247152118069992250">🔓</tg-emoji> <b>Полный функционал портала</b>
→ Доступны все основные возможности Госуслуг

<tg-emoji emoji-id="5463172695132745432">📦</tg-emoji> <b>В комплекте:</b>
• Данные для входа (логин и пароль)
• Паспортные данные
• ИНН
• СНИЛС
• Полный доступ к аккаунту

<tg-emoji emoji-id="5408869739982246969">⭐</tg-emoji> <b>Возможности аккаунта:</b>
• Запись на приём к врачу
• Оплата штрафов и задолженностей
• Получение справок и выписок
• Оформление различных документов
• Использование других сервисов портала""",
        "faq_warranty": """<tg-emoji emoji-id="5296369303661067030">🔒</tg-emoji> <b>Гарантийные обязательства</b>

Мы гарантируем:

<tg-emoji emoji-id="5197366171434763365">✔️</tg-emoji> <b>Достоверность указанных данных</b>
→ Паспортные данные и ИНН, содержащиеся в профиле, являются действительными.

<tg-emoji emoji-id="5197366171434763365">✔️</tg-emoji> <b>Доступ к аккаунту</b>
→ Предоставляются актуальные данные для входа.
→ Авторизация в аккаунте осуществляется без ограничений на момент передачи.

<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> <b>Гарантия распространяется на следующие случаи:</b>

• Замена предоставляется только в случае получения невалидного ГУ. Во всех остальных случаях замена или возврат товара не предусмотрены.

<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> <b>Гарантия не распространяется на:</b>

• Отсутствие адреса постоянной регистрации.
• Неудовлетворительную кредитную историю.
• Возможность получения кредитных продуктов и иных финансовых услуг.
• Блокировки, ограничения или иные изменения, возникшие после передачи аккаунта покупателю.
• Возможность оформления банковских услуг
• Блокировку аккаунта в течение 72 часов - возврат <b>не производится</b>

<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji> <b>Порядок компенсации</b>

Если в предоставленном аккаунте будут обнаружены недействительные или некорректные данные, стоимость заказа зачисляется на баланс бота для оформления нового заказа.

<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> <b>Возврат денежных средств</b> на банковские карты, электронные кошельки и другие внешние платёжные системы <b>не осуществляется.</b>""",
        "faq_support": """<tg-emoji emoji-id="5354899958329784877">🎧</tg-emoji> <b>Служба поддержки</b>

Если у вас возникли вопросы или требуется помощь, вы можете обратиться к нашим специалистам через соответствующий раздел бота.

<tg-emoji emoji-id="5345951166335311399">📩</tg-emoji> <b>Способ обращения:</b>
→ Откройте меню «Поддержка» и отправьте свой запрос.

<tg-emoji emoji-id="5197239152071960003">⌚️</tg-emoji> <b>Срок обработки обращений:</b>
→ Обычно ответ поступает в течение 1 часа.

<tg-emoji emoji-id="5413879192267805083">🗓</tg-emoji> <b>График работы:</b>
→ Ежедневно без выходных
→ С 10:00 до 22:00 (МСК)

<tg-emoji emoji-id="5397782960512444700">📌</tg-emoji> <b>По каким вопросам можно обратиться:</b>

• Консультация перед оформлением заказа
• Вопросы по полученному аккаунту
• Помощь в решении технических сложностей
• Уточнение условий гарантии
• Другие вопросы, связанные с работой сервиса

<tg-emoji emoji-id="5463249828450424568">🤝</tg-emoji> <b>Мы готовы помочь</b>

Каждое обращение рассматривается в индивидуальном порядке. Наша задача — предоставить оперативную поддержку и помочь в решении возникших вопросов.

<tg-emoji emoji-id="5346132860631791153">📚</tg-emoji> <b>Полезно знать</b>

Перед созданием обращения рекомендуем ознакомиться с разделом FAQ. Там собраны ответы на самые популярные вопросы пользователей.""",
    }
    if faq_key not in answers:
        await call.answer("❌ Раздел FAQ не найден", show_alert=True)
        return
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data="back_to_faq", icon_custom_emoji_id=CustomEmoji.BACK, style="danger")
    if faq_key in FAQ_KEYS:
        await execute_query(
            "INSERT OR IGNORE INTO faq_progress (user_id, faq_key, completed_at) VALUES (?, ?, ?)",
            (call.from_user.id, faq_key, datetime.now(timezone.utc).isoformat()),
            commit=True
        )
        if await faq_access_granted(call.from_user.id):
            registration = await fetchone(
                "SELECT accepted, privacy_accepted FROM users WHERE id = ?",
                (call.from_user.id,),
            )
            await call.message.delete()
            if not registration or not registration[0]:
                await show_agreement(call.message)
            elif registration[1] != 1:
                await show_privacy_policy(call.message)
            else:
                await show_main_menu(call.message)
            await call.answer()
            return
    await call.message.edit_text(
        answers[faq_key],
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await call.answer()

@dp.message(F.text == "Поддержка")
async def text_help(message: types.Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardBuilder()
    kb.button(text="Владелец проекта", url=SUPPORT_ACCOUNT_URL, icon_custom_emoji_id=CustomEmoji.SUPPORTlife, style='primary')
    kb.button(text="Команда поддержки", url=SUPPORT_URL, icon_custom_emoji_id=CustomEmoji.SUPPORTbot, style='primary')
    kb.adjust(1)
    text = (f'<b><tg-emoji emoji-id="{CustomEmoji.SUPPORT_HEADER}">⏰</tg-emoji> Связаться с владельцем проекта и командой поддержки</b>\n\n'
        f'<blockquote><b>Если у вас возникли вопросы или проблемы, вы всегда можете обратиться в нашу службу поддержки. '
        f'Владельцу писать только в случаях предложений о сотрудничестве.</b></blockquote>\n\n'
            f'<b>С кем хотите связаться?</b>')
    await send_with_image(message, 'EleghantSupport', text, kb.as_markup())

@dp.message(F.text == "Предзаказ")
async def legacy_preorder_disabled(message: types.Message):
    await message.answer("Предзаказ отключен. Доступна покупка товаров в наличии.")

# ===========================
# ОБРАБОТЧИК ДЛЯ ТОТР-КЛЮЧЕЙ
# ===========================
@dp.message(F.text == "ТОТР-Ключи")
async def text_totp(message: types.Message):
    await message.answer("Раздел TOTP-Ключей удален из ALTERA.")

# --- ДОБАВЛЕНИЕ КЛЮЧА ---
@dp.callback_query(F.data == "totp_add")
async def totp_add_start(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(ShopState.waiting_for_totp_name)
    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена", callback_data="totp_cancel", icon_custom_emoji_id=CustomEmoji.BACKTOTP, style='danger')
    await call.message.edit_text(
        f'<tg-emoji emoji-id="{CustomEmoji.TOTP}">🔐</tg-emoji> <b>Добавление TOTP-ключа</b>\n\n'
        'Введите название для этого ключа (например: "ГосУслуги", "ГосУслуги2", "Гос1"):',
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await call.answer()

@dp.message(ShopState.waiting_for_totp_name)
async def totp_add_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        await message.answer("❌ Название не может быть пустым.")
        return
    # Проверяем, есть ли уже ключ с таким названием
    existing = await fetchone(
        "SELECT id FROM totp_keys WHERE user_id = ? AND name = ?",
        (message.from_user.id, name)
    )
    if existing:
        await message.answer(f"❌ Ключ с названием «{name}» уже существует. Используйте другое название.")
        return
    await state.update_data(totp_name=name)
    await state.set_state(ShopState.waiting_for_totp_secret)
    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена", callback_data="totp_cancel", icon_custom_emoji_id=CustomEmoji.BACKTOTP, style='danger')
    await message.answer(
        f'<tg-emoji emoji-id="{CustomEmoji.TOTP}">🔐</tg-emoji> <b>Ключ: {name}</b>\n\n'
        'Введите секретный ключ в формате base32.\n\n'
        'Пример: <code>JBSWY3DPEHPK3PXP</code>\n\n'
        'Ключ можно скопировать из приложения-аутентификатора.',
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )

@dp.message(ShopState.waiting_for_totp_secret)
async def totp_add_secret(message: types.Message, state: FSMContext):
    secret = message.text.strip().upper().replace(' ', '')
    # Проверяем, что секрет в формате base32
    try:
        # Пытаемся декодировать base32
        base64.b32decode(secret, casefold=True)
    except Exception:
        await message.answer(
            "❌ Неверный формат секретного ключа.\n\n"
            "Убедитесь, что вы ввели корректный base32 ключ.\n"
            "Пример: <code>JBSWY3DPEHPK3PXP</code>",
            parse_mode="HTML"
        )
        return
    data = await state.get_data()
    name = data.get('totp_name')
    user_id = message.from_user.id
    # Сохраняем ключ в БД
    await execute_query(
        "INSERT INTO totp_keys (user_id, name, secret, created_at) VALUES (?, ?, ?, ?)",
        (user_id, name, secret, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")),
        commit=True
    )
    await message.answer(
        f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CHECK}">✅</tg-emoji> <b>Ключ «{name}» успешно добавлен!</b>',
        parse_mode="HTML"
    )
    await state.clear()
    # Показываем меню TOTP
    await text_totp(message)

# --- СПИСОК КЛЮЧЕЙ ---
@dp.callback_query(F.data == "totp_list")
async def totp_list(call: types.CallbackQuery):
    user_id = call.from_user.id
    keys = await fetchall(
        "SELECT id, name, secret, created_at FROM totp_keys WHERE user_id = ?",
        (user_id,)
    )
    if not keys:
        kb = InlineKeyboardBuilder()
        kb.button(text="Назад", callback_data="totp_back_to_menu", style='danger')
        await call.message.edit_text(
            f'<tg-emoji emoji-id="{CustomEmoji.TOTP}">🔐</tg-emoji> <b>Мои TOTP-ключи</b>\n\n'
            'У вас пока нет сохранённых ключей.',
            parse_mode="HTML",
            reply_markup=kb.as_markup()
        )
        await call.answer()
        return
    kb = InlineKeyboardBuilder()
    for key_id, name, secret, created_at in keys:
        # Генерируем текущий код
        try:
            totp = pyotp.TOTP(secret)
            code = totp.now()
            # Подсчитываем оставшиеся секунды до смены кода
            remaining = 30 - (int(time.time()) % 30)
            kb.button(
                text=f"🔑 {name}: {code} ({remaining}с)",
                callback_data=f"totp_view_{key_id}"
            )
        except Exception as e:
            logger.error(f"Ошибка генерации TOTP для {name}: {e}")
            kb.button(
                text=f"❌ {name}: ошибка",
                callback_data=f"totp_view_{key_id}"
            )
    kb.button(text="Добавить ключ", callback_data="totp_add", icon_custom_emoji_id=CustomEmoji.ADDTOTP, style='SUCCESS')
    kb.button(text="Назад", callback_data="totp_back_to_menu", style='danger')
    kb.adjust(1)
    await call.message.edit_text(
        f'<tg-emoji emoji-id="{CustomEmoji.TOTP}">🔐</tg-emoji> <b>Мои TOTP-ключи</b>\n\n'
        'Нажмите на ключ для управления им.\n'
        'Коды обновляются каждые 30 секунд.',
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await call.answer()

# --- ПРОСМОТР КОНКРЕТНОГО КЛЮЧА ---
@dp.callback_query(F.data.startswith("totp_view_"))
async def totp_view(call: types.CallbackQuery):
    try:
        key_id = int(call.data.split("_")[2])
    except (IndexError, ValueError):
        await call.answer("❌ Ошибка")
        return
    user_id = call.from_user.id
    key = await fetchone(
        "SELECT id, name, secret, created_at FROM totp_keys WHERE id = ? AND user_id = ?",
        (key_id, user_id)
    )
    if not key:
        await call.answer("❌ Ключ не найден", show_alert=True)
        return
    key_id, name, secret, created_at = key
    try:
        totp = pyotp.TOTP(secret)
        code = totp.now()
        remaining = 30 - (int(time.time()) % 30)
        progress = int((30 - remaining) / 30 * 10)
        progress_bar = "█" * progress + "░" * (10 - progress)
        code_text = (
            f'<tg-emoji emoji-id="{CustomEmoji.TOTP}">🔐</tg-emoji> <b>{name}</b>\n\n'
            f'<b>Текущий код:</b>\n'
            f'<code>{code}</code>\n\n'
            f'Обновление через: <b>{remaining} сек.</b>\n'
            f'[{progress_bar}]'
        )
    except Exception as e:
        logger.error(f"Ошибка генерации TOTP для {name}: {e}")
        code_text = f'❌ <b>{name}</b>\n\nОшибка генерации кода. Возможно, секретный ключ повреждён.'
    kb = InlineKeyboardBuilder()
    kb.button(text="Обновить", callback_data=f"totp_refresh_{key_id}", style = 'primary')
    kb.button(text="Удалить", callback_data=f"totp_delete_{key_id}", style="danger")
    kb.button(text="Назад к списку", callback_data="totp_list", style='danger')
    kb.adjust(1)
    await call.message.edit_text(
        code_text,
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await call.answer()

# --- ОБНОВЛЕНИЕ КОНКРЕТНОГО КЛЮЧА ---
@dp.callback_query(F.data.startswith("totp_refresh_"))
async def totp_refresh(call: types.CallbackQuery):
    try:
        key_id = int(call.data.split("_")[2])
    except (IndexError, ValueError):
        await call.answer("Ошибка")
        return
    # Просто перенаправляем на просмотр
    await totp_view(call)

# --- ОБНОВЛЕНИЕ ВСЕХ КЛЮЧЕЙ ---
@dp.callback_query(F.data == "totp_refresh_all")
async def totp_refresh_all(call: types.CallbackQuery):
    # Просто обновляем список
    await totp_list(call)

# --- УДАЛЕНИЕ КЛЮЧА ---
@dp.callback_query(F.data.startswith("totp_delete_"))
async def totp_delete(call: types.CallbackQuery):
    try:
        key_id = int(call.data.split("_")[2])
    except (IndexError, ValueError):
        await call.answer("❌ Ошибка")
        return
    user_id = call.from_user.id
    key = await fetchone(
        "SELECT name FROM totp_keys WHERE id = ? AND user_id = ?",
        (key_id, user_id)
    )
    if not key:
        await call.answer("❌ Ключ не найден", show_alert=True)
        return
    name = key[0]
    kb = InlineKeyboardBuilder()
    kb.button(text="Да, удалить", callback_data=f"totp_confirm_delete_{key_id}", style="danger")
    kb.button(text="Отмена", callback_data=f"totp_view_{key_id}")
    kb.adjust(1)
    await call.message.edit_text(
        f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">⚠️</tg-emoji> <b>Удаление ключа</b>\n\n'
        f'Вы уверены, что хотите удалить ключ «{name}»?\n\n'
        f'<b>Это действие необратимо!</b>',
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await call.answer()

@dp.callback_query(F.data.startswith("totp_confirm_delete_"))
async def totp_confirm_delete(call: types.CallbackQuery):
    try:
        key_id = int(call.data.split("_")[3])
    except (IndexError, ValueError):
        await call.answer("❌ Ошибка")
        return
    user_id = call.from_user.id
    key = await fetchone(
        "SELECT name FROM totp_keys WHERE id = ? AND user_id = ?",
        (key_id, user_id)
    )
    if not key:
        await call.answer("❌ Ключ не найден", show_alert=True)
        return
    name = key[0]
    await execute_query(
        "DELETE FROM totp_keys WHERE id = ? AND user_id = ?",
        (key_id, user_id),
        commit=True
    )
    await call.message.edit_text(
        f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CHECK}">✅</tg-emoji> Ключ «{name}» успешно удалён.',
        parse_mode="HTML"
    )
    await call.answer()
    # Через секунду показываем список
    await asyncio.sleep(1)
    await totp_list(call)

# --- ОТМЕНА ДОБАВЛЕНИЯ ---
@dp.callback_query(F.data == "totp_cancel")
async def totp_cancel(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Действие отменено.")
    await call.answer()
    await text_totp(call.message)

# --- ВОЗВРАТ В МЕНЮ TOTP ---
@dp.callback_query(F.data == "totp_back_to_menu")
async def totp_back_to_menu(call: types.CallbackQuery):
    await call.message.delete()
    await text_totp(call.message)
    await call.answer()

# --- КАТАЛОГ ---
@dp.callback_query(F.data.startswith("group_"))
async def show_group_categories(call: types.CallbackQuery):
    group_key = call.data.split("_")[1]
    await show_categories_group(call, group_key)

@dp.callback_query(F.data == "back_to_main_catalog")
async def back_to_main_catalog(call: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="Госуслуги 1960-2008R",callback_data="group_gy",icon_custom_emoji_id=CustomEmoji.GY,style="SUCCESS")
    kb.button(text="ТБанк", callback_data="group_tbank", icon_custom_emoji_id=CustomEmoji.TBANK, style="SUCCESS")
    kb.button(text="Логи 1952-2008R", callback_data="group_l0gu", icon_custom_emoji_id="5312126452043363774", style="SUCCESS")
    kb.adjust(1)
    text = (
        '<b><tg-emoji emoji-id="4924866615515809418">❓</tg-emoji> Ассортимент товаров</b>\n\n'
        '<blockquote><b><tg-emoji emoji-id="5213359409874377109">❓</tg-emoji> '
        'Выберите интересующий вас раздел:</b></blockquote>'
    )
    await call.message.delete()
    await send_with_image(call.message, 'AlteraStore', text, kb.as_markup())
    await call.answer()

@dp.callback_query(F.data == "back_to_l0gu")
async def back_to_l0gu(call: types.CallbackQuery):
    await show_categories_group(call, "l0gu")

@dp.callback_query(F.data == "back_to_gy")
async def back_to_gy(call: types.CallbackQuery):
    await show_categories_group(call, "gy")

@dp.callback_query(F.data == "back_to_tbank")
async def back_to_tbank(call: types.CallbackQuery):
    await show_categories_group(call, "tbank")

@dp.callback_query(F.data.startswith("view_"))
async def view_cat_cb(call: types.CallbackQuery):
    try:
        cid = int(call.data.split("_")[1])
    except Exception:
        await call.answer("❌ Ошибка")
        return
    cat = await fetchone("SELECT name, desc, price, cat_group, maintenance FROM categories WHERE id = ?", (cid,))
    if not cat:
        await call.answer("❌ Категория не найдена")
        return
    cat_name, cat_desc, cat_price, cat_group, maintenance = cat
    if maintenance:
        await call.answer("🛠 Категория временно на технических работах.", show_alert=True)
        return
    stock = await fetchone("SELECT COUNT(*) FROM inventory WHERE cat_id = ?", (cid,))
    stock_count = stock[0] if stock else 0
    review_stats = await fetchone(
        "SELECT COUNT(*), COALESCE(AVG(rating), 0) FROM reviews WHERE cat_id = ?", (cid,)
    )
    review_count, review_avg = review_stats or (0, 0)
    text = (
        f'<b>{cat_desc}\n\n'
        f'<tg-emoji emoji-id="{CustomEmoji.PRICE}">💵</tg-emoji> Цена: {cat_price} USDT/шт\n'
        f'<tg-emoji emoji-id="{CustomEmoji.STOCK}">❗️</tg-emoji> Наличие: {stock_count} шт.\n'
        f'<tg-emoji emoji-id="{CustomEmoji.RATING}">⭐</tg-emoji> Рейтинг: {review_avg:.1f}/5.0 ({review_count} отзывов)</b>'
    )
    kb = InlineKeyboardBuilder()
    if stock_count > 0:
        kb.button(text="Купить", callback_data=f"buy_{cid}", icon_custom_emoji_id="4925115139503455129", style='success')
    else:
        kb.button(text="Нет в наличии", callback_data=f"out_of_stock_{cid}", style='danger')
    if cat_group == "l0gu_1970":
        kb.button(text="Назад к операторам", callback_data="back_to_l0gu", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    elif cat_group == "gy_1970":
        kb.button(text="Назад к GY", callback_data="back_to_gy", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    elif cat_group == "tbank":
        kb.button(text="Назад к ТБанку", callback_data="back_to_tbank", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    else:
        kb.button(text="Назад к разделам", callback_data="back_to_main_catalog", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    kb.adjust(1)
    await call.message.delete()
    await call.message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("out_of_stock_"))
async def out_of_stock_cb(call: types.CallbackQuery):
    await call.answer("❌ Товар закончился. Предзаказ оформляется только напрямую через лот.", show_alert=True)

# --- ПРЕДЗАКАЗ ---
@dp.callback_query(F.data.startswith("preorder_cat_"))
async def preorder_cat_cb(call: types.CallbackQuery, state: FSMContext):
    try:
        cat_id = int(call.data.split("_")[2])
    except (IndexError, ValueError):
        await call.answer("❌ Ошибка", show_alert=True)
        return
    cat = await fetchone("SELECT name, price FROM categories WHERE id = ?", (cat_id,))
    if not cat:
        await call.answer("❌ Категория не найдена", show_alert=True)
        return
    await state.update_data(preorder_cat_id=cat_id, preorder_cat_name=cat[0], preorder_price=cat[1])
    await state.set_state(ShopState.waiting_for_preorder_quantity)
    await call.message.answer(
        f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_BOX}">📦</tg-emoji> <b>Предзаказ: {cat[0]}</b>\n'
        f'<tg-emoji emoji-id="{CustomEmoji.MONEY}">💰</tg-emoji> Цена: {cat[1]} USDT/шт\n\n'
        f'<tg-emoji emoji-id="{CustomEmoji.QUESTION}">❓</tg-emoji> Сколько штук хотите предзаказать? (от {MIN_PREORDER_QUANTITY} до {MAX_QUANTITY_PER_PURCHASE} шт.)\n'
        f"Отправьте число:", parse_mode="HTML"
    )
    await call.answer()

@dp.message(ShopState.waiting_for_preorder_quantity)
async def preorder_quantity_msg(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❗️</tg-emoji> Введите положительное число.', parse_mode="HTML")
    qty = int(message.text)
    if qty < MIN_PREORDER_QUANTITY or qty > MAX_QUANTITY_PER_PURCHASE:
        return await message.answer(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❗️</tg-emoji> Введите число от {MIN_PREORDER_QUANTITY} до {MAX_QUANTITY_PER_PURCHASE}.', parse_mode="HTML")
    data = await state.get_data()
    cat_id = data['preorder_cat_id']
    cat_name = data['preorder_cat_name']
    price = data['preorder_price']
    total = round(price * qty, 2)
    await state.update_data(preorder_qty=qty, preorder_total=total)
    await state.set_state(ShopState.waiting_for_preorder_provider)
    kb = InlineKeyboardBuilder()
    kb.button(text="Оплатить @xRocket", callback_data="preorder_pay_xrocket", icon_custom_emoji_id=CustomEmoji.XROCKET_PAY, style='primary')
    kb.adjust(1)
    await message.answer(
        f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_BOX}">📦</tg-emoji> {cat_name} x{qty}\n'
        f'<tg-emoji emoji-id="{CustomEmoji.MONEY}">💰</tg-emoji> Сумма: {total} USDT\n\n'
        f'Выберите способ оплаты:',
        reply_markup=kb.as_markup(), parse_mode="HTML"
    )

@dp.callback_query(F.data == "preorder_pay_xrocket", ShopState.waiting_for_preorder_provider)
async def preorder_pay_provider_cb(call: types.CallbackQuery, state: FSMContext):
    provider = "xrocket"
    data = await state.get_data()
    cat_id = data['preorder_cat_id']
    cat_name = data['preorder_cat_name']
    qty = data['preorder_qty']
    total = data['preorder_total']
    user_id = call.from_user.id

    await execute_query(
        "INSERT INTO preorders (user_id, cat_id, quantity, total, created_at, status) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, cat_id, qty, total, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), "pending"),
        commit=True
    )
    preorder = await fetchone("SELECT id FROM preorders WHERE user_id = ? AND cat_id = ? ORDER BY id DESC LIMIT 1",
                              (user_id, cat_id))
    preorder_id = preorder[0] if preorder else None

    if provider == "xrocket":
        inv = await xrocket_create_invoice(amount=total, description=f"Предзаказ: {cat_name} x{qty}", expired_in=3600)
        if not inv.get('ok'):
            await call.message.answer(f"⚠ Ошибка API xRocket: {inv.get('description', 'Неизвестная ошибка')}")
            await state.clear()
            await call.answer()
            return
        invoice_id = inv['id']
        pay_url = inv['link']
        provider_emoji = CustomEmoji.XROCKET_PAY
    pending_payments[invoice_id] = {
        'user_id': user_id, 'cat_id': cat_id, 'quantity': qty,
        'total': total, 'created_at': datetime.now(), 'is_preorder': True,
        'preorder_id': preorder_id, 'provider': provider
    }
    kb = InlineKeyboardBuilder()
    kb.button(text="Оплатить предзаказ", url=pay_url, icon_custom_emoji_id=provider_emoji, style='success')
    kb.button(text="Проверить оплату", callback_data=f"check_payment_{invoice_id}", style='primary', icon_custom_emoji_id=CustomEmoji.CHECKPAY)
    kb.adjust(1)
    msg = await call.message.answer(
        f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CLOCK}">🕞</tg-emoji> <b>Предзаказ оформлен!</b>\n\n'
        f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_BOX}">📦</tg-emoji> Товар: {cat_name}\n'
        f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_SETTINGS}">🔢</tg-emoji> Количество: {qty} шт.\n'
        f'<tg-emoji emoji-id="{CustomEmoji.MONEY}">💰</tg-emoji> Сумма: {total} USDT\n\n'
        f'Нажмите кнопку ниже для оплаты:',
        reply_markup=kb.as_markup(), parse_mode="HTML"
    )
    pending_payments[invoice_id]['msg'] = msg
    asyncio.create_task(auto_check_preorder_payment(invoice_id, user_id, cat_id, qty, msg, total, cat_name, preorder_id, provider))
    await state.clear()
    await call.answer()

async def auto_check_preorder_payment(invoice_id, user_id: int, cat_id: int, quantity: int,
                                      msg_to_edit: types.Message, total_cost: float, cat_name: str,
                                      preorder_id: int = None, provider: str = "xrocket"):
    async with payment_check_semaphore:
        for attempt in range(PAYMENT_CHECK_ATTEMPTS):
            await asyncio.sleep(PAYMENT_CHECK_INTERVAL)
            if invoice_id not in pending_payments:
                return
            if provider == "xrocket":
                inv = await xrocket_get_invoice(str(invoice_id))
                if not inv.get('ok'):
                    continue
                is_paid = _xrocket_is_paid(inv.get('status'), inv.get('paid_amount'))
                is_expired = _xrocket_is_expired(inv.get('status'))
            if is_paid:
                if preorder_id:
                    await execute_query("UPDATE preorders SET status = 'paid', paid_at = ? WHERE id = ?",
                                      (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), preorder_id), commit=True)
                del pending_payments[invoice_id]
                await get_active_bot().send_message(user_id,
                    f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CHECK}">✅</tg-emoji> <b>Предзаказ оплачен!</b>\n\n'
                    f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_BOX}">📦</tg-emoji> Товар: {cat_name}\n'
                    f'<tg-emoji emoji-id="{CustomEmoji.MONEY}">💰</tg-emoji> Сумма: {total_cost} USDT\n\n'
                    f'Как только товар появится, он будет автоматически выдан вам.',
                    parse_mode="HTML"
                )
                try:
                    await msg_to_edit.delete()
                except Exception:
                    pass
                return
            elif is_expired:
                if preorder_id:
                    await execute_query("UPDATE preorders SET status = 'expired' WHERE id = ?", (preorder_id,), commit=True)
                await msg_to_edit.edit_text(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Счет просрочен.', parse_mode="HTML")
                del pending_payments[invoice_id]
                return
        if invoice_id in pending_payments:
            if preorder_id:
                await execute_query("UPDATE preorders SET status = 'expired' WHERE id = ?", (preorder_id,), commit=True)
            await msg_to_edit.edit_text(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Время ожидания истекло.', parse_mode="HTML")
            del pending_payments[invoice_id]

@dp.callback_query(F.data == "cancel_preorder")
async def cancel_preorder_cb(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Предзаказ отменен', parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data.startswith("preorder_from_cat_"))
async def preorder_from_cat_cb(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = int(call.data.split("_")[3])
    except (IndexError, ValueError):
        await call.answer("❌ Ошибка", show_alert=True)
        return
    cat = await fetchone("SELECT name, price, maintenance FROM categories WHERE id = ?", (cid,))
    if not cat:
        await call.answer("❌ Категория не найдена", show_alert=True)
        return
    await state.update_data(preorder_cat_id=cid, preorder_cat_name=cat[0], preorder_price=cat[1])
    await state.set_state(ShopState.waiting_for_preorder_quantity)
    await call.message.answer(
        f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CLOCK}">🕞</tg-emoji> <b>Предзаказ: {cat[0]}</b>\n'
        f'<tg-emoji emoji-id="{CustomEmoji.MONEY}">💰</tg-emoji> Цена: {cat[1]} USDT/шт\n\n'
        f'<tg-emoji emoji-id="{CustomEmoji.QUESTION}">❓</tg-emoji> Сколько штук хотите предзаказать? (от {MIN_PREORDER_QUANTITY} до {MAX_QUANTITY_PER_PURCHASE} шт.)\n'
        f"Отправьте число:", parse_mode="HTML"
    )
    await call.answer()

# ═══════════════════════════════════════════════════════════════════════════════
# ПОКУПКА
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data.startswith("buy_"))
async def buy_cb(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = int(call.data.split("_")[1])
    except Exception:
        await call.answer("❌ Ошибка")
        return
    cat = await fetchone("SELECT name, price FROM categories WHERE id = ?", (cid,))
    if not cat:
        await call.answer("❌ Категория не найдена")
        return
    stock = await fetchone("SELECT COUNT(*) FROM inventory WHERE cat_id = ?", (cid,))
    stock_count = stock[0] if stock else 0
    if stock_count == 0:
        await call.answer("❌ Товар закончился", show_alert=True)
        return
    cat_name, price = cat[0], float(cat[1])
    await state.update_data(cid=cid, cat_name=cat_name, price=price, stock_count=stock_count)
    await state.set_state(ShopState.waiting_for_quantity)
    await show_quantity_keyboard(call.message, cid, cat_name, price, stock_count)
    await call.answer()

@dp.callback_query(F.data.startswith("qty_custom_"), ShopState.waiting_for_quantity)
async def qty_custom_cb(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = int(call.data.split("_")[2])
    except Exception:
        await call.answer("❌ Ошибка")
        return
    await state.set_state(ShopState.waiting_for_custom_quantity)
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data=f"back_to_category_{cid}", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    kb.adjust(1)
    await call.message.edit_text(
        f'<tg-emoji emoji-id="{CustomEmoji.QUESTION}">❓</tg-emoji> Введите количество (1–{MAX_QUANTITY_PER_PURCHASE}):',
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await call.answer()

@dp.callback_query(F.data.startswith("qty_"), ShopState.waiting_for_quantity)
async def qty_preset_cb(call: types.CallbackQuery, state: FSMContext):
    parts = call.data.split("_")
    try:
        cid = int(parts[1])
        qty = int(parts[2])
    except Exception:
        await call.answer("❌ Ошибка")
        return
    await _process_quantity_chosen(call.message, state, call.from_user.id, cid, qty, call)

@dp.message(ShopState.waiting_for_custom_quantity)
async def custom_quantity_msg(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        return await message.answer(
            f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❗️</tg-emoji> Введите положительное число.',
            parse_mode="HTML"
        )
    qty = int(message.text)
    if qty <= 0 or qty > MAX_QUANTITY_PER_PURCHASE:
        return await message.answer(
            f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❗️</tg-emoji> Введите число от 1 до {MAX_QUANTITY_PER_PURCHASE}.',
            parse_mode="HTML"
        )
    data = await state.get_data()
    cid = data.get('cid')
    if not cid:
        await message.answer("❌ Ошибка состояния, начните покупку заново.")
        await state.clear()
        return
    await _process_quantity_chosen(message, state, message.from_user.id, cid, qty)

async def _process_quantity_chosen(
    message: types.Message,
    state: FSMContext,
    user_id: int,
    cid: int,
    qty: int,
    call: types.CallbackQuery = None
):
    stock = await fetchone("SELECT COUNT(*) FROM inventory WHERE cat_id = ?", (cid,))
    stock_count = stock[0] if stock else 0
    cat = await fetchone("SELECT name, price, maintenance FROM categories WHERE id = ?", (cid,))
    if not cat:
        await message.answer("❌ Категория не найдена")
        await state.clear()
        if call:
            await call.answer()
        return
    cat_name, price, maintenance = cat[0], float(cat[1]), bool(cat[2])
    if maintenance:
        await message.answer("🛠 Эта категория временно на технических работах.")
        await state.clear()
        return
    if qty > stock_count:
        await state.clear()
        txt = (
            f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❗️</tg-emoji> В наличии только <b>{stock_count} шт.</b>\n\n'
            f'Предзаказ недоступен. Выберите меньшее количество или вернитесь позже.'
        )
        await message.answer(txt, parse_mode="HTML")
        if call:
            await call.answer()
        return
    total = round(price * qty, 2)
    discount_text = ""
    if qty >= 10:
        total = round(total * 0.8, 2)
        discount_text = f'\n<tg-emoji emoji-id="{CustomEmoji.DISCOUNT}">🎉</tg-emoji> <b>Скидка 20% применена за заказ от 10 шт.</b>'
    # Применяем промокод (если есть)
    if hasattr(get_active_bot(), 'user_promos') and user_id in get_active_bot().user_promos:
        promo_data = get_active_bot().user_promos[user_id]
        if promo_data['type'] == 'percent':
            discount = round(total * promo_data['discount'] / 100, 2)
            total = round(total - discount, 2)
            discount_text += f'\n<tg-emoji emoji-id="{CustomEmoji.PROMO}">🎫</tg-emoji> Скидка {promo_data["discount"]}% по промокоду!'
            del get_active_bot().user_promos[user_id]
    balance = await get_balance(user_id)
    await state.update_data(cid=cid, quantity=qty, total=total, cat_name=cat_name)
    await state.set_state(ShopState.waiting_for_payment_method)
    kb = InlineKeyboardBuilder()
    kb.button(text="Подтвердить выбор", callback_data="confirm_purchase", icon_custom_emoji_id="5213056077809099062", style='success')
    kb.button(text="Отменить заказ", callback_data=f"cancel_purchase_{cid}", icon_custom_emoji_id="5215248628548931525", style='danger')
    kb.adjust(1)
    text = (
        '<b>'
        f'<tg-emoji emoji-id="4924866615515809418">❓</tg-emoji> {cat_name} × {qty} шт.\n'
        f'<tg-emoji emoji-id="4927470722906850798">💵</tg-emoji> Цена за шт.: {price} USDT\n'
        f'<tg-emoji emoji-id="5213056077809099062">❓</tg-emoji> Итого: {total} USDT'
        f'{discount_text}\n'
        f'<tg-emoji emoji-id="4924714844256470686">❓</tg-emoji> Ваш баланс: {balance} USDT'
        '</b>\n\n'
        '<blockquote><b><tg-emoji emoji-id="5213256712911363107">🛡️</tg-emoji> '
        'Проверьте выбор перед оплатой:</b></blockquote>'
    )
    await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    if call:
        await call.answer()

@dp.callback_query(F.data.startswith("cancel_purchase"))
async def cancel_purchase_cb(call: types.CallbackQuery, state: FSMContext):
    try:
        cid = int(call.data.rsplit("_", 1)[1])
    except (IndexError, ValueError):
        data = await state.get_data()
        cid = data.get("cid")
    await state.clear()
    if cid:
        category_call = call.model_copy(update={"data": f"view_{cid}"})
        await view_cat_cb(category_call)
    else:
        await call.message.edit_text("❌ Покупка отменена.")
        await call.answer()

@dp.callback_query(F.data.startswith("cancel_payment_"))
async def cancel_payment_cb(call: types.CallbackQuery):
    invoice_id = call.data.removeprefix("cancel_payment_")
    payment_data = pending_payments.get(invoice_id)
    if payment_data is None:
        try:
            payment_data = pending_payments.get(int(invoice_id))
        except ValueError:
            payment_data = None
    if not payment_data:
        await call.answer("Счёт уже отменён или обработан.", show_alert=True)
        return
    if payment_data["user_id"] != call.from_user.id:
        await call.answer("❌ Это не ваш заказ.", show_alert=True)
        return
    cat_id = payment_data["cat_id"]
    pending_payments.pop(invoice_id, None)
    try:
        pending_payments.pop(int(invoice_id), None)
    except ValueError:
        pass
    category_call = call.model_copy(update={"data": f"view_{cat_id}"})
    await view_cat_cb(category_call)

@dp.callback_query(F.data == "confirm_purchase", ShopState.waiting_for_payment_method)
async def confirm_purchase_cb(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    balance = await get_balance(call.from_user.id)
    kb = InlineKeyboardBuilder()
    kb.button(text="@xRocket", callback_data="pay_xrocket", icon_custom_emoji_id=CustomEmoji.XROCKET_PAY, style='primary')
    kb.button(text="Telegram Stars", callback_data="pay_stars", icon_custom_emoji_id="5213085536989780516", style='primary')
    kb.button(text="Баланс", callback_data="pay_balance", icon_custom_emoji_id="4925106025582823166", style='primary')
    kb.button(text="Отменить заказ", callback_data=f"cancel_purchase_{data['cid']}", icon_custom_emoji_id="5215248628548931525", style='danger')
    kb.adjust(1)
    await call.message.edit_text(
        f'<b><tg-emoji emoji-id="4924866615515809418">❓</tg-emoji> '
        f'{data.get("cat_name")} × {data.get("quantity")} шт.\n'
        f'<tg-emoji emoji-id="4927470722906850798">💵</tg-emoji> '
        f'Итого: {data.get("total")} USDT\n'
        f'<tg-emoji emoji-id="4925106025582823166">❓</tg-emoji> '
        f'Баланс: {balance:.2f} USDT</b>\n\n'
        '<blockquote><b><tg-emoji emoji-id="4924819078817777378">💳</tg-emoji> '
        'Выберите способ оплаты:</b></blockquote>',
        parse_mode="HTML", reply_markup=kb.as_markup()
    )
    await call.answer()

@dp.callback_query(F.data == "pay_stars")
async def pay_stars_cb(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    total = round(float(data["total"]), 2)
    stars = max(1, int(round(total * STAR_USDT_RATE)))
    await call.message.answer_invoice(
        title="Покупка в ALTERA",
        description=f"{data['cat_name']} x{data['quantity']} — {total:.2f} USDT",
        payload=json.dumps({
            "type": "purchase", "cat_id": data["cid"], "quantity": data["quantity"], "total": total
        }, separators=(",", ":")),
        currency="XTR",
        prices=[LabeledPrice(label=f"{data['cat_name']} x{data['quantity']}", amount=stars)],
        reply_markup=InlineKeyboardBuilder().button(
            text="Отменить заказ",
            callback_data=f"cancel_purchase_{data['cid']}",
            icon_custom_emoji_id="5215248628548931525",
            style="danger",
        ).as_markup(),
    )
    await state.clear()
    await call.answer()

@dp.callback_query(F.data == "pay_xrocket")
async def pay_xrocket_cb(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cid = data['cid']
    quantity = data['quantity']
    total = data['total']
    cat_name = data['cat_name']
    user_id = call.from_user.id
    inv = await xrocket_create_invoice(amount=total, description=f"{cat_name} x{quantity}", expired_in=1800)
    if not inv.get('ok'):
        await call.message.answer(f"⚠ Ошибка API xRocket: {inv.get('description', 'Неизвестная ошибка')}")
        await state.clear()
        return
    invoice_id = inv['id']
    pending_payments[invoice_id] = {
        'user_id': user_id, 'cat_id': cid, 'quantity': quantity,
        'total': total, 'created_at': datetime.now(), 'is_preorder': False, 'provider': 'xrocket'
    }
    kb = InlineKeyboardBuilder()
    kb.button(text="Оплатить", url=inv['link'], icon_custom_emoji_id=CustomEmoji.XROCKET_PAY, style='success')
    kb.button(text="Проверить оплату", callback_data=f"check_payment_{invoice_id}", style='primary', icon_custom_emoji_id=CustomEmoji.CHECKPAY)
    kb.button(text="Отменить заказ", callback_data=f"cancel_payment_{invoice_id}", icon_custom_emoji_id="5215248628548931525", style='danger')
    kb.adjust(1)
    msg = await call.message.answer(
        f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_BOX}">📦</tg-emoji> {cat_name} — {quantity} шт.\n'
        f'<tg-emoji emoji-id="{CustomEmoji.MONEY}">💰</tg-emoji> Сумма: {total} USDT\n'
        f'<tg-emoji emoji-id="{CustomEmoji.TIME}">⏳</tg-emoji> Счет действителен 30 минут\n\nНажмите кнопку ниже для оплаты:',
        reply_markup=kb.as_markup(), parse_mode="HTML"
    )
    pending_payments[invoice_id]['msg'] = msg
    asyncio.create_task(auto_check_payment(invoice_id, user_id, cid, quantity, msg, total, 'xrocket'))
    await state.clear()
    await call.answer()

@dp.callback_query(F.data == "pay_balance")
async def pay_balance_cb(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cid = data['cid']
    quantity = data['quantity']
    total = data['total']
    cat_name = data['cat_name']
    user_id = call.from_user.id
    balance = await get_balance(user_id)
    if balance < total:
        await call.message.answer(
            f'<blockquote><b>'
            f'<tg-emoji emoji-id="5213360384831952090">🛡️</tg-emoji> Недостаточно средств.\n'
            f'<tg-emoji emoji-id="4927470722906850798">💵</tg-emoji> Ваш баланс: {balance} USDT\n'
            f'<tg-emoji emoji-id="4925106025582823166">❓</tg-emoji> Необходимо: {total} USDT'
            f'</b></blockquote>',
            parse_mode="HTML",
        )
        await state.clear()
        await call.answer()
        return
    try:
        items = await buy_items_with_transaction(cid, quantity, user_id, total)
        if not items:
            await call.message.answer(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Товар закончился. Деньги не списаны.', parse_mode="HTML")
            await state.clear()
            await call.answer()
            return
        res_text = f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CHECK}">✅</tg-emoji> Оплачено с баланса!\n\n<tg-emoji emoji-id="{CustomEmoji.PREORDER_BOX}">🎁</tg-emoji> Ваш товар:\n'
        for _, i_data in items:
            res_text += f"• `{i_data}`\n"
        await call.message.answer(
            res_text,
            parse_mode="Markdown",
            reply_markup=purchase_review_keyboard(cid).as_markup(),
        )
        referrer = await fetchone("SELECT referrer_id FROM users WHERE id = ?", (user_id,))
        if referrer and referrer[0]:
            ref_bonus = round(total * 0.1, 2)
            await add_referral_earning(referrer[0], ref_bonus, user_id)
            await get_active_bot().send_message(referrer[0], f'<tg-emoji emoji-id="{CustomEmoji.MONEY}">💰</tg-emoji> Вы получили {ref_bonus} USDT (10%) от покупки!', parse_mode="HTML")
    except Exception as e:
        logger.error(f"Payment error: {e}")
        await call.message.answer(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Ошибка при покупке. Обратитесь в поддержку.', parse_mode="HTML")
    await state.clear()
    await call.answer()

# --- ПРОФИЛЬ ---
async def show_profile_with_image(user_id: int, target_message: types.Message):
    username = (await get_active_bot().get_chat(user_id)).username or "не указан"
    user_data = await fetchone("SELECT total, created_at FROM users WHERE id = ?", (user_id,))
    total_bought = user_data[0] if user_data else 0
    created_at = user_data[1] if user_data else None
    balance = await get_balance(user_id)
    review_count = await fetchone("SELECT COUNT(*) FROM reviews WHERE user_id = ?", (user_id,))
    registration_text = "дата не указана"
    if created_at:
        try:
            registered_date = datetime.fromisoformat(created_at)
            months = (
                "января", "февраля", "марта", "апреля", "мая", "июня",
                "июля", "августа", "сентября", "октября", "ноября", "декабря"
            )
            registration_text = (
                f"{registered_date.day} {months[registered_date.month - 1]} "
                f"{registered_date.year} года"
            )
        except ValueError:
            registration_text = created_at[:10]
    text = (
        "<b>"
        f'<blockquote><tg-emoji emoji-id="{CustomEmoji.PROFILE_EMOJI}">🎥</tg-emoji> <b>Профиль</b>\n'
        f'<tg-emoji emoji-id="{CustomEmoji.SHIELD}">🛡</tg-emoji> ID: {user_id}\n'
        f'<tg-emoji emoji-id="{CustomEmoji.CHECK}">✅</tg-emoji> Username: @{username}</blockquote>\n'
        f'<blockquote><tg-emoji emoji-id="{CustomEmoji.LOCK}">🔒</tg-emoji> Баланс: {balance:.2f} USDT\n'
        f'<tg-emoji emoji-id="{CustomEmoji.UP}">🔼</tg-emoji> Покупок: {total_bought}</blockquote>\n'
        f'<blockquote><tg-emoji emoji-id="{CustomEmoji.RATING}">⭐</tg-emoji> Оставлено отзывов: {review_count[0] if review_count else 0}</blockquote>\n'
        f'<blockquote><tg-emoji emoji-id="{CustomEmoji.REGISTRATION}">📅</tg-emoji> Зарегистрирован {registration_text}.</blockquote>'
        "</b>"
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="История покупок", callback_data="profile_history", icon_custom_emoji_id=CustomEmoji.PURCHASE_HISTORY, style='primary')
    kb.button(text="Оставить отзыв", callback_data="profile_reviews", icon_custom_emoji_id=CustomEmoji.REVIEW, style='primary')
    kb.button(text="Реферальная ссылка", callback_data="profile_referral", icon_custom_emoji_id=CustomEmoji.REFERRAL, style='primary')
    kb.button(text="Активировать промокод", callback_data="profile_promo", icon_custom_emoji_id=CustomEmoji.PROMO_CODE, style='primary')
    kb.button(text="Создать свое зеркало", callback_data="profile_mirror", icon_custom_emoji_id=CustomEmoji.CREATE_MIRROR, style='primary')
    kb.button(text="Вывод с реф. баланса", callback_data="profile_withdraw", icon_custom_emoji_id=CustomEmoji.REF_WITHDRAW, style='primary')
    kb.adjust(1)
    await send_with_image(target_message, 'EleghantProfile', text, kb.as_markup())

@dp.callback_query(F.data == "profile_reviews")
async def profile_reviews_cb(call: types.CallbackQuery):
    cats = await fetchall(
        "SELECT DISTINCT h.cat_id, c.name FROM history h JOIN categories c ON c.id = h.cat_id "
        "WHERE h.user_id = ? AND h.cat_id IS NOT NULL ORDER BY h.id DESC", (call.from_user.id,)
    )
    kb = InlineKeyboardBuilder()
    for cat_id, name in cats:
        kb.button(text=name, callback_data=f"review_cat_{cat_id}")
    kb.button(text="Назад к профилю", callback_data="back_to_profile", style='danger')
    kb.adjust(1)
    await call.message.edit_text(
        '<tg-emoji emoji-id="5213085536989780516">⭐️</tg-emoji> <b>Отзывы о покупках</b>\n\n'
        '<blockquote><b>Выберите приобретенный лот:</b></blockquote>',
        parse_mode="HTML", reply_markup=kb.as_markup()
    )
    await call.answer()

@dp.callback_query(F.data.startswith("review_cat_"))
async def review_cat_cb(call: types.CallbackQuery, state: FSMContext):
    try:
        cat_id = int(call.data.rsplit("_", 1)[1])
    except ValueError:
        await call.answer("❌ Некорректный лот", show_alert=True)
        return
    purchased = await fetchone(
        "SELECT 1 FROM history WHERE user_id = ? AND cat_id = ? LIMIT 1",
        (call.from_user.id, cat_id)
    )
    cat = await fetchone("SELECT name FROM categories WHERE id = ?", (cat_id,))
    if not purchased or not cat:
        await call.answer("❌ Отзыв доступен только после покупки.", show_alert=True)
        return
    await state.update_data(review_cat_id=cat_id, review_cat_name=cat[0])
    await state.set_state(ShopState.waiting_for_review_rating)
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад к отзывам", callback_data="back_to_reviews", icon_custom_emoji_id=CustomEmoji.BACK, style="danger")
    await call.message.answer(f"Оцените «{cat[0]}» от 1 до 5:", reply_markup=kb.as_markup())
    await call.answer()

@dp.message(ShopState.waiting_for_review_rating)
async def review_rating_msg(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit() or not 1 <= int(message.text) <= 5:
        await message.answer("❌ Укажите целое число от 1 до 5.")
        return
    await state.update_data(review_rating=int(message.text))
    await state.set_state(ShopState.waiting_for_review_text)
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад к отзывам", callback_data="back_to_reviews", icon_custom_emoji_id=CustomEmoji.BACK, style="danger")
    await message.answer(
        "Напишите отзыв одним сообщением (или отправьте «-», чтобы оставить только оценку):",
        reply_markup=kb.as_markup()
    )

@dp.message(ShopState.waiting_for_review_text)
async def review_text_msg(message: types.Message, state: FSMContext):
    data = await state.get_data()
    review_text = "" if message.text.strip() == "-" else message.text.strip()
    await execute_query(
        "INSERT INTO reviews (user_id, cat_id, rating, text, created_at) VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(user_id, cat_id) DO UPDATE SET rating=excluded.rating, text=excluded.text, created_at=excluded.created_at",
        (message.from_user.id, data["review_cat_id"], data["review_rating"], review_text,
         datetime.now(timezone.utc).isoformat()), commit=True
    )
    await state.clear()
    await message.answer("✅ Спасибо! Отзыв сохранен.", reply_markup=main_menu_back_keyboard("back_to_profile"))

async def _mirror_polling(mirror_bot: Bot):
    """Run one mirror on the same router as the main bot."""
    try:
        await dp._polling(
            bot=mirror_bot,
            polling_timeout=10,
            allowed_updates=dp.resolve_used_update_types(),
        )
    except asyncio.CancelledError:
        raise
    except Exception as error:
        # Do not include the token in diagnostics.
        logger.error("Mirror polling stopped for bot id %s: %s", mirror_bot.id, type(error).__name__)

async def _stop_mirror(user_id: int):
    task = mirror_polling_tasks.pop(user_id, None)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    old_bot = mirror_bots.pop(user_id, None)
    if old_bot:
        await old_bot.session.close()

async def _activate_mirror(user_id: int, mirror_bot: Bot):
    await _stop_mirror(user_id)
    mirror_bots[user_id] = mirror_bot
    mirror_polling_tasks[user_id] = asyncio.create_task(_mirror_polling(mirror_bot))

async def _load_saved_mirrors():
    for user_id, token in await fetchall("SELECT user_id, bot_token FROM user_mirrors"):
        mirror_bot = None
        try:
            mirror_bot = Bot(token=token)
            mirror_info = await asyncio.wait_for(mirror_bot.get_me(), timeout=15)
            if mirror_info.id == bot.id or any(
                owner_id != user_id and active_bot.id == mirror_info.id
                for owner_id, active_bot in mirror_bots.items()
            ):
                logger.warning("Saved mirror skipped because its bot is already in use")
                await mirror_bot.session.close()
                mirror_bot = None
                continue
            await mirror_bot.set_my_commands(BOT_COMMANDS)
            await mirror_bot.delete_webhook(drop_pending_updates=True)
            await _activate_mirror(user_id, mirror_bot)
            mirror_bot = None
        except asyncio.TimeoutError:
            logger.warning("Saved mirror validation timed out for user %s", user_id)
            if mirror_bot is not None:
                await mirror_bot.session.close()
        except Exception as error:
            logger.warning("Saved mirror could not be started for user %s: %s", user_id, type(error).__name__)
            if mirror_bot is not None:
                await mirror_bot.session.close()

@dp.callback_query(F.data == "profile_mirror")
async def profile_mirror_cb(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(ShopState.waiting_for_mirror_token)
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад к профилю", callback_data="back_to_profile", icon_custom_emoji_id=CustomEmoji.BACK, style="danger")
    await call.message.answer(
        '<b><tg-emoji emoji-id="5213464610803323563">🔗</tg-emoji> Создание зеркала</b>\n\n'
        "<blockquote>Создайте бота через @BotFather и отправьте сюда его токен. "
        "Токен нужен только для подключения зеркала, никому его не пересылайте.</blockquote>",
        parse_mode="HTML", reply_markup=kb.as_markup()
    )
    await call.answer()

@dp.message(ShopState.waiting_for_mirror_token)
async def mirror_token_msg(message: types.Message, state: FSMContext):
    token = (message.text or "").strip()
    if len(token) < 20 or ":" not in token:
        await message.answer("❌ Похоже, это не токен Telegram-бота. Отправьте токен из @BotFather.")
        return
    mirror_bot = None
    mirror_ready = False
    try:
        mirror_bot = Bot(token=token)
        mirror_info = await asyncio.wait_for(mirror_bot.get_me(), timeout=15)
        if mirror_info.id == bot.id:
            await message.answer("❌ Нельзя подключить токен основного бота в качестве зеркала.")
            return
        if any(
            owner_id != message.from_user.id and active_bot.id == mirror_info.id
            for owner_id, active_bot in mirror_bots.items()
        ):
            await message.answer("❌ Этот бот уже подключен как зеркало другого пользователя.")
            return
        await mirror_bot.set_my_commands(BOT_COMMANDS)
        await mirror_bot.delete_webhook(drop_pending_updates=True)
        mirror_ready = True
    except asyncio.TimeoutError:
        logger.warning("Mirror bot validation timed out for user %s", message.from_user.id)
        await message.answer("❌ Telegram не ответил за 15 секунд. Попробуйте ещё раз.")
        return
    except Exception as error:
        logger.warning("Mirror bot validation failed for user %s: %s", message.from_user.id, type(error).__name__)
        await message.answer("❌ Токен недействителен или бот недоступен.")
        return
    finally:
        if mirror_bot is not None and not mirror_ready:
            await mirror_bot.session.close()
    now = datetime.now(timezone.utc).isoformat()
    mirror_username = mirror_info.username or str(mirror_info.id)
    try:
        await execute_query(
            "INSERT INTO user_mirrors (user_id, bot_token, bot_username, created_at, updated_at) VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET bot_token=excluded.bot_token, bot_username=excluded.bot_username, updated_at=excluded.updated_at",
            (message.from_user.id, token, mirror_username, now, now), commit=True
        )
        await _activate_mirror(message.from_user.id, mirror_bot)
    except Exception:
        await mirror_bot.session.close()
        raise
    mirror_bot = None
    await state.clear()
    await message.answer(
        f"✅ Зеркало @{mirror_username} подключено. При необходимости повторно отправьте новый токен для замены."
    )

# ═══════════════════════════════════════════════════════════════════════════════
# ВЫВОД СРЕДСТВ
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "profile_withdraw")
async def profile_withdraw_cb(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    balance = await get_balance(user_id)
    await state.set_state(ShopState.waiting_for_withdraw_amount)
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад к профилю", callback_data="back_to_profile", icon_custom_emoji_id=CustomEmoji.BACK, style="danger")
    kb.adjust(1)
    await call.message.answer(
        '<b><tg-emoji emoji-id="4924714844256470686">❓</tg-emoji> Вывод средств с реферального баланса</b>\n\n'
        '<blockquote><b><tg-emoji emoji-id="4924694584895735802">❓</tg-emoji> '
        'Производим выводы на такие сервисы как: @xRocket; По адресу кошелька.</b></blockquote>\n\n'
        f'<blockquote><b><tg-emoji emoji-id="4927470722906850798">🔒</tg-emoji> Ваш баланс: {balance} USDT</b></blockquote>\n\n'
        '<b><tg-emoji emoji-id="5213067717170466441">❓</tg-emoji> '
        'Введите сумму для вывода (минимальная сумма для вывода 1$):</b>',
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await call.answer()

@dp.message(ShopState.waiting_for_withdraw_amount)
async def withdraw_amount_msg(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    balance = await get_balance(user_id)
    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError
        amount = round(amount, 2)
    except (ValueError, AttributeError):
        await message.answer(
            f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❗️</tg-emoji> Введите корректную сумму (например: 10 или 5.50)',
            parse_mode="HTML"
        )
        return
    if amount < 1:
        await message.answer(
            f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❗️</tg-emoji> Минимальная сумма вывода — <b>1 USDT</b>.',
            parse_mode="HTML"
        )
        return
    if amount > balance:
        await message.answer(
            f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> <b>Недостаточно средств!</b>\n\n'
            f'Ваш баланс: <b>{balance} USDT</b>\n'
            f'Запрошено: <b>{amount} USDT</b>\n\n'
            f'Пожалуйста, введите сумму не превышающую баланс.',
            parse_mode="HTML"
        )
        return
    await state.update_data(withdraw_amount=amount)
    await state.set_state(ShopState.waiting_for_withdraw_confirm)
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Да, вывести", callback_data="confirm_withdraw")
    kb.button(text="Назад к профилю", callback_data="back_to_profile", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    kb.adjust(2)
    await message.answer(
        f'<tg-emoji emoji-id="{CustomEmoji.QUESTION}">❓</tg-emoji> <b>Подтверждение вывода</b>\n\n'
        f'Вы уверены, что хотите вывести <b>{amount} USDT</b>?\n\n'
        f'После подтверждения заявка будет отправлена администратору.',
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data == "confirm_withdraw", ShopState.waiting_for_withdraw_confirm)
async def confirm_withdraw_cb(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    data = await state.get_data()
    amount = data.get('withdraw_amount', 0)
    balance = await get_balance(user_id)
    if amount > balance:
        await call.message.edit_text(
            f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Недостаточно средств на балансе. '
            f'Текущий баланс: {balance} USDT.',
            parse_mode="HTML"
        )
        await state.clear()
        await call.answer()
        return
    username = call.from_user.username or ""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    await execute_query(
        "INSERT INTO withdraw_requests (user_id, username, amount, status, created_at) VALUES (?, ?, ?, 'pending', ?)",
        (user_id, username, amount, now_str),
        commit=True
    )
    request_row = await fetchone(
        "SELECT id FROM withdraw_requests WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user_id,)
    )
    request_id = request_row[0] if request_row else "?"
    await call.message.edit_text(
        f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CHECK}">✅</tg-emoji> <b>Заявка создана!</b>\n\n'
        f'Администрация рассмотрит её в ближайшее время.\n\n'
        f'<tg-emoji emoji-id="{CustomEmoji.MONEY}">💰</tg-emoji> Сумма вывода: <b>{amount} USDT</b>\n'
        f'<tg-emoji emoji-id="{CustomEmoji.TIME}">⏳</tg-emoji> Номер заявки: <b>#{request_id}</b>',
        parse_mode="HTML"
    )
    user_link = f"@{username}" if username else f"<a href='tg://user?id={user_id}'>ID: {user_id}</a>"
    admin_text = (
        f'💸 <b>Новая заявка на вывод #{request_id}</b>\n\n'
        f'👤 Пользователь: {user_link}\n'
        f'🆔 ID: <code>{user_id}</code>\n'
        f'💰 Сумма: <b>{amount} USDT</b>\n'
        f'📅 Дата: {now_str[:16]}'
    )
    admin_kb = InlineKeyboardBuilder()
    admin_kb.button(text="✅ Одобрить", callback_data=f"withdraw_approve_{request_id}")
    admin_kb.button(text="❌ Отклонить", callback_data=f"withdraw_reject_{request_id}")
    admin_kb.adjust(2)
    try:
        await get_active_bot().send_message(ADMIN_ID, admin_text, parse_mode="HTML", reply_markup=admin_kb.as_markup())
    except Exception as e:
        logger.error(f"Не удалось уведомить администратора о заявке #{request_id}: {e}")
    await state.clear()
    await call.answer()

@dp.callback_query(F.data == "cancel_withdraw")
async def cancel_withdraw_cb(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Вывод средств отменён.',
        parse_mode="HTML"
    )
    await call.answer()

@dp.callback_query(F.data.startswith("withdraw_approve_"))
async def withdraw_approve_cb(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    try:
        request_id = int(call.data.split("_")[2])
    except (IndexError, ValueError):
        await call.answer("❌ Ошибка", show_alert=True)
        return
    request = await fetchone(
        "SELECT user_id, username, amount, status FROM withdraw_requests WHERE id = ?",
        (request_id,)
    )
    if not request:
        await call.message.edit_text(f"❌ Заявка #{request_id} не найдена.")
        await call.answer()
        return
    user_id, username, amount, status = request
    if status != 'pending':
        await call.answer(f"⚠️ Заявка уже обработана (статус: {status})", show_alert=True)
        return
    balance = await get_balance(user_id)
    if balance < amount:
        await call.message.edit_text(
            f"❌ У пользователя недостаточно средств!\n"
            f"Баланс: {balance} USDT, заявка: {amount} USDT\n\n"
            f"Заявка #{request_id} отклонена автоматически."
        )
        await execute_query(
            "UPDATE withdraw_requests SET status = 'rejected', processed_at = ?, admin_note = ? WHERE id = ?",
            (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), "Недостаточно средств", request_id),
            commit=True
        )
        await call.answer()
        return
    await update_balance(user_id, -amount, "withdraw", ADMIN_ID)
    await execute_query(
        "UPDATE withdraw_requests SET status = 'approved', processed_at = ? WHERE id = ?",
        (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), request_id),
        commit=True
    )
    user_link = f"@{username}" if username else f"ID: {user_id}"
    await call.message.edit_text(
        f'✅ <b>Заявка #{request_id} одобрена</b>\n\n'
        f'👤 Пользователь: {user_link}\n'
        f'💰 Сумма: {amount} USDT\n'
        f'💳 Баланс списан.',
        parse_mode="HTML"
    )
    try:
        await get_active_bot().send_message(
            user_id,
            f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CHECK}">✅</tg-emoji> <b>Ваша заявка на вывод одобрена!</b>\n\n'
            f'<tg-emoji emoji-id="{CustomEmoji.MONEY}">💰</tg-emoji> Сумма: <b>{amount} USDT</b>\n\n'
            f'Средства будут переведены вам в ближайшее время. По вопросам обращайтесь в поддержку.',
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Не удалось уведомить пользователя {user_id} об одобрении заявки: {e}")
    await call.answer("✅ Заявка одобрена, баланс списан!")
    logger.info(f"Admin {call.from_user.id} approved withdraw #{request_id} for user {user_id}, amount {amount} USDT")

@dp.callback_query(F.data.startswith("withdraw_reject_"))
async def withdraw_reject_cb(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        await call.answer("❌ Нет доступа", show_alert=True)
        return
    try:
        request_id = int(call.data.split("_")[2])
    except (IndexError, ValueError):
        await call.answer("❌ Ошибка", show_alert=True)
        return
    request = await fetchone(
        "SELECT user_id, username, amount, status FROM withdraw_requests WHERE id = ?",
        (request_id,)
    )
    if not request:
        await call.message.edit_text(f"❌ Заявка #{request_id} не найдена.")
        await call.answer()
        return
    user_id, username, amount, status = request
    if status != 'pending':
        await call.answer(f"⚠️ Заявка уже обработана (статус: {status})", show_alert=True)
        return
    await state.update_data(reject_request_id=request_id, reject_user_id=user_id,
                            reject_username=username, reject_amount=amount)
    await state.set_state(AdminState.withdraw_reject_reason)
    kb = InlineKeyboardBuilder()
    kb.button(text="Пропустить причину", callback_data=f"withdraw_reject_noreason_{request_id}")
    kb.adjust(1)
    await call.message.answer(
        f'❌ <b>Отклонение заявки #{request_id}</b>\n\n'
        f'Введите причину отклонения (или нажмите кнопку, чтобы пропустить):',
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await call.answer()

@dp.message(AdminState.withdraw_reject_reason)
async def withdraw_reject_reason_msg(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    request_id = data['reject_request_id']
    user_id = data['reject_user_id']
    username = data['reject_username']
    amount = data['reject_amount']
    reason = message.text.strip()
    await _do_reject_withdraw(request_id, user_id, username, amount, reason, state, message)

@dp.callback_query(F.data.startswith("withdraw_reject_noreason_"))
async def withdraw_reject_noreason_cb(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    request_id = data.get('reject_request_id')
    user_id = data.get('reject_user_id')
    username = data.get('reject_username', '')
    amount = data.get('reject_amount', 0)
    await _do_reject_withdraw(request_id, user_id, username, amount, None, state, call.message)
    await call.answer()

async def _do_reject_withdraw(request_id, user_id, username, amount, reason, state, message_obj):
    note = reason if reason else "Без причины"
    await execute_query(
        "UPDATE withdraw_requests SET status = 'rejected', processed_at = ?, admin_note = ? WHERE id = ?",
        (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), note, request_id),
        commit=True
    )
    user_link = f"@{username}" if username else f"ID: {user_id}"
    await message_obj.answer(
        f'❌ <b>Заявка #{request_id} отклонена</b>\n\n'
        f'👤 Пользователь: {user_link}\n'
        f'💰 Сумма: {amount} USDT\n'
        f'📝 Причина: {note}',
        parse_mode="HTML"
    )
    reason_text = f'\n📝 Причина: {reason}' if reason else ''
    try:
        await get_active_bot().send_message(
            user_id,
            f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> <b>Ваша заявка на вывод отклонена.</b>\n\n'
            f'<tg-emoji emoji-id="{CustomEmoji.MONEY}">💰</tg-emoji> Сумма: <b>{amount} USDT</b>'
            f'{reason_text}\n\n'
            f'Ваш баланс не изменился. По вопросам обращайтесь в поддержку.',
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Не удалось уведомить пользователя {user_id} об отклонении заявки: {e}")
    logger.info(f"Withdraw #{request_id} rejected for user {user_id}, reason: {note}")
    await state.clear()

@dp.message(Command("withdraws"))
async def cmd_withdraws(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    requests = await fetchall(
        "SELECT id, user_id, username, amount, status, created_at FROM withdraw_requests "
        "WHERE status = 'pending' ORDER BY created_at ASC"
    )
    if not requests:
        await message.answer("📭 Нет активных заявок на вывод.")
        return
    text = f'💸 <b>Активные заявки на вывод ({len(requests)}):</b>\n\n'
    for rid, uid, uname, amount, status, created in requests:
        u = f"@{uname}" if uname else f"ID:{uid}"
        text += f"#{rid} | {u} | {amount} USDT | {created[:16]}\n"
    await message.answer(text, parse_mode="HTML")

# --- ПРЕДЗАКАЗЫ ПРОФИЛЬ ---
@dp.callback_query(F.data == "profile_preorders")
async def profile_preorders_cb(call: types.CallbackQuery):
    preorders = await fetchall(
        "SELECT id, cat_id, quantity, total, created_at, paid_at, status FROM preorders WHERE user_id = ? ORDER BY created_at DESC",
        (call.from_user.id,)
    )
    if not preorders:
        await call.message.edit_text(f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_BOX}">📦</tg-emoji> У вас нет предзаказов.', parse_mode="HTML")
        return
    text = f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CLOCK}">🕞</tg-emoji> <b>Ваши предзаказы:</b>\n\n'
    for pid, cat_id, qty, total, created, paid_at, status in preorders:
        cat = await fetchone("SELECT name FROM categories WHERE id = ?", (cat_id,))
        cat_name = cat[0] if cat else "Неизвестно"
        status_map = {
            "pending": (f'<tg-emoji emoji-id="{CustomEmoji.TIME}">⏳</tg-emoji>', "Ожидает оплаты"),
            "paid": (f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CHECK}">✅</tg-emoji>', "Оплачен, ожидает выдачи"),
            "expired": (f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji>', "Просрочен"),
            "completed": (f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_COMPLETED}">🎁</tg-emoji>', "Выполнен"),
        }
        status_emoji, status_text = status_map.get(status, ("❓", "Неизвестно"))
        text += f"{status_emoji} <b>#{pid}</b> - {cat_name}\n"
        text += f'   📦 {qty} шт. | 💰 {total} USDT\n'
        text += f'   📅 Создан: {created[:10] if created else "Неизвестно"}\n'
        if paid_at:
            text += f'   💳 Оплачен: {paid_at[:10]}\n'
        text += f"   {status_emoji} Статус: {status_text}\n\n"
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад к профилю", callback_data="back_to_profile", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await call.answer()

# Вспомогательная функция – без декоратора
async def show_history(message: types.Message, user_id: int, period: str):
    now = datetime.now(timezone.utc)
    filter_condition = ""
    params = [user_id]
    limit = 20

    if period == "yesterday":
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=0, minute=0, second=0, microsecond=0)
        filter_condition = "AND created_at >= ? AND created_at < ?"
        params.extend([start.isoformat(), end.isoformat()])
    elif period == "week":
        week_ago = now - timedelta(days=7)
        filter_condition = "AND created_at >= ?"
        params.append(week_ago.isoformat())
    elif period == "month":
        month_ago = now - timedelta(days=30)
        filter_condition = "AND created_at >= ?"
        params.append(month_ago.isoformat())

    if period == "all":
        sql = "SELECT id, cat_id, item_data, date, created_at FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?"
        params.append(limit)
    else:
        sql = f"SELECT id, cat_id, item_data, date, created_at FROM history WHERE user_id = ? {filter_condition} ORDER BY id DESC LIMIT ?"
        params.append(limit)

    history = await fetchall(sql, tuple(params))

    if not history:
        text = f'<b><tg-emoji emoji-id="{CustomEmoji.EMPTY_HISTORY}">✏️</tg-emoji> Нет покупок за выбранный период.</b>'
    else:
        period_names = {
            "all": "все время",
            "yesterday": "вчера",
            "week": "последнюю неделю",
            "month": "последний месяц"
        }
        period_name = period_names.get(period, "все время")
        text = f'<b><tg-emoji emoji-id="5215633599352572357">✏️</tg-emoji> История покупок (за {period_name}, последние {len(history)} записей):\n\n'
        for hid, cat_id, item, date, created_at in history:
            short_item = item[:40] + "..." if len(item) > 40 else item
            # Форматируем дату
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at)
                    display_date = dt.strftime("%d.%m %H:%M")
                except:
                    display_date = created_at[:16]  # fallback
            else:
                display_date = date  # старый формат (уже "дд.мм ЧЧ:ММ")
            text += f"• {display_date}: {hcode(short_item)}\n"
        text += "</b>"

    kb = InlineKeyboardBuilder()
    kb.button(text="Все", callback_data="history_period_all", style='primary')
    kb.button(text="Вчера", callback_data="history_period_yesterday", style='primary')
    kb.button(text="Неделя", callback_data="history_period_week", style='primary')
    kb.button(text="Месяц", callback_data="history_period_month", style='primary')
    kb.button(text="Назад к профилю", callback_data="back_to_profile", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    kb.adjust(2, 2, 1)

    try:
        await message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    except Exception:
        await message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")


# Обработчик для кнопки "История покупок" – с правильным декоратором
@dp.callback_query(F.data == "profile_history")
async def profile_history_cb(call: types.CallbackQuery):
    await show_history(call.message, call.from_user.id, "all")
    await call.answer()

@dp.callback_query(F.data.startswith("history_period_"))
async def history_period_cb(call: types.CallbackQuery):
    period = call.data.split("_")[2]  # all, yesterday, week, month
    await show_history(call.message, call.from_user.id, period)
    await call.answer()

@dp.callback_query(F.data == "profile_referral")
async def profile_referral_cb(call: types.CallbackQuery):
    user_id = call.from_user.id
    ref_count, ref_earn = await get_referral_info(user_id)
    bot_info = await get_active_bot().get_me()
    
    bot_username = bot_info.username.replace("@", "")
    link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    share_text = "Заходи в крутого бота по моей ссылке! Нам обоим дадут бонусы 🎁"
    
    text = (
        f'<tg-emoji emoji-id="{CustomEmoji.REFERRAL_LINK}">🔗</tg-emoji> <b>Ваша реферальная ссылка:</b>\n<code>{link}</code>\n\n'
        f'<blockquote><b><tg-emoji emoji-id="{CustomEmoji.REFERRAL_USER}">👤</tg-emoji> Рефералов: {ref_count}\n'
        f'<tg-emoji emoji-id="{CustomEmoji.REFERRAL_EARNINGS}">➕</tg-emoji> Заработано: {ref_earn} USDT</b></blockquote>\n\n'
        "<b>За каждого приведённого пользователя, совершившего покупку, вы получаете 10% от суммы его покупки. "
        "К примеру: Пользователь купил товар на 100$ - Вам на баланс 10$.</b>"
    )
    
    kb = InlineKeyboardBuilder()
    
    # ПРАВИЛЬНЫЙ способ: кнопка с share URL
    share_url = f"https://t.me/share/url?url={quote(link)}&text={quote(share_text)}"
    kb.button(text="Поделиться ссылкой", url=share_url, icon_custom_emoji_id=CustomEmoji.SHARE, style='primary')
    
    kb.button(text="Назад к профилю", callback_data="back_to_profile", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    kb.adjust(1, 1)
    
    try:
        await call.message.delete()
    except Exception:
        pass
        
    await send_with_image(call.message, 'ReferalIcon', text, kb.as_markup())
    await call.answer()



@dp.callback_query(F.data == "profile_promo")
async def profile_promo_cb(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(ShopState.waiting_for_promo_code)
    await call.message.answer(
        f'<b><tg-emoji emoji-id="{CustomEmoji.PROMO_CODE}">🎫</tg-emoji> Введите промокод:</b>\n\n'
        '<blockquote><b>Важно, один промокод можно активировать не более раза на один аккаунт.</b></blockquote>',
        parse_mode="HTML",
        reply_markup=main_menu_back_keyboard("back_to_profile"),
    )
    await call.answer()

@dp.message(ShopState.waiting_for_promo_code)
async def promo_code_activate(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    code = message.text.strip().upper()
    current_time = time.time()
    if user_id in user_promo_attempts:
        attempts, last_attempt = user_promo_attempts[user_id]
        if attempts >= MAX_PROMO_ATTEMPTS and current_time - last_attempt < PROMO_BLOCK_TIME:
            await message.answer(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Слишком много попыток. Попробуйте через {int(PROMO_BLOCK_TIME - (current_time - last_attempt))} сек.', parse_mode="HTML")
            await state.clear()
            return
    promo = await fetchone("SELECT amount, max_uses, used, promo_type FROM promo_codes WHERE code = ?", (code,))
    if not promo:
        user_promo_attempts[user_id] = (user_promo_attempts.get(user_id, (0, current_time))[0] + 1, current_time)
        await message.answer(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Промокод не найден.', parse_mode="HTML")
        await state.clear()
        return
    amount, max_uses, used, promo_type = promo
    already_used = await fetchone(
        "SELECT 1 FROM promo_usage WHERE code = ? AND user_id = ? LIMIT 1",
        (code, user_id)
    )
    if already_used:
        await message.answer(
            f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> '
            'Вы уже активировали этот промокод.',
            parse_mode="HTML"
        )
        await state.clear()
        return
    if used >= max_uses:
        await message.answer(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Промокод уже использован максимальное количество раз.', parse_mode="HTML")
        await state.clear()
        return
    if user_id in user_promo_attempts:
        del user_promo_attempts[user_id]

    # Записываем использование промокода
    await execute_query(
        "INSERT INTO promo_usage (code, user_id, username, used_at) VALUES (?, ?, ?, ?)",
        (code, user_id, username, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")),
        commit=True
    )

    if promo_type == 'percent':
        await message.answer(
            f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CHECK}">✅</tg-emoji> Промокод {code} активирован!\n'
            f'Скидка: {amount}% на следующую покупку!',
            parse_mode="HTML"
        )
        if not hasattr(get_active_bot(), 'user_promos'):
            get_active_bot().user_promos = {}
        get_active_bot().user_promos[user_id] = {'code': code, 'discount': amount, 'type': 'percent'}
        await execute_query("UPDATE promo_codes SET used = used + 1 WHERE code = ?", (code,), commit=True)
    else:
        await update_balance(message.from_user.id, amount, "promo")
        await execute_query("UPDATE promo_codes SET used = used + 1 WHERE code = ?", (code,), commit=True)
        await message.answer(f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CHECK}">✅</tg-emoji> Промокод активирован! Зачислено {amount} USDT.', parse_mode="HTML")
    await state.clear()

# --- ПОПОЛНЕНИЕ БАЛАНСА ---
@dp.callback_query(F.data.in_({"deposit_provider_xrocket", "deposit_provider_stars"}))
async def deposit_provider_cb(call: types.CallbackQuery, state: FSMContext):
    provider = "xrocket" if call.data == "deposit_provider_xrocket" else "stars"
    provider_name = {"xrocket": "@xRocket", "stars": "Telegram Stars"}[provider]
    await state.update_data(deposit_provider=provider)
    await state.set_state(ShopState.waiting_for_deposit_amount)
    stars_hint = (
        f'\nДля Stars сумма будет пересчитана по курсу {STAR_USDT_RATE:g} Stars = 1 USDT:'
        if provider == "stars" else ""
    )
    await call.message.answer(
        f'<b><tg-emoji emoji-id="4924714844256470686">💰</tg-emoji> Оплата через {provider_name}</b>\n\n'
        f'<blockquote><b>Введите сумму пополнения в USDT (минимум 1 USDT).</b></blockquote>'
        f'{stars_hint}',
        parse_mode="HTML",
        reply_markup=main_menu_back_keyboard("back_to_deposit")
    )
    await call.answer()

@dp.message(ShopState.waiting_for_deposit_amount)
async def deposit_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        if amount < 1 or amount > 10000:
            return await message.answer("❌ Сумма должна быть от 1 до 10000 USDT.")
        amount = round(amount, 2)
    except Exception:
        return await message.answer("❌ Введите число.")
    data = await state.get_data()
    provider = data.get('deposit_provider')
    if provider not in {"xrocket", "stars"}:
        await message.answer("❌ Способ оплаты не выбран. Откройте пополнение баланса заново.")
        await state.clear()
    if provider == "stars":
        stars = max(1, int(round(amount * STAR_USDT_RATE)))
        await message.answer_invoice(
            title="Пополнение ALTERA",
            description=f"Пополнение баланса на {amount:.2f} USDT",
            payload=json.dumps({"type": "deposit", "amount": amount}, separators=(",", ":")),
            currency="XTR",
            prices=[LabeledPrice(label=f"{amount:.2f} USDT", amount=stars)],
        )
        await state.clear()
        return
    if provider == "xrocket":
        inv = await xrocket_create_invoice(
            amount=amount,
            description=f"Пополнение баланса пользователя {message.from_user.id}",
            expired_in=1800
        )
        if not inv.get('ok'):
            await message.answer(f"⚠ Ошибка API xRocket: {inv.get('description', 'Неизвестная ошибка')}")
            await state.clear()
            return
        invoice_id = inv['id']
        pay_url = inv['link']
        provider_emoji = CustomEmoji.XROCKET_PAY
    pending_balance_payments[invoice_id] = {
        'user_id': message.from_user.id, 'amount': amount,
        'created_at': datetime.now(), 'provider': provider
    }
    kb = InlineKeyboardBuilder()
    kb.button(text="Оплатить", url=pay_url, icon_custom_emoji_id=provider_emoji, style='success')
    kb.button(text="Проверить оплату", callback_data=f"check_balance_payment_{invoice_id}", style='primary', icon_custom_emoji_id=CustomEmoji.CHECKPAY)
    kb.button(text="Отменить пополнение", callback_data=f"cancel_balance_payment_{invoice_id}", icon_custom_emoji_id="5215248628548931525", style='danger')
    kb.adjust(1)
    msg = await message.answer(
        f'<b><tg-emoji emoji-id="4924714844256470686">❓</tg-emoji> Пополнение баланса</b>\n\n'
        f'<blockquote><b><tg-emoji emoji-id="4927470722906850798">💵</tg-emoji> Сумма: {amount} USDT</b></blockquote>\n\n'
        f'<blockquote><b><tg-emoji emoji-id="5213216202779824232">❓</tg-emoji> '
        'Нажмите кнопку ниже для оплаты, далее после оплаты счета нажмите "Проверить оплату" '
        'и средства поступят на баланс:</b></blockquote>',
        reply_markup=kb.as_markup(), parse_mode="HTML"
    )
    pending_balance_payments[invoice_id]['msg'] = msg
    asyncio.create_task(check_deposit_payment(invoice_id, message.from_user.id, amount, msg, provider))
    await state.clear()

@dp.message(Command("invoice"))
async def cmd_create_invoice(message: types.Message):
    args = message.text.split() if message.text else []
    amount = parse_check_amount(args[1]) if len(args) >= 2 else None
    if amount is None or amount < 1 or amount > 10000:
        await message.answer("Использование: /invoice 25 [назначение]\nСумма: от 1 до 10000 USDT.")
        return
    description = " ".join(args[2:]).strip() or f"Пополнение ALTERA пользователем {message.from_user.id}"
    inv = await xrocket_create_invoice(amount, description, expired_in=1800)
    if not inv.get("ok"):
        await message.answer(
            f"❌ Не удалось создать счёт: {html.escape(inv.get('description', 'ошибка API'))}",
            parse_mode="HTML",
        )
        return
    invoice_id = inv["id"]
    pay_url = inv["link"]
    pending_balance_payments[invoice_id] = {
        "user_id": message.from_user.id,
        "amount": amount,
        "created_at": datetime.now(),
        "provider": "xrocket",
    }
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Оплатить счёт",
        url=pay_url,
        icon_custom_emoji_id=CustomEmoji.XROCKET_PAY,
        style="success",
    )
    kb.button(
        text="Проверить оплату",
        callback_data=f"check_balance_payment_{invoice_id}",
        icon_custom_emoji_id=CustomEmoji.CHECKPAY,
        style="primary",
    )
    kb.adjust(1)
    msg = await message.answer(
        f"<b>💳 Счёт ALTERA на {amount:.2f} USDT</b>\n\n"
        f"<blockquote>{html.escape(description)}</blockquote>\n\n"
        "После оплаты нажмите «Проверить оплату».",
        parse_mode="HTML",
        reply_markup=kb.as_markup(),
    )
    pending_balance_payments[invoice_id]["msg"] = msg
    asyncio.create_task(check_deposit_payment(invoice_id, message.from_user.id, amount, msg))

@dp.message(Command("webapp"))
async def cmd_open_webapp(message: types.Message):
    if not WEB_APP_URL:
        await message.answer(
            "Web App ещё не настроен. Укажите переменную ALTERA_WEB_APP_URL с HTTPS-адресом."
        )
        return
    kb = InlineKeyboardBuilder()
    kb.button(text="Открыть каталог", web_app=WebAppInfo(url=WEB_APP_URL), style="success")
    await message.answer("Откройте каталог ALTERA:", reply_markup=kb.as_markup())

async def webapp_catalog(request: web.Request) -> web.Response:
    rows = await fetchall(
        "SELECT c.id, c.name, c.desc, c.price, COUNT(i.id) "
        "FROM categories c LEFT JOIN inventory i ON i.cat_id = c.id "
        "WHERE c.maintenance = 0 GROUP BY c.id ORDER BY c.id"
    )
    response = web.json_response({
        "categories": [
            {
                "id": row[0],
                "name": row[1],
                "description": re.sub(
                    r"<tg-emoji\b[^>]*>.*?</tg-emoji>|<[^>]+>",
                    "",
                    html.unescape(row[2] or ""),
                    flags=re.IGNORECASE | re.DOTALL,
                ).strip(),
                "price": row[3] or 0,
                "stock": row[4],
            }
            for row in rows
        ]
    })
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

async def webapp_options(request: web.Request) -> web.Response:
    return web.Response(
        status=204,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    )

async def start_webapp_server() -> Optional[web.AppRunner]:
    if not WEB_APP_URL:
        return None
    app = web.Application()
    app.router.add_get("/api/catalog", webapp_catalog)
    app.router.add_options("/api/catalog", webapp_options)
    app.router.add_get(
        "/",
        lambda request: web.FileResponse(
            os.path.join(os.path.dirname(__file__), "webapp", "index.html")
        ),
    )
    app.router.add_static(
        "/", os.path.join(os.path.dirname(__file__), "webapp")
    )
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(
        runner,
        os.getenv("ALTERA_WEB_APP_HOST", "127.0.0.1"),
        int(os.getenv("PORT") or os.getenv("ALTERA_WEB_APP_PORT", "8080")),
    )
    await site.start()
    logger.info("Web App server started")
    return runner

@dp.message(F.web_app_data)
async def webapp_purchase(message: types.Message):
    try:
        payload = json.loads(message.web_app_data.data)
    except (TypeError, ValueError, json.JSONDecodeError):
        await message.answer("❌ Не удалось прочитать данные Web App.")
        return
    if payload.get("action") != "purchase":
        await message.answer("❌ Неизвестное действие Web App.")
        return
    try:
        cat_id = int(payload["cat_id"])
        quantity = int(payload["quantity"])
    except (KeyError, TypeError, ValueError):
        await message.answer("❌ Некорректные данные покупки.")
        return
    if quantity < 1 or quantity > MAX_QUANTITY_PER_PURCHASE:
        await message.answer("❌ Некорректное количество товара.")
        return
    category = await fetchone(
        "SELECT id, name, price FROM categories WHERE id = ? AND maintenance = 0",
        (cat_id,),
    )
    if not category:
        await message.answer("❌ Категория товара недоступна.")
        return
    cat_id, cat_name, price = category
    stock = await fetchone("SELECT COUNT(*) FROM inventory WHERE cat_id = ?", (cat_id,))
    if not stock or stock[0] < quantity:
        await message.answer("❌ Недостаточно товара в наличии.")
        return
    total = round(float(price) * quantity, 2)
    payment = payload.get("payment")
    if payment == "balance":
        items = await buy_items_with_transaction(cat_id, quantity, message.from_user.id, total)
        if not items:
            await message.answer("❌ Недостаточно средств или товар закончился.")
            return
        text = "✅ Покупка оплачена с баланса!\n\n🎁 Ваш товар:\n"
        text += "\n".join(f"• {hcode(item_data)}" for _, item_data in items)
        await message.answer(text, parse_mode="HTML", reply_markup=purchase_review_keyboard(cat_id).as_markup())
        return
    if payment != "xrocket":
        await message.answer("❌ Выберите способ оплаты: баланс или xRocket.")
        return
    inv = await xrocket_create_invoice(
        amount=total,
        description=f"{cat_name} x{quantity}",
        expired_in=1800,
    )
    if not inv.get("ok"):
        await message.answer(
            f"❌ Не удалось создать счёт: {html.escape(inv.get('description', 'ошибка API'))}",
            parse_mode="HTML",
        )
        return
    invoice_id = inv["id"]
    pending_payments[invoice_id] = {
        "user_id": message.from_user.id,
        "cat_id": cat_id,
        "quantity": quantity,
        "total": total,
        "created_at": datetime.now(),
        "is_preorder": False,
        "provider": "xrocket",
    }
    kb = InlineKeyboardBuilder()
    kb.button(text="Оплатить", url=inv["link"], icon_custom_emoji_id=CustomEmoji.XROCKET_PAY, style="success")
    kb.button(text="Проверить оплату", callback_data=f"check_payment_{invoice_id}", icon_custom_emoji_id=CustomEmoji.CHECKPAY, style="primary")
    kb.button(text="Отменить заказ", callback_data=f"cancel_payment_{invoice_id}", icon_custom_emoji_id="5215248628548931525", style="danger")
    kb.adjust(1)
    msg = await message.answer(
        f"💳 <b>{html.escape(cat_name)} × {quantity}</b>\n"
        f"Сумма: <b>{total:.2f} USDT</b>\n\n"
        "Счёт действителен 30 минут.",
        parse_mode="HTML",
        reply_markup=kb.as_markup(),
    )
    pending_payments[invoice_id]["msg"] = msg
    asyncio.create_task(auto_check_payment(invoice_id, message.from_user.id, cat_id, quantity, msg, total, "xrocket"))

@dp.pre_checkout_query()
async def stars_pre_checkout(query: types.PreCheckoutQuery):
    await query.answer(ok=True)

def purchase_review_keyboard(cat_id: int) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Оценить товар",
        callback_data=f"review_cat_{cat_id}",
        icon_custom_emoji_id=CustomEmoji.REVIEW,
        style="success",
    )
    return kb

@dp.message(F.successful_payment)
async def stars_successful_payment(message: types.Message):
    payment = message.successful_payment
    try:
        payload = json.loads(payment.invoice_payload)
    except (TypeError, ValueError):
        logger.error("Invalid Telegram Stars payload for user %s", message.from_user.id)
        await message.answer("❌ Не удалось обработать платёж. Обратитесь в поддержку.")
        return
    if payload.get("type") == "deposit":
        amount = round(float(payload["amount"]), 2)
        await update_balance(message.from_user.id, amount, "deposit_stars")
        await message.answer(f"✅ Баланс пополнен на {amount:.2f} USDT через Telegram Stars.")
        return
    if payload.get("type") != "purchase":
        await message.answer("❌ Неизвестный тип платежа.")
        return
    items = await buy_items_with_transaction(
        int(payload["cat_id"]), int(payload["quantity"]), message.from_user.id, float(payload["total"])
    )
    if not items:
        await message.answer("❌ Товар закончился во время оплаты. Обратитесь в поддержку.")
        return
    result = "✅ Оплата через Telegram Stars подтверждена!\n\n🎁 Ваш товар:\n"
    result += "\n".join(f"• {hcode(item_data)}" for _, item_data in items)
    await message.answer(
        result,
        parse_mode="HTML",
        reply_markup=purchase_review_keyboard(int(payload["cat_id"])).as_markup(),
    )

# --- КОМАНДЫ ---
@dp.message(CommandStart(deep_link=True))
async def cmd_start_deep(message: types.Message):
    args = message.text.split() if message.text else []
    if len(args) >= 2 and args[1].startswith("check_"):
        await handle_start(message, None)
        user_row = await fetchone(
            "SELECT accepted, privacy_accepted FROM users WHERE id = ?",
            (message.from_user.id,),
        )
        if user_row and user_row[0] and user_row[1] == 1:
            await claim_check_from_message(message, args[1][6:])
        else:
            await message.answer("После принятия соглашения откройте ссылку на чек ещё раз.")
        return
    ref_id = parse_referrer_id(message)
    await handle_start(message, ref_id)

@dp.message(Command("start"))
async def cmd_start_plain(message: types.Message):
    await handle_start(message, None)

async def handle_start(message: types.Message, referrer_id: int = None):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    existing = await fetchone("SELECT accepted FROM users WHERE id = ?", (user_id,))
    if not existing:
        await save_user(username, user_id, referrer_id)
    else:
        await execute_query("UPDATE users SET username = ? WHERE id = ?", (username, user_id), commit=True)
        await execute_query(
            "UPDATE users SET created_at = COALESCE(created_at, ?) WHERE id = ?",
            (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), user_id),
            commit=True
        )
    if not await faq_access_granted(user_id):
        await show_required_faq(message)
    else:
        user_row = await fetchone(
            "SELECT accepted, privacy_accepted FROM users WHERE id = ?",
            (user_id,)
        )
        if not user_row or not user_row[0]:
            await show_agreement(message)
        elif user_row[1] != 1:
            await show_privacy_policy(message)
        else:
            await send_welcome_message(message)
            await show_main_menu(message)

async def claim_check_from_message(message: types.Message, token: str):
    if not token or len(token) > 64:
        await message.answer("❌ Некорректная ссылка на чек.")
        return
    status, amount, creator_id, comment = await claim_balance_check(token, message.from_user.id)
    if status == "claimed":
        text = f"✅ Чек активирован. На ваш баланс зачислено {amount:.2f} USDT."
        if comment:
            text += f"\n\n💬 Комментарий: {html.escape(comment)}"
        await message.answer(text, parse_mode="HTML")
    elif status == "expired":
        await message.answer("⌛ Срок действия чека истёк. Средства возвращены создателю.")
    elif status == "already_claimed":
        await message.answer("ℹ️ Этот чек уже активирован.")
    elif status == "already_expired":
        await message.answer("ℹ️ Этот чек уже использован.")
    elif status == "wrong_recipient":
        await message.answer("❌ Этот чек предназначен для другого пользователя.")
    else:
        await message.answer("❌ Чек не найден или ссылка повреждена.")

@dp.message(Command("check"))
async def cmd_create_check(message: types.Message):
    args = message.text.split() if message.text else []
    spec = parse_check_spec(args[1:])
    if not spec:
        await message.answer(
            "Использование: /check 100 4 оплата услуги\n"
            "Для конкретного пользователя: /check 100 1 @username оплата услуги"
        )
        return
    total, claims, recipient, comment = spec
    recipient_data = await resolve_username(recipient) if recipient else None
    if recipient and not recipient_data:
        await message.answer("❌ Получатель ещё не запускал бота или username указан неверно.")
        return
    token = await create_balance_check(
        message.from_user.id, total, claims, comment, recipient,
        recipient_data[0] if recipient_data else None,
    )
    if not token:
        await message.answer("❌ Недостаточно средств на балансе.")
        return
    me = await get_active_bot().get_me()
    link = f"https://t.me/{me.username}?start=check_{token}"
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Активировать чек",
        url=link,
        icon_custom_emoji_id="4925136584275134324",
        style="success",
    )
    await message.answer(
        f'<blockquote><b><tg-emoji emoji-id="4924874531140535819">🎁</tg-emoji> '
        f'Чек ALTERA на {total:.2f} USDT'
        f'{" (" + str(claims) + " активации по " + f"{total / claims:.2f}" + " USDT)" if claims > 1 else ""}'
        f'{" — " + html.escape(comment) if comment else ""}</b></blockquote>\n\n'
        '<blockquote><b><tg-emoji emoji-id="5213354182899179724">💬</tg-emoji> '
        'Чтобы активировать данный чек, нажмите на кнопку ниже</b></blockquote>',
        parse_mode="HTML",
        reply_markup=kb.as_markup(),
    )

@dp.inline_query()
async def inline_create_check(query: InlineQuery):
    spec = parse_check_spec(query.query.split())
    if not spec:
        await query.answer(
            results=[],
            cache_time=0,
            is_personal=True,
            switch_pm_text="Открыть ALTERA",
            switch_pm_parameter="start",
        )
        return
    total, claims, recipient, comment = spec
    pending_id = secrets.token_urlsafe(8)
    pending_inline_checks[pending_id] = {
        "user_id": query.from_user.id,
        "total": total,
        "claims": claims,
        "recipient": recipient,
        "comment": comment,
        "created_at": time.time(),
    }
    kb = InlineKeyboardBuilder()
    kb.button(
        text=f"Создать счёт на {total:.2f} USDT",
        callback_data=f"create_check_{pending_id}",
        icon_custom_emoji_id="4924874531140535819",
        style="success",
    )
    result = InlineQueryResultArticle(
        id=f"check_{pending_id}",
        title="Создать счёт",
        description=f"Многоразовый счёт на {total:.2f} USDT",
        input_message_content=InputTextMessageContent(
            message_text=(
                f'<blockquote><b><tg-emoji emoji-id="4924819078817777378">💳</tg-emoji> '
                f'Счёт ALTERA на {total:.2f} USDT</b></blockquote>\n\n'
                '<blockquote><b><tg-emoji emoji-id="5213354182899179724">💬</tg-emoji> '
                'Нажмите кнопку ниже, чтобы создать чек и отправить его получателю.</b></blockquote>'
            ),
            parse_mode="HTML",
        ),
        reply_markup=kb.as_markup(),
    )
    await query.answer(results=[result], cache_time=0, is_personal=True)

@dp.message(Command("pay"))
async def cmd_pay_user(message: types.Message):
    args = message.text.split() if message.text else []
    if len(args) < 3 or not args[1].startswith("@"):
        await message.answer("Использование: /pay @username 10 комментарий")
        return
    amount = parse_check_amount(args[2])
    if amount is None:
        await message.answer("❌ Укажите корректную сумму перевода.")
        return
    recipient = await resolve_username(args[1])
    if not recipient:
        await message.answer("❌ Получатель ещё не запускал бота или username указан неверно.")
        return
    if not await transfer_balance(message.from_user.id, recipient[0], amount):
        await message.answer("❌ Недостаточно средств или нельзя переводить самому себе.")
        return
    comment = " ".join(args[3:]).strip()
    await message.answer(
        f"✅ Перевод выполнен: {amount:.2f} USDT пользователю @{html.escape(recipient[1])}."
        + (f"\n💬 Комментарий: {html.escape(comment)}" if comment else ""),
        parse_mode="HTML",
    )
    try:
        await get_active_bot().send_message(
            recipient[0],
            f"💰 Вам переведено {amount:.2f} USDT пользователем "
            f"@{html.escape(message.from_user.username or str(message.from_user.id))}."
            + (f"\n💬 Комментарий: {html.escape(comment)}" if comment else ""),
            parse_mode="HTML",
        )
    except TelegramAPIError as exc:
        logger.warning("Не удалось уведомить получателя перевода: %s", exc)

@dp.callback_query(F.data.startswith("create_check_"))
async def create_inline_check_cb(call: types.CallbackQuery):
    pending_id = call.data.removeprefix("create_check_")
    draft = pending_inline_checks.pop(pending_id, None)
    if not draft or draft["user_id"] != call.from_user.id:
        await call.answer("❌ Некорректная сумма чека.", show_alert=True)
        return
    recipient_data = await resolve_username(draft["recipient"]) if draft["recipient"] else None
    if draft["recipient"] and not recipient_data:
        await call.answer("❌ Получатель ещё не запускал бота.", show_alert=True)
        return
    token = await create_balance_check(
        call.from_user.id,
        draft["total"],
        draft["claims"],
        draft["comment"],
        draft["recipient"],
        recipient_data[0] if recipient_data else None,
    )
    if not token:
        await call.answer("❌ Недостаточно средств на балансе.", show_alert=True)
        return
    me = await get_active_bot().get_me()
    link = f"https://t.me/{me.username}?start=check_{token}"
    kb = InlineKeyboardBuilder()
    kb.button(
        text="Активировать чек",
        url=link,
        icon_custom_emoji_id="4925136584275134324",
        style="success",
    )
    check_text = (
        f'<blockquote><b><tg-emoji emoji-id="4924874531140535819">🎁</tg-emoji> '
        f'Чек ALTERA на {draft["total"]:.2f} USDT'
        f'{" (" + str(draft["claims"]) + " активации по " + f"{draft["total"] / draft["claims"]:.2f}" + " USDT)" if draft["claims"] > 1 else ""}'
        f'{" — " + html.escape(draft["comment"]) if draft["comment"] else ""}</b></blockquote>\n\n'
        '<blockquote><b><tg-emoji emoji-id="5213354182899179724">💬</tg-emoji> '
        'Чтобы активировать данный чек, нажмите на кнопку ниже</b></blockquote>'
    )
    if call.inline_message_id:
        await get_active_bot().edit_message_text(
            inline_message_id=call.inline_message_id,
            text=check_text,
            parse_mode="HTML",
            reply_markup=kb.as_markup(),
        )
    elif call.message:
        await call.message.edit_text(
            check_text,
            parse_mode="HTML",
            reply_markup=kb.as_markup(),
        )
    else:
        await call.answer("❌ Не удалось найти сообщение чека.", show_alert=True)
        return
    await call.answer("✅ Чек создан.")

@dp.callback_query(F.data == "accept_agreement")
async def accept_agreement_callback(call: types.CallbackQuery):
    user_id = call.from_user.id
    if not await faq_access_granted(user_id):
        await call.answer()
        return
    
    # Обновляем статус принятия соглашения
    await execute_query(
        "UPDATE users SET accepted = 1, accepted_at = ? WHERE id = ?",
        (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), user_id),
        commit=True
    )
    
    await call.answer("✅ Соглашение принято!")
    await call.message.delete()
    await show_privacy_policy(call.message)

@dp.callback_query(F.data == "accept_privacy")
async def accept_privacy_callback(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_row = await fetchone("SELECT accepted FROM users WHERE id = ?", (user_id,))
    if not user_row or not user_row[0]:
        await call.answer("Сначала примите пользовательское соглашение.", show_alert=True)
        return

    await execute_query(
        "UPDATE users SET privacy_accepted = 1 WHERE id = ?",
        (user_id,),
        commit=True
    )
    await call.answer("✅ Политика конфиденциальности принята!")
    await call.message.delete()
    await send_welcome_message(call.message)
    await show_main_menu(call.message)

async def send_welcome_message(message: types.Message):
    user_row = await fetchone(
        "SELECT welcome_sent FROM users WHERE id = ?",
        (message.chat.id,)
    )
    if not user_row or user_row[0]:
        return

    try:
        chat = await get_active_bot().get_chat(message.chat.id)
        if chat.pinned_message:
            await get_active_bot().delete_message(
                chat_id=message.chat.id,
                message_id=chat.pinned_message.message_id,
            )
    except (TelegramBadRequest, TelegramForbiddenError) as exc:
        logger.warning("Не удалось удалить старое закреплённое сообщение для %s: %s", message.chat.id, exc)

    welcome = await message.answer(
        '<b><tg-emoji emoji-id="4924775407590311811">❓</tg-emoji> Добро пожаловать в ALTERA! Магазин, в котором вы всегда '
        "можете найти нужные и, самое главное, качественные товары, под любой вкус и цвет.</b>\n\n"
        '<blockquote><b><tg-emoji emoji-id="5213256712911363107">🛡️</tg-emoji> Наши актуальные контакты:\n'
        "Основной бот маркет — @AlteraneBot\n"
        "Владелец проекта — @devAltera\n"
        "Поддержка — в личных сообщениях</b></blockquote>\n\n"
        '<blockquote><b><tg-emoji emoji-id="5213464941515808062">🛡️</tg-emoji> Правила пользования сервисом:\n'
        f'<a href="{AGREEMENT_URL}">Пользовательское соглашение</a>\n'
        f'<a href="{PRIVACY_POLICY_URL}">Политика конфиденциальности</a></b></blockquote>',
        parse_mode="HTML",
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
    try:
        await get_active_bot().pin_chat_message(
            chat_id=message.chat.id,
            message_id=welcome.message_id,
            disable_notification=True,
        )
    except TelegramBadRequest as exc:
        logger.warning("Не удалось закрепить приветствие для %s: %s", message.chat.id, exc)
    await execute_query(
        "UPDATE users SET welcome_sent = 1 WHERE id = ?",
        (message.chat.id,),
        commit=True,
    )

async def show_main_menu(message: types.Message):
    caption_text = (
        "<b>"
        f'<tg-emoji emoji-id="{CustomEmoji.DIAMOND}">💎</tg-emoji> Главное меню ALTERA. Качество, проверенное временем. Зашифрованные платежи, моментальная выдача товара, быстрая замена, все у нас есть.\n\n'
        f'<tg-emoji emoji-id="{CustomEmoji.PIN}">📌</tg-emoji> Нижние кнопки - навигация по магазину.'
        "</b>"
    )
    await send_with_image(message, 'EleghantShopIcon', caption_text, main_keyboard())

def main_menu_back_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data=callback_data, icon_custom_emoji_id=CustomEmoji.BACK, style="danger")
    return kb.as_markup()

@dp.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu_cb(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await call.message.delete()
    except TelegramBadRequest:
        pass
    await show_main_menu(call.message)
    await call.answer()

@dp.callback_query(F.data == "back_to_faq")
async def back_to_faq_cb(call: types.CallbackQuery, state: FSMContext):
    await text_faq(call.message, call.from_user.id, state)
    await call.answer()

@dp.callback_query(F.data == "onboarding_agreement")
async def onboarding_agreement_cb(call: types.CallbackQuery):
    if not await faq_access_granted(call.from_user.id):
        await call.answer()
        return
    registration = await fetchone(
        "SELECT accepted, privacy_accepted FROM users WHERE id = ?",
        (call.from_user.id,),
    )
    if registration and registration[0] and registration[1] == 1:
        await call.message.delete()
        await show_main_menu(call.message)
        await call.answer()
        return
    await call.message.delete()
    await show_agreement(call.message)
    await call.answer()

@dp.callback_query(F.data == "back_to_deposit")
async def back_to_deposit_cb(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await text_deposit(call.message, state)
    await call.answer()

@dp.callback_query(F.data == "back_to_reviews")
async def back_to_reviews_cb(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await profile_reviews_cb(call)

# ═══════════════════════════════════════════════════════════════════════════════
# АДМИН ПАНЕЛЬ
# ═══════════════════════════════════════════════════════════════════════════════

def build_admin_keyboard() -> InlineKeyboardMarkup:
    status_btn_text = "🔴 Выключить тех. работы" if MAINTENANCE_MODE else "🟢 Включить тех. работы"
    kb = InlineKeyboardBuilder()
    kb.button(text=status_btn_text, callback_data="admin_toggle_maintenance")
    kb.button(text="📢 Рассылка", callback_data="admin_broadcast")
    kb.button(text="📢 Рассылка с картинкой", callback_data="admin_broadcast_image")
    kb.button(text="💰 Выдать баланс", callback_data="admin_give_balance")
    kb.button(text="📦 Добавить товар", callback_data="admin_add_stock")
    kb.button(text="📄 Загрузить товары из .txt", callback_data="admin_add_stock_txt")
    kb.button(text="🎫 Создать промокод", callback_data="admin_create_promo")
    kb.button(text="🎫 Список промокодов", callback_data="admin_list_promos")
    kb.button(text="📊 История промокодов", callback_data="admin_promo_history")
    kb.button(text="💰 Изменить цену категории", callback_data="admin_change_price")
    kb.button(text="📝 Изменить описание категории", callback_data="admin_change_desc")
    kb.button(text="🛠 Тех. работы категорий", callback_data="admin_category_maintenance")
    kb.button(text="⭐ Статистика лотов", callback_data="admin_product_stats")
    kb.button(text="⭐ Выдать отзывы категории", callback_data="admin_give_reviews")
    kb.button(text="🏆 Топ покупателей", callback_data="admin_top_buyers")
    kb.button(text="🔍 Найти пользователя", callback_data="admin_search_user")
    kb.button(text="🚫 Заблокировать пользователя", callback_data="admin_ban_user")
    kb.button(text="✅ Разблокировать пользователя", callback_data="admin_unban_user")
    kb.button(text="💸 Заявки на вывод", callback_data="admin_withdraws")
    kb.adjust(1)
    return kb.as_markup()

@dp.callback_query(F.data == "admin_product_stats")
async def admin_product_stats_cb(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    rows = await fetchall(
        "SELECT c.id, c.name, COUNT(DISTINCT h.user_id), COUNT(r.id), COALESCE(AVG(r.rating), 0) "
        "FROM categories c LEFT JOIN history h ON h.cat_id = c.id LEFT JOIN reviews r ON r.cat_id = c.id "
        "GROUP BY c.id ORDER BY c.id"
    )
    text = "⭐ <b>Статистика лотов</b>\n\n"
    for cat_id, name, buyers, reviews, avg in rows:
        text += f"#{cat_id} {html.escape(name)} — покупок: {buyers}, отзывов: {reviews}, рейтинг: {avg:.1f}/5\n"
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data="back_to_admin", style="danger")
    await call.message.edit_text(text or "Нет категорий.", parse_mode="HTML", reply_markup=kb.as_markup())
    await call.answer()

@dp.callback_query(F.data == "admin_give_reviews")
async def admin_give_reviews_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    categories = await fetchall("SELECT id, name FROM categories ORDER BY id")
    if not categories:
        await call.answer("❌ Категории не найдены", show_alert=True)
        return
    kb = InlineKeyboardBuilder()
    for cat_id, name in categories:
        kb.button(text=f"[{cat_id}] {name}", callback_data=f"give_reviews_cat_{cat_id}")
    kb.button(text="Назад", callback_data="back_to_admin", style="danger")
    kb.adjust(1)
    await call.message.edit_text(
        "⭐ <b>Выдача отзывов</b>\n\nВыберите категорию:",
        parse_mode="HTML",
        reply_markup=kb.as_markup(),
    )
    await state.set_state(AdminState.give_reviews_category)
    await call.answer()

@dp.callback_query(F.data.startswith("give_reviews_cat_"), AdminState.give_reviews_category)
async def admin_give_reviews_category(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    try:
        cat_id = int(call.data.rsplit("_", 1)[1])
    except (IndexError, ValueError):
        await call.answer("❌ Некорректная категория", show_alert=True)
        return
    category = await fetchone("SELECT name FROM categories WHERE id = ?", (cat_id,))
    if not category:
        await call.answer("❌ Категория не найдена", show_alert=True)
        return
    await state.update_data(give_reviews_cat_id=cat_id, give_reviews_cat_name=category[0])
    await state.set_state(AdminState.give_reviews_count)
    await call.message.edit_text(
        f"⭐ Категория: <b>{html.escape(category[0])}</b>\n\n"
        f"Введите количество отзывов (от 1 до {MAX_BULK_ADD}):",
        parse_mode="HTML",
    )
    await call.answer()

@dp.message(AdminState.give_reviews_count)
async def admin_give_reviews_count(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        count = int((message.text or "").strip())
    except ValueError:
        await message.answer("❌ Введите целое число.")
        return
    if not 1 <= count <= MAX_BULK_ADD:
        await message.answer(f"❌ Количество должно быть от 1 до {MAX_BULK_ADD}.")
        return
    await state.update_data(give_reviews_count=count)
    await state.set_state(AdminState.give_reviews_rating)
    await message.answer("Введите оценку для этих отзывов (от 1 до 5):")

@dp.message(AdminState.give_reviews_rating)
async def admin_give_reviews_rating(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        rating = int((message.text or "").strip())
    except ValueError:
        await message.answer("❌ Введите целое число от 1 до 5.")
        return
    if not 1 <= rating <= 5:
        await message.answer("❌ Оценка должна быть от 1 до 5.")
        return
    await state.update_data(give_reviews_rating=rating)
    await state.set_state(AdminState.give_reviews_text)
    await message.answer("Введите текст отзывов или отправьте «-», чтобы оставить их без текста:")

@dp.message(AdminState.give_reviews_text)
async def admin_give_reviews_text(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    review_text = "" if (message.text or "").strip() == "-" else (message.text or "").strip()
    cat_id = data["give_reviews_cat_id"]
    count = data["give_reviews_count"]
    rating = data["give_reviews_rating"]
    lowest_id = await fetchone("SELECT COALESCE(MIN(user_id), 0) FROM reviews")
    first_synthetic_user_id = min(-1, (lowest_id[0] if lowest_id else 0) - 1)
    created_at = datetime.now(timezone.utc).isoformat()
    rows = [
        (first_synthetic_user_id - index, cat_id, rating, review_text, created_at)
        for index in range(count)
    ]
    await executemany(
        "INSERT INTO reviews (user_id, cat_id, rating, text, created_at) VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    await message.answer(
        f"✅ Добавлено отзывов: <b>{count}</b>\n"
        f"Категория: <b>{html.escape(data['give_reviews_cat_name'])}</b>\n"
        f"Оценка: <b>{rating}/5</b>",
        parse_mode="HTML",
    )
    logger.info(
        "Admin %s added %s synthetic reviews to category %s",
        message.from_user.id,
        count,
        cat_id,
    )
    await state.clear()

@dp.callback_query(F.data == "admin_category_maintenance")
async def admin_category_maintenance_cb(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    categories = await fetchall("SELECT id, name, maintenance FROM categories ORDER BY id")
    kb = InlineKeyboardBuilder()
    for cat_id, name, maintenance in categories:
        status = "🔴 ВЫКЛ" if maintenance else "🟢 ВКЛ"
        kb.button(text=f"{status} [{cat_id}] {name}", callback_data=f"toggle_cat_maintenance_{cat_id}")
    kb.button(text="Назад", callback_data="back_to_admin", style="danger")
    kb.adjust(1)
    await call.message.edit_text(
        "🛠 <b>Технические работы категорий</b>\n\n"
        "Выключенная категория остается в каталоге, но покупки недоступны.",
        parse_mode="HTML", reply_markup=kb.as_markup()
    )
    await call.answer()

@dp.callback_query(F.data.startswith("toggle_cat_maintenance_"))
async def toggle_category_maintenance_cb(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    try:
        cat_id = int(call.data.rsplit("_", 1)[1])
    except ValueError:
        await call.answer("❌ Некорректная категория", show_alert=True)
        return
    await execute_query(
        "UPDATE categories SET maintenance = CASE maintenance WHEN 1 THEN 0 ELSE 1 END WHERE id = ?",
        (cat_id,), commit=True
    )
    await call.answer("✅ Статус категории обновлен")
    await admin_category_maintenance_cb(call)

@dp.message(Command("admintools"))
async def admin_tools(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    status_text = "🔴 Тех. работы ВКЛЮЧЕНЫ" if MAINTENANCE_MODE else "🟢 Бот работает в штатном режиме"
    await message.answer(
        f"🔧 <b>Панель администратора</b>\n\nСтатус: {status_text}\n\nВыберите действие:",
        reply_markup=build_admin_keyboard(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "admin_toggle_maintenance")
async def admin_toggle_maintenance(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    global MAINTENANCE_MODE
    MAINTENANCE_MODE = not MAINTENANCE_MODE
    if MAINTENANCE_MODE:
        status_text = "🔴 Тех. работы <b>ВКЛЮЧЕНЫ</b>\n\nПользователи видят сообщение о тех. работах."
        logger.info(f"Admin {call.from_user.id} ENABLED maintenance mode")
    else:
        status_text = "🟢 Бот <b>работает в штатном режиме</b>\n\nВсе пользователи имеют доступ."
        logger.info(f"Admin {call.from_user.id} DISABLED maintenance mode")
    try:
        await call.message.edit_text(
            f"🔧 <b>Панель администратора</b>\n\nСтатус: {status_text}\n\nВыберите действие:",
            reply_markup=build_admin_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        await call.message.answer(
            f"🔧 <b>Панель администратора</b>\n\nСтатус: {status_text}\n\nВыберите действие:",
            reply_markup=build_admin_keyboard(),
            parse_mode="HTML"
        )
    await call.answer("✅ Статус изменён!")

# ═══════════════════════════════════════════════════════════════════════════════
# НОВОЕ: ИЗМЕНЕНИЕ ОПИСАНИЯ КАТЕГОРИИ
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "admin_change_desc")
async def admin_change_desc_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    categories = await fetchall("SELECT id, name FROM categories")
    if not categories:
        await call.message.edit_text("❌ Нет категорий.")
        return
    kb = InlineKeyboardBuilder()
    for cat_id, name in categories:
        kb.button(text=name, callback_data=f"change_desc_cat_{cat_id}")
    kb.button(text="Назад", callback_data="back_to_admin", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    kb.adjust(1)
    await call.message.edit_text(
        "📝 <b>Изменение описания категории</b>\n\nВыберите категорию:",
        reply_markup=kb.as_markup(), parse_mode="HTML"
    )
    await state.set_state(AdminState.change_desc_category)
    await call.answer()

@dp.callback_query(F.data.startswith("change_desc_cat_"), AdminState.change_desc_category)
async def admin_change_desc_cat(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    try:
        cat_id = int(call.data.split("_")[3])
    except (IndexError, ValueError):
        await call.answer("❌ Ошибка")
        return
    cat = await fetchone("SELECT id, name, desc FROM categories WHERE id = ?", (cat_id,))
    if not cat:
        await call.answer("❌ Категория не найдена")
        return
    await state.update_data(change_desc_cat_id=cat_id, change_desc_cat_name=cat[1])
    await state.set_state(AdminState.change_desc_value)
    current_desc = cat[2] or "Описание не задано"
    preview = html.escape(current_desc[:400] + ("..." if len(current_desc) > 400 else ""))
    await call.message.answer(
        f"📝 <b>Категория: {cat[1]}</b>\n\n"
        f"<b>Текущее описание (первые 400 символов):</b>\n<code>{preview}</code>\n\n"
        f"Отправьте новое описание (поддерживается HTML и tg-emoji):",
        parse_mode="HTML"
    )
    await call.answer()

@dp.message(AdminState.change_desc_value)
async def admin_change_desc_value(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    new_desc = message.html_text
    if not new_desc or not new_desc.strip():
        await message.answer("❌ Описание не может быть пустым.")
        return
    data = await state.get_data()
    cat_id = data['change_desc_cat_id']
    cat_name = data['change_desc_cat_name']
    await execute_query(
        "UPDATE categories SET desc = ? WHERE id = ?",
        (new_desc, cat_id), commit=True
    )
    await state.clear()
    await message.answer(
        f"✅ <b>Описание категории «{cat_name}» обновлено!</b>\n\n"
        f"<b>Новое описание:</b>\n{html.escape(new_desc)}",
        parse_mode="HTML"
    )
    logger.info(f"Admin {message.from_user.id} changed description for category {cat_id}")

# ═══════════════════════════════════════════════════════════════════════════════
# НОВОЕ: СПИСОК И УДАЛЕНИЕ ПРОМОКОДОВ
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "admin_list_promos")
async def admin_list_promos_cb(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    promos = await fetchall(
        "SELECT id, code, amount, promo_type, max_uses, used FROM promo_codes ORDER BY id DESC"
    )
    kb = InlineKeyboardBuilder()
    if not promos:
        kb.button(text="Назад", callback_data="back_to_admin", style='danger')
        try:
            await call.message.delete()
        except Exception:
            pass
        await call.message.answer(
            "🎫 <b>Промокоды</b>\n\n📭 Нет активных промокодов.",
            parse_mode="HTML", reply_markup=kb.as_markup()
        )
        await call.answer()
        return

    text = "🎫 <b>Все промокоды:</b>\n\n"
    for pid, code, amount, promo_type, max_uses, used in promos:
        remaining = max_uses - used
        status = "✅" if remaining > 0 else "❌"
        type_str = f"{amount}%" if promo_type == "percent" else f"{amount} USDT"
        text += f"{status} <code>{code}</code> | {type_str} | {used}/{max_uses} исп.\n"

    # Кнопки удаления — по одной на каждый промокод
    for pid, code, amount, promo_type, max_uses, used in promos:
        kb.button(text=f"🗑 Удалить {code}", callback_data=f"admin_del_promo_{pid}")
    kb.button(text="Назад", callback_data="back_to_admin", style='danger')
    kb.adjust(1)

    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(text, parse_mode="HTML", reply_markup=kb.as_markup())
    await call.answer()

@dp.callback_query(F.data.startswith("admin_del_promo_"))
async def admin_del_promo_cb(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    try:
        promo_id = int(call.data.split("_")[3])
    except (IndexError, ValueError):
        await call.answer("❌ Ошибка")
        return
    promo = await fetchone("SELECT code FROM promo_codes WHERE id = ?", (promo_id,))
    if not promo:
        await call.answer("❌ Промокод не найден", show_alert=True)
        return
    code = promo[0]
    await execute_query("DELETE FROM promo_codes WHERE id = ?", (promo_id,), commit=True)
    logger.info(f"Admin {call.from_user.id} deleted promo code {code} (id={promo_id})")
    await call.answer(f"✅ Промокод {code} удалён!")
    # Обновляем список
    await admin_list_promos_cb(call)

# ═══════════════════════════════════════════════════════════════════════════════
# НОВОЕ: ИСТОРИЯ ИСПОЛЬЗОВАНИЯ ПРОМОКОДОВ
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "admin_promo_history")
async def admin_promo_history_cb(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    rows = await fetchall(
        "SELECT code, user_id, username, used_at FROM promo_usage ORDER BY id DESC LIMIT 50"
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data="back_to_admin", style='danger')
    kb.adjust(1)
    if not rows:
        try:
            await call.message.delete()
        except Exception:
            pass
        await call.message.answer(
            "📊 <b>История промокодов</b>\n\n📭 Пока никто не использовал промокоды.",
            parse_mode="HTML", reply_markup=kb.as_markup()
        )
        await call.answer()
        return
    text = f"📊 <b>История использования промокодов (последние {len(rows)}):</b>\n\n"
    for code, user_id, username, used_at in rows:
        u = f"@{username}" if username else f"ID:{user_id}"
        text += f"<code>{code}</code> | {u} | {used_at[:16]}\n"
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(text, parse_mode="HTML", reply_markup=kb.as_markup())
    await call.answer()

# ═══════════════════════════════════════════════════════════════════════════════
# НОВОЕ: ТОП ПОКУПАТЕЛЕЙ
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "admin_top_buyers")
async def admin_top_buyers_cb(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    rows = await fetchall(
        "SELECT id, username, total FROM users ORDER BY total DESC LIMIT 20"
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data="back_to_admin", style='danger')
    kb.adjust(1)
    if not rows:
        try:
            await call.message.delete()
        except Exception:
            pass
        await call.message.answer(
            "🏆 <b>Топ покупателей</b>\n\n📭 Нет данных.",
            parse_mode="HTML", reply_markup=kb.as_markup()
        )
        await call.answer()
        return
    medals = ["🥇", "🥈", "🥉"]
    text = "🏆 <b>Топ-20 покупателей по количеству покупок:</b>\n\n"
    for idx, (uid, username, total) in enumerate(rows):
        medal = medals[idx] if idx < 3 else f"{idx + 1}."
        u = f"@{username}" if username else f"ID:{uid}"
        text += f"{medal} {u} — <b>{total} шт.</b>\n"
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(text, parse_mode="HTML", reply_markup=kb.as_markup())
    await call.answer()

# ═══════════════════════════════════════════════════════════════════════════════
# НОВОЕ: ПОИСК ПОЛЬЗОВАТЕЛЯ ПО USERNAME
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "admin_search_user")
async def admin_search_user_cb(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminState.search_user_username)
    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена", callback_data="back_to_admin")
    kb.adjust(1)
    await call.message.answer(
        "🔍 <b>Поиск пользователя</b>\n\n"
        "Введите username (без @) или ID пользователя:",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await call.answer()

@dp.message(AdminState.search_user_username)
async def admin_search_user_msg(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    query = message.text.strip().lstrip('@')
    await state.clear()

    # Пробуем найти по ID
    user_row = None
    if query.isdigit():
        user_row = await fetchone(
            "SELECT id, username, total, is_banned, ban_reason FROM users WHERE id = ?",
            (int(query),)
        )
    # Если не нашли по ID — ищем по username
    if not user_row:
        user_row = await fetchone(
            "SELECT id, username, total, is_banned, ban_reason FROM users WHERE LOWER(username) = LOWER(?)",
            (query,)
        )

    if not user_row:
        await message.answer(f"❌ Пользователь <code>{query}</code> не найден в базе.", parse_mode="HTML")
        return

    uid, username, total, is_banned, ban_reason = user_row
    balance = await get_balance(uid)
    ref_count, ref_earn = await get_referral_info(uid)
    ban_status = f"🚫 Заблокирован\nПричина: {ban_reason or 'не указана'}" if is_banned else "✅ Активен"

    text = (
        f"🔍 <b>Результат поиска</b>\n\n"
        f"🆔 ID: <code>{uid}</code>\n"
        f"🔗 Username: @{username if username else '—'}\n"
        f"💰 Баланс: <b>{balance} USDT</b>\n"
        f"🛒 Покупок: <b>{total}</b>\n"
        f"👥 Рефералов: {ref_count} | Заработано: {ref_earn} USDT\n"
        f"📊 Статус: {ban_status}"
    )
    kb = InlineKeyboardBuilder()
    if is_banned:
        kb.button(text="✅ Разблокировать", callback_data=f"quick_unban_{uid}")
    else:
        kb.button(text="🚫 Заблокировать", callback_data=f"quick_ban_{uid}")
    kb.button(text="Назад", callback_data="back_to_admin", style='danger')
    kb.adjust(1)
    await message.answer(text, parse_mode="HTML", reply_markup=kb.as_markup())

# ═══════════════════════════════════════════════════════════════════════════════
# НОВОЕ: БАН / РАЗБАН ПОЛЬЗОВАТЕЛЯ
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "admin_ban_user")
async def admin_ban_user_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminState.ban_user_id)
    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена", callback_data="back_to_admin")
    kb.adjust(1)
    await call.message.answer(
        "🚫 <b>Блокировка пользователя</b>\n\nВведите ID или username пользователя:",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await call.answer()

@dp.message(AdminState.ban_user_id)
async def admin_ban_user_id_msg(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    query = message.text.strip().lstrip('@')
    user_row = None
    if query.isdigit():
        user_row = await fetchone("SELECT id, username FROM users WHERE id = ?", (int(query),))
    if not user_row:
        user_row = await fetchone("SELECT id, username FROM users WHERE LOWER(username) = LOWER(?)", (query,))
    if not user_row:
        await message.answer(f"❌ Пользователь не найден.")
        await state.clear()
        return
    uid, username = user_row
    await state.update_data(ban_target_id=uid, ban_target_username=username)
    await state.set_state(AdminState.ban_user_reason)
    kb = InlineKeyboardBuilder()
    kb.button(text="Без причины", callback_data=f"ban_noreason_{uid}")
    kb.adjust(1)
    await message.answer(
        f"🚫 Блокировка: @{username or uid}\n\nВведите причину блокировки:",
        reply_markup=kb.as_markup()
    )

@dp.message(AdminState.ban_user_reason)
async def admin_ban_user_reason_msg(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    uid = data['ban_target_id']
    username = data['ban_target_username']
    reason = message.text.strip()
    await _do_ban_user(uid, username, reason, message, state)

@dp.callback_query(F.data.startswith("ban_noreason_"))
async def ban_noreason_cb(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    uid = data.get('ban_target_id')
    username = data.get('ban_target_username', '')
    await _do_ban_user(uid, username, None, call.message, state)
    await call.answer()

@dp.callback_query(F.data.startswith("quick_ban_"))
async def quick_ban_cb(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    try:
        uid = int(call.data.split("_")[2])
    except (IndexError, ValueError):
        await call.answer("❌ Ошибка")
        return
    user_row = await fetchone("SELECT username FROM users WHERE id = ?", (uid,))
    username = user_row[0] if user_row else ""
    await state.update_data(ban_target_id=uid, ban_target_username=username)
    await state.set_state(AdminState.ban_user_reason)
    kb = InlineKeyboardBuilder()
    kb.button(text="Без причины", callback_data=f"ban_noreason_{uid}")
    kb.adjust(1)
    await call.message.answer(
        f"🚫 Блокировка ID {uid}\n\nВведите причину блокировки:",
        reply_markup=kb.as_markup()
    )
    await call.answer()

async def _do_ban_user(uid, username, reason, message_obj, state):
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    await execute_query(
        "UPDATE users SET is_banned = 1, ban_reason = ?, banned_at = ? WHERE id = ?",
        (reason, now_str, uid), commit=True
    )
    u = f"@{username}" if username else f"ID:{uid}"
    reason_text = reason or "Не указана"
    await message_obj.answer(
        f"✅ <b>Пользователь {u} заблокирован</b>\n\n📝 Причина: {reason_text}",
        parse_mode="HTML"
    )
    try:
        notify_text = (
            f'🚫 <b>Вы заблокированы</b>\n\n'
            f'Причина: {reason_text}\n\n'
            f'Для обжалования обратитесь в поддержку: {SUPPORT_URL}'
        )
        await get_active_bot().send_message(uid, notify_text, parse_mode="HTML")
    except Exception:
        pass
    logger.info(f"Admin banned user {uid}, reason: {reason_text}")
    await state.clear()

# --- РАЗБАН ---
@dp.callback_query(F.data == "admin_unban_user")
async def admin_unban_user_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminState.unban_user_id)
    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена", callback_data="back_to_admin")
    kb.adjust(1)
    await call.message.answer(
        "✅ <b>Разблокировка пользователя</b>\n\nВведите ID или username пользователя:",
        parse_mode="HTML",
        reply_markup=kb.as_markup()
    )
    await call.answer()

@dp.message(AdminState.unban_user_id)
async def admin_unban_user_msg(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    query = message.text.strip().lstrip('@')
    user_row = None
    if query.isdigit():
        user_row = await fetchone("SELECT id, username, is_banned FROM users WHERE id = ?", (int(query),))
    if not user_row:
        user_row = await fetchone("SELECT id, username, is_banned FROM users WHERE LOWER(username) = LOWER(?)", (query,))
    if not user_row:
        await message.answer("❌ Пользователь не найден.")
        await state.clear()
        return
    uid, username, is_banned = user_row
    if not is_banned:
        await message.answer(f"ℹ️ Пользователь @{username or uid} не заблокирован.")
        await state.clear()
        return
    await execute_query(
        "UPDATE users SET is_banned = 0, ban_reason = NULL, banned_at = NULL WHERE id = ?",
        (uid,), commit=True
    )
    u = f"@{username}" if username else f"ID:{uid}"
    await message.answer(f"✅ <b>Пользователь {u} разблокирован!</b>", parse_mode="HTML")
    try:
        await get_active_bot().send_message(uid, "✅ <b>Ваша блокировка снята.</b> Добро пожаловать обратно!", parse_mode="HTML")
    except Exception:
        pass
    logger.info(f"Admin unbanned user {uid}")
    await state.clear()

@dp.callback_query(F.data.startswith("quick_unban_"))
async def quick_unban_cb(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    try:
        uid = int(call.data.split("_")[2])
    except (IndexError, ValueError):
        await call.answer("❌ Ошибка")
        return
    user_row = await fetchone("SELECT username FROM users WHERE id = ?", (uid,))
    username = user_row[0] if user_row else ""
    await execute_query(
        "UPDATE users SET is_banned = 0, ban_reason = NULL, banned_at = NULL WHERE id = ?",
        (uid,), commit=True
    )
    u = f"@{username}" if username else f"ID:{uid}"
    await call.message.answer(f"✅ <b>Пользователь {u} разблокирован!</b>", parse_mode="HTML")
    try:
        await get_active_bot().send_message(uid, "✅ <b>Ваша блокировка снята.</b> Добро пожаловать обратно!", parse_mode="HTML")
    except Exception:
        pass
    logger.info(f"Admin unbanned user {uid}")
    await call.answer("✅ Разблокирован!")

# ═══════════════════════════════════════════════════════════════════════════════
# ЗАЯВКИ НА ВЫВОД В АДМИНКЕ
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "admin_withdraws")
async def admin_withdraws_cb(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    requests = await fetchall(
        "SELECT id, user_id, username, amount, status, created_at FROM withdraw_requests "
        "WHERE status = 'pending' ORDER BY created_at ASC LIMIT 20"
    )
    if not requests:
        kb = InlineKeyboardBuilder()
        kb.button(text="Назад", callback_data="back_to_admin", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
        try:
            await call.message.delete()
        except Exception:
            pass
        await call.message.answer(
            "💸 <b>Заявки на вывод</b>\n\n📭 Активных заявок нет.",
            parse_mode="HTML",
            reply_markup=kb.as_markup()
        )
        await call.answer()
        return
    text = f'💸 <b>Активные заявки на вывод ({len(requests)}):</b>\n\n'
    for rid, uid, uname, amount, status, created in requests:
        u = f"@{uname}" if uname else f"ID:{uid}"
        text += f"<b>#{rid}</b> | {u} | <b>{amount} USDT</b> | {created[:16]}\n"
    kb = InlineKeyboardBuilder()
    for rid, uid, uname, amount, status, created in requests:
        kb.button(text=f"#{rid} — {amount} USDT", callback_data=f"admin_withdraw_detail_{rid}")
    kb.button(text="Назад", callback_data="back_to_admin", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    kb.adjust(1)
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(text, parse_mode="HTML", reply_markup=kb.as_markup())
    await call.answer()

@dp.callback_query(F.data.startswith("admin_withdraw_detail_"))
async def admin_withdraw_detail_cb(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    try:
        request_id = int(call.data.split("_")[3])
    except (IndexError, ValueError):
        await call.answer("❌ Ошибка")
        return
    request = await fetchone(
        "SELECT id, user_id, username, amount, status, created_at FROM withdraw_requests WHERE id = ?",
        (request_id,)
    )
    if not request:
        await call.answer("❌ Заявка не найдена", show_alert=True)
        return
    rid, uid, uname, amount, status, created = request
    u = f"@{uname}" if uname else f"ID:{uid}"
    text = (
        f'💸 <b>Заявка #{rid}</b>\n\n'
        f'👤 Пользователь: {u}\n'
        f'🆔 ID: <code>{uid}</code>\n'
        f'💰 Сумма: <b>{amount} USDT</b>\n'
        f'📅 Дата: {created[:16]}\n'
        f'📊 Статус: {status}'
    )
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Одобрить", callback_data=f"withdraw_approve_{rid}")
    kb.button(text="❌ Отклонить", callback_data=f"withdraw_reject_{rid}")
    kb.button(text="К списку заявок", callback_data="admin_withdraws")
    kb.adjust(2)
    await call.message.answer(text, parse_mode="HTML", reply_markup=kb.as_markup())
    await call.answer()

# ═══════════════════════════════════════════════════════════════════════════════
# РАССЫЛКА
# ═══════════════════════════════════════════════════════════════════════════════

BROADCAST_HELP = (
    "📢 <b>Рассылка</b>\n\n"
    "Напишите текст рассылки. Поддерживается <b>HTML-форматирование</b>:\n\n"
    "<b>Теги форматирования:</b>\n"
    "• <code>&lt;b&gt;жирный&lt;/b&gt;</code>\n"
    "• <code>&lt;i&gt;курсив&lt;/i&gt;</code>\n"
    "• <code>&lt;u&gt;подчёркнутый&lt;/u&gt;</code>\n"
    "• <code>&lt;s&gt;зачёркнутый&lt;/s&gt;</code>\n"
    "• <code>&lt;code&gt;моноширный&lt;/code&gt;</code>\n"
    "• <code>&lt;pre&gt;блок кода&lt;/pre&gt;</code>\n"
    "• <code>&lt;blockquote&gt;цитата&lt;/blockquote&gt;</code>\n\n"
    "<b>Премиум-эмодзи:</b>\n"
    "<code>&lt;tg-emoji emoji-id=\"ID\"&gt;🔥&lt;/tg-emoji&gt;</code>\n\n"
    "<b>Ссылки:</b>\n"
    "<code>&lt;a href=\"https://...\"&gt;текст&lt;/a&gt;</code>\n\n"
    "Просто отправьте текст с нужным оформлением:"
)

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await state.update_data(broadcast_photo=None)
    await state.set_state(AdminState.broadcast_text)
    await call.message.edit_text(BROADCAST_HELP, parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data == "admin_broadcast_image")
async def admin_broadcast_image_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminState.broadcast_with_image)
    await call.message.edit_text(
        "📢 <b>Рассылка с картинкой</b>\n\nСначала отправьте <b>фото</b> (как фото, не файл):",
        parse_mode="HTML"
    )
    await call.answer()

@dp.message(AdminState.broadcast_with_image)
async def admin_broadcast_image_get(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.photo:
        await message.answer("❌ Пожалуйста, отправьте фото (не файл).")
        return
    photo = message.photo[-1]
    await state.update_data(broadcast_photo=photo.file_id)
    await state.set_state(AdminState.broadcast_text)
    await message.answer(BROADCAST_HELP, parse_mode="HTML")

@dp.message(AdminState.broadcast_text)
async def admin_broadcast_send(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.html_text
    await state.update_data(broadcast_text=text)
    await state.set_state(AdminState.broadcast_ask_button)
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Добавить кнопку", callback_data="broadcast_add_button")
    kb.button(text="➡️ Без кнопки", callback_data="broadcast_no_button")
    kb.adjust(1)
    await message.answer("Хотите добавить инлайн-кнопку к рассылке?", reply_markup=kb.as_markup())


@dp.callback_query(F.data == "broadcast_add_button")
async def broadcast_add_button_cb(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminState.broadcast_button_text)
    await call.message.edit_text("Введите текст кнопки (например: Перейти в магазин):")
    await call.answer()


@dp.callback_query(F.data == "broadcast_no_button", AdminState.broadcast_ask_button)
async def broadcast_no_button_cb(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await state.update_data(broadcast_buttons=[])
    await _show_broadcast_preview(call.message, state)
    await call.answer()


@dp.message(AdminState.broadcast_button_text)
async def broadcast_button_text_msg(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    btn_text = message.text.strip()
    if not btn_text:
        await message.answer("❌ Текст кнопки не может быть пустым.")
        return
    await state.update_data(broadcast_button_text=btn_text)
    await state.set_state(AdminState.broadcast_button_url)
    await message.answer(
        "🔗 Теперь введите ссылку для кнопки.\n"
        "Например: <code>https://t.me/AlteraneBot</code>",
        parse_mode="HTML",
    )


@dp.message(AdminState.broadcast_button_url)
async def broadcast_button_url_msg(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("tg://")):
        await message.answer("❌ Ссылка должна начинаться с http://, https:// или tg://")
        return
    await state.update_data(broadcast_button_url=url)
    await state.set_state(AdminState.broadcast_button_emoji)
    await message.answer(
        "✨ Отправьте ID премиум-эмодзи для кнопки.\n"
        "Или отправьте <code>-</code>, чтобы оставить кнопку без эмодзи.",
        parse_mode="HTML",
    )


@dp.message(AdminState.broadcast_button_emoji)
async def broadcast_button_emoji_msg(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    emoji_id = (message.text or "").strip()
    if emoji_id == "-":
        emoji_id = None
    elif not emoji_id.isdigit():
        await message.answer("❌ ID должен содержать только цифры. Или отправьте «-».")
        return
    await state.update_data(broadcast_button_emoji=emoji_id)
    await state.set_state(AdminState.broadcast_button_style)
    kb = InlineKeyboardBuilder()
    for style, label in (
        ("primary", "🔵 Синий"),
        ("success", "🟢 Зелёный"),
        ("danger", "🔴 Красный"),
        ("-","⚪ Стандартный"),
    ):
        kb.button(text=label, callback_data=f"broadcast_style_{style}")
    kb.adjust(2)
    await message.answer("🎨 Выберите цвет кнопки:", reply_markup=kb.as_markup())


@dp.callback_query(F.data.startswith("broadcast_style_"), AdminState.broadcast_button_style)
async def broadcast_button_style_cb(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    style = call.data.removeprefix("broadcast_style_")
    data = await state.get_data()
    buttons = list(data.get("broadcast_buttons") or [])
    buttons.append({
        "text": data["broadcast_button_text"],
        "url": data["broadcast_button_url"],
        "emoji": data.get("broadcast_button_emoji"),
        "style": None if style == "-" else style,
    })
    await state.update_data(broadcast_buttons=buttons)
    await state.set_state(AdminState.broadcast_more_buttons)
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Добавить ещё кнопку", callback_data="broadcast_add_button")
    kb.button(text="✅ Готово, показать предпросмотр", callback_data="broadcast_buttons_done")
    kb.adjust(1)
    await call.message.edit_text(
        f"✅ Кнопка добавлена ({len(buttons)}).\n\n"
        "Можно добавить ещё кнопки или перейти к предпросмотру.",
        reply_markup=kb.as_markup(),
    )
    await call.answer()


@dp.callback_query(F.data == "broadcast_buttons_done", AdminState.broadcast_more_buttons)
async def broadcast_buttons_done_cb(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await _show_broadcast_preview(call.message, state)
    await call.answer()


async def _show_broadcast_preview(message_obj: types.Message, state: FSMContext):
    data = await state.get_data()
    text = data.get('broadcast_text', '')
    photo_id = data.get('broadcast_photo')
    buttons = data.get("broadcast_buttons") or []

    preview_kb = InlineKeyboardBuilder()
    for button in buttons:
        preview_kb.button(
            text=button["text"],
            url=button["url"],
            icon_custom_emoji_id=button.get("emoji"),
            style=button.get("style"),
        )
    preview_kb.button(text="✅ Отправить всем", callback_data="confirm_broadcast")
    preview_kb.button(text="❌ Отменить", callback_data="cancel_broadcast")
    preview_kb.adjust(1, 2)

    preview_msg = "👁 <b>Предпросмотр рассылки:</b>\n\n"
    if photo_id:
        await message_obj.answer_photo(
            photo=photo_id,
            caption=f"{preview_msg}{text}" if len(preview_msg + text) <= 1024 else text,
            parse_mode="HTML",
            reply_markup=preview_kb.as_markup()
        )
    else:
        await message_obj.answer(
            f"{preview_msg}{text}",
            parse_mode="HTML",
            reply_markup=preview_kb.as_markup()
        )
    await state.set_state(None)

@dp.callback_query(F.data == "confirm_broadcast")
async def confirm_broadcast_cb(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    text = data.get('broadcast_text', '')
    photo_id = data.get('broadcast_photo')
    buttons = data.get("broadcast_buttons") or []

    send_kb = None
    if buttons:
        kb = InlineKeyboardBuilder()
        for button in buttons:
            kb.button(
                text=button["text"],
                url=button["url"],
                icon_custom_emoji_id=button.get("emoji"),
                style=button.get("style"),
            )
        send_kb = kb.as_markup()

    users = await fetchall("SELECT id FROM users WHERE accepted = 1")
    if not users:
        await call.message.edit_text("❌ Нет пользователей для рассылки.")
        await state.clear()
        return
    status_msg = await call.message.answer(f"⏳ Начинаю рассылку {len(users)} пользователям...")
    sent = 0
    failed = 0
    for idx, (user_id,) in enumerate(users):
        try:
            if photo_id:
                await get_active_bot().send_photo(user_id, photo=photo_id, caption=text, parse_mode="HTML", reply_markup=send_kb)
            else:
                await get_active_bot().send_message(user_id, text, parse_mode="HTML", reply_markup=send_kb)
            sent += 1
            if idx > 0 and idx % 100 == 0:
                await status_msg.edit_text(f"📊 Прогресс: {idx}/{len(users)}\n✅ Отправлено: {sent}\n❌ Ошибок: {failed}")
            await asyncio.sleep(0.05)
        except Exception as e:
            failed += 1
            logger.error(f"Ошибка отправки пользователю {user_id}: {e}")
    await status_msg.edit_text(f"✅ Рассылка завершена.\nОтправлено: {sent}\nОшибок: {failed}")
    await state.clear()
    await call.answer()

@dp.callback_query(F.data == "cancel_broadcast")
async def cancel_broadcast_cb(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await call.message.edit_text("❌ Рассылка отменена.")
    await call.answer()

# ═══════════════════════════════════════════════════════════════════════════════
# ЗАГРУЗКА ТОВАРОВ ЧЕРЕЗ .TXT
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "admin_add_stock_txt")
async def admin_add_stock_txt_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    categories = await fetchall("SELECT id, name FROM categories")
    if not categories:
        await call.message.edit_text("❌ Нет категорий.")
        return
    kb = InlineKeyboardBuilder()
    for cat_id, name in categories:
        kb.button(text=f"[{cat_id}] {name}", callback_data=f"txt_cat_{cat_id}")
    kb.adjust(1)
    await call.message.edit_text(
        "📄 <b>Загрузка товаров из .txt</b>\n\nВыберите категорию:",
        reply_markup=kb.as_markup(), parse_mode="HTML"
    )
    await state.set_state(AdminState.add_stock_txt_cat_id)
    await call.answer()

@dp.callback_query(F.data.startswith("txt_cat_"), AdminState.add_stock_txt_cat_id)
async def admin_add_stock_txt_cat(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    try:
        cat_id = int(call.data.split("_")[2])
    except Exception:
        await call.answer("❌ Ошибка")
        return
    cat = await fetchone("SELECT id, name FROM categories WHERE id = ?", (cat_id,))
    if not cat:
        await call.answer("❌ Категория не найдена")
        return
    await state.update_data(txt_cat_id=cat_id, txt_cat_name=cat[1])
    await state.set_state(AdminState.add_stock_txt_file)
    await call.message.edit_text(
        f"📄 <b>Категория: {cat[1]}</b>\n\n"
        f"Отправьте .txt файл, где <b>каждая строка — один товар</b>.\n\n"
        f"<i>Пустые строки будут пропущены автоматически.</i>",
        parse_mode="HTML"
    )
    await call.answer()

@dp.message(AdminState.add_stock_txt_file)
async def admin_add_stock_txt_file(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.document:
        await message.answer("❌ Пожалуйста, отправьте .txt файл документом.")
        return
    doc = message.document
    if not doc.file_name or not doc.file_name.lower().endswith('.txt'):
        await message.answer("❌ Файл должен быть в формате .txt")
        return
    if doc.file_size and doc.file_size > 5 * 1024 * 1024:
        await message.answer("❌ Файл слишком большой (максимум 5 МБ).")
        return
    data = await state.get_data()
    cat_id = data['txt_cat_id']
    cat_name = data['txt_cat_name']
    status_msg = await message.answer("⏳ Читаю файл...")
    try:
        active_bot = get_active_bot()
        file = await active_bot.get_file(doc.file_id)
        file_path = file.file_path
        file_url = f"https://api.telegram.org/file/bot{active_bot.token}/{file_path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                raw_bytes = await resp.read()
        try:
            raw_text = raw_bytes.decode('utf-8')
        except UnicodeDecodeError:
            raw_text = raw_bytes.decode('cp1251', errors='replace')
        lines = raw_text.splitlines()
        items = [line.strip() for line in lines if line.strip()]
        if not items:
            await status_msg.edit_text("❌ Файл пустой или не содержит валидных строк.")
            await state.clear()
            return
        if len(items) > MAX_BULK_ADD:
            await status_msg.edit_text(
                f"❌ В файле {len(items)} строк, максимум {MAX_BULK_ADD}.\n"
                f"Разбейте файл на части."
            )
            await state.clear()
            return
        await status_msg.edit_text(f"⏳ Найдено {len(items)} товаров. Сохраняю в базу данных...")
        items_to_insert = [(cat_id, item) for item in items]
        await executemany("INSERT INTO inventory (cat_id, data) VALUES (?, ?)", items_to_insert)
        await status_msg.edit_text(
            f"✅ <b>Готово!</b>\n\n"
            f"📦 Категория: <b>{cat_name}</b>\n"
            f"➕ Добавлено товаров: <b>{len(items)} шт.</b>\n\n"
            f"<i>Первый товар: <code>{items[0][:60]}</code></i>",
            parse_mode="HTML"
        )
        logger.info(f"Admin {message.from_user.id} uploaded {len(items)} items to category {cat_id} via txt")
    except Exception as e:
        logger.error(f"Ошибка при загрузке txt файла: {e}")
        await status_msg.edit_text(f"❌ Ошибка при обработке файла: {e}")
    await state.clear()

# ═══════════════════════════════════════════════════════════════════════════════
# ПРОМОКОДЫ — СОЗДАНИЕ
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "admin_create_promo")
async def admin_create_promo_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 Фиксированная сумма (USDT)", callback_data="promo_type_fixed")
    kb.button(text="📊 Процентная скидка (%)", callback_data="promo_type_percent")
    kb.adjust(1)
    await call.message.edit_text(
        "🎫 <b>Создание промокода</b>\n\nВыберите тип промокода:",
        reply_markup=kb.as_markup(), parse_mode="HTML"
    )
    await state.set_state(AdminState.create_promo_type)
    await call.answer()

@dp.callback_query(F.data.startswith("promo_type_"))
async def admin_create_promo_type(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    promo_type = call.data.split("_")[2]
    await state.update_data(promo_type=promo_type)
    await state.set_state(AdminState.create_promo_code)
    type_text = "фиксированную сумму в USDT" if promo_type == "fixed" else "процент скидки (1–100)"
    await call.message.edit_text(f"🎫 Введите код промокода (буквы и цифры):\n\nТип: {type_text}")
    await call.answer()

@dp.message(AdminState.create_promo_code)
async def admin_create_promo_code(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    code = message.text.strip().upper()
    if not code.replace('_', '').replace('-', '').isalnum():
        await message.answer("❌ Код может содержать только буквы, цифры, _ и -")
        return
    existing = await fetchone("SELECT code FROM promo_codes WHERE code = ?", (code,))
    if existing:
        await message.answer("❌ Промокод с таким кодом уже существует.")
        return
    await state.update_data(code=code)
    data = await state.get_data()
    promo_type = data.get('promo_type', 'fixed')
    await state.set_state(AdminState.create_promo_value)
    if promo_type == 'fixed':
        await message.answer("🎫 Введите сумму начисления (USDT):\nПример: 10.5")
    else:
        await message.answer("🎫 Введите процент скидки (1–100):\nПример: 15")

@dp.message(AdminState.create_promo_value)
async def admin_create_promo_value(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    promo_type = data.get('promo_type', 'fixed')
    try:
        if promo_type == 'fixed':
            value = round(float(message.text.replace(',', '.')), 2)
            if value <= 0:
                raise ValueError
            value_text = f"{value} USDT"
        else:
            value = round(float(message.text.replace(',', '.')), 1)
            if value <= 0 or value > 100:
                await message.answer("❌ Процент должен быть от 1 до 100.")
                return
            value_text = f"{value}%"
    except Exception:
        await message.answer("❌ Введите корректное число.")
        return
    await state.update_data(promo_value=value)
    await state.set_state(AdminState.create_promo_limit)
    await message.answer(f"🎫 Введите максимальное количество использований:\n\nЗначение: {value_text}")

@dp.message(AdminState.create_promo_limit)
async def admin_create_promo_limit(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        limit = int(message.text)
        if limit <= 0:
            raise ValueError
    except Exception:
        await message.answer("❌ Введите положительное целое число.")
        return
    data = await state.get_data()
    code = data['code']
    promo_type = data['promo_type']
    value = data['promo_value']
    await execute_query(
        "INSERT INTO promo_codes (code, amount, promo_type, max_uses) VALUES (?, ?, ?, ?)",
        (code, value, promo_type, limit), commit=True
    )
    type_text = "сумму" if promo_type == 'fixed' else "скидку"
    value_text = f"{value} USDT" if promo_type == 'fixed' else f"{value}%"
    await message.answer(
        f"✅ <b>Промокод создан!</b>\n\n"
        f"📝 Код: <code>{code}</code>\n"
        f"🎯 Тип: {type_text}\n"
        f"💰 Значение: {value_text}\n"
        f"📊 Лимит: {limit}",
        parse_mode="HTML"
    )
    await state.clear()

# ═══════════════════════════════════════════════════════════════════════════════
# ВЫДАЧА БАЛАНСА
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "admin_give_balance")
async def admin_give_balance_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminState.give_balance_user_id)
    await call.message.edit_text("💰 Введите ID пользователя:")
    await call.answer()

@dp.message(AdminState.give_balance_user_id)
async def admin_give_balance_user(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(message.text)
    except Exception:
        await message.answer("❌ Введите число.")
        return
    user_exists = await fetchone("SELECT id FROM users WHERE id = ?", (user_id,))
    if not user_exists:
        await message.answer("❌ Пользователь не найден.")
        await state.clear()
        return
    await state.update_data(target_user_id=user_id)
    await state.set_state(AdminState.give_balance_amount)
    await message.answer("💰 Введите сумму (может быть отрицательной для списания):")

@dp.message(AdminState.give_balance_amount)
async def admin_give_balance_amount(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        amount = round(float(message.text.replace(',', '.')), 2)
    except Exception:
        await message.answer("❌ Введите число.")
        return
    data = await state.get_data()
    user_id = data['target_user_id']
    await update_balance(user_id, amount, "admin_give", ADMIN_ID)
    await message.answer(f"✅ Баланс пользователя {user_id} изменён на {amount} USDT.")
    await state.clear()

# ═══════════════════════════════════════════════════════════════════════════════
# ДОБАВЛЕНИЕ ТОВАРА (поштучно)
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "admin_add_stock")
async def admin_add_stock_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminState.add_stock_cat_id)
    await call.message.edit_text("📦 Введите ID категории:")
    await call.answer()

@dp.message(AdminState.add_stock_cat_id)
async def admin_add_stock_cat(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        cat_id = int(message.text)
    except Exception:
        await message.answer("❌ Введите число.")
        return
    cat = await fetchone("SELECT id, name FROM categories WHERE id = ?", (cat_id,))
    if not cat:
        await message.answer("❌ Категория не найдена.")
        await state.clear()
        return
    await state.update_data(cat_id=cat_id, cat_name=cat[1])
    await state.set_state(AdminState.add_stock_count)
    await message.answer(
        f"📦 <b>Категория: {cat[1]}</b>\n\nСколько товаров хотите добавить? (1–{MAX_BULK_ADD})",
        parse_mode="HTML"
    )

@dp.message(AdminState.add_stock_count)
async def admin_add_stock_count(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        count = int(message.text)
        if count < 1 or count > MAX_BULK_ADD:
            await message.answer(f"❌ Введите число от 1 до {MAX_BULK_ADD}.")
            return
    except Exception:
        await message.answer("❌ Введите число.")
        return
    await state.update_data(total_count=count, current_index=0, items=[])
    await state.set_state(AdminState.add_stock_data)
    await message.answer(f"📦 Товар #1 из {count}\n\nВведите данные товара:", parse_mode="HTML")

@dp.message(AdminState.add_stock_data)
async def admin_add_stock_data(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    cat_id = data['cat_id']
    total_count = data['total_count']
    current_index = data.get('current_index', 0)
    items = data.get('items', [])
    items.append(message.text)
    current_index += 1
    if current_index < total_count:
        await state.update_data(current_index=current_index, items=items)
        await message.answer(f"✅ Товар #{current_index} добавлен!\n\nТовар #{current_index + 1} из {total_count}\nВведите данные:")
    else:
        await message.answer(f"⏳ Сохраняю {total_count} товаров...")
        items_to_insert = [(cat_id, item) for item in items]
        await executemany("INSERT INTO inventory (cat_id, data) VALUES (?, ?)", items_to_insert)
        await message.answer(
            f"✅ <b>Готово!</b>\n\nДобавлено: {total_count} шт.\nКатегория: {data.get('cat_name', str(cat_id))}",
            parse_mode="HTML"
        )
        logger.info(f"Admin added {total_count} items to category {cat_id}")
        await state.clear()

# ═══════════════════════════════════════════════════════════════════════════════
# ИЗМЕНЕНИЕ ЦЕНЫ
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "admin_change_price")
async def admin_change_price_start(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    categories = await fetchall("SELECT id, name FROM categories")
    if not categories:
        await call.message.edit_text("❌ Нет категорий.")
        return
    kb = InlineKeyboardBuilder()
    for cat_id, name in categories:
        kb.button(text=name, callback_data=f"change_price_cat_{cat_id}")
    kb.adjust(1)
    await call.message.edit_text("💰 Выберите категорию:", reply_markup=kb.as_markup())
    await call.answer()

@dp.callback_query(F.data.startswith("change_price_cat_"))
async def admin_change_price_cat(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    try:
        cat_id = int(call.data.split("_")[3])
    except Exception:
        await call.answer("❌ Ошибка")
        return
    await state.update_data(change_cat_id=cat_id)
    await state.set_state(AdminState.change_price_value)
    await call.message.answer("💰 Введите новую цену в USDT:")
    await call.answer()

@dp.message(AdminState.change_price_value)
async def admin_change_price_value(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        new_price = float(message.text.replace(',', '.'))
        if new_price <= 0:
            raise ValueError
    except Exception:
        await message.answer("❌ Введите положительное число.")
        return
    data = await state.get_data()
    cat_id = data['change_cat_id']
    await execute_query("UPDATE categories SET price = ? WHERE id = ?", (new_price, cat_id), commit=True)
    await message.answer(f"✅ Цена обновлена на {new_price} USDT.")
    await state.clear()

# ═══════════════════════════════════════════════════════════════════════════════
# ПРЕДЗАКАЗЫ (АДМИН)
# ═══════════════════════════════════════════════════════════════════════════════

@dp.callback_query(F.data == "admin_preorders")
async def admin_preorders_cb(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    preorders = await fetchall("""
        SELECT p.id, p.user_id, u.username, c.name, p.quantity, p.total, p.created_at, p.paid_at, p.status
        FROM preorders p
        JOIN categories c ON p.cat_id = c.id
        LEFT JOIN users u ON p.user_id = u.id
        ORDER BY CASE p.status WHEN 'paid' THEN 1 WHEN 'pending' THEN 2 ELSE 3 END, p.created_at DESC
        LIMIT 50
    """)
    if not preorders:
        await call.message.edit_text("📦 Нет предзаказов.")
        return
    paid = [p for p in preorders if p[8] == 'paid']
    pending = [p for p in preorders if p[8] == 'pending']
    other = [p for p in preorders if p[8] not in ('paid', 'pending')]
    text = f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CLOCK}">🕞</tg-emoji> <b>Управление предзаказами</b>\n\n'
    if paid:
        text += f'✅ <b>Оплаченные (ожидают выдачи):</b>\n'
        for pid, uid, username, cat_name, qty, total, created, paid_at, status in paid[:10]:
            u = f"@{username}" if username else f"ID:{uid}"
            text += f"   #{pid} | {u} | {cat_name} x{qty} | {total} USDT\n"
        if len(paid) > 10:
            text += f"   ... и еще {len(paid) - 10}\n"
        text += "\n"
    if pending:
        text += f'⏳ <b>Ожидают оплаты:</b>\n'
        for pid, uid, username, cat_name, qty, total, created, paid_at, status in pending[:5]:
            u = f"@{username}" if username else f"ID:{uid}"
            text += f"   #{pid} | {u} | {cat_name} x{qty} | {total} USDT\n"
        if len(pending) > 5:
            text += f"   ... и еще {len(pending) - 5}\n"
        text += "\n"
    if other:
        text += f'❌ <b>Просроченные/Завершенные:</b> {len(other)}\n\n'
    text += f'📊 <b>Итого:</b> всего {len(preorders)}, ждут выдачи: {len(paid)}, ждут оплаты: {len(pending)}'
    kb = InlineKeyboardBuilder()
    if paid:
        kb.button(text="✅ Выдать предзаказы", callback_data="admin_complete_preorders", icon_custom_emoji_id=CustomEmoji.CHECKMARK)
    kb.button(text="🔄 Обновить", callback_data="admin_preorders")
    kb.button(text="Назад", callback_data="back_to_admin", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    kb.adjust(1)
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await call.answer()

@dp.callback_query(F.data == "admin_complete_preorders")
async def admin_complete_preorders_cb(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    preorders = await fetchall("""
        SELECT p.id, p.user_id, p.cat_id, p.quantity, p.total, c.name, u.username
        FROM preorders p
        JOIN categories c ON p.cat_id = c.id
        LEFT JOIN users u ON p.user_id = u.id
        WHERE p.status = 'paid'
        ORDER BY p.created_at ASC
    """)
    if not preorders:
        await call.answer("📦 Нет оплаченных предзаказов", show_alert=True)
        return
    text = '✅ <b>Оплаченные предзаказы:</b>\n\n'
    for pid, uid, cat_id, qty, total, cat_name, username in preorders[:20]:
        u = f"@{username}" if username else f"ID:{uid}"
        text += f"<b>#{pid}</b> - {cat_name} x{qty} ({total} USDT) | {u}\n"
    if len(preorders) > 20:
        text += f"\n... и еще {len(preorders) - 20}\n"
    text += "\nИспользуйте <code>/complete_preorder &lt;id&gt;</code> для выдачи."
    kb = InlineKeyboardBuilder()
    kb.button(text="Назад", callback_data="admin_preorders", icon_custom_emoji_id=CustomEmoji.BACK, style='danger')
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await call.answer()

@dp.message(Command("complete_preorder"))
async def cmd_complete_preorder(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Использование: /complete_preorder <preorder_id>")
        return
    try:
        preorder_id = int(args[1])
    except ValueError:
        await message.answer("❌ Введите число.")
        return
    preorder = await fetchone("""
        SELECT p.user_id, p.cat_id, p.quantity, p.total, c.name, p.status
        FROM preorders p JOIN categories c ON p.cat_id = c.id WHERE p.id = ?
    """, (preorder_id,))
    if not preorder:
        await message.answer(f"❌ Предзаказ #{preorder_id} не найден.")
        return
    user_id, cat_id, quantity, total, cat_name, status = preorder
    if status != 'paid':
        await message.answer(f"❌ Статус предзаказа: '{status}'. Выдать можно только оплаченные.")
        return
    stock = await fetchone("SELECT COUNT(*) FROM inventory WHERE cat_id = ?", (cat_id,))
    stock_count = stock[0] if stock else 0
    if stock_count < quantity:
        await message.answer(f"❌ Товара не хватает! В наличии: {stock_count}, нужно: {quantity}")
        return
    items = await buy_items_with_transaction(cat_id, quantity, user_id, 0)
    if not items:
        await message.answer("❌ Ошибка при выдаче товара")
        return
    await execute_query("UPDATE preorders SET status = 'completed' WHERE id = ?", (preorder_id,), commit=True)
    res_text = (
        f'✅ <b>Ваш предзаказ выполнен!</b>\n\n'
        f'📦 Товар: {cat_name}\n'
        f'🔢 Количество: {quantity} шт.\n\n'
        f'🎁 Данные товара:\n'
    )
    for _, i_data in items:
        res_text += f"• {hcode(i_data)}\n"
    try:
        await get_active_bot().send_message(user_id, res_text, parse_mode="HTML")
        await message.answer(f"✅ Предзаказ #{preorder_id} выдан!")
    except Exception as e:
        await message.answer(f"⚠️ Выдан, но не удалось отправить сообщение: {e}")
    logger.info(f"Admin {message.from_user.id} completed preorder #{preorder_id} for user {user_id}")

# ═══════════════════════════════════════════════════════════════════════════════
# СТАТИСТИКА
# ═══════════════════════════════════════════════════════════════════════════════

@dp.message(Command("userstats"))
async def show_user_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        total_users = await fetchone("SELECT COUNT(*) FROM users")
        accepted_users = await fetchone("SELECT COUNT(*) FROM users WHERE accepted = 1")
        banned_users = await fetchone("SELECT COUNT(*) FROM users WHERE is_banned = 1")
        # subscribed_users = await fetchone("SELECT COUNT(*) FROM users WHERE subscribed = 1")  # если добавили поле
        
        # Новые пользователи за сегодня
        today = datetime.now().strftime("%Y-%m-%d")
        new_today = await fetchone(
            "SELECT COUNT(*) FROM users WHERE DATE(created_at) = ?",
            (today,)
        )
        
        # Активные пользователи за сегодня (если есть поле last_activity)
        active_today = await fetchone(
            "SELECT COUNT(*) FROM users WHERE DATE(last_activity) = ?",
            (today,)
        )
        
        text = (
            f'📊 <b>Статистика бота</b>\n\n'
            f"👥 Всего пользователей: {total_users[0] if total_users else 0}\n"
            f"✅ Приняли соглашение: {accepted_users[0] if accepted_users else 0}\n"
            f"🚫 Заблокировано: {banned_users[0] if banned_users else 0}\n"
            f"📈 Новых сегодня: {new_today[0] if new_today else 0}\n"
            f"🟢 Активных сегодня: {active_today[0] if active_today else 0}\n\n"
            f"📢 <b>Для рассылки:</b>\n"
            f"Всего получателей: {total_users[0] if total_users else 0}"
        )
        
        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.message(Command("userinfo"))
async def show_user_info(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("❌ Использование: /userinfo <user_id>")
        return
    try:
        target_user_id = int(args[1])
    except ValueError:
        await message.answer("❌ Введите число.")
        return
    try:
        user_data = await fetchone("SELECT id, username, total, referrer_id, is_banned, ban_reason FROM users WHERE id = ?", (target_user_id,))
        balance = await get_balance(target_user_id)
        preorders = await fetchall(
            "SELECT id, cat_id, quantity, total, status FROM preorders WHERE user_id = ? ORDER BY id DESC",
            (target_user_id,)
        )
        withdraws = await fetchall(
            "SELECT id, amount, status, created_at FROM withdraw_requests WHERE user_id = ? ORDER BY id DESC LIMIT 5",
            (target_user_id,)
        )
        try:
            user = await get_active_bot().get_chat(target_user_id)
            tg_info = (
                f"🆔 ID: {user.id}\n"
                f"📛 Имя: {user.first_name or '—'}\n"
                f"🏷 Фамилия: {user.last_name or '—'}\n"
                f"🔗 Username: @{user.username if user.username else '—'}\n"
                f"⭐ Премиум: {'Да' if getattr(user, 'is_premium', False) else 'Нет'}\n\n"
            )
        except Exception as e:
            tg_info = f"⚠️ Не удалось получить данные Telegram: {e}\n\n"

        ban_status = ""
        if user_data and user_data[4]:
            ban_status = f"\n🚫 <b>ЗАБЛОКИРОВАН</b>\nПричина: {user_data[5] or 'не указана'}\n"

        totp_keys = await fetchall("SELECT id, name FROM totp_keys WHERE user_id = ?", (target_user_id,))
        totp_text = ""
        if totp_keys:
            totp_text = "\n🔐 <b>TOTP-ключи:</b>\n"
            for kid, kname in totp_keys:
                totp_text += f"   • {kname}\n"

        bot_info = (
            f"💰 Баланс: {balance} USDT\n"
            f"🛒 Покупок: {user_data[2] if user_data else 0}\n"
            f"🔗 Реферер: {user_data[3] if user_data and user_data[3] else 'Нет'}\n"
            f"{ban_status}\n"
            f"🕞 <b>Предзаказы:</b>\n"
        )
        if preorders:
            for pid, cat_id, qty, total, status in preorders[:10]:
                cat = await fetchone("SELECT name FROM categories WHERE id = ?", (cat_id,))
                cat_name = cat[0] if cat else "Неизвестно"
                emoji = {"pending": "⏳", "paid": "✅", "expired": "❌", "completed": "🎁"}.get(status, "❓")
                bot_info += f"   {emoji} #{pid} - {cat_name} x{qty} ({total} USDT)\n"
        else:
            bot_info += "   Нет предзаказов\n"
        if withdraws:
            bot_info += "\n💸 <b>Заявки на вывод:</b>\n"
            for wid, wamount, wstatus, wcreated in withdraws:
                emoji = {"pending": "⏳", "approved": "✅", "rejected": "❌"}.get(wstatus, "❓")
                bot_info += f"   {emoji} #{wid} — {wamount} USDT ({wcreated[:10]})\n"
        bot_info += totp_text
        await message.answer(f"<b>Информация о пользователе</b>\n\n{tg_info}{bot_info}", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer("✅ Действие отменено.")
    else:
        await message.answer("❌ Нет активных действий.")

@dp.message(Command("mypreorders"))
async def cmd_my_preorders(message: types.Message):
    preorders = await fetchall(
        "SELECT p.id, c.name, p.quantity, p.total, p.created_at, p.paid_at, p.status "
        "FROM preorders p JOIN categories c ON p.cat_id = c.id "
        "WHERE p.user_id = ? ORDER BY p.created_at DESC",
        (message.from_user.id,)
    )
    if not preorders:
        await message.answer(f'📦 У вас нет предзаказов.')
        return
    text = '🕞 <b>Ваши предзаказы:</b>\n\n'
    for pid, cat_name, qty, total, created, paid_at, status in preorders:
        status_map = {
            "pending": ("⏳", "Ожидает оплаты"),
            "paid": ("✅", "Оплачен, ожидает выдачи"),
            "expired": ("❌", "Просрочен"),
            "completed": ("🎁", "Выполнен"),
        }
        se, st = status_map.get(status, ("❓", "Неизвестно"))
        text += f"{se} <b>#{pid}</b> - {cat_name}\n"
        text += f"   📦 {qty} шт. | 💰 {total} USDT\n"
        text += f"   📅 {created[:10] if created else '—'}\n"
        if paid_at:
            text += f"   💳 Оплачен: {paid_at[:10]}\n"
        text += f"   {se} {st}\n\n"
    await message.answer(text, parse_mode="HTML")

@dp.callback_query(F.data == "back_to_profile")
async def back_to_profile_cb(call: types.CallbackQuery):
    await show_profile_with_image(call.from_user.id, call.message)
    await call.answer()

@dp.callback_query(F.data == "back_to_admin")
async def back_to_admin_cb(call: types.CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await state.clear()
    status_text = "🔴 Тех. работы ВКЛЮЧЕНЫ" if MAINTENANCE_MODE else "🟢 Бот работает в штатном режиме"
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(
        f"🔧 <b>Панель администратора</b>\n\nСтатус: {status_text}\n\nВыберите действие:",
        reply_markup=build_admin_keyboard(),
        parse_mode="HTML"
    )
    await call.answer()

# --- ДОБАВЛЕНИЕ ЧЕРЕЗ /addstock ---
@dp.message(Command("addstock"))
async def cmd_add_stock(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 3:
        await message.answer("❌ Использование: /addstock <cat_id> <количество>")
        return
    try:
        cat_id = int(args[1])
        count = int(args[2])
        if count < 1 or count > MAX_BULK_ADD:
            await message.answer(f"❌ Количество от 1 до {MAX_BULK_ADD}.")
            return
    except ValueError:
        await message.answer("❌ Неверный формат.")
        return
    cat = await fetchone("SELECT id, name FROM categories WHERE id = ?", (cat_id,))
    if not cat:
        await message.answer(f"❌ Категория {cat_id} не найдена.")
        return
    await message.answer(f"📦 <b>Категория: {cat[1]}</b>\n\nОтправляйте товары по одному.\nВведите /done для завершения.", parse_mode="HTML")
    if not hasattr(get_active_bot(), 'pending_stock_add'):
        get_active_bot().pending_stock_add = {}
    get_active_bot().pending_stock_add[message.from_user.id] = {
        'cat_id': cat_id, 'cat_name': cat[1], 'total_count': count, 'items': [], 'current_index': 0
    }

@dp.message(Command("done"))
async def cmd_done_add_stock(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    if not hasattr(get_active_bot(), 'pending_stock_add') or message.from_user.id not in get_active_bot().pending_stock_add:
        await message.answer("❌ Нет активного процесса. Используйте /addstock")
        return
    data = get_active_bot().pending_stock_add[message.from_user.id]
    cat_id = data['cat_id']
    items = data['items']
    if not items:
        await message.answer("❌ Не добавлено ни одного товара.")
        del get_active_bot().pending_stock_add[message.from_user.id]
        return
    await message.answer(f"⏳ Сохраняю {len(items)} товаров...")
    items_to_insert = [(cat_id, item) for item in items]
    await executemany("INSERT INTO inventory (cat_id, data) VALUES (?, ?)", items_to_insert)
    await message.answer(f"✅ Добавлено: {len(items)} шт. в категорию {data['cat_name']}", parse_mode="HTML")
    logger.info(f"Admin added {len(items)} items to category {cat_id}")
    del get_active_bot().pending_stock_add[message.from_user.id]

@dp.message()
async def handle_add_stock_items(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    if not hasattr(get_active_bot(), 'pending_stock_add') or message.from_user.id not in get_active_bot().pending_stock_add:
        return
    if message.text and message.text.startswith('/'):
        return
    data = get_active_bot().pending_stock_add[message.from_user.id]
    items = data['items']
    total_count = data['total_count']
    items.append(message.text)
    get_active_bot().pending_stock_add[message.from_user.id]['items'] = items
    if len(items) < total_count:
        await message.answer(f"✅ #{len(items)} добавлен! Осталось: {total_count - len(items)}. Или /done для завершения.")
    else:
        await message.answer(f"✅ Все {len(items)} товаров получены. Введите /done для сохранения.")


# ПРОВЕРКА ПЛАТЕЖЕЙ @xRocket / Telegram Stars / Balance

# Обработчик для проверки оплаты товара (xRocket)
@dp.callback_query(F.data.startswith("check_payment_"))
async def check_payment_cb(call: types.CallbackQuery):
    # Извлекаем invoice_id как строку (без преобразования в int)
    try:
        invoice_id = call.data.split("_")[2]
    except IndexError:
        await call.answer("❌ Ошибка в данных", show_alert=True)
        return

    # Проверяем, есть ли платеж в ожидании (ключ – строка)
    payment_data = pending_payments.get(invoice_id)
    if not payment_data:
        # Возможно, ключ сохранён как int? Проверим оба варианта
        try:
            invoice_id_int = int(invoice_id)
            payment_data = pending_payments.get(invoice_id_int)
        except ValueError:
            payment_data = None
        if not payment_data:
            await call.answer("ℹ️ Счёт не найден или уже обработан.", show_alert=True)
            return
        else:
            invoice_id = invoice_id_int  # используем int, если нашли

    user_id = payment_data['user_id']
    if user_id != call.from_user.id:
        await call.answer("❌ Это не ваш платёж.", show_alert=True)
        return

    provider = payment_data.get('provider', 'xrocket')
    cat_id = payment_data['cat_id']
    quantity = payment_data['quantity']
    total = payment_data['total']
    is_preorder = payment_data.get('is_preorder', False)
    preorder_id = payment_data.get('preorder_id')

    await call.answer("⏳ Проверяю статус оплаты...")

    if provider == "xrocket":
        inv = await xrocket_get_invoice(str(invoice_id))
        if not inv.get('ok'):
            await call.answer("⚠️ Ошибка при проверке платежа", show_alert=True)
            return
        is_paid = _xrocket_is_paid(inv.get('status'), inv.get('paid_amount'))
        is_expired = _xrocket_is_expired(inv.get('status'))
        logger.info(f"xRocket check: invoice_id={invoice_id}, status={inv.get('status')}, paid_amount={inv.get('paid_amount')}, is_paid={is_paid}, is_expired={is_expired}")
    if is_paid:
        # Платёж подтверждён
        if is_preorder:
            if preorder_id:
                await execute_query("UPDATE preorders SET status = 'paid', paid_at = ? WHERE id = ?",
                                  (datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), preorder_id), commit=True)
            await call.message.edit_text(
                f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CHECK}">✅</tg-emoji> <b>Предзаказ оплачен!</b>\n\n'
                f'Как только товар появится, он будет автоматически выдан вам.',
                parse_mode="HTML"
            )
            await call.answer("✅ Предзаказ оплачен!", show_alert=True)
        else:
            items = await buy_items_with_transaction(cat_id, quantity, user_id, total)
            if not items:
                await call.message.edit_text(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Товар закончился во время оплаты. Обратитесь в поддержку.', parse_mode="HTML")
                await call.answer("❌ Товар закончился", show_alert=True)
                return
            res_text = f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CHECK}">✅</tg-emoji> Оплата подтверждена!\n\n<tg-emoji emoji-id="{CustomEmoji.PREORDER_BOX}">🎁</tg-emoji> Ваш товар:\n'
            for _, i_data in items:
                res_text += f"• `{i_data}`\n"
            await call.message.edit_text(res_text, parse_mode="Markdown")
            await call.answer("✅ Оплата подтверждена!", show_alert=True)
            referrer = await fetchone("SELECT referrer_id FROM users WHERE id = ?", (user_id,))
            if referrer and referrer[0]:
                ref_bonus = round(total * 0.1, 2)
                await add_referral_earning(referrer[0], ref_bonus, user_id)
                await get_active_bot().send_message(referrer[0], f'<tg-emoji emoji-id="{CustomEmoji.MONEY}">💰</tg-emoji> Вы получили {ref_bonus} USDT (10%) от покупки!', parse_mode="HTML")
        # Удаляем запись
        if invoice_id in pending_payments:
            del pending_payments[invoice_id]
    elif is_expired:
        await call.message.edit_text(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Счёт просрочен. Создайте новый заказ.', parse_mode="HTML")
        if invoice_id in pending_payments:
            del pending_payments[invoice_id]
        await call.answer("❌ Счёт просрочен", show_alert=True)
    else:
        # Не оплачен и не просрочен – оставляем запись
        await call.answer("💳 Оплата пока не обнаружена. Счёт активен.", show_alert=True)
        # НЕ удаляем запись


# Обработчик для проверки пополнения баланса
@dp.callback_query(F.data.startswith("check_balance_payment_"))
async def check_balance_payment_cb(call: types.CallbackQuery):
    try:
        invoice_id = call.data.split("_")[3]  # строка
    except IndexError:
        await call.answer("❌ Ошибка в данных", show_alert=True)
        return

    payment_data = pending_balance_payments.get(invoice_id)
    if not payment_data:
        try:
            invoice_id_int = int(invoice_id)
            payment_data = pending_balance_payments.get(invoice_id_int)
        except ValueError:
            payment_data = None
        if not payment_data:
            await call.answer("ℹ️ Счёт не найден или уже обработан.", show_alert=True)
            return
        else:
            invoice_id = invoice_id_int

    user_id = payment_data['user_id']
    if user_id != call.from_user.id:
        await call.answer("❌ Это не ваш платёж.", show_alert=True)
        return

    amount = payment_data['amount']
    provider = payment_data.get('provider', 'xrocket')
    msg_to_edit = payment_data.get('msg')

    await call.answer("⏳ Проверяю статус оплаты...")

    if provider == "xrocket":
        inv = await xrocket_get_invoice(str(invoice_id))
        if not inv.get('ok'):
            await call.answer("⚠️ Ошибка при проверке платежа", show_alert=True)
            return
        is_paid = _xrocket_is_paid(inv.get('status'), inv.get('paid_amount'))
        is_expired = _xrocket_is_expired(inv.get('status'))
        logger.info(f"xRocket balance check: invoice_id={invoice_id}, status={inv.get('status')}, paid_amount={inv.get('paid_amount')}, is_paid={is_paid}, is_expired={is_expired}")
    if is_paid:
        await update_balance(user_id, amount, "deposit")
        del pending_balance_payments[invoice_id]
        try:
            await msg_to_edit.delete()
        except:
            pass
        await call.message.answer(f'<tg-emoji emoji-id="{CustomEmoji.PREORDER_CHECK}">✅</tg-emoji> Баланс успешно пополнен на {amount} USDT!', parse_mode="HTML")
        await call.answer("✅ Баланс пополнен!", show_alert=True)
    elif is_expired:
        await msg_to_edit.edit_text(f'<tg-emoji emoji-id="{CustomEmoji.WARNING}">❌</tg-emoji> Счёт просрочен. Попробуйте снова.', parse_mode="HTML")
        del pending_balance_payments[invoice_id]
        await call.answer("❌ Счёт просрочен", show_alert=True)
    else:
        await call.answer("💳 Оплата пока не обнаружена. Счёт активен.", show_alert=True)

@dp.callback_query(F.data.startswith("cancel_balance_payment_"))
async def cancel_balance_payment_cb(call: types.CallbackQuery, state: FSMContext):
    invoice_id = call.data.removeprefix("cancel_balance_payment_")
    payment_data = pending_balance_payments.get(invoice_id)
    if payment_data is None:
        try:
            payment_data = pending_balance_payments.get(int(invoice_id))
        except ValueError:
            payment_data = None
    if not payment_data:
        await call.answer("Пополнение уже отменено или обработано.", show_alert=True)
        return
    if payment_data["user_id"] != call.from_user.id:
        await call.answer("❌ Это не ваше пополнение.", show_alert=True)
        return
    pending_balance_payments.pop(invoice_id, None)
    try:
        pending_balance_payments.pop(int(invoice_id), None)
    except ValueError:
        pass
    await state.clear()
    await call.message.delete()
    await text_deposit(call.message, state)
    await call.answer("Пополнение отменено.")

# ═══════════════════════════════════════════════════════════════════════════════
# ЗАПУСК
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    logger.info("Starting bot...")
    webapp_runner = None
    try:
        await init_db()
        await setup_catalog()
        webapp_runner = await start_webapp_server()
        asyncio.create_task(cleanup_old_payments())
        if not hasattr(bot, 'user_promos'):
            bot.user_promos = {}
        await bot.set_my_commands(BOT_COMMANDS)
        await bot.delete_webhook(drop_pending_updates=True)
        await _load_saved_mirrors()
        logger.info("Bot started successfully!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise
    finally:
        logger.info("Shutting down...")
        if webapp_runner:
            await webapp_runner.cleanup()
        for user_id in list(mirror_bots):
            await _stop_mirror(user_id)
        await bot.session.close()
        await close_db()
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Bot stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
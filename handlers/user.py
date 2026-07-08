from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message

from config import OWNER_ID
from database import queries

router = Router()


def _content_preview(message: Message) -> str:
    if message.text:
        return message.text[:200]
    if message.caption:
        return f"[media] {message.caption[:200]}"
    if message.photo:
        return "[rasm]"
    if message.video:
        return "[video]"
    if message.voice:
        return "[ovozli xabar]"
    if message.video_note:
        return "[video xabar]"
    if message.document:
        return f"[fayl] {message.document.file_name or ''}"
    if message.sticker:
        return "[stiker]"
    return "[xabar]"


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    source_code = command.args

    if message.from_user.id == OWNER_ID:
        await message.answer(
            "👋 Salom, bu sizning anonim xabarlar botingiz.\n\n"
            "Foydalanuvchilar xabar yozganda ular sizga shu yerga keladi.\n"
            "Ularga reply qilish uchun ularning xabariga oddiy Telegram-reply qiling.\n\n"
            "Komandalar:\n"
            "/newsource <kod> <nom> — yangi manba link yaratish\n"
            "/sources — barcha manbalar statistikasi"
        )
        return

    await queries.upsert_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        source_code=source_code,
    )

    await message.answer(
        "👋 Salom!\n\n"
        "Bu yerga istalgan savol, fikr yoki xabaringizni yozishingiz mumkin — "
        "u to'liq anonim tarzda yetkaziladi.\n\n"
        "✍️ Xabaringizni yozing:"
    )


@router.message(F.chat.type == "private")
async def handle_incoming_message(message: Message, bot: Bot):
    if message.from_user.id == OWNER_ID:
        return

    source_code = await queries.get_user_last_source(message.from_user.id)

    sent = await bot.copy_message(
        chat_id=OWNER_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id,
    )

    source_label = source_code or "noma'lum"
    info_text = (
        f"📩 <b>Yangi anonim xabar</b>\n"
        f"👤 {message.from_user.first_name or ''} "
        f"(@{message.from_user.username or 'username yoʻq'})\n"
        f"🆔 <code>{message.from_user.id}</code>\n"
        f"📍 Manba: <b>{source_label}</b>\n\n"
        f"↩️ Javob berish uchun shu xabarga (yoki yuqoridagi nusxaga) reply qiling."
    )

    await bot.send_message(
        chat_id=OWNER_ID,
        text=info_text,
        reply_to_message_id=sent.message_id,
        parse_mode="HTML",
    )

    await queries.save_message(
        sender_telegram_id=message.from_user.id,
        sender_username=message.from_user.username,
        sender_first_name=message.from_user.first_name,
        source_code=source_code,
        user_message_id=message.message_id,
        owner_message_id=sent.message_id,
        content_preview=_content_preview(message),
    )

    await message.answer("✅ Xabaringiz yuborildi. Javob kelsa shu yerga keladi.")

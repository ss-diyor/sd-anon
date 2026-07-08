from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from config import OWNER_ID
from database import queries

router = Router()
router.message.filter(F.from_user.id == OWNER_ID)


@router.message(Command("newsource"))
async def cmd_newsource(message: Message, command: CommandObject):
    if not command.args:
        await message.answer(
            "Foydalanish: <code>/newsource kod Nom</code>\n"
            "Masalan: <code>/newsource bio Instagram bio</code>",
            parse_mode="HTML",
        )
        return

    parts = command.args.split(maxsplit=1)
    code = parts[0].lower().strip()
    label = parts[1] if len(parts) > 1 else code

    if not code.isalnum():
        await message.answer("⚠️ Kod faqat harf va raqamlardan iborat bo'lishi kerak (bo'sh joysiz).")
        return

    created = await queries.create_source(code, label)
    if not created:
        await message.answer(f"⚠️ <code>{code}</code> kodi allaqachon band.", parse_mode="HTML")
        return

    bot_info = await message.bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={code}"

    await message.answer(
        f"✅ Yangi manba yaratildi!\n\n"
        f"📍 Kod: <code>{code}</code>\n"
        f"🏷 Nom: {label}\n"
        f"🔗 Link: {link}",
        parse_mode="HTML",
    )


@router.message(Command("sources"))
async def cmd_sources(message: Message):
    rows = await queries.list_sources_with_stats()
    if not rows:
        await message.answer("Hali hech qanday manba yaratilmagan. /newsource bilan yarating.")
        return

    bot_info = await message.bot.get_me()
    lines = ["📊 <b>Manbalar statistikasi</b>\n"]
    for r in rows:
        link = f"https://t.me/{bot_info.username}?start={r['code']}"
        lines.append(
            f"📍 <b>{r['label']}</b> (<code>{r['code']}</code>)\n"
            f"   ✉️ {r['message_count']} ta xabar\n"
            f"   🔗 {link}\n"
        )

    await message.answer("\n".join(lines), parse_mode="HTML")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    stats = await queries.get_stats_summary()
    await message.answer(
        f"📈 <b>Umumiy statistika</b>\n\n"
        f"✉️ Jami xabarlar: {stats['total']}\n"
        f"↩️ Javob berilgan: {stats['replied']}\n"
        f"👥 Unikal foydalanuvchilar: {stats['unique_senders']}",
        parse_mode="HTML",
    )


@router.message(Command("whois"))
async def cmd_whois(message: Message):
    if not message.reply_to_message:
        await message.answer(
            "ℹ️ Xabar yuboruvchisini bilish uchun o'sha xabarga (yoki uning nusxasiga) "
            "reply qilib <code>/whois</code> deb yozing.",
            parse_mode="HTML",
        )
        return

    replied_to_id = message.reply_to_message.message_id
    record = await queries.get_message_by_owner_msg_id(replied_to_id)
    if not record:
        await message.answer(
            "⚠️ Bu xabar uchun ma'lumot topilmadi. "
            "Iltimos, foydalanuvchi yuborgan xabarning o'ziga (nusxasiga) reply qiling."
        )
        return

    username = record["sender_username"]
    username_text = f"@{username}" if username else "username yoʻq"
    first_name = record["sender_first_name"] or "-"
    source_label = record["source_code"] or "noma'lum"
    sent_at = record["sent_at"].strftime("%Y-%m-%d %H:%M")
    replied_mark = "✅ ha" if record["replied"] else "❌ yo'q"

    await message.answer(
        f"👤 <b>Yuboruvchi ma'lumotlari</b>\n\n"
        f"Ism: {first_name}\n"
        f"Username: {username_text}\n"
        f"🆔 ID: <code>{record['sender_telegram_id']}</code>\n"
        f"📍 Manba: <b>{source_label}</b>\n"
        f"🕒 Yuborilgan: {sent_at}\n"
        f"↩️ Javob berilgan: {replied_mark}",
        parse_mode="HTML",
    )


@router.message(F.reply_to_message)
async def handle_owner_reply(message: Message, bot: Bot):
    replied_to_id = message.reply_to_message.message_id

    record = await queries.get_message_by_owner_msg_id(replied_to_id)
    if not record:
        return

    try:
        await bot.copy_message(
            chat_id=record["sender_telegram_id"],
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            reply_to_message_id=record["user_message_id"],
        )
        await queries.mark_replied(record["id"])
        await message.answer("✅ Javob yuborildi.")
    except Exception as e:
        await message.answer(f"⚠️ Javob yuborilmadi (foydalanuvchi botni bloklagan bo'lishi mumkin).\n{e}")

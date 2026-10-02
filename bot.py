"""
4000 Essential English Words - Interactive Telegram Bot
Featuring:
- Interactive in-place window navigation (@Jonylearningbot style)
- Multiple vocabulary learning methods (Flashcards with flip, 4-choice Quiz, Spelling, Audio Listening)
- 1v1 Battle with Friends (via deep links) & vs Bot AI
- Detailed Statistics, Progress Bar, Daily Streak & Leaderboards
- Instant search in English and Uzbek
- Bot Chat Menu button (🎓 Jony Academy) and standard commands
"""
import os
import sys

# Configure UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import uuid
import random
import logging
from typing import Dict

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import database as db
import keyboards as kb
from config import BOT_TOKEN, BOOKS_INFO
import tunnel_manager

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Active sessions in memory:
active_quizzes: Dict[str, dict] = {}
active_battles: Dict[str, dict] = {}
user_spelling_sessions: Dict[int, dict] = {} # user_id -> spelling_data

def format_word_card(word: dict, is_starred: bool, is_known: bool) -> str:
    """Formats an interactive flashcard for a word."""
    b_id = word["book_id"]
    u_num = word["unit_number"]
    w_idx = word["word_index"]
    
    star_badge = " ⭐ [Saqlangan]" if is_starred else ""
    known_badge = " ✅ [Yodlangan]" if is_known else ""

    w = word["word"].capitalize()
    pro = word.get("phonetic", "")
    pos = word.get("part_of_speech_uz") or word.get("part_of_speech", "")
    tr = word.get("translation_uz", "").capitalize()
    definition = word.get("definition", "")
    example = word.get("example", "")

    text = (
        f"📖 *Book {b_id}* | *Unit {u_num}* | So'z: *{w_idx}/20*{star_badge}{known_badge}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🔤 *{w}*  `{pro}`\n"
        f"📌 *Turkumi:* _{pos}_\n"
        f"🇺🇿 *Tarjimasi:* *{tr}*\n\n"
        f"💡 *Ta'rif:* \n_{definition}_\n\n"
        f"📝 *Misol:* \n_{example}_\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )
    return text

# ==================== COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /start command, including battle deep-linking."""
    user = update.effective_user
    await db.ensure_user(user.id, user.first_name, user.username)

    # Check for deep-linking arguments (e.g. /start battle_xxxx)
    args = context.args
    if args and len(args) > 0 and args[0].startswith("battle_"):
        battle_id = args[0].replace("battle_", "").strip()
        battle = await db.get_battle(battle_id)
        if battle:
            if battle["status"] == "waiting" and battle["player1_id"] != user.id:
                # Join battle
                joined = await db.join_battle(battle_id, user.id, user.first_name)
                if joined:
                    # Notify Player 1
                    try:
                        p1_text = (
                            f"⚔️ *Raqib topildi!*\n\n"
                            f"👤 *{user.first_name}* jangga qo'shildi!\n"
                            f"5 ta tezkor savol beriladi. Jang boshlandi! 🚀"
                        )
                        q0 = joined["questions"][0]
                        p1_msg = await context.bot.send_message(
                            chat_id=joined["player1_id"],
                            text=f"{p1_text}\n\n1-Savol:\n{q0['question']}",
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=kb.battle_question_kb(battle_id, 0, q0["options"])
                        )
                    except Exception as e:
                        logger.error(f"Error notifying player 1: {e}")

                    # Notify Player 2
                    p2_text = (
                        f"⚔️ *Battle boshlandi!*\n\n"
                        f"Siz *{joined['player1_name']}* bilan 1v1 bellashuvdasiz!\n"
                        f"5 ta tezkor savol beriladi. Omad tilaymiz! 🎯\n\n"
                        f"1-Savol:\n{joined['questions'][0]['question']}"
                    )
                    await update.message.reply_text(
                        p2_text,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=kb.battle_question_kb(battle_id, 0, joined["questions"][0]["options"])
                    )
                    return
            elif battle["player1_id"] == user.id:
                await update.message.reply_text("Bu siz yaratgan jang xonasi. Do'stingiz qo'shilishini kuting!")
                return
            else:
                await update.message.reply_text("Ushbu jang xonasi to'lgan yoki yakunlangan.")

    safe_name = (user.first_name or "O'quvchi").replace("*", "").replace("_", " ").replace("`", "").replace("[", "")
    stats = await db.get_user_stats(user.id)
    web_url = tunnel_manager.get_web_app_url()
    browser_link = f"🌐 *Kompyuter brauzerida to'liq ochish:* [Ushbu havolani bosing]({web_url})\n\n" if web_url and web_url.startswith("https://") else ""

    welcome_text = (
        f"👋 *Assalomu alaykum, {safe_name}!*\n\n"
        f"📚 *4000 Essential English Words* interaktiv ta'lim akademiyasiga xush kelibsiz!\n\n"
        f"Paul Nation'ning 6 ta kitobi, 180 ta uniti va barcha 3600 ta so'zini zamonaviy usullarda o'rganing:\n\n"
        f"🏆 *Sizning darajangiz:* {stats['level_title']}\n"
        f"📊 *Progress:* `[{stats['progress_bar']}]` *{stats['progress_pct']}%*\n"
        f"• ⭕ Yodlangan: *{stats['learned_count']}* / {stats['total_words']} ta\n"
        f"• 🔥 Kunlik streak: *{stats['streak_days']}* kun\n"
        f"• ⚔️ Battle reytingi: *{stats['battle_rating']}* ball ({stats['battles_won']}G' / {stats['battles_lost']}M)\n"
        f"• 🎯 Test aniqligi: *{stats['accuracy']}%*\n\n"
        f"{browser_link}"
        f"👇 Kerakli bo'limni tanlang yoki pastdagi *🎓 4000 Academy* tugmasini bosing:"
    )

    if update.message:
        try:
            await update.message.reply_text(
                "Asosiy menyu:",
                reply_markup=kb.persistent_reply_kb()
            )
        except Exception as e:
            logger.error(f"Error sending persistent keyboard: {e}")

        try:
            await update.message.reply_text(
                welcome_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=kb.main_menu_inline_kb()
            )
        except Exception as e:
            logger.error(f"Markdown send error in start_command: {e}")
            clean_text = welcome_text.replace("*", "").replace("`", "").replace("[", "").replace("]", "")
            await update.message.reply_text(
                clean_text,
                reply_markup=kb.main_menu_inline_kb()
            )
    elif update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                welcome_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=kb.main_menu_inline_kb()
            )
        except Exception as e:
            clean_text = welcome_text.replace("*", "").replace("`", "").replace("[", "").replace("]", "")
            await update.callback_query.edit_message_text(
                clean_text,
                reply_markup=kb.main_menu_inline_kb()
            )

async def learn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /learn command."""
    books = await db.get_books()
    text = (
        f"📚 *4000 Essential English Words - Kitoblar:*\n\n"
        f"Kerakli kitobni tanlang:\n\n"
        f"🟢 *Book 1 (A2)* - Boshlang'ich (Elementary)\n"
        f"🟡 *Book 2 (B1)* - O'rta-quyi (Pre-Intermediate)\n"
        f"🟠 *Book 3 (B1+)* - O'rta (Intermediate)\n"
        f"🔵 *Book 4 (B2)* - O'rtadan yuqori (Upper-Intermediate)\n"
        f"🟣 *Book 5 (B2+)* - Yuqori (Advanced)\n"
        f"🔴 *Book 6 (C1)* - Professional (Proficiency)\n"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.books_kb(books))
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.books_kb(books))

async def practice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /practice command."""
    text = (
        f"🎯 *So'z yodlash usullari (Practice Hub):*\n\n"
        f"O'zingizga qulay o'rganish usulini tanlang:\n\n"
        f"🗂 *1. Flashcard usuli* — Kartochkani aylantirib, o'zbekcha ma'nosi va misolini ko'rish.\n"
        f"🧠 *2. 4-Variantli Test* — Qiziqarli ko'p variantli tezkor viktorina.\n"
        f"✍️ *3. Yozma Mashq (Spelling)* — So'zni to'g'ri yozish orqali xotirada muhrlash.\n"
        f"🔊 *4. Audio Listening* — Native audio talaffuzni eshitib, so'zni aniqlash.\n"
        f"⚔️ *5. Bellashuv (Battle)* — Do'stingiz yoki Bot AI bilan 1v1 bilimlar jangi!\n"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.practice_menu_kb())
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.practice_menu_kb())

async def battle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /battle command."""
    user = update.effective_user
    stats = await db.get_user_stats(user.id)
    text = (
        f"⚔️ *Do'stlar bilan 1v1 Battle (Bellashuv)!*\n\n"
        f"Ingliz tili so'z boyligingizni do'stlaringiz bilan sinang!\n\n"
        f"👤 *Sizning jang statistikangiz:*\n"
        f"• Reyting: ⭐ *{stats['battle_rating']}* ball\n"
        f"• G'alabalar: 🏆 *{stats['battles_won']}* ta\n"
        f"• Mag'lubiyatlar: ❌ *{stats['battles_lost']}* ta\n\n"
        f"Quyidagilardan birini tanlang:"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.battle_menu_kb())
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.battle_menu_kb())

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays detailed user stats with leaderboard button."""
    user = update.effective_user
    stats = await db.get_user_stats(user.id)
    text = (
        f"📊 *Foydalanuvchi profili va statistikasi:*\n\n"
        f"👤 *Ism:* {user.first_name}\n"
        f"🏅 *Daraja:* {stats['level_title']}\n"
        f"🔥 *Kunlik streak:* {stats['streak_days']} kun davom etmoqda!\n\n"
        f"📚 *Lug'at boyligi:*\n"
        f"Progress: `[{stats['progress_bar']}]` *{stats['progress_pct']}%*\n"
        f"• Yodlangan so'zlar: *{stats['learned_count']}* / {stats['total_words']} ta\n"
        f"• Saqlangan (yulduzcha): *{stats['bookmarks_count']}* ta\n\n"
        f"🧠 *Testlar:*\n"
        f"• Topshirilgan: *{stats['total_quizzes']}* ta\n"
        f"• To'g'ri javoblar: *{stats['correct_answers']}* ta\n"
        f"• Aniqlik: *{stats['accuracy']}%*\n\n"
        f"⚔️ *1v1 Battle reytingi:*\n"
        f"• Reyting: *{stats['battle_rating']}* ball\n"
        f"• G'alabalar: *{stats['battles_won']}* | Mag'lubiyatlar: *{stats['battles_lost']}*\n"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.leaderboard_kb())
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.leaderboard_kb())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /help command."""
    help_text = (
        f"ℹ️ *4000 Essential English Words boti qo'llanmasi:*\n\n"
        f"📚 */learn* - 6 ta kitob va 180 ta unitdan birini tanlab o'rganish.\n"
        f"🎯 */practice* - 5 xil so'z yodlash usuli (Flashcard, Quiz, Spelling, Audio, Battle).\n"
        f"⚔️ */battle* - Do'stingizga havola yuboring va 1v1 bellashuv o'tkazing!\n"
        f"📊 */stats* - Shaxsiy yutuqlaringiz, kunlik streak va reytingingiz.\n"
        f"🔍 */search* - Istalgan so'zni inglizcha yoki o'zbekcha yozib qidiring.\n"
        f"🎓 *Jony Academy* - Pastdagi ko'k tugma orqali to'liq mini-appni oching.\n\n"
        f"Har kuni 15-20 daqiqa shug'ullanib, so'z boyligingizni yangi darajaga olib chiqing! 🚀"
    )
    if update.message:
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.main_menu_inline_kb())
    elif update.callback_query:
        await update.callback_query.edit_message_text(help_text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.main_menu_inline_kb())

# ==================== CALLBACK QUERY ROUTER ====================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main callback query dispatcher."""
    query = update.callback_query
    data = query.data
    user = query.from_user
    await db.ensure_user(user.id, user.first_name, user.username)

    try:
        # Navigation
        if data == "main_menu":
            await query.answer()
            await start_command(update, context)
            return

        if data == "view_help":
            await query.answer()
            await help_command(update, context)
            return

        if data == "view_stats":
            await query.answer()
            await stats_command(update, context)
            return

        if data == "view_books":
            await query.answer()
            await learn_command(update, context)
            return

        if data == "practice_menu":
            await query.answer()
            await practice_command(update, context)
            return

        if data == "battle_menu":
            await query.answer()
            await battle_command(update, context)
            return

        # Book selected -> Show Units
        if data.startswith("book_"):
            await query.answer()
            b_id = int(data.split("_")[1])
            b_info = BOOKS_INFO.get(b_id, {})
            text = (
                f"📚 *{b_info.get('title', f'Book {b_id}')}*\n"
                f"🎯 Daraja: *{b_info.get('cefr', '')}*\n"
                f"📝 {b_info.get('desc', '')}\n\n"
                f"O'rganish uchun kerakli *Unit*ni tanlang (1-30):"
            )
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.units_kb(b_id, page=0))
            return

        # Units pagination
        if data.startswith("units_page_"):
            await query.answer()
            parts = data.split("_")
            b_id = int(parts[2])
            page = int(parts[3])
            b_info = BOOKS_INFO.get(b_id, {})
            text = f"📚 *{b_info.get('title', f'Book {b_id}')}*\n\nO'rganish uchun *Unit*ni tanlang (1-30):"
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.units_kb(b_id, page=page))
            return

        # Unit menu
        if data.startswith("unit_"):
            await query.answer()
            parts = data.split("_")
            b_id = int(parts[1])
            u_num = int(parts[2])
            unit = await db.get_unit(b_id, u_num)
            u_title = unit["title"] if unit else f"Unit {u_num}"
            text = (
                f"📖 *Book {b_id} | Unit {u_num}*\n"
                f"🏷 *Mavzu:* {u_title}\n"
                f"🔢 *So'zlar soni:* 20 ta yangi so'z\n\n"
                f"Nimani boshlamoqchisiz?"
            )
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.unit_menu_kb(b_id, u_num))
            return

        # Word list for unit
        if data.startswith("wordlist_"):
            await query.answer()
            parts = data.split("_")
            b_id = int(parts[1])
            u_num = int(parts[2])
            words = await db.get_unit_words(b_id, u_num)
            
            text_lines = [f"📋 *Book {b_id} | Unit {u_num} so'zlari:*\n"]
            for w in words:
                idx = w["word_index"]
                word_text = w["word"].capitalize()
                tr = w.get("translation_uz", "")
                text_lines.append(f"*{idx}.* `{word_text}` - {tr}")
            
            text_lines.append("\n_So'zlarni bittalab o'rganish uchun quyidagi tugmani bosing:_")
            text = "\n".join(text_lines)
            kb_list = [
                [kb.InlineKeyboardButton("🗂 1-so'zdan boshlash", callback_data=f"word_{b_id}_{u_num}_1")],
                [kb.InlineKeyboardButton("🔙 Unit menyusi", callback_data=f"unit_{b_id}_{u_num}")]
            ]
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.InlineKeyboardMarkup(kb_list))
            return

        # Reading Story
        if data.startswith("story_"):
            await query.answer()
            parts = data.split("_")
            b_id = int(parts[1])
            u_num = int(parts[2])
            unit = await db.get_unit(b_id, u_num)
            u_title = unit["title"] if unit else f"Unit {u_num}"
            story = unit.get("story", "") if unit else "_Hikoya yuklanmoqda..._"
            text = (
                f"📖 *Book {b_id} | Unit {u_num}: {u_title}*\n"
                f"━━━━━━━━━━━━━━━━━━━\n\n"
                f"{story}\n\n"
                f"━━━━━━━━━━━━━━━━━━━"
            )
            back_kb = kb.InlineKeyboardMarkup([
                [kb.InlineKeyboardButton("🗂 Unit so'zlarini o'rganish", callback_data=f"word_{b_id}_{u_num}_1")],
                [kb.InlineKeyboardButton("🔙 Unit menyusi", callback_data=f"unit_{b_id}_{u_num}")]
            ])
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_kb)
            return

        # Word card
        if data.startswith("word_"):
            await query.answer()
            parts = data.split("_")
            b_id = int(parts[1])
            u_num = int(parts[2])
            w_idx = int(parts[3])
            
            word = await db.get_word_by_index(b_id, u_num, w_idx)
            if not word:
                await query.answer("So'z topilmadi!", show_alert=True)
                return
                
            is_starred = await db.is_bookmarked(user.id, word["id"])
            is_known = await db.is_learned(user.id, word["id"])
            card_text = format_word_card(word, is_starred, is_known)
            reply_markup = kb.word_card_kb(b_id, u_num, w_idx, word["id"], is_starred, is_known)
            await query.edit_message_text(card_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            return

        # View word by ID
        if data.startswith("view_word_id_"):
            await query.answer()
            word_id = int(data.split("_")[3])
            word = await db.get_word(word_id)
            if not word:
                await query.answer("So'z topilmadi!", show_alert=True)
                return
            is_starred = await db.is_bookmarked(user.id, word["id"])
            is_known = await db.is_learned(user.id, word["id"])
            card_text = format_word_card(word, is_starred, is_known)
            reply_markup = kb.word_card_kb(word["book_id"], word["unit_number"], word["word_index"], word["id"], is_starred, is_known, from_bookmark=True)
            await query.edit_message_text(card_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            return

        # Audio
        if data.startswith("audio_"):
            word_id = int(data.split("_")[1])
            word = await db.get_word(word_id)
            if not word or not word.get("audio_url"):
                await query.answer("Audio topilmadi.", show_alert=True)
                return
            await query.answer("🔊 Audio yuborilmoqda...")
            try:
                await context.bot.send_audio(
                    chat_id=query.message.chat_id,
                    audio=word["audio_url"],
                    title=word["word"].capitalize(),
                    performer=f"4000 Essential English Words - Book {word['book_id']}"
                )
            except Exception as e:
                logger.error(f"Error sending audio: {e}")
                await query.answer("Audioni yuborishda xatolik yuz berdi.", show_alert=True)
            return

        # Image
        if data.startswith("image_"):
            word_id = int(data.split("_")[1])
            word = await db.get_word(word_id)
            if not word or not word.get("image_url"):
                await query.answer("Rasm mavjud emas.", show_alert=True)
                return
            await query.answer("🖼 Rasm yuborilmoqda...")
            try:
                caption = f"🔤 *{word['word'].capitalize()}* - {word.get('translation_uz', '')}"
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=word["image_url"],
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Error sending photo: {e}")
                await query.answer("Rasmni yuklashda xatolik yuz berdi.", show_alert=True)
            return

        # Star toggle
        if data.startswith("toggle_star_"):
            parts = data.split("_")
            word_id = int(parts[2])
            b_id = int(parts[3])
            u_num = int(parts[4])
            w_idx = int(parts[5])
            
            is_now_starred = await db.toggle_bookmark(user.id, word_id)
            is_known = await db.is_learned(user.id, word_id)
            msg = "⭐ Lug'atga saqlandi!" if is_now_starred else "❌ Lug'atdan chiqarildi!"
            await query.answer(msg)
            word = await db.get_word(word_id)
            card_text = format_word_card(word, is_now_starred, is_known)
            reply_markup = kb.word_card_kb(b_id, u_num, w_idx, word_id, is_now_starred, is_known)
            await query.edit_message_text(card_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            return

        # Learned toggle
        if data.startswith("toggle_learned_"):
            parts = data.split("_")
            word_id = int(parts[2])
            b_id = int(parts[3])
            u_num = int(parts[4])
            w_idx = int(parts[5])
            
            is_now_known = await db.toggle_learned(user.id, word_id)
            is_starred = await db.is_bookmarked(user.id, word_id)
            msg = "✅ So'z yodlangan deb belgilandi! (+1)" if is_now_known else "⭕ Yodlanmagan holatga qaytarildi!"
            await query.answer(msg)
            word = await db.get_word(word_id)
            card_text = format_word_card(word, is_starred, is_now_known)
            reply_markup = kb.word_card_kb(b_id, u_num, w_idx, word_id, is_starred, is_now_known)
            await query.edit_message_text(card_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            return

        # Random word
        if data == "random_word":
            await query.answer()
            word = await db.get_random_word()
            if not word:
                await query.answer("So'zlar yuklanmoqda...", show_alert=True)
                return
            is_starred = await db.is_bookmarked(user.id, word["id"])
            is_known = await db.is_learned(user.id, word["id"])
            card_text = f"🎲 *Tasodifiy so'z:*\n\n" + format_word_card(word, is_starred, is_known)
            reply_markup = kb.word_card_kb(word["book_id"], word["unit_number"], word["word_index"], word["id"], is_starred, is_known, from_random=True)
            await query.edit_message_text(card_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
            return

        # Bookmarks
        if data.startswith("bookmarks_"):
            await query.answer()
            page = int(data.split("_")[1])
            bookmarks, total = await db.get_user_bookmarks(user.id, limit=6, offset=page * 6)
            if total == 0:
                text = (
                    "⭐ *Sizning lug'atingiz bo'sh!*\n\n"
                    "So'zlarni o'rganayotganda kartochkadagi *☆ Saqlash* tugmasini bossangiz, "
                    "ular shu yerda to'planadi."
                )
                await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.main_menu_inline_kb())
                return
            text = f"⭐ *Mening saqlangan so'zlarim ({total} ta):*\n\nKerakli so'z ustiga bosing:"
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.bookmarks_list_kb(bookmarks, page, total, page_size=6))
            return

        # Prompt search
        if data == "prompt_search":
            await query.answer()
            text = (
                "🔍 *So'z qidirish:*\n\n"
                "Istalgan inglizcha yoki o'zbekcha so'zni chatga yozib yuboring.\n"
                "Masalan: `agree` yoki `rozi` yoki `travel`"
            )
            back_kb = kb.InlineKeyboardMarkup([[kb.InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]])
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_kb)
            return

        # ================= PRACTICE MODES =================

        # 1. Interactive Flashcard Mode
        if data == "practice_flashcard":
            await query.answer()
            word = await db.get_random_word()
            if not word:
                await query.answer("So'zlar yuklanmoqda...", show_alert=True)
                return
            text = (
                f"🗂 *Interaktiv Flashcard (Old tomoni):*\n\n"
                f"🔤 *{word['word'].upper()}*  `{word.get('phonetic', '')}`\n\n"
                f"Ushbu so'zning ma'nosini eslashga harakat qiling, so'ng kartani aylantiring 👇"
            )
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.flashcard_interactive_kb(word["id"], is_flipped=False))
            return

        if data.startswith("fc_flip_"):
            await query.answer("🔄 Karta aylantirildi!")
            word_id = int(data.split("_")[2])
            word = await db.get_word(word_id)
            text = (
                f"🗂 *Interaktiv Flashcard (Orqa tomoni):*\n\n"
                f"🔤 *{word['word'].upper()}*  `{word.get('phonetic', '')}`\n"
                f"🇺🇿 *Tarjimasi:* *{word.get('translation_uz', '').capitalize()}*\n"
                f"📌 *Turkumi:* _{word.get('part_of_speech_uz') or word.get('part_of_speech')}_\n\n"
                f"💡 *Ta'rif:* _{word.get('definition')}_\n\n"
                f"📝 *Misol:* _{word.get('example')}_\n\n"
                f"So'zni bilar edingizmi?"
            )
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.flashcard_interactive_kb(word_id, is_flipped=True))
            return

        if data.startswith("fc_known_"):
            word_id = int(data.split("_")[2])
            await db.toggle_learned(user.id, word_id)
            await query.answer("🎉 Barakalla! So'z yodlandi deb belgilandi (+1)")
            # load next flashcard
            word = await db.get_random_word()
            text = (
                f"🗂 *Interaktiv Flashcard (Keyingi so'z):*\n\n"
                f"🔤 *{word['word'].upper()}*  `{word.get('phonetic', '')}`\n\n"
                f"Ushbu so'zning ma'nosini eslashga harakat qiling 👇"
            )
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.flashcard_interactive_kb(word["id"], is_flipped=False))
            return

        if data.startswith("fc_unknown_"):
            word_id = int(data.split("_")[2])
            await db.toggle_bookmark(user.id, word_id)
            await query.answer("⭐ So'z takrorlash uchun shaxsiy lug'atga saqlandi!")
            # load next flashcard
            word = await db.get_random_word()
            text = (
                f"🗂 *Interaktiv Flashcard (Keyingi so'z):*\n\n"
                f"🔤 *{word['word'].upper()}*  `{word.get('phonetic', '')}`\n\n"
                f"Ushbu so'zning ma'nosini eslashga harakat qiling 👇"
            )
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.flashcard_interactive_kb(word["id"], is_flipped=False))
            return

        # 3. Spelling Mode
        if data == "practice_spelling":
            await query.answer()
            sp_data = await db.get_spelling_question()
            if not sp_data:
                await query.answer("So'zlar yuklanmoqda...", show_alert=True)
                return
            user_spelling_sessions[user.id] = sp_data
            text = (
                f"✍️ *Yozma Mashq (Spelling):*\n\n"
                f"🇺🇿 *Ma'nosi:* {sp_data['translation_uz'].capitalize()}\n"
                f"💡 *Ta'rif:* _{sp_data['definition']}_\n\n"
                f"🔤 Harflar soni: *{sp_data['length']} ta*\n"
                f"Шаблон: `{sp_data['masked']}`\n\n"
                f"👇 Ushbu so'zni to'g'ri yozib, chatga yuboring:"
            )
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.spelling_kb(sp_data["word_id"], show_hint=False))
            return

        if data.startswith("spell_hint_"):
            await query.answer("💡 Maslahat!")
            word_id = int(data.split("_")[2])
            sp_data = user_spelling_sessions.get(user.id)
            if not sp_data:
                word = await db.get_word(word_id)
                w = word["word"]
                sp_data = {"word": w, "masked": w[0] + " " + " ".join(["_" for _ in range(len(w) - 2)]) + " " + w[-1], "example": word["example"], "translation_uz": word["translation_uz"]}
            text = (
                f"✍️ *Yozma Mashq (Maslahat bilan):*\n\n"
                f"🇺🇿 *Ma'nosi:* {sp_data['translation_uz'].capitalize()}\n"
                f"💡 *Misol gap:* _{sp_data.get('example', '')}_\n\n"
                f"🔤 Yashiringan so'z: `{sp_data['masked']}`\n\n"
                f"Chatga to'g'ri so'zni yuboring:"
            )
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.spelling_kb(word_id, show_hint=True))
            return

        if data.startswith("spell_reveal_"):
            word_id = int(data.split("_")[2])
            word = await db.get_word(word_id)
            await query.answer(f"To'g'ri so'z: {word['word'].upper()}")
            text = (
                f"👀 *To'g'ri javob:* *{word['word'].upper()}*  `{word.get('phonetic', '')}`\n\n"
                f"🇺🇿 *Tarjimasi:* {word.get('translation_uz', '').capitalize()}\n"
                f"💡 *Ta'rif:* _{word.get('definition')}_\n"
                f"📝 *Misol:* _{word.get('example')}_\n"
            )
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.spelling_kb(word_id, show_hint=True))
            return

        # 4. Listening Mode
        if data == "practice_listening":
            await query.answer("🔊 Audio yuklanmoqda...")
            l_data = await db.get_listening_question()
            if not l_data:
                await query.answer("Audio topilmadi.", show_alert=True)
                return
            # Send audio first
            try:
                await context.bot.send_audio(
                    chat_id=query.message.chat_id,
                    audio=l_data["audio_url"],
                    title="Audio Mashq",
                    performer="4000 Essential English Words"
                )
            except Exception as e:
                logger.error(f"Error sending audio: {e}")

            text = (
                f"🔊 *Audio Mashqi (Listening):*\n\n"
                f"Audioni tinglang va qaysi so'z aytilganini toping!\n"
                f"💡 *O'zbekcha ma'nosi:* {l_data['translation_uz']}\n\n"
                f"To'g'ri variantni tanlang:"
            )
            await query.message.reply_text(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=kb.listening_kb(l_data["word_id"], l_data["options"])
            )
            return

        if data.startswith("listen_ans_"):
            parts = data.split("_")
            word_id = int(parts[2])
            opt_idx = int(parts[3])
            word = await db.get_word(word_id)
            
            # Find chosen option from message
            reply_markup = query.message.reply_markup
            chosen_btn = reply_markup.inline_keyboard[opt_idx][0].text
            chosen_word = chosen_btn.split(") ")[1].strip().lower()
            
            if chosen_word == word["word"].lower():
                await query.answer("🎉 TO'G'RI! Qoyilmaqom!", show_alert=True)
                feedback = f"✅ *TO'G'RI JAVOB! Barakalla!*\n\n🔤 *{word['word'].upper()}* - {word['translation_uz']}"
            else:
                await query.answer("❌ Noto'g'ri!", show_alert=True)
                feedback = f"❌ *NOTO'G'RI!*\nTo'g'ri javob: ✅ *{word['word'].upper()}* - {word['translation_uz']}"

            text = (
                f"🔊 *Audio Mashqi Natijasi:*\n\n"
                f"{feedback}\n\n"
                f"💡 *Ta'rif:* _{word['definition']}_\n"
                f"📝 *Misol:* _{word['example']}_"
            )
            retry_kb = kb.InlineKeyboardMarkup([
                [kb.InlineKeyboardButton("🎲 Keyingi audio mashq ➡️", callback_data="practice_listening")],
                [kb.InlineKeyboardButton("🔙 Usullar menyusi", callback_data="practice_menu")]
            ])
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=retry_kb)
            return

        # ================= 1v1 BATTLE SYSTEM =================

        if data == "battle_create":
            await query.answer()
            battle_id = await db.create_battle(user.id, user.first_name, book_id=1)
            bot_info = await context.bot.get_me()
            invite_url = f"https://t.me/{bot_info.username}?start=battle_{battle_id}"
            text = (
                f"⚔️ *1v1 BATTLE XONASI YARATILDI!*\n\n"
                f"🆔 *Jang kodi:* `{battle_id}`\n"
                f"👤 *Tashkilotchi:* {user.first_name}\n"
                f"❓ *Savollar soni:* 5 ta tezkor savol\n\n"
                f"🔗 *Taklif havolasi:*\n`{invite_url}`\n\n"
                f"Do'stingizga quyidagi tugma orqali havolani yuboring. U havolani ochishi bilan jang boshlanadi!"
            )
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.battle_invite_kb(battle_id, bot_info.username))
            return

        if data.startswith("battle_check_"):
            battle_id = data.split("_")[2]
            battle = await db.get_battle(battle_id)
            if not battle:
                await query.answer("Jang topilmadi.", show_alert=True)
                return
            if battle["status"] == "active":
                await query.answer("⚔️ Raqib qo'shildi! Jang boshlanmoqda!")
                q0 = battle["questions"][0]
                text = (
                    f"⚔️ *Jang boshlandi!*\n"
                    f"👤 {battle['player1_name']} 🆚 {battle['player2_name']}\n\n"
                    f"1-Savol:\n{q0['question']}"
                )
                await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.battle_question_kb(battle_id, 0, q0["options"]))
            else:
                await query.answer("⏳ Raqib hali qo'shilmadi. Kutilmoqda...", show_alert=True)
            return

        # Battle vs Bot AI
        if data == "battle_vs_bot":
            await query.answer("🤖 Bot AI ga qarshi jang boshlanmoqda!")
            battle_id = str(uuid.uuid4())[:8]
            questions = await db.get_quiz_data_for_unit(random.randint(1, 6), random.randint(1, 30), num_questions=5)
            active_battles[battle_id] = {
                "user_id": user.id,
                "user_name": user.first_name,
                "user_score": 0,
                "bot_score": 0,
                "current_idx": 0,
                "questions": questions,
                "is_vs_bot": True
            }
            q0 = questions[0]
            text = (
                f"⚔️ *1v1 Jang: Siz 🆚 Smart Bot AI*\n"
                f"5 ta tezkor savol beriladi. Kim ko'p to'g'ri topsa, g'olib bo'ladi!\n\n"
                f"Savol 1/5:\n{q0['question']}"
            )
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.battle_question_kb(battle_id, 0, q0["options"]))
            return

        # Battle answer selected
        if data.startswith("bans_"):
            parts = data.split("_")
            battle_id = parts[1]
            q_idx = int(parts[2])
            opt_idx = int(parts[3])

            # Check if battle vs Bot AI
            if battle_id in active_battles and active_battles[battle_id].get("is_vs_bot"):
                b_session = active_battles[battle_id]
                q_data = b_session["questions"][q_idx]
                chosen = q_data["options"][opt_idx]
                if chosen.strip().lower() == q_data["correct_option"].strip().lower():
                    b_session["user_score"] += 1
                    user_correct = True
                else:
                    user_correct = False

                # Bot AI answers with 70% probability
                if random.random() < 0.7:
                    b_session["bot_score"] += 1

                next_q = q_idx + 1
                if next_q < len(b_session["questions"]):
                    q_next_data = b_session["questions"][next_q]
                    icon = "✅" if user_correct else "❌"
                    text = (
                        f"⚔️ *Jang davom etmoqda ({next_q + 1}/5):*\n\n"
                        f"Oldingi savol: {icon} (Siz: {b_session['user_score']} | Bot: {b_session['bot_score']})\n\n"
                        f"{q_next_data['question']}"
                    )
                    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.battle_question_kb(battle_id, next_q, q_next_data["options"]))
                else:
                    # Final result vs Bot AI
                    u_s = b_session["user_score"]
                    b_s = b_session["bot_score"]
                    if u_s > b_s:
                        res_title = "🏆 SIZ G'OLIB BO'LDINGIZ! Qoyilmaqom!"
                        await db.update_battle_ratings(None, user.id, 0)
                        rating_text = "+25 ball reytingingizga qo'shildi!"
                    elif u_s < b_s:
                        res_title = "❌ BOT AI G'OLIB BO'LDI! Keyingi safar albatta yutasiz!"
                        rating_text = "-15 ball"
                    else:
                        res_title = "🤝 DURRANG! Kuchlar teng keldi!"
                        rating_text = "+5 ball"

                    res_text = (
                        f"🏁 *BATTLE YAKUNLANDI!*\n\n"
                        f"{res_title}\n\n"
                        f"📊 *Yakuniy hisob:*\n"
                        f"👤 Siz: *{u_s} / 5* ball\n"
                        f"🤖 Bot AI: *{b_s} / 5* ball\n\n"
                        f"⭐ *Reyting o'zgarishi:* {rating_text}"
                    )
                    active_battles.pop(battle_id, None)
                    fin_kb = kb.InlineKeyboardMarkup([
                        [kb.InlineKeyboardButton("🔁 Yana jang qilish", callback_data="battle_vs_bot")],
                        [kb.InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
                    ])
                    await query.edit_message_text(res_text, parse_mode=ParseMode.MARKDOWN, reply_markup=fin_kb)
                return

            # Live 1v1 Battle with Friend
            battle = await db.get_battle(battle_id)
            if not battle:
                await query.answer("Jang topilmadi.", show_alert=True)
                return

            is_player1 = (user.id == battle["player1_id"])
            q_data = battle["questions"][q_idx]
            chosen = q_data["options"][opt_idx]
            is_correct = (chosen.strip().lower() == q_data["correct_option"].strip().lower())

            # Store player score
            score_key = f"{battle_id}_{user.id}_score"
            current_score = active_battles.get(score_key, 0)
            if is_correct:
                current_score += 1
            active_battles[score_key] = current_score

            next_q = q_idx + 1
            if next_q < len(battle["questions"]):
                q_next_data = battle["questions"][next_q]
                text = (
                    f"⚔️ *1v1 Battle | Savol {next_q + 1}/5*\n\n"
                    f"{q_next_data['question']}"
                )
                await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.battle_question_kb(battle_id, next_q, q_next_data["options"]))
            else:
                # Finished 5 questions
                player_num = 1 if is_player1 else 2
                await db.record_battle_result(battle_id, player_num, current_score)
                updated_b = await db.get_battle(battle_id)
                
                if updated_b["player1_done"] == 1 and updated_b["player2_done"] == 1:
                    # Both finished!
                    p1_s = updated_b["player1_score"]
                    p2_s = updated_b["player2_score"]
                    if p1_s > p2_s:
                        winner = updated_b["player1_name"]
                    elif p2_s > p1_s:
                        winner = updated_b["player2_name"]
                    else:
                        winner = "Durrang"

                    final_text = (
                        f"🏁 *1v1 JANG YAKUNLANDI!*\n\n"
                        f"🏆 *G'olib:* *{winner}*\n\n"
                        f"📊 *Natijalar:*\n"
                        f"• {updated_b['player1_name']}: *{p1_s} / 5* ball\n"
                        f"• {updated_b['player2_name']}: *{p2_s} / 5* ball\n\n"
                        f"G'olibga +25 ball reyting berildi! 🎯"
                    )
                    fin_kb = kb.InlineKeyboardMarkup([
                        [kb.InlineKeyboardButton("⚔️ Yangi jang boshlash", callback_data="battle_create")],
                        [kb.InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
                    ])
                    await query.edit_message_text(final_text, parse_mode=ParseMode.MARKDOWN, reply_markup=fin_kb)
                else:
                    wait_text = (
                        f"🏁 *Siz barcha 5 ta savolga javob berdingiz!*\n\n"
                        f"Sizning to'plagan ballingiz: *{current_score} / 5*\n\n"
                        f"⏳ Raqibingiz hali javob bermoqda. U tugatishi bilan yakuniy natija ko'rsatiladi!"
                    )
                    check_kb = kb.InlineKeyboardMarkup([
                        [kb.InlineKeyboardButton("🔄 Natijani tekshirish", callback_data=f"bcheck_fin_{battle_id}")],
                        [kb.InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
                    ])
                    await query.edit_message_text(wait_text, parse_mode=ParseMode.MARKDOWN, reply_markup=check_kb)
            return

        if data.startswith("bcheck_fin_"):
            battle_id = data.split("_")[2]
            updated_b = await db.get_battle(battle_id)
            if updated_b and updated_b["player1_done"] == 1 and updated_b["player2_done"] == 1:
                p1_s = updated_b["player1_score"]
                p2_s = updated_b["player2_score"]
                winner = updated_b["player1_name"] if p1_s > p2_s else (updated_b["player2_name"] if p2_s > p1_s else "Durrang")
                final_text = (
                    f"🏁 *1v1 JANG YAKUNLANDI!*\n\n"
                    f"🏆 *G'olib:* *{winner}*\n\n"
                    f"📊 *Natijalar:*\n"
                    f"• {updated_b['player1_name']}: *{p1_s} / 5* ball\n"
                    f"• {updated_b['player2_name']}: *{p2_s} / 5* ball\n"
                )
                fin_kb = kb.InlineKeyboardMarkup([
                    [kb.InlineKeyboardButton("⚔️ Yangi jang boshlash", callback_data="battle_create")],
                    [kb.InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")]
                ])
                await query.edit_message_text(final_text, parse_mode=ParseMode.MARKDOWN, reply_markup=fin_kb)
            else:
                await query.answer("⏳ Raqib hali yakunlamadi, bir oz kuting...", show_alert=True)
            return

        # ================= LEADERBOARD =================

        if data == "leaderboard_learners":
            await query.answer()
            top = await db.get_leaderboard_learners(10)
            text_lines = ["🏆 *TOP 10 — Eng ko'p so'z yodlaganlar:*\n"]
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            for i, u in enumerate(top):
                name = u["first_name"] or "Foydalanuvchi"
                cnt = u["learned_count"]
                badge = medals[i] if i < len(medals) else f"{i+1}."
                text_lines.append(f"{badge} *{name}* — {cnt} ta so'z")
            text = "\n".join(text_lines)
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.leaderboard_kb())
            return

        if data == "leaderboard_battlers":
            await query.answer()
            top = await db.get_leaderboard_battlers(10)
            text_lines = ["⚔️ *TOP 10 — Eng kuchli Battle jangchilari:*\n"]
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            for i, u in enumerate(top):
                name = u["first_name"] or "Jangchi"
                rating = u["battle_rating"]
                won = u["battles_won"]
                badge = medals[i] if i < len(medals) else f"{i+1}."
                text_lines.append(f"{badge} *{name}* — ⭐ *{rating}* ball ({won} g'alaba)")
            if len(top) == 0:
                text_lines.append("_Hozircha janglar o'tkazilmagan. Birinchi bo'lib do'stingizni jangga chaqiring!_")
            text = "\n".join(text_lines)
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.leaderboard_kb())
            return

        # ================= QUIZ ENGINE =================

        if data.startswith("quiz_start_"):
            await query.answer()
            parts = data.split("_")
            b_id = int(parts[2])
            u_num = int(parts[3])
            questions = await db.get_quiz_data_for_unit(b_id, u_num, num_questions=10)
            if not questions:
                await query.answer("Savollar topilmadi!", show_alert=True)
                return
            session_id = str(uuid.uuid4())[:8]
            active_quizzes[session_id] = {
                "book_id": b_id,
                "unit_num": u_num,
                "questions": questions,
                "current_idx": 0,
                "score": 0,
                "user_id": user.id,
            }
            await render_quiz_question(query, session_id, 0)
            return

        if data == "quick_quiz":
            await query.answer()
            books = await db.get_books()
            if not books:
                await query.answer("Yuklanmoqda...", show_alert=True)
                return
            b = random.choice(books)
            u_num = random.randint(1, 30)
            questions = await db.get_quiz_data_for_unit(b["id"], u_num, num_questions=10)
            if not questions:
                await query.answer("Savollar topilmadi!", show_alert=True)
                return
            session_id = str(uuid.uuid4())[:8]
            active_quizzes[session_id] = {
                "book_id": b["id"],
                "unit_num": u_num,
                "questions": questions,
                "current_idx": 0,
                "score": 0,
                "user_id": user.id,
            }
            await render_quiz_question(query, session_id, 0)
            return

        if data.startswith("qans_"):
            parts = data.split("_")
            session_id = parts[1]
            q_idx = int(parts[2])
            opt_idx = int(parts[3])
            
            session = active_quizzes.get(session_id)
            if not session or session["current_idx"] != q_idx:
                await query.answer("Test muddati o'tgan.", show_alert=True)
                return
                
            q_data = session["questions"][q_idx]
            chosen_opt = q_data["options"][opt_idx]
            is_correct = (chosen_opt.strip().lower() == q_data["correct_option"].strip().lower())
            
            if is_correct:
                session["score"] += 1
                await query.answer("✅ To'g'ri!")
                feedback_head = "🎉 *TO'G'RI JAVOB! Barakalla!*"
            else:
                await query.answer("❌ Noto'g'ri!")
                feedback_head = f"❌ *NOTO'G'RI!*\nSiz tanladingiz: _{chosen_opt}_\nTo'g'ri javob: ✅ *{q_data['correct_option']}*"
                
            total_q = len(session["questions"])
            is_last = (q_idx + 1 >= total_q)
            text = (
                f"🧠 *Test ({q_idx + 1}/{total_q})*\n\n"
                f"{feedback_head}\n\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"🔤 *{q_data['target_word'].capitalize()}*\n"
                f"💡 *Ta'rif:* _{q_data['definition']}_\n"
                f"📝 *Misol:* _{q_data['example']}_\n"
                f"━━━━━━━━━━━━━━━━━━━\n\n"
                f"Hozirgi ball: *{session['score']} / {q_idx + 1}*"
            )
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.quiz_feedback_kb(session_id, q_idx, is_last=is_last))
            return

        if data.startswith("qnext_"):
            await query.answer()
            parts = data.split("_")
            session_id = parts[1]
            next_idx = int(parts[2])
            session = active_quizzes.get(session_id)
            if not session:
                await query.answer("Test yakunlangan.", show_alert=True)
                return
            if next_idx >= len(session["questions"]):
                await finish_quiz(query, session, user)
                active_quizzes.pop(session_id, None)
                return
            session["current_idx"] = next_idx
            await render_quiz_question(query, session_id, next_idx)
            return

        if data.startswith("qstop_"):
            await query.answer("Test to'xtatildi.")
            session_id = data.split("_")[1]
            session = active_quizzes.pop(session_id, None)
            if session:
                await finish_quiz(query, session, user)
            else:
                await start_command(update, context)
            return

        if data == "noop":
            await query.answer()
            return

    except Exception as e:
        logger.error(f"Error handling callback {data}: {e}", exc_info=True)
        try:
            await query.answer("Xatolik yuz berdi.", show_alert=True)
        except Exception:
            pass

async def render_quiz_question(query, session_id: str, q_idx: int):
    session = active_quizzes[session_id]
    q_data = session["questions"][q_idx]
    total_q = len(session["questions"])
    text = (
        f"🧠 *Interaktiv Test | Savol {q_idx + 1}/{total_q}*\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"{q_data['question']}\n\n"
        f"Quyidagi variantlardan birini tanlang:"
    )
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.quiz_question_kb(session_id, q_idx, q_data["options"]))

async def finish_quiz(query, session: dict, user):
    score = session["score"]
    total = len(session["questions"])
    pct = round((score / total) * 100, 1) if total > 0 else 0
    await db.update_quiz_stats(user.id, score, total)
    
    if pct >= 90:
        comment = "🏆 A'lo daraja! So'zlarni mukammal bilasiz!"
    elif pct >= 70:
        comment = "👏 Juda yaxshi natija! Bir oz takrorlash bilan 100% ga erishasiz!"
    elif pct >= 50:
        comment = "👍 Qoniqarli! So'zlarni yana bir bor takrorlab chiqing."
    else:
        comment = "💪 Tushkunlikka tushmang! Qaytadan topshiring."

    b_id = session.get("book_id", 0)
    u_num = session.get("unit_num", 0)
    text = (
        f"🏁 *TEST YAKUNLANDI!*\n\n"
        f"📊 *Sizning natijangiz:*\n"
        f"• To'g'ri javoblar: *{score} / {total}*\n"
        f"• Aniqlik: *{pct}%*\n\n"
        f"{comment}\n\n"
        f"Natijangiz shaxsiy statistikangizga saqlandi! 🎯"
    )
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.quiz_completed_kb(b_id, u_num))

# ==================== TEXT MESSAGE HANDLER ====================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user = update.effective_user
    await db.ensure_user(user.id, user.first_name, user.username)

    # Check spelling session
    if user.id in user_spelling_sessions:
        sp_data = user_spelling_sessions[user.id]
        if text.lower() == sp_data["word"].lower():
            user_spelling_sessions.pop(user.id, None)
            await db.toggle_learned(user.id, sp_data["word_id"])
            success_text = (
                f"🎉 *QOYILMAQOM! TO'G'RI YOZINGIZ!*\n\n"
                f"🔤 *{sp_data['word'].upper()}*  `{sp_data.get('phonetic', '')}`\n"
                f"🇺🇿 *Tarjimasi:* {sp_data['translation_uz'].capitalize()}\n\n"
                f"So'z yodlangan deb belgilandi (+1)! 🎯"
            )
            next_kb = kb.InlineKeyboardMarkup([
                [kb.InlineKeyboardButton("✍️ Keyingi so'z ➡️", callback_data="practice_spelling")],
                [kb.InlineKeyboardButton("🔙 Usullar menyusi", callback_data="practice_menu")]
            ])
            await update.message.reply_text(success_text, parse_mode=ParseMode.MARKDOWN, reply_markup=next_kb)
            return

    # Reply keyboard navigation
    if text == "📚 Kitoblar":
        await learn_command(update, context)
        return

    if text == "🎯 Mashq qilish":
        await practice_command(update, context)
        return

    if text == "⚔️ Battle":
        await battle_command(update, context)
        return

    if text == "🎲 Tasodifiy so'z":
        word = await db.get_random_word()
        if not word:
            await update.message.reply_text("So'zlar yuklanmoqda...")
            return
        is_starred = await db.is_bookmarked(user.id, word["id"])
        is_known = await db.is_learned(user.id, word["id"])
        card_text = f"🎲 *Tasodifiy so'z:*\n\n" + format_word_card(word, is_starred, is_known)
        reply_markup = kb.word_card_kb(word["book_id"], word["unit_number"], word["word_index"], word["id"], is_starred, is_known, from_random=True)
        await update.message.reply_text(card_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        return

    if text == "⭐ Lug'atim":
        bookmarks, total = await db.get_user_bookmarks(user.id, limit=6, offset=0)
        if total == 0:
            msg = "⭐ *Sizning lug'atingiz bo'sh!*\n\nKartochkadagi *☆ Saqlash* tugmasini bosib so'zlarni saqlang."
            await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.main_menu_inline_kb())
            return
        msg = f"⭐ *Mening saqlangan so'zlarim ({total} ta):*\n\nKerakli so'z ustiga bosing:"
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=kb.bookmarks_list_kb(bookmarks, 0, total, page_size=6))
        return

    if text == "📊 Statistika":
        await stats_command(update, context)
        return

    if text == "ℹ️ Yordam":
        await help_command(update, context)
        return

    if text == "🔍 Qidiruv":
        await update.message.reply_text(
            "🔍 Qidirmoqchi bo'lgan so'zingizni inglizcha yoki o'zbekcha yozing:",
            reply_markup=kb.persistent_reply_kb()
        )
        return

    # Text Search in database
    results = await db.search_words(text, limit=8)
    if not results:
        await update.message.reply_text(
            f"❌ *\"{text}\"* bo'yicha hech narsa topilmadi.\nBoshqa so'z bilan qidirib ko'ring.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    found_text = f"🔍 *\"{text}\"* bo'yicha {len(results)} ta natija topildi:\nKerakli so'z ustiga bosing:"
    await update.message.reply_text(
        found_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=kb.search_results_kb(results)
    )

def build_application() -> Application:
    """Builds and configures Application."""
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("learn", learn_command))
    app.add_handler(CommandHandler("practice", practice_command))
    app.add_handler(CommandHandler("battle", battle_command))
    app.add_handler(CommandHandler("cards", lambda u, c: practice_command(u, c)))
    app.add_handler(CommandHandler("quiz", lambda u, c: start_command(u, c)))
    app.add_handler(CommandHandler("spelling", lambda u, c: practice_command(u, c)))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("search", lambda u, c: u.message.reply_text("🔍 So'z yozing:")))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", start_command))

    # Callbacks
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.error(f"Global bot error on update {update}: {context.error}")

    app.add_error_handler(global_error_handler)

    return app

if __name__ == "__main__":
    app = build_application()
    app.run_polling(drop_pending_updates=True)

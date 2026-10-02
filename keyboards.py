"""
Inline and Reply Keyboards for 4000 Essential English Words Telegram Bot
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import BOOKS_INFO
import tunnel_manager

def main_menu_inline_kb() -> InlineKeyboardMarkup:
    url = tunnel_manager.get_web_app_url()
    keyboard = []
    if url and url.startswith("https://"):
        keyboard.append([
            InlineKeyboardButton("🚀 Interaktiv Oyna (Mini App)", web_app=WebAppInfo(url=url)),
            InlineKeyboardButton("💻 PC Brauzerda", url=url)
        ])
    keyboard.extend([
        [
            InlineKeyboardButton("📚 Kitoblar (Books 1-6)", callback_data="view_books"),
            InlineKeyboardButton("🎯 Mashq qilish (Practice)", callback_data="practice_menu"),
        ],
        [
            InlineKeyboardButton("⚔️ Do'stlar bilan Battle", callback_data="battle_menu"),
            InlineKeyboardButton("🎲 Tasodifiy so'z", callback_data="random_word"),
        ],
        [
            InlineKeyboardButton("⭐ Lug'atim", callback_data="bookmarks_0"),
            InlineKeyboardButton("📊 Statistika & Reyting", callback_data="view_stats"),
        ],
        [
            InlineKeyboardButton("🔍 So'z qidirish", callback_data="prompt_search"),
            InlineKeyboardButton("ℹ️ Bot qo'llanmasi", callback_data="view_help"),
        ]
    ])
    return InlineKeyboardMarkup(keyboard)

def persistent_reply_kb() -> ReplyKeyboardMarkup:
    url = tunnel_manager.get_web_app_url()
    keyboard = []
    if url and url.startswith("https://"):
        keyboard.append([
            KeyboardButton("🚀 Interaktiv WebApp", web_app=WebAppInfo(url=url))
        ])
    keyboard.extend([
        ["📚 Kitoblar", "🎯 Mashq qilish"],
        ["⚔️ Battle", "🎲 Tasodifiy so'z"],
        ["⭐ Lug'atim", "📊 Statistika"],
        ["🔍 Qidiruv", "ℹ️ Yordam"]
    ])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def practice_menu_kb() -> InlineKeyboardMarkup:
    url = tunnel_manager.get_web_app_url()
    keyboard = []
    if url and url.startswith("https://"):
        keyboard.append([
            InlineKeyboardButton("🚀 Interaktiv Platformani Ochish", web_app=WebAppInfo(url=url))
        ])
    keyboard.extend([
        [
            InlineKeyboardButton("🗂 1. Flashcard usuli (Kartochkalar)", callback_data="practice_flashcard"),
        ],
        [
            InlineKeyboardButton("🧠 2. 4-Variantli Test (Quiz)", callback_data="quick_quiz"),
        ],
        [
            InlineKeyboardButton("✍️ 3. Yozma Mashq (Spelling)", callback_data="practice_spelling"),
        ],
        [
            InlineKeyboardButton("🔊 4. Audio / Listening mashqi", callback_data="practice_listening"),
        ],
        [
            InlineKeyboardButton("⚔️ 5. Bellashuv (Battle rejimi)", callback_data="battle_menu"),
        ],
        [
            InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")
        ]
    ])
    return InlineKeyboardMarkup(keyboard)

def flashcard_interactive_kb(word_id: int, is_flipped: bool = False) -> InlineKeyboardMarkup:
    keyboard = []
    if not is_flipped:
        keyboard.append([
            InlineKeyboardButton("🔄 Kartani aylantirish (Tarjimani ko'rish)", callback_data=f"fc_flip_{word_id}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("❌ Bilmayman", callback_data=f"fc_unknown_{word_id}"),
            InlineKeyboardButton("✅ Bilaman (+1)", callback_data=f"fc_known_{word_id}")
        ])
        keyboard.append([
            InlineKeyboardButton("🔊 Talaffuz", callback_data=f"audio_{word_id}"),
            InlineKeyboardButton("🖼 Rasm", callback_data=f"image_{word_id}")
        ])
        
    keyboard.append([
        InlineKeyboardButton("🎲 Keyingi kartochka ➡️", callback_data="practice_flashcard"),
        InlineKeyboardButton("🔙 Usullar menyusi", callback_data="practice_menu")
    ])
    return InlineKeyboardMarkup(keyboard)

def listening_kb(word_id: int, options: list) -> InlineKeyboardMarkup:
    keyboard = []
    letters = ["A", "B", "C", "D"]
    for i, opt in enumerate(options):
        letter = letters[i] if i < len(letters) else f"{i+1}"
        keyboard.append([
            InlineKeyboardButton(f"{letter}) {opt.capitalize()}", callback_data=f"listen_ans_{word_id}_{i}")
        ])
    keyboard.append([
        InlineKeyboardButton("🔊 Qayta tinglash", callback_data=f"audio_{word_id}"),
        InlineKeyboardButton("🎲 Keyingi mashq", callback_data="practice_listening")
    ])
    keyboard.append([
        InlineKeyboardButton("🔙 Usullar menyusi", callback_data="practice_menu")
    ])
    return InlineKeyboardMarkup(keyboard)

def spelling_kb(word_id: int, show_hint: bool = False) -> InlineKeyboardMarkup:
    keyboard = []
    if not show_hint:
        keyboard.append([
            InlineKeyboardButton("💡 Maslahat (Hint)", callback_data=f"spell_hint_{word_id}"),
            InlineKeyboardButton("👀 Javobni ko'rish", callback_data=f"spell_reveal_{word_id}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("👀 Javobni ko'rish", callback_data=f"spell_reveal_{word_id}")
        ])
        
    keyboard.append([
        InlineKeyboardButton("🎲 Keyingi so'z ➡️", callback_data="practice_spelling"),
        InlineKeyboardButton("🔙 Usullar menyusi", callback_data="practice_menu")
    ])
    return InlineKeyboardMarkup(keyboard)

def battle_menu_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("👥 Do'stni jangga chaqirish (1v1)", callback_data="battle_create"),
        ],
        [
            InlineKeyboardButton("🤖 Bot AI bilan bellashuv", callback_data="battle_vs_bot"),
        ],
        [
            InlineKeyboardButton("🏆 Battle Reytingi (TOP)", callback_data="leaderboard_battlers"),
            InlineKeyboardButton("📊 Mening janglarim", callback_data="view_stats"),
        ],
        [
            InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def battle_invite_kb(battle_id: str, bot_username: str) -> InlineKeyboardMarkup:
    invite_url = f"https://t.me/{bot_username}?start=battle_{battle_id}"
    share_text = f"⚔️ 4000 Essential English Words bilimlar jangiga tayyormisiz? Men bilan 1v1 bellashuvga kiring!"
    share_url = f"https://t.me/share/url?url={invite_url}&text={share_text}"
    
    keyboard = [
        [
            InlineKeyboardButton("📢 Do'stga jo'natish (Ulashish)", url=share_url)
        ],
        [
            InlineKeyboardButton("🔄 Raqibni kutish (Yangilash)", callback_data=f"battle_check_{battle_id}")
        ],
        [
            InlineKeyboardButton("❌ Jangni bekor qilish", callback_data="battle_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def battle_question_kb(battle_id: str, q_idx: int, options: list) -> InlineKeyboardMarkup:
    keyboard = []
    letters = ["A", "B", "C", "D"]
    for i, opt in enumerate(options):
        letter = letters[i] if i < len(letters) else f"{i+1}"
        keyboard.append([
            InlineKeyboardButton(f"{letter}) {opt}", callback_data=f"bans_{battle_id}_{q_idx}_{i}")
        ])
    return InlineKeyboardMarkup(keyboard)

def leaderboard_kb() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("📚 Eng ko'p so'z yodlaganlar", callback_data="leaderboard_learners"),
            InlineKeyboardButton("⚔️ Eng kuchli jangchilar", callback_data="leaderboard_battlers"),
        ],
        [
            InlineKeyboardButton("🔙 Statistikaga qaytish", callback_data="view_stats"),
            InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def books_kb(books: list) -> InlineKeyboardMarkup:
    keyboard = []
    badges = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔵", 5: "🟣", 6: "🔴"}
    for b in books:
        b_id = b["id"]
        badge = badges.get(b_id, "📘")
        cefr = b.get("cefr_level", "")
        text = f"{badge} Book {b_id} ({cefr}) - 600 words"
        keyboard.append([InlineKeyboardButton(text, callback_data=f"book_{b_id}")])
    
    keyboard.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def units_kb(book_id: int, page: int = 0) -> InlineKeyboardMarkup:
    start_unit = page * 10 + 1
    end_unit = min(start_unit + 9, 30)

    keyboard = []
    row1 = []
    for u in range(start_unit, min(start_unit + 5, end_unit + 1)):
        row1.append(InlineKeyboardButton(f"Unit {u}", callback_data=f"unit_{book_id}_{u}"))
    keyboard.append(row1)

    if end_unit >= start_unit + 5:
        row2 = []
        for u in range(start_unit + 5, end_unit + 1):
            row2.append(InlineKeyboardButton(f"Unit {u}", callback_data=f"unit_{book_id}_{u}"))
        keyboard.append(row2)

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Oldingi 10 ta", callback_data=f"units_page_{book_id}_{page - 1}"))
    if page < 2:
        nav_row.append(InlineKeyboardButton("Keyingi 10 ta ➡️", callback_data=f"units_page_{book_id}_{page + 1}"))
    if nav_row:
        keyboard.append(nav_row)

    keyboard.append([InlineKeyboardButton("🔙 Kitoblar ro'yxatiga", callback_data="view_books")])
    return InlineKeyboardMarkup(keyboard)

def unit_menu_kb(book_id: int, unit_num: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🗂 So'zlarni o'rganish (1/20)", callback_data=f"word_{book_id}_{unit_num}_1")
        ],
        [
            InlineKeyboardButton("📝 Unit bo'yicha Test (Quiz)", callback_data=f"quiz_start_{book_id}_{unit_num}"),
            InlineKeyboardButton("📖 Unit Hikoyasi", callback_data=f"story_{book_id}_{unit_num}")
        ],
        [
            InlineKeyboardButton("📋 So'zlar ro'yxati (20 ta)", callback_data=f"wordlist_{book_id}_{unit_num}")
        ],
        [
            InlineKeyboardButton("🔙 Unitlar ro'yxatiga", callback_data=f"book_{book_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def word_card_kb(book_id: int, unit_num: int, word_index: int, word_id: int, 
                 is_starred: bool, is_known: bool, from_random: bool = False,
                 from_bookmark: bool = False) -> InlineKeyboardMarkup:
    keyboard = []
    prev_idx = word_index - 1 if word_index > 1 else 20
    next_idx = word_index + 1 if word_index < 20 else 1
    
    if not from_random and not from_bookmark:
        keyboard.append([
            InlineKeyboardButton("⬅️ Oldingi", callback_data=f"word_{book_id}_{unit_num}_{prev_idx}"),
            InlineKeyboardButton(f"📍 {word_index}/20", callback_data=f"wordlist_{book_id}_{unit_num}"),
            InlineKeyboardButton("Keyingi ➡️", callback_data=f"word_{book_id}_{unit_num}_{next_idx}")
        ])
    elif from_random:
        keyboard.append([
            InlineKeyboardButton("🎲 Yana tasodifiy so'z", callback_data="random_word")
        ])
    
    keyboard.append([
        InlineKeyboardButton("🔊 Talaffuz (Audio)", callback_data=f"audio_{word_id}"),
        InlineKeyboardButton("🖼 Rasm", callback_data=f"image_{word_id}")
    ])
    
    star_icon = "⭐ Saqlangan" if is_starred else "☆ Saqlash"
    known_icon = "✅ Yodladim" if is_known else "⭕ Yodlash"
    
    keyboard.append([
        InlineKeyboardButton(star_icon, callback_data=f"toggle_star_{word_id}_{book_id}_{unit_num}_{word_index}"),
        InlineKeyboardButton(known_icon, callback_data=f"toggle_learned_{word_id}_{book_id}_{unit_num}_{word_index}")
    ])
    
    if from_bookmark:
        keyboard.append([InlineKeyboardButton("🔙 Saqlanganlarga qaytish", callback_data="bookmarks_0")])
    elif not from_random:
        keyboard.append([
            InlineKeyboardButton("📝 Test topshirish", callback_data=f"quiz_start_{book_id}_{unit_num}"),
            InlineKeyboardButton("🔙 Unit menyusi", callback_data=f"unit_{book_id}_{unit_num}")
        ])
    else:
        keyboard.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")])
        
    return InlineKeyboardMarkup(keyboard)

def quiz_question_kb(session_id: str, q_idx: int, options: list) -> InlineKeyboardMarkup:
    keyboard = []
    letters = ["A", "B", "C", "D"]
    for i, opt in enumerate(options):
        letter = letters[i] if i < len(letters) else f"{i+1}"
        keyboard.append([
            InlineKeyboardButton(f"{letter}) {opt}", callback_data=f"qans_{session_id}_{q_idx}_{i}")
        ])
    keyboard.append([
        InlineKeyboardButton("🛑 Testni yakunlash", callback_data=f"qstop_{session_id}")
    ])
    return InlineKeyboardMarkup(keyboard)

def quiz_feedback_kb(session_id: str, q_idx: int, is_last: bool = False) -> InlineKeyboardMarkup:
    next_btn_text = "🏁 Natijani ko'rish" if is_last else "Keyingi savol ➡️"
    callback = f"qnext_{session_id}_{q_idx + 1}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(next_btn_text, callback_data=callback)]
    ])

def quiz_completed_kb(book_id: int, unit_num: int) -> InlineKeyboardMarkup:
    keyboard = []
    if book_id > 0 and unit_num > 0:
        next_unit = unit_num + 1 if unit_num < 30 else 1
        next_book = book_id if unit_num < 30 else (book_id + 1 if book_id < 6 else 1)
        keyboard.append([
            InlineKeyboardButton("🔁 Qayta topshirish", callback_data=f"quiz_start_{book_id}_{unit_num}"),
            InlineKeyboardButton("📖 Keyingi Unit", callback_data=f"unit_{next_book}_{next_unit}")
        ])
        keyboard.append([InlineKeyboardButton("🔙 Unit menyusi", callback_data=f"unit_{book_id}_{unit_num}")])
    else:
        keyboard.append([InlineKeyboardButton("🧠 Yana tezkor test", callback_data="quick_quiz")])
        keyboard.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def bookmarks_list_kb(bookmarks: list, page: int = 0, total: int = 0, page_size: int = 6) -> InlineKeyboardMarkup:
    keyboard = []
    for b in bookmarks:
        w = b["word"]
        tr = b.get("translation_uz", "")
        btn_text = f"⭐ {w.capitalize()} - {tr[:20]}" if tr else f"⭐ {w.capitalize()}"
        keyboard.append([
            InlineKeyboardButton(btn_text, callback_data=f"view_word_id_{b['id']}")
        ])
    
    max_pages = (total - 1) // page_size if total > 0 else 0
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Oldingi", callback_data=f"bookmarks_{page - 1}"))
    if total > 0:
        nav_row.append(InlineKeyboardButton(f"📄 {page + 1}/{max_pages + 1}", callback_data="noop"))
    if page < max_pages:
        nav_row.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"bookmarks_{page + 1}"))
    
    if nav_row:
        keyboard.append(nav_row)
        
    keyboard.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def search_results_kb(results: list) -> InlineKeyboardMarkup:
    keyboard = []
    for r in results:
        w = r["word"]
        tr = r.get("translation_uz", "")
        b = r.get("book_id", 1)
        u = r.get("unit_number", 1)
        label = f"📖 B{b}U{u}: {w.capitalize()} ({tr[:18]})" if tr else f"📖 B{b}U{u}: {w.capitalize()}"
        keyboard.append([
            InlineKeyboardButton(label, callback_data=f"view_word_id_{r['id']}")
        ])
    keyboard.append([InlineKeyboardButton("🏠 Bosh menyu", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

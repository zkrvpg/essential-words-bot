"""
Database operations for 4000 Essential English Words Bot
With Battle (1v1), Practice Modes, Leaderboard, and Extended Stats
"""
import aiosqlite
import random
import json
import uuid
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
from config import DB_PATH, BOOKS_INFO

async def init_extended_tables():
    """Initializes tables for battles, rankings, and learning modes."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Check and add columns to user_stats if not present
        async with db.execute("PRAGMA table_info(user_stats)") as cur:
            columns = [row[1] for row in await cur.fetchall()]
        
        if "battles_won" not in columns:
            await db.execute("ALTER TABLE user_stats ADD COLUMN battles_won INTEGER DEFAULT 0")
        if "battles_lost" not in columns:
            await db.execute("ALTER TABLE user_stats ADD COLUMN battles_lost INTEGER DEFAULT 0")
        if "battle_rating" not in columns:
            await db.execute("ALTER TABLE user_stats ADD COLUMN battle_rating INTEGER DEFAULT 1000")
        if "streak_days" not in columns:
            await db.execute("ALTER TABLE user_stats ADD COLUMN streak_days INTEGER DEFAULT 1")
        if "last_active_date" not in columns:
            await db.execute("ALTER TABLE user_stats ADD COLUMN last_active_date TEXT DEFAULT ''")

        # Create battles table
        await db.execute("""
        CREATE TABLE IF NOT EXISTS battles (
            id TEXT PRIMARY KEY,
            player1_id INTEGER,
            player1_name TEXT,
            player1_score INTEGER DEFAULT 0,
            player1_done INTEGER DEFAULT 0,
            player2_id INTEGER,
            player2_name TEXT,
            player2_score INTEGER DEFAULT 0,
            player2_done INTEGER DEFAULT 0,
            book_id INTEGER DEFAULT 1,
            questions_json TEXT,
            winner_id INTEGER,
            status TEXT DEFAULT 'waiting',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        await db.commit()

async def ensure_user(user_id: int, first_name: str, username: Optional[str] = None):
    today_str = date.today().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT last_active_date, streak_days FROM user_stats WHERE user_id = ?", (user_id,)) as cur:
            existing = await cur.fetchone()

        if existing:
            last_date = existing["last_active_date"] or ""
            current_streak = existing["streak_days"] or 1
            if last_date != today_str:
                # check if consecutive day
                try:
                    delta = (date.today() - datetime.strptime(last_date, "%Y-%m-%d").date()).days
                    if delta == 1:
                        current_streak += 1
                    elif delta > 1:
                        current_streak = 1
                except Exception:
                    current_streak = 1

            await db.execute("""
            UPDATE user_stats SET
                first_name = ?,
                username = ?,
                streak_days = ?,
                last_active_date = ?,
                last_active = CURRENT_TIMESTAMP
            WHERE user_id = ?
            """, (first_name, username, current_streak, today_str, user_id))
        else:
            await db.execute("""
            INSERT INTO user_stats (user_id, first_name, username, streak_days, last_active_date, battle_rating, last_active)
            VALUES (?, ?, ?, 1, ?, 1000, CURRENT_TIMESTAMP)
            """, (user_id, first_name, username, today_str))

        await db.commit()

async def get_books() -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, title, cefr_level, description FROM books ORDER BY id ASC") as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

async def get_book(book_id: int) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, title, cefr_level, description FROM books WHERE id = ?", (book_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

async def get_units(book_id: int) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT id, book_id, unit_number, title, story
            FROM units
            WHERE book_id = ?
            ORDER BY unit_number ASC
        """, (book_id,)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

async def get_unit(book_id: int, unit_number: int) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT id, book_id, unit_number, title, story
            FROM units
            WHERE book_id = ? AND unit_number = ?
        """, (book_id, unit_number)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

async def get_unit_words(book_id: int, unit_number: int) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM words
            WHERE book_id = ? AND unit_number = ?
            ORDER BY word_index ASC
        """, (book_id, unit_number)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

async def get_word(word_id: int) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM words WHERE id = ?", (word_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

async def get_word_by_index(book_id: int, unit_number: int, word_index: int) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM words
            WHERE book_id = ? AND unit_number = ? AND word_index = ?
        """, (book_id, unit_number, word_index)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

async def get_random_word(book_id: Optional[int] = None) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if book_id:
            query = "SELECT * FROM words WHERE book_id = ? ORDER BY RANDOM() LIMIT 1"
            params = (book_id,)
        else:
            query = "SELECT * FROM words ORDER BY RANDOM() LIMIT 1"
            params = ()
        async with db.execute(query, params) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None

async def search_words(query: str, limit: int = 15) -> List[Dict]:
    q = f"%{query.strip().lower()}%"
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM words
            WHERE word LIKE ? OR translation_uz LIKE ? OR definition LIKE ?
            ORDER BY 
                CASE WHEN word = ? THEN 1
                     WHEN word LIKE ? THEN 2
                     ELSE 3 END,
                book_id ASC, unit_number ASC, word_index ASC
            LIMIT ?
        """, (q, q, q, query.strip().lower(), f"{query.strip().lower()}%", limit)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

async def is_bookmarked(user_id: int, word_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM user_bookmarks WHERE user_id = ? AND word_id = ?", (user_id, word_id)) as cur:
            row = await cur.fetchone()
            return row is not None

async def toggle_bookmark(user_id: int, word_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM user_bookmarks WHERE user_id = ? AND word_id = ?", (user_id, word_id)) as cur:
            exists = await cur.fetchone()
        
        if exists:
            await db.execute("DELETE FROM user_bookmarks WHERE user_id = ? AND word_id = ?", (user_id, word_id))
            await db.commit()
            return False
        else:
            await db.execute("INSERT OR REPLACE INTO user_bookmarks (user_id, word_id) VALUES (?, ?)", (user_id, word_id))
            await db.commit()
            return True

async def get_user_bookmarks(user_id: int, limit: int = 50, offset: int = 0) -> Tuple[List[Dict], int]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT count(*) FROM user_bookmarks WHERE user_id = ?", (user_id,)) as cur:
            total = (await cur.fetchone())[0]
            
        async with db.execute("""
            SELECT w.* FROM words w
            JOIN user_bookmarks b ON w.id = b.word_id
            WHERE b.user_id = ?
            ORDER BY b.created_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, limit, offset)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows], total

async def is_learned(user_id: int, word_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM user_learned WHERE user_id = ? AND word_id = ?", (user_id, word_id)) as cur:
            row = await cur.fetchone()
            return row is not None

async def toggle_learned(user_id: int, word_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM user_learned WHERE user_id = ? AND word_id = ?", (user_id, word_id)) as cur:
            exists = await cur.fetchone()
        
        if exists:
            await db.execute("DELETE FROM user_learned WHERE user_id = ? AND word_id = ?", (user_id, word_id))
            await db.commit()
            return False
        else:
            await db.execute("INSERT OR REPLACE INTO user_learned (user_id, word_id) VALUES (?, ?)", (user_id, word_id))
            await db.commit()
            return True

async def get_user_stats(user_id: int) -> Dict:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        # Learned count
        async with db.execute("SELECT count(*) FROM user_learned WHERE user_id = ?", (user_id,)) as cur:
            learned_count = (await cur.fetchone())[0]
            
        # Bookmarks count
        async with db.execute("SELECT count(*) FROM user_bookmarks WHERE user_id = ?", (user_id,)) as cur:
            bookmarks_count = (await cur.fetchone())[0]
            
        # Total words in DB
        async with db.execute("SELECT count(*) FROM words") as cur:
            total_words = (await cur.fetchone())[0]
            
        # User quiz and battle record
        async with db.execute("""
            SELECT total_quizzes, correct_answers, total_answers, battles_won, battles_lost, battle_rating, streak_days
            FROM user_stats WHERE user_id = ?
        """, (user_id,)) as cur:
            row = await cur.fetchone()
            if row:
                t_quizzes = row["total_quizzes"] or 0
                c_answers = row["correct_answers"] or 0
                t_answers = row["total_answers"] or 0
                b_won = row["battles_won"] or 0
                b_lost = row["battles_lost"] or 0
                b_rating = row["battle_rating"] or 1000
                streak = row["streak_days"] or 1
            else:
                t_quizzes = 0
                c_answers = 0
                t_answers = 0
                b_won = 0
                b_lost = 0
                b_rating = 1000
                streak = 1
                
        accuracy = round((c_answers / t_answers * 100), 1) if t_answers > 0 else 0
        
        # User level title
        if learned_count >= 2000:
            level_title = "💎 Grandmaster (Lug'at Ustasi)"
        elif learned_count >= 1000:
            level_title = "🥇 Master (Tajribali)"
        elif learned_count >= 400:
            level_title = "🥈 Advanced (Ilg'or)"
        elif learned_count >= 100:
            level_title = "🥉 Intermediate (O'rta)"
        else:
            level_title = "🌱 Beginner (Boshlovchi)"

        # Progress bar
        pct = min(100, round((learned_count / total_words * 100), 1)) if total_words > 0 else 0
        filled = int(pct // 10)
        progress_bar = "█" * filled + "░" * (10 - filled)

        return {
            "learned_count": learned_count,
            "bookmarks_count": bookmarks_count,
            "total_words": total_words,
            "total_quizzes": t_quizzes,
            "correct_answers": c_answers,
            "total_answers": t_answers,
            "accuracy": accuracy,
            "battles_won": b_won,
            "battles_lost": b_lost,
            "battle_rating": b_rating,
            "streak_days": streak,
            "level_title": level_title,
            "progress_bar": progress_bar,
            "progress_pct": pct
        }

async def update_quiz_stats(user_id: int, correct_count: int, total_count: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO user_stats (user_id, first_name, streak_days, battle_rating, last_active)
            VALUES (?, 'O''quvchi', 1, 1000, CURRENT_TIMESTAMP)
        """, (user_id,))
        await db.execute("""
            UPDATE user_stats
            SET total_quizzes = COALESCE(total_quizzes, 0) + 1,
                correct_answers = COALESCE(correct_answers, 0) + ?,
                total_answers = COALESCE(total_answers, 0) + ?,
                last_active = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (correct_count, total_count, user_id))
        await db.commit()

async def get_leaderboard_learners(limit: int = 10) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT u.user_id, u.first_name, u.username, COUNT(l.word_id) as learned_count
            FROM user_stats u
            LEFT JOIN user_learned l ON u.user_id = l.user_id
            GROUP BY u.user_id
            ORDER BY learned_count DESC, u.total_quizzes DESC
            LIMIT ?
        """, (limit,)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

async def get_leaderboard_battlers(limit: int = 10) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT user_id, first_name, username, battles_won, battles_lost, battle_rating
            FROM user_stats
            WHERE (battles_won + battles_lost) > 0
            ORDER BY battle_rating DESC, battles_won DESC
            LIMIT ?
        """, (limit,)) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

# ==================== QUIZ & PRACTICE MODES ====================

async def get_quiz_data_for_unit(book_id: int, unit_number: int, num_questions: int = 10) -> List[Dict]:
    """Generates 4-choice questions."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM words WHERE book_id = ? AND unit_number = ?
        """, (book_id, unit_number)) as cur:
            target_words = [dict(r) for r in await cur.fetchall()]
        
        if not target_words:
            return []
            
        async with db.execute("""
            SELECT word, translation_uz, definition FROM words WHERE book_id = ?
        """, (book_id,)) as cur:
            pool = [dict(r) for r in await cur.fetchall()]

    sample_words = random.sample(target_words, min(len(target_words), num_questions))
    questions = []

    for idx, tw in enumerate(sample_words):
        q_type = "en_to_uz" if idx % 2 == 0 else "def_to_en"
        
        if q_type == "en_to_uz" and tw.get("translation_uz"):
            correct_val = tw["translation_uz"]
            distractor_pool = [w["translation_uz"] for w in pool if w.get("translation_uz") and w["translation_uz"] != correct_val]
            distractors = random.sample(distractor_pool, min(3, len(distractor_pool)))
            
            options = [correct_val] + distractors
            random.shuffle(options)
            
            questions.append({
                "type": "en_to_uz",
                "question": f"🇬🇧 *{tw['word'].upper()}* `{tw.get('phonetic', '')}`\n\n📌 Ushbu so'zning o'zbekcha tarjimasini toping:",
                "target_word": tw["word"],
                "correct_option": correct_val,
                "options": options,
                "word_id": tw["id"],
                "definition": tw["definition"],
                "example": tw["example"]
            })
        else:
            correct_val = tw["word"]
            distractor_pool = [w["word"] for w in pool if w.get("word") and w["word"] != correct_val]
            distractors = random.sample(distractor_pool, min(3, len(distractor_pool)))
            
            options = [correct_val] + distractors
            random.shuffle(options)
            
            questions.append({
                "type": "def_to_en",
                "question": f"💡 *Ta'rif:*\n_{tw['definition']}_\n\n❓ Qaysi so'z ifodalangan?",
                "target_word": tw["word"],
                "correct_option": correct_val,
                "options": options,
                "word_id": tw["id"],
                "definition": tw["definition"],
                "example": tw["example"]
            })

    return questions

async def get_spelling_question(book_id: Optional[int] = None) -> Optional[Dict]:
    """Generates a spelling exercise."""
    word = await get_random_word(book_id)
    if not word:
        return None
    w = word["word"].lower().strip()
    # Masked representation: e.g. a _ _ _ e
    if len(w) > 3:
        masked = w[0] + " " + " ".join(["_" for _ in range(len(w) - 2)]) + " " + w[-1]
    else:
        masked = " ".join(["_" for _ in range(len(w))])
        
    return {
        "word_id": word["id"],
        "word": w,
        "masked": masked,
        "length": len(w),
        "translation_uz": word.get("translation_uz", ""),
        "definition": word.get("definition", ""),
        "example": word.get("example", ""),
        "phonetic": word.get("phonetic", ""),
        "book_id": word["book_id"],
        "unit_number": word["unit_number"]
    }

async def get_listening_question(book_id: Optional[int] = None) -> Optional[Dict]:
    """Generates a listening exercise with 4 options."""
    word = await get_random_word(book_id)
    if not word or not word.get("audio_url"):
        return None
        
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT word FROM words WHERE book_id = ? AND word != ? ORDER BY RANDOM() LIMIT 3
        """, (word["book_id"], word["word"])) as cur:
            distractors = [r["word"] for r in await cur.fetchall()]

    options = [word["word"]] + distractors
    random.shuffle(options)
    
    return {
        "word_id": word["id"],
        "correct_word": word["word"],
        "audio_url": word["audio_url"],
        "translation_uz": word.get("translation_uz", ""),
        "definition": word.get("definition", ""),
        "options": options,
        "book_id": word["book_id"],
        "unit_number": word["unit_number"]
    }

# ==================== 1v1 BATTLE ENGINE ====================

async def create_battle(creator_id: int, creator_name: str, book_id: int = 1) -> str:
    """Creates a new battle room."""
    battle_id = str(uuid.uuid4())[:8]
    # Pick 5 questions from the chosen book
    unit_num = random.randint(1, 30)
    questions = await get_quiz_data_for_unit(book_id, unit_num, num_questions=5)
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO battles (id, player1_id, player1_name, book_id, questions_json, status)
            VALUES (?, ?, ?, ?, ?, 'waiting')
        """, (battle_id, creator_id, creator_name, book_id, json.dumps(questions)))
        await db.commit()
        
    return battle_id

async def join_battle(battle_id: str, opponent_id: int, opponent_name: str) -> Optional[Dict]:
    """Joins an existing battle room."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM battles WHERE id = ?", (battle_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                return None
            battle = dict(row)
            
        if battle["status"] != "waiting":
            return None
        if battle["player1_id"] == opponent_id:
            # Cannot join own battle as opponent
            return None
            
        await db.execute("""
            UPDATE battles
            SET player2_id = ?, player2_name = ?, status = 'active'
            WHERE id = ?
        """, (opponent_id, opponent_name, battle_id))
        await db.commit()
        
        battle["player2_id"] = opponent_id
        battle["player2_name"] = opponent_name
        battle["status"] = "active"
        battle["questions"] = json.loads(battle["questions_json"])
        return battle

async def get_battle(battle_id: str) -> Optional[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM battles WHERE id = ?", (battle_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                return None
            res = dict(row)
            res["questions"] = json.loads(res["questions_json"])
            return res

async def record_battle_result(battle_id: str, player_num: int, score: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if player_num == 1:
            await db.execute("UPDATE battles SET player1_score = ?, player1_done = 1 WHERE id = ?", (score, battle_id))
        else:
            await db.execute("UPDATE battles SET player2_score = ?, player2_done = 1 WHERE id = ?", (score, battle_id))
        await db.commit()

        # Check if both done
        async with db.execute("SELECT * FROM battles WHERE id = ?", (battle_id,)) as cur:
            b = dict(await cur.fetchone())
            
        if b["player1_done"] == 1 and b["player2_done"] == 1:
            # Determine winner
            if b["player1_score"] > b["player2_score"]:
                winner_id = b["player1_id"]
                await update_battle_ratings(db, b["player1_id"], b["player2_id"])
            elif b["player2_score"] > b["player1_score"]:
                winner_id = b["player2_id"]
                await update_battle_ratings(db, b["player2_id"], b["player1_id"])
            else:
                winner_id = 0 # Draw
                
            await db.execute("UPDATE battles SET winner_id = ?, status = 'finished' WHERE id = ?", (winner_id, battle_id))
            await db.commit()

async def update_battle_ratings(db, winner_id: int, loser_id: int):
    """Updates Elo ratings after a battle (+25 for winner, -15 for loser)."""
    await db.execute("""
        UPDATE user_stats
        SET battles_won = COALESCE(battles_won, 0) + 1,
            battle_rating = COALESCE(battle_rating, 1000) + 25
        WHERE user_id = ?
    """, (winner_id,))
    
    await db.execute("""
        UPDATE user_stats
        SET battles_lost = COALESCE(battles_lost, 0) + 1,
            battle_rating = MAX(500, COALESCE(battle_rating, 1000) - 15)
        WHERE user_id = ?
    """, (loser_id,))

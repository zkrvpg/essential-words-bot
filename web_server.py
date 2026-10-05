"""
Aiohttp web server to serve the clean, ad-free Telegram WebApp and REST APIs
Expanded with:
- Units with Reading Stories
- User Stats & Leaderboard APIs
- Battle (1v1) Quiz Questions & Result Recording
- Personal Bookmarks & Learning Progress Synchronization
"""
import os
import json
from aiohttp import web
import database as db

WEBAPP_DIR = os.path.join(os.path.dirname(__file__), "webapp")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}

async def handle_options(request):
    return web.Response(headers=CORS_HEADERS)

async def handle_index(request):
    index_file = os.path.join(WEBAPP_DIR, "index.html")
    if os.path.exists(index_file):
        return web.FileResponse(index_file)
    return web.Response(text="Web App loading...", content_type="text/html")

async def handle_api_books(request):
    books = await db.get_books()
    return web.json_response(books, headers=CORS_HEADERS)

async def handle_api_units(request):
    try:
        book_id = int(request.query.get("book", 1))
        units = await db.get_units(book_id)
        trimmed = [
            {"id": u["id"], "book_id": u["book_id"], "unit_number": u["unit_number"], "title": u.get("title", f"Unit {u['unit_number']}")}
            for u in units
        ]
        return web.json_response(trimmed, headers=CORS_HEADERS)
    except Exception:
        return web.json_response([], headers=CORS_HEADERS)

async def handle_api_unit_details(request):
    try:
        book_id = int(request.query.get("book", 1))
        unit_num = int(request.query.get("unit", 1))
        unit = await db.get_unit(book_id, unit_num)
        words = await db.get_unit_words(book_id, unit_num)
        data = dict(unit) if unit else {"book_id": book_id, "unit_number": unit_num, "title": f"Unit {unit_num}", "story": ""}
        data["words"] = words
        return web.json_response(data, headers=CORS_HEADERS)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500, headers=CORS_HEADERS)

async def handle_api_words(request):
    book_id = int(request.query.get("book", 1))
    unit_num = int(request.query.get("unit", 1))
    words = await db.get_unit_words(book_id, unit_num)
    return web.json_response(words, headers=CORS_HEADERS)

async def handle_api_search(request):
    q = request.query.get("q", "").strip()
    if not q:
        return web.json_response([], headers=CORS_HEADERS)
    results = await db.search_words(q, limit=20)
    return web.json_response(results, headers=CORS_HEADERS)

async def handle_api_stats(request):
    try:
        user_id = int(request.query.get("user_id", 0))
        first_name = request.query.get("first_name", "")
        username = request.query.get("username", None)
        if user_id > 0:
            if first_name:
                await db.ensure_user(user_id, first_name, username)
            else:
                await db.ensure_user(user_id, "O'quvchi", username)
            stats = await db.get_user_stats(user_id)
            return web.json_response(stats, headers=CORS_HEADERS)
    except Exception as e:
        pass

    # Default global stats
    stats = {
        "learned_count": 0,
        "bookmarks_count": 0,
        "total_words": 3600,
        "total_quizzes": 0,
        "correct_answers": 0,
        "total_answers": 0,
        "accuracy": 0,
        "battles_won": 0,
        "battles_lost": 0,
        "battle_rating": 1000,
        "streak_days": 1,
        "level_title": "🌱 Beginner (Boshlovchi)",
        "progress_bar": "░░░░░░░░░░",
        "progress_pct": 0
    }
    return web.json_response(stats, headers=CORS_HEADERS)

async def handle_api_leaderboard(request):
    l_type = request.query.get("type", "learners")
    if l_type == "battlers":
        data = await db.get_leaderboard_battlers(10)
    else:
        data = await db.get_leaderboard_learners(10)
    return web.json_response(data, headers=CORS_HEADERS)

async def handle_api_battle_questions(request):
    book_id = int(request.query.get("book", 1))
    import random
    unit_num = int(request.query.get("unit", random.randint(1, 30)))
    questions = await db.get_quiz_data_for_unit(book_id, unit_num, num_questions=5)
    return web.json_response(questions, headers=CORS_HEADERS)

async def handle_api_toggle_learned(request):
    try:
        body = await request.json()
        user_id = int(body.get("user_id", 0))
        word_id = int(body.get("word_id", 0))
        if user_id > 0 and word_id > 0:
            await db.ensure_user(user_id, "O'quvchi")
            is_learned = await db.toggle_learned(user_id, word_id)
            stats = await db.get_user_stats(user_id)
            return web.json_response({"ok": True, "is_learned": is_learned, "stats": stats}, headers=CORS_HEADERS)
    except Exception as e:
        pass
    return web.json_response({"ok": False}, headers=CORS_HEADERS)

async def handle_api_toggle_bookmark(request):
    try:
        body = await request.json()
        user_id = int(body.get("user_id", 0))
        word_id = int(body.get("word_id", 0))
        if user_id > 0 and word_id > 0:
            await db.ensure_user(user_id, "O'quvchi")
            is_bookmarked = await db.toggle_bookmark(user_id, word_id)
            stats = await db.get_user_stats(user_id)
            return web.json_response({"ok": True, "is_bookmarked": is_bookmarked, "stats": stats}, headers=CORS_HEADERS)
    except Exception as e:
        pass
    return web.json_response({"ok": False}, headers=CORS_HEADERS)

async def handle_api_quiz_result(request):
    try:
        body = await request.json()
        user_id = int(body.get("user_id", 0))
        correct = int(body.get("correct", 0))
        total = int(body.get("total", 0))
        if user_id > 0 and total > 0:
            await db.ensure_user(user_id, "O'quvchi")
            await db.update_quiz_stats(user_id, correct, total)
            stats = await db.get_user_stats(user_id)
            return web.json_response({"ok": True, "stats": stats}, headers=CORS_HEADERS)
    except Exception:
        pass
    return web.json_response({"ok": False}, headers=CORS_HEADERS)

async def handle_api_battle_result(request):
    try:
        body = await request.json()
        user_id = int(body.get("user_id", 0))
        won = bool(body.get("won", False))
        if user_id > 0:
            await db.ensure_user(user_id, "O'quvchi")
            import aiosqlite
            async with aiosqlite.connect(db.DB_PATH) as db_conn:
                if won:
                    await db_conn.execute("""
                        UPDATE user_stats
                        SET battles_won = COALESCE(battles_won, 0) + 1,
                            battle_rating = COALESCE(battle_rating, 1000) + 25,
                            last_active = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    """, (user_id,))
                else:
                    await db_conn.execute("""
                        UPDATE user_stats
                        SET battles_lost = COALESCE(battles_lost, 0) + 1,
                            battle_rating = MAX(500, COALESCE(battle_rating, 1000) - 15),
                            last_active = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    """, (user_id,))
                await db_conn.commit()
            stats = await db.get_user_stats(user_id)
            return web.json_response({"ok": True, "stats": stats}, headers=CORS_HEADERS)
    except Exception:
        pass
    return web.json_response({"ok": False}, headers=CORS_HEADERS)

async def handle_api_import_words(request):
    try:
        body = await request.json()
        book_id = int(body.get("book_id", 8))
        unit_number = int(body.get("unit_number", 1))
        unit_title = body.get("unit_title", f"Unit {unit_number}").strip()
        book_title = body.get("book_title", None)
        story = body.get("story", "").strip()
        raw_text = body.get("raw_text", "")
        parsed_words = []

        if "words" in body and isinstance(body["words"], list):
            parsed_words = body["words"]
        elif raw_text:
            lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
            for line in lines:
                parts = []
                if " - " in line:
                    parts = [p.strip() for p in line.split(" - ")]
                elif "\t" in line:
                    parts = [p.strip() for p in line.split("\t")]
                elif ":" in line:
                    parts = [p.strip() for p in line.split(":", 1)]
                else:
                    parts = [line]

                if parts:
                    w_text = parts[0]
                    tr_text = parts[1] if len(parts) > 1 else w_text
                    defn_text = parts[2] if len(parts) > 2 else f"Meaning of {w_text}."
                    parsed_words.append({
                        "word": w_text,
                        "translation_uz": tr_text,
                        "definition": defn_text,
                        "part_of_speech": "n.",
                        "part_of_speech_uz": "ot (noun)",
                        "example": f"Example sentence using {w_text}."
                    })

        if not parsed_words:
            return web.json_response({"ok": False, "error": "Hech qanday so'z topilmadi"}, headers=CORS_HEADERS)

        ok, count, msg = await db.add_custom_words(
            book_id=book_id,
            unit_number=unit_number,
            unit_title=unit_title,
            words=parsed_words,
            book_title=book_title,
            story=story
        )
        return web.json_response({"ok": ok, "count": count, "message": msg}, headers=CORS_HEADERS)
    except Exception as e:
        return web.json_response({"ok": False, "error": str(e)}, status=500, headers=CORS_HEADERS)

async def handle_health(request):
    return web.json_response({"status": "ok", "app": "4000 Essential English Words"}, headers=CORS_HEADERS)

def create_web_app() -> web.Application:
    app = web.Application()
    app.router.add_route("OPTIONS", "/{tail:.*}", handle_options)
    app.router.add_get("/", handle_index)
    app.router.add_get("/health", handle_health)
    app.router.add_get("/api/books", handle_api_books)
    app.router.add_get("/api/units", handle_api_units)
    app.router.add_get("/api/unit_details", handle_api_unit_details)
    app.router.add_get("/api/words", handle_api_words)
    app.router.add_get("/api/search", handle_api_search)
    app.router.add_get("/api/stats", handle_api_stats)
    app.router.add_get("/api/leaderboard", handle_api_leaderboard)
    app.router.add_get("/api/battle/questions", handle_api_battle_questions)
    app.router.add_post("/api/user/toggle_learned", handle_api_toggle_learned)
    app.router.add_post("/api/user/toggle_bookmark", handle_api_toggle_bookmark)
    app.router.add_post("/api/user/quiz_result", handle_api_quiz_result)
    app.router.add_post("/api/user/battle_result", handle_api_battle_result)
    app.router.add_post("/api/import_words", handle_api_import_words)
    return app

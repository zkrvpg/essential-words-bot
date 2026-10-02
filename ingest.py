"""
4000 Essential English Words - Data Ingestion and DB Setup
"""
import os
import sys
import re
import json
import sqlite3
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from translatepy import Translator

DB_PATH = os.path.join(os.path.dirname(__file__), "essential_words.db")

CEFR_LEVELS = {
    1: ("Book 1 (A2 - Elementary)", "A2", "Boshlang'ich darajadagi eng muhim 600 ta so'z"),
    2: ("Book 2 (B1 - Pre-Intermediate)", "B1", "O'rta-boshlang'ich darajadagi 600 ta so'z"),
    3: ("Book 3 (B1+ - Intermediate)", "B1+", "O'rta darajadagi 600 ta so'z"),
    4: ("Book 4 (B2 - Upper-Intermediate)", "B2", "O'rtadan yuqori darajadagi 600 ta so'z"),
    5: ("Book 5 (B2+ - Advanced)", "B2+", "Yuqori darajadagi 600 ta so'z"),
    6: ("Book 6 (C1 - Proficiency)", "C1", "Eng yuqori professional darajadagi 600 ta so'z"),
}

PART_OF_SPEECH_UZ = {
    "v.": "fe'l (verb)",
    "n.": "ot (noun)",
    "adj.": "sifat (adj)",
    "adv.": "ravish (adv)",
    "pron.": "olmosh (pron)",
    "prep.": "predlog (prep)",
    "conj.": "bog'lovchi (conj)",
    "interj.": "undov (interj)",
}

translator = Translator()

def get_uzbek_translation(word: str) -> str:
    try:
        res = translator.translate(word, "uz")
        if res and res.result:
            return res.result.strip().lower()
    except Exception as e:
        pass
    return ""

def init_db(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY,
        title TEXT,
        cefr_level TEXT,
        description TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS units (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        unit_number INTEGER,
        title TEXT,
        story TEXT,
        UNIQUE(book_id, unit_number)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        unit_id INTEGER,
        unit_number INTEGER,
        word_index INTEGER,
        word TEXT,
        phonetic TEXT,
        part_of_speech TEXT,
        part_of_speech_uz TEXT,
        definition TEXT,
        example TEXT,
        translation_uz TEXT,
        image_url TEXT,
        audio_url TEXT,
        UNIQUE(book_id, unit_number, word_index)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_bookmarks (
        user_id INTEGER,
        word_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, word_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_learned (
        user_id INTEGER,
        word_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, word_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_stats (
        user_id INTEGER PRIMARY KEY,
        first_name TEXT,
        username TEXT,
        total_quizzes INTEGER DEFAULT 0,
        correct_answers INTEGER DEFAULT 0,
        total_answers INTEGER DEFAULT 0,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_settings (
        user_id INTEGER PRIMARY KEY,
        current_book INTEGER DEFAULT 1,
        current_unit INTEGER DEFAULT 1,
        current_word_idx INTEGER DEFAULT 1
    );
    """)

    for b_id, (b_title, b_cefr, b_desc) in CEFR_LEVELS.items():
        cur.execute("""
        INSERT OR REPLACE INTO books (id, title, cefr_level, description)
        VALUES (?, ?, ?, ?)
        """, (b_id, b_title, b_cefr, b_desc))

    conn.commit()

def ingest_book(book_num: int, conn: sqlite3.Connection, translate: bool = True):
    print(f"[*] Kitob {book_num} ma'lumotlari yuklanmoqda...", flush=True)
    url = f"https://raw.githubusercontent.com/MohKardan/4000-Essential-English-Words/main/data/2nd-edition/book{book_num}/data.json"
    
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw_data = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    data = json.loads(raw_data)
    
    cur = conn.cursor()
    flashcards = data.get("flashcard", [])
    
    words_to_translate = []
    parsed_words = []

    for unit_idx, u in enumerate(flashcards, start=1):
        unit_title = u.get("en", f"Unit {unit_idx}")
        if ":" in unit_title:
            unit_title = unit_title.split(":", 1)[1].strip()
        
        soup = BeautifulSoup(u.get("reading", ""), "html.parser")
        
        story_paras = []
        for p in soup.find_all("p"):
            txt = p.text.strip()
            if txt and not p.get("class") and len(txt) > 25:
                story_paras.append(txt)
        story_text = "\n\n".join(story_paras)

        cur.execute("""
        INSERT OR REPLACE INTO units (book_id, unit_number, title, story)
        VALUES (?, ?, ?, ?)
        """, (book_num, unit_idx, unit_title, story_text))
        unit_id = cur.lastrowid or cur.execute("SELECT id FROM units WHERE book_id=? AND unit_number=?", (book_num, unit_idx)).fetchone()[0]

        word_elements = [li for li in soup.find_all("li") if li.get("word")]
        for w_idx, li in enumerate(word_elements, start=1):
            w = li.get("word", "").strip().lower()
            pro = li.get("pro", "").strip()
            if pro and not pro.startswith("/"):
                pro = f"/{pro}/"
            img_filename = li.get("img", "")
            
            divs = li.find_all("div")
            pos = ""
            pos_uz = ""
            def_text = ""
            ex_text = ""
            
            if divs:
                em = divs[0].find("em")
                if em:
                    pos = em.text.strip()
                    pos_uz = PART_OF_SPEECH_UZ.get(pos, pos)
                def_text = divs[0].text.strip()
                if pos and def_text.startswith(pos):
                    def_text = def_text[len(pos):].strip()
            
            if len(divs) > 1:
                ex_text = divs[1].text.strip()
            
            img_url = f"https://raw.githubusercontent.com/MohKardan/4000-Essential-English-Words/main/data/2nd-edition/book{book_num}/images/{img_filename}" if img_filename else ""
            audio_url = f"https://raw.githubusercontent.com/MohKardan/4000-Essential-English-Words/main/data/2nd-edition/book{book_num}/audio/{w}.mp3"

            parsed_words.append({
                "book_id": book_num,
                "unit_id": unit_id,
                "unit_number": unit_idx,
                "word_index": w_idx,
                "word": w,
                "phonetic": pro,
                "part_of_speech": pos,
                "part_of_speech_uz": pos_uz,
                "definition": def_text,
                "example": ex_text,
                "translation_uz": "",
                "image_url": img_url,
                "audio_url": audio_url
            })
            words_to_translate.append(w)

    print(f"[+] Kitob {book_num}: {len(flashcards)} ta unit, {len(parsed_words)} ta so'z tayyorlandi.", flush=True)

    if translate:
        print(f"[*] {len(words_to_translate)} ta so'z o'zbek tiliga parallel tarjima qilinmoqda...", flush=True)
        unique_words = list(dict.fromkeys(words_to_translate))
        word_map = {}
        
        def do_translate(word):
            return word, get_uzbek_translation(word)
        
        with ThreadPoolExecutor(max_workers=16) as executor:
            for w, uz in executor.map(do_translate, unique_words):
                word_map[w] = uz
        
        for item in parsed_words:
            item["translation_uz"] = word_map.get(item["word"], "")

    for item in parsed_words:
        cur.execute("""
        INSERT OR REPLACE INTO words 
        (book_id, unit_id, unit_number, word_index, word, phonetic, part_of_speech, 
         part_of_speech_uz, definition, example, translation_uz, image_url, audio_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["book_id"], item["unit_id"], item["unit_number"], item["word_index"],
            item["word"], item["phonetic"], item["part_of_speech"], item["part_of_speech_uz"],
            item["definition"], item["example"], item["translation_uz"], item["image_url"],
            item["audio_url"]
        ))
    
    conn.commit()
    print(f"[OK] Kitob {book_num} bazaga muvaffaqiyatli saqlandi!", flush=True)

def main():
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    start_b = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end_b = int(sys.argv[2]) if len(sys.argv) > 2 else start_b
    
    for b in range(start_b, end_b + 1):
        ingest_book(b, conn, translate=True)
        
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM words")
    total = cur.fetchone()[0]
    print(f"Bazadagi jami so'zlar: {total}", flush=True)
    conn.close()

if __name__ == "__main__":
    main()

"""
Configuration and constants for 4000 Essential English Words Telegram Bot
"""
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "7868753159:AAHBTJVkYXV_uHwIq796H0IJbAdPgZp6jsM")
DB_PATH = os.path.join(os.path.dirname(__file__), "essential_words.db")

# CEFR Levels and descriptions
BOOKS_INFO = {
    1: {
        "title": "Book 1 (A2 Elementary)",
        "badge": "🟢 Book 1",
        "cefr": "A2",
        "desc": "Boshlang'ich daraja. Kundalik va eng zarur 600 ta so'z.",
        "units": 30,
        "words": 600,
    },
    2: {
        "title": "Book 2 (B1 Pre-Intermediate)",
        "badge": "🟡 Book 2",
        "cefr": "B1",
        "desc": "O'rta-boshlang'ich daraja. Suhbat va matnlar uchun 600 ta so'z.",
        "units": 30,
        "words": 600,
    },
    3: {
        "title": "Book 3 (B1+ Intermediate)",
        "badge": "🟠 Book 3",
        "cefr": "B1+",
        "desc": "O'rta daraja. CEFR va IELTS tayyorgarligi uchun 600 ta so'z.",
        "units": 30,
        "words": 600,
    },
    4: {
        "title": "Book 4 (B2 Upper-Intermediate)",
        "badge": "🔵 Book 4",
        "cefr": "B2",
        "desc": "O'rtadan yuqori daraja. Akademik va jiddiy matnlar uchun 600 ta so'z.",
        "units": 30,
        "words": 600,
    },
    5: {
        "title": "Book 5 (B2+ Advanced)",
        "badge": "🟣 Book 5",
        "cefr": "B2+",
        "desc": "Yuqori daraja. IELTS 6.5-7.5+ va professional so'zlar.",
        "units": 30,
        "words": 600,
    },
    6: {
        "title": "Book 6 (C1 Proficiency)",
        "badge": "🔴 Book 6",
        "cefr": "C1",
        "desc": "Eng yuqori professional daraja. Murakkab akademik so'zlar.",
        "units": 30,
        "words": 600,
    },
    7: {
        "title": "Reading for the Real World 1",
        "badge": "📘 Book 7",
        "cefr": "B1",
        "desc": "Akademik o'qish va ilmiy mavzular (Compass Publishing).",
        "units": 3,
        "words": 45,
    },
    8: {
        "title": "Reading for the Real World 2",
        "badge": "📗 Book 8",
        "cefr": "B2",
        "desc": "Biznes, jamiyat va Jony Academy dasturidagi darslar.",
        "units": 2,
        "words": 30,
    },
    9: {
        "title": "IELTS & Academic Core",
        "badge": "📙 Book 9",
        "cefr": "C1",
        "desc": "IELTS 7.5 - 9.0 va ilmiy insholar uchun akademik so'zlar.",
        "units": 1,
        "words": 15,
    },
}

PART_OF_SPEECH_MAP = {
    "v.": "fe'l (verb)",
    "n.": "ot (noun)",
    "adj.": "sifat (adjective)",
    "adv.": "ravish (adverb)",
    "pron.": "olmosh (pronoun)",
    "prep.": "predlog (preposition)",
    "conj.": "bog'lovchi (conjunction)",
    "interj.": "undov (interjection)",
}

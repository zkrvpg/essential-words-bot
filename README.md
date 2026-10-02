# 📚 4000 Essential English Words - Telegram Ta'lim Boti

Ushbu bot Paul Nation tomonidan yaratilgan mashhur **"4000 Essential English Words" (2nd Edition)** darsliklar turkumidagi barcha 6 ta kitob va 180 ta unit so'zlarini interaktiv tarzda o'rganish, yodlash va mustahkamlash uchun mo'ljallangan.

Bot namuna sifatida keltirilgan `@Jonylearningbot` kabi zamonaviy **interaktiv oyna (Inline Keyboard UI)** va **🎓 Jony Academy** menyu tugmasi bilan to'liq jihozlangan.

---

## ✨ Kengaytirilgan Imkoniyatlar va Funksiyalar

### 1. 🎓 Chat Menyu Tugmasi (Jony Academy)
* Xabar yozish maydoni yonida **`🎓 Jony Academy`** ko'k oval tugmasi o'rnatilgan.
* Uni bosganda Telegram ichida to'liq interaktiv ta'lim mini-app ochiladi.
* Quyidagi barcha qulay komandalar menyuda mavjud:
  * `/start` — Asosiy interaktiv oyna
  * `/learn` — 📚 Kitoblar va Unitlar (Books 1-6)
  * `/practice` — 🎯 So'z yodlashning barcha usullari
  * `/battle` — ⚔️ Do'stlar bilan 1v1 Battle (Bellashuv)
  * `/cards` — 🗂 Flashcard usulida yodlash
  * `/quiz` — 🧠 4-Variantli Test
  * `/spelling` — ✍️ Yozma mashq (Spelling)
  * `/stats` — 📊 Statistika va TOP Reyting (Leaderboard)
  * `/search` — 🔍 Lug'atdan so'z qidirish
  * `/help` — ℹ️ Qo'llanma

### 2. 🎯 So'z Yodlash Usullari (5 xil usul):
1. 🗂 **Flashcard usuli (Kartochkalar):**
   * Kartaning old tomonida so'z va transkripsiyasi.
   * `🔄 Kartani aylantirish` bosilganda o'zbekcha tarjimasi, ta'rifi va misol gapi ochiladi.
   * `✅ Bilaman (+1)` yoki `❌ Bilmayman` (qayta takrorlash uchun saqlanadi).
2. 🧠 **4-Variantli Test (Quiz):**
   * Inglizcha ➡️ O'zbekcha va Ta'rif ➡️ So'zni topish savollari.
   * Darhol xato/to'g'ri javob tahlili.
3. ✍️ **Yozma Mashq (Spelling):**
   * O'zbekcha ma'nosi va andaza (`a _ _ _ e`) ko'rsatiladi.
   * So'zni chatga yozib yuborish orqali to'g'ri yozilishi xotirada qoladi.
4. 🔊 **Audio / Listening mashqi:**
   * So'zning haqiqiy native talaffuzi yangraydi, siz qaysi so'z ekanligini topasiz.
5. ⚔️ **Battle usuli:**
   * Vaqtga qarshi poyga orqali so'zlarni tez eslash ko'nikmasi.

### 3. ⚔️ Do'stlar bilan 1v1 Battle (Bellashuv):
* **👥 Do'stni jangga chaqirish:**
  * Bot sizga maxsus taklif havolasi beradi (`t.me/Bot_to_study_bot?start=battle_xxx`).
  * Do'stingiz havolani ochishi bilan ikkalangizga bir vaqtda 5 ta tezkor savol yuboriladi!
  * Kim ko'p va tez to'g'ri topsa — g'olib bo'ladi!
* **🤖 Bot AI bilan bellashuv:**
  * Do'stingiz yo'q vaqtda ham darhol Bot AI ga qarshi bellashishingiz mumkin.
* **⭐ Elo Reyting tizimi:**
  * G'alabalar uchun +25 reyting balli, mag'lubiyat uchun -15 ball.

### 4. 📊 Kengaytirilgan Statistika va TOP Reyting:
* Foydalanuvchi darajasi: 🌱 Beginner ➡️ 🥉 Intermediate ➡️ 🥈 Advanced ➡️ 🥇 Master ➡️ 💎 Grandmaster
* Vizual progress bar: `[████░░░░░░] 40%`
* 🔥 Kunlik streak (necha kun ketma-ket dars qilinayotgani)
* 🏆 **TOP 10 Leaderboard:**
  * Eng ko'p so'z yodlaganlar reytingi
  * Eng kuchli jangchilar reytingi

### 5. 💻 Kompyuter Yoqilganda Avtomatik Ishga Tushish (Autostart):
* Windows Startup papkasiga (`shell:startup`) silent fon rejimida ishga tushiruvchi `Start_4000_Words_Telegram_Bot.vbs` o'rnatilgan.
* Kompyuteringiz yonganda hech qanday qora oyna chiqmasdan, bot fonda avtomatik ishlayveradi!

---

## 📁 Loyiha Strukturasi

- `bot.py` — Telegram botning barcha interaktiv logikasi, battle va mashq rejimlari
- `database.py` — SQLite ma'lumotlar bazasi (3600 so'z, unitlar, janglar, reytinglar)
- `keyboards.py` — Inline va Reply tugmalar tizimi
- `config.py` — Sozlamalar va kitoblar ta'rifi
- `run_silent.vbs` — Fondagi yashirin ishga tushiruvchi VBScript
- `start_bot.bat` — Qo'lda ishga tushirish uchun qulay fayl

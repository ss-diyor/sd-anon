# Anon Message Bot

Foydalanuvchilar uchun toʻliq anonim koʻrinadigan, lekin owner (siz) uchun kim yozganini
bilish imkonini beruvchi Telegram bot. Har xil manba (bio, kanal, va h.k.) uchun alohida
kuzatiluvchi linklar yaratish imkoniyati bilan.

## Xususiyatlar

- 📩 Matn, rasm, video, ovozli xabar, fayl — barcha turdagi xabarlarni qabul qiladi
- 🔗 Har bir joy uchun alohida deep-link (`/newsource` orqali) — qaysi linkdan kim kelganini bilasiz
- 👤 Owner panelida har bir xabar ostida yuboruvchining ID/username'i koʻrinadi
- ↩️ Telegram'ning tabiiy **reply** funksiyasi orqali javob berish — javob foydalanuvchiga
  thread koʻrinishida yetadi
- 📊 `/stats` va `/sources` orqali statistikalarni koʻrish

## Ishga tushirish (lokal)

```bash
pip install -r requirements.txt
cp .env.example .env
# .env faylini toʻldiring: BOT_TOKEN, OWNER_ID, DATABASE_URL
python bot.py
```

## Railway'ga deploy

1. GitHub repo yarating va shu kodni push qiling
2. Railway'da **New Project → Deploy from GitHub repo**
3. **PostgreSQL** plaginini qoʻshing (Railway avtomatik `DATABASE_URL` beradi)
4. Environment Variables qoʻshing:
   - `BOT_TOKEN` — @BotFather'dan olingan token
   - `OWNER_ID` — sizning Telegram user ID'ingiz (masalan @userinfobot orqali biling)
   - `BOT_USERNAME` — bot username'i (@ belgisisiz)
5. Deploy qiling — `Procfile` avtomatik `python bot.py`ni ishga tushiradi

## Render'ga deploy

Ikki usul bor:

### A) `render.yaml` orqali (tavsiya etiladi — bir bosishda)

1. GitHub repo yarating va shu kodni (shu jumladan `render.yaml`ni) push qiling
2. Render Dashboard → **New → Blueprint** → repo'ni tanlang
3. Render `render.yaml`ni oʻqib, avtomatik **PostgreSQL** va **Background Worker** yaratadi
4. Sizdan `BOT_TOKEN`, `OWNER_ID`, `BOT_USERNAME` qiymatlarini kiritish soʻraladi (bular maxfiy boʻlgani uchun faylga yozilmagan)
5. Deploy tugmasini bosing

### B) Qoʻlda (GUI orqali)

1. Render Dashboard → **New → Background Worker** (⚠️ Web Service emas — bot HTTP portini eshitmaydi)
2. Repo'ni ulang
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `python bot.py`
5. Alohida **New → PostgreSQL** yarating, uning "Internal Connection String"'ini nusxalang
6. Worker'ning Environment sozlamalarida `BOT_TOKEN`, `OWNER_ID`, `BOT_USERNAME`, `DATABASE_URL` qoʻshing

**Eslatma:** Render'ning bepul PostgreSQL tarifi 90 kundan keyin oʻchib ketadi (Render siyosati) — uzoq muddatli foydalanish uchun pullik rejaga oʻtish yoki muddat yaqinlashganda bazani yangilash kerak boʻladi.

## Foydalanish

1. Botga `/start` yozing (owner sifatida) — qoʻllanma chiqadi
2. `/newsource bio Instagram bio` — yangi manba yaratadi, sizga link beradi
3. Shu linkni Instagram bio, kanal descriptionga joylashtiring
4. Kimdir link orqali kirib xabar yozsa — sizga keladi, kimligi va qaysi manbadan
   kelgani koʻrsatiladi
5. Javob berish uchun kelgan xabarga (yoki nusxasiga) oddiy **reply** qiling —
   bot avtomatik yuboruvchiga yetkazadi

## Muhim eslatma

Bot foydalanuvchilarga "toʻliq anonim" koʻrinadi, lekin owner panel orqali siz
kimligini bilasiz. Agar bu ochiq boʻlishini istasangiz, botning `/start` xabariga
(`handlers/user.py`) tegishli izohni qoʻshib qoʻying — bu foydalanuvchi ishonchini
saqlashga yordam beradi.

import asyncio
import sqlite3
import random
import hashlib
import logging
from groq import Groq
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

# ==================== SOZLAMALAR ====================
GROQ_API_KEY = "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"  # https://console.groq.com/keys
TELEGRAM_TOKEN = "8413537344:AAEXixgbU5wcvSiG5_N4J1QISNhWurjxpc4"
CHANNEL_ID = "@psixoboshqaruv" 
ADMIN_ID = 508914809

# Groq Client - juda tez! ⚡
groq_client = Groq(api_key=GROQ_API_KEY)
MODEL_ID = "llama-3.3-70b-versatile"  # Eng yaxshi model

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ==================== KENG MAVZULAR BAZASI ====================
PSYCHOLOGY_TOPICS = {
    'emotions': {
        'name': 'Hissiyotlar',
        'emoji': '😊',
        'topics': [
            "Qo'rquvni yengish strategiyalari",
            "G'azabni boshqarish texnikalari", 
            "Xursandchilik kimyosi va sirlari",
            "Tashvishdan qutulish usullari",
            "Hafsala pasti va uning yechimlari",
            "Sevgi psixologiyasi: ilmiy yondashuv",
            "Yolg'izlik bilan kurashish yo'llari",
            "Hasad va rashk hissi bilan ishlash",
            "Aybdorlik va uyat hissidan xalos bo'lish",
            "Empatiya va uning rivojlanishi"
        ]
    },
    'relationships': {
        'name': 'Munosabatlar',
        'emoji': '👥',
        'topics': [
            "Samarali muloqot san'ati",
            "Nikoh psixologiyasi va uyg'unlik sirlari", 
            "Ota-ona va farzand o'rtasidagi bog'",
            "Chin do'stlikni tanish",
            "Konfliktlarni konstruktiv hal qilish",
            "Ishonch va uning qayta tiklanishi",
            "Shaxsiy chegaralarni belgilash",
            "Toksik munosabatlardan chiqish",
            "Oilaviy muammolarni bartaraf etish",
            "Professional munosabatlar etiket"
        ]
    },
    'personal_growth': {
        'name': "O'z-o'zini rivojlantirish",
        'emoji': '🌱',
        'topics': [
            "Shaxsiy o'sish yo'l xaritasi",
            "SMART maqsadlar qo'yish texnikasi",
            "Motivatsiya manbalari va saqlash",
            "Vaqt menejementi: Eisenhower matritsasi",
            "O'z-o'ziga ishonchni mustahkamlash",
            "Karyera o'sishi strategiyalari",
            "Shaxsiy brending asoslari",
            "Liderlik ko'nikmalari",
            "Kreativlikni rivojlantirish",
            "Life-work balansini topish"
        ]
    },
    'mental_health': {
        'name': 'Mental salomatlik',
        'emoji': '🧠',
        'topics': [
            "Stressni boshqarish: ilmiy usullar",
            "Depressiya belgilari va yordam",
            "Sog'lom uyqu gigiyanasi qoidalari",
            "Meditatsiya va mindfulness amaliyoti",
            "Burnout sindromi va oldini olish",
            "Psixoterapiya turlari va tanlash",
            "Anksiete buzilishini tushunish",
            "Mental salomatlikni saqlash kundalik amaliyotlar",
            "Travma va tiklanish yo'llari",
            "Pandemiya davri psixologiyasi"
        ]
    },
    'cognitive': {
        'name': 'Kognitiv qobiliyatlar',
        'emoji': '🎯',
        'topics': [
            "Xotirani kuchaytirish texnikalari",
            "Diqqat konsentratsiyasini oshirish",
            "Tanqidiy fikrlash ko'nikmalari",
            "Ijodiy potentsialni ochish",
            "To'g'ri qaror qabul qilish modellari",
            "Kognitiv buzilishlar va korreksiya",
            "Miyani mashq qildirish o'yinlari",
            "O'qish tezligi va tushunish",
            "Multitasking xavfi",
            "Neyroplastiklik va miyani o'zgartirish"
        ]
    },
    'work_productivity': {
        'name': 'Ish va samaradorlik',
        'emoji': '💼',
        'topics': [
            "Prokrastinatsiyani yengish",
            "Pomodoro texnikasi va boshqalar",
            "Deep Work: chuqur ish rejimi",
            "Delegatsiya san'ati",
            "Prioritetlarni to'g'ri belgilash",
            "Yig'ilishlar samaradorligi",
            "Remote work psixologiyasi",
            "Stress management ishda",
            "Teamwork va hamkorlik",
            "Professional rivojlanish plani"
        ]
    },
    'habits_lifestyle': {
        'name': 'Odatlar va turmush tarzi',
        'emoji': '🔄',
        'topics': [
            "21 kunlik odat shakllantirish",
            "Yomon odatlarni buzish psixologiyasi",
            "Ertalabki tartib-qoidalar",
            "Sog'lom hayot tarzi asoslari",
            "Digital detox zaruriyati",
            "Minimalizm falsafasi",
            "Muvozanatli ovqatlanish va psixologiya",
            "Sport va mental salomatlik aloqasi",
            "Kundalik journaling faydasi",
            "Screen time bilan kurashish"
        ]
    },
    'communication': {
        'name': 'Kommunikatsiya',
        'emoji': '💬',
        'topics': [
            "Aktiv tinglash texnikasi",
            "Verbal bo'lmagan kommunikatsiya",
            "Assertivlik: o'z fikrini himoya qilish",
            "Public speaking qo'rquvini yengish",
            "Feedback berish va qabul qilish",
            "Manipulyatsiyalarni aniqlash",
            "Storytelling kuchi",
            "Cross-cultural kommunikatsiya",
            "Online muloqot odoblari",
            "Gaslighting va himoyalanish"
        ]
    },
    'children_teens': {
        'name': "Bolalar va o'smirlar",
        'emoji': '👶',
        'topics': [
            "Bolalar psixologiyasi asoslari",
            "O'smirlik inqirozi va yordam",
            "Maktab stressini kamaytirish",
            "Gadgetlar va bolalar miyasi",
            "Bully va unga qarshi kurash",
            "O'qishga motivatsiya qilish",
            "Bolalarda emosional intellekt",
            "ADHD: belgilar va yordam",
            "Ajralish va bolalarga ta'siri",
            "Ijobiy tarbiya prinsiplari"
        ]
    },
    'modern_issues': {
        'name': 'Zamonaviy muammolar',
        'emoji': '📱',
        'topics': [
            "Ijtimoiy tarmoqlar va mental salomatlik",
            "FOMO (Fear of Missing Out) sindrom",
            "Information overload muammosi",
            "Online dating psixologiyasi",
            "Zoom fatigue va yechimlari",
            "AI davr tashvishi",
            "Cancel culture va uning ta'siri",
            "Influencerlar ta'siri",
            "Fake news va tanqidiy fikrlash",
            "Digital nomad hayot tarzi"
        ]
    }
}

# ==================== MA'LUMOTLAR BAZASI ====================
def init_db():
    """Databazalarni yaratish va sozlash"""
    conn = sqlite3.connect('psixo_data.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            hash TEXT UNIQUE, 
            date TEXT,
            topic TEXT,
            category TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            added_date TEXT,
            priority INTEGER DEFAULT 0
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS used_topics (
            topic TEXT,
            used_date TEXT,
            category TEXT,
            success_rate REAL DEFAULT 0
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_type TEXT,
            topic TEXT,
            category TEXT,
            sent_date TEXT,
            views INTEGER DEFAULT 0,
            engagement REAL DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    logging.info("✅ Databaza muvaffaqiyatli sozlandi")

# ==================== AQLLI MAVZU TANLASH ====================
def get_smart_topic():
    """Eng mos mavzuni tanlash"""
    conn = sqlite3.connect('psixo_data.db')
    
    try:
        # 1. Admin navbatidan tekshirish
        queued = conn.execute(
            "SELECT id, topic FROM queue ORDER BY priority DESC, id ASC LIMIT 1"
        ).fetchone()
        
        if queued:
            topic = queued[1]
            conn.execute("DELETE FROM queue WHERE id=?", (queued[0],))
            conn.commit()
            logging.info(f"📋 Navbatdan: {topic}")
            return topic, "admin_queue"
        
        # 2. Oxirgi 60 kunda ishlatilmagan mavzular
        sixty_days_ago = (datetime.now() - timedelta(days=60)).isoformat()
        used_recently = conn.execute(
            "SELECT topic FROM used_topics WHERE used_date > ?",
            (sixty_days_ago,)
        ).fetchall()
        
        used_topics = set([row[0] for row in used_recently])
        
        # 3. Mavjud mavzularni yig'ish
        available_topics = []
        for category_key, category_data in PSYCHOLOGY_TOPICS.items():
            for topic in category_data['topics']:
                if topic not in used_topics:
                    available_topics.append({
                        'topic': topic,
                        'category': category_key,
                        'emoji': category_data['emoji']
                    })
        
        # 4. Agar bo'sh bo'lsa, eng eskisini olish
        if not available_topics:
            oldest = conn.execute(
                "SELECT topic, category FROM used_topics ORDER BY used_date ASC LIMIT 1"
            ).fetchone()
            
            if oldest:
                return oldest[0], oldest[1]
            else:
                category = random.choice(list(PSYCHOLOGY_TOPICS.keys()))
                topic = random.choice(PSYCHOLOGY_TOPICS[category]['topics'])
                return topic, category
        
        # 5. Kategoriyalar balansi
        category_usage = {}
        for category in PSYCHOLOGY_TOPICS.keys():
            count = conn.execute(
                "SELECT COUNT(*) FROM used_topics WHERE category=? AND used_date > ?",
                (category, sixty_days_ago)
            ).fetchone()[0]
            category_usage[category] = count
        
        min_usage_category = min(category_usage, key=category_usage.get)
        category_topics = [t for t in available_topics if t['category'] == min_usage_category]
        
        selected = random.choice(category_topics) if category_topics else random.choice(available_topics)
        
        # 6. Saqlash
        conn.execute(
            "INSERT INTO used_topics (topic, used_date, category) VALUES (?, ?, ?)",
            (selected['topic'], datetime.now().isoformat(), selected['category'])
        )
        conn.commit()
        
        logging.info(f"🎯 Tanlandi: {selected['topic']}")
        return selected['topic'], selected['category']
        
    except Exception as e:
        logging.error(f"❌ Mavzu tanlashda xato: {e}")
        category = random.choice(list(PSYCHOLOGY_TOPICS.keys()))
        topic = random.choice(PSYCHOLOGY_TOPICS[category]['topics'])
        return topic, category
    finally:
        conn.close()

def get_category_info(category_key):
    """Kategoriya ma'lumotlari"""
    if category_key in PSYCHOLOGY_TOPICS:
        return PSYCHOLOGY_TOPICS[category_key]
    return {'name': 'Umumiy', 'emoji': '📌'}

# ==================== GROQ AI GENERATSIYA ====================
async def generate_with_groq(prompt, max_retries=3):
    """Groq AI bilan kontent yaratish"""
    
    for attempt in range(max_retries):
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Sen professional psixolog va yozuvchisan. O'zbek tilida mukammal yozassan. Matnda * va _ belgilarini ishlatma."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=MODEL_ID,
                temperature=0.8,
                max_tokens=2048,
                top_p=1
            )
            
            return chat_completion.choices[0].message.content
        
        except Exception as e:
            error_msg = str(e)
            
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                wait_time = 60 * (attempt + 1)
                logging.warning(f"⏳ Limit. {wait_time}s kutish...")
                await asyncio.sleep(wait_time)
                if attempt < max_retries - 1:
                    continue
            
            logging.error(f"❌ Groq xatosi: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5)
                continue
            else:
                raise e
    
    raise Exception("Maksimal urinishlar tugadi")

# ==================== POST YARATISH ====================
async def generate_and_post(forced_type=None):
    """Post yaratish va yuborish"""
    
    hour = datetime.now().hour
    if forced_type:
        hour_map = {"morning": 8, "fact": 12, "article": 16, "quote": 21}
        hour = hour_map.get(forced_type, hour)
    
    signature = "\n\n---\n📌 @psixoboshqaruv 👈🏻 obuna bo'ling!"
    prompt = ""
    post_mode = "text"
    post_type = ""
    topic = ""
    category = "general"
    
    try:
        # ERTALAB (07:00-10:00)
        if 7 <= hour <= 10 or forced_type == "morning":
            post_type = "morning"
            current_date = datetime.now().strftime("%d %B")
            
            prompt = f"""Quyidagi formatda ertalabki motivatsion xabar yoz:

🌅 XAYRLI TONG!

📅 {current_date}

💭 [Kuchli motivatsion iqtibos]

✨ Bugungi vazifa: [Amaliy tavsiya]

O'zbek tilida, 120 so'zgacha."""
        
        # FAKT (11:00-14:00)
        elif 11 <= hour <= 14 or forced_type == "fact":
            post_type = "fact"
            
            prompt = """Quyidagi formatda psixologik fakt yoz:

💡 BILASIZMI?

📍 [Qiziqarli psixologik fakt]

🔬 Ilmiy izoh: [Qisqa tushuntirish]

💼 Amaliy foyda: [Hayotda qo'llash]

O'zbek tilida, 150 so'zgacha."""
        
        # MAQOLA (15:00-18:00)
        elif 15 <= hour <= 18 or forced_type == "article":
            post_type = "article"
            post_mode = "photo"
            
            topic, category = get_smart_topic()
            category_info = get_category_info(category)
            
            prompt = f"""Mavzu: {topic}

Quyidagi formatda maqola yoz:

{category_info['emoji']} {topic.upper()}

Kirish:
[Muammo - 2 jumla]

Asosiy qism:
1️⃣ [Birinchi jihat]
2️⃣ [Ikkinchi jihat]
3️⃣ [Uchinchi jihat]

Amaliy tavsiyalar:
✅ [Tavsiya 1]
✅ [Tavsiya 2]
✅ [Tavsiya 3]

Xulosa:
[Xulosaviy fikr]

O'zbek tilida, 200 so'zgacha, professional."""
        
        # IQTIBOS (19:00-23:00)
        elif 19 <= hour <= 23 or forced_type == "quote":
            post_type = "quote"
            
            prompt = """Quyidagi formatda kechki xabar yoz:

🌙 KECHQURUN UCHUN

💭 "[Chuqur iqtibos]"

— [Muallif]

🎯 Fikr yuritish uchun:
[Bu iqtibosdan nima o'rganish mumkin - 2 jumla]

✨ Ertaga yanada yaxshi bo'ling!

O'zbek tilida, 100 so'zgacha."""
        
        # KONTENT YARATISH
        if prompt:
            logging.info(f"🤖 Groq AI ishlamoqda... ({post_type})")
            
            content_text = await generate_with_groq(prompt)
            
            # Tozalash
            safe_text = content_text.replace("_", "").replace("*", "").replace("[", "").replace("]", "")
            
            # Takrorlanish tekshiruvi
            content_hash = hashlib.md5(safe_text.encode()).hexdigest()
            conn = sqlite3.connect('psixo_data.db')
            
            existing = conn.execute("SELECT * FROM history WHERE hash=?", (content_hash,)).fetchone()
            
            if existing:
                logging.warning("⚠️ Takroriy kontent, qayta yaratilmoqda...")
                conn.close()
                return await generate_and_post(forced_type)
            
            # Saqlash
            topic_used = topic if post_type == "article" else post_type
            category_used = category if post_type == "article" else "general"
            
            conn.execute(
                "INSERT INTO history (hash, date, topic, category) VALUES (?, ?, ?, ?)",
                (content_hash, datetime.now().isoformat(), topic_used, category_used)
            )
            conn.commit()
            conn.close()
            
            # YUBORISH
            if post_mode == "photo":
                photo_url = f"https://picsum.photos/1200/630?random={random.randint(1,10000)}"
                msg = await bot.send_photo(
                    CHANNEL_ID,
                    photo=photo_url,
                    caption=safe_text[:1000] + signature
                )
                logging.info(f"✅ Maqola yuborildi! (ID: {msg.message_id})")
            else:
                msg = await bot.send_message(CHANNEL_ID, safe_text + signature)
                logging.info(f"✅ Post yuborildi! (ID: {msg.message_id})")
            
            # Statistika
            conn = sqlite3.connect('psixo_data.db')
            conn.execute(
                "INSERT INTO statistics (post_type, topic, category, sent_date) VALUES (?, ?, ?, ?)",
                (post_type, topic_used, category_used, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
            
    except Exception as e:
        logging.error(f"❌ Xatolik: {e}")
        try:
            await bot.send_message(
                ADMIN_ID,
                f"⚠️ BOT XATOSI\n\n🕐 {datetime.now().strftime('%H:%M')}\n❌ {str(e)[:150]}"
            )
        except:
            pass

# ==================== ADMIN BUYRUQLARI ====================

@dp.message(Command("start"))
async def start_command(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "🧠 **Psixologiya Bot**\n\n"
            "/add <mavzu> - Navbatga qo'shish\n"
            "/queue - Navbat\n"
            "/test - Test\n"
            "/stats - Statistika\n"
            "/topics - Mavzular\n"
            "/history - Tarix"
        )
    else:
        await message.answer(
            "👋 Assalomu alaykum!\n\n"
            "📢 @psixoboshqaruv kanaliga obuna bo'ling!"
        )

@dp.message(Command("add"))
async def add_to_queue(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    topic = message.text.replace("/add", "").strip()
    if not topic:
        await message.answer("❌ Mavzu kiriting!\nMisol: /add Stressni boshqarish")
        return
    
    try:
        conn = sqlite3.connect('psixo_data.db')
        conn.execute(
            "INSERT INTO queue (topic, added_date) VALUES (?, ?)",
            (topic, datetime.now().isoformat())
        )
        conn.commit()
        total = conn.execute("SELECT COUNT(*) FROM queue").fetchone()[0]
        conn.close()
        
        await message.answer(f"✅ Qo'shildi!\n\n📝 {topic}\n📊 Navbatda: {total} ta")
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")

@dp.message(Command("queue"))
async def show_queue(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    conn = sqlite3.connect('psixo_data.db')
    queued = conn.execute(
        "SELECT id, topic, added_date FROM queue ORDER BY id ASC"
    ).fetchall()
    conn.close()
    
    if not queued:
        await message.answer("📭 Navbat bo'sh")
        return
    
    response = "📋 **NAVBAT:**\n\n"
    for i, (qid, topic, date) in enumerate(queued, 1):
        response += f"{i}. {topic}\n   🕐 {date[:10]}\n\n"
    
    await message.answer(response)

@dp.message(Command("test"))
async def test_post(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="🌅 Ertalab", callback_data="test_morning"),
            types.InlineKeyboardButton(text="💡 Fakt", callback_data="test_fact")
        ],
        [
            types.InlineKeyboardButton(text="📝 Maqola", callback_data="test_article"),
            types.InlineKeyboardButton(text="💭 Iqtibos", callback_data="test_quote")
        ]
    ])
    
    await message.answer("🧪 Test post:", reply_markup=keyboard)

@dp.callback_query(lambda c: c.data.startswith("test_"))
async def process_test(callback: types.CallbackQuery):
    test_type = callback.data.replace("test_", "")
    await callback.message.edit_text("⏳ Tayyorlanmoqda...")
    
    try:
        await generate_and_post(forced_type=test_type)
        await callback.message.edit_text("✅ Yuborildi!")
    except Exception as e:
        await callback.message.edit_text(f"❌ {e}")

@dp.message(Command("stats"))
async def show_statistics(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    conn = sqlite3.connect('psixo_data.db')
    total_posts = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    week_posts = conn.execute(
        "SELECT COUNT(*) FROM history WHERE date > ?", (week_ago,)
    ).fetchone()[0]
    queue_count = conn.execute("SELECT COUNT(*) FROM queue").fetchone()[0]
    conn.close()
    
    await message.answer(
        f"📊 **STATISTIKA**\n\n"
        f"📝 Jami: {total_posts}\n"
        f"📅 7 kun: {week_posts}\n"
        f"📋 Navbat: {queue_count}"
    )

@dp.message(Command("topics"))
async def show_topics(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    response = "📚 **MAVZULAR**\n\n"
    total = 0
    for category_key, category_data in PSYCHOLOGY_TOPICS.items():
        response += f"{category_data['emoji']} {category_data['name']}: {len(category_data['topics'])}\n"
        total += len(category_data['topics'])
    
    response += f"\n🎯 Jami: {total} ta"
    await message.answer(response)

@dp.message(Command("history"))
async def show_history(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    conn = sqlite3.connect('psixo_data.db')
    recent = conn.execute(
        "SELECT topic, category, date FROM history ORDER BY date DESC LIMIT 10"
    ).fetchall()
    conn.close()
    
    if not recent:
        await message.answer("📭 Hali postlar yo'q")
        return
    
    response = "📜 **OXIRGI POSTLAR:**\n\n"
    for topic, category, date in recent:
        cat_info = get_category_info(category)
        response += f"{cat_info.get('emoji', '📌')} {topic}\n   🕐 {date[:16]}\n\n"
    
    await message.answer(response)

# ==================== ISHGA TUSHIRISH ====================
async def main():
    init_db()
    
    scheduler = AsyncIOScheduler(timezone="Asia/Tashkent")
    
    post_times = [
        (8, 0, "morning"),
        (12, 0, "fact"),
        (16, 0, "article"),
        (21, 0, "quote")
    ]
    
    for hour, minute, post_type in post_times:
        scheduler.add_job(
            generate_and_post,
            'cron',
            hour=hour,
            minute=minute,
            args=[post_type],
            id=f'post_{post_type}'
        )
        logging.info(f"⏰ {post_type}: {hour:02d}:{minute:02d}")
    
    scheduler.start()
    
    logging.info("=" * 50)
    logging.info("🚀 BOT ISHGA TUSHDI! (Groq AI)")
    logging.info(f"📊 Mavzular: {sum(len(cat['topics']) for cat in PSYCHOLOGY_TOPICS.values())}")
    logging.info(f"⚡ Model: {MODEL_ID}")
    logging.info("=" * 50)
    
    try:
        await bot.send_message(
            ADMIN_ID,
            f"✅ Bot ishga tushdi!\n\n"
            f"⚡ Groq AI ({MODEL_ID})\n"
            f"📊 Mavzular: {sum(len(cat['topics']) for cat in PSYCHOLOGY_TOPICS.values())}\n"
            f"📢 {CHANNEL_ID}"
        )
    except:
        pass
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 To'xtatildi")
    except Exception as e:

        logging.error(f"❌ Fatal: {e}")

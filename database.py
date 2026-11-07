import sqlite3
from datetime import date, timedelta

DB_NAME = "tour_agency.db"

class DatabaseManager:
    def get_connection(self):
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        return conn

    def count_tours(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tours")
            return cursor.fetchone()[0]

    def get_all_tours(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tours")
            return cursor.fetchall()

    def add_tour(self, name, destination, city, stars, start_date, end_date, base_price, room_type, meal_type, max_people, description="", reviews="", weather="☀️ +28°C, вода +24°C"):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO tours (name, destination, city, stars, start_date, end_date, base_price_per_person, room_type, meal_type, max_people, description, reviews, weather)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, destination, city, stars, str(start_date), str(end_date), base_price, room_type, meal_type, max_people, description, reviews, weather))
            conn.commit()

    def get_favorites_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT tour_id FROM favorites")
            return [row[0] for row in cursor.fetchall()]

    def add_favorite_db(self, tour_id):
        with self.get_connection() as conn:
            conn.execute("INSERT OR IGNORE INTO favorites (tour_id) VALUES (?)", (tour_id,))
            conn.commit()

    def remove_favorite_db(self, tour_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM favorites WHERE tour_id = ?", (tour_id,))
            conn.commit()

    def add_booking_db(self, tour_id, tour_name, traveler_name, passport, phone, adults, children, total_price):
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO bookings (tour_id, tour_name, traveler_name, passport, phone, adults, children, total_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (tour_id, tour_name, traveler_name, passport, phone, adults, children, total_price))
            conn.commit()

    def update_booking_db(self, booking_id, traveler_name, passport, phone, adults, children, total_price):
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE bookings 
                SET traveler_name = ?, passport = ?, phone = ?, adults = ?, children = ?, total_price = ?
                WHERE id = ?
            """, (traveler_name, passport, phone, adults, children, total_price, booking_id))
            conn.commit()

    def delete_booking_db(self, booking_id):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
            conn.commit()

    def get_all_bookings(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bookings")
            return [dict(row) for row in cursor.fetchall()]


def init_db_with_samples():
    db = DatabaseManager()
    with db.get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tours (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                destination TEXT,
                city TEXT,
                stars INTEGER,
                start_date TEXT,
                end_date TEXT,
                base_price_per_person REAL,
                room_type TEXT,
                meal_type TEXT,
                max_people INTEGER,
                description TEXT,
                reviews TEXT,
                weather TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                tour_id INTEGER PRIMARY KEY
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tour_id INTEGER,
                tour_name TEXT,
                traveler_name TEXT,
                passport TEXT,
                phone TEXT,
                adults INTEGER,
                children INTEGER,
                total_price REAL
            )
        """)
        conn.commit()

    if db.count_tours() < 10:
        with db.get_connection() as conn:
            conn.execute("DELETE FROM tours")
            conn.commit()

        today = date.today()
        samples = [
            ("Rixos Premium Tekirova 5*", "Турция", "Кемер", 5, today + timedelta(days=5), today + timedelta(days=15), 3200, "double", "AI", 8, "Роскошный курорт у подножия гор Тахталы. Собственный пляж и аквапарк.", "★ 4.9/5 — Потрясающий сервис и питание!", "☀️ Воздух +30°C, вода +25°C"),
            ("The Land of Legends Kingdom 5*", "Турция", "Белек", 5, today + timedelta(days=10), today + timedelta(days=20), 4100, "family", "AI", 8, "Тематический отель-парк развлечений. Бесплатный доступ к аттракционам.", "★ 4.8/5 — Дети в восторге от парка!", "☀️ Воздух +31°C, вода +26°C"),
            ("Burj Al Arab Jumeirah 7*", "ОАЭ", "Дубай", 5, today + timedelta(days=20), today + timedelta(days=27), 12500, "double", "BB", 6, "Легендарный отель-парус. Трансфер на Rolls-Royce, дворецкий.", "★ 5.0/5 — Высший уровень роскоши.", "☀️ Воздух +35°C, вода +28°C"),
            ("Atlantis The Royal 5*", "ОАЭ", "Дубай", 5, today + timedelta(days=25), today + timedelta(days=32), 9800, "double", "BB", 6, "Самый премиальный отель на Palm Jumeirah. Панорамный бассейн Cloud 22.", "★ 4.9/5 — Лучшие виды в Дубае.", "☀️ Воздух +35°C, вода +28°C"),
            ("Kuramathi Maldives 4*", "Мальдивы", "Мале", 4, today + timedelta(days=30), today + timedelta(days=40), 8900, "double", "AI", 6, "Остров-курорт с косой 1.5 км. Водные виллы, риф с акулами.", "★ 4.9/5 — Настоящий рай на земле.", "☀️ Воздух +30°C, вода +29°C"),
            ("Rixos Premium Magawish 5*", "Египет", "Хургада", 5, today + timedelta(days=8), today + timedelta(days=18), 2900, "double", "AI", 8, "Люкс-отель с виллами у бассейна и лучшим коралловым рифом.", "★ 4.7/5 — Отличное море и дайвинг.", "☀️ Воздух +32°C, вода +26°C"),
            ("Banyan Tree Phuket 5*", "Таиланд", "Пхукет", 5, today + timedelta(days=22), today + timedelta(days=32), 6100, "double", "BB", 6, "Премиальные виллы с собственными бассейнами в саду.", "★ 4.7/5 — Очень уединенно и красивейшая природа.", "☀️ Воздух +31°C, вода +28°C"),
            ("Mitsis Alila Resort 5*", "Греция", "Родос", 5, today + timedelta(days=12), today + timedelta(days=22), 4300, "double", "AI", 6, "Первая линия Эгейского моря с ультра всё включено.", "★ 4.8/5 — Прекрасная кухня и чистейшее море.", "☀️ Воздух +29°C, вода +24°C"),
            ("Hotel Danieli Venice 5*", "Италия", "Венеция", 5, today + timedelta(days=14), today + timedelta(days=21), 6900, "double", "BB", 4, "Готический дворец XIV века рядом с площадью Сан-Марко.", "★ 4.7/5 — Настоящий венецианский шарм.", "⛅ Воздух +24°C, вода +20°C"),
            ("Le Meurice 5*", "Франция", "Париж", 5, today + timedelta(days=6), today + timedelta(days=13), 7800, "double", "BB", 4, "Дворец напротив Тюильри с рестораном от Алена Дюкасса.", "★ 4.9/5 — Атмосфера классического Парижа.", "⛅ Воздух +22°C"),
            ("W Barcelona 5*", "Испания", "Барселона", 5, today + timedelta(days=35), today + timedelta(days=42), 5800, "double", "BB", 6, "Символ пляжа Барселонета в форме паруса. Бар на крыше.", "★ 4.7/5 — Отличный тусовочный вариант.", "☀️ Воздух +27°C, вода +23°C"),
            ("Aman Tokyo 5*", "Япония", "Токио", 5, today + timedelta(days=20), today + timedelta(days=28), 9200, "double", "BB", 4, "Традиционный стиль в современной башне с видами на Фудзи.", "★ 5.0/5 — Незабываемый отдых в Токио.", "🌤️ Воздух +23°C"),
            ("Royalton Hicacos 5*", "Куба", "Гавана", 5, today + timedelta(days=14), today + timedelta(days=24), 3600, "double", "AI", 6, "Курорт на белоснежном пляже Варадеро.", "★ 4.6/5 — Прекрасный океан и ром.", "☀️ Воздух +30°C, вода +27°C"),
            ("Ayana Resort Bali 5*", "Индонезия", "Бали", 5, today + timedelta(days=15), today + timedelta(days=25), 4900, "double", "BB", 6, "Курорт на скале над океаном с легендарным Rock Bar.", "★ 4.9/5 — Лучшие закаты на Бали.", "☀️ Воздух +30°C, вода +28°C"),
            ("Four Seasons Lion Palace 5*", "Россия", "Санкт-Петербург", 5, today + timedelta(days=5), today + timedelta(days=12), 3100, "double", "BB", 4, "Отель-дворец XIX века у Исаакиевского собора.", "★ 4.9/5 — Великолепный Петербург.", "⛅ Воздух +20°C")
        ]
        for item in samples:
            db.add_tour(*item)
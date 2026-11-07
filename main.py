from datetime import datetime, date
import os
import csv
from database import DatabaseManager, init_db_with_samples

init_db_with_samples()

class Tour:
    def __init__(self, id, name, destination, city, stars, start_date, end_date, base_price, room_type, meal_type, max_people, description="", reviews="", weather="☀️ +28°C, вода +24°C"):
        self.id = id
        self.name = name
        self.destination = destination
        self.city = city
        self.stars = stars
        self.start_date = start_date if isinstance(start_date, date) else datetime.strptime(str(start_date), "%Y-%m-%d").date()
        self.end_date = end_date if isinstance(end_date, date) else datetime.strptime(str(end_date), "%Y-%m-%d").date()
        self.base_price = base_price
        self.room_type = room_type
        self.meal_type = meal_type
        self.max_people = max_people
        self.description = description
        self.reviews = reviews
        self.weather = weather

class ClientRequest:
    def __init__(self, destination="Все страны", city="Все города", adults=2, children=0, max_budget=None, extra_services=None, transport_type="✈️ Самолет", transport_class="Эконом"):
        self.destination = destination
        self.city = city
        self.adults = adults
        self.children = children
        self.max_budget = max_budget
        self.extra_services = extra_services or []
        self.transport_type = transport_type
        self.transport_class = transport_class

class BookingRecord:
    def __init__(self, tour_id, tour_name, traveler_name, passport, phone, adults, children, total_price):
        self.tour_id = tour_id
        self.tour_name = tour_name
        self.traveler_name = traveler_name
        self.passport = passport
        self.phone = phone
        self.adults = adults
        self.children = children
        self.total_price = total_price

class TourService:
    def __init__(self):
        self.favorites = set()
        self.tours = []
        self.reload_tours()
        self.reload_favorites()

    def reload_tours(self):
        db = DatabaseManager()
        rows = db.get_all_tours()
        self.tours = []
        for r in rows:
            r_dict = dict(r)
            tour = Tour(
                id=r_dict.get("id"), 
                name=r_dict.get("name"), 
                destination=r_dict.get("destination"),
                city=r_dict.get("city"), 
                stars=r_dict.get("stars"),
                start_date=r_dict.get("start_date"), 
                end_date=r_dict.get("end_date"),
                base_price=r_dict.get("base_price_per_person"), 
                room_type=r_dict.get("room_type"),
                meal_type=r_dict.get("meal_type"), 
                max_people=r_dict.get("max_people"),
                description=r_dict.get("description", ""),
                reviews=r_dict.get("reviews", "Отзывов пока нет."),
                weather=r_dict.get("weather", "☀️ Сезон отличный, +27°C")
            )
            self.tours.append(tour)

    def reload_favorites(self):
        db = DatabaseManager()
        self.favorites = set(db.get_favorites_db())

    def get_destinations(self):
        dests = sorted(list(set(t.destination for t in self.tours)))
        return ["Все страны"] + dests

    def get_cities(self, destination=None):
        if not destination or destination == "Все страны":
            cities = [t.city for t in self.tours]
        else:
            cities = [t.city for t in self.tours if destination.lower() in t.destination.lower()]
        return ["Все города"] + sorted(list(set(cities)))

    def toggle_favorite(self, tour_id):
        db = DatabaseManager()
        if tour_id in self.favorites:
            self.favorites.remove(tour_id)
            db.remove_favorite_db(tour_id)
        else:
            self.favorites.add(tour_id)
            db.add_favorite_db(tour_id)

    def get_favorite_tours(self):
        return [t for t in self.tours if t.id in self.favorites]

    def add_booking(self, booking: BookingRecord):
        db = DatabaseManager()
        db.add_booking_db(
            booking.tour_id, str(booking.tour_name), str(booking.traveler_name),
            str(booking.passport), str(booking.phone), int(booking.adults),
            int(booking.children), float(booking.total_price)
        )

    def update_booking(self, booking_id, traveler_name, passport, phone, adults, children, total_price):
        db = DatabaseManager()
        db.update_booking_db(booking_id, str(traveler_name), str(passport), str(phone), int(adults), int(children), float(total_price))

    def delete_booking(self, booking_id):
        db = DatabaseManager()
        db.delete_booking_db(booking_id)

    def get_all_bookings(self):
        db = DatabaseManager()
        return db.get_all_bookings()

    def search(self, req: ClientRequest):
        results = []
        total_tourists = req.adults + req.children

        transport_type_mult = {
            "✈️ Самолет": 1.0,
            "🚌 Автобус": 0.6,
            "🚗 Автомобиль": 0.8,
            "🚢 Лайнер": 1.4
        }.get(req.transport_type, 1.0)

        transport_class_mult = {
            "Эконом": 1.0,
            "Комфорт": 1.25,
            "Бизнес-класс": 1.7,
            "V.I.P.": 2.5
        }.get(req.transport_class, 1.0)

        t_mult = transport_type_mult * transport_class_mult

        for tour in self.tours:
            if req.destination and req.destination != "Все страны":
                if req.destination.lower() not in tour.destination.lower():
                    continue

            if req.city and req.city != "Все города":
                if req.city.lower() not in tour.city.lower():
                    continue

            nights = (tour.end_date - tour.start_date).days
            if nights <= 0: nights = 7

            total_pp = (tour.base_price or 0.0) * (nights / 7.0)
            extra_cost = 0
            if "страховка" in req.extra_services: extra_cost += 350 * total_tourists
            if "трансфер" in req.extra_services: extra_cost += 1200
            if "экскурсии" in req.extra_services: extra_cost += 2500 * total_tourists

            base_total = (total_pp * req.adults) + (total_pp * 0.5 * req.children) + extra_cost
            total_price = base_total * t_mult

            if req.max_budget is not None and total_price > req.max_budget:
                continue

            results.append({
                "tour": tour,
                "total_price": total_price,
                "nights": nights
            })

        return results

    def get_currency_symbol(self, currency):
        return {"RUB": "₽", "USD": "$", "EUR": "€"}.get(currency, "RUB")

    def convert_price(self, price_rub, currency):
        rates = {"RUB": 1.0, "USD": 0.011, "EUR": 0.010}
        return price_rub * rates.get(currency, 1.0)


def generate_travel_voucher(booking_record, filename="tour_voucher.pdf"):
    from PyQt6.QtGui import QTextDocument, QPdfWriter
    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 30px; border: 2px solid #e11d48; border-radius: 12px; max-width: 600px; margin: auto; background-color: #fff5f5;">
        <h1 style="color: #e11d48; text-align: center;">✈️ TRAVELFINDER PRO</h1>
        <h2 style="text-align: center; color: #1f2937;">ТУРИСТИЧЕСКИЙ ВАУЧЕР № {booking_record.tour_id}</h2>
        <hr style="border: 1px solid #fecdd3;">
        <p><b>🏨 Забронированный отель:</b> {booking_record.tour_name}</p>
        <p><b>📌 Статус:</b> <span style="color: #059669; font-weight: bold;">ПОДТВЕРЖДЕНО И ОПЛАЧЕНО</span></p>
        <br>
        <h3 style="color: #4b5563; border-bottom: 1px solid #fecdd3; padding-bottom: 5px;">Данные туриста:</h3>
        <p><b>👤 ФИО:</b> {booking_record.traveler_name}</p>
        <p><b>🛂 Паспортные данные:</b> {booking_record.passport}</p>
        <p><b>📞 Телефон для связи:</b> {booking_record.phone}</p>
        <p><b>👥 Состав тура:</b> Взрослых — {booking_record.adults}, Детей — {booking_record.children}</p>
        <br>
        <div style="background-color: #e11d48; color: white; padding: 15px; border-radius: 8px; text-align: center; font-size: 14pt;">
            <b>Итоговая стоимость: {booking_record.total_price:,.2f} ₽</b>
        </div>
        <p style="text-align: center; font-size: 9pt; color: #9ca3af; margin-top: 30px;">
            Спасибо, что выбрали TravelFinder Pro! Желаем вам незабываемого путешествия.
        </p>
    </div>
    """
    doc = QTextDocument()
    doc.setHtml(html_content)
    pdf_path = os.path.abspath(filename)
    writer = QPdfWriter(pdf_path)
    doc.print_(writer)
    return pdf_path


def export_bookings_to_excel(filename="bookings_report.csv"):
    """Экспорт в формат CSV (с разделителем-запятой для идеального открытия в Excel двойным кликом)"""
    db = DatabaseManager()
    bookings = db.get_all_bookings()
    
    filepath = os.path.abspath(filename)
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(["ID", "ID Тура", "Название тура", "ФИО Туриста", "Паспорт", "Телефон", "Взрослых", "Детей", "Сумма (₽)"])
        for b in bookings:
            writer.writerow([
                b.get("id"),
                b.get("tour_id"),
                b.get("tour_name"),
                b.get("traveler_name"),
                b.get("passport"),
                b.get("phone"),
                b.get("adults"),
                b.get("children"),
                b.get("total_price")
            ])
    return filepath
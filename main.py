from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class TourPackage:
    """Класс, представляющий туристический пакет"""
    id: int
    name: str                       # Название тура / отеля
    destination: str                # Направление
    start_date: date
    end_date: date
    base_price_per_person: float    # Базовая цена за человека
    room_type: str                  # single / double / family
    meal_type: str                  # RO / BB / HB / AI
    max_people: int
    description: str = ""


@dataclass
class ClientRequest:
    """Класс, представляющий запрос клиента"""
    destination: str
    start_date: date
    end_date: date
    adults: int
    children: int = 0
    preferred_room: Optional[str] = None
    preferred_meal: Optional[str] = None
    max_budget: Optional[float] = None
    extra_services: List[str] = field(default_factory=list)
    

def get_sample_tours() -> List[TourPackage]:
    """Возвращает список тестовых туристических пакетов"""
    return [
        TourPackage(1, "Солнечный берег Deluxe", "Болгария",
                    date(2025, 6, 10), date(2025, 6, 20),
                    1850, "double", "AI", 4, "Отель 4*, первый берег"),

        TourPackage(2, "Анталия All Inclusive", "Турция",
                    date(2025, 7, 5), date(2025, 7, 15),
                    2400, "double", "AI", 4, "Отель 5*, ультра все включено"),

        TourPackage(3, "Египет Хургада", "Египет",
                    date(2025, 5, 15), date(2025, 5, 25),
                    1950, "double", "AI", 3, "Отель 4*, коралловый риф"),

        TourPackage(4, "Греция Крит Family", "Греция",
                    date(2025, 8, 1), date(2025, 8, 12),
                    3200, "family", "HB", 5, "Семейный отель, анимация"),

        TourPackage(5, "Тунис бюджетный", "Тунис",
                    date(2025, 6, 20), date(2025, 6, 30),
                    1450, "double", "BB", 3, "Отель 3*, хороший пляж"),

        TourPackage(6, "ОАЭ Дубай", "ОАЭ",
                    date(2025, 9, 10), date(2025, 9, 17),
                    4100, "double", "BB", 2, "Отель 5*, центр Дубая"),

        TourPackage(7, "Черногория Будва", "Черногория",
                    date(2025, 7, 12), date(2025, 7, 22),
                    2100, "double", "HB", 4, "Вид на море"),

        TourPackage(8, "Испания Барселона", "Испания",
                    date(2025, 8, 5), date(2025, 8, 15),
                    2800, "double", "BB", 3, "Центр города"),
    ]

class TourService:
    """Сервис поиска туров и расчёта стоимости"""

    def __init__(self, tours: List[TourPackage]):
        self.tours = tours

    def search(self, request: ClientRequest) -> List[dict]:
        """Поиск подходящих туров + расчёт стоимости"""
        results = []

        for tour in self.tours:
            if not self._is_suitable(tour, request):
                continue

            price = self.calculate_price(tour, request)

            # Фильтр по бюджету
            if request.max_budget and price > request.max_budget:
                continue

            results.append({
                "tour": tour,
                "total_price": round(price, 2),
                "price_per_person": round(price / (request.adults + request.children), 2)
            })

        # Сортировка по цене
        results.sort(key=lambda x: x["total_price"])
        return results

    def _is_suitable(self, tour: TourPackage, request: ClientRequest) -> bool:
        """Проверяет, подходит ли тур под запрос клиента"""
        # Направление
        if request.destination.lower() not in tour.destination.lower():
            return False

        # Даты (тур должен покрывать запрошенный период)
        if tour.start_date > request.start_date or tour.end_date < request.end_date:
            return False

        # Количество мест
        total_people = request.adults + request.children
        if total_people > tour.max_people:
            return False

        # Предпочтения по номеру и питанию
        if request.preferred_room and request.preferred_room != tour.room_type:
            return False
        if request.preferred_meal and request.preferred_meal != tour.meal_type:
            return False

        return True

    def calculate_price(self, tour: TourPackage, request: ClientRequest) -> float:
        """Расчёт итоговой стоимости тура"""
        adults_price = tour.base_price_per_person * request.adults
        children_price = tour.base_price_per_person * 0.7 * request.children

        base = adults_price + children_price

        # Коэффициент питания
        meal_coeffs = {"RO": 1.0, "BB": 1.1, "HB": 1.25, "AI": 1.4}
        meal_coeff = meal_coeffs.get(tour.meal_type, 1.0)

        # Коэффициент типа номера
        room_coeffs = {"single": 1.3, "double": 1.0, "family": 0.95}
        room_coeff = room_coeffs.get(tour.room_type, 1.0)

        # Сезонный коэффициент
        season_coeff = self._get_season_coefficient(tour.start_date)

        total = base * meal_coeff * room_coeff * season_coeff

        # Дополнительные услуги
        extra_prices = {
            "страховка": 350 * (request.adults + request.children),
            "трансфер": 1200,
            "экскурсии": 2500
        }
        for service in request.extra_services:
            total += extra_prices.get(service.lower(), 0)

        # Скидка за раннее бронирование
        if (tour.start_date - date.today()).days > 60:
            total *= 0.95

        return total

    def _get_season_coefficient(self, start: date) -> float:
        """Возвращает сезонный коэффициент"""
        month = start.month
        if month in [6, 7, 8]:      # высокий сезон
            return 1.25
        elif month in [5, 9]:       # средний сезон
            return 1.1
        else:
            return 1.0
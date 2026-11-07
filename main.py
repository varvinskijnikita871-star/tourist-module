from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Dict, Any


@dataclass
class TourPackage:
    """Туристический пакет"""
    id: int
    name: str
    destination: str
    start_date: date
    end_date: date
    base_price_per_person: float
    room_type: str
    meal_type: str
    max_people: int
    description: str = ""

    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days

    def __str__(self) -> str:
        return (
            f"{self.name} ({self.destination}) | "
            f"{self.start_date.strftime('%d.%m.%Y')} - {self.end_date.strftime('%d.%m.%Y')} | "
            f"{self.base_price_per_person:.0f} руб./чел."
        )


@dataclass
class ClientRequest:
    """Запрос клиента"""
    destination: str
    start_date: date
    end_date: date
    adults: int
    children: int = 0
    preferred_room: Optional[str] = None
    preferred_meal: Optional[str] = None
    max_budget: Optional[float] = None
    min_budget: Optional[float] = None
    extra_services: List[str] = field(default_factory=list)
    name_query: Optional[str] = None

    @property
    def total_people(self) -> int:
        return self.adults + self.children

    def validate(self) -> None:
        if not self.destination.strip():
            raise ValueError("Направление не может быть пустым")
        if self.end_date <= self.start_date:
            raise ValueError("Дата возвращения должна быть позже даты выезда")
        if self.adults < 1:
            raise ValueError("Должен быть хотя бы 1 взрослый")
        if self.children < 0:
            raise ValueError("Количество детей не может быть отрицательным")
        if self.max_budget is not None and self.max_budget < 0:
            raise ValueError("Максимальный бюджет не может быть отрицательным")
        if self.min_budget is not None and self.min_budget < 0:
            raise ValueError("Минимальный бюджет не может быть отрицательным")


class TourService:
    """Сервис поиска туров и расчёта стоимости"""

    MEAL_COEFFS = {"RO": 1.0, "BB": 1.1, "HB": 1.25, "AI": 1.4}
    ROOM_COEFFS = {"single": 1.3, "double": 1.0, "family": 0.95}
    EXTRA_PRICES = {
        "страховка": 350,
        "трансфер": 1200,
        "экскурсии": 2500,
    }
    CHILD_COEFF = 0.7
    EARLY_BOOKING_DAYS = 60
    EARLY_BOOKING_DISCOUNT = 0.05

    def __init__(self, tours: List[TourPackage]):
        self.tours = tours

    # ---------- поиск ----------
    def search(self, request: ClientRequest) -> List[Dict[str, Any]]:
        request.validate()
        results = []

        for tour in self.tours:
            if not self._is_suitable(tour, request):
                continue

            price = self.calculate_price(tour, request)

            if request.max_budget is not None and price > request.max_budget:
                continue
            if request.min_budget is not None and price < request.min_budget:
                continue

            if request.name_query:
                if request.name_query.lower() not in tour.name.lower():
                    continue

            results.append({
                "tour": tour,
                "total_price": round(price, 2),
                "price_per_person": round(price / max(request.total_people, 1), 2),
                "breakdown": self.get_price_breakdown(tour, request),
            })

        results.sort(key=lambda x: x["total_price"])
        return results

    def _is_suitable(self, tour: TourPackage, request: ClientRequest) -> bool:
        if request.destination.lower() not in tour.destination.lower():
            return False
        if tour.start_date > request.start_date or tour.end_date < request.end_date:
            return False
        if request.total_people > tour.max_people:
            return False
        if request.preferred_room and request.preferred_room != tour.room_type:
            return False
        if request.preferred_meal and request.preferred_meal != tour.meal_type:
            return False
        return True

    # ---------- цена ----------
    def calculate_price(self, tour: TourPackage, request: ClientRequest) -> float:
        adults_price = tour.base_price_per_person * request.adults
        children_price = tour.base_price_per_person * self.CHILD_COEFF * request.children
        base = adults_price + children_price

        meal_coeff = self.MEAL_COEFFS.get(tour.meal_type, 1.0)
        room_coeff = self.ROOM_COEFFS.get(tour.room_type, 1.0)
        season_coeff = self._get_season_coefficient(tour.start_date)

        total = base * meal_coeff * room_coeff * season_coeff
        total += self._extras_cost(request)

        if self._is_early_booking(tour.start_date):
            total *= (1 - self.EARLY_BOOKING_DISCOUNT)

        return total

    def get_price_breakdown(self, tour: TourPackage, request: ClientRequest) -> dict:
        adults_price = tour.base_price_per_person * request.adults
        children_price = tour.base_price_per_person * self.CHILD_COEFF * request.children
        base = adults_price + children_price

        meal_coeff = self.MEAL_COEFFS.get(tour.meal_type, 1.0)
        room_coeff = self.ROOM_COEFFS.get(tour.room_type, 1.0)
        season_coeff = self._get_season_coefficient(tour.start_date)

        after_coeffs = base * meal_coeff * room_coeff * season_coeff
        extras_total = self._extras_cost(request)
        total = after_coeffs + extras_total

        early_discount = 0.0
        if self._is_early_booking(tour.start_date):
            early_discount = total * self.EARLY_BOOKING_DISCOUNT
            total *= (1 - self.EARLY_BOOKING_DISCOUNT)

        return {
            "base_adults": round(adults_price, 2),
            "base_children": round(children_price, 2),
            "meal_coeff": meal_coeff,
            "room_coeff": room_coeff,
            "season_coeff": season_coeff,
            "extras": round(extras_total, 2),
            "early_discount": round(early_discount, 2),
            "total": round(total, 2),
        }

    def _extras_cost(self, request: ClientRequest) -> float:
        total = 0.0
        for service in request.extra_services:
            key = service.lower()
            if key == "страховка":
                total += self.EXTRA_PRICES["страховка"] * request.total_people
            else:
                total += self.EXTRA_PRICES.get(key, 0)
        return total

    def _get_season_coefficient(self, start: date) -> float:
        month = start.month
        if month in (6, 7, 8):
            return 1.25
        if month in (5, 9):
            return 1.10
        return 1.0

    def _is_early_booking(self, start: date) -> bool:
        return (start - date.today()).days > self.EARLY_BOOKING_DAYS

    # ---------- справочники / аналитика ----------
    def get_destinations(self) -> List[str]:
        return sorted(set(t.destination for t in self.tours))

    def get_tour_by_id(self, tour_id: int) -> Optional[TourPackage]:
        for tour in self.tours:
            if tour.id == tour_id:
                return tour
        return None

    def get_tours_by_destination(self, destination: str) -> List[TourPackage]:
        d = destination.lower()
        return [t for t in self.tours if d in t.destination.lower()]

    def get_statistics(self, results: List[Dict[str, Any]]) -> dict:
        if not results:
            return {"count": 0}
        prices = [r["total_price"] for r in results]
        cheapest = min(results, key=lambda x: x["total_price"])
        expensive = max(results, key=lambda x: x["total_price"])
        return {
            "count": len(results),
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": sum(prices) / len(prices),
            "cheapest_name": cheapest["tour"].name,
            "expensive_name": expensive["tour"].name,
        }

    def get_tour_info(self, tour: TourPackage) -> str:
        return (
            f"{tour.name}\n"
            f"  Направление: {tour.destination}\n"
            f"  Даты: {tour.start_date.strftime('%d.%m.%Y')} — {tour.end_date.strftime('%d.%m.%Y')}\n"
            f"  Длительность: {tour.duration_days} дн.\n"
            f"  Номер: {tour.room_type} | Питание: {tour.meal_type}\n"
            f"  Макс. человек: {tour.max_people}\n"
            f"  Базовая цена: {tour.base_price_per_person:,.0f} руб./чел.\n"
            f"  {tour.description}"
        )


def parse_date(text: str) -> date:
    """Преобразует строку ДД.ММ.ГГГГ в date"""
    from datetime import datetime
    try:
        return datetime.strptime(text.strip(), "%d.%m.%Y").date()
    except ValueError:
        raise ValueError("Неверный формат даты. Используйте ДД.ММ.ГГГГ")
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
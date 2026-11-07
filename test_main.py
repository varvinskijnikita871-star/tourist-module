import pytest
from datetime import date, timedelta
from main import TourPackage, ClientRequest, TourService, parse_date
from data import get_sample_tours


@pytest.fixture
def service():
    return TourService(get_sample_tours())


def test_parse_date_valid():
    assert parse_date("05.07.2025") == date(2025, 7, 5)


def test_parse_date_invalid():
    with pytest.raises(ValueError):
        parse_date("2025-07-05")


def test_search_found(service):
    # Берем дату из первого доступного тура в базе данных для надежности теста
    tour = service.tours[0]
    request = ClientRequest(
        destination=tour.destination,
        start_date=tour.start_date,
        end_date=tour.end_date,
        adults=2,
        children=0
    )
    results = service.search(request)
    assert len(results) > 0
    assert results[0]["tour"].destination == tour.destination


def test_search_not_found(service):
    request = ClientRequest(
        destination="НесуществующаяСтрана999",
        start_date=date.today() + timedelta(days=10),
        end_date=date.today() + timedelta(days=20),
        adults=2
    )
    results = service.search(request)
    assert len(results) == 0


def test_price_calculation(service):
    tour = service.tours[1]
    request = ClientRequest(
        destination=tour.destination,
        start_date=tour.start_date,
        end_date=tour.end_date,
        adults=2,
        children=0
    )
    price = service.calculate_price(tour, request)
    assert price > 0


def test_children_discount(service):
    tour = service.tours[1]
    request_adults = ClientRequest(tour.destination, tour.start_date, tour.end_date, adults=2, children=0)
    request_with_child = ClientRequest(tour.destination, tour.start_date, tour.end_date, adults=1, children=1)

    price1 = service.calculate_price(tour, request_adults)
    price2 = service.calculate_price(tour, request_with_child)
    assert price2 < price1


def test_budget_filter(service):
    tour = service.tours[0]
    request = ClientRequest(
        destination=tour.destination,
        start_date=tour.start_date,
        end_date=tour.end_date,
        adults=2,
        max_budget=10  # слишком маленький бюджет
    )
    results = service.search(request)
    assert len(results) == 0


def test_max_people(service):
    tour = service.tours[0]
    request = ClientRequest(
        destination=tour.destination,
        start_date=tour.start_date,
        end_date=tour.end_date,
        adults=20  # слишком много людей
    )
    results = service.search(request)
    assert len(results) == 0


def test_season_coefficient(service):
    coeff_high = service._get_season_coefficient(date(2026, 7, 1))
    coeff_low = service._get_season_coefficient(date(2026, 1, 1))
    assert coeff_high > coeff_low


def test_extra_services(service):
    tour = service.tours[1]
    request = ClientRequest(
        destination=tour.destination,
        start_date=tour.start_date,
        end_date=tour.end_date,
        adults=2,
        extra_services=["страховка"]
    )
    price_with = service.calculate_price(tour, request)

    request.extra_services = []
    price_without = service.calculate_price(tour, request)

    assert price_with > price_without
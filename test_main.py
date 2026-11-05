import pytest
from datetime import date
from main import TourPackage, ClientRequest, TourService, get_sample_tours, parse_date


@pytest.fixture
def service():
    return TourService(get_sample_tours())


def test_parse_date_valid():
    assert parse_date("05.07.2025") == date(2025, 7, 5)


def test_parse_date_invalid():
    with pytest.raises(ValueError):
        parse_date("2025-07-05")


def test_search_found(service):
    request = ClientRequest(
        destination="Турция",
        start_date=date(2025, 7, 5),
        end_date=date(2025, 7, 15),
        adults=2,
        children=1
    )
    results = service.search(request)
    assert len(results) > 0
    assert results[0]["tour"].destination == "Турция"


def test_search_not_found(service):
    request = ClientRequest(
        destination="Япония",
        start_date=date(2025, 7, 5),
        end_date=date(2025, 7, 15),
        adults=2
    )
    results = service.search(request)
    assert len(results) == 0


def test_price_calculation(service):
    tour = get_sample_tours()[1]  # Анталия
    request = ClientRequest(
        destination="Турция",
        start_date=date(2025, 7, 5),
        end_date=date(2025, 7, 15),
        adults=2,
        children=0
    )
    price = service.calculate_price(tour, request)
    assert price > 0


def test_children_discount(service):
    tour = get_sample_tours()[1]
    request_adults = ClientRequest("Турция", date(2025, 7, 5), date(2025, 7, 15), adults=2, children=0)
    request_with_child = ClientRequest("Турция", date(2025, 7, 5), date(2025, 7, 15), adults=1, children=1)

    price1 = service.calculate_price(tour, request_adults)
    price2 = service.calculate_price(tour, request_with_child)
    assert price2 < price1


def test_budget_filter(service):
    request = ClientRequest(
        destination="Турция",
        start_date=date(2025, 7, 5),
        end_date=date(2025, 7, 15),
        adults=2,
        max_budget=1000  # слишком маленький бюджет
    )
    results = service.search(request)
    assert len(results) == 0


def test_max_people(service):
    request = ClientRequest(
        destination="Турция",
        start_date=date(2025, 7, 5),
        end_date=date(2025, 7, 15),
        adults=10  # слишком много людей
    )
    results = service.search(request)
    assert len(results) == 0


def test_season_coefficient(service):
    coeff_high = service._get_season_coefficient(date(2025, 7, 1))
    coeff_low = service._get_season_coefficient(date(2025, 1, 1))
    assert coeff_high > coeff_low


def test_extra_services(service):
    tour = get_sample_tours()[1]
    request = ClientRequest(
        destination="Турция",
        start_date=date(2025, 7, 5),
        end_date=date(2025, 7, 15),
        adults=2,
        extra_services=["страховка"]
    )
    price_with = service.calculate_price(tour, request)

    request.extra_services = []
    price_without = service.calculate_price(tour, request)

    assert price_with > price_without
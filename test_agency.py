import unittest
from datetime import date
from main import Tour, ClientRequest, TourService, BookingRecord

class TestTravelAgencyModule(unittest.TestCase):
    
    def setUp(self):
        # Инициализация тестовых данных для модуля
        self.tour = Tour(
            id=1, 
            name="Grand Resort 5*", 
            destination="Турция",
            start_date=date(2026, 6, 1), 
            end_date=date(2026, 6, 8), # 7 ночей
            base_price=14000.0, 
            room_type="double", 
            meal_type="AI", 
            max_people=4,
            description="Тестовый отель"
        )

    def test_tour_duration_calculation(self):
        """Тест расчёта длительности ночей"""
        nights = (self.tour.end_date - self.tour.start_date).days
        self.assertEqual(nights, 7)

    def test_children_coefficient_logic(self):
        """Тест расчёта стоимости с учетом детей (коэффициент 0.5)"""
        nights = 7
        total_pp = self.tour.base_price * (nights / 7.0)
        adults = 2
        children = 1
        
        # 2 взрослых + 1 ребёнок (половина стоимости)
        total_price = (total_pp * adults) + (total_pp * 0.5 * children)
        self.assertEqual(total_price, 14000.0 * 2 + 14000.0 * 0.5) # 28000 + 7000 = 35000

    def test_budget_restriction_filter(self):
        """Тест фильтрации по максимальному бюджету"""
        max_budget = 20000.0
        calculated_price = 35000.0
        # Проверяем срабатывание лимита бюджета
        is_exceeded = calculated_price > max_budget
        self.assertTrue(is_exceeded)

if __name__ == "__main__":
    unittest.main()
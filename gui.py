import sys
import random
from datetime import datetime, timedelta
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, 
    QLineEdit, QComboBox, QSpinBox, QCheckBox, QTextEdit, 
    QHBoxLayout, QVBoxLayout, QStackedWidget, QScrollArea, 
    QMessageBox, QFrame, QDialog, QFormLayout, QSlider,
    QTableWidget, QTableWidgetItem, QHeaderView
)

from main import ClientRequest, TourService, BookingRecord, generate_travel_voucher, export_bookings_to_excel
from database import DatabaseManager, init_db_with_samples

LANG_TEXTS = {
    "Русский": {
        "brand": "✦ TravelFinder",
        "search": "🔍  Поиск туров",
        "fav": "⭐  Избранное",
        "all": "🌐  Каталог отелей",
        "admin": "⚡  Управление и брони",
        "settings": "⚙️  Настройки",
        "ai": "🤖  Ковбой-Ассистент",
    },
    "English": {
        "brand": "✦ TravelFinder",
        "search": "🔍  Tour Search",
        "fav": "⭐  Favorites",
        "all": "🌐  Hotel Catalog",
        "admin": "⚡  Admin & Bookings",
        "settings": "⚙️  Settings",
        "ai": "🤖  Cowboy Assistant",
    },
    "Español": {
        "brand": "✦ TravelFinder",
        "search": "🔍  Buscar Tурes",
        "fav": "⭐  Favoritos",
        "all": "🌐  Catálogo de Hoteles",
        "admin": "⚡  Gestión y Reservas",
        "settings": "⚙️  Ajustes",
        "ai": "🤖  Asistente Vaquero",
    }
}


class HotelDetailDialog(QDialog):
    def __init__(self, tour, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Информация об отеле: {tour.name}")
        self.resize(540, 480)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel(f"🏨 {tour.name} ({'⭐' * tour.stars})")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #e11d48;")
        layout.addWidget(title)

        info = QLabel(f"📍 Страна: {tour.destination}   •   Город: {tour.city}\n🛏 Номер: {tour.room_type}   •   🍽 Питание: {tour.meal_type}\n👥 Вместимость: {tour.max_people} чел.\n💳 Базовая цена: {tour.base_price:,.0f} ₽")
        info.setStyleSheet("font-size: 11pt;")
        layout.addWidget(info)

        weather_lbl = QLabel(f"<b>🌤 Прогноз погоды на курорте:</b> {tour.weather}")
        weather_lbl.setStyleSheet("color: #0284c7; background-color: #f0f9ff; padding: 10px; border-radius: 8px; border: 1px solid #bae6fd;")
        layout.addWidget(weather_lbl)

        desc = QLabel(f"<b>Описание:</b> {tour.description if tour.description else 'Описание отсутствует.'}")
        desc.setWordWrap(True)
        desc.setStyleSheet("padding: 12px; border-radius: 8px; border: 1px solid #d1d5db;")
        layout.addWidget(desc)

        rev = QLabel(f"💬 <b>Рейтинг и отзывы:</b>\n{tour.reviews}")
        rev.setWordWrap(True)
        rev.setStyleSheet("color: #9f1239; padding: 12px; border-radius: 8px; border: 1px solid #fecdd3;")
        layout.addWidget(rev)

        close_btn = QPushButton("Закрыть")
        close_btn.setObjectName("PrimaryButton")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class HotelCompareDialog(QDialog):
    def __init__(self, tours, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Сравнение выбранных отелей")
        self.resize(800, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("⚖️ Сравнение отелей бок о бок")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #e11d48; margin-bottom: 10px;")
        layout.addWidget(title)

        table = QTableWidget()
        table.setRowCount(6)
        table.setColumnCount(len(tours) + 1)
        table.setHorizontalHeaderLabels(["Параметр"] + [t.name for t in tours])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        rows_data = [
            ("Страна / Город", lambda t: f"{t.destination}, {t.city}"),
            ("Звёздность", lambda t: "⭐" * t.stars),
            ("Базовая цена", lambda t: f"{t.base_price:,.0f} ₽"),
            ("Тип номера", lambda t: t.room_type),
            ("Питание", lambda t: t.meal_type),
            ("Погода", lambda t: t.weather)
        ]

        for r_idx, (param_name, func) in enumerate(rows_data):
            table.setItem(r_idx, 0, QTableWidgetItem(param_name))
            for c_idx, tour in enumerate(tours, 1):
                table.setItem(r_idx, c_idx, QTableWidgetItem(str(func(tour))))

        layout.addWidget(table)
        
        close_btn = QPushButton("Закрыть")
        close_btn.setObjectName("PrimaryButton")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class BookingDialog(QDialog):
    def __init__(self, tour_name, price, currency_symbol, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Регистрация и оформление брони")
        self.resize(520, 440)
        self.setModal(True)

        layout = QFormLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel(f"🏨 {tour_name}")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #e11d48;")
        layout.addRow(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ФИО туриста")
        layout.addRow("ФИО туриста:", self.name_input)

        self.passport_input = QLineEdit()
        self.passport_input.setPlaceholderText("Номер паспорта")
        layout.addRow("Серия и номер паспорта:", self.passport_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Телефон")
        layout.addRow("Телефон для связи:", self.phone_input)

        price_lbl = QLabel(f"{price:,.2f} {currency_symbol}")
        price_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        price_lbl.setStyleSheet("color: #e11d48;")
        layout.addRow("Итого к оплате:", price_lbl)

        btn_layout = QHBoxLayout()
        confirm_btn = QPushButton("Подтвердить бронирование")
        confirm_btn.setObjectName("PrimaryButton")
        confirm_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "passport": self.passport_input.text(),
            "phone": self.phone_input.text()
        }


class TourApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.service = TourService()
        self.last_results = []
        self.currency = "RUB"
        self.language = "Русский"
        self.theme = "Тёмная (Красный неон)"

        self.apply_theme()
        self.init_ui()

    def get_text(self, key):
        return LANG_TEXTS.get(self.language, LANG_TEXTS["Русский"]).get(key, key)

    def apply_theme(self):
        if self.theme == "Тёмная (Красный неон)":
            theme_qss = """
                QMainWindow { background-color: #030712; }
                QWidget { color: #f3f4f6; font-family: 'Segoe UI', Arial; font-size: 10.5pt; }
                .Sidebar { background-color: #0b0f19; border-right: 2px solid #881337; }
                .Card { background-color: #0d111d; border-radius: 12px; border: 1px solid #be123c; }
                QLabel { color: #f3f4f6; }
                QLineEdit, QComboBox, QSpinBox { background-color: #111827; color: #ffffff; border: 1px solid #be123c; border-radius: 8px; padding: 8px 12px; }
                QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 2px solid #f43f5e; background-color: #030712; }
                QComboBox QAbstractItemView { background-color: #111827; color: #ffffff; selection-background-color: #e11d48; }
                QCheckBox { color: #f3f4f6; spacing: 8px; font-weight: 500; }
                QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #be123c; border-radius: 4px; background: #111827; }
                QCheckBox::indicator:checked { background: #e11d48; border-color: #f43f5e; }
                QPushButton { background-color: #1c0a10; color: #ffffff; border: 1px solid #be123c; border-radius: 8px; padding: 9px 15px; font-weight: bold; }
                QPushButton:hover { background-color: #e11d48; border-color: #f43f5e; }
                QPushButton#SidebarButton { background-color: transparent; color: #9ca3af; border: none; text-align: left; padding: 12px 16px; border-radius: 8px; font-weight: bold; font-size: 10.5pt; }
                QPushButton#SidebarButton:hover { background-color: #881337; color: #ffffff; }
                QPushButton#SidebarButton[active="true"] { background-color: #e11d48; color: #ffffff; }
                QPushButton#PrimaryButton { background-color: #e11d48; color: #ffffff; border: 1px solid #f43f5e; border-radius: 8px; font-size: 10.5pt; padding: 10px; }
                QPushButton#PrimaryButton:hover { background-color: #be123c; border-color: #ffffff; }
                QPushButton#DangerButton { background-color: #111827; color: #f43f5e; border: 1px solid #f43f5e; border-radius: 8px; }
                QPushButton#DangerButton:hover { background-color: #f43f5e; color: #ffffff; }
                QTextEdit { background-color: #111827; color: #ffffff; border: 1px solid #be123c; border-radius: 8px; padding: 10px; }
                QTableWidget { background-color: #0b0f19; color: #ffffff; gridline-color: #881337; border: 1px solid #be123c; border-radius: 8px; }
                QHeaderView::section { background-color: #1c0a10; color: #f43f5e; font-weight: bold; border: 1px solid #be123c; padding: 6px; }
            """
        else:
            theme_qss = """
                QMainWindow { background-color: #f8fafc; }
                QWidget { color: #0f172a; font-family: 'Segoe UI', Arial; font-size: 10.5pt; }
                .Sidebar { background-color: #ffffff; border-right: 1px solid #cbd5e1; }
                .Card { background-color: #ffffff; border-radius: 12px; border: 1px solid #cbd5e1; }
                QLabel { color: #0f172a; }
                QLineEdit, QComboBox, QSpinBox { background-color: #ffffff; color: #0f172a; border: 1px solid #94a3b8; border-radius: 8px; padding: 8px 12px; font-weight: 500; }
                QLineEdit:focus, QComboBox:focus, QSpinBox:focus { border: 2px solid #e11d48; background-color: #ffffff; }
                QComboBox QAbstractItemView { background-color: #ffffff; color: #0f172a; selection-background-color: #f43f5e; selection-color: #ffffff; }
                QCheckBox { color: #0f172a; spacing: 8px; font-weight: 600; }
                QCheckBox::indicator { width: 18px; height: 18px; border: 1px solid #94a3b8; border-radius: 4px; background: #ffffff; }
                QCheckBox::indicator:checked { background: #e11d48; border-color: #e11d48; }
                QPushButton { background-color: #f1f5f9; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 8px; padding: 9px 15px; font-weight: bold; }
                QPushButton:hover { background-color: #e2e8f0; border-color: #94a3b8; }
                QPushButton#SidebarButton { background-color: transparent; color: #334155; border: none; text-align: left; padding: 12px 16px; border-radius: 8px; font-weight: bold; font-size: 10.5pt; }
                QPushButton#SidebarButton:hover { background-color: #f1f5f9; color: #e11d48; }
                QPushButton#SidebarButton[active="true"] { background-color: #e11d48; color: #ffffff; }
                QPushButton#PrimaryButton { background-color: #e11d48; color: #ffffff; border: 1px solid #be123c; border-radius: 8px; font-size: 10.5pt; padding: 10px; }
                QPushButton#PrimaryButton:hover { background-color: #be123c; }
                QPushButton#DangerButton { background-color: #ffffff; color: #e11d48; border: 1px solid #e11d48; border-radius: 8px; }
                QPushButton#DangerButton:hover { background-color: #e11d48; color: #ffffff; }
                QTextEdit { background-color: #ffffff; color: #0f172a; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; }
                QTableWidget { background-color: #ffffff; color: #0f172a; gridline-color: #e2e8f0; border: 1px solid #cbd5e1; border-radius: 8px; }
                QHeaderView::section { background-color: #f1f5f9; color: #1e293b; font-weight: bold; border: 1px solid #cbd5e1; padding: 6px; }
            """
        self.setStyleSheet(theme_qss)

    def init_ui(self):
        self.setWindowTitle("TravelFinder Pro — Ultimate Edition")
        self.resize(1650, 950)
        self.setMinimumSize(1300, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = QWidget()
        self.sidebar.setProperty("class", "Sidebar")
        self.sidebar.setFixedWidth(260)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(16, 24, 16, 24)
        self.sidebar_layout.setSpacing(8)

        self.brand_lbl = QLabel(self.get_text("brand"))
        self.brand_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.brand_lbl.setStyleSheet("color: #e11d48; margin-bottom: 20px;")
        self.sidebar_layout.addWidget(self.brand_lbl)

        self.nav_buttons = {}
        self.nav_keys = [
            ("search", "search"),
            ("fav", "fav"),
            ("all", "all"),
            ("admin", "admin"),
            ("settings", "settings"),
            ("ai", "ai")
        ]

        for key, text_key in self.nav_keys:
            btn = QPushButton(self.get_text(text_key))
            btn.setObjectName("SidebarButton")
            btn.clicked.connect(lambda checked, k=key: self.switch_view(k))
            self.sidebar_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        self.sidebar_layout.addStretch()
        main_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent; border: none;")

        self.search_page = self.create_search_view()
        self.fav_page = self.create_fav_view()
        self.all_page = self.create_all_view()
        self.admin_page = self.create_admin_view()
        self.settings_page = self.create_settings_view()
        self.ai_page = self.create_ai_view()

        self.stack.addWidget(self.search_page)
        self.stack.addWidget(self.fav_page)
        self.stack.addWidget(self.all_page)
        self.stack.addWidget(self.admin_page)
        self.stack.addWidget(self.settings_page)
        self.stack.addWidget(self.ai_page)

        main_layout.addWidget(self.stack)
        self.switch_view("search")

    def update_ui_texts(self):
        self.brand_lbl.setText(self.get_text("brand"))
        for key, text_key in self.nav_keys:
            if key in self.nav_buttons:
                self.nav_buttons[key].setText(self.get_text(text_key))

    def create_floating_assistant_widget(self, parent_layout):
        assistant_frame = QFrame()
        assistant_frame.setMaximumHeight(50)
        assistant_frame.setStyleSheet("QFrame { background: rgba(225, 29, 72, 0.08); border: 1px solid #e11d48; border-radius: 8px; }")
        h_layout = QHBoxLayout(assistant_frame)
        h_layout.setContentsMargins(12, 4, 12, 4)
        
        icon_lbl = QLabel("🤠")
        icon_lbl.setFont(QFont("Segoe UI", 12))
        h_layout.addWidget(icon_lbl)
        
        text_lbl = QLabel("<b>Ковбой-помощник:</b> Нужна помощь с поиском или подбором?")
        text_lbl.setStyleSheet("font-size: 9.5pt;")
        h_layout.addWidget(text_lbl)
        
        help_btn = QPushButton("Спросить")
        help_btn.setFixedSize(90, 30)
        help_btn.setObjectName("PrimaryButton")
        help_btn.clicked.connect(lambda: self.switch_view("ai"))
        h_layout.addWidget(help_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        parent_layout.addWidget(assistant_frame)

    def switch_view(self, key):
        views = {"search": 0, "fav": 1, "all": 2, "admin": 3, "settings": 4, "ai": 5}
        self.stack.setCurrentIndex(views[key])

        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.setProperty("active", "true")
            else:
                btn.setProperty("active", "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if key == "fav": self.load_favorites()
        elif key == "all": self.load_all_catalog()
        elif key == "admin": 
            self.update_admin_tour_combo()
            self.refresh_admin_text()

    # 1. Поиск туров
    def create_search_view(self):
        widget = QWidget()
        main_vbox = QVBoxLayout(widget)
        main_vbox.setContentsMargins(24, 20, 24, 16)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        filter_card = QFrame()
        filter_card.setProperty("class", "Card")
        filter_card.setFixedWidth(420)
        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setContentsMargins(18, 18, 18, 18)
        filter_layout.setSpacing(10)

        f_title = QLabel("⚡ ПОИСК ТУРОВ И ОТЕЛЕЙ")
        f_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        f_title.setStyleSheet("color: #e11d48;")
        filter_layout.addWidget(f_title)

        filter_layout.addWidget(QLabel("СТРАНА"))
        self.destination_cb = QComboBox()
        self.update_destination_combo()
        self.destination_cb.currentTextChanged.connect(self.update_city_combo)
        filter_layout.addWidget(self.destination_cb)

        filter_layout.addWidget(QLabel("ГОРОД"))
        self.city_cb = QComboBox()
        self.update_city_combo()
        filter_layout.addWidget(self.city_cb)

        trans_layout = QHBoxLayout()
        vbox_type = QVBoxLayout()
        vbox_type.addWidget(QLabel("ВИД ТРАНСПОРТА"))
        self.transport_type_cb = QComboBox()
        self.transport_type_cb.addItems(["✈️ Самолет", "🚌 Автобус", "🚗 Автомобиль", "🚢 Лайнер"])
        vbox_type.addWidget(self.transport_type_cb)

        vbox_class = QVBoxLayout()
        vbox_class.addWidget(QLabel("КЛАСС"))
        self.transport_class_cb = QComboBox()
        self.transport_class_cb.addItems(["Эконом", "Комфорт", "Бизнес-класс", "V.I.P."])
        vbox_class.addWidget(self.transport_class_cb)

        trans_layout.addLayout(vbox_type)
        trans_layout.addLayout(vbox_class)
        filter_layout.addLayout(trans_layout)

        filter_layout.addWidget(QLabel("КОЛИЧЕСТВО ТУРИСТОВ"))
        tourists_layout = QHBoxLayout()
        tourists_layout.addWidget(QLabel("Взрослых:"))
        self.adults_spin = QSpinBox()
        self.adults_spin.setRange(1, 10)
        self.adults_spin.setValue(2)
        tourists_layout.addWidget(self.adults_spin)

        tourists_layout.addWidget(QLabel("Детей:"))
        self.children_spin = QSpinBox()
        self.children_spin.setRange(0, 10)
        self.children_spin.setValue(0)
        tourists_layout.addWidget(self.children_spin)
        filter_layout.addLayout(tourists_layout)

        self.budget_lbl = QLabel("МАКСИМАЛЬНЫЙ БЮДЖЕТ: Без ограничений")
        filter_layout.addWidget(self.budget_lbl)
        self.budget_slider = QSlider(Qt.Orientation.Horizontal)
        self.budget_slider.setRange(10000, 500000)
        self.budget_slider.setSingleStep(10000)
        self.budget_slider.setValue(500000)
        self.budget_slider.valueChanged.connect(self.on_budget_slider_change)
        filter_layout.addWidget(self.budget_slider)

        filter_layout.addWidget(QLabel("ДОПОЛНИТЕЛЬНЫЕ УСЛУГИ"))
        self.chk_ins = QCheckBox("Страховка (+350₽/чел)")
        self.chk_tr = QCheckBox("Трансфер (+1200₽)")
        self.chk_ex = QCheckBox("Экскурсии (+2500₽)")
        filter_layout.addWidget(self.chk_ins)
        filter_layout.addWidget(self.chk_tr)
        filter_layout.addWidget(self.chk_ex)

        filter_layout.addSpacing(6)
        
        btn_layout = QHBoxLayout()
        search_btn = QPushButton("НАЙТИ ТУРЫ")
        search_btn.setObjectName("PrimaryButton")
        search_btn.clicked.connect(self.perform_search)
        btn_layout.addWidget(search_btn)

        random_btn = QPushButton("🎲 Мне повезет!")
        random_btn.clicked.connect(self.pick_random_tour)
        btn_layout.addWidget(random_btn)

        filter_layout.addLayout(btn_layout)
        filter_layout.addStretch()
        content_layout.addWidget(filter_card)

        results_card = QFrame()
        results_card.setProperty("class", "Card")
        results_layout = QVBoxLayout(results_card)
        results_layout.setContentsMargins(18, 18, 18, 18)

        res_top = QHBoxLayout()
        res_title_lbl = QLabel("Найденные туры и отели")
        res_title_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        res_top.addWidget(res_title_lbl)

        self.counter_lbl = QLabel("")
        self.counter_lbl.setStyleSheet("color: #e11d48; font-weight: bold; font-size: 11pt;")
        res_top.addWidget(self.counter_lbl, alignment=Qt.AlignmentFlag.AlignRight)
        results_layout.addLayout(res_top)

        self.search_scroll_area = QScrollArea()
        self.search_scroll_area.setWidgetResizable(True)
        self.search_scroll_widget = QWidget()
        self.search_scroll_layout = QVBoxLayout(self.search_scroll_widget)
        self.search_scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.search_scroll_area.setWidget(self.search_scroll_widget)
        results_layout.addWidget(self.search_scroll_area)

        content_layout.addWidget(results_card)
        main_vbox.addLayout(content_layout)

        self.create_floating_assistant_widget(main_vbox)
        return widget

    def pick_random_tour(self):
        if self.destination_cb.count() > 1:
            idx = random.randint(1, self.destination_cb.count() - 1)
            self.destination_cb.setCurrentIndex(idx)
            self.perform_search()

    def on_budget_slider_change(self, val):
        if val >= 500000:
            self.budget_lbl.setText("МАКСИМАЛЬНЫЙ БЮДЖЕТ: Без ограничений")
        else:
            self.budget_lbl.setText(f"МАКСИМАЛЬНЫЙ БЮДЖЕТ: до {val:,.0f} ₽")

    def update_destination_combo(self):
        self.destination_cb.clear()
        dests = self.service.get_destinations()
        self.destination_cb.addItems(dests)

    def update_city_combo(self):
        self.city_cb.clear()
        dest = self.destination_cb.currentText()
        cities = self.service.get_cities(dest)
        self.city_cb.addItems(cities)

    def perform_search(self):
        try:
            dest = self.destination_cb.currentText().strip()
            city = self.city_cb.currentText().strip()
            t_type = self.transport_type_cb.currentText().strip()
            t_class = self.transport_class_cb.currentText().strip()

            adults = self.adults_spin.value()
            children = self.children_spin.value()
            
            slider_val = self.budget_slider.value()
            max_budget = None if slider_val >= 500000 else float(slider_val)

            extras = []
            if self.chk_ins.isChecked(): extras.append("страховка")
            if self.chk_tr.isChecked(): extras.append("трансфер")
            if self.chk_ex.isChecked(): extras.append("экскурсии")

            req = ClientRequest(
                destination=dest, city=city,
                adults=adults, children=children, max_budget=max_budget,
                extra_services=extras, transport_type=t_type, transport_class=t_class
            )

            results = self.service.search(req)
            self.last_results = results
            self.display_search_results(results)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при поиске:\n{str(e)}")

    def display_search_results(self, results):
        while self.search_scroll_layout.count():
            child = self.search_scroll_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        if not results:
            self.counter_lbl.setText("0 вариантов")
            self.search_scroll_layout.addWidget(QLabel("Ничего не найдено по выбранным параметрам."))
            return

        self.counter_lbl.setText(f"Найдено: {len(results)}")
        curr_symbol = self.service.get_currency_symbol(self.currency)

        for i, res in enumerate(results, 1):
            t = res["tour"]
            price = self.service.convert_price(res["total_price"], self.currency)

            card = QFrame()
            card.setProperty("class", "Card")
            card_layout = QVBoxLayout(card)

            top_row = QHBoxLayout()
            title_lbl = QLabel(f"{i}. 🏨 {t.name} ({'⭐' * t.stars})")
            title_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            top_row.addWidget(title_lbl)

            price_lbl = QLabel(f"Итого: {price:,.2f} {curr_symbol}")
            price_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            price_lbl.setStyleSheet("color: #e11d48;")
            top_row.addWidget(price_lbl, alignment=Qt.AlignmentFlag.AlignRight)
            card_layout.addLayout(top_row)

            btn_layout = QHBoxLayout()
            fav_text = "★ В избранном" if t.id in self.service.favorites else "☆ В избранное"
            btn_fav = QPushButton(fav_text)
            btn_fav.setFixedWidth(130)
            btn_fav.clicked.connect(lambda checked, tid=t.id: self.toggle_fav_and_refresh_search(tid))
            btn_layout.addWidget(btn_fav)

            btn_info = QPushButton("ℹ️ О отеле")
            btn_info.setFixedWidth(130)
            btn_info.clicked.connect(lambda checked, tour=t: self.open_hotel_details(tour))
            btn_layout.addWidget(btn_info)

            btn_delete = QPushButton("🗑 Удалить отель")
            btn_delete.setObjectName("DangerButton")
            btn_delete.setFixedWidth(140)
            btn_delete.clicked.connect(lambda checked, tid=t.id, tname=t.name: self.delete_tour_from_search(tid, tname))
            btn_layout.addWidget(btn_delete)

            btn_book = QPushButton("📝 Забронировать")
            btn_book.setObjectName("PrimaryButton")
            btn_book.setFixedWidth(160)
            btn_book.clicked.connect(lambda checked, tour=t, p=price, sym=curr_symbol: self.open_booking_dialog(tour, p, sym))
            btn_layout.addWidget(btn_book, alignment=Qt.AlignmentFlag.AlignRight)

            card_layout.addLayout(btn_layout)

            t_type_text = self.transport_type_cb.currentText()
            t_class_text = self.transport_class_cb.currentText()
            info_text = f"📍 Страна: {t.destination} | Город: {t.city}   •   {t_type_text} ({t_class_text})   •   📅 Ночей: {res['nights']}\n🛏 Номер: {t.room_type}   •   🍽 Питание: {t.meal_type}   •   🌤 {t.weather}"
            card_layout.addWidget(QLabel(info_text))

            self.search_scroll_layout.addWidget(card)

    def delete_tour_from_search(self, tour_id, tour_name):
        reply = QMessageBox.question(
            self, "Удаление отеля",
            f"Вы действительно хотите удалить отель «{tour_name}» из базы данных?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            db = DatabaseManager()
            with db.get_connection() as conn:
                conn.execute("DELETE FROM tours WHERE id = ?", (tour_id,))
                conn.execute("DELETE FROM favorites WHERE tour_id = ?", (tour_id,))
                conn.commit()
            self.service.reload_tours()
            self.update_destination_combo()
            self.update_city_combo()
            self.perform_search()
            QMessageBox.information(self, "Успех", f"Отель «{tour_name}» успешно удален!")

    def toggle_fav_and_refresh_search(self, tour_id):
        self.service.toggle_favorite(tour_id)
        if self.last_results:
            self.display_search_results(self.last_results)

    def open_hotel_details(self, tour):
        dialog = HotelDetailDialog(tour, self)
        dialog.exec()

    def open_booking_dialog(self, tour, price, currency_symbol):
        dialog = BookingDialog(tour.name, price, currency_symbol, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            booking = BookingRecord(
                tour_id=tour.id, tour_name=tour.name,
                traveler_name=data["name"] if data["name"] else "Без имени",
                passport=data["passport"] if data["passport"] else "0000 000000",
                phone=data["phone"] if data["phone"] else "Нет телефона",
                adults=self.adults_spin.value(),
                children=self.children_spin.value(), total_price=price
            )
            self.service.add_booking(booking)
            
            path = generate_travel_voucher(booking)
            QMessageBox.information(
                self, "Успех", 
                f"Бронь успешно зарегистрирована в БД!\n\nВаучер сохранен в PDF:\n{path}"
            )

    # 2. Избранное
    def create_fav_view(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 20, 24, 16)
        top = QHBoxLayout()
        title = QLabel("⭐ Избранные отели")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        top.addWidget(title)
        
        btn_ref = QPushButton("🔄 Обновить")
        btn_ref.clicked.connect(self.load_favorites)
        top.addWidget(btn_ref, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(top)

        self.fav_scroll = QScrollArea()
        self.fav_scroll.setWidgetResizable(True)
        self.fav_widget = QWidget()
        self.fav_layout = QVBoxLayout(self.fav_widget)
        self.fav_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.fav_scroll.setWidget(self.fav_widget)
        layout.addWidget(self.fav_scroll)

        self.create_floating_assistant_widget(layout)
        return widget

    def load_favorites(self):
        self.service.reload_favorites()
        while self.fav_layout.count():
            child = self.fav_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        
        favs = self.service.get_favorite_tours()
        if not favs:
            self.fav_layout.addWidget(QLabel("В избранном пока ничего нет."))
            return

        curr_symbol = self.service.get_currency_symbol(self.currency)

        for i, tour in enumerate(favs, 1):
            card = QFrame()
            card.setProperty("class", "Card")
            card_layout = QVBoxLayout(card)

            top_row = QHBoxLayout()
            h_lbl = QLabel(f"{i}. 🏨 {tour.name} ({'⭐' * tour.stars})")
            h_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            top_row.addWidget(h_lbl)

            price = self.service.convert_price(tour.base_price, self.currency)
            price_lbl = QLabel(f"Базовая цена: {price:,.2f} {curr_symbol}")
            price_lbl.setStyleSheet("color: #e11d48; font-weight: bold;")
            top_row.addWidget(price_lbl, alignment=Qt.AlignmentFlag.AlignRight)
            card_layout.addLayout(top_row)

            btn_layout = QHBoxLayout()
            btn_rem = QPushButton("★ Удалить")
            btn_rem.setObjectName("DangerButton")
            btn_rem.setFixedWidth(140)
            btn_rem.clicked.connect(lambda checked, tid=tour.id: self.remove_favorite_from_fav_tab(tid))
            btn_layout.addWidget(btn_rem)

            btn_info = QPushButton("ℹ️ О отеле")
            btn_info.setFixedWidth(110)
            btn_info.clicked.connect(lambda checked, t=tour: self.open_hotel_details(t))
            btn_layout.addWidget(btn_info)

            btn_book = QPushButton("📝 Регистрация и бронь")
            btn_book.setObjectName("PrimaryButton")
            btn_book.setFixedWidth(200)
            btn_book.clicked.connect(lambda checked, t=tour, p=price, sym=curr_symbol: self.open_booking_dialog(t, p, sym))
            btn_layout.addWidget(btn_book, alignment=Qt.AlignmentFlag.AlignRight)

            card_layout.addLayout(btn_layout)
            card_layout.addWidget(QLabel(f"📍 Страна: {tour.destination} | Город: {tour.city}   •   🛏 Номер: {tour.room_type}"))
            
            self.fav_layout.addWidget(card)

    def remove_favorite_from_fav_tab(self, tour_id):
        self.service.toggle_favorite(tour_id)
        self.load_favorites()

    # 3. Каталог отелей
    def create_all_view(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 20, 24, 16)
        
        top = QHBoxLayout()
        title = QLabel("🌐 Каталог премиум отелей мира")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        top.addWidget(title)
        
        top.addWidget(QLabel("Фильтр:"))
        self.catalog_filter_cb = QComboBox()
        self.catalog_filter_cb.currentTextChanged.connect(self.load_all_catalog)
        top.addWidget(self.catalog_filter_cb)

        self.compare_btn = QPushButton("⚖️ Сравнить выбранные")
        self.compare_btn.clicked.connect(self.open_comparison_dialog)
        top.addWidget(self.compare_btn)

        btn_ref = QPushButton("🔄 Обновить")
        btn_ref.clicked.connect(self.load_all_catalog)
        top.addWidget(btn_ref, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addLayout(top)

        self.all_scroll = QScrollArea()
        self.all_scroll.setWidgetResizable(True)
        self.all_widget = QWidget()
        self.all_layout = QVBoxLayout(self.all_widget)
        self.all_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.all_scroll.setWidget(self.all_widget)
        layout.addWidget(self.all_scroll)

        self.create_floating_assistant_widget(layout)
        return widget

    def load_all_catalog(self):
        self.service.reload_tours()
        
        if self.catalog_filter_cb.count() == 0:
            self.catalog_filter_cb.addItems(self.service.get_destinations())

        selected_dest = self.catalog_filter_cb.currentText()

        while self.all_layout.count():
            child = self.all_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        self.compare_checkboxes = {}

        for i, tour in enumerate(self.service.tours, 1):
            if selected_dest and selected_dest != "Все страны":
                if selected_dest.lower() not in tour.destination.lower():
                    continue

            card = QFrame()
            card.setProperty("class", "Card")
            l = QVBoxLayout(card)

            top = QHBoxLayout()
            h_lbl = QLabel(f"🏨 {tour.name}   ({'⭐' * tour.stars})")
            h_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            h_lbl.setStyleSheet("color: #e11d48;")
            top.addWidget(h_lbl)

            chk_comp = QCheckBox("Сравнить")
            self.compare_checkboxes[tour.id] = (tour, chk_comp)
            top.addWidget(chk_comp, alignment=Qt.AlignmentFlag.AlignRight)

            l.addLayout(top)

            l.addWidget(QLabel(f"📍 <b>Местоположение:</b> {tour.destination}, г. {tour.city}  •  🌤 {tour.weather}"))
            l.addWidget(QLabel(f"💳 <b>Цена за ночь:</b> от {tour.base_price:,.0f} ₽  •  🛏 <b>Тип номера:</b> {tour.room_type}  •  🍽 <b>Питание:</b> {tour.meal_type}"))
            
            if tour.description:
                l.addWidget(QLabel(f"📝 {tour.description}"))

            btn_row = QHBoxLayout()
            fav_text = "★ В избранном" if tour.id in self.service.favorites else "☆ В избранное"
            btn_fav = QPushButton(fav_text)
            btn_fav.setFixedWidth(140)
            btn_fav.clicked.connect(lambda checked, tid=tour.id: self.toggle_fav_catalog(tid))
            btn_row.addWidget(btn_fav)

            btn_book = QPushButton("Забронировать этот отель")
            btn_book.setObjectName("PrimaryButton")
            btn_book.setFixedWidth(200)
            btn_book.clicked.connect(lambda checked, t=tour: self.open_booking_dialog(t, t.base_price, "₽"))
            btn_row.addWidget(btn_book, alignment=Qt.AlignmentFlag.AlignRight)

            l.addLayout(btn_row)
            self.all_layout.addWidget(card)

    def open_comparison_dialog(self):
        selected_tours = [tour for tour, chk in self.compare_checkboxes.values() if chk.isChecked()]
        if len(selected_tours) < 2:
            QMessageBox.warning(self, "Внимание", "Выберите хотя бы 2 отеля галочками «Сравнить» в каталоге!")
            return
        dialog = HotelCompareDialog(selected_tours, self)
        dialog.exec()

    def toggle_fav_catalog(self, tour_id):
        self.service.toggle_favorite(tour_id)
        self.load_all_catalog()

    # 4. Управление и бронирования
    def create_admin_view(self):
        widget = QWidget()
        main_vbox = QVBoxLayout(widget)
        main_vbox.setContentsMargins(24, 20, 24, 16)
        
        layout = QHBoxLayout()

        form_card = QFrame()
        form_card.setProperty("class", "Card")
        form_card.setFixedWidth(420)
        fl = QVBoxLayout(form_card)
        
        self.form_title_lbl = QLabel("⚡ ДОБАВИТЬ БРОНИРОВАНИЕ В БД")
        self.form_title_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.form_title_lbl.setStyleSheet("color: #e11d48;")
        fl.addWidget(self.form_title_lbl)

        fl.addWidget(QLabel("Выберите тур / отель:"))
        self.adm_tour_cb = QComboBox()
        self.update_admin_tour_combo()
        fl.addWidget(self.adm_tour_cb)

        fl.addWidget(QLabel("ФИО туриста:"))
        self.adm_name_input = QLineEdit()
        self.adm_name_input.setPlaceholderText("Любое имя")
        fl.addWidget(self.adm_name_input)

        fl.addWidget(QLabel("Серия и номер паспорта:"))
        self.adm_passport_input = QLineEdit()
        self.adm_passport_input.setPlaceholderText("Любые данные")
        fl.addWidget(self.adm_passport_input)

        fl.addWidget(QLabel("Телефон:"))
        self.adm_phone_input = QLineEdit()
        self.adm_phone_input.setPlaceholderText("Любой номер")
        fl.addWidget(self.adm_phone_input)

        tourists_layout = QHBoxLayout()
        tourists_layout.addWidget(QLabel("Взрослых:"))
        self.adm_adults_spin = QSpinBox()
        self.adm_adults_spin.setRange(1, 10)
        self.adm_adults_spin.setValue(2)
        tourists_layout.addWidget(self.adm_adults_spin)

        tourists_layout.addWidget(QLabel("Детей:"))
        self.adm_children_spin = QSpinBox()
        self.adm_children_spin.setRange(0, 10)
        tourists_layout.addWidget(self.adm_children_spin)
        fl.addLayout(tourists_layout)

        fl.addWidget(QLabel("Итоговая стоимость (₽):"))
        self.adm_price_input = QLineEdit("15000")
        fl.addWidget(self.adm_price_input)

        self.save_booking_btn = QPushButton("ЗАРЕГИСТРИРОВАТЬ БРОНЬ")
        self.save_booking_btn.setObjectName("PrimaryButton")
        self.save_booking_btn.clicked.connect(self.save_booking_action)
        fl.addWidget(self.save_booking_btn)

        self.cancel_edit_btn = QPushButton("Отменить редактирование")
        self.cancel_edit_btn.setVisible(False)
        self.cancel_edit_btn.clicked.connect(self.cancel_edit_mode)
        fl.addWidget(self.cancel_edit_btn)
        
        export_btn = QPushButton("📊 Экспорт реестра в Excel (.csv)")
        export_btn.clicked.connect(self.export_excel_action)
        fl.addWidget(export_btn)

        self.adm_status = QLabel("")
        fl.addWidget(self.adm_status)
        fl.addStretch()
        layout.addWidget(form_card)

        table_card = QFrame()
        table_card.setProperty("class", "Card")
        tl = QVBoxLayout(table_card)
        
        tl.addWidget(QLabel("📋 Реестр зарегистрированных бронирований"))
        
        self.bookings_table = QTableWidget()
        self.bookings_table.setColumnCount(8)
        self.bookings_table.setHorizontalHeaderLabels(["ID", "Тур", "Турист", "Паспорт", "Телефон", "Взр.", "Дет.", "Сумма"])
        self.bookings_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.bookings_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.bookings_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tl.addWidget(self.bookings_table)

        row_btn_layout = QHBoxLayout()
        edit_btn = QPushButton("✏️ Изменить выбранную бронь")
        edit_btn.clicked.connect(self.load_booking_to_form)
        row_btn_layout.addWidget(edit_btn)

        del_btn = QPushButton("🗑 Удалить бронирование")
        del_btn.setObjectName("DangerButton")
        del_btn.clicked.connect(self.delete_selected_booking)
        row_btn_layout.addWidget(del_btn)

        tl.addLayout(row_btn_layout)
        layout.addWidget(table_card)

        main_vbox.addLayout(layout)
        self.create_floating_assistant_widget(main_vbox)

        self.current_editing_id = None
        self.refresh_admin_text()
        return widget

    def update_admin_tour_combo(self):
        self.adm_tour_cb.clear()
        self.service.reload_tours()
        for t in self.service.tours:
            self.adm_tour_cb.addItem(f"{t.name} ({t.destination}, г. {t.city})", t.id)

    def save_booking_action(self):
        try:
            name = self.adm_name_input.text()
            passport = self.adm_passport_input.text()
            phone = self.adm_phone_input.text()
            price_text = self.adm_price_input.text().strip()

            if not name: name = "Без имени"
            if not passport: passport = "0000 000000"

            tour_id = self.adm_tour_cb.currentData()
            tour_name = self.adm_tour_cb.currentText()
            
            try:
                total_price = float(price_text.replace(" ", "").replace(",", "."))
            except ValueError:
                total_price = 10000.0

            if self.current_editing_id is None:
                booking = BookingRecord(
                    tour_id=tour_id if tour_id else 1,
                    tour_name=tour_name,
                    traveler_name=name,
                    passport=passport,
                    phone=phone,
                    adults=self.adm_adults_spin.value(),
                    children=self.adm_children_spin.value(),
                    total_price=total_price
                )
                self.service.add_booking(booking)
                self.adm_status.setText("✔ Бронь успешно добавлена!")
            else:
                self.service.update_booking(
                    self.current_editing_id, name, passport, phone,
                    self.adm_adults_spin.value(), self.adm_children_spin.value(), total_price
                )
                self.adm_status.setText("✔ Бронь успешно обновлена!")
                self.cancel_edit_mode()

            self.refresh_admin_text()
            self.clear_admin_form()
        except Exception as e:
            self.adm_status.setText(f"✖ Ошибка: {str(e)}")

    def load_booking_to_form(self):
        selected_rows = self.bookings_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Внимание", "Выберите строку с бронированием в таблице для изменения!")
            return
        
        row = selected_rows[0].row()
        self.current_editing_id = int(self.bookings_table.item(row, 0).text())
        
        self.adm_name_input.setText(self.bookings_table.item(row, 2).text())
        self.adm_passport_input.setText(self.bookings_table.item(row, 3).text())
        self.adm_phone_input.setText(self.bookings_table.item(row, 4).text())
        self.adm_adults_spin.setValue(int(self.bookings_table.item(row, 5).text()))
        self.adm_children_spin.setValue(int(self.bookings_table.item(row, 6).text()))
        
        price_str = self.bookings_table.item(row, 7).text().replace(" ", "").replace("₽", "")
        self.adm_price_input.setText(price_str)

        self.form_title_lbl.setText(f"⚡ РЕДАКТИРОВАНИЕ БРОНИ №{self.current_editing_id}")
        self.save_booking_btn.setText("СОХРАНИТЬ ИЗМЕНЕНИЯ")
        self.cancel_edit_btn.setVisible(True)

    def cancel_edit_mode(self):
        self.current_editing_id = None
        self.form_title_lbl.setText("⚡ ДОБАВИТЬ БРОНИРОВАНИЕ В БД")
        self.save_booking_btn.setText("ЗАРЕГИСТРИРОВАТЬ БРОНЬ")
        self.cancel_edit_btn.setVisible(False)
        self.clear_admin_form()

    def clear_admin_form(self):
        self.adm_name_input.clear()
        self.adm_passport_input.clear()
        self.adm_phone_input.clear()
        self.adm_price_input.setText("15000")
        self.adm_adults_spin.setValue(2)
        self.adm_children_spin.setValue(0)

    def delete_selected_booking(self):
        selected_rows = self.bookings_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Внимание", "Выберите строку с бронированием для удаления!")
            return
        
        row = selected_rows[0].row()
        booking_id = int(self.bookings_table.item(row, 0).text())
        traveler = self.bookings_table.item(row, 2).text()

        reply = QMessageBox.question(
            self, "Подтверждение удаления", 
            f"Вы действительно хотите удалить бронирование для туриста {traveler}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.service.delete_booking(booking_id)
            self.refresh_admin_text()
            QMessageBox.information(self, "Успех", "Бронирование удалено из базы данных.")

    def export_excel_action(self):
        try:
            path = export_bookings_to_excel()
            QMessageBox.information(self, "Экспорт успешен", f"Реестр бронирований выгружен в Excel (.csv):\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать:\n{str(e)}")

    def refresh_admin_text(self):
        bookings = self.service.get_all_bookings()
        self.bookings_table.setRowCount(len(bookings))
        
        for row, b in enumerate(bookings):
            self.bookings_table.setItem(row, 0, QTableWidgetItem(str(b["id"])))
            self.bookings_table.setItem(row, 1, QTableWidgetItem(str(b["tour_name"])))
            self.bookings_table.setItem(row, 2, QTableWidgetItem(str(b["traveler_name"])))
            self.bookings_table.setItem(row, 3, QTableWidgetItem(str(b["passport"])))
            self.bookings_table.setItem(row, 4, QTableWidgetItem(str(b["phone"])))
            self.bookings_table.setItem(row, 5, QTableWidgetItem(str(b["adults"])))
            self.bookings_table.setItem(row, 6, QTableWidgetItem(str(b["children"])))
            self.bookings_table.setItem(row, 7, QTableWidgetItem(f"{b['total_price']:,.0f} ₽"))

    # 5. Настройки
    def create_settings_view(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 20, 24, 16)
        
        card = QFrame()
        card.setProperty("class", "Card")
        cl = QVBoxLayout(card)
        cl.setSpacing(14)
        
        self.set_title_lbl = QLabel("⚙️ Системные настройки приложения")
        self.set_title_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.set_title_lbl.setStyleSheet("color: #e11d48;")
        cl.addWidget(self.set_title_lbl)
        
        cl.addWidget(QLabel("Выбор языка интерфейса:"))
        self.cb_language = QComboBox()
        self.cb_language.addItems(["Русский", "English", "Español"])
        self.cb_language.currentTextChanged.connect(self.on_language_change)
        cl.addWidget(self.cb_language)

        cl.addWidget(QLabel("Тема оформления интерфейса:"))
        self.cb_theme = QComboBox()
        self.cb_theme.addItems(["Тёмная (Красный неон)", "Светлая (Ruby Red)"])
        self.cb_theme.currentTextChanged.connect(self.on_theme_change)
        cl.addWidget(self.cb_theme)

        cl.addWidget(QLabel("Выбор валюты расчетов:"))
        self.cb_currency_settings = QComboBox()
        self.cb_currency_settings.addItems(["RUB", "USD", "EUR"])
        self.cb_currency_settings.currentTextChanged.connect(self.on_currency_setting_change)
        cl.addWidget(self.cb_currency_settings)

        cl.addSpacing(15)
        btn_reset = QPushButton("🗑 Сбросить базу данных и загрузить 14+ стран заново")
        btn_reset.setObjectName("DangerButton")
        btn_reset.clicked.connect(self.reset_db)
        cl.addWidget(btn_reset)
        
        cl.addStretch()
        layout.addWidget(card)

        self.create_floating_assistant_widget(layout)
        return widget

    def on_language_change(self, lang):
        self.language = lang
        self.update_ui_texts()
        QMessageBox.information(self, "Настройки", f"Язык интерфейса изменен на: {lang}")

    def on_theme_change(self, theme):
        self.theme = theme
        self.apply_theme()
        QMessageBox.information(self, "Настройки", f"Тема изменена на: {theme}")

    def on_currency_setting_change(self, curr):
        self.currency = curr
        if self.last_results:
            self.display_search_results(self.last_results)

    def reset_db(self):
        db = DatabaseManager()
        with db.get_connection() as conn:
            conn.execute("DROP TABLE IF EXISTS tours")
            conn.execute("DROP TABLE IF EXISTS bookings")
            conn.execute("DROP TABLE IF EXISTS favorites")
            conn.commit()
        init_db_with_samples()
        self.service.reload_tours()
        self.service.reload_favorites()
        self.update_destination_combo()
        self.update_admin_tour_combo()
        self.load_all_catalog()
        QMessageBox.information(self, "Готово", "База данных успешно пересоздана со всеми 14+ странами!")

    # 6. Прокачанный ИИ Ассистент («Ковбой») с базой умных ответов
    def create_ai_view(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 20, 24, 16)
        layout.setSpacing(12)
        
        header_layout = QHBoxLayout()
        avatar_lbl = QLabel("🤠")
        avatar_lbl.setFont(QFont("Segoe UI", 20))
        avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_lbl.setFixedSize(50, 50)
        avatar_lbl.setStyleSheet("background-color: rgba(225, 29, 72, 0.1); border: 2px solid #e11d48; border-radius: 25px;")
        header_layout.addWidget(avatar_lbl)

        title_container = QVBoxLayout()
        title = QLabel("ИИ Ассистент «Ковбой» — Интеллектуальный гид")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        
        subtitle = QLabel("Online • Отвечаю на любые вопросы о путешествиях и подбираю туры!")
        subtitle.setStyleSheet("color: #e11d48; font-size: 9.5pt;")
        
        title_container.addWidget(title)
        title_container.addWidget(subtitle)
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)

        self.ai_chat_box = QTextEdit()
        self.ai_chat_box.setReadOnly(True)
        self.ai_chat_box.setStyleSheet("QTextEdit { border: 1px solid #cbd5e1; border-radius: 12px; padding: 15px; font-size: 11pt; }")
        
        init_html = """
        <div style="margin-bottom: 15px;">
            <div style="border: 1px solid #e11d48; border-left: 4px solid #e11d48; padding: 12px 16px; border-radius: 10px;">
                <b style="color: #e11d48;">🤠 Ковбой:</b> Йе-хоу, партнёр! 🏜️ Спроси меня о чем угодно: о странах, погоде, багаже, визах или попроси подобрать тур!
            </div>
        </div>
        """
        self.ai_chat_box.setHtml(init_html)
        layout.addWidget(self.ai_chat_box)

        self.chips_layout = QHBoxLayout()
        self.update_ai_chips([
            "🇹🇷 Туры в Турцию", 
            "☀️ Куда полететь греться?", 
            "🎒 Что брать с собой?",
            "✈️ Правила перелета",
            "💸 Самый дешевый тур"
        ])
        layout.addLayout(self.chips_layout)

        input_row = QHBoxLayout()
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Напишите любой вопрос или название страны...")
        self.ai_input.returnPressed.connect(self.send_ai_message)
        input_row.addWidget(self.ai_input)

        send_btn = QPushButton("Спросить Ковбоя")
        send_btn.setObjectName("PrimaryButton")
        send_btn.clicked.connect(self.send_ai_message)
        input_row.addWidget(send_btn)
        
        layout.addLayout(input_row)
        return widget

    def update_ai_chips(self, questions):
        while self.chips_layout.count():
            child = self.chips_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        for q in questions:
            btn = QPushButton(q)
            btn.clicked.connect(lambda checked, text=q: self.ask_predefined_question(text))
            self.chips_layout.addWidget(btn)

    def ask_predefined_question(self, text):
        self.ai_input.setText(text)
        self.send_ai_message()

    def send_ai_message(self):
        text = self.ai_input.text().strip()
        if not text: return
        
        user_msg_html = f"""
        <div style="margin: 12px 0; text-align: right;">
            <div style="display: inline-block; background-color: #e11d48; padding: 10px 14px; border-radius: 12px; color: #ffffff; text-align: left; max-width: 80%;">
                <b>Вы:</b> {text}
            </div>
        </div>
        """
        self.ai_chat_box.append(user_msg_html)
        self.ai_input.clear()
        
        q = text.lower()
        tours = self.service.tours
        next_chips = []
        resp = ""

        # Умный разбор запросов пользователя на любые темы
        if "багаж" in q or "сумк" in q or "вещ" in q:
            resp = "🎒 <b>Совет по багажу:</b> В ручную кладь обычно разрешено брать до 10 кг (габариты до 55х40х20 см). Жидкости везтите в емкостях до 100 мл в прозрачном пакете. Ценные вещи, документы и лекарства всегда берите в салон самолета!"
            next_chips = ["✈️ Правила перелета", "🇹🇷 Турция", "🎒 Что брать с собой?"]
        elif "перелет" in q or "самол" in q or "аэропорт" in q:
            resp = "✈️ <b>Правила полета:</b> Прибывайте в аэропорт за 2-3 часа до вылета международных рейсов. Регистрация обычно заканчивается за 40 минут до отправления. Не забудьте проверить срок действия загранпаспорта (минимум 6 месяцев до окончания)!"
            next_chips = ["🇹🇷 Турция", "🇦🇪 ОАЭ", "💸 Самый дешевый тур"]
        elif "полететь" in q or "греть" in q or "море" in q or "пляж" in q or "отпуск" in q:
            resp = "🌴 Для пляжного отдыха идеально подходят <b>Турция</b> (Кемер, Белек), <b>ОАЭ</b> (Дубай), <b>Мальдивы</b>, <b>Египет</b> (Хургада) и <b>Таиланд</b> (Пхукет). Вода там теплая круглый год, а сервис на высшем уровне!"
            next_chips = ["🇹🇷 Туры в Турцию", "🇦🇪 Отели в ОАЭ", "🌴 Райские Мальдивы"]
        elif "дешев" in q or "бюджет" in q or "скидк" in q:
            cheapest = min(tours, key=lambda x: x.base_price)
            resp = f"💸 Самый выгодный вариант на сегодня — <b>{cheapest.name}</b> в городе {cheapest.city} ({cheapest.destination}) всего от <b>{cheapest.base_price:,.0f} ₽</b> за ночь! Отличный выбор для экономного путешествия."
            next_chips = ["🎲 Случайный тур", "🇹🇷 Турция", "🇦🇪 ОАЭ"]
        elif "случайный" in q or "повезет" in q or "выбор" in q:
            rand_t = random.choice(tours)
            resp = f"🎲 Фортуна выбрала для вас потрясающий отель: <b>{rand_t.name}</b> в стране {rand_t.destination} ({rand_t.city})! Базовая цена: {rand_t.base_price:,.0f} ₽/ночь."
            next_chips = ["Еще вариант", "Самый дешевый тур", "Показать все страны"]
        else:
            # Ищем туры по ключевым словам (страна, город, название)
            matched_tours = [t for t in tours if q in t.destination.lower() or q in t.city.lower() or q in t.name.lower() or q in t.description.lower()]
            if matched_tours:
                resp = f"🤠 Я откопал для вас лучшие варианты по запросу «<b>{text}</b>»:<br><br>"
                for t in matched_tours[:3]:
                    resp += f"🏨 <b>{t.name}</b> ({'⭐'*t.stars}) — {t.destination}, г. {t.city} | От {t.base_price:,.0f} ₽/ночь<br><i>{t.weather}</i><br><br>"
                next_chips = ["🎲 Случайный тур", "💸 Самый дешевый тур", "🎒 Что брать с собой?"]
            else:
                resp = f"Партнёр, я внимательно выслушал твой вопрос («<i>{text}</i>»). В моей базе более 14 стран (Турция, ОАЭ, Мальдивы, Египет, Таиланд, Греция, Италия, Япония и др.), а также полезные советы по перелетам и багажу. Выбирай интересующую тему ниже или воспользуйся вкладкой поиска туров!"
                next_chips = ["🇹🇷 Турция", "🇦🇪 ОАЭ", "🎒 Что брать с собой?", "💸 Самый дешевый тур"]

        ai_resp_html = f"""
        <div style="margin: 12px 0; text-align: left;">
            <div style="display: inline-block; border: 1px solid #e11d48; border-left: 4px solid #e11d48; padding: 12px 16px; border-radius: 12px; max-width: 85%;">
                <b style="color: #e11d48;">🤠 Ковбой:</b> {resp}
            </div>
        </div>
        """
        self.ai_chat_box.append(ai_resp_html)
        self.update_ai_chips(next_chips)
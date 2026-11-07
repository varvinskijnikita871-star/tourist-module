import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from main import ClientRequest, TourService, get_sample_tours


class TourApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Туристическое агентство — подбор туров")
        self.root.geometry("920x680")
        self.root.configure(bg="#f0f4f8")
        self.root.resizable(True, True)

        self.service = TourService(get_sample_tours())
        self._setup_styles()
        self._build_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#f0f4f8", font=("Segoe UI", 10))
        style.configure("TLabelframe", background="#f0f4f8", font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", background="#f0f4f8", foreground="#1a5276")
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=8)
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#1a5276", background="#f0f4f8")
        style.configure("TEntry", padding=5)
        style.configure("TCombobox", padding=5)

    def _build_ui(self):
        # Заголовок
        header = ttk.Label(self.root, text="✈️  Подбор туристических пакетов", style="Header.TLabel")
        header.pack(pady=(15, 5))

        subtitle = ttk.Label(self.root, text="Модуль расчёта стоимости туров", foreground="#5d6d7e")
        subtitle.pack(pady=(0, 10))

        # Основной контейнер
        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=20, pady=5)

        # Левая панель — параметры
        left = ttk.LabelFrame(main, text="Параметры поиска", padding=15)
        left.pack(side="left", fill="y", padx=(0, 10))

        # Направление
        ttk.Label(left, text="Направление").grid(row=0, column=0, sticky="w", pady=(0, 2))
        self.destination = ttk.Combobox(left, width=28, values=[
            "Турция", "Египет", "Греция", "Болгария", "Тунис", "ОАЭ",
            "Черногория", "Испания", "Россия", "Таиланд", "Мальдивы",
            "Италия", "Кипр", "Грузия"
        ])
        self.destination.grid(row=1, column=0, sticky="w", pady=(0, 10))
        self.destination.set("Турция")

        # Даты
        ttk.Label(left, text="Дата выезда (ДД.ММ.ГГГГ)").grid(row=2, column=0, sticky="w", pady=(0, 2))
        self.start_date = ttk.Entry(left, width=30)
        self.start_date.grid(row=3, column=0, sticky="w", pady=(0, 10))
        self.start_date.insert(0, "05.07.2025")

        ttk.Label(left, text="Дата возвращения (ДД.ММ.ГГГГ)").grid(row=4, column=0, sticky="w", pady=(0, 2))
        self.end_date = ttk.Entry(left, width=30)
        self.end_date.grid(row=5, column=0, sticky="w", pady=(0, 10))
        self.end_date.insert(0, "15.07.2025")

        # Люди
        people = ttk.Frame(left)
        people.grid(row=6, column=0, sticky="w", pady=(0, 10))
        ttk.Label(people, text="Взрослые:").pack(side="left")
        self.adults = ttk.Spinbox(people, from_=1, to=20, width=5)
        self.adults.pack(side="left", padx=(5, 15))
        self.adults.set(2)
        ttk.Label(people, text="Дети:").pack(side="left")
        self.children = ttk.Spinbox(people, from_=0, to=10, width=5)
        self.children.pack(side="left", padx=5)
        self.children.set(0)

        # Номер и питание
        ttk.Label(left, text="Тип номера").grid(row=7, column=0, sticky="w", pady=(0, 2))
        self.room = ttk.Combobox(left, values=["любой", "single", "double", "family"], width=28)
        self.room.grid(row=8, column=0, sticky="w", pady=(0, 10))
        self.room.set("любой")

        ttk.Label(left, text="Тип питания").grid(row=9, column=0, sticky="w", pady=(0, 2))
        self.meal = ttk.Combobox(left, values=["любой", "RO", "BB", "HB", "AI"], width=28)
        self.meal.grid(row=10, column=0, sticky="w", pady=(0, 10))
        self.meal.set("любой")

        # Бюджет
        ttk.Label(left, text="Макс. бюджет (руб.)").grid(row=11, column=0, sticky="w", pady=(0, 2))
        self.budget = ttk.Entry(left, width=30)
        self.budget.grid(row=12, column=0, sticky="w", pady=(0, 10))

        # Доп. услуги
        ttk.Label(left, text="Дополнительные услуги").grid(row=13, column=0, sticky="w", pady=(0, 5))
        self.var_ins = tk.BooleanVar()
        self.var_tr = tk.BooleanVar()
        self.var_ex = tk.BooleanVar()
        ttk.Checkbutton(left, text="Страховка", variable=self.var_ins).grid(row=14, column=0, sticky="w")
        ttk.Checkbutton(left, text="Трансфер", variable=self.var_tr).grid(row=15, column=0, sticky="w")
        ttk.Checkbutton(left, text="Экскурсии", variable=self.var_ex).grid(row=16, column=0, sticky="w")

        # Кнопка
        btn = ttk.Button(left, text="🔍  Найти туры", command=self.search)
        btn.grid(row=17, column=0, pady=15, sticky="ew")

        # Правая панель — результаты
        right = ttk.LabelFrame(main, text="Результаты поиска", padding=10)
        right.pack(side="left", fill="both", expand=True)

        self.results = scrolledtext.ScrolledText(
            right, font=("Consolas", 10), bg="#ffffff", fg="#2c3e50",
            relief="flat", padx=10, pady=10
        )
        self.results.pack(fill="both", expand=True)
        self.results.insert("1.0", "Введите параметры и нажмите «Найти туры»")

    def parse_date(self, text):
        try:
            return datetime.strptime(text.strip(), "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Неверный формат даты. Используйте ДД.ММ.ГГГГ")

    def search(self):
        self.results.delete("1.0", tk.END)
        try:
            destination = self.destination.get().strip()
            if not destination:
                raise ValueError("Укажите направление")

            start = self.parse_date(self.start_date.get())
            end = self.parse_date(self.end_date.get())
            if end <= start:
                raise ValueError("Дата возвращения должна быть позже даты выезда")

            adults = int(self.adults.get())
            children = int(self.children.get())
            if adults < 1:
                raise ValueError("Должен быть хотя бы 1 взрослый")

            room = self.room.get()
            meal = self.meal.get()
            preferred_room = None if room == "любой" else room
            preferred_meal = None if meal == "любой" else meal

            budget_text = self.budget.get().strip()
            max_budget = float(budget_text) if budget_text else None

            extras = []
            if self.var_ins.get():
                extras.append("страховка")
            if self.var_tr.get():
                extras.append("трансфер")
            if self.var_ex.get():
                extras.append("экскурсии")

            request = ClientRequest(
                destination=destination,
                start_date=start,
                end_date=end,
                adults=adults,
                children=children,
                preferred_room=preferred_room,
                preferred_meal=preferred_meal,
                max_budget=max_budget,
                extra_services=extras
            )

            found = self.service.search(request)

            if not found:
                self.results.insert(tk.END, "❌  Подходящих туров не найдено.\n\n"
                                            "Попробуйте:\n"
                                            "• изменить даты\n"
                                            "• выбрать другое направление\n"
                                            "• убрать фильтры по номеру/питанию\n"
                                            "• увеличить бюджет\n")
                return

            self.results.insert(tk.END, f"✅  Найдено вариантов: {len(found)}\n")
            self.results.insert(tk.END, "═" * 55 + "\n\n")

            for i, res in enumerate(found, 1):
                t = res["tour"]
                self.results.insert(tk.END, f"{i}. {t.name}\n")
                self.results.insert(tk.END, f"   📍 {t.destination}\n")
                self.results.insert(tk.END, f"   📅 {t.start_date.strftime('%d.%m.%Y')} — "
                                            f"{t.end_date.strftime('%d.%m.%Y')}\n")
                self.results.insert(tk.END, f"   🛏 {t.room_type}  |  🍽 {t.meal_type}\n")
                self.results.insert(tk.END, f"   💰 {res['total_price']:,.0f} руб. "
                                            f"({res['price_per_person']:,.0f} руб./чел.)\n")
                self.results.insert(tk.END, f"   {t.description}\n")
                self.results.insert(tk.END, "─" * 45 + "\n\n")

        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = TourApp(root)
    root.mainloop()
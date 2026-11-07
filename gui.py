import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import date, datetime
from main import TourPackage, ClientRequest, TourService, get_sample_tours


class TourApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Модуль подбора туристических пакетов")
        self.root.geometry("900x650")
        self.root.resizable(True, True)

        self.service = TourService(get_sample_tours())
        self._build_ui()

    def _build_ui(self):
        # --- Заголовок ---
        title = tk.Label(
            self.root,
            text="Подбор и расчёт стоимости туристических пакетов",
            font=("Arial", 16, "bold"),
            pady=10
        )
        title.pack()

        # --- Рамка ввода ---
        frame = ttk.LabelFrame(self.root, text="Параметры поиска", padding=15)
        frame.pack(fill="x", padx=15, pady=5)

        # Направление
        ttk.Label(frame, text="Направление:").grid(row=0, column=0, sticky="w", pady=4)
        self.destination = ttk.Entry(frame, width=30)
        self.destination.grid(row=0, column=1, sticky="w", pady=4, padx=5)
        self.destination.insert(0, "Турция")

        # Даты
        ttk.Label(frame, text="Дата выезда (ДД.ММ.ГГГГ):").grid(row=1, column=0, sticky="w", pady=4)
        self.start_date = ttk.Entry(frame, width=30)
        self.start_date.grid(row=1, column=1, sticky="w", pady=4, padx=5)
        self.start_date.insert(0, "05.07.2025")

        ttk.Label(frame, text="Дата возвращения (ДД.ММ.ГГГГ):").grid(row=2, column=0, sticky="w", pady=4)
        self.end_date = ttk.Entry(frame, width=30)
        self.end_date.grid(row=2, column=1, sticky="w", pady=4, padx=5)
        self.end_date.insert(0, "15.07.2025")

        # Люди
        ttk.Label(frame, text="Взрослые:").grid(row=3, column=0, sticky="w", pady=4)
        self.adults = ttk.Spinbox(frame, from_=1, to=20, width=5)
        self.adults.grid(row=3, column=1, sticky="w", pady=4, padx=5)
        self.adults.set(2)

        ttk.Label(frame, text="Дети:").grid(row=3, column=1, sticky="e", pady=4)
        self.children = ttk.Spinbox(frame, from_=0, to=10, width=5)
        self.children.grid(row=3, column=2, sticky="w", pady=4, padx=5)
        self.children.set(0)

        # Тип номера
        ttk.Label(frame, text="Тип номера:").grid(row=4, column=0, sticky="w", pady=4)
        self.room = ttk.Combobox(frame, values=["любой", "single", "double", "family"], width=12)
        self.room.grid(row=4, column=1, sticky="w", pady=4, padx=5)
        self.room.set("любой")

        # Тип питания
        ttk.Label(frame, text="Тип питания:").grid(row=5, column=0, sticky="w", pady=4)
        self.meal = ttk.Combobox(frame, values=["любой", "RO", "BB", "HB", "AI"], width=12)
        self.meal.grid(row=5, column=1, sticky="w", pady=4, padx=5)
        self.meal.set("любой")

        # Бюджет
        ttk.Label(frame, text="Макс. бюджет (руб.):").grid(row=6, column=0, sticky="w", pady=4)
        self.budget = ttk.Entry(frame, width=30)
        self.budget.grid(row=6, column=1, sticky="w", pady=4, padx=5)

        # Доп. услуги
        ttk.Label(frame, text="Доп. услуги:").grid(row=7, column=0, sticky="w", pady=4)
        self.var_ins = tk.BooleanVar()
        self.var_tr = tk.BooleanVar()
        self.var_ex = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Страховка", variable=self.var_ins).grid(row=7, column=1, sticky="w")
        ttk.Checkbutton(frame, text="Трансфер", variable=self.var_tr).grid(row=7, column=2, sticky="w")
        ttk.Checkbutton(frame, text="Экскурсии", variable=self.var_ex).grid(row=7, column=3, sticky="w")

        # Кнопка поиска
        btn = ttk.Button(self.root, text="Найти туры", command=self.search)
        btn.pack(pady=10)

        # --- Результаты ---
        res_frame = ttk.LabelFrame(self.root, text="Результаты поиска", padding=10)
        res_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.results = scrolledtext.ScrolledText(res_frame, height=12, font=("Consolas", 10))
        self.results.pack(fill="both", expand=True)

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
            if children < 0:
                raise ValueError("Количество детей не может быть отрицательным")

            room = self.room.get()
            meal = self.meal.get()
            preferred_room = None if room == "любой" else room
            preferred_meal = None if meal == "любой" else meal

            budget_text = self.budget.get().strip()
            max_budget = float(budget_text) if budget_text else None
            if max_budget is not None and max_budget < 0:
                raise ValueError("Бюджет не может быть отрицательным")

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
                self.results.insert(tk.END, "Подходящих туров не найдено.\n"
                                            "Попробуйте изменить параметры поиска.\n")
                return

            self.results.insert(tk.END, f"Найдено вариантов: {len(found)}\n")
            self.results.insert(tk.END, "=" * 70 + "\n\n")

            for i, res in enumerate(found, 1):
                t = res["tour"]
                self.results.insert(tk.END, f"{i}. {t.name}\n")
                self.results.insert(tk.END, f"   Направление: {t.destination}\n")
                self.results.insert(tk.END, f"   Даты: {t.start_date.strftime('%d.%m.%Y')} — "
                                            f"{t.end_date.strftime('%d.%m.%Y')}\n")
                self.results.insert(tk.END, f"   Номер: {t.room_type} | Питание: {t.meal_type}\n")
                self.results.insert(tk.END, f"   Стоимость: {res['total_price']:,.0f} руб. "
                                            f"({res['price_per_person']:,.0f} руб./чел.)\n")
                self.results.insert(tk.END, f"   {t.description}\n")
                self.results.insert(tk.END, "-" * 50 + "\n\n")

        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = TourApp(root)
    root.mainloop()
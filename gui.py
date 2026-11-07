import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime, timedelta
from main import ClientRequest, TourService
from data import get_sample_tours
BG = "#0b1220"
CARD = "#141b2d"
CARD2 = "#1a2335"
ACCENT = "#22d3ee"
ACCENT2 = "#a78bfa"
TEXT = "#eef2ff"
MUTED = "#94a3b8"
SUCCESS = "#34d399"
WARNING = "#fbbf24"
ERROR = "#fb7185"
INPUT_BG = "#1e293b"


class TourApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TravelFinder — умный подбор туров")
        self.root.geometry("1180x760")
        self.root.configure(bg=BG)
        self.root.minsize(1050, 680)

        self.service = TourService(get_sample_tours())
        self.last_results = []
        self._build_ui()
        self._show_welcome()

    def _build_ui(self):
        # HEADER
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=28, pady=(18, 6))

        tk.Label(header, text="✈  TravelFinder", font=("Segoe UI", 24, "bold"),
                 fg=ACCENT, bg=BG).pack(side="left")
        tk.Label(header, text="умный подбор и расчёт стоимости туров",
                 font=("Segoe UI", 11), fg=MUTED, bg=BG).pack(side="left", padx=(12, 0), pady=(8, 0))

        self.status = tk.Label(header, text="", font=("Segoe UI", 10), fg=MUTED, bg=BG)
        self.status.pack(side="right", pady=(8, 0))

        # BODY
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=8)

        # LEFT
        left = tk.Frame(body, bg=CARD, padx=16, pady=14)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.configure(width=320)
        left.pack_propagate(False)

        self._section(left, "НАПРАВЛЕНИЕ")
        dests = self.service.get_destinations() if hasattr(self.service, "get_destinations") else [
            "Турция", "Египет", "Греция", "Болгария", "Тунис", "ОАЭ", "Черногория",
            "Испания", "Россия", "Таиланд", "Мальдивы", "Италия", "Кипр", "Грузия"
        ]
        self.destination = self._combo(left, dests, "Турция")

        self._section(left, "ПОИСК ПО НАЗВАНИЮ")
        self.name_query = self._entry(left, "")

        self._section(left, "ДАТЫ ПОЕЗДКИ")
        self.start_date = self._entry(left, "05.07.2025")
        self.end_date = self._entry(left, "15.07.2025")

        quick = tk.Frame(left, bg=CARD)
        quick.pack(fill="x", pady=(0, 6))
        for text, days in [("+7д", 7), ("+14д", 14), ("+30д", 30)]:
            tk.Button(quick, text=text, font=("Segoe UI", 8), bg=INPUT_BG, fg=TEXT,
                      relief="flat", cursor="hand2",
                      command=lambda d=days: self._quick_dates(d)).pack(side="left", padx=2)

        self._section(left, "ТУРИСТЫ")
        row = tk.Frame(left, bg=CARD)
        row.pack(fill="x", pady=(0, 6))
        tk.Label(row, text="Взрослые", font=("Segoe UI", 9), fg=MUTED, bg=CARD).pack(side="left")
        self.adults = self._spin(row, 1, 20, 2)
        tk.Label(row, text="  Дети", font=("Segoe UI", 9), fg=MUTED, bg=CARD).pack(side="left")
        self.children = self._spin(row, 0, 10, 0)

        self._section(left, "НОМЕР / ПИТАНИЕ")
        self.room = self._combo(left, ["любой", "single", "double", "family"], "любой")
        self.meal = self._combo(left, ["любой", "RO", "BB", "HB", "AI"], "любой")

        self._section(left, "БЮДЖЕТ ОТ / ДО (руб.)")
        self.min_budget = self._entry(left, "")
        self.budget = self._entry(left, "")

        self._section(left, "ДОП. УСЛУГИ")
        self.var_ins = tk.BooleanVar()
        self.var_tr = tk.BooleanVar()
        self.var_ex = tk.BooleanVar()
        for t, v in [("Страховка", self.var_ins), ("Трансфер", self.var_tr), ("Экскурсии", self.var_ex)]:
            tk.Checkbutton(left, text=t, variable=v, font=("Segoe UI", 10), fg=TEXT, bg=CARD,
                           selectcolor=INPUT_BG, activebackground=CARD, activeforeground=ACCENT,
                           cursor="hand2").pack(anchor="w")

        self._section(left, "СОРТИРОВКА")
        self.sort_by = self._combo(left, ["По цене ↑", "По цене ↓", "По дате", "По названию"], "По цене ↑")

        tk.Button(left, text="🔍  Найти туры", font=("Segoe UI", 11, "bold"),
                  bg=ACCENT, fg=BG, activebackground=ACCENT2, relief="flat",
                  cursor="hand2", pady=9, command=self.search).pack(fill="x", pady=(12, 5))

        row2 = tk.Frame(left, bg=CARD)
        row2.pack(fill="x")
        tk.Button(row2, text="Все туры", font=("Segoe UI", 9), bg=INPUT_BG, fg=TEXT,
                  relief="flat", cursor="hand2", pady=5, command=self.show_all).pack(
            side="left", expand=True, fill="x", padx=(0, 3))
        tk.Button(row2, text="Сбросить", font=("Segoe UI", 9), bg=INPUT_BG, fg=TEXT,
                  relief="flat", cursor="hand2", pady=5, command=self.reset).pack(
            side="left", expand=True, fill="x", padx=(3, 0))

        tk.Button(left, text="💾  Сохранить результаты", font=("Segoe UI", 9),
                  bg=CARD2, fg=TEXT, relief="flat", cursor="hand2", pady=6,
                  command=self.save_results).pack(fill="x", pady=(8, 0))

        row3 = tk.Frame(left, bg=CARD)
        row3.pack(fill="x", pady=(6, 0))
        tk.Button(row3, text="📊 Статистика", font=("Segoe UI", 9), bg=INPUT_BG, fg=TEXT,
                  relief="flat", cursor="hand2", pady=5, command=self.show_stats).pack(
            side="left", expand=True, fill="x", padx=(0, 3))
        tk.Button(row3, text="📋 Копировать", font=("Segoe UI", 9), bg=INPUT_BG, fg=TEXT,
                  relief="flat", cursor="hand2", pady=5, command=self.copy_results).pack(
            side="left", expand=True, fill="x", padx=(3, 0))

        # RIGHT
        right = tk.Frame(body, bg=CARD)
        right.pack(side="left", fill="both", expand=True)

        top = tk.Frame(right, bg=CARD)
        top.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(top, text="Результаты поиска", font=("Segoe UI", 14, "bold"),
                 fg=TEXT, bg=CARD).pack(side="left")
        self.counter = tk.Label(top, text="", font=("Segoe UI", 10, "bold"),
                                fg=ACCENT, bg=CARD)
        self.counter.pack(side="right")

        self.results = scrolledtext.ScrolledText(
            right, font=("Consolas", 11), bg=CARD, fg=TEXT, relief="flat",
            padx=16, pady=10, insertbackground=TEXT, wrap="word"
        )
        self.results.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        for tag, color, font in [
            ("title", ACCENT, ("Consolas", 12, "bold")),
            ("price", SUCCESS, ("Consolas", 11, "bold")),
            ("muted", MUTED, ("Consolas", 10)),
            ("error", ERROR, ("Consolas", 11, "bold")),
            ("ok", SUCCESS, ("Consolas", 11, "bold")),
            ("warn", WARNING, ("Consolas", 10)),
            ("head", ACCENT2, ("Consolas", 11, "bold")),
        ]:
            self.results.tag_configure(tag, foreground=color, font=font)

    def _section(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 8, "bold"),
                 fg=MUTED, bg=CARD, anchor="w").pack(fill="x", pady=(7, 2))

    def _entry(self, parent, default=""):
        e = tk.Entry(parent, font=("Segoe UI", 11), bg=INPUT_BG, fg=TEXT,
                     insertbackground=TEXT, relief="flat")
        e.pack(fill="x", pady=(0, 3), ipady=5)
        if default:
            e.insert(0, default)
        return e

    def _combo(self, parent, values, default):
        cb = ttk.Combobox(parent, values=values, font=("Segoe UI", 10), width=28)
        cb.pack(fill="x", pady=(0, 3), ipady=2)
        cb.set(default)
        return cb

    def _spin(self, parent, from_, to, default):
        sb = tk.Spinbox(parent, from_=from_, to=to, width=4, font=("Segoe UI", 11),
                        bg=INPUT_BG, fg=TEXT, buttonbackground=ACCENT,
                        relief="flat", insertbackground=TEXT)
        sb.pack(side="left", padx=4)
        sb.delete(0, "end")
        sb.insert(0, str(default))
        return sb

    def _quick_dates(self, days):
        start = datetime.now().date() + timedelta(days=7)
        end = start + timedelta(days=days)
        self.start_date.delete(0, "end")
        self.start_date.insert(0, start.strftime("%d.%m.%Y"))
        self.end_date.delete(0, "end")
        self.end_date.insert(0, end.strftime("%d.%m.%Y"))

    def parse_date(self, text):
        return datetime.strptime(text.strip(), "%d.%m.%Y").date()

    def _set_status(self, text):
        self.status.config(text=text)

    def _show_welcome(self):
        self.results.delete("1.0", "end")
        self.results.insert("end", "Добро пожаловать в TravelFinder!\n\n", "title")
        self.results.insert("end", "• Выберите направление и даты\n", "muted")
        self.results.insert("end", "• Можно искать по названию отеля\n", "muted")
        self.results.insert("end", "• Задайте бюджет от/до и доп. услуги\n", "muted")
        self.results.insert("end", "• Нажмите «Найти туры»\n\n", "muted")
        self.results.insert("end", "Подсказка: «Все туры» покажет всю базу.\n", "warn")
        self.counter.config(text="")
        self._set_status(f"База: {len(self.service.tours)} туров")

    def _display(self, results):
        self.results.delete("1.0", "end")

        if not results:
            self.results.insert("end", "Ничего не найдено\n\n", "error")
            self.results.insert("end", "Попробуйте:\n", "muted")
            self.results.insert("end", "• изменить даты или направление\n", "muted")
            self.results.insert("end", "• убрать фильтр номера/питания\n", "muted")
            self.results.insert("end", "• изменить бюджет\n", "muted")
            self.counter.config(text="0")
            self._set_status("Результатов нет")
            return

        sort = self.sort_by.get()
        if sort == "По цене ↑":
            results = sorted(results, key=lambda x: x["total_price"])
        elif sort == "По цене ↓":
            results = sorted(results, key=lambda x: -x["total_price"])
        elif sort == "По дате":
            results = sorted(results, key=lambda x: x["tour"].start_date)
        elif sort == "По названию":
            results = sorted(results, key=lambda x: x["tour"].name)

        self.results.insert("end", f"Найдено вариантов: {len(results)}\n", "ok")
        self.results.insert("end", "═" * 52 + "\n\n", "muted")

        for i, res in enumerate(results, 1):
            t = res["tour"]
            self.results.insert("end", f"{i}. {t.name}\n", "title")
            self.results.insert("end", f"   {t.destination}  •  "
                                f"{t.start_date.strftime('%d.%m.%Y')} — {t.end_date.strftime('%d.%m.%Y')}\n", "muted")
            self.results.insert("end", f"   Номер: {t.room_type}  |  Питание: {t.meal_type}  |  до {t.max_people} чел.\n", "muted")
            self.results.insert("end", f"   {res['total_price']:,.0f} руб.", "price")
            self.results.insert("end", f"   ({res['price_per_person']:,.0f} руб./чел.)\n", "muted")
            self.results.insert("end", f"   {t.description}\n", "muted")

            if "breakdown" in res:
                b = res["breakdown"]
                self.results.insert("end", "   ┌ Разбивка цены\n", "head")
                self.results.insert("end", f"   │ Взрослые:      {b['base_adults']:,.0f} ₽\n", "muted")
                if b["base_children"] > 0:
                    self.results.insert("end", f"   │ Дети (×0.7):   {b['base_children']:,.0f} ₽\n", "muted")
                self.results.insert("end", f"   │ Питание:       ×{b['meal_coeff']}\n", "muted")
                self.results.insert("end", f"   │ Номер:         ×{b['room_coeff']}\n", "muted")
                self.results.insert("end", f"   │ Сезон:         ×{b['season_coeff']}\n", "muted")
                if b["extras"] > 0:
                    self.results.insert("end", f"   │ Доп. услуги:   {b['extras']:,.0f} ₽\n", "muted")
                if b["early_discount"] > 0:
                    self.results.insert("end", f"   │ Скидка 5%:    −{b['early_discount']:,.0f} ₽\n", "warn")
                self.results.insert("end", f"   └ ИТОГО:         {b['total']:,.0f} ₽\n", "price")

            self.results.insert("end", "\n")

        self.counter.config(text=f"{len(results)} шт.")
        self._set_status(f"Показано: {len(results)}")

    def search(self):
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
                raise ValueError("Нужен хотя бы 1 взрослый")
            if children < 0:
                raise ValueError("Количество детей не может быть отрицательным")

            room = self.room.get()
            meal = self.meal.get()

            budget_text = self.budget.get().strip()
            max_budget = float(budget_text) if budget_text else None
            if max_budget is not None and max_budget < 0:
                raise ValueError("Максимальный бюджет не может быть отрицательным")

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
                preferred_room=None if room == "любой" else room,
                preferred_meal=None if meal == "любой" else meal,
                max_budget=max_budget,
                extra_services=extras
            )

            results = self.service.search(request)

            # фильтр по названию
            name_q = self.name_query.get().strip().lower()
            if name_q:
                results = [r for r in results if name_q in r["tour"].name.lower()]

            # фильтр по минимальному бюджету
            min_budget_text = self.min_budget.get().strip()
            if min_budget_text:
                min_b = float(min_budget_text)
                if min_b < 0:
                    raise ValueError("Минимальный бюджет не может быть отрицательным")
                results = [r for r in results if r["total_price"] >= min_b]

            for res in results:
                if hasattr(self.service, "get_price_breakdown"):
                    res["breakdown"] = self.service.get_price_breakdown(res["tour"], request)

            self.last_results = results
            self._display(results)
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_all(self):
        results = []
        for tour in self.service.tours:
            req = ClientRequest(
                destination=tour.destination,
                start_date=tour.start_date,
                end_date=tour.end_date,
                adults=2,
                children=0
            )
            price = self.service.calculate_price(tour, req)
            item = {
                "tour": tour,
                "total_price": round(price, 2),
                "price_per_person": round(price / 2, 2)
            }
            if hasattr(self.service, "get_price_breakdown"):
                item["breakdown"] = self.service.get_price_breakdown(tour, req)
            results.append(item)
        self.last_results = results
        self._display(results)

    def reset(self):
        self.destination.set("Турция")
        self.name_query.delete(0, "end")
        self.start_date.delete(0, "end")
        self.start_date.insert(0, "05.07.2025")
        self.end_date.delete(0, "end")
        self.end_date.insert(0, "15.07.2025")
        self.adults.delete(0, "end")
        self.adults.insert(0, "2")
        self.children.delete(0, "end")
        self.children.insert(0, "0")
        self.room.set("любой")
        self.meal.set("любой")
        self.min_budget.delete(0, "end")
        self.budget.delete(0, "end")
        self.var_ins.set(False)
        self.var_tr.set(False)
        self.var_ex.set(False)
        self.sort_by.set("По цене ↑")
        self._show_welcome()

    def save_results(self):
        if not self.last_results:
            messagebox.showinfo("Сохранение", "Нет результатов для сохранения.\nСначала выполните поиск.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовый файл", "*.txt"), ("Все файлы", "*.*")],
            initialfile="tours_result.txt"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("Результаты подбора туров\n")
                f.write("=" * 40 + "\n\n")
                for i, res in enumerate(self.last_results, 1):
                    t = res["tour"]
                    f.write(f"{i}. {t.name}\n")
                    f.write(f"   Направление: {t.destination}\n")
                    f.write(f"   Даты: {t.start_date.strftime('%d.%m.%Y')} — {t.end_date.strftime('%d.%m.%Y')}\n")
                    f.write(f"   Номер: {t.room_type} | Питание: {t.meal_type}\n")
                    f.write(f"   Стоимость: {res['total_price']:,.0f} руб.\n")
                    f.write(f"   {t.description}\n\n")
            messagebox.showinfo("Сохранение", f"Сохранено:\n{path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")

    def show_stats(self):
        if not self.last_results:
            messagebox.showinfo("Статистика", "Сначала выполните поиск.")
            return
        prices = [r["total_price"] for r in self.last_results]
        cheapest = min(self.last_results, key=lambda x: x["total_price"])
        expensive = max(self.last_results, key=lambda x: x["total_price"])
        avg = sum(prices) / len(prices)
        msg = (
            f"Найдено туров: {len(prices)}\n\n"
            f"Минимальная цена: {min(prices):,.0f} руб.\n"
            f"  → {cheapest['tour'].name}\n\n"
            f"Максимальная цена: {max(prices):,.0f} руб.\n"
            f"  → {expensive['tour'].name}\n\n"
            f"Средняя цена: {avg:,.0f} руб."
        )
        messagebox.showinfo("Статистика по результатам", msg)

    def copy_results(self):
        if not self.last_results:
            messagebox.showinfo("Копирование", "Нет результатов для копирования.")
            return
        lines = []
        for i, res in enumerate(self.last_results, 1):
            t = res["tour"]
            lines.append(
                f"{i}. {t.name} | {t.destination} | "
                f"{t.start_date.strftime('%d.%m.%Y')}-{t.end_date.strftime('%d.%m.%Y')} | "
                f"{res['total_price']:,.0f} руб."
            )
        text = "\n".join(lines)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self._set_status("Результаты скопированы")
        messagebox.showinfo("Копирование", "Результаты скопированы в буфер обмена.")


if __name__ == "__main__":
    root = tk.Tk()
    app = TourApp(root)
    root.mainloop()
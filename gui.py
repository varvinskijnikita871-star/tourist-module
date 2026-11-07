import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from main import ClientRequest, TourService, get_sample_tours

BG = "#0f172a"
CARD = "#1e293b"
ACCENT = "#38bdf8"
ACCENT2 = "#818cf8"
TEXT = "#f1f5f9"
MUTED = "#94a3b8"
SUCCESS = "#34d399"
ERROR = "#f87171"
INPUT_BG = "#334155"


class TourApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TravelFinder — подбор туров")
        self.root.geometry("1050x720")
        self.root.configure(bg=BG)
        self.root.minsize(950, 620)
        self.service = TourService(get_sample_tours())
        self.last_results = []
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=30, pady=(20, 8))
        tk.Label(header, text="TravelFinder", font=("Segoe UI", 26, "bold"),
                 fg=ACCENT, bg=BG).pack(side="left")
        tk.Label(header, text="  подбор и расчёт стоимости туров",
                 font=("Segoe UI", 12), fg=MUTED, bg=BG).pack(side="left", pady=(10, 0))

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=30, pady=8)

        left = tk.Frame(main, bg=CARD, padx=18, pady=16)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.configure(width=300)
        left.pack_propagate(False)

        self._label(left, "НАПРАВЛЕНИЕ")
        self.destination = self._combo(left, [
            "Турция", "Египет", "Греция", "Болгария", "Тунис", "ОАЭ",
            "Черногория", "Испания", "Россия", "Таиланд", "Мальдивы",
            "Италия", "Кипр", "Грузия"
        ], "Турция")

        self._label(left, "ДАТЫ (ДД.ММ.ГГГГ)")
        self.start_date = self._entry(left, "05.07.2025")
        self.end_date = self._entry(left, "15.07.2025")

        self._label(left, "ТУРИСТЫ")
        pf = tk.Frame(left, bg=CARD)
        pf.pack(fill="x", pady=(0, 8))
        tk.Label(pf, text="Взр.", font=("Segoe UI", 9), fg=MUTED, bg=CARD).pack(side="left")
        self.adults = self._spin(pf, 1, 20, 2)
        tk.Label(pf, text="  Дети", font=("Segoe UI", 9), fg=MUTED, bg=CARD).pack(side="left")
        self.children = self._spin(pf, 0, 10, 0)

        self._label(left, "НОМЕР")
        self.room = self._combo(left, ["любой", "single", "double", "family"], "любой")
        self._label(left, "ПИТАНИЕ")
        self.meal = self._combo(left, ["любой", "RO", "BB", "HB", "AI"], "любой")

        self._label(left, "БЮДЖЕТ (руб.)")
        self.budget = self._entry(left, "")

        self._label(left, "ДОП. УСЛУГИ")
        self.var_ins = tk.BooleanVar()
        self.var_tr = tk.BooleanVar()
        self.var_ex = tk.BooleanVar()
        for text, var in [("Страховка", self.var_ins), ("Трансфер", self.var_tr), ("Экскурсии", self.var_ex)]:
            tk.Checkbutton(left, text=text, variable=var, font=("Segoe UI", 10),
                           fg=TEXT, bg=CARD, selectcolor=INPUT_BG, activebackground=CARD,
                           activeforeground=ACCENT, cursor="hand2").pack(anchor="w")

        self._label(left, "СОРТИРОВКА")
        self.sort_by = self._combo(left, ["По цене (дешевле)", "По цене (дороже)", "По дате"], "По цене (дешевле)")

        tk.Button(left, text="Найти туры", font=("Segoe UI", 11, "bold"),
                  bg=ACCENT, fg=BG, activebackground=ACCENT2, relief="flat",
                  cursor="hand2", pady=8, command=self.search).pack(fill="x", pady=(14, 6))

        btn_row = tk.Frame(left, bg=CARD)
        btn_row.pack(fill="x")
        tk.Button(btn_row, text="Все туры", font=("Segoe UI", 9),
                  bg=INPUT_BG, fg=TEXT, relief="flat", cursor="hand2", pady=5,
                  command=self.show_all).pack(side="left", expand=True, fill="x", padx=(0, 4))
        tk.Button(btn_row, text="Сбросить", font=("Segoe UI", 9),
                  bg=INPUT_BG, fg=TEXT, relief="flat", cursor="hand2", pady=5,
                  command=self.reset).pack(side="left", expand=True, fill="x", padx=(4, 0))

        right = tk.Frame(main, bg=CARD)
        right.pack(side="left", fill="both", expand=True)

        rh = tk.Frame(right, bg=CARD)
        rh.pack(fill="x", padx=18, pady=(14, 4))
        tk.Label(rh, text="Результаты", font=("Segoe UI", 14, "bold"),
                 fg=TEXT, bg=CARD).pack(side="left")

        self.results = scrolledtext.ScrolledText(
            right, font=("Consolas", 11), bg=CARD, fg=TEXT, relief="flat",
            padx=18, pady=8, insertbackground=TEXT
        )
        self.results.pack(fill="both", expand=True, padx=6, pady=(0, 12))
        self.results.insert("1.0", "Введите параметры и нажмите «Найти туры»")

        self.results.tag_configure("title", foreground=ACCENT, font=("Consolas", 12, "bold"))
        self.results.tag_configure("price", foreground=SUCCESS, font=("Consolas", 11, "bold"))
        self.results.tag_configure("muted", foreground=MUTED)
        self.results.tag_configure("error", foreground=ERROR)
        self.results.tag_configure("ok", foreground=SUCCESS)

    def _label(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 8, "bold"),
                 fg=MUTED, bg=CARD, anchor="w").pack(fill="x", pady=(6, 2))

    def _entry(self, parent, default=""):
        e = tk.Entry(parent, font=("Segoe UI", 11), bg=INPUT_BG, fg=TEXT,
                     insertbackground=TEXT, relief="flat")
        e.pack(fill="x", pady=(0, 3), ipady=5)
        if default:
            e.insert(0, default)
        return e

    def _combo(self, parent, values, default):
        cb = ttk.Combobox(parent, values=values, font=("Segoe UI", 10), width=26)
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

    def parse_date(self, text):
        return datetime.strptime(text.strip(), "%d.%m.%Y").date()

    def _display(self, results):
        self.results.delete("1.0", "end")
        if not results:
            self.results.insert("end", "Подходящих туров не найдено\n\n", "error")
            self.results.insert("end", "Измените даты, направление или фильтры.", "muted")
            return

        sort = self.sort_by.get()
        if sort == "По цене (дешевле)":
            results = sorted(results, key=lambda x: x["total_price"])
        elif sort == "По цене (дороже)":
            results = sorted(results, key=lambda x: -x["total_price"])
        elif sort == "По дате":
            results = sorted(results, key=lambda x: x["tour"].start_date)

        self.results.insert("end", f"Найдено: {len(results)}\n", "ok")
        self.results.insert("end", "─" * 50 + "\n\n", "muted")

        for i, res in enumerate(results, 1):
            t = res["tour"]
            self.results.insert("end", f"{i}. {t.name}\n", "title")
            self.results.insert("end", f"   {t.destination}  •  "
                                f"{t.start_date.strftime('%d.%m.%Y')} — {t.end_date.strftime('%d.%m.%Y')}\n", "muted")
            self.results.insert("end", f"   Номер: {t.room_type}  |  Питание: {t.meal_type}\n", "muted")
            self.results.insert("end", f"   {res['total_price']:,.0f} руб.", "price")
            self.results.insert("end", f"  ({res['price_per_person']:,.0f} руб./чел.)\n", "muted")
            self.results.insert("end", f"   {t.description}\n", "muted")

            if "breakdown" in res:
                b = res["breakdown"]
                self.results.insert("end", "   ┌ Разбивка цены:\n", "muted")
                self.results.insert("end", f"   │  Взрослые:     {b['base_adults']:,.0f} руб.\n", "muted")
                if b["base_children"] > 0:
                    self.results.insert("end", f"   │  Дети (×0.7):  {b['base_children']:,.0f} руб.\n", "muted")
                self.results.insert("end", f"   │  Коэф. питания: ×{b['meal_coeff']}\n", "muted")
                self.results.insert("end", f"   │  Коэф. номера:  ×{b['room_coeff']}\n", "muted")
                self.results.insert("end", f"   │  Сезон:         ×{b['season_coeff']}\n", "muted")
                if b["extras"] > 0:
                    self.results.insert("end", f"   │  Доп. услуги:   {b['extras']:,.0f} руб.\n", "muted")
                if b["early_discount"] > 0:
                    self.results.insert("end", f"   │  Скидка 5%:    −{b['early_discount']:,.0f} руб.\n", "muted")
                self.results.insert("end", f"   └ Итого:         {b['total']:,.0f} руб.\n", "price")

            self.results.insert("end", "\n")

    def search(self):
        try:
            destination = self.destination.get().strip()
            if not destination:
                raise ValueError("Укажите направление")
            start = self.parse_date(self.start_date.get())
            end = self.parse_date(self.end_date.get())
            if end <= start:
                raise ValueError("Дата возвращения должна быть позже выезда")
            adults = int(self.adults.get())
            children = int(self.children.get())
            if adults < 1:
                raise ValueError("Нужен хотя бы 1 взрослый")

            room = self.room.get()
            meal = self.meal.get()
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
                destination=destination, start_date=start, end_date=end,
                adults=adults, children=children,
                preferred_room=None if room == "любой" else room,
                preferred_meal=None if meal == "любой" else meal,
                max_budget=max_budget, extra_services=extras
            )

            results = self.service.search(request)
            for res in results:
                res["breakdown"] = self.service.get_price_breakdown(res["tour"], request)

            self.last_results = results
            self._display(self.last_results)
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
                adults=2, children=0
            )
            price = self.service.calculate_price(tour, req)
            breakdown = self.service.get_price_breakdown(tour, req)
            results.append({
                "tour": tour,
                "total_price": round(price, 2),
                "price_per_person": round(price / 2, 2),
                "breakdown": breakdown
            })
        self.last_results = results
        self._display(results)

    def reset(self):
        self.destination.set("Турция")
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
        self.budget.delete(0, "end")
        self.var_ins.set(False)
        self.var_tr.set(False)
        self.var_ex.set(False)
        self.sort_by.set("По цене (дешевле)")
        self.results.delete("1.0", "end")
        self.results.insert("1.0", "Фильтры сброшены. Введите параметры поиска.")


if __name__ == "__main__":
    root = tk.Tk()
    app = TourApp(root)
    root.mainloop()
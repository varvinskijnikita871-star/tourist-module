from gui import TourApp
import tkinter as tk


def main():
    root = tk.Tk()
    app = TourApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
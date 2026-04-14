import tkinter as tk
from ui.MainFrame import MainFrame

class Main:
    @staticmethod
    def run():
        """Lance l'application"""
        fenetre = tk.Tk()
        MainFrame(fenetre)
        fenetre.mainloop()


if __name__ == "__main__":
    Main.run()
    
import tkinter as tk
from tkinter import ttk
from ui.AppareilFrame import AppareilFrame
from ui.PeriodeFrame import PeriodeFrame
from ui.UtilisationFrame import UtilisationFrame


class MainFrame:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion d'Énergie - Système Solaire")
        self.root.geometry("1000x650")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.appareil_frame = AppareilFrame(self.notebook)
        self.notebook.add(self.appareil_frame, text="Appareils")
        
        self.periode_frame = PeriodeFrame(self.notebook)
        self.notebook.add(self.periode_frame, text="Périodes")
        
        self.utilisation_frame = UtilisationFrame(self.notebook)
        self.notebook.add(self.utilisation_frame, text="Utilisations")


def create_windows():
    fenetre = tk.Tk()
    MainFrame(fenetre)
    fenetre.mainloop()

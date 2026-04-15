import tkinter as tk
from tkinter import ttk
from ui.AppareilFrame import AppareilFrame
from ui.DimensionnementFrame import DimensionnementFrame
from ui.PeriodeFrame import PeriodeFrame
from ui.UtilisationFrame import UtilisationFrame


class MainFrame:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestion d'Énergie - Système Solaire")
        self.root.geometry("1920x1080")
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.appareil_frame = AppareilFrame(self.notebook)
        self.notebook.add(self.appareil_frame, text="Appareils")
        
        self.periode_frame = PeriodeFrame(self.notebook)
        self.notebook.add(self.periode_frame, text="Périodes")
        
        self.utilisation_frame = UtilisationFrame(self.notebook)
        self.notebook.add(self.utilisation_frame, text="Utilisations")

        self.dimensionnement_frame = DimensionnementFrame(self.notebook)
        self.notebook.add(self.dimensionnement_frame, text="Dimensionnement")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event=None):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if hasattr(current_tab, "refresh_results"):
            current_tab.refresh_results()


def create_windows():
    fenetre = tk.Tk()
    MainFrame(fenetre)
    fenetre.mainloop()

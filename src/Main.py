import tkinter as tk
from database.DatabaseManager import DatabaseManager
from ui.MainFrame import MainFrame
from model.Materiel import Materiel

class Main:
    if __name__ == "__main__":
        test = Materiel.get_all_materiel()
        for ligne in test:
            print(ligne)
    
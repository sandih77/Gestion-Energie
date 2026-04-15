import tkinter as tk
from tkinter import ttk, messagebox

from model.EnergieCalculator import EnergieCalculator


class DimensionnementFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.result_vars = {}

        self.setup_ui()
        self.load_defaults()
        self.refresh_results()

    def setup_ui(self):
        params_frame = ttk.LabelFrame(self, text="Paramètres de calcul", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(params_frame, text="Rendement matin (%):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_matin = ttk.Entry(params_frame, width=12)
        self.entry_matin.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(params_frame, text="Rendement FA (%):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.entry_fa = ttk.Entry(params_frame, width=12)
        self.entry_fa.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(params_frame, text="Marge batterie pratique (%):").grid(row=0, column=4, sticky=tk.W, padx=5, pady=5)
        self.entry_batterie = ttk.Entry(params_frame, width=12)
        self.entry_batterie.grid(row=0, column=5, padx=5, pady=5)

        button_frame = ttk.Frame(params_frame)
        button_frame.grid(row=1, column=0, columnspan=6, pady=10)

        ttk.Button(button_frame, text="Calculer", command=self.refresh_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Réinitialiser", command=self.load_defaults).pack(side=tk.LEFT, padx=5)

        summary_frame = ttk.LabelFrame(self, text="Résultats de dimensionnement", padding=10)
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        rows = [
            ("Batterie théorique", "battery_theoretical_wh", "Wh"),
            ("Batterie pratique", "battery_practical_wh", "Wh"),
            ("Temps utilisation soirée", "soiree_usage_hours", "h"),
            ("Début charge batterie", "battery_charge_start", ""),
            ("Fin charge batterie", "battery_charge_end", ""),
            ("Puissance charge batterie", "battery_charge_power_w", "W"),
            ("Puissance charge batterie pratique", "battery_charge_practical_w", "W"),
            ("Panneau matin théorique", "panel_morning_theoretical_w", "W"),
            ("Panneau matin pratique", "panel_morning_practical_w", "W"),
            ("Panneau FA théorique", "panel_fa_theoretical_w", "W"),
            ("Panneau FA pratique", "panel_fa_practical_w", "W"),
            ("Panneau solaire nécessaire", "panel_required_w", "W"),
        ]

        for index, (label, key, unit) in enumerate(rows):
            ttk.Label(summary_frame, text=label + " :", width=30).grid(row=index, column=0, sticky=tk.W, padx=5, pady=6)
            value_var = tk.StringVar(value="0")
            self.result_vars[key] = value_var
            ttk.Label(summary_frame, textvariable=value_var, width=18, anchor=tk.E).grid(row=index, column=1, sticky=tk.E, padx=5, pady=6)
            ttk.Label(summary_frame, text=unit).grid(row=index, column=2, sticky=tk.W, padx=5, pady=6)

        self.info_label = ttk.Label(
            summary_frame,
            text="Matin: 6h-17h | FA: 17h-19h | Soirée: 19h-6h",
            foreground="#555555",
        )
        self.info_label.grid(row=len(rows), column=0, columnspan=3, sticky=tk.W, padx=5, pady=(10, 0))

    def load_defaults(self):
        defaults = EnergieCalculator.get_default_parameters()
        self.entry_matin.delete(0, tk.END)
        self.entry_matin.insert(0, str(defaults["matin_yield"]))
        self.entry_fa.delete(0, tk.END)
        self.entry_fa.insert(0, str(defaults["fa_yield"]))
        self.entry_batterie.delete(0, tk.END)
        self.entry_batterie.insert(0, str(defaults["battery_margin"]))

    def refresh_results(self):
        try:
            matin_yield = float(self.entry_matin.get().strip())
            fa_yield = float(self.entry_fa.get().strip())
            battery_margin = float(self.entry_batterie.get().strip())
        except ValueError:
            messagebox.showerror("Erreur", "Les paramètres doivent être des nombres valides")
            return

        results = EnergieCalculator.calculate_dimensionnement(matin_yield, fa_yield, battery_margin)

        self.result_vars["battery_theoretical_wh"].set(f"{results['battery_theoretical_wh']:.2f}")
        self.result_vars["battery_practical_wh"].set(f"{results['battery_practical_wh']:.2f}")
        self.result_vars["soiree_usage_hours"].set(f"{results['soiree_usage_hours']:.2f}")
        self.result_vars["battery_charge_start"].set(results["battery_charge_start"])
        self.result_vars["battery_charge_end"].set(results["battery_charge_end"])
        self.result_vars["battery_charge_power_w"].set(f"{results['battery_charge_power_w']:.2f}")
        self.result_vars["battery_charge_practical_w"].set(f"{results['battery_charge_practical_w']:.2f}")
        self.result_vars["panel_morning_theoretical_w"].set(f"{results['panel_morning_theoretical_w']:.2f}")
        self.result_vars["panel_morning_practical_w"].set(f"{results['panel_morning_practical_w']:.2f}")
        self.result_vars["panel_fa_theoretical_w"].set(f"{results['panel_fa_theoretical_w']:.2f}")
        self.result_vars["panel_fa_practical_w"].set(f"{results['panel_fa_practical_w']:.2f}")
        self.result_vars["panel_required_w"].set(f"{results['panel_required_w']:.2f}")
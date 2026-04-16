import tkinter as tk
from tkinter import ttk, messagebox

from model.EnergieCalculator import EnergieCalculator


class DimensionnementFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.result_vars_p1 = {}
        self.result_vars_p2 = {}
        self.result_vars_common = {}

        self.setup_ui()
        self.load_defaults()
        self.refresh_results()

    def setup_ui(self):
        params_frame = ttk.LabelFrame(self, text="Paramètres de calcul", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=10)

        p1_frame = ttk.LabelFrame(params_frame, text="Réglages P1", padding=8)
        p1_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        ttk.Label(p1_frame, text="Rendement matin (%):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=4)
        self.entry_p1_matin = ttk.Entry(p1_frame, width=10)
        self.entry_p1_matin.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(p1_frame, text="Rendement FA (%):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=4)
        self.entry_p1_fa = ttk.Entry(p1_frame, width=10)
        self.entry_p1_fa.grid(row=0, column=3, padx=5, pady=4)

        ttk.Label(p1_frame, text="Marge batterie (%):").grid(row=0, column=4, sticky=tk.W, padx=5, pady=4)
        self.entry_p1_batterie = ttk.Entry(p1_frame, width=10)
        self.entry_p1_batterie.grid(row=0, column=5, padx=5, pady=4)

        p2_frame = ttk.LabelFrame(params_frame, text="Réglages P2", padding=8)
        p2_frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        ttk.Label(p2_frame, text="Rendement matin (%):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=4)
        self.entry_p2_matin = ttk.Entry(p2_frame, width=10)
        self.entry_p2_matin.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(p2_frame, text="Rendement FA (%):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=4)
        self.entry_p2_fa = ttk.Entry(p2_frame, width=10)
        self.entry_p2_fa.grid(row=0, column=3, padx=5, pady=4)

        ttk.Label(p2_frame, text="Marge batterie (%):").grid(row=0, column=4, sticky=tk.W, padx=5, pady=4)
        self.entry_p2_batterie = ttk.Entry(p2_frame, width=10)
        self.entry_p2_batterie.grid(row=0, column=5, padx=5, pady=4)

        button_frame = ttk.Frame(params_frame)
        button_frame.grid(row=2, column=0, pady=10, sticky=tk.W)

        ttk.Button(button_frame, text="Calculer", command=self.refresh_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Réinitialiser", command=self.load_defaults).pack(side=tk.LEFT, padx=5)

        summary_frame = ttk.LabelFrame(self, text="Résultats de dimensionnement", padding=10)
        summary_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(summary_frame, text="Mesure", width=32).grid(row=0, column=0, sticky=tk.W, padx=5, pady=4)
        ttk.Label(summary_frame, text="P1", width=14, anchor=tk.E).grid(row=0, column=1, sticky=tk.E, padx=5, pady=4)
        ttk.Label(summary_frame, text="P2", width=14, anchor=tk.E).grid(row=0, column=2, sticky=tk.E, padx=5, pady=4)
        ttk.Label(summary_frame, text="Unité", width=8).grid(row=0, column=3, sticky=tk.W, padx=5, pady=4)

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

        for index, (label, key, unit) in enumerate(rows, start=1):
            ttk.Label(summary_frame, text=label + " :", width=32).grid(row=index, column=0, sticky=tk.W, padx=5, pady=4)

            p1_var = tk.StringVar(value="0")
            self.result_vars_p1[key] = p1_var
            ttk.Label(summary_frame, textvariable=p1_var, width=14, anchor=tk.E).grid(row=index, column=1, sticky=tk.E, padx=5, pady=4)

            p2_var = tk.StringVar(value="0")
            self.result_vars_p2[key] = p2_var
            ttk.Label(summary_frame, textvariable=p2_var, width=14, anchor=tk.E).grid(row=index, column=2, sticky=tk.E, padx=5, pady=4)

            ttk.Label(summary_frame, text=unit, width=8).grid(row=index, column=3, sticky=tk.W, padx=5, pady=4)

        commun_frame = ttk.LabelFrame(self, text="Résultats communs (P1 et P2)", padding=10)
        commun_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        common_rows = [
            ("Pic matin", "pic_matin_w", "W"),
            ("Pic FA", "pic_fa_w", "W"),
            ("Pic soirée", "pic_soiree_w", "W"),
            ("Puissance pic journée", "puissance_pic_journee_w", "W"),
            ("Puissance convertisseur", "puissance_convertisseur_w", "W"),
            ("Puissance convertisseur (appareils seuls)", "puissance_convertisseur_appareils_w", "W"),
        ]

        for index, (label, key, unit) in enumerate(common_rows):
            ttk.Label(commun_frame, text=label + " :", width=32).grid(row=index, column=0, sticky=tk.W, padx=5, pady=3)
            common_var = tk.StringVar(value="0")
            self.result_vars_common[key] = common_var
            ttk.Label(commun_frame, textvariable=common_var, width=14, anchor=tk.E).grid(row=index, column=1, sticky=tk.E, padx=5, pady=3)
            ttk.Label(commun_frame, text=unit).grid(row=index, column=2, sticky=tk.W, padx=5, pady=3)

        self.info_label = ttk.Label(
            commun_frame,
            text="Matin: 6h-17h | FA: 17h-19h | Soirée: 19h-6h",
            foreground="#555555",
        )
        self.info_label.grid(row=len(common_rows), column=0, columnspan=3, sticky=tk.W, padx=5, pady=(8, 0))

    def load_defaults(self):
        defaults = EnergieCalculator.get_default_parameters()

        self.entry_p1_matin.delete(0, tk.END)
        self.entry_p1_matin.insert(0, str(defaults["matin_yield"]))
        self.entry_p1_fa.delete(0, tk.END)
        self.entry_p1_fa.insert(0, str(defaults["fa_yield"]))
        self.entry_p1_batterie.delete(0, tk.END)
        self.entry_p1_batterie.insert(0, str(defaults["battery_margin"]))

        self.entry_p2_matin.delete(0, tk.END)
        self.entry_p2_matin.insert(0, str(defaults["matin_yield"]))
        self.entry_p2_fa.delete(0, tk.END)
        self.entry_p2_fa.insert(0, str(defaults["fa_yield"]))
        self.entry_p2_batterie.delete(0, tk.END)
        self.entry_p2_batterie.insert(0, str(defaults["battery_margin"]))

    def refresh_results(self):
        try:
            p1_matin_yield = float(self.entry_p1_matin.get().strip())
            p1_fa_yield = float(self.entry_p1_fa.get().strip())
            p1_battery_margin = float(self.entry_p1_batterie.get().strip())

            p2_matin_yield = float(self.entry_p2_matin.get().strip())
            p2_fa_yield = float(self.entry_p2_fa.get().strip())
            p2_battery_margin = float(self.entry_p2_batterie.get().strip())
        except ValueError:
            messagebox.showerror("Erreur", "Les paramètres doivent être des nombres valides")
            return

        results = EnergieCalculator.calculate_dimensionnement_double(
            p1_matin_yield,
            p1_fa_yield,
            p1_battery_margin,
            p2_matin_yield,
            p2_fa_yield,
            p2_battery_margin,
        )

        for key, var in self.result_vars_p1.items():
            p1_value = results["p1"][key]
            if isinstance(p1_value, (int, float)):
                var.set(f"{p1_value:.2f}")
            else:
                var.set(str(p1_value))

        for key, var in self.result_vars_p2.items():
            p2_value = results["p2"][key]
            if isinstance(p2_value, (int, float)):
                var.set(f"{p2_value:.2f}")
            else:
                var.set(str(p2_value))

        for key, var in self.result_vars_common.items():
            common_value = results["commun"][key]
            if isinstance(common_value, (int, float)):
                var.set(f"{common_value:.2f}")
            else:
                var.set(str(common_value))
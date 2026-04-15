import tkinter as tk
from tkinter import ttk, messagebox
import re
from model.Materiel import Appareil
from model.Periode import Periode
from model.Utilisation import Utilisation


class UtilisationFrame(ttk.Frame):
    """Cadre pour gérer les utilisations"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.selected_id = None
        self.appareil_map = {}
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        form_frame = ttk.LabelFrame(self, text="Ajouter/Modifier une Utilisation", padding=10)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Appareil:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.combo_appareil = ttk.Combobox(form_frame, width=25, state="readonly")
        self.combo_appareil.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Heure début (HH:MM):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_debut = ttk.Entry(form_frame, width=20)
        self.entry_debut.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Heure fin (HH:MM):").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.entry_fin = ttk.Entry(form_frame, width=20)
        self.entry_fin.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(
            form_frame,
            text="Période et durée: calculées automatiquement selon les périodes",
        ).grid(row=2, column=0, columnspan=4, sticky=tk.W, padx=5, pady=5)
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Ajouter", command=self.add_utilisation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Modifier", command=self.update_utilisation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.delete_utilisation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Rafraîchir", command=self.refresh_data).pack(side=tk.LEFT, padx=5)
        
        list_frame = ttk.LabelFrame(self, text="Liste des Utilisations", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tree = ttk.Treeview(list_frame, columns=("ID", "Appareil", "Période", "Début", "Fin", "Durée"), height=15)
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("ID", anchor=tk.CENTER, width=50)
        self.tree.column("Appareil", anchor=tk.W, width=120)
        self.tree.column("Période", anchor=tk.W, width=100)
        self.tree.column("Début", anchor=tk.CENTER, width=100)
        self.tree.column("Fin", anchor=tk.CENTER, width=100)
        self.tree.column("Durée", anchor=tk.CENTER, width=100)
        
        self.tree.heading("#0", text="", anchor=tk.CENTER)
        self.tree.heading("ID", text="ID", anchor=tk.CENTER)
        self.tree.heading("Appareil", text="Appareil", anchor=tk.CENTER)
        self.tree.heading("Période", text="Période", anchor=tk.CENTER)
        self.tree.heading("Début", text="Début", anchor=tk.CENTER)
        self.tree.heading("Fin", text="Fin", anchor=tk.CENTER)
        self.tree.heading("Durée", text="Durée (h)", anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<Double-1>", self.on_item_select)

    def _parse_time(self, raw):
        value = (raw or "").strip().lower()
        # Accepte: 8, 08:30, 8h30, 06:00:00 (format SQL Server)
        match = re.fullmatch(r"(\d{1,2})(?:[:h](\d{1,2}))?(?:[:h](\d{1,2}))?", value)
        if not match:
            raise ValueError(f"Format horaire invalide: {raw}")

        hours = int(match.group(1))
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        if hours < 0 or hours > 23 or minutes < 0 or minutes > 59 or seconds < 0 or seconds > 59:
            raise ValueError(f"Heure hors limites: {raw}")

        return hours * 60 + minutes

    def _minutes_to_hhmm(self, total_minutes):
        minutes = total_minutes % 1440
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"

    def _split_interval(self, start_min, end_min):
        if end_min > start_min:
            return [(start_min, end_min)]
        return [(start_min, 1440), (0, end_min)]

    def _build_period_segments(self):
        segments = []
        for periode in Periode.get_all():
            if not periode.heure_debut or not periode.heure_fin:
                continue

            start_min = self._parse_time(str(periode.heure_debut))
            end_min = self._parse_time(str(periode.heure_fin))

            if start_min == end_min:
                continue

            if end_min > start_min:
                segments.append((start_min, end_min, periode.id))
            else:
                segments.append((start_min, 1440, periode.id))
                segments.append((0, end_min, periode.id))

        return segments

    def _split_usage_by_period(self, start_min, end_min):
        period_segments = self._build_period_segments()
        usage_segments = self._split_interval(start_min, end_min)
        splits = []

        for usage_start, usage_end in usage_segments:
            for period_start, period_end, period_id in period_segments:
                overlap_start = max(usage_start, period_start)
                overlap_end = min(usage_end, period_end)
                if overlap_start < overlap_end:
                    splits.append((overlap_start, overlap_end, period_id))

        # Déduplication simple au cas où les périodes se recouvrent mal en base.
        unique = list({(s, e, p) for s, e, p in splits})

        def order_key(item):
            start = item[0]
            if start < start_min:
                return start + 1440
            return start

        unique.sort(key=order_key)
        return unique
    
    def refresh_comboboxes(self):
        appareils = Appareil.get_all()
        self.appareil_map = {f"{app.id}: {app.nom}": app.id for app in appareils}
        self.combo_appareil["values"] = list(self.appareil_map.keys())
    
    def add_utilisation(self):
        try:
            app_choice = self.combo_appareil.get()
            debut_raw = self.entry_debut.get().strip()
            fin_raw = self.entry_fin.get().strip()

            if not app_choice or not debut_raw or not fin_raw:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs correctement")
                return

            start_min = self._parse_time(debut_raw)
            end_min = self._parse_time(fin_raw)

            if start_min == end_min:
                messagebox.showerror("Erreur", "L'heure de fin doit être différente de l'heure de début")
                return

            splits = self._split_usage_by_period(start_min, end_min)
            if not splits:
                messagebox.showerror(
                    "Erreur",
                    "Aucun chevauchement trouvé avec les périodes. Vérifiez les périodes en base.",
                )
                return

            app_id = self.appareil_map[app_choice]

            success_count = 0
            for split_start, split_end, period_id in splits:
                duree = (split_end - split_start) / 60.0
                if Utilisation.create(
                    app_id,
                    period_id,
                    self._minutes_to_hhmm(split_start),
                    self._minutes_to_hhmm(split_end),
                    round(duree, 2),
                ):
                    success_count += 1

            if success_count != len(splits):
                messagebox.showerror("Erreur", "Impossible d'ajouter l'utilisation")
                return

            messagebox.showinfo(
                "Succès",
                f"Utilisation ajoutée et découpée automatiquement en {success_count} ligne(s)",
            )
            self.clear_form()
            self.refresh_data()
        except ValueError:
            messagebox.showerror("Erreur", "Format horaire invalide. Exemple: 08:00 ou 8h30")
    
    def update_utilisation(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Erreur", "Sélectionnez une utilisation à modifier")
            return
        
        item = selection[0]
        values = self.tree.item(item)["values"]
        util_id = values[0]
        
        try:
            app_choice = self.combo_appareil.get()
            debut_raw = self.entry_debut.get().strip()
            fin_raw = self.entry_fin.get().strip()

            if not app_choice or not debut_raw or not fin_raw:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs correctement")
                return

            start_min = self._parse_time(debut_raw)
            end_min = self._parse_time(fin_raw)
            if start_min == end_min:
                messagebox.showerror("Erreur", "L'heure de fin doit être différente de l'heure de début")
                return

            splits = self._split_usage_by_period(start_min, end_min)
            if len(splits) != 1:
                messagebox.showerror(
                    "Erreur",
                    "La modification d'une seule ligne doit rester dans une seule période. "
                    "Supprimez puis ajoutez pour un découpage multi-périodes.",
                )
                return

            app_id = self.appareil_map[app_choice]
            split_start, split_end, period_id = splits[0]
            duree = round((split_end - split_start) / 60.0, 2)

            if Utilisation.update(
                util_id,
                app_id,
                period_id,
                self._minutes_to_hhmm(split_start),
                self._minutes_to_hhmm(split_end),
                duree,
            ):
                messagebox.showinfo("Succès", "Utilisation modifiée avec succès")
                self.clear_form()
                self.refresh_data()
            else:
                messagebox.showerror("Erreur", "Impossible de modifier l'utilisation")
        except ValueError:
            messagebox.showerror("Erreur", "Format horaire invalide. Exemple: 08:00 ou 8h30")
    
    def delete_utilisation(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Erreur", "Sélectionnez une utilisation à supprimer")
            return
        
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette utilisation?"):
            item = selection[0]
            values = self.tree.item(item)["values"]
            util_id = values[0]
            
            if Utilisation.delete(util_id):
                messagebox.showinfo("Succès", "Utilisation supprimée avec succès")
                self.refresh_data()
            else:
                messagebox.showerror("Erreur", "Impossible de supprimer l'utilisation")
    
    def refresh_data(self):
        self.refresh_comboboxes()
        self.refresh_utilisations()
    
    def refresh_utilisations(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        utilisations = Utilisation.get_all()
        appareils_map = {app.id: app.nom for app in Appareil.get_all()}
        periodes_map = {per.id: per.nom for per in Periode.get_all()}
        
        for util in utilisations:
            app_name = appareils_map.get(util.appareil_id, "N/A")
            per_name = periodes_map.get(util.periode_id, "N/A")
            self.tree.insert("", tk.END, values=(util.id, app_name, per_name, util.heure_debut, util.heure_fin, util.duree_heures))
    
    def on_item_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)["values"]
            
            utilisations = Utilisation.get_all()
            for util in utilisations:
                if util.id == values[0]:
                    appareils = Appareil.get_all()
                    for app in appareils:
                        if app.id == util.appareil_id:
                            self.combo_appareil.set(f"{app.id}: {app.nom}")
                            break
                    
                    periodes = Periode.get_all()
                    for per in periodes:
                        if per.id == util.periode_id:
                            break
                    
                    self.entry_debut.delete(0, tk.END)
                    self.entry_debut.insert(0, util.heure_debut)
                    self.entry_fin.delete(0, tk.END)
                    self.entry_fin.insert(0, util.heure_fin)
                    self.selected_id = util.id
                    break
    
    def clear_form(self):
        self.combo_appareil.set("")
        self.entry_debut.delete(0, tk.END)
        self.entry_fin.delete(0, tk.END)
        self.selected_id = None

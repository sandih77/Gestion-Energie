import tkinter as tk
from tkinter import ttk, messagebox
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
        self.periode_map = {}
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        form_frame = ttk.LabelFrame(self, text="Ajouter/Modifier une Utilisation", padding=10)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Appareil:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.combo_appareil = ttk.Combobox(form_frame, width=25, state="readonly")
        self.combo_appareil.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Période:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.combo_periode = ttk.Combobox(form_frame, width=25, state="readonly")
        self.combo_periode.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Heure début (HH:MM):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_debut = ttk.Entry(form_frame, width=20)
        self.entry_debut.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Heure fin (HH:MM):").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.entry_fin = ttk.Entry(form_frame, width=20)
        self.entry_fin.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Durée (heures):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_duree = ttk.Entry(form_frame, width=20)
        self.entry_duree.grid(row=2, column=1, padx=5, pady=5)
        
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
    
    def refresh_comboboxes(self):
        appareils = Appareil.get_all()
        self.appareil_map = {f"{app.id}: {app.nom}": app.id for app in appareils}
        self.combo_appareil["values"] = list(self.appareil_map.keys())
        
        periodes = Periode.get_all()
        self.periode_map = {f"{per.id}: {per.nom}": per.id for per in periodes}
        self.combo_periode["values"] = list(self.periode_map.keys())
    
    def add_utilisation(self):
        try:
            app_choice = self.combo_appareil.get()
            per_choice = self.combo_periode.get()
            debut = self.entry_debut.get().strip()
            fin = self.entry_fin.get().strip()
            duree = float(self.entry_duree.get().strip())
            
            if not app_choice or not per_choice or not debut or not fin or duree <= 0:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs correctement")
                return
            
            app_id = self.appareil_map[app_choice]
            per_id = self.periode_map[per_choice]
            
            if Utilisation.create(app_id, per_id, debut, fin, duree):
                messagebox.showinfo("Succès", "Utilisation ajoutée avec succès")
                self.clear_form()
                self.refresh_data()
            else:
                messagebox.showerror("Erreur", "Impossible d'ajouter l'utilisation")
        except ValueError:
            messagebox.showerror("Erreur", "Format invalide. Vérifiez la durée (nombre)")
    
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
            per_choice = self.combo_periode.get()
            debut = self.entry_debut.get().strip()
            fin = self.entry_fin.get().strip()
            duree = float(self.entry_duree.get().strip())
            
            if not app_choice or not per_choice or not debut or not fin or duree <= 0:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs correctement")
                return
            
            app_id = self.appareil_map[app_choice]
            per_id = self.periode_map[per_choice]
            
            if Utilisation.update(util_id, app_id, per_id, debut, fin, duree):
                messagebox.showinfo("Succès", "Utilisation modifiée avec succès")
                self.clear_form()
                self.refresh_data()
            else:
                messagebox.showerror("Erreur", "Impossible de modifier l'utilisation")
        except ValueError:
            messagebox.showerror("Erreur", "Format invalide")
    
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
                            self.combo_periode.set(f"{per.id}: {per.nom}")
                            break
                    
                    self.entry_debut.delete(0, tk.END)
                    self.entry_debut.insert(0, util.heure_debut)
                    self.entry_fin.delete(0, tk.END)
                    self.entry_fin.insert(0, util.heure_fin)
                    self.entry_duree.delete(0, tk.END)
                    self.entry_duree.insert(0, util.duree_heures)
                    self.selected_id = util.id
                    break
    
    def clear_form(self):
        self.combo_appareil.set("")
        self.combo_periode.set("")
        self.entry_debut.delete(0, tk.END)
        self.entry_fin.delete(0, tk.END)
        self.entry_duree.delete(0, tk.END)
        self.selected_id = None

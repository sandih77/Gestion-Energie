import tkinter as tk
from tkinter import ttk, messagebox
from model.Periode import Periode


class PeriodeFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.selected_id = None
        
        self.setup_ui()
        self.refresh_periodes()
    
    def setup_ui(self):
        form_frame = ttk.LabelFrame(self, text="Ajouter/Modifier une Période", padding=10)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Nom:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_nom = ttk.Entry(form_frame, width=20)
        self.entry_nom.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Heure début (HH:MM):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.entry_debut = ttk.Entry(form_frame, width=15)
        self.entry_debut.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Heure fin (HH:MM):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_fin = ttk.Entry(form_frame, width=15)
        self.entry_fin.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Rendement panneau (%):").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.entry_rendement = ttk.Entry(form_frame, width=15)
        self.entry_rendement.grid(row=1, column=3, padx=5, pady=5)
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Ajouter", command=self.add_periode).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Modifier", command=self.update_periode).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.delete_periode).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Rafraîchir", command=self.refresh_periodes).pack(side=tk.LEFT, padx=5)
        
        list_frame = ttk.LabelFrame(self, text="Liste des Périodes", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tree = ttk.Treeview(list_frame, columns=("ID", "Nom", "Début", "Fin", "Rendement"), height=15)
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("ID", anchor=tk.CENTER, width=50)
        self.tree.column("Nom", anchor=tk.W, width=120)
        self.tree.column("Début", anchor=tk.CENTER, width=100)
        self.tree.column("Fin", anchor=tk.CENTER, width=100)
        self.tree.column("Rendement", anchor=tk.CENTER, width=100)
        
        self.tree.heading("#0", text="", anchor=tk.CENTER)
        self.tree.heading("ID", text="ID", anchor=tk.CENTER)
        self.tree.heading("Nom", text="Nom", anchor=tk.CENTER)
        self.tree.heading("Début", text="Début", anchor=tk.CENTER)
        self.tree.heading("Fin", text="Fin", anchor=tk.CENTER)
        self.tree.heading("Rendement", text="Rendement (%)", anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<Double-1>", self.on_item_select)
    
    def add_periode(self):
        nom = self.entry_nom.get().strip()
        debut = self.entry_debut.get().strip()
        fin = self.entry_fin.get().strip()
        
        try:
            rendement = float(self.entry_rendement.get().strip())
            if not nom or not debut or not fin or rendement < 0:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs correctement")
                return
            if Periode.create(nom, debut, fin, rendement):
                messagebox.showinfo("Succès", "Période ajoutée avec succès")
                self.clear_form()
                self.refresh_periodes()
            else:
                messagebox.showerror("Erreur", "Impossible d'ajouter la période")
        except ValueError:
            messagebox.showerror("Erreur", "Format invalide. Rendement doit être un nombre")
    
    def update_periode(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Erreur", "Sélectionnez une période à modifier")
            return
        
        item = selection[0]
        values = self.tree.item(item)["values"]
        per_id = values[0]
        
        nom = self.entry_nom.get().strip()
        debut = self.entry_debut.get().strip()
        fin = self.entry_fin.get().strip()
        
        try:
            rendement = float(self.entry_rendement.get().strip())
            if not nom or not debut or not fin or rendement < 0:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs correctement")
                return
            if Periode.update(per_id, nom, debut, fin, rendement):
                messagebox.showinfo("Succès", "Période modifiée avec succès")
                self.clear_form()
                self.refresh_periodes()
            else:
                messagebox.showerror("Erreur", "Impossible de modifier la période")
        except ValueError:
            messagebox.showerror("Erreur", "Format invalide")
    
    def delete_periode(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Erreur", "Sélectionnez une période à supprimer")
            return
        
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette période?"):
            item = selection[0]
            values = self.tree.item(item)["values"]
            per_id = values[0]
            
            if Periode.delete(per_id):
                messagebox.showinfo("Succès", "Période supprimée avec succès")
                self.refresh_periodes()
            else:
                messagebox.showerror("Erreur", "Impossible de supprimer la période")
    
    def refresh_periodes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        periodes = Periode.get_all()
        for per in periodes:
            self.tree.insert("", tk.END, values=(per.id, per.nom, per.heure_debut, per.heure_fin, per.rendement_panneau))
    
    def on_item_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)["values"]
            self.selected_id = values[0]
            self.entry_nom.delete(0, tk.END)
            self.entry_nom.insert(0, values[1])
            self.entry_debut.delete(0, tk.END)
            self.entry_debut.insert(0, values[2])
            self.entry_fin.delete(0, tk.END)
            self.entry_fin.insert(0, values[3])
            self.entry_rendement.delete(0, tk.END)
            self.entry_rendement.insert(0, values[4])
    
    def clear_form(self):
        self.entry_nom.delete(0, tk.END)
        self.entry_debut.delete(0, tk.END)
        self.entry_fin.delete(0, tk.END)
        self.entry_rendement.delete(0, tk.END)
        self.selected_id = None

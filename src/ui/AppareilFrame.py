import tkinter as tk
from tkinter import ttk, messagebox
from model.Materiel import Appareil


class AppareilFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.selected_id = None
        
        self.setup_ui()
        self.refresh_appareils()
    
    def setup_ui(self):
        form_frame = ttk.LabelFrame(self, text="Ajouter/Modifier un Appareil", padding=10)
        form_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Nom:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_nom = ttk.Entry(form_frame, width=30)
        self.entry_nom.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Puissance (W):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.entry_puissance = ttk.Entry(form_frame, width=15)
        self.entry_puissance.grid(row=0, column=3, padx=5, pady=5)
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Ajouter", command=self.add_appareil).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Modifier", command=self.update_appareil).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.delete_appareil).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Rafraîchir", command=self.refresh_appareils).pack(side=tk.LEFT, padx=5)
        
        list_frame = ttk.LabelFrame(self, text="Liste des Appareils", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.tree = ttk.Treeview(list_frame, columns=("ID", "Nom", "Puissance"), height=15)
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("ID", anchor=tk.CENTER, width=50)
        self.tree.column("Nom", anchor=tk.W, width=400)
        self.tree.column("Puissance", anchor=tk.CENTER, width=150)
        
        self.tree.heading("#0", text="", anchor=tk.CENTER)
        self.tree.heading("ID", text="ID", anchor=tk.CENTER)
        self.tree.heading("Nom", text="Nom", anchor=tk.CENTER)
        self.tree.heading("Puissance", text="Puissance (W)", anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<Double-1>", self.on_item_select)
    
    def add_appareil(self):
        nom = self.entry_nom.get().strip()
        try:
            puissance = int(self.entry_puissance.get().strip())
            if not nom or puissance <= 0:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs correctement")
                return
            if Appareil.create(nom, puissance):
                messagebox.showinfo("Succès", "Appareil ajouté avec succès")
                self.clear_form()
                self.refresh_appareils()
            else:
                messagebox.showerror("Erreur", "Impossible d'ajouter l'appareil")
        except ValueError:
            messagebox.showerror("Erreur", "La puissance doit être un nombre entier")
    
    def update_appareil(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Erreur", "Sélectionnez un appareil à modifier")
            return
        
        item = selection[0]
        values = self.tree.item(item)["values"]
        app_id = values[0]
        
        nom = self.entry_nom.get().strip()
        try:
            puissance = int(self.entry_puissance.get().strip())
            if not nom or puissance <= 0:
                messagebox.showerror("Erreur", "Veuillez remplir tous les champs correctement")
                return
            if Appareil.update(app_id, nom, puissance):
                messagebox.showinfo("Succès", "Appareil modifié avec succès")
                self.clear_form()
                self.refresh_appareils()
            else:
                messagebox.showerror("Erreur", "Impossible de modifier l'appareil")
        except ValueError:
            messagebox.showerror("Erreur", "La puissance doit être un nombre entier")
    
    def delete_appareil(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Erreur", "Sélectionnez un appareil à supprimer")
            return
        
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cet appareil?"):
            item = selection[0]
            values = self.tree.item(item)["values"]
            app_id = values[0]
            
            if Appareil.delete(app_id):
                messagebox.showinfo("Succès", "Appareil supprimé avec succès")
                self.refresh_appareils()
            else:
                messagebox.showerror("Erreur", "Impossible de supprimer l'appareil")
    
    def refresh_appareils(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        appareils = Appareil.get_all()
        for app in appareils:
            self.tree.insert("", tk.END, values=(app.id, app.nom, app.puissance_w))
    
    def on_item_select(self, event):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)["values"]
            self.selected_id = values[0]
            self.entry_nom.delete(0, tk.END)
            self.entry_nom.insert(0, values[1])
            self.entry_puissance.delete(0, tk.END)
            self.entry_puissance.insert(0, values[2])
    
    def clear_form(self):
        self.entry_nom.delete(0, tk.END)
        self.entry_puissance.delete(0, tk.END)
        self.selected_id = None

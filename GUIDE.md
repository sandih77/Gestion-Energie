# Gestion d'Énergie - Guide d'Utilisation

## Architecture du Projet

### Structure des Dossiers

```
src/
├── Main.py                          # Point d'entrée de l'application
├── database/
│   └── DatabaseManager.py           # Gestionnaire de connexion SQL Server
├── model/
│   ├── Materiel.py (Appareil)      # Modèle pour les appareils
│   ├── Periode.py                   # Modèle pour les périodes
│   ├── Utilisation.py              # Modèle pour les utilisations
│   ├── Batterie.py                 # Modèle pour la batterie
│   └── PanneauSolaire.py           # Modèle pour le panneau solaire
└── ui/
    └── MainFrame.py                 # Interface Tkinter
```

## Installation

### Prérequis
- Python 3.7+
- SQL Server
- ODBC Driver 18 for SQL Server

### Installation des dépendances

```bash
pip install pyodbc
```

## Configuration

### Connexion à la Base de Données

Editez [DatabaseManager.py](src/database/DatabaseManager.py) pour configurer :

```python
self.server = "localhost"           # Serveur SQL Server
self.database = "gestion_energie"   # Nom de la base
self.uid = "SA"                    # Utilisateur
self.pwd = "Sqlserver123!"         # Mot de passe
```

### Création de la Base de Données

1. Ouvrez SQL Server Management Studio
2. Exécutez le script [schema.sql](script/schema.sql)

## Utilisation

### Démarrer l'Application

```bash
python src/Main.py
```

## Interface Tkinter

L'application propose 4 onglets :

#### **Onglet Appareils**
- Ajouter un nouvel appareil avec son nom et sa puissance (W)
- Modifier les données d'un appareil (double-clic sur la ligne)
- Supprimer un appareil
- Voir tous les appareils en temps réel

#### **Onglet Périodes**
- Ajouter une période (Matin, FA, Soirée) avec :
  - Nom
  - Heure de début (HH:MM)
  - Heure de fin (HH:MM)
  - Rendement du panneau (%)
- Modifier une période existante
- Supprimer une période

#### **Onglet Utilisations**
- Choisir l'appareil et saisir seulement l'heure de début et de fin
- Découper automatiquement l'utilisation selon les périodes (Matin, FA, Soirée, etc.)
- Calculer automatiquement la durée de chaque ligne créée
- Modifier ou supprimer les utilisations

#### **Onglet Dimensionnement**
- Calculer la puissance batterie théorique et pratique en Wh
- Calculer la puissance panneau solaire théorique et pratique en W
- Ajuster les coefficients de rendement du matin, de la FA et la marge pratique de batterie
- Recalculer automatiquement les résultats à partir des données en base

## CRUD - Modèles

Chaque modèle possède les méthodes CRUD suivantes :

### Appareil

```python
from model.Materiel import Appareil

# Récupérer tous les appareils
appareils = Appareil.get_all()

# Récupérer un appareil par ID
appareil = Appareil.get_by_id(1)

# Créer un appareil
Appareil.create("PC", 50)

# Modifier un appareil
Appareil.update(1, "PC Gamer", 100)

# Supprimer un appareil
Appareil.delete(1)
```

### Periode

```python
from model.Periode import Periode

# Récupérer toutes les périodes
periodes = Periode.get_all()

# Récupérer une période par ID
periode = Periode.get_by_id(1)

# Créer une période
Periode.create("Matin", "06:00", "17:00", 40)

# Modifier une période
Periode.update(1, "Matin", "06:00", "17:00", 40)

# Supprimer une période
Periode.delete(1)
```

### Utilisation

```python
from model.Utilisation import Utilisation

# Récupérer toutes les utilisations
utilisations = Utilisation.get_all()

# Récupérer une utilisation par ID
utilisation = Utilisation.get_by_id(1)

# Récupérer les utilisations d'un appareil
utilisations = Utilisation.get_by_appareil(1)

# Créer une utilisation
Utilisation.create(
    appareil_id=1, 
    periode_id=1, 
    heure_debut="09:00", 
    heure_fin="11:00", 
    duree_heures=2
)

# Modifier une utilisation
Utilisation.update(
    id=1,
    appareil_id=1, 
    periode_id=1, 
    heure_debut="09:00", 
    heure_fin="11:00", 
    duree_heures=2
)

# Supprimer une utilisation
Utilisation.delete(1)
```

## Exemples d'Utilisation

### Exemple 1 : Ajouter un PC de 50W utilisé 2 heures le matin

1. Allez dans **Appareils** → Ajoutez "PC" avec 50W
2. Allez dans **Périodes** → Vérifiez que "Matin" existe (06:00-17:00, 40%)
3. Allez dans **Utilisations** → Sélectionnez "PC" et "Matin"
4. Entrez l'heure début (09:00) et fin (11:00), durée (2h)
5. Cliquez "Ajouter"

### Exemple 2 : Récupérer les données via code

```python
from model.Materiel import Appareil
from model.Periode import Periode
from model.Utilisation import Utilisation

# Récupérer tous les appareils
appareils = Appareil.get_all()
for app in appareils:
    print(f"{app.nom}: {app.puissance_w}W")

# Récupérer les utilisations d'un appareil spécifique
pc = Appareil.get_by_id(1)
utilisations = Utilisation.get_by_appareil(pc.id)
for util in utilisations:
    print(f"Utilisation: {util.duree_heures}h")
```

## Calculs d'Énergie

La classe [EnergieCalculator.py](src/model/EnergieCalculator.py) fournit les calculs de dimensionnement suivants :

- `EnergieCalculator.get_default_parameters()` : charge les coefficients par défaut depuis les périodes en base
- `EnergieCalculator.calculate_dimensionnement(...)` : retourne les valeurs théoriques et pratiques de la batterie et du panneau solaire
- La batterie couvre la période du soir et de la nuit, tandis que le panneau couvre le matin et la FA

## Fichiers Importants

- [DatabaseManager.py](src/database/DatabaseManager.py) - Configuration base de données
- [schema.sql](script/schema.sql) - Structure de la base de données
- [Main.py](src/Main.py) - Point d'entrée
- [MainFrame.py](src/ui/MainFrame.py) - Interface utilisateur

## Prochaines Étapes

1. **Tests** : Ajouter des tests unitaires pour chaque modèle
2. **Calculs** : Implémenter les calculs d'énergie solaire/batterie
3. **Rapports** : Ajouter un onglet pour générer des rapports
4. **Export** : Ajouter la capacité à exporter les données en CSV/PDF
5. **Graphiques** : Ajouter des graphiques de consommation avec matplotlib

## Dépannage

### Erreur : "Erreur de connexion"
- Vérifiez que SQL Server est en cours d'exécution
- Vérifiez les paramètres de connexion dans DatabaseManager.py
- Assurez-vous que ODBC Driver 18 for SQL Server est installé

### Erreur : "La base de données n'existe pas"
- Exécutez schema.sql pour créer la base de données

### Erreur : "Référence de clé étrangère"
- Assurez-vous d'avoir créé les périodes et appareils avant les utilisations

## Support

Pour plus d'informations sur Tkinter : https://docs.python.org/3/library/tkinter.html
Pour pyodbc : https://github.com/mkleehammer/pyodbc

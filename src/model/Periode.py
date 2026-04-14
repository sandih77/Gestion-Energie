from database.DatabaseManager import DatabaseManager

class Periode:
    def __init__(self, id=None, nom=None, heure_debut=None, heure_fin=None, rendement_panneau=None):
        self.id = id
        self.nom = nom
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin
        self.rendement_panneau = rendement_panneau

    @staticmethod
    def get_all():
        db = DatabaseManager()
        query = "SELECT id, nom, heure_debut, heure_fin, rendement_panneau FROM periode ORDER BY nom"
        results = db.execute_query(query)
        periodes = []
        if results:
            for row in results:
                periode = Periode(
                    id=row[0], 
                    nom=row[1], 
                    heure_debut=str(row[2]) if row[2] else None,
                    heure_fin=str(row[3]) if row[3] else None,
                    rendement_panneau=row[4]
                )
                periodes.append(periode)
        return periodes

    @staticmethod
    def get_by_id(id):
        db = DatabaseManager()
        query = "SELECT id, nom, heure_debut, heure_fin, rendement_panneau FROM periode WHERE id = ?"
        results = db.execute_query(query, [id])
        if results:
            row = results[0]
            return Periode(
                id=row[0], 
                nom=row[1], 
                heure_debut=str(row[2]) if row[2] else None,
                heure_fin=str(row[3]) if row[3] else None,
                rendement_panneau=row[4]
            )
        return None

    @staticmethod
    def create(nom, heure_debut, heure_fin, rendement_panneau):
        db = DatabaseManager()
        query = """INSERT INTO periode (nom, heure_debut, heure_fin, rendement_panneau) 
                   VALUES (?, ?, ?, ?)"""
        return db.execute_update(query, [nom, heure_debut, heure_fin, rendement_panneau])

    @staticmethod
    def update(id, nom, heure_debut, heure_fin, rendement_panneau):
        db = DatabaseManager()
        query = """UPDATE periode SET nom = ?, heure_debut = ?, heure_fin = ?, rendement_panneau = ? 
                   WHERE id = ?"""
        return db.execute_update(query, [nom, heure_debut, heure_fin, rendement_panneau, id])

    @staticmethod
    def delete(id):
        db = DatabaseManager()
        query = "DELETE FROM periode WHERE id = ?"
        return db.execute_update(query, [id])

    def __str__(self):
        return f"Periode(id={self.id}, nom={self.nom}, {self.heure_debut}-{self.heure_fin}, rendement={self.rendement_panneau})"

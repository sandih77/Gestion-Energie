from database.DatabaseManager import DatabaseManager

class Utilisation:
    def __init__(self, id=None, appareil_id=None, periode_id=None, heure_debut=None, 
                 heure_fin=None, duree_heures=None):
        self.id = id
        self.appareil_id = appareil_id
        self.periode_id = periode_id
        self.heure_debut = heure_debut
        self.heure_fin = heure_fin
        self.duree_heures = duree_heures

    @staticmethod
    def get_all():
        db = DatabaseManager()
        query = """SELECT id, appareil_id, periode_id, heure_debut, heure_fin, duree_heures 
                   FROM utilisation ORDER BY appareil_id, periode_id"""
        results = db.execute_query(query)
        utilisations = []
        if results:
            for row in results:
                util = Utilisation(
                    id=row[0], 
                    appareil_id=row[1], 
                    periode_id=row[2],
                    heure_debut=str(row[3]) if row[3] else None,
                    heure_fin=str(row[4]) if row[4] else None,
                    duree_heures=row[5]
                )
                utilisations.append(util)
        return utilisations

    @staticmethod
    def get_by_id(id):
        db = DatabaseManager()
        query = """SELECT id, appareil_id, periode_id, heure_debut, heure_fin, duree_heures 
                   FROM utilisation WHERE id = ?"""
        results = db.execute_query(query, [id])
        if results:
            row = results[0]
            return Utilisation(
                id=row[0], 
                appareil_id=row[1], 
                periode_id=row[2],
                heure_debut=str(row[3]) if row[3] else None,
                heure_fin=str(row[4]) if row[4] else None,
                duree_heures=row[5]
            )
        return None

    @staticmethod
    def get_by_appareil(appareil_id):
        db = DatabaseManager()
        query = """SELECT id, appareil_id, periode_id, heure_debut, heure_fin, duree_heures 
                   FROM utilisation WHERE appareil_id = ?"""
        results = db.execute_query(query, [appareil_id])
        utilisations = []
        if results:
            for row in results:
                util = Utilisation(
                    id=row[0], 
                    appareil_id=row[1], 
                    periode_id=row[2],
                    heure_debut=str(row[3]) if row[3] else None,
                    heure_fin=str(row[4]) if row[4] else None,
                    duree_heures=row[5]
                )
                utilisations.append(util)
        return utilisations

    @staticmethod
    def create(appareil_id, periode_id, heure_debut, heure_fin, duree_heures):
        db = DatabaseManager()
        query = """INSERT INTO utilisation (appareil_id, periode_id, heure_debut, heure_fin, duree_heures) 
                   VALUES (?, ?, ?, ?, ?)"""
        return db.execute_update(query, [appareil_id, periode_id, heure_debut, heure_fin, duree_heures])

    @staticmethod
    def update(id, appareil_id, periode_id, heure_debut, heure_fin, duree_heures):
        db = DatabaseManager()
        query = """UPDATE utilisation SET appareil_id = ?, periode_id = ?, heure_debut = ?, 
                   heure_fin = ?, duree_heures = ? WHERE id = ?"""
        return db.execute_update(query, [appareil_id, periode_id, heure_debut, heure_fin, duree_heures, id])

    @staticmethod
    def delete(id):
        db = DatabaseManager()
        query = "DELETE FROM utilisation WHERE id = ?"
        return db.execute_update(query, [id])

    def __str__(self):
        return f"Utilisation(id={self.id}, appareil_id={self.appareil_id}, periode_id={self.periode_id}, {self.heure_debut}-{self.heure_fin})"

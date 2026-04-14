from database.DatabaseManager import DatabaseManager

class Appareil:
    def __init__(self, id=None, nom=None, puissance_w=None):
        self.id = id
        self.nom = nom
        self.puissance_w = puissance_w

    @staticmethod
    def get_all():
        db = DatabaseManager()
        query = "SELECT id, nom, puissance_w FROM appareil ORDER BY nom"
        results = db.execute_query(query)
        appareils = []
        if results:
            for row in results:
                app = Appareil(id=row[0], nom=row[1], puissance_w=row[2])
                appareils.append(app)
        return appareils

    @staticmethod
    def get_by_id(id):
        db = DatabaseManager()
        query = "SELECT id, nom, puissance_w FROM appareil WHERE id = ?"
        results = db.execute_query(query, [id])
        if results:
            row = results[0]
            return Appareil(id=row[0], nom=row[1], puissance_w=row[2])
        return None

    @staticmethod
    def create(nom, puissance_w):
        db = DatabaseManager()
        query = "INSERT INTO appareil (nom, puissance_w) VALUES (?, ?)"
        return db.execute_update(query, [nom, puissance_w])

    @staticmethod
    def update(id, nom, puissance_w):
        db = DatabaseManager()
        query = "UPDATE appareil SET nom = ?, puissance_w = ? WHERE id = ?"
        return db.execute_update(query, [nom, puissance_w, id])

    @staticmethod
    def delete(id):
        db = DatabaseManager()
        query = "DELETE FROM appareil WHERE id = ?"
        return db.execute_update(query, [id])

    def __str__(self):
        return f"Appareil(id={self.id}, nom={self.nom}, puissance_w={self.puissance_w}W)"
        

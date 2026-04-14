from database.DatabaseManager import DatabaseManager

class Materiel:
    def get_all_materiel():
        db = DatabaseManager()
        connexion = db.get_connection()
        curseur = connexion.cursor()
        curseur.execute("SELECT * FROM configuration")
        data = curseur.fetchall()
        return data
        

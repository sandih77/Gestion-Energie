import pyodbc

class DatabaseManager:
    def __init__(self):
        self.driver = "{ODBC Driver 18 for SQL Server}"
        self.server = "localhost"
        self.database = "gestion_energie"
        self.uid = "SA"
        self.pwd = "Sqlserver123!"
        
        self.conn_str = (
            f"DRIVER={self.driver};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.uid};"
            f"PWD={self.pwd};"
            "TrustServerCertificate=yes;"
        )

    def get_connection(self):
        try:
            conn = pyodbc.connect(self.conn_str)
            return conn
        except pyodbc.Error as e:
            print(f"Erreur de connexion : {e}")
            return None

    def execute_query(self, query, params=None):
        try:
            conn = self.get_connection()
            if conn is None:
                return None
            curseur = conn.cursor()
            if params:
                curseur.execute(query, params)
            else:
                curseur.execute(query)
            results = curseur.fetchall()
            conn.close()
            return results
        except pyodbc.Error as e:
            print(f"Erreur lors de l'exécution : {e}")
            return None

    def execute_update(self, query, params=None):
        try:
            conn = self.get_connection()
            if conn is None:
                return False
            curseur = conn.cursor()
            if params:
                curseur.execute(query, params)
            else:
                curseur.execute(query)
            conn.commit()
            conn.close()
            return True
        except pyodbc.Error as e:
            print(f"Erreur lors de la mise à jour : {e}")
            return False
import pyodbc

class DatabaseManager:
    def __init__(self):
        self.driver = "{ODBC Driver 18 for SQL Server}"
        self.server = "localhost"
        self.database = "akoho"
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
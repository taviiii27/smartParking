import mysql.connector

class Database():
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def conexiune(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.connection.cursor()

    def executeConection(self, query, values=None):
        self.conexiune()
        try:
            if values:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Eroare: {err}")
            self.connection.rollback()
        finally:
            self.close()

    def resultConection(self, query, values=None):
        self.conexiune()
        try:
            if values:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)
            rezultatInregistrare = self.cursor.fetchall()
            return rezultatInregistrare
        finally:
            self.close()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

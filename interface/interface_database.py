# Functionally empty for now until I get my raspberry pi setup with mariadb
# TODO: Write interface
# TODO: As interface is implemented, write specialized getters and setters for common operations
import mysql.connector
from mysql.connector import Error

class IF_Database:
    def __init__(self, host, user, password, database):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor(dictionary=True)
            return "[DB] Connected to MariaDB." 
        except Error as e:
            return f"[DB] Error connecting to MariaDB: {e}" 

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("[DB] Disconnected from MariaDB.")

    def query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            print("[DB] Query executed successfully.")
        except Error as e:
            print(f"[DB] Error executing query: {e}")
            self.connection.rollback()

    def fetch(self, query, params=None, all=False):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall() if all else self.cursor.fetchone()
        except Error as e:
            print(f"[DB] Error fetching data: {e}")
            return [] if all else None

    def __del__(self):
        self.disconnect()

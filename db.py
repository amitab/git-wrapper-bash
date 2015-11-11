import sqlite3
import os

class DB:
    def __init__(self, db_file_path):
        self.db_file_path = db_file_path
        self.is_new = False
        
        if not os.path.isfile(self.db_file_path):
            self.is_new = True
        
        self.conn = sqlite3.connect(self.db_file_path)
        
        self.queries = {
            'branch': {
                'create': '''CREATE TABLE IF NOT EXISTS branch (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    NAME CHAR(50),
                    LAST_REMOTE_COMMIT CHAR(50),
                    TYPE CHAR(10),
                    UNIQUE(NAME)
                );''',
                'insert': 'INSERT OR IGNORE INTO branch (NAME, LAST_REMOTE_COMMIT, TYPE) VALUES(?, ?, ?)',
                'delete': 'DELETE FROM branch WHERE NAME = ? AND TYPE = ?',
                'fetch': 'SELECT * FROM branch WHERE NAME = ?'
            }
        }
        
        self.execute_query('branch', 'create')
    
    def execute_query(self, table, type, data = None):
        if data:
            cursor = self.conn.execute(self.queries[table][type], data)
        else:
            cursor = self.conn.execute(self.queries[table][type])
        self.conn.commit()
        return cursor
    
    def insert(self, table, data):
        return self.execute_query(table, 'insert', data = data)
    
    def delete(self, table, data):
        self.execute_query(table, 'delete', data = data)
    
    def fetch(self, table, data):
        return self.execute_query(table, 'fetch', data = data)
        
    def fetchone(self, table, data):
        return self.fetch(table, data).fetchone()
        
    def clean(self):
        self.conn.close()
        os.remove(self.db_file_path)
import sqlite3
from .exceptions import *


class Cache:
    db: sqlite3.Connection = None
    cursor: sqlite3.Cursor = None
    enable: bool = True

    def __init__(self):
        pass

    def connect(self, databaseName: str = "Dingraia_cache.db", **kwargs):
        self.db = sqlite3.connect(databaseName, **kwargs)
        self.cursor = self.db.cursor()
        self.init_tables()
        
    def change_database(self, databaseName):
        self.close()
        self.enable = True
        self.connect(databaseName=databaseName)
        
    def execute(self, command, result=False):
        if self.enable:
            self.cursor.execute(command)
            if result:
                return self.cursor.fetchall()
        else:
            return ()
        
    def get_tables(self):
        res = self.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';", True)
        return [x[0] for x in res]
    
    def get_table(self, table):
        return self.execute(f"SELECT * FROM {table};", True)
    
    def create_table(self, table_name, keys):
        if self.enable:
            def type_transformer(typ: type):
                if typ == str:
                    return "TEXT"
                elif typ == int:
                    return "BIGINT"
                return typ
            if keys:
                if isinstance(keys, list):
                    if isinstance(keys[0], list) and len(keys[0]) == 2:
                        n_keys = {}
                        for i in keys:
                            n_keys[i[0]] = i[1]
                        keys = n_keys
                elif isinstance(keys, dict):
                    pass
                else:
                    return ValueError("Keys can only be list or dict, but %s given" % type(keys).__name__)
                types = []
                for k, v in keys.items():
                    types += [f"{k} {type_transformer(v)} not null"]
                types = ', '.join(types)
                self.execute(f"CREATE TABLE {table_name}({types});")
                self.commit()
            else:
                raise ValueError("Keys is empty!")
    
    def drop_table(self, table):
        self.execute(f"DROP TABLE {table};")
        self.commit()
        
    def rename_table(self, table, new_name):
        self.execute(f"ALTER TABLE {table} RENAME TO {new_name};")
        self.commit()
        
    def add_column(self, table, key, typ):
        self.execute(f"ALTER TABLE {table} ADD COLUMN {key} {typ};")
        self.commit()
    
    def init_tables(self):
        to_tables = {
            "webhooks": {
                "id": str,
                "url": str
            },
            "group_info": {
                "chatId"            : str,
                "openConversationId": str,
                "info"              : str
            },
            "counts": {
                "type": str,
                "count": int
            }
        }
        tables = self.get_tables()
        for t, v in to_tables.items():
            if t not in tables:
                self.create_table(t, v)
    
    def key_exists(self, table, column, name) -> bool:
        return bool(self.execute(f"SELECT * FROM `{table}` WHERE {column}='{name}'", result=True))
    
    def add_value(self, table, column, name, index, add: int = 1):
        if self.key_exists(table, column, name):
            self.execute(f"UPDATE `{table}` SET {name}={name}+{add} WHERE {index}='openApi';")
            self.commit()
        else:
            raise SQLError(f"Index '{index}' does not found in the table '{table}'")
    
    def add_openapi_count(self, times: int = 1):
        if self.key_exists('counts', 'type', 'openApi'):
            self.execute(f"UPDATE `counts` SET count=count+{times} WHERE type='openApi';")
        else:
            self.execute(f"INSERT INTO `counts` (type, count) VALUES ('openApi', {times});")
        self.commit()
    
    def get_api_counts(self):
        res = self.execute("SELECT * FROM `counts` WHERE type='openApi'", result=True)
        if res:
            return res[0][1]
        return 0
                
    def commit(self):
        if self.enable:
            self.db.commit()

    def close(self):
        self.cursor.close()
        self.db.close()
        
        
cache = Cache()
cache.connect(check_same_thread=False)

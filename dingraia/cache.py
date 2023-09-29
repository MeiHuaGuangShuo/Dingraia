import sqlite3


class Cache:
    db: sqlite3.Connection = None
    cursor: sqlite3.Cursor = None

    def __init__(self):
        pass

    @classmethod
    def connect(cls, databaseName: str = "Dingraia_cache.db"):
        cls.db = sqlite3.connect(databaseName)
        cls.cursor = cls.db.cursor()
        
    @classmethod
    def execute(cls, command, result=False):
        cls.cursor.execute(command)
        if result:
            return cls.cursor.fetchall()
        
    @classmethod
    def get_tables(cls):
        res = cls.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';", True)
        return [x[0] for x in res]
    
    @classmethod
    def get_table(cls, table):
        return cls.execute(f"SELECT * FROM {table};", True)
    
    @classmethod
    def create_table(cls, table_name, keys):
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
            cls.execute(f"CREATE TABLE {table_name}({types});")
            cls.db.commit()
        else:
            raise ValueError("Keys is empty!")
    
    @classmethod
    def drop_table(cls, table):
        cls.execute(f"DROP TABLE {table};")
        cls.db.commit()
        
    @classmethod
    def rename_table(cls, table, new_name):
        cls.execute(f"ALTER TABLE {table} RENAME TO {new_name};")
        cls.db.commit()
        
    @classmethod
    def add_column(cls, table, key, typ):
        cls.execute(f"ALTER TABLE {table} ADD COLUMN {key} {typ};")
        cls.db.commit()
    
    @classmethod
    def init_tables(cls):
        to_tables = {
            "webhooks": {
                "id": str,
                "url": str
            },
            "group_info": {
                "chatId"            : str,
                "openConversationId": str,
                "info"              : str
            }
        }
        tables = cls.get_tables()
        for t, v in to_tables.items():
            if t not in tables:
                cls.create_table(t, v)

    @classmethod
    def close(cls):
        cls.cursor.close()
        cls.db.close()

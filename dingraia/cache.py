import sqlite3
import datetime
from .exceptions import *
from typing import Optional, Union
from pathlib import Path


class Cache:
    db: Optional[sqlite3.Connection] = None
    db_name: Optional[str] = None
    cursor: Optional[sqlite3.Cursor] = None
    enable: bool = True

    def __init__(self):
        pass

    def connect(self, databaseName: str = "Dingraia_cache.db", **kwargs):
        self.db_name = databaseName
        self.db = sqlite3.connect(databaseName, **kwargs)
        self.cursor = self.db.cursor()
        self.init_tables()

    def change_database(self, databaseName):
        self.close()
        self.enable = True
        self.connect(databaseName=databaseName)

    def execute(self, command: str, params=tuple(), *, result: bool = False):
        if self.enable:
            self.cursor.execute(command, params)
            if result:
                return self.cursor.fetchall()
        else:
            return ()

    def get_tables(self):
        res = self.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';",
                           result=True)
        return [x[0] for x in res]

    def get_table(self, table):
        return self.execute(f"SELECT * FROM {table};", result=True)

    def create_table(self, table_name, keys):
        if self.enable:
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
                    types += [f"{k} {self._type_transformer(v)} not null"]
                types = ', '.join(types)
                self.execute(f"CREATE TABLE {table_name}({types});")
                self.commit()
            else:
                raise ValueError("Keys is empty!")

    @staticmethod
    def _type_transformer(typ: Union[type, str]):
        if typ == str:
            return "TEXT"
        elif typ == int:
            return "BIGINT"
        return typ

    def drop_table(self, table):
        self.execute(f"DROP TABLE {table};")
        self.commit()

    def rename_table(self, table, new_name):
        self.execute(f"ALTER TABLE {table} RENAME TO {new_name};")
        self.commit()

    def add_column(self, table, key, typ):
        self.execute(f"ALTER TABLE {table} ADD COLUMN {key} {typ};")
        self.commit()

    def get_table_columns(self, table_name):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns = self.cursor.fetchall()
        column_dict = {col[1]: col[2] for col in columns}
        return column_dict

    def init_tables(self):
        to_tables = {
            "webhooks"  : {
                "id"                : int,
                "openConversationId": str,
                "url"               : str,
                "expired"           : int,
                "timeStamp"         : int,
            },
            "group_info": {
                "id"       : int,
                "chatId"   : str,
                "openConversationId": str,
                "name"     : str,
                "info"     : str,
                "timeStamp": int,
            },
            "user_info" : {
                "id"     : int,
                "name"     : str,
                "staffId"  : str,
                "unionId": str,
                "info"     : str,
                "timeStamp": int,
            },
            "counts"    : {
                "type": str,
                "count": int
            }
        }
        for k, v in to_tables.items():
            for k2, v2 in v.items():
                to_tables[k][k2] = self._type_transformer(v2)
        tables = self.get_tables()
        for t, v in to_tables.items():
            if t in tables:
                # 获取表的列信息
                table_columns = self.get_table_columns(t)
                if not self.columns_match(table_columns, v):
                    print('Database restore: ', table_columns, '<->', v)
                    self.backup_database()
                    self.drop_table(t)
                    self.create_table(t, v)
            else:
                self.create_table(t, v)

    @staticmethod
    def columns_match(table_columns, expected_columns):
        # 检查表中的列是否与预期的列匹配
        for col, col_type in expected_columns.items():
            if col not in table_columns or table_columns[col] != col_type:
                return False
        return True

    def value_exist(self, table, column, value) -> bool:
        return bool(self.execute(f"SELECT * FROM `{table}` WHERE {column}=?", (value,), result=True))
    
    def add_value(self, table, column, name, index, add: int = 1):
        if self.value_exist(table, column, name):
            self.execute(f"UPDATE `{table}` SET {name}={name}+{add} WHERE {index}='openApi';")
            self.commit()
        else:
            raise SQLError(f"Index '{index}' does not found in the table '{table}'")

    def add_openapi_count(self, times: int = 1):
        current_month = datetime.datetime.now().strftime('openApi_%Y_%m')
        if self.value_exist('counts', 'type', current_month):
            self.execute(f"UPDATE `counts` SET count=count+{times} WHERE type='{current_month}';")
        else:
            self.execute(f"INSERT INTO `counts` (type, count) VALUES ('{current_month}', {times});")
        self.commit()

    def get_api_counts(self):
        current_month = datetime.datetime.now().strftime('openApi_%Y_%m')
        res = self.execute(f"SELECT * FROM `counts` WHERE type='{current_month}'", result=True)
        if res:
            return res[0][1]
        return 0

    def commit(self):
        if self.enable:
            self.db.commit()

    def is_connected(self) -> bool:
        return self.db is not None and self.cursor is not None

    def backup_database(self):
        if self.is_connected():
            backup_file = Path(self.db_name).stem + datetime.datetime.now().strftime('_%Y_%m_%d_%H_%M_%S') + '.db'
            backup_conn = sqlite3.connect(backup_file)
            with backup_conn:
                self.db.backup(backup_conn)
        else:
            raise SQLError("Database is not connected!")

    def close(self):
        self.cursor.close()
        self.db.close()
        self.db = None
        self.db_name = None
        self.cursor = None


cache = Cache()
cache.connect(check_same_thread=False)

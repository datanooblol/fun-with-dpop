from package.ezorm.utils import remove_escape_characters
from package.ezorm.utils import create_directory
from typing import List, Type, get_args
from package.ezorm.variables import EzORM
from package.ezorm.validation import issubclass_ezorm
from package.ezorm.configuration import settings
import os

def create_tbl_query(table:Type[EzORM])->str:
    issubclass_ezorm(table)
    data_types = {
        str: "TEXT",    # or "TEXT" for unlimited length
        int: "INTEGER",
        float: "FLOAT",    # or "REAL" depending on the database
        bool: "BOOLEAN",
        # "datetime": "DATETIME"  # Use "TIMESTAMP" for PostgreSQL
    }

    query = []

    for field, detail in table.model_fields.items():
        if field != 'table_name':
            proxy = []
            
            is_optional = 'Optional' in str(detail.annotation)
            if is_optional:
                dtype, _ = get_args(detail.annotation)
            else:
                dtype = detail.annotation

            proxy.append(f"""{field} {data_types[dtype]}""")
            is_required = not is_optional
            
            if is_required:
                proxy.append(f"""NOT NULL""")
            else:
                default = detail.default
                if (default is not None) and (default != ""):
                    if isinstance(detail.default, bool):
                        proxy.append(f"""DEFAULT {str(default).upper()}""")
                    elif isinstance(detail.default, str):
                        proxy.append(f"""DEFAULT '{default}'""")
                    else:
                        proxy.append(f"""DEFAULT {default}""")
                        
            query.append(" ".join(proxy))

    query = ", ".join(query)
    query = remove_escape_characters(query).strip()

    QUERY = f"""CREATE TABLE IF NOT EXISTS {table.__table__} ( {query} );"""
    return QUERY

def delete_tbl_query(table:Type[EzORM])->str:
    issubclass_ezorm(table)
    QUERY = f"""DROP TABLE IF EXISTS {table.__table__};"""
    return QUERY

def create_tables(tables:List[EzORM]):
    create_directory(db_path=settings.database)
    for table in tables:
        query = create_tbl_query(table)
        settings.engine(query, [])
        print(f"Model: {table.__table__} created successfully")
    print("All tables created successfully")

def delete_tables(tables:List[EzORM]):
    for table in tables:
        query = delete_tbl_query(table)
        settings.engine(query, [])
        print(f"Model: {table.__table__} deleted successfully")
    print("All tables deleted successfully")

def delete_database():
    if os.path.exists(settings.database):
        os.remove(settings.database)

def list_table():
    query = """SHOW TABLES;"""
    return settings.engine(query, [])
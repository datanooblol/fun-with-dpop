import duckdb
from contextlib import contextmanager
import re
# Context Manager for DuckDB Connection
@contextmanager
def duck_connection(database:str):
    """A context manager to manage DuckDB connections."""
    # Establish the connection
    conn = duckdb.connect(database=database)
    try:
        yield conn  # Yield the connection for usage
    finally:
        conn.close()  # Ensure the connection is closed after use

def remove_escape_characters(text:str)->str:
    pattern = r"[;]"
    return re.sub(pattern, "", text)
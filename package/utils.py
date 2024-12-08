from typing import Generator

import duckdb

from package.ezorm.ezcrud import EzCrud


def hello_package():
    return "hello from package"

def get_db() -> Generator:
    return EzCrud(engine=duckdb, database="./db/test.db")
from package.ezorm import EzORM
from typing import Type, Any

def isinstance_ezorm(any:Type[Any]):
    if not issubclass(any, EzORM):
        raise ValueError(f"Expected a subclass of EzORM, but got {type(any)}")
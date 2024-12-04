from pydantic import BaseModel

class EzORM(BaseModel):
    __table__:str = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Set the table name to the lowercase name of the class
        cls.__table__ = cls.__name__.lower()

    @classmethod
    def __getattr__(cls, item):
        if item in cls.__annotations__:
            return item
        raise AttributeError(f"'{cls.__name__}' has no attribute '{item}'")
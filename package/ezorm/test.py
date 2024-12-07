from pydantic import BaseModel
from pydantic._internal._model_construction import ModelMetaclass as ModelMetaclass
class EzORMMeta(ModelMetaclass):
    """This is a metaclass to create __table__ that will be used in later step
    Args:
        name (str) : the input class name
        bases (any) : abc
        dct (dict) : this is the annotation of pydantic BaseModel
        table (str) : a specified table name

    Note:
        This will be inspected and debugged later.
    """
    def __new__(cls, name:str, bases, dct:dict, table:str=None):
        new_class = super().__new__(cls, name, bases, dct)
        setattr(new_class, "__table__", table if table else name.lower())
        return new_class

class EzORM(BaseModel, metaclass=EzORMMeta):
    """This is a base class for EzORM"""
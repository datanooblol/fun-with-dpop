# from pydantic import BaseModel, Field
# from typing import Optional, Type

# class EzORMMeta(type(BaseModel)):
#     """This is a metaclass to create __table__ that will be used in later step
#     Args:
#         name (str) : the input class name
#         bases (any) : abc
#         dct (dict) : this is the annotation of pydantic BaseModel
#         table (str) : a specified table name

#     Note:
#         This will be inspected and debugged later.
#     """
#     def __new__(cls, name:str, bases, dct:dict, table:str=None):
#         new_class = super().__new__(cls, name, bases, dct)
#         setattr(new_class, "__table__", table if table else name.lower())
#         return new_class

# class EzORM(BaseModel, metaclass=EzORMMeta):
#     """This is a base class for EzORM"""

from pydantic import BaseModel

class EzORM(BaseModel):
    __table__: str = None  # Initialize as None

    @classmethod
    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.__table__ = cls.__name__.lower()  # Set __table__ dynamically to the class name

    class ConfigDict:
        # Ensure __table__ is not included in model fields
        exclude = {'__table__'}

    def __init__(self, **data):
        data.pop('__table__', None)  # Remove __table__ from the constructor arguments
        super().__init__(**data)
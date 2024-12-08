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
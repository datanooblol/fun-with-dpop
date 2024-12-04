from package.ezorm.variables import EzORM

class Table:
    def __init__(self, obj: EzORM):
        self.obj = obj

    def __getattr__(self, item: str):
        """Allow dynamic access to the field names."""
        fields = self.obj.model_fields
        if item in fields:
            return item
        raise AttributeError(f"'{self.obj.__name__}' has no field '{item}'")
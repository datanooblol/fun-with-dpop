from sqlmodel import SQLModel, Field, Session, create_engine
from typing import Optional, Callable, Any
from functools import wraps

# Define your database URL
DATABASE_URL = "sqlite:///db/dev.db"  # Adjust according to your database

# Define the decorator to handle the connection
def with_connection(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator that manages database connections for SQLModel queries.

    Args:
        func (Callable): A function that performs database operations and accepts a Session.

    Returns:
        Callable: The wrapped function with connection handling.
    """
    @wraps(func)  # Apply wraps to preserve the original function signature
    def wrapper(*args, **kwargs) -> Any:
        engine = create_engine(DATABASE_URL)
        try:
            with Session(engine) as session:
                # Pass the session to the decorated function
                return func(session, *args, **kwargs)
        finally:
            # Dispose of the engine to release the database file
            engine.dispose()
    return wrapper  # Return the wrapped function
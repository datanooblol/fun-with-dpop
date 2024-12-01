# File: dpop_proof_jti.py

from package.data_models.utils import with_connection
from sqlmodel import SQLModel, Field, Session, select

class DpopProofJTI(SQLModel, table=True):
    jti: str = Field(primary_key=True)
    __table_args__ = {'extend_existing': True}

    @classmethod
    def create(cls, jti: str):
        """
        Creates a new DpopProofJTI record.
        """
        @with_connection
        def create_in_db(session: Session):
            dpop_proof = cls(jti=jti)
            session.add(dpop_proof)
            session.commit()
            session.refresh(dpop_proof)
            return dpop_proof
        
        return create_in_db()

    @classmethod
    def get_by_jti(cls, jti: str):
        """
        Retrieves a DpopProofJTI record by jti.
        """
        @with_connection
        def get_from_db(session: Session):
            # Use session.exec() instead of session.query()
            statement = select(cls).filter(cls.jti == jti)
            result = session.exec(statement).first()
            return result

        return get_from_db()

    @classmethod
    def delete(cls, jti: str):
        """
        Deletes a DpopProofJTI record by jti.
        """
        @with_connection
        def delete_from_db(session: Session):
            dpop_proof = cls.get_by_jti(jti)
            if dpop_proof:
                session.delete(dpop_proof)
                session.commit()
                return True
            return False

        return delete_from_db()

    @classmethod
    def update(cls, jti: str, **kwargs):
        """
        Update any attributes of DpopProofJTI dynamically.
        Pass the attributes as keyword arguments.
        """
        @with_connection
        def update_in_db(session: Session):
            dpop_proof = cls.get_by_jti(jti)
            if dpop_proof:
                for key, value in kwargs.items():
                    if hasattr(dpop_proof, key):
                        setattr(dpop_proof, key, value)
                session.commit()
                session.refresh(dpop_proof)
                return dpop_proof
            return None

        return update_in_db()
# File: access_token_jti.py

from sqlmodel import SQLModel, Field, Session
from typing import Optional

class AccessTokenJTI(SQLModel, table=True):
    jti: str = Field(primary_key=True)
    token: str
    client_id: str
    exp: int
    active: bool
    remark: Optional[str] = None
    __table_args__ = {'extend_existing': True}

    @classmethod
    def create(cls, session: Session, jti: str, token: str, client_id: str, exp: int, active: bool, remark: Optional[str] = None):
        access_token = cls(jti=jti, token=token, client_id=client_id, exp=exp, active=active, remark=remark)
        session.add(access_token)
        session.commit()
        session.refresh(access_token)
        return access_token

    @classmethod
    def get_by_jti(cls, session: Session, jti: str):
        return session.query(cls).filter(cls.jti == jti).first()

    @classmethod
    def update(cls, session: Session, jti: str, token: Optional[str] = None, client_id: Optional[str] = None, 
               exp: Optional[int] = None, active: Optional[bool] = None, remark: Optional[str] = None):
        access_token = cls.get_by_jti(session, jti)
        if access_token:
            if token:
                access_token.token = token
            if client_id:
                access_token.client_id = client_id
            if exp:
                access_token.exp = exp
            if active is not None:
                access_token.active = active
            if remark is not None:
                access_token.remark = remark
            session.commit()
            session.refresh(access_token)
            return access_token
        return None

    @classmethod
    def delete(cls, session: Session, jti: str):
        access_token = cls.get_by_jti(session, jti)
        if access_token:
            session.delete(access_token)
            session.commit()
            return True
        return False

    @classmethod
    def update_multiple(cls, session: Session, client_id: str, active: bool):
        """
        Update multiple records in the table where client_id matches the provided value.
        """
        updated_count = session.query(cls).filter(cls.client_id == client_id).update({cls.active: active})
        session.commit()
        return updated_count

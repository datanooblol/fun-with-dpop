# File: refresh_token_jti.py

from sqlmodel import SQLModel, Field, Session
from typing import Optional

class RefreshTokenJTI(SQLModel, table=True):
    jti: str = Field(primary_key=True)
    token: str
    client_id: str
    exp: int
    active: bool
    remark: Optional[str] = None
    __table_args__ = {'extend_existing': True}

    @classmethod
    def create(cls, session: Session, jti: str, token: str, client_id: str, exp: int, active: bool, remark: Optional[str] = None):
        refresh_token = cls(jti=jti, token=token, client_id=client_id, exp=exp, active=active, remark=remark)
        session.add(refresh_token)
        session.commit()
        session.refresh(refresh_token)
        return refresh_token

    @classmethod
    def get_by_jti(cls, session: Session, jti: str):
        return session.query(cls).filter(cls.jti == jti).first()

    @classmethod
    def update(cls, session: Session, jti: str, token: Optional[str] = None, client_id: Optional[str] = None, 
               exp: Optional[int] = None, active: Optional[bool] = None, remark: Optional[str] = None):
        refresh_token = cls.get_by_jti(session, jti)
        if refresh_token:
            if token:
                refresh_token.token = token
            if client_id:
                refresh_token.client_id = client_id
            if exp:
                refresh_token.exp = exp
            if active is not None:
                refresh_token.active = active
            if remark is not None:
                refresh_token.remark = remark
            session.commit()
            session.refresh(refresh_token)
            return refresh_token
        return None

    @classmethod
    def delete(cls, session: Session, jti: str):
        refresh_token = cls.get_by_jti(session, jti)
        if refresh_token:
            session.delete(refresh_token)
            session.commit()
            return True
        return False

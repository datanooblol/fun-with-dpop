from fastapi import Depends, FastAPI
from package.routes import AuthorizerRouter, ResourceRouter
from package.ezorm.configuration import settings
from package.ezorm.engine import duck_engine
from package.database_management.data_models import CodeModel, DPoPModel, AccessTokenModel, RefreshTokenModel, UserModel
from package.ezorm.db_management import create_tables, delete_tables
from pydantic import BaseModel
import duckdb
from package.ezorm.ezcrud import EzCrud
from package.utils import get_db

settings.configure(engine=duck_engine)
tables = [DPoPModel, AccessTokenModel, RefreshTokenModel, UserModel, CodeModel]
delete_tables(tables)
create_tables(tables)

with settings.context(database='./db/test.db'):
    print(settings)
    delete_tables(tables)
    create_tables(tables)
    EzCrud(
        engine=duckdb, database=settings.database
    ).Create(UserModel(client_id="testclientid", username="testusername", password="testpassword"))

app = FastAPI()

# Include the routers
app.include_router(AuthorizerRouter)
app.include_router(ResourceRouter)

@app.get("/health")
async def get_root():
    return {"response": "Alive!"}

class Health(BaseModel):
    user:str

@app.post("/health/")
async def post_root(user:Health):
    return {"response": f"Hey {user.user} I'm Alive!"}

@app.get("/db")
async def read_db(db:EzCrud = Depends(get_db)):
    record = db.Read(UserModel())
    print(record)
    return {"response": "db"}

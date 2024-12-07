from fastapi import FastAPI
from package.routes import AuthorizerRouter, ResourceRouter
from package.ezorm.configuration import settings
from package.ezorm.engine import duck_engine
from package.database_management.data_models import CodeModel, DPoPModel, AccessTokenModel, RefreshTokenModel, UserModel
from package.ezorm.db_management import create_tables, delete_tables
from pydantic import BaseModel

settings.configure(engine=duck_engine)
tables = [DPoPModel, AccessTokenModel, RefreshTokenModel, UserModel, CodeModel]
delete_tables(tables)
create_tables(tables)

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
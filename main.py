from fastapi import FastAPI, Request
from package.routes import AuthorizerRouter, ResourceRouter

app = FastAPI()

# Include the routers
app.include_router(AuthorizerRouter)
app.include_router(ResourceRouter)

@app.get("/health")
async def root():
    return {"response": "Alive!"}
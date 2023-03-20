from src.auth.router import auth_router # app depend
from os import environ
from fastapi import FastAPI, APIRouter
import uvicorn
app = FastAPI()

# { Your app routers
app.include_router(auth_router)
# }


api_router = APIRouter(prefix='/api')
app.include_router(api_router)
if __name__ == "__main__":
    host = environ.get('TEST_HOST')
    port = environ.get('TEST_PORT')
    uvicorn.run(app, host=host, port=port)

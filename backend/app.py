from dotenv import load_dotenv
from fastapi import FastAPI

from backend.routes.chat import router

load_dotenv()
app = FastAPI()

app.include_router(router)

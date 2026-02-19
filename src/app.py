from typing import List, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from routes import general_routes, users_routes
from database import engine, Base
from models import users_model

# database setup
# Base.metadata.create_all(bind=engine)

# app setup
app = FastAPI(title="sql alchemy")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(general_routes.general_router)
app.include_router(users_routes.users_router)

if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import Base, engine


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def get_root():
    return {"Hello World ! "}
    
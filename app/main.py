import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import Base, engine
from .routers import jobs, employers, auth, candidates
import time


app = FastAPI()

origins = ["https://talenthire-b9q0.onrender.com", 
        "http://localhost:8000"]

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(jobs.router)
app.include_router(employers.router)
app.include_router(auth.router)
app.include_router(candidates.router)


@app.on_event("startup")
def startup():
    #Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

@app.get("/")
def get_root():
    return {"Hello World ! "}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

@app.on_event("shutdown")
def shutdown():
    logger.info("Shutting down.....")    
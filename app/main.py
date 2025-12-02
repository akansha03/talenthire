from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models
from .database import Base, engine
from .routers import jobs, employers, auth, candidates


app = FastAPI()

origins = ["*"]

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
    
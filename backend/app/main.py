from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .controllers import books, loans, members
from .database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(books.router)
app.include_router(members.router)
app.include_router(loans.router)

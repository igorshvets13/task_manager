from fastapi import FastAPI
from app.routers import auth, tasks
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API",
    description="REST API для управления задачами с JWT-аутентификацией",
    version="1.0.0",
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])


@app.get("/")
def root():
    return {"message": "Task Manager API работает"}

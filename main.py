from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from app.routers import quiz

app = FastAPI(
    title="Quiz Grades Processor",
    description="A web application for processing quiz grades from CSV files, with the ability to convert scores from one scale to another.",
    version="1.0.0"
)

# Include routers
app.include_router(quiz.router)

# Mount static files
os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

from fastapi import FastAPI

from src.config import config
from src.logging import init_loggers
from src.database import create_tables


init_loggers()

app = FastAPI(debug=config('DEBUG', False))


@app.on_event('startup')
async def startup_event():
    await create_tables()
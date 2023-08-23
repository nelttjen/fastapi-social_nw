from fastapi import FastAPI

from src.config import config
from src.database import create_tables
from src.logging import init_loggers

# from src.middlewares import QueryLoggingMiddleware

init_loggers()

app = FastAPI(debug=config('DEBUG', False))
# app.add_middleware(QueryLoggingMiddleware)

@app.on_event('startup')
async def startup_event():
    await create_tables()

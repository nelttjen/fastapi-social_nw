from fastapi import FastAPI

from src.config import config
from src.logging import init_loggers

init_loggers()

app = FastAPI(debug=config('DEBUG', False))

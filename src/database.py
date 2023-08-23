import logging
from typing import AsyncGenerator

from sqlalchemy.event import listens_for
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import config

DATABASE_URL = config('DB_URL')


engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
debugger = logging.getLogger('debugger')


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def create_tables() -> None:
    return
    async with engine.begin() as connection:
        from src.base.models import BaseModel
        await connection.run_sync(BaseModel.metadata.create_all)
        await connection.commit()
        debugger.debug('Tables created')

    await engine.dispose()


@listens_for(engine.sync_engine, 'before_cursor_execute', named=True)
def log_query(
        conn, cursor, statement, parameters, context, executemany,
):
    # if not hasattr(conn, 'queries'):
    #     setattr(conn, 'queries', [])
    # conn.queries.append([statement, parameters])
    debugger.debug(f'Executing query:\n{statement} with parameters: {parameters}')

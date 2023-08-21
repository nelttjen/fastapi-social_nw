from sqlalchemy.orm import (
    declarative_base, DeclarativeMeta,
)
from sqlalchemy import MetaData

base_metadata = MetaData()

BaseModel: DeclarativeMeta = declarative_base(metadata=base_metadata)


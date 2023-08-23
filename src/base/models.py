from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeMeta, declarative_base

base_metadata = MetaData()

BaseModel: DeclarativeMeta = declarative_base(metadata=base_metadata)

from sqlalchemy import Column, Integer, VARCHAR, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./hihigs.db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "user_table"
    user_id   = Column(Integer, primary_key=True)
    username  = Column(VARCHAR(255), nullable=False)
    tutorcode = Column(VARCHAR(8), unique=True, nullable=True)
    subscribe = Column(Integer, nullable=True)
    extra     = Column(Text, nullable=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

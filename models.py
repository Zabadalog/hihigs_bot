from sqlalchemy import Column, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Настройки базы данных
DATABASE_URL = "sqlite+aiosqlite:///./users.db"

engine = create_async_engine(DATABASE_URL, echo=False)
Base = declarative_base()
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Модель пользователя
class User(Base):
    __tablename__ = 'users'
    userid = Column(String, primary_key=True)
    username = Column(String)
    tutorcode = Column(String, nullable=True)
    subscribe = Column(String, nullable=True)
    extra = Column(String, nullable=True)

# Инициализация базы данных
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

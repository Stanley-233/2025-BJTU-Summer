import os

from typing import Generator

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv("config.env")
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
  """初始化数据库，创建所有表"""
  SQLModel.metadata.drop_all(engine)
  SQLModel.metadata.create_all(engine)
  print("Initialized database and created tables.")


def get_session() -> Generator[Session, None, None]:
  """获取数据库会话的依赖项"""
  with Session(engine) as session:
    yield session

from contextlib import contextmanager, AbstractContextManager
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from typing import Annotated, Generator


class Repository:
    __engine: Engine
    __session_factory: sessionmaker

    def __init__(self):
        self.__engine = create_engine(os.environ.get("DATABASE_URL"))
        with Session(self.__engine) as session:
            session.execute
        self.__session_factory = scoped_session(
            sessionmaker(bind=self.__engine),
        )

    @contextmanager
    def session(self) -> Generator[Annotated[Session, AbstractContextManager[Session]]]:
        session: AbstractContextManager[Session] = self.__session_factory()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

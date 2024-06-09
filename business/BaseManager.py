import os
from pathlib import Path

from sqlalchemy import create_engine, Select
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session, sessionmaker

from data_access.data_base import init_db


class BaseManager(object):
    def __init__(self, session):
        self._session: Session = session

    def select_all(self, query: Select):
        return self._session.execute(query).scalars().all()

    def select_one(self, query: Select):
        return self._session.execute(query).scalars().one()
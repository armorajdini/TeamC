# include all user-related functions here
# login, register, authenticate
import os

from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.scoping import scoped_session
from data_access.data_base import init_db
from data_models.models import *

from data_access.data_generator import *

from business.SearchManager import SearchManager
from business.BaseManager import BaseManager
class UserManager(BaseManager):
    def __init__(self):
        super().__init__(True)
        self._current_user = None
        self._MAX_ATTEMPTS = 3
        self._attempts_left = self._MAX_ATTEMPTS

    def login(self, username, password):
        if self._attempts_left <= 0
            print("No attempts left")
        else:
            query = select(User).where(User.username == username, User.password == password)
        self._attempts_left -= 1


    def logout(self):

    def attempts_left(self):
        return self._attempts_left


if __name__ == '__main__':
    os.environ["DB_FILE"] = "../data/test.db"
    um = UserManager()


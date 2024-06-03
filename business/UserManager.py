# include all user-related functions here
# login, register, authenticate
import os
import sys

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

    def get_current_login(self):
        return self._current_user

    def login(self, username, password):
        if self._attempts_left <= 0:
            raise RuntimeError('No attempts left')
        else:
            query = select(Login).where(Login.username == username, Login.password == password)
            result = self._session.execute(query).scalars().one_or_none()
            self._current_user = result
            self._attempts_left -= 1
        return self._current_user


    def logout(self):
        self._current_user = None
        self._attempts_left = self._MAX_ATTEMPTS

    def has_attempts_left(self):
        if self._attempts_left <= 0:
            return False
        else:
            return True

    def is_admin(self, login:Login):
        if login.role.access_level == sys.maxsize:
            return True
        else:
            return False

    def get_reg_guest_of(self, login:Login) -> RegisteredGuest:
        query = select(RegisteredGuest).where(RegisteredGuest.login == login)
        result = self._session.execute(query).scalars().one_or_none()
        return result


if __name__ == '__main__':
    os.environ["DB_FILE"] = "../data/test.db"
    um = UserManager()

    while um.has_attempts_left():
        username = input('Username: ')
        password = input('Password: ')
        if um.login(username, password) is not None:
            break
        else:
            print('Username or password wrong!')
    if um.get_current_login() is not None:
        if um.is_admin(um.get_current_login()):
            print(f"Welcome administrator {um.get_current_login().username}")
        else:
            reg_guest = um.get_reg_guest_of(um.get_current_login())
            print(f"Welcome {reg_guest.firstname} {reg_guest.lastname}!")
    else:
        print("Too many attempts, program is closed!")
        sys.exit(1)

    logout = input("Do you wish to logot? (y/n): ")
    match logout:
        case "y":
            print(f"Goodbye {um.get_current_login().username}!")
            um.logout()
        case "n":
            print(um.get_current_login())

    um_1 = UserManager()
    print(um_1.get_current_login())


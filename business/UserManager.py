import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import scoped_session, sessionmaker
from data_access.data_base import init_db
from data_models.models import *
from business.BaseManager import BaseManager

class UserManager(BaseManager):
    def __init__(self, session):
        super().__init__(session)
        self._current_user = None
        self._MAX_ATTEMPTS = 3
        self._attempts_left = self._MAX_ATTEMPTS

    def get_current_user(self):
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
        return self._attempts_left > 0

    def is_admin(self, login: Login):
        return login.role.access_level == sys.maxsize

    def get_reg_guest_of(self, login: Login) -> RegisteredGuest:
        query = select(RegisteredGuest).where(RegisteredGuest.login == login)
        result = self._session.execute(query).scalars().one_or_none()
        return result

    def login_user(self):
        while self.has_attempts_left():
            username = input('Username: ')
            password = input('Password: ')
            if self.login(username, password):
                break
            else:
                print('Username or password wrong!')
        if self.get_current_user():
            if self.is_admin(self.get_current_user()):
                print(f"Welcome administrator {self.get_current_user().username}")
            else:
                reg_guest = self.get_reg_guest_of(self.get_current_user())
                print(f"Welcome {reg_guest.firstname} {reg_guest.lastname}!")
        else:
            print("Too many attempts, program is closed!")
            sys.exit(1)

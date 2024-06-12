import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import scoped_session, sessionmaker
from data_access.data_base import init_db
from data_models.models import *
from business.BaseManager import BaseManager

# Function to display the welcome message
def show_welcome():
    print("Welcome to the Hotel Reservation System!")

# Function to display the main menu
def show_menu():
    print("\nMain Menu:")
    print("1. Register")
    print("2. Log in")
    print("3. Exit")

# Function to navigate through the menu
def navigate_menu(um):
    while True:
        show_menu()
        choice = input("Choose an option: ")
        if choice == '1':
            um.register_user()
        elif choice == '2':
            um.login_user()
            current_user = um.get_current_user()


                    # More admin functions can be called here



                        # More registered user functions can be called here
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# Definition of the UserManager class
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
                print(f"Welcome  {self.get_current_user().username}")
            else:
                reg_guest = self.get_reg_guest_of(self.get_current_user())
                print(f"Welcome {reg_guest.firstname} {reg_guest.lastname}!")
        else:
            print("Too many attempts, program is closed!")
            sys.exit(1)

    def register_user(self):
        try:
            email = input("Please enter your email address: ")
            password = input("Enter password: ")
            username = email  # Use email as username for simplicity

            # Check if the username already exists
            existing_user_query = select(Login).where(Login.username == username)
            existing_user = self._session.execute(existing_user_query).scalars().one_or_none()
            if existing_user:
                raise ValueError("Username already exists. Please choose a different email.")

            firstname = input("Please enter your first name: ")
            lastname = input("Please enter your last name: ")

            street = input("Please enter your street: ")
            zip_code = input("Please enter your zip code: ")
            city = input("Please enter your city: ")

            address = Address(street=street, zip=zip_code, city=city)
            self._session.add(address)
            self._session.commit()

            role_query = select(Role).where(Role.name == 'registered_user')
            role = self._session.execute(role_query).scalars().one_or_none()
            if not role:
                # If the role does not exist, create it
                role = Role(name='registered_user', access_level=1)
                self._session.add(role)
                self._session.commit()

            guest = RegisteredGuest(
                firstname=firstname,
                lastname=lastname,
                email=email,
                address_id=address.id,
                login=Login(username=username, password=password, role_id=role.id)
            )
            self._session.add(guest)
            self._session.commit()

            print(f"User {username} successfully registered as a registered user.")
            return guest
        except Exception as e:
            print(f"Error registering user: {e}")
            return None


if __name__ == '__main__':
    os.environ["DB_FILE"] = "../data/test.db"
    db_file = os.environ["DB_FILE"]
    db_path = Path(db_file)
    if not db_path.is_file():
        init_db(db_file, generate_example_data=True)

    engine = create_engine(f"sqlite:///{db_file}")
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    um = UserManager(session)

    show_welcome()
    navigate_menu(um)

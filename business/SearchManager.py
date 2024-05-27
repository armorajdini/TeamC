# include all search functions here
# accept search criteria, search by various criteria

from datetime import date, datetime, timedelta

from datetime import date, datetime, timedelta
from pathlib import Path

from sqlalchemy import create_engine, select, or_, and_
from sqlalchemy.orm import scoped_session, sessionmaker, session

from data_access.data_base import init_db
from data_models.models import *

class SearchManager:
    def __init__(self, database_file):
        database_path = Path(database_file)
        if not database_path.is_file():
            init_db(database_file, generate_example_data=True)
        self.__engine = create_engine(f'sqlite:///{database_path}', echo=False)
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    def get_available_hotels(self, start_date: date, end_date: date):
        query_booked_rooms = select(Room.number).join(Booking).where(
            Booking.start_date.between(start_date, end_date) | Booking.end_date.between(start_date, end_date)
        )
        query_available_hotels = select(Hotel).group_by(Hotel.id).join(Room).where(
            Room.number.not_in(query_booked_rooms))
        return self.__session.execute(query_available_hotels).scalars().all()

    def get_available_hotels_by_city(self, start_date: date, end_date: date, city : str):
        query_booked_rooms = select(Room.number).join(Booking).where(
            or_(Booking.start_date.between(start_date, end_date), Booking.end_date.between(start_date, end_date))
        )
        query_available_hotels = select(Hotel).join(Address).group_by(Hotel.id).join(Room).where(
            and_(Room.number.not_in(query_booked_rooms), Address.city.like(f"%{city}%"))
        )
        return self.__session.execute(query_available_hotels).scalars().all()

    def get_all_cities_with_hotels(self):
        query = select(Address.city).join(Hotel)
        return self.__session.execute(query).scalars().all()


def check_user_input(question, valid):
    user_in = input(question)
    while user_in not in valid:
        print("Invalid input. Please try again.")
        user_in = input(question)
    return user_in

if __name__ == "__main__":
    sm = SearchManager("../data/hotel_reservation.db")
    cities_with_hotels = sm.get_all_cities_with_hotels()
    print(cities_with_hotels)

    start = input("Enter your arrival (MM.DD.YYYY): ")
    date_format = "%d.%m.%Y"
    start_date = datetime.strptime(start, date_format)
    print(start_date.strftime(date_format))

    stay = input("Enter how long you stay in days: ")
    days = int(stay)
    end_date = start_date + timedelta(days=days)
    print(end_date.strftime(date_format))

    available = sm.get_available_hotels(start_date, end_date)
    for hotel in available:
        print(hotel)

    city = input("Enter city: ")
    available_city = sm.get_available_hotels_by_city(start_date, end_date, city)
    for hotel in available_city:
        print(hotel)

    user_stars = input("Enter the number of stars:  ")
    valid = ["1","2","3","4","5"]
    while user_stars not in valid:
        print(f"Please enter a number between {valid[0]} and {valid[1]}")
        user_stars = input("Enter number of stars: ")

    if user_stars == valid[0]:
        print(f"You are looking for hotels with {user_stars} star")
    else:
        print(f"You are looking for hotels with {user_stars} stars")

    nr_guests = input("For how many guests are you looking for ")
    valid = ["1","2","3","4"]
    while nr_guests not in valid:
        print(f"Please enter a number between {valid[0]} and {valid[1]}")
        nr_guests = input("Enter number of guests: ")

    if nr_guests == valid[0]:
        print(f"You are looking for hotels with {nr_guests} guest")
    else:
        print(f"You are looking for hotels with {nr_guests} guests")



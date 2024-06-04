from datetime import date, datetime, timedelta
from pathlib import Path

from sqlalchemy import create_engine, select, or_, and_
from sqlalchemy.orm import scoped_session, sessionmaker

from data_access.data_base import init_db
from data_models.models import Hotel, Room, Booking, Address

class SearchManager:
    def __init__(self, database_file):
        database_path = Path(database_file)
        if not database_path.is_file():
            init_db(database_file, generate_example_data=True)
        self.__engine = create_engine(f'sqlite:///{database_path}', echo=False)
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    def get_available_hotels(self, start_date: date, end_date: date):
        query_booked_rooms = select(Room.number).join(Booking).where(
            or_(Booking.start_date.between(start_date, end_date), Booking.end_date.between(start_date, end_date))
        )
        query_available_hotels = select(Hotel).group_by(Hotel.id).join(Room).where(
            Room.number.not_in(query_booked_rooms))

        return self.__session.execute(query_available_hotels).scalars().all()

    def get_available_hotels_by_city(self, start_date: date, end_date: date, city: str):
        query_booked_rooms = select(Room.number).join(Booking).where(
            or_(Booking.start_date.between(start_date, end_date), Booking.end_date.between(start_date, end_date))
        )
        query_available_hotels = (
            select(Hotel)
            .join(Address)
            .join(Room)
            .where(
                and_(
                    Room.number.not_in(query_booked_rooms),
                    Address.city.like(f"%{city}%")
                )
            )
            .group_by(Hotel.id)
        )

        return self.__session.execute(query_available_hotels).scalars().all()

    def get_hotel_details(self, hotel: Hotel):
        hotel_details = {
            'name': hotel.name,
            'address': f"{hotel.address.street}, {hotel.address.city} {hotel.address.zip}",
            'rooms': []
        }

        query_rooms = select(Room).where(Room.hotel_id == hotel.id)
        rooms = self.__session.execute(query_rooms).scalars().all()

        for room in rooms:
            room_details = {
                'type': room.type,
                'description': room.description,
                'max_guests': room.max_guests,
                'price': room.price,
                'amenities': room.amenities
            }
            hotel_details['rooms'].append(room_details)

        return hotel_details

    def get_all_cities_with_hotels(self):
        query = select(Address.city).join(Hotel)
        return self.__session.execute(query).scalars().all()

def check_user_input(question, valid):
    user_in = input(question)
    while user_in not in valid:
        print("Invalid input. Please try again.")
        user_in = input(question)
    return user_in

def get_date_input(prompt):
    date_format = "%d.%m.%Y"
    while True:
        user_input = input(prompt)
        try:
            return datetime.strptime(user_input, date_format)
        except ValueError:
            print(f"Invalid date format. Please use {date_format}")

if __name__ == "__main__":
    sm = SearchManager("../data/hotel_reservation.db")
    cities_with_hotels = sm.get_all_cities_with_hotels()
    print("Available cities with hotels:", cities_with_hotels)

    start_date = get_date_input("Enter your arrival date (DD.MM.YYYY): ")
    print("Arrival date:", start_date.strftime("%d.%m.%Y"))

    stay_duration = input("Enter the number of days you will stay: ")
    end_date = start_date + timedelta(days=int(stay_duration))
    print("Departure date:", end_date.strftime("%d.%m.%Y"))

    city = input("Enter the city you want to search for hotels: ")
    available_hotels_in_city = sm.get_available_hotels_by_city(start_date, end_date, city)
    if not available_hotels_in_city:
        print("No hotels available in this city for the given dates.")
    else:
        for hotel in available_hotels_in_city:
            details = sm.get_hotel_details(hotel)
            print(f"\nHotel: {details['name']}")
            print(f"Address: {details['address']}")
            print("Rooms:")
            for room in details['rooms']:
                print(f"  Type: {room['type']}")
                print(f"  Description: {room['description']}")
                print(f"  Max Guests: {room['max_guests']}")
                print(f"  Price: {room['price']}")
                print(f"  Amenities: {room['amenities']}")
                print("")

    user_stars = check_user_input("Enter the number of stars: ", ["1", "2", "3", "4", "5"])
    print(f"You are looking for hotels with {user_stars} star(s)")

    nr_guests = check_user_input("For how many guests are you looking for: ", ["1", "2", "3", "4"])
    print(f"You are looking for hotels with {nr_guests} guest(s)")



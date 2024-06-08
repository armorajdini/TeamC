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

    def get_available_hotels_by_city_stars_and_guests(self, start_date: date, end_date: date, city: str, stars: int,
                                                      guests: int):
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
                    Address.city.like(f"%{city}%"),
                    Hotel.stars == stars,
                    Room.max_guests >= guests
                )
            )
            .group_by(Hotel.id)
        )

        return self.__session.execute(query_available_hotels).scalars().all()

    def get_room_details(self, hotel: Hotel, stay_duration: int):
        query_rooms = select(Room).where(Room.hotel_id == hotel.id)
        rooms = self.__session.execute(query_rooms).scalars().all()

        room_details = []
        for room in rooms:
            room_info = {
                'type': room.type,
                'description': room.description,
                'max_guests': room.max_guests,
                'price_per_night': room.price,
                'total_price': room.price * stay_duration,
                'amenities': room.amenities
            }
            room_details.append(room_info)

        return room_details

    def get_all_cities_with_hotels(self):
        query = select(Address.city).join(Hotel)
        return self.__session.execute(query).scalars().all()


def check_user_input(question, valid):
    user_in = input(question).strip()
    while user_in not in valid:
        print("Invalid input. Please try again.")
        user_in = input(question).strip()
    return user_in


def get_date_input(prompt):
    date_format = "%d.%m.%Y"
    while True:
        user_input = input(prompt).strip()
        try:
            return datetime.strptime(user_input, date_format).date()
        except ValueError:
            print(f"Invalid date format. Please use {date_format}")


if __name__ == "__main__":
    sm = SearchManager("../data/hotel_reservation.db")
    cities_with_hotels = sm.get_all_cities_with_hotels()

    if not cities_with_hotels:
        print("No cities with hotels found.")
    else:
        print(f"Available cities with hotels: {', '.join(cities_with_hotels)}")

        start_date = get_date_input("Enter your arrival date (DD.MM.YYYY): ")
        stay_duration = input("Enter the number of days you will stay: ").strip()
        while not stay_duration.isdigit() or int(stay_duration) <= 0:
            print("Please enter a valid number of days.")
            stay_duration = input("Enter the number of days you will stay: ").strip()
        stay_duration = int(stay_duration)

        end_date = start_date + timedelta(days=stay_duration)
        print("Departure date:", end_date.strftime("%d.%m.%Y"))

        city = input("Enter the city you want to search for hotels: ").strip()
        user_stars = int(check_user_input("Enter the number of stars: ", ["1", "2", "3", "4", "5"]))
        nr_guests = input("For how many guests are you looking for: ").strip()
        while not nr_guests.isdigit() or int(nr_guests) <= 0:
            print("Please enter a valid number of guests.")
            nr_guests = input("For how many guests are you looking for: ").strip()
        nr_guests = int(nr_guests)

        available_hotels = sm.get_available_hotels_by_city_stars_and_guests(start_date, end_date, city, user_stars,
                                                                            nr_guests)

        if not available_hotels:
            print(f"No {user_stars}-star hotels available in {city} for {nr_guests} guest(s) and the given dates.")
        else:
            for hotel in available_hotels:
                room_details = sm.get_room_details(hotel, stay_duration)
                print(f"\nHotel: {hotel.name}")
                print(f"Address: {hotel.address.street}, {hotel.address.city} {hotel.address.zip}")
                for room in room_details:
                    if room['max_guests'] >= nr_guests:
                        print(f"\nRoom Type: {room['type']}")
                        print(f"Description: {room['description']}")
                        print(f"Max Guests: {room['max_guests']}")
                        print(f"Price per Night: {room['price_per_night']}")
                        print(f"Total Price for {stay_duration} nights: {room['total_price']}")
                        print(f"Amenities: {room['amenities']}")

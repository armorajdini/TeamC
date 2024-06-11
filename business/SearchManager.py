from datetime import date, datetime, timedelta
from pathlib import Path

from sqlalchemy import create_engine, select, or_, and_
from sqlalchemy.orm import scoped_session, sessionmaker

from data_access.data_base import init_db
from business.BaseManager import BaseManager
from data_models.models import Hotel, Room, Booking, Address


class SearchManager(BaseManager):
    def __init__(self, session):
        super().__init__(session)

    def get_available_rooms(self, hotel_id, start_date: date, end_date: date, guests: int):
        query_booked_rooms = select(Room.id).join(Booking).where(
            Room.hotel_id == hotel_id,
            or_(Booking.start_date.between(start_date, end_date), Booking.end_date.between(start_date, end_date))
        )
        query = select(Room).where(
            Room.hotel_id == hotel_id,
            Room.id.not_in(query_booked_rooms),
            Room.max_guests >= guests
        )
        result = self._session.execute(query).scalars().all()

        return result

    def get_available_hotels_by_city_stars_and_guests(self, start_date: date, end_date: date, guests: int,
                                                      city: str = None, stars: int = None, stars_is_max=True):
        query_booked_rooms = select(Room.id).join(Booking).where(
            or_(Booking.start_date.between(start_date, end_date), Booking.end_date.between(start_date, end_date))
        )

        query_available_rooms = select(Room).join(Hotel).where(
            Room.id.not_in(query_booked_rooms),
            Room.max_guests >= guests
        )

        if city:
            query_available_rooms = query_available_rooms.join(Address).where(
                Address.city.like(f"%{city}%")
            )
        if stars:
            if stars_is_max:
                query_available_rooms = query_available_rooms.where(Hotel.stars <= stars)
            else:
                query_available_rooms = query_available_rooms.where(Hotel.stars >= stars)

        result = self._session.execute(query_available_rooms).scalars().all()
        hotels = []
        for room in result:
            if room.hotel not in hotels:
                hotels.append(room.hotel)

        return hotels

    def get_room_details(self, hotel: Hotel, stay_duration: int):
        query_rooms = select(Room).where(Room.hotel_id == hotel.id)
        rooms = self._session.execute(query_rooms).scalars().all()

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
        return self._session.execute(query).scalars().all()


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
    db_file = '../data/test.db'
    db_path = Path(db_file)
    if not db_path.is_file():
        init_db(db_file, generate_example_data=True)

    engine = create_engine(f'sqlite:///{db_file}')
    session = scoped_session(sessionmaker(bind=engine))

    sm = SearchManager(session)

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

        while True:
            user_stars = input("Enter the number of stars (1-5): ").strip()
            if user_stars.isdigit() and 1 <= int(user_stars) <= 5:
                user_stars = int(user_stars)
                break
            else:
                print("Invalid input. Please enter a number between 1 and 5.")

        star_filter_type = check_user_input("Do you want a minimum or maximum star filter? (min/max): ", ["min", "max"])
        user_stars_is_max = True if star_filter_type == "max" else False

        nr_guests = input("For how many guests are you looking for: ").strip()
        while not nr_guests.isdigit() or int(nr_guests) <= 0:
            print("Please enter a valid number of guests.")
            nr_guests = input("For how many guests are you looking for: ").strip()
        nr_guests = int(nr_guests)

        available_hotels = sm.get_available_hotels_by_city_stars_and_guests(
            start_date,
            end_date,
            nr_guests,
            city,
            user_stars,
            user_stars_is_max
        )

        if not available_hotels:
            print(
                f"No hotels available in {city} with {user_stars} star(s) for {nr_guests} guest(s) and the given dates.")
        else:
            for hotel in available_hotels:
                print(f"Hotel: {hotel.name}")
                print("-" * 20)
                available_rooms = sm.get_available_rooms(hotel.id, start_date, end_date, nr_guests)
                for room in available_rooms:
                    print(f"Room Type: {room.type}")
                    print(f"Room Number: {room.number}")
                    print(f"Room max guests: {room.max_guests}")
                    print(f"Room costs per night: {room.price}")
                    print(f"Room total costs: {room.price * stay_duration}")
                    print(f"Room amenities: {room.amenities}")
                    print()
                    print()

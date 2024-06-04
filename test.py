# include all search functions here
# accept search criteria, search by various criteria
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.orm import scoped_session, sessionmaker

from data_access.data_base import init_db
from data_models.models import *

class SearchManager:
    def __init__(self, path: Path):
        if not path.is_file():
            init_db(str(path), generate_example_data=True)
        self._engine = create_engine(f"sqlite:///{path}")
        self._session = scoped_session(sessionmaker(bind=self._engine))

    def search(self, hotel_id):
        query = select(Hotel).where(Hotel.id == hotel_id)
        return self._session.execute(query).scalars().one()

if __name__ == "__main__":
    sm = SearchManager(Path("../data/test.db"))
    hotel = sm.search(1)
    print(hotel)

def get_available_hotel_in_city(self, start_date: date, end_date: date, city_name: str):
    q_booked_rooms = select(Room).join(Booking).where(
        Booking.end_date.between(start_date, end_date) | Booking.end_date.between(start_date, end_date)
    )
    booked_room = self._session.execute(q_booked_rooms).scalars().all()

    q_all_rooms = select(Room).join(Hotel).join(Address).where(Address.city.like(f"%{city_name}%"))
    all_room = self._session.execute(q_all_rooms).scalars().all()

    hotels = []
    for room in all_room:
        if room not in booked_room:
            if room.hotel not in hotels:
                hotels.append(room.hotel)
    return hotels

    in_start = "12.01.24"
    input("Enter the start date (DD.MM.YY): ")
    date_format = "%d.%m.%y"
    start_date = datetime.strptime(in_start, date_format)
    date_format_out = "%d.%m.%Y"
    print(start_date.strftime(date_format_out))

def get_all_bookings_of(self, guest: RegisteredGuest):
    query = select(Booking).where(Booking.guest_id == guest.id)
    bookings = self._session.execute(query).scalars().all()
    return bookings

def get_guest_by_id(self, id: int):
    query = select(Guest).where(Guest.id == id)
    guest = self._session.execute(query).scalars().one()
    return guest

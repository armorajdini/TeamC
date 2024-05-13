from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select
from sqlalchemy.orm import scoped_session, sessionmaker
from data_access.data_base import init_db
from data_models.models import *

from business.SearchManager import SearchManager
from business.BaseManager import BaseManager

class BookingManager(BaseManager):
    def __init__(self, db_file: Path):
        if not db_file.exists():
            init_db(str(db_file), generate_example_data=True)
        self.__engine = create_engine(f"sqlite:///{db_file}")
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    def get_bookings_of(self, guest: RegisteredGuest):
        query_booking = select(Booking).join(Guest, Guest.id == guest.id)
        bookings = self.__session.execute(query_booking).scalars().all()
        return bookings

    def get_available_rooms(self, hotel: Hotel, start_date: datetime, end_date: datetime, number_of_guests: int):
        q_booked_rooms = select(Room).join(Booking).where(
            (Booking.start_date <= end_date) & (Booking.end_date >= start_date)
        ).where(Room.hotel_id == hotel.id)
        q_all_rooms = select(Room).where(Room.hotel_id == hotel.id).where(Room.max_guests >= number_of_guests)
        booked_rooms = self.__session.execute(q_booked_rooms).scalars().all()
        all_rooms = self.__session.execute(q_all_rooms).scalars().all()
        available = [room for room in all_rooms if room not in booked_rooms]
        return available

    def get_r_guest(self, id: int):
        guest_query = select(RegisteredGuest).where(RegisteredGuest.id == id)
        guest = self.__session.execute(guest_query).scalars().one()
        return guest

    def create_booking(self, room: Room, guest: Guest, number_of_guests: int, start_date: datetime, end_date: datetime, comment: str):
        booking = Booking(room=room, guest=guest, number_of_guests=number_of_guests,
                          start_date=start_date, end_date=end_date, comment=comment)
        self.__session.add(booking)
        self.__session.commit()

if __name__ == '__main__':
    db_path = Path("../data/hotel_reservation.db")
    sm = SearchManager(db_path)
    bm = BookingManager(db_path)

    guest_id = 5
    laura = bm.get_r_guest(guest_id)
    bookings = bm.get_bookings_of(laura)
    for booking in bookings:
        print(booking)

    in_city = input("Stadt: ")
    in_start = input("Startdatum (DD.MM.YY): ")
    date_format = '%d.%m.%y'
    in_start_date = datetime.strptime(in_start, date_format)

    in_duration = int(input("Wie viele Tage?: "))
    in_end_date = in_start_date + timedelta(days=in_duration)

    all_hotels = sm.get_available_hotels_by_city(in_start_date, in_end_date, in_city)
    for i, hotel in enumerate(all_hotels, 1):
        print(f"{i}. {hotel}")

    selection = int(input("Wählen Sie ein Hotel: "))
    selected_hotel = all_hotels[selection - 1]
    in_number_of_guests = int(input("Anzahl der Gäste: "))

    available_rooms = bm.get_available_rooms(selected_hotel, in_start_date, in_end_date, in_number_of_guests)
    if len(available_rooms) < 1:
        print("Keine Zimmer verfügbar!")
    else:
        for i, room in enumerate(available_rooms, 1):
            print(f"{i}. {room}")
        selection = int(input("Wählen Sie ein Zimmer: "))
        selected_room = available_rooms[selection - 1]

        in_comment = input("Buchungskommentar: ")

        bm.create_booking(selected_room, laura, in_number_of_guests, in_start_date, in_end_date, in_comment)

        bookings = bm.get_bookings_of(laura)
        for booking in bookings:
            print(booking)

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
from business.BookingManager import BookingManager

class HotelManager(BaseManager):
    def __init__(self, db_file: Path):
        if not db_file.is_file():
            init_db(str(db_file), generate_example_data=True)
        self.__engine = create_engine(f"sqlite:///{db_file}")
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    def add_hotel(self, name: str, stars: int, address: Address, rooms):
        if len(rooms) > 0:
            hotel = Hotel(name=name, stars=stars, address=address, rooms=rooms)
            self.__session.add(hotel)
            self.__session.commit()
        else:
            raise AttributeError('Hotel with no rooms are not allowed')

    def remove_hotel(self, hotel_id: int):
        hotel_query = delete(Hotel).where(Hotel.id == hotel_id)
        self.__session.execute(hotel_query)
        self.__session.commit()

    def get_all_hotels(self):
        query = select(Hotel)
        return self.__session.execute(query).scalars().all()

    def update_hotel(self, hotel_id: int, name: str = None, stars: int = None, address: str = None):
        update_values = {}
        if name:
            update_values[Hotel.name] = name
        if stars:
            update_values[Hotel.stars] = stars
        if address:
            update_values[Hotel.address] = address

        if update_values:
            hotel_query = update(Hotel).where(Hotel.id == hotel_id).values(**update_values)
            self.__session.execute(hotel_query)
            self.__session.commit()



    def get_bookings_of(self, registered_guest_id:int):
        pass



if __name__ == '__main__':
    db_path = Path("../data/hotel_reservation.db")

    hm = HotelManager(db_path)
    sm = SearchManager(db_path)
    bm = BookingManager(db_path)

    print("All Hotels:")
    all_hotels = hm.get_all_hotels()
    for hotel in all_hotels:
        print(hotel)
    input("Press Enter to continue...")
    print("\n")

    address_1 = Address(street="Beispiel",zip="4321",city="Bern")
    room_1 = [Room(number = "01",type="Double",max_guests=2,description="Wunderschönes Doppelzimmer",amenities="tbd",
                      price=130)]
    hm.add_hotel(name="Test Hotel2", stars=4, address=address_1, rooms=room_1)
    all_hotels = hm.get_all_hotels()
    for hotel in all_hotels:
        print(hotel)

    hm.remove_hotel(hotel_id=14)

    updated_address = Address(street="Beispielupdate", city="Thun", zip="5555")
    # hm.update_hotel(hotel_id=9, name="Test Hotel update", stars=5, address=updated_address)

    print("All Bookings:")
    all_bookings = bm.get_all_bookings()
    for booking in all_bookings:
        print(booking)
    input("Press Enter to continue...")
    print("\n")

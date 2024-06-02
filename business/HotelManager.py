from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import scoped_session, sessionmaker
from data_access.data_base import init_db
from data_models.models import *

from data_access.data_generator import *

from business.SearchManager import *
from business.BaseManager import BaseManager

class HotelManager(BaseManager):
    def __init__(self, db_file: Path):
        if not db_file.exists():
            init_db(str(db_file), generate_example_data=True)
        self.__engine = create_engine(f"sqlite:///{db_file}")
        self.__session = scoped_session(sessionmaker(bind=self.__engine))

    def add_hotel(self, name: str, stars: int, address: Address, room):
        hotel = Hotel(name=name, stars=stars, address=address, rooms=room)
        self.__session.add(hotel)
        self.__session.commit()

    def remove_hotel(self, hotel_id: int):
        hotel_query = delete(Hotel).where(Hotel.id == hotel_id)
        self.__session.execute(hotel_query)
        self.__session.commit()

    def get_all_hotels(self):
        query = select(Hotel)
        return self.__session.execute(query).scalars().all()

    def update_hotel(self, hotel_id: int, name: str = None, city: str = None, stars: int = None,
                     description: str = None):
        update_values = {}
        if name:
            update_values[Hotel.name] = name
        if city:
            update_values[Hotel.city] = city
        if stars:
            update_values[Hotel.stars] = stars
        if description:
            update_values[Hotel.description] = description

        if update_values:
            hotel_query = update(Hotel).where(Hotel.id == hotel_id).values(**update_values)
            self.__session.execute(hotel_query)
            self.__session.commit()

    def get_all_bookings(self):
        bookings_query = select(Booking)
        bookings = self.__session.execute(bookings_query).scalars().all()
        return bookings



if __name__ == '__main__':
    db_path = Path("../data/hotel_reservation.db")
    hm = HotelManager(db_path)
    address_1 = Address(street="Beispiel",zip="4321",city="Bern")
    room_1 = [Room(number = "01",type="Double",max_guests=2,description="Wunderschönes Doppelzimmer",amenities="tbd",
                      price=130)]
    hm.add_hotel(name="Test Hotel2", stars=4, address=address_1, room=room_1)
    #hm.update_hotel(hotel_id=1, name="Updated Hotel Name")
    #hm.remove_hotel(hotel_id=1)
    all_hotels = hm.get_all_hotels()
    for hotel in all_hotels:
        print(hotel)


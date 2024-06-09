import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, select, update, delete, insert
from sqlalchemy.orm import scoped_session, sessionmaker, joinedload
from sqlalchemy.orm.scoping import scoped_session
from data_access.data_base import init_db
from data_models.models import *

from data_access.data_generator import *

from business.SearchManager import SearchManager
from business.BaseManager import BaseManager
from business.BookingManager import BookingManager
from business.UserManager import UserManager


class HotelManager(BaseManager):
    def __init__(self, session):
        super().__init__(session)

    def add_hotel(self, name: str, stars: int, address: Address, rooms):
        if len(rooms) > 0:
            hotel = Hotel(name=name, stars=stars, address=address, rooms=rooms)
            self._session.add(hotel)
            self._session.commit()
        else:
            raise AttributeError('Hotel with no rooms are not allowed')

    def remove_hotel(self, hotel_id: int):
        hotel_query = delete(Hotel).where(Hotel.id == hotel_id)
        self._session.execute(hotel_query)
        self._session.commit()

    def get_all_hotels(self):
        query = select(Hotel)
        return self._session.execute(query).scalars().all()

    def update_hotel(self, hotel_id: int, name: str = None, stars: int = None):
        query = update(Hotel).where(Hotel.id == hotel_id).values(name=name, stars=stars)
        self._session.execute(query)
        self._session.commit()

    def update_address(self, address_id: int, street: str, city: str, zip_code: int):
        query = update(Address).where(Address.id == address_id).values(street=street, city=city, zip=zip_code)
        self._session.execute(query)
        self._session.commit()

    def update_room(self, room_id: int, room_number: int, type: str, max_guests: int, description: str, amenities: str,
                    price: float):
        query = update(Room).where(Room.id == room_id).values(number=room_number, type=type, max_guests=max_guests,
                                                              description=description, amenities=amenities, price=price)
        self._session.execute(query)
        self._session.commit()
        pass

    def get_rooms_by_hotel_id(self, hotel_id: int):
        # add join?
        query = select(Room).join(Room.hotel).where(Hotel.id == hotel_id)
        return self._session.execute(query).scalars().all()

    def add_hotel_console(self):

        #Add hotel infos
        hotel_name = input("Hotel name: ")
        hotel_stars = input("Hotel stars: ")

        # Add address of hotel
        address_street = input("Street name: ")
        address_city = input("City name: ")
        address_zip = input("Zip code: ")
        full_address = Address(street=address_street, zip=address_zip, city=address_city)

        print(f"The address is: {full_address}, continue with the hotel infos")

        # Add rooms of hotel
        add_room = True
        hotel_rooms = []

        while add_room:
            room_number = input("Room number: ")
            room_type = input("Room type: ")
            room_max_guests = input("Room max guests: ")
            room_description = input("Room description: ")
            room_amenities = input("Room amenities: ")
            room_price = input("Room price: ")
            add_room_input = input("Do you want to add another room (Y/N)")

            # append new room to list
            full_room = Room(number=room_number, type=room_type, max_guests=room_max_guests, description=room_description,
                 amenities=room_amenities, price=room_price)
            hotel_rooms.append(full_room)

            # ask user to add another room
            if add_room_input == "n" or add_room_input == "N":
                add_room = False

        for room in hotel_rooms:
            print(f"Room infos: {room}")

        hm.add_hotel(name=hotel_name, stars=hotel_stars, address=full_address, rooms=hotel_rooms)
        check_all_hotels = hm.get_all_hotels()
        print("all hotels after: ")
        for hotel in check_all_hotels:
            print(hotel)

    def update_hotel_console(self):
        print("All Hotels:")
        all_hotels = hm.get_all_hotels()
        for hotel in all_hotels:
            print(hotel)

        print("1.) Update Hotel-info")
        print("2.) Update Hotel-address")
        print("3.) Update Hotel-rooms")
        user_selection_update = input("Please choose an option: ")

        match user_selection_update:
            case "1":
                print("UPDATE HOTEL")
                update_hotel_id = int(input("select hotel id to update values: "))
                for hotel in all_hotels:
                    if hotel.id == update_hotel_id:
                        selected_hotel = hotel

                print(f"selected hotel: {selected_hotel}")

                # update hotel infos
                update_hotel_name = input("Hotel name: ")
                update_hotel_stars = int(input("Hotel stars: "))

                hm.update_hotel(selected_hotel.id, update_hotel_name, update_hotel_stars)
            case "2":
                print("UPDATE ADDRESS")
                update_hotel_id = int(input("select hotel to update values: "))
                for hotel in all_hotels:
                    if hotel.id == update_hotel_id:
                        selected_address_id = hotel.address.id

                update_address_street = input("Street name: ")
                update_address_city = input("City name: ")
                update_address_zip = input("Zip code: ")

                hm.update_address(address_id=selected_address_id, street=update_address_street, city=update_address_city, zip_code=update_address_zip)
            case "3":
                print("GET ROOMS BY HOTEL_ID")
                selected_hotel_id = int(input("SELECT HOTEL BY ID: "))
                all_rooms = hm.get_rooms_by_hotel_id(selected_hotel_id)

                for room in all_rooms:
                    print(f"room in all_rooms: {room}")
                valid = False
                while not valid:
                    try:
                        room_id = int(input("select room to update values:"))
                        valid = True
                    except ValueError:
                        print("Please enter a valid id")

                print(f"UPDATE ROOM WITH ID: {room_id}")

                update_room_number = int(input("Room number: "))
                update_room_type = input("Room type: ")
                update_room_max_guests = int(input("Room max guests: "))
                update_room_description = input("Room description: ")
                update_room_amenities = input("Room amenities: ")
                update_room_price = int(input("Room price: "))

                hm.update_room(room_id,update_room_number, update_room_type, update_room_max_guests,
                               update_room_description, update_room_amenities, update_room_price)

                all_rooms = hm.get_rooms_by_hotel_id(selected_hotel_id)

                for room in all_rooms:
                    print(f"room in all_rooms after update: {room}")

        print("All Hotels after update:")
        all_hotels = hm.get_all_hotels()
        for hotel in all_hotels:
            print(hotel)



    def remove_hotel_console(self):
        print("All Hotels:")
        hotels = hm.get_all_hotels()
        for hotel in hotels:
            print(hotel)

        delete_hotel_id = int(input("Id to delete Hotel by id: "))

        hm.remove_hotel(delete_hotel_id)

        print("All Hotels after removing:")
        all_hotels = hm.get_all_hotels()
        for hotel in all_hotels:
            print(hotel)



if __name__ == '__main__':
    db_file = '../data/test.db'
    db_path = Path(db_file)
    # Ensure the environment Variable is set
    if not db_path.is_file():
        init_db(db_file, generate_example_data=True)

    # create the engine and the session.
    # the engine is private, no need for subclasses to be able to access it.
    engine = create_engine(f'sqlite:///{db_file}')
    # create the session as db connection
    # subclasses need access therefore, protected attribute so every inheriting manager has access to the connection
    session = scoped_session(sessionmaker(bind=engine))

    hm = HotelManager(session)
    sm = SearchManager(session)
    bm = BookingManager(session)
    um = UserManager(session)

    # login user -> only admins can access this part
    um.login_user()
    current_user = um.get_current_user()

    while True:
        if current_user.role.name == "administrator":
            print("** ---------------- Hotel Manager ---------------- **")
            print("1.) Add Hotel")
            print("2.) Remove Hotel")
            print("3.) Update Hotel / Address / Room information")
            print("4.) Get all bookings")
            print("5.) Show all hotels")
            user_selection = input("Please choose an option: ")

            match user_selection:
                case "1":
                    pass
                    hm.add_hotel_console()
                case "2":
                    pass
                    hm.remove_hotel_console()
                case "3":
                    pass
                    hm.update_hotel_console()
                case "4":
                    all_bookings = bm.get_all_bookings()
                    for booking in all_bookings:
                        print(f"Booking: {booking}")
                case "5":
                    all_hotels = hm.get_all_hotels()
                    for hotels in all_hotels:
                        print(f"Hotel: {hotels}")

            user_logout_input = input("Do you want to logout?`(Y/N)")
            if user_logout_input == "y" or user_logout_input == "Y":
                um.logout()
        else:
            print("Please login as a Admin to access this part of the application")
            sys.exit(1)
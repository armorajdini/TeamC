from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import scoped_session, sessionmaker
from data_access.data_base import init_db
from data_models.models import *
from business.SearchManager import SearchManager
from business.BaseManager import BaseManager
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookingManager(BaseManager):
    def __init__(self, session):
        super().__init__(session)

    def get_bookings_of(self, guest_id: int):
        try:
            query_booking = select(Booking).where(Booking.guest_id == guest_id)
            bookings = self._session.execute(query_booking).scalars().all()
            return bookings
        except Exception as e:
            logger.error(f"Error fetching bookings: {e}")
            return []

    def create_booking(self, room_hotel_id: int, room_number: str, guest_id: int, number_of_guests: int,
                       start_date: datetime, end_date: datetime, comment: str):
        try:
            booking = Booking(
                room_hotel_id=room_hotel_id,
                room_number=room_number,
                guest_id=guest_id,
                number_of_guests=number_of_guests,
                start_date=start_date,
                end_date=end_date,
                comment=comment
            )
            self._session.add(booking)
            self._session.commit()
            logger.info("Booking created successfully")
        except Exception as e:
            logger.error(f"Error creating booking: {e}")

    def get_available_rooms(self, hotel: Hotel, start_date: datetime, end_date: datetime, number_of_guests: int):
        try:
            q_booked_rooms = select(Room).join(Booking).where(
                and_(
                    Booking.start_date <= end_date,
                    Booking.end_date >= start_date
                )
            ).where(Room.hotel_id == hotel.id)
            q_all_rooms = select(Room).where(
                and_(
                    Room.hotel_id == hotel.id,
                    Room.max_guests >= number_of_guests
                )
            )
            booked_rooms = self._session.execute(q_booked_rooms).scalars().all()
            all_rooms = self._session.execute(q_all_rooms).scalars().all()
            available = [room for room in all_rooms if room not in booked_rooms]
            return available
        except Exception as e:
            logger.error(f"Error fetching available rooms: {e}")
            return []

    def get_all_bookings(self):
        try:
            bookings_query = select(Booking)
            bookings = self._session.execute(bookings_query).scalars().all()
            return bookings
        except Exception as e:
            logger.error(f"Error fetching all bookings: {e}")
            return []

    def get_guest(self, id: int):
        try:
            guest_query = select(Guest).where(Guest.id == id)
            guest = self._session.execute(guest_query).scalars().one()
            return guest
        except Exception as e:
            logger.error(f"Error fetching guest: {e}")
            return None

    def create_or_login_guest(self, email: str, password: str):
        try:
            # Check if the username already exists
            existing_user_query = select(Login).where(Login.username == email)
            existing_user = self._session.execute(existing_user_query).scalars().first()

            if existing_user:
                # Check if the password matches
                if existing_user.password == password:
                    logger.info("Welcome back!")
                    guest_query = select(Guest).where(Guest.email == email)
                    guest = self._session.execute(guest_query).scalars().first()
                    return guest
                else:
                    logger.error("Password does not match.")
                    return None
            else:
                # Create a new guest
                role_query = select(Role).where(Role.name == "guest")
                role = self._session.execute(role_query).scalars().first()
                if not role:
                    role = Role(name="guest", access_level=1)
                    self._session.add(role)
                    self._session.commit()

                # Create a dummy address if needed
                address = Address(street="Unknown", zip="00000", city="Unknown")
                self._session.add(address)
                self._session.commit()

                # Create the Guest entry
                guest = Guest(
                    firstname="Guest",
                    lastname="User",
                    email=email,
                    address_id=address.id,
                    type="guest"
                )
                self._session.add(guest)
                self._session.commit()

                # Create the Login entry linked to the guest with the guest role
                new_login = Login(username=email, password=password, role_id=role.id)
                self._session.add(new_login)
                self._session.commit()

                return guest
        except Exception as e:
            logger.error(f"Error creating or logging in guest: {e}")
            return None

    def update_booking(self, reservation_id: int, **kwargs):
        try:
            booking_query = select(Booking).where(Booking.id == reservation_id)
            booking = self._session.execute(booking_query).scalars().one()
            for key, value in kwargs.items():
                setattr(booking, key, value)
            self._session.commit()
        except Exception as e:
            logger.error(f"Error updating booking: {e}")

    def delete_booking(self, reservation_id: int):
        try:
            booking_query = select(Booking).where(Booking.id == reservation_id)
            booking = self._session.execute(booking_query).scalars().one()
            self._session.delete(booking)
            self._session.commit()
        except Exception as e:
            logger.error(f"Error deleting booking: {e}")

    def update_room_availability(self, room_hotel_id: int, room_number: str, availability: bool):
        try:
            room_query = select(Room).where(
                and_(Room.hotel_id == room_hotel_id, Room.number == room_number)
            )
            room = self._session.execute(room_query).scalars().one()
            room.available = availability
            self._session.commit()
        except Exception as e:
            logger.error(f"Error updating room availability: {e}")

    def update_room_price(self, room_hotel_id: int, room_number: str, price: float):
        try:
            room_query = select(Room).where(
                and_(Room.hotel_id == room_hotel_id, Room.number == room_number)
            )
            room = self._session.execute(room_query).scalars().one()
            room.price = price
            self._session.commit()
        except Exception as e:
            logger.error(f"Error updating room price: {e}")

    def login(self, email: str, password: str):
        try:
            user_query = select(Login).where(
                and_(Login.username == email, Login.password == password)
            )
            user = self._session.execute(user_query).scalars().one_or_none()

            if user and user.role.name != 'guest':
                return user
            else:
                logger.error("E-Mail oder Passwort ist falsch.")
                return None
        except Exception as e:
            logger.error(f"Error logging in: {e}")
            return None


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
    sm = SearchManager(session)
    bm = BookingManager(session)

    user = None
    date_format = '%d.%m.%y'

    while True:
        if not user:
            print("1. Als Gast fortfahren")
            print("2. Anmelden")
            print("3. Beenden")
            choice = input("Wählen Sie eine Option: ")

            if choice == '1':
                # Gastbenutzer: Prüfe oder registriere neuen Gast
                email = input("Geben Sie Ihre E-Mail ein: ")
                password = input("Geben Sie Ihr Passwort ein: ")
                guest = bm.create_or_login_guest(email, password)
                if guest:
                    user = guest
                    if guest.firstname == "Guest":
                        print(f"Erfolgreich als neuer Gast angemeldet. Ihre Gast-ID ist {user.id}")
                    else:
                        print(f"Willkommen zurück, {guest.firstname}!")
                else:
                    print("Fehler bei der Anmeldung oder Registrierung als Gast.")

            elif choice == '2':
                # Benutzeranmeldung
                email = input("E-Mail: ")
                password = input("Passwort: ")
                user = bm.login(email, password)
                if user:
                    print(f"Benutzer {user.id} erfolgreich angemeldet.")
                else:
                    print("E-Mail oder Passwort ist falsch.")
                    user = None

            elif choice == '3':
                print("Programm beendet.")
                break
            else:
                print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")

        else:
            print("1. Meine Buchungen anzeigen")
            print("2. Neue Buchung erstellen")
            print("3. Buchung verwalten")
            print("4. Logout")
            choice = input("Wählen Sie eine Option: ")

            if choice == '1':
                bookings = bm.get_bookings_of(user.id)
                if bookings:
                    for i, booking in enumerate(bookings, 1):
                        print(f"{i}. {booking}")
                else:
                    print("Keine Buchungen gefunden.")

            elif choice == '2':
                in_city = input("Stadt: ")
                in_start = input("Startdatum (DD.MM.YY): ")
                in_start_date = datetime.strptime(in_start, date_format)

                in_duration = int(input("Wie viele Tage?: "))
                in_end_date = in_start_date + timedelta(days=in_duration)

                all_hotels = sm.get_available_hotels_by_city(in_start_date, in_end_date, in_city)
                for i, hotel in enumerate(all_hotels, 1):
                    print(f"{i}. {hotel}")

                selection = int(input("Wählen Sie ein Hotel: "))
                selected_hotel = all_hotels[selection - 1]
                in_number_of_guests = int(input("Anzahl der Gäste: "))

                available_rooms = bm.get_available_rooms(selected_hotel, in_start_date, in_end_date,
                                                         in_number_of_guests)
                if len(available_rooms) < 1:
                    print("Keine Zimmer verfügbar!")
                else:
                    for i, room in enumerate(available_rooms, 1):
                        print(f"{i}. {room}")
                    selection = int(input("Wählen Sie ein Zimmer: "))
                    selected_room = available_rooms[selection - 1]

                    in_comment = input("Buchungskommentar: ")

                    bm.create_booking(selected_room.hotel_id, selected_room.number, user.id, in_number_of_guests,
                                      in_start_date, in_end_date, in_comment)
                    print("Buchung erfolgreich!")

            elif choice == '3':
                bookings = bm.get_bookings_of(user.id)
                if bookings:
                    for i, booking in enumerate(bookings, 1):
                        print(f"{i}. {booking}")

                    action = input("Möchten Sie eine Buchung aktualisieren (1) oder stornieren (2)?: ")
                    if action == '1':
                        reservation_id = int(
                            input("Wählen Sie die Nummer der Buchung, die Sie aktualisieren möchten: "))
                        selected_booking = bookings[reservation_id - 1]

                        print("1. Startdatum ändern")
                        print("2. Enddatum ändern")
                        print("3. Kommentar ändern")
                        field_choice = input("Wählen Sie eine Option: ")
                        if field_choice == '1':
                            new_start_date = input("Neues Startdatum (DD.MM.YY): ")
                            new_start_date = datetime.strptime(new_start_date, date_format)
                            bm.update_booking(selected_booking.id, start_date=new_start_date)
                        elif field_choice == '2':
                            new_end_date = input("Neues Enddatum (DD.MM.YY): ")
                            new_end_date = datetime.strptime(new_end_date, date_format)
                            bm.update_booking(selected_booking.id, end_date=new_end_date)
                        elif field_choice == '3':
                            new_comment = input("Neuer Kommentar: ")
                            bm.update_booking(selected_booking.id, comment=new_comment)
                        else:
                            print("Ungültige Auswahl.")

                        print("Buchung erfolgreich aktualisiert!")

                    elif action == '2':
                        reservation_id = int(input("Wählen Sie die Nummer der Buchung, die Sie stornieren möchten: "))
                        selected_booking = bookings[reservation_id - 1]
                        bm.delete_booking(selected_booking.id)
                        print("Buchung erfolgreich gelöscht!")
                    else:
                        print("Ungültige Auswahl.")

            elif choice == '4':
                user = None
                print("Erfolgreich ausgeloggt.")

            else:
                print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import scoped_session, sessionmaker
from data_access.data_base import init_db
from data_models.models import *
from business.SearchManager import SearchManager
from business.BaseManager import BaseManager
from business.UserManager import UserManager
from business.HotelManager import HotelManager
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
            logger.error(f"Fehler beim Abrufen der Buchungen: {e}")
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
            logger.info("Buchung erfolgreich erstellt")
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Buchung: {e}")

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
            logger.error(f"Fehler beim Abrufen der verfügbaren Zimmer: {e}")
            return []

    def get_all_bookings(self):
        try:
            bookings_query = select(Booking)
            bookings = self._session.execute(bookings_query).scalars().all()
            return bookings
        except Exception as e:
            logger.error(f"Fehler beim Abrufen aller Buchungen: {e}")
            return []

    def get_bookings_by_hotel(self, hotel_id: int):
        try:
            bookings_query = select(Booking).join(Room).where(Room.hotel_id == hotel_id)
            bookings = self._session.execute(bookings_query).scalars().all()
            return bookings
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Buchungen für das Hotel: {e}")
            return []

    def get_guest(self, id: int):
        try:
            guest_query = select(Guest).where(Guest.id == id)
            guest = self._session.execute(guest_query).scalars().one()
            return guest
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Gastes: {e}")
            return None

    def create_guest(self):
        try:
            first_name = input("Bitte geben Sie Ihren Vornamen ein: ")
            last_name = input("Bitte geben Sie Ihren Nachnamen ein: ")
            email = input("Bitte geben Sie Ihre E-Mail-Adresse ein: ")
            street = input("Bitte geben Sie Ihre Straße ein: ")
            zip_code = input("Bitte geben Sie Ihre Postleitzahl ein: ")
            city = input("Bitte geben Sie Ihre Stadt ein: ")
            address = Address(street=street, zip=zip_code, city=city)

            guest = Guest(
                firstname=first_name,
                lastname=last_name,
                email=email,
                address=address,
            )
            self._session.add(guest)
            self._session.commit()
            return guest
        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Gastes: {e}")
            return None

    def update_booking(self, reservation_id: int, **kwargs):
        try:
            booking_query = select(Booking).where(Booking.id == reservation_id)
            booking = self._session.execute(booking_query).scalars().one()
            for key, value in kwargs.items():
                setattr(booking, key, value)
            self._session.commit()
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren der Buchung: {e}")

    def delete_booking(self, reservation_id: int):
        try:
            booking_query = select(Booking).where(Booking.id == reservation_id)
            booking = self._session.execute(booking_query).scalars().one()
            self._session.delete(booking)
            self._session.commit()
        except Exception as e:
            logger.error(f"Fehler beim Löschen der Buchung: {e}")

    def update_room_availability(self, room_hotel_id: int, room_number: str, availability: bool):
        try:
            room_query = select(Room).where(
                and_(Room.hotel_id == room_hotel_id, Room.number == room_number)
            )
            room = self._session.execute(room_query).scalars().one()
            room.available = availability
            self._session.commit()
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren der Zimmerverfügbarkeit: {e}")

    def update_room_price(self, room_hotel_id: int, room_number: str, price: float):
        try:
            room_query = select(Room).where(
                and_(Room.hotel_id == room_hotel_id, Room.number == room_number)
            )
            room = self._session.execute(room_query).scalars().one()
            room.price = price
            self._session.commit()
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Zimmerpreises: {e}")

    def download_booking_details(self, booking: Booking):
        try:
            file_name = f"booking_details_{booking.id}.txt"
            with open(file_name, 'w') as file:
                file.write(f"Buchungs-ID: {booking.id}\n")
                file.write(f"Hotel: {booking.room.hotel.name}\n")
                file.write(f"Zimmernummer: {booking.room.number}\n")
                file.write(f"Gästeanzahl: {booking.number_of_guests}\n")
                file.write(f"Startdatum: {booking.start_date}\n")
                file.write(f"Enddatum: {booking.end_date}\n")
                file.write(f"Kommentar: {booking.comment}\n")
            print(f"Buchungsdetails erfolgreich in {file_name} heruntergeladen.")
        except Exception as e:
            logger.error(f"Fehler beim Herunterladen der Buchungsdetails: {e}")

def display_hotels(hotels):
    print("\nVerfügbare Hotels:")
    for i, hotel in enumerate(hotels, 1):
        print(f"{i}. {hotel.name} - {hotel.address.city} - {hotel.stars} Sterne")

def display_rooms(rooms):
    print("\nVerfügbare Zimmer:")
    for i, room in enumerate(rooms, 1):
        print(f"{i}. Zimmernummer: {room.number}, Preis: {room.price} EUR/Nacht, Max. Gäste: {room.max_guests}")

def handle_guest_session(bm, sm, user, date_format):
    print(f"Erfolgreich als neuer Gast angemeldet. Ihre Gast-ID ist {user.id}")

    while True:
        print("\nGast-Menü:")
        print("1. Neue Buchung erstellen")
        print("2. Zurück zum Hauptmenü")
        choice = input("Wählen Sie eine Option: ")

        if choice == '1':
            in_city = input("Stadt: ")
            in_start = input("Startdatum (DD.MM.YY): ")
            in_start_date = datetime.strptime(in_start, date_format)

            in_duration = int(input("Wie viele Tage?: "))
            in_end_date = in_start_date + timedelta(days=in_duration)

            all_hotels = sm.get_available_hotels_by_city_stars_and_guests(in_start_date, in_end_date, in_duration, in_city)
            if all_hotels:
                display_hotels(all_hotels)

                selection = int(input("Wählen Sie ein Hotel: "))
                selected_hotel = all_hotels[selection - 1]
                in_number_of_guests = int(input("Anzahl der Gäste: "))

                available_rooms = bm.get_available_rooms(selected_hotel, in_start_date, in_end_date, in_number_of_guests)
                if available_rooms:
                    display_rooms(available_rooms)
                    selection = int(input("Wählen Sie ein Zimmer: "))
                    selected_room = available_rooms[selection - 1]

                    in_comment = input("Buchungskommentar: ")

                    bm.create_booking(selected_room.hotel_id, selected_room.number, user.id, in_number_of_guests,
                                      in_start_date, in_end_date, in_comment)
                    print("Buchung erfolgreich!")
                else:
                    print("Keine Zimmer verfügbar!")
            else:
                print("Keine Hotels verfügbar!")
        elif choice == '2':
            break
        else:
            print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")

def handle_admin_session(um, hm, bm):
    current_user = um.get_current_user()
    print(f"Willkommen, Administrator {current_user.username}")

    while True:
        print("\nAdmin-Menü:")
        print("1. Alle Hotels anzeigen")
        print("2. Logout")
        admin_choice = input("Wählen Sie eine Option: ")

        if admin_choice == '1':
            all_hotels = hm.get_all_hotels()
            if all_hotels:
                display_hotels(all_hotels)

                hotel_selection = int(input("Wählen Sie ein Hotel, um alle Buchungen zu sehen: "))
                selected_hotel = all_hotels[hotel_selection - 1]
                bookings = bm.get_bookings_by_hotel(selected_hotel.id)

                for i, booking in enumerate(bookings, 1):
                    print(f"{i}. {booking}")

                detail_choice = input("Möchten Sie die Details einer Buchung herunterladen? (j/n): ")
                if detail_choice.lower() == 'j':
                    booking_id = int(input("Wählen Sie die Nummer der Buchung: "))
                    selected_booking = bookings[booking_id - 1]
                    bm.download_booking_details(selected_booking)
            else:
                print("Keine Hotels verfügbar.")
        elif admin_choice == '2':
            um.logout()
            break
        else:
            print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")

def handle_registered_user_session(um, bm, sm, user, date_format):
    print(f"Willkommen, {user.firstname} {user.lastname}")

    while True:
        print("\nBenutzer-Menü:")
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
            handle_guest_session(bm, sm, user, date_format)

        elif choice == '3':
            bookings = bm.get_bookings_of(user.id)
            if bookings:
                for i, booking in enumerate(bookings, 1):
                    print(f"{i}. {booking}")

                action = input("Möchten Sie eine Buchung aktualisieren (1) oder stornieren (2)?: ")
                if action == '1':
                    reservation_id = int(input("Wählen Sie die Nummer der Buchung, die Sie aktualisieren möchten: "))
                    selected_booking = bookings[reservation_id - 1]

                    print("1. Startdatum ändern")
                    print("2. Enddatum ändern")
                    print("3. Kommentar ändern")
                    print("4. Buchungsdetails herunterladen")
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
                    elif field_choice == '4':
                        bm.download_booking_details(selected_booking)
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
            um.logout()
            break
        else:
            print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")

if __name__ == '__main__':
    db_file = '../data/test.db'
    db_path = Path(db_file)
    if not db_path.is_file():
        init_db(db_file, generate_example_data=True)

    engine = create_engine(f'sqlite:///{db_file}')
    session = scoped_session(sessionmaker(bind=engine))
    sm = SearchManager(session)
    bm = BookingManager(session)
    um = UserManager(session)
    hm = HotelManager(session)

    user = None
    date_format = '%d.%m.%y'

    print("Willkommen zum Hotelbuchungssystem von Team C!")
    while True:
        print("\nHauptmenü:")
        print("1. Als Gast fortfahren")
        print("2. Anmelden")
        print("3. Beenden")
        choice = input("Wählen Sie eine Option: ")

        if choice == '1':
            guest = bm.create_guest()
            if guest:
                user = guest
                handle_guest_session(bm, sm, user, date_format)
            else:
                print("Fehler bei der Erstellung des Gastes.")

        elif choice == '2':
            um.login_user()
            current_user = um.get_current_user()
            if current_user:
                if um.is_admin(current_user):
                    handle_admin_session(um, hm, bm)
                else:
                    reg_guest = um.get_reg_guest_of(current_user)
                    print(f"Registrierter Gast {reg_guest.firstname} {reg_guest.lastname} angemeldet.")
                    user = reg_guest
                    handle_registered_user_session(um, bm, sm, user, date_format)
        elif choice == '3':
            print("Auf Wiedersehen!")
            break
        else:
            print("Ungültige Auswahl. Bitte versuchen Sie es erneut.")

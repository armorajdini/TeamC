from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select, delete
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

    def get_session(self):
        return self.__session

    def get_bookings_of(self, guest_id: int):
        query_booking = select(Booking).where(Booking.guest_id == guest_id)
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

    def get_all_bookings(self):
        bookings_query = select(Booking)
        bookings = self.__session.execute(bookings_query).scalars().all()
        return bookings

    def get_r_guest(self, id: int):
        guest_query = select(RegisteredGuest).where(RegisteredGuest.id == id)
        guest = self.__session.execute(guest_query).scalars().one_or_none()
        if guest is None:
            print(f"Kein registrierter Gast gefunden mit ID: {id}")
        return guest

    def create_booking(self, room: Room, guest: Guest, number_of_guests: int, start_date: datetime, end_date: datetime,
                       comment: str):
        booking = Booking(room=room, guest=guest, number_of_guests=number_of_guests,
                          start_date=start_date, end_date=end_date, comment=comment)
        self.__session.add(booking)
        self.__session.commit()

    def update_booking(self, booking_id: int, **kwargs):
        booking_query = select(Booking).where(Booking.id == booking_id)
        booking = self.__session.execute(booking_query).scalars().one()
        for key, value in kwargs.items():
            setattr(booking, key, value)
        self.__session.commit()

    def delete_booking(self, booking_id: int, file_path: Path = None):
        if file_path and file_path.exists():
            try:
                file_path.unlink()
                print(f"Gespeicherte Buchungsdetails gelöscht: {file_path}")
            except Exception as e:
                print(f"Fehler beim Löschen der Datei: {e}")

        delete_query = delete(Booking).where(Booking.id == booking_id)
        self.__session.execute(delete_query)
        self.__session.commit()

    def save_booking_details_to_file(self, booking: Booking, file_path: Path):
        try:
            with open(file_path, 'w') as f:
                f.write(f"Booking ID: {booking.id}\n")
                f.write(f"Hotel ID: {booking.room.hotel_id}\n")
                f.write(f"Room Number: {booking.room.room_number}\n")
                f.write(f"Guest ID: {booking.guest_id}\n")
                f.write(f"Number of Guests: {booking.number_of_guests}\n")
                f.write(f"Start Date: {booking.start_date}\n")
                f.write(f"End Date: {booking.end_date}\n")
                f.write(f"Comment: {booking.comment}\n")
            print(f"Buchungsdetails gespeichert unter: {file_path}")
        except Exception as e:
            print(f"Fehler beim Speichern der Datei: {e}")

    def login(self, username: str, password: str):
        login_query = select(Login).where(Login.username == username).where(Login.password == password)
        user = self.__session.execute(login_query).scalars().one_or_none()
        if user is None:
            print(f"Ungültige Anmeldeinformationen für Benutzer: {username}")
        return user


def show_bookings(bookings):
    print("Ihre Buchungen:")
    for i, booking in enumerate(bookings, 1):
        print(f"{i}. {booking}")


def make_booking(bm, guest):
    sm = SearchManager(db_path)
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

        bm.create_booking(selected_room, guest, in_number_of_guests, in_start_date, in_end_date, in_comment)


def manage_booking(bm, bookings, guest):
    show_bookings(bookings)
    selection = int(input("Wählen Sie eine Buchung: "))
    selected_booking = bookings[selection - 1]

    action = input("Was möchten Sie tun? (ändern/stornieren): ").strip().lower()
    if action == 'ändern':
        start_date = input("Neues Startdatum (DD.MM.YY): ")
        end_date = input("Neues Enddatum (DD.MM.YY): ")
        comment = input("Neuer Kommentar: ")

        date_format = '%d.%m.%y'
        start_date = datetime.strptime(start_date, date_format)
        end_date = datetime.strptime(end_date, date_format)

        bm.update_booking(selected_booking.id, start_date=start_date, end_date=end_date, comment=comment)
    elif action == 'stornieren':
        save_path = Path(
            input("Pfad der gespeicherten Buchungsdetails zur Löschung (falls vorhanden, z.B. 'buchung.txt'): "))
        bm.delete_booking(selected_booking.id, save_path)


if __name__ == '__main__':
    db_path = Path("../../data/hotel_reservation.db")
    bm = BookingManager(db_path)

    # User login
    username = input("Benutzername: ")
    password = input("Passwort: ")
    user = bm.login(username, password)

    if user:
        print(f"Willkommen, {user.username}!")

        # Use the correct RegisteredGuest ID for the logged-in user
        session = bm.get_session()
        guest_id_query = select(RegisteredGuest).where(RegisteredGuest.login_id == user.id)
        guest = session.execute(guest_id_query).scalars().one_or_none()

        if guest:
            while True:
                bookings = bm.get_bookings_of(guest.id)
                show_bookings(bookings)

                action = input(
                    "Was möchten Sie tun? (neu buchen, buchungsdetails, verwalten, beenden): ").strip().lower()

                if action == 'neu buchen':
                    make_booking(bm, guest)
                elif action == 'buchungsdetails':
                    show_bookings(bookings)
                    selection = int(input("Wählen Sie eine Buchung: "))
                    selected_booking = bookings[selection - 1]
                    save_path = Path(input("Speicherpfad für Buchungsdetails (z.B. 'buchung.txt'): "))
                    bm.save_booking_details_to_file(selected_booking, save_path)
                elif action == 'verwalten':
                    manage_booking(bm, bookings, guest)
                elif action == 'beenden':
                    print("Auf Wiedersehen!")
                    break
                else:
                    print("Ungültige Aktion, bitte erneut versuchen.")
        else:
            print("Registrierter Gast konnte nicht gefunden werden.")
    else:
        print("Ungültige Anmeldeinformationen")

 # TeamC

1. Vinci Claudio, Cruz Pablo, Ajdini Armor & Nagarajah Kavisan
2. Wir haben die User Stories auf Manager aufgeteilt. SearchManager wurde von Claudio bearbeitet. Booking Manager wurde von Armor bearbeitet. Hotel Manager wurde von Kavisan bearbeitet. UserManager wurde von Pablo bearbeitet.
3. Im nächsten Abschnitt ist die Erklärung bzw. Instruktionen unserer Applikation.

Hotel Manager
Die Klasse HotelManager kümmert sich um die Verwaltung von Hotels. Sie kann Hotels hinzufügen, entfernen und
aktualisieren. Außerdem verwaltet sie die zugehörigen Zimmer und Adressen der Hotels.

Methoden:
__init__(self, db_file: Path): Initialisiert den HotelManager mit der angegebenen Datenbankdatei, sonst wird 
eine neue Datenbank mit Beispieldaten initialisiert.

add_hotel: Wie der Name schon sagt, wird da ein Hotel mit dem angegebenen Namen, Sternen, Adresse und Zimmer
hinzugefügt.

remove_hotel: Entfernt das Hotel mit der angegebenen ID aus der Datenbank

get_all_hotels: Gibt eine Liste aller Hotels in der Datenbank zurück

update_hotel: Aktualisiert den Namen und die Sterne des Hotels mit der angegebenen ID.

update_address: Aktualisiert die Adresse mit der angegebenen ID.

update_room: Aktualisiert die Zimmereinzelheiten mit der angegebenen aktuellen Zimmernummer.

get_rooms_by_hotel_id: Ruft alle Zimmer für das Hotel mit der angegebenen ID ab.

add_hotel_console: Konsolenschnittstelle zum Hinzufügen eines neuen Hotels.

update_hotel_console: Konsolenschnittstelle zum Aktualisieren der Hoteldetails.

remove_hotel_console: Konsolenschnittstelle zum Entfernen eines Hotels.

Konsolenschnittstelle
Die Konsolenschnittstelle bietet Administratoren Optionen zur Verwaltung von Hotels:
1. Hotel hinzufügen
2. Hotel entfernen
3. Hotel / Adresse / Zimmerinformationen aktualisieren
4. Alle Buchungen abrufen

Nur Benutzer mit der Administratorrolle können auf die Funktionen von HotelManger zugreifen.

USER MANAGER

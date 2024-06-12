 # TeamC

1. Vinci Claudio, Cruz Pablo, Ajdini Armor & Nagarajah Kavisan
2. Wir haben die User Stories auf Manager aufgeteilt. SearchManager wurde von Claudio bearbeitet. Booking Manager wurde von Armor bearbeitet. Hotel Manager wurde von Kavisan bearbeitet. UserManager wurde von Pablo bearbeitet.
3. Im nächsten Abschnitt ist die Erklärung bzw. Instruktionen unserer Applikation.

Search Manager 

Der SearchManager verwaltet die Suche nach Hotels , verfügbaren Zimmern und Zimmereinzelheiten. Zusätzlich enthält er Funktionen zur validierung von Benutzereingaben und Datumsformaten.

Methoden:
get_all_cities_with_hotels: Ruft eine Liste von Städten mit Hotels ab.
get_available_rooms: Findet verfügbare Zimmer in einem Hotel für einen bestimmten Zeitraum und die Anzahl der Gäste.
get_available_hotels_by_city_stars_and_guests: Lokalisiert verfügbare Hotels basierend auf Stadt, Sternebewertung und Gästeanzahl.
get_room_details: Holt Details zu verfügbaren Zimmern in einem bestimmten Hotel ab.

Funktionen: 
check_user_input(question, valid): Validieren von Benutzereingaben anhand der bereitgestellten Optionen.
get_date_input(prompt): Validieren und Parsen von Benutzereingaben für ein Datum im Format "TT.MM.JJJJ".

Konsolenschnittstelle:
Erlaubt die Eingabe des Ankunftsdatums, der Aufenthaltsdauer, der Auswahl der Stadt, der Sternebewertung und der Anzahl der Gäste.
Validiert Benutzereingaben für Daten, Anzahl der Tage, Sternebewertung und Gäste.
Zeigt verfügbare Städte mit Hotels an, falls vorhanden.
Verarbeitet die Benutzereingabe zur Suche nach verfügbaren Hotels basierend auf den angegebenen Kriterien.
Anzeige der Suchergebnisse:
Zeigt eine entsprechende Meldung an, wenn keine Hotels für die ausgewählten Kriterien verfügbar sind.
Für jedes verfügbare Hotel:
Gibt den Hotelnamen aus.
Ruft verfügbare Zimmerdetails ab und zeigt sie an, einschließlich Zimmertyp, Nummer, maximale Gäste, Preis pro Nacht, Gesamtkosten und Annehmlichkeiten.


Base Manager

Der BaseManager übernimmt die Verwaltung der Datenbank-Sitzung (_session), die für die Ausführung von Datenbankabfragen
verwendet wird. Abgeleitete Klassen können somit direkt auf die Datenbank zugreifen, 
ohne eigene Sitzungen erstellen zu müssen.

Um zirkuläre Abhängigkeiten zu vermeiden, haben wir den BaseManager implementiert, der grundlegende Datenbankoperationen
bereitstellt und von verschiedenen Manager-Klassen gerbt wird.
Zum Beispiel wird select_all(self, query: Select)
im Hotelmanager verwendet, um alle Ergebnisse als Liste zurückzuerhalten.
Und select_one(self, query: Select)
gibt ein einzelnes Ergebnis zurück. Sie wird im UserManager verwendet, 
um einen spezifischen Benutzer basierend auf Benutzername und Passwort basierend auf dem Login abzurufen.


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

Im UserManager kann man sich anmelden (login_user) oder registrieren (register_user).

Benutzer melden sich mit ihrem Benutzernamen (Emailadresse) und Passwort an.
Die Methode login_user überprüft, ob der Benutzername und das Passwort übereinstimmen.
Wenn die Anmeldeinformationen korrekt sind, wird der Benutzer angemeldet und eine Sitzung gestartet.
Wenn die Anmeldeinformationen nicht korrekt sind, wird eine Fehlermeldung ausgegeben.
Die Methode register_user wird verwendet, um einen neuen Benutzer zu registrieren.

 existing_user_query = select(Login).where(Login.username == username)
            existing_user = self._session.execute(existing_user_query).scalars().one_or_none()
Damit wird überprüft, ob der Benutzername bereits vorhanden ist. 
Wenn der Benutzername noch nicht vorhanden ist, wird der Benutzer registriert und eine Sitzung gestartet.
Man hat 3 Versuche, sich anzumelden, bevor das Programm beendet wird.
(has_attempts_left):
Die Methode get_current_user wird verwendet, um den aktuell angemeldeten Benutzer zurückzugeben.
Überprüfen, ob der angemeldete Benutzer die erforderlichen Rechte hat.
(is_admin): Überprüft, ob der angemeldete Benutzer ein Administrator ist.
Wenn der Benutzer ein Administrator ist, wird True zurückgegeben, andernfalls False.

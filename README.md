# TeamC Hotel-Reservierungssystem

![Logo von TeamC](./data_models/HotelTeamC.png)

## Autoren
1. Vinci Claudio
2. Cruz Pablo
3. Ajdini Armor
4. Nagarajah Kavisan

## Aufgabenverteilung
- **SearchManager:** Claudio
- **Booking Manager:** Armor
- **Hotel Manager:** Kavisan
- **UserManager:** Pablo

## Applikationserklärung

### Search Manager

Der SearchManager verwaltet die Suche nach Hotels, verfügbaren Zimmern und Zimmereinzelheiten. Zusätzlich enthält er Funktionen zur Validierung von Benutzereingaben und Datumsformaten.

#### Methoden
- **get_all_cities_with_hotels:** Ruft eine Liste von Städten mit Hotels ab.
- **get_available_rooms:** Findet verfügbare Zimmer in einem Hotel für einen bestimmten Zeitraum und die Anzahl der Gäste.
- **get_available_hotels_by_city_stars_and_guests:** Lokalisiert verfügbare Hotels basierend auf Stadt, Sternebewertung und Gästeanzahl.
- **get_room_details:** Holt Details zu verfügbaren Zimmern in einem bestimmten Hotel ab.

#### Funktionen
- **check_user_input(question, valid):** Validieren von Benutzereingaben anhand der bereitgestellten Optionen.
- **get_date_input(prompt):** Validieren und Parsen von Benutzereingaben für ein Datum im Format "TT.MM.JJJJ".

#### Konsolenschnittstelle
- Erlaubt die Eingabe des Ankunftsdatums, der Aufenthaltsdauer, der Auswahl der Stadt, der Sternebewertung und der Anzahl der Gäste.
- Validiert Benutzereingaben für Daten, Anzahl der Tage, Sternebewertung und Gäste.
- Zeigt verfügbare Städte mit Hotels an, falls vorhanden.
- Verarbeitet die Benutzereingabe zur Suche nach verfügbaren Hotels basierend auf den angegebenen Kriterien.
- **Anzeige der Suchergebnisse:**
  - Zeigt eine entsprechende Meldung an, wenn keine Hotels für die ausgewählten Kriterien verfügbar sind.
  - Für jedes verfügbare Hotel:
    - Gibt den Hotelnamen aus.
    - Ruft verfügbare Zimmerdetails ab und zeigt sie an, einschließlich Zimmertyp, Nummer, maximale Gäste, Preis pro Nacht, Gesamtkosten und Annehmlichkeiten.

### Base Manager

Der BaseManager übernimmt die Verwaltung der Datenbank-Sitzung (_session), die für die Ausführung von Datenbankabfragen verwendet wird. Abgeleitete Klassen können somit direkt auf die Datenbank zugreifen, ohne eigene Sitzungen erstellen zu müssen.

#### Funktionen
- **select_all(self, query: Select):** Wird im Hotelmanager verwendet, um alle Ergebnisse als Liste zurückzuerhalten.
- **select_one(self, query: Select):** Wird im UserManager verwendet, um einen spezifischen Benutzer basierend auf Benutzername und Passwort basierend auf dem Login abzurufen.

### Hotel Manager

Die Klasse HotelManager kümmert sich um die Verwaltung von Hotels. Sie kann Hotels hinzufügen, entfernen und aktualisieren. Außerdem verwaltet sie die zugehörigen Zimmer und Adressen der Hotels.

#### Methoden
- **__init__(self, db_file: Path):** Initialisiert den HotelManager mit der angegebenen Datenbankdatei, sonst wird eine neue Datenbank mit Beispieldaten initialisiert.
- **add_hotel:** Fügt ein Hotel mit dem angegebenen Namen, Sternen, Adresse und Zimmer hinzu.
- **remove_hotel:** Entfernt das Hotel mit der angegebenen ID aus der Datenbank.
- **get_all_hotels:** Gibt eine Liste aller Hotels in der Datenbank zurück.
- **update_hotel:** Aktualisiert den Namen und die Sterne des Hotels mit der angegebenen ID.
- **update_address:** Aktualisiert die Adresse mit der angegebenen ID.
- **update_room:** Aktualisiert die Zimmereinzelheiten mit der angegebenen aktuellen Zimmernummer.
- **get_rooms_by_hotel_id:** Ruft alle Zimmer für das Hotel mit der angegebenen ID ab.
- **add_hotel_console:** Konsolenschnittstelle zum Hinzufügen eines neuen Hotels.
- **update_hotel_console:** Konsolenschnittstelle zum Aktualisieren der Hoteldetails.
- **remove_hotel_console:** Konsolenschnittstelle zum Entfernen eines Hotels.

#### Konsolenschnittstelle
Die Konsolenschnittstelle bietet Administratoren Optionen zur Verwaltung von Hotels:
1. Hotel hinzufügen
2. Hotel entfernen
3. Hotel / Adresse / Zimmerinformationen aktualisieren
4. Alle Buchungen abrufen

Nur Benutzer mit der Administratorrolle können auf die Funktionen von HotelManager zugreifen.

### User Manager

Im UserManager kann man sich anmelden (login_user) oder registrieren (register_user).

#### Funktionen
- **login_user:** Überprüft, ob der Benutzername und das Passwort übereinstimmen. Wenn die Anmeldeinformationen korrekt sind, wird der Benutzer angemeldet und eine Sitzung gestartet. Bei falschen Anmeldeinformationen wird eine Fehlermeldung ausgegeben.
- **register_user:** Registriert einen neuen Benutzer, nachdem überprüft wurde, ob der Benutzername bereits vorhanden ist.
- **get_current_user:** Gibt den aktuell angemeldeten Benutzer zurück.
- **is_admin:** Überprüft, ob der angemeldete Benutzer ein Administrator ist.

### Booking Manager

#### Hauptanwendung
Der Einstiegspunkt der Anwendung befindet sich im Block `if __name__ == '__main__':`, der die Datenbank initialisiert und die Hauptmenüschleife startet.
- **Datenbankinitialisierung:** Überprüft, ob die Datenbankdatei existiert, und initialisiert sie mit Beispieldaten, falls nicht.
- **Engine- und Sitzungserstellung:** Richtet die SQLAlchemy-Engine und -Sitzung für die Datenbankinteraktion ein.
- **Manager-Instanzen:** Erstellt Instanzen von SearchManager, BookingManager, UserManager und HotelManager.

#### BookingManager-Klasse
Der BookingManager erweitert BaseManager und bietet Methoden zur Verwaltung von Buchungen:
- **get_bookings_of(guest_id):** Ruft Buchungen für einen bestimmten Gast ab.
- **create_booking:** Erstellt eine neue Buchung.
- **get_available_rooms:** Ruft verfügbare Zimmer in einem Hotel für einen bestimmten Zeitraum und eine bestimmte Gästeanzahl ab.
- **get_all_bookings:** Ruft alle Buchungen ab.
- **get_bookings_by_hotel:** Ruft Buchungen für ein bestimmtes Hotel ab.
- **get_guest(id):** Ruft Gastdetails anhand der ID ab.
- **create_guest:** Fordert den Benutzer auf, Gastdetails einzugeben und erstellt einen neuen Gast.
- **update_booking:** Aktualisiert die Details einer Buchung.
- **delete_booking:** Löscht eine Buchung.
- **update_room_availability:** Aktualisiert den Verfügbarkeitsstatus eines Zimmers.
- **update_room_price:** Aktualisiert den Preis eines Zimmers.
- **download_booking_details:** Lädt Buchungsdetails in eine Textdatei herunter.

#### Benutzerinteraktionsfunktionen
- **display_hotels:** Zeigt eine Liste verfügbarer Hotels an.
- **display_rooms:** Zeigt eine Liste verfügbarer Zimmer an.
- **handle_guest_session:** Verwaltet die Sitzung für einen Gast und ermöglicht ihm, neue Buchungen zu erstellen.
- **handle_admin_session:** Verwaltet die Sitzung für einen Administrator und ermöglicht ihm, Hotels und Buchungen zu verwalten.
- **handle_registered_user_session:** Verwaltet die Sitzung für einen registrierten Benutzer und ermöglicht ihm, seine Buchungen anzusehen und zu verwalten.

#### Hauptmenüschleife
Das Hauptmenü bietet Optionen, als Gast fortzufahren, sich anzumelden oder die Anwendung zu beenden. Je nach Auswahl des Benutzers wird zur entsprechenden Sitzungsverwaltungsfunktion navigiert.

#### Logging
Das System verwendet das Python-logging-Modul, um Informationen und Fehler zu protokollieren, was die Verfolgung und Fehlerbehebung des Anwendungsverhaltens erleichtert.

### Ausführen der Anwendung
1. Stellen Sie sicher, dass alle Abhängigkeiten installiert sind (SQLAlchemy, usw.).
2. Führen Sie das Hauptskript mit Python aus.
3. Folgen Sie den Anweisungen auf dem Bildschirm, um durch das System zu navigieren.

### Abhängigkeiten
- Python 3.x
- SQLAlchemy
- Weitere notwendige Module (pathlib, datetime, usw.)
- 

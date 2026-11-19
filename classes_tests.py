import random
from datetime import datetime, time
from abc import ABC, abstractmethod
import sqlite3
from datetime import date

#definuju název databáze, kterou pak vytvořím a používám v jednotlivých třídách
DB_NAME = "events_app.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
#vytváří tabulku- první argument je sloupec, pak dat typ a nakonec případná omezení
#např omezení PRIMARY KEY zaručuje unikátnost tohoto parametru a to že musí být vyplněn, not null říká !=prázdná hodnota
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (    
            event_id INTEGER PRIMARY KEY,        
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            organizer TEXT NOT NULL,
            is_alcohol BOOLEAN NOT NULL
        )
    ''')
#tahle tabulka vytváří vazbu event<->uživatel
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS participants (        
            event_id INTEGER,
            username TEXT,
            FOREIGN KEY(event_id) REFERENCES events(event_id),
            PRIMARY KEY(event_id, username))
            ''')
    conn.commit()
    conn.close()

            

class Event:
    def __init__(self, event_id: int, title: str, category: str, date: str, start_time: str, end_time: str, capacity: int, organizer: str, is_alcohol: bool = False):
        self.event_id = event_id
        self.title = title
        self.category = category
        self.date = datetime.strptime(date, "%Y %m %d").date()    #datetime.strptime dostane input v nějakém pořadí s nějakým oddělovačem (definováno v závorce a nutno dodržet)
        self.start_time = datetime.strptime(start_time, "%H:%M").time() 
        self.end_time = datetime.strptime(end_time, "%H:%M").time()
        self.capacity = capacity
        self.organizer = organizer
        self.is_alcohol = is_alcohol

    @property
    def participants(self) ->list[str]:
        conn = sqlite3.connect(DB_NAME)    #vytvoří spojení s databází
        cursor = conn.cursor()    #pomocník pro exekuci příkazů v databázi
        cursor.execute("SELECT username FROM participants WHERE event_id = ?", (self.event_id,)) #spojení s databází SQL a výběr username pro odpovídající event_id
        rows = cursor.fetchall()        #vytáhne všechny řádky z předchozího kroku (sqlite se chová tak, že vrací sadu tuples)
        conn.close()
        return [row[0] for row in rows]    #z každého tuple přečte první prvek- tedy username

    def is_full(self) -> bool:
        return len(self.participants) >= self.capacity  #je kvůli bezpečnosti (např kdyby se změnila kapacita na počet menší než je přihlášených, = by vracelo false, a program by dál prohluboval chybu)

    def add_participant(self, username: str) -> bool:
        if not self.is_full() and username not in self.participants:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()       

            cursor.execute("INSERT OR IGNORE INTO participants (event_id, username) VALUES (?, ?)", (self.event_id, username)) #vytvářím místo pro doplnění hodnot, přičemž hodnoty musí být ze seznamu v závorce za stringem- prevence sql injection

            conn.commit()
            conn.close()
            return True
        return False

            
           

    def remove_participant(self, username: str) -> bool:
        if username in self.participants:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM participants WHERE event_id = ? AND username = ?", (self.event_id, username))
            conn.commit()
            conn.close()
            return True
        return False

    def __repr__(self):
        date_str = self.date.strftime("%d.%m. %Y")  
        start_str = self.start_time.strftime("%H:%M")
        end_str = self.end_time.strftime("%H:%M")
        return f"Event('{self.title}', {date_str} {start_str} - {end_str}, Volno: {self.capacity - len(self.participants)})"



class User(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def can_manage_events(self) -> bool:    #je tam pass, ale proto, že to je dekorováno, dědící třídy se musí vyjádřit
        pass

    @abstractmethod
    def perform_admin_action(self, action_desc: str):  
        pass

    def filter_events(self, events: list[Event]) -> list[Event]:    #toto některé z dědících tříd přepíšou a zavedou si filtr a už neuvidí vše
        return events

class AndySabotageException(Exception):  
    pass

class AdminUser(User):
    def can_manage_events(self) -> bool:
        return True

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

    def perform_admin_action(self, action_desc: str):
        return f"[ADMIN] Úspěšně provedeno: {action_desc}"

class SabotagedAdminUser(User):
    def can_manage_events(self) -> bool:
        return True  

    def perform_admin_action(self, action_desc: str):
        errors = [
            "Chyba: SAMOZŘEJMĚ JSI ADMIN ALE...Server raději předstíral pád, než aby tohle uložil.",
            "SAMOZŘEJMĚ JSI ADMIN ALE...Systém vyhodnotil tvůj požadavek jako otravný a smazal ho.",
            "SAMOZŘEJMĚ JSI ADMIN ALE...Chviličku, systém si musí odpočinout",
            "SAMOZŘEJMĚ SI ADMIN ALE...požadavek se ani tak nezpracoval. Třeba někdy příště"
        ]
        raise AndySabotageException(random.choice(errors))

class AlcoholIntolerantUser(User):
    def can_manage_events(self) -> bool:
        return False

    def perform_admin_action(self, action_desc: str):
        raise PermissionError("Pro tuto akci jsou vyžadována administrátorská práva!")

    def filter_events(self, events: list[Event]) -> list[Event]:
        return [e for e in events if not e.is_alcohol]

class EarlyBirdUser(User):
    def __init__(self, name: str, max_hour: str = "18:25"):    #pokud není přepsáno jiným max hour při tvorbě instance, bude tam default
        super().__init__(name)    #potřebuju do init narvat ještě parametr navíc (max hour)- pokud bych to udělal normálně, přepíšu ten zděděný konstruktor. Super() přepsání zabrání
        self.max_hour = datetime.strptime(max_hour, "%H:%M").time()

    def can_manage_events(self) -> bool:
        return False

    def perform_admin_action(self, action_desc: str):
        raise PermissionError("Pro tuto akci jsou vyžadována administrátorská práva!")

    def filter_events(self, events: list[Event]) -> list[Event]:
        return [e for e in events if e.end_time <= self.max_hour]

class EventManager:
    def __init__(self):

        init_db()
        self.seed_initial_data() #příprava databáze a naplnění výchozími daty
        
        self.users = {
            "Eda": AdminUser("Eda"),
            "Andy": SabotagedAdminUser("Andy"),
            "Zuzka": AlcoholIntolerantUser("Zuzka"),
            "Evžen": EarlyBirdUser("Evžen"),
        }
        self.load_events()

    def seed_initial_data(self):

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events")    #spočítá počet řádků v tabulce

        if cursor.fetchone()[0] == 0:    #pokud je počet řádků nula, vlož initial_events, cursor si pamatuje svůj aktuální stav a fetchone tu hodnotu volá
            initial_events = [
                (1, "Ranní běh", "Sport", "2026 11 28", "6:30", "7:15", 9, "Eda", 0),
                (2, "Python", "Vzdělávání", "2026 12 24", "18:00", "20:00", 2, "Eda", 0),
                (3, "Věže", "Zábava", "2027 7 5", "8:00", "18:00", 4, "Eda", 1),
                (4, "Frisbee", "Zábava", "2026 12 31", "18:00", "23:59", 10, "Eda", 0)
            ]
            cursor.executemany("INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", initial_events)    #vložení matic akcí
            conn.commit()
        conn.close()

    def load_events(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT event_id, title, category, date, start_time, end_time, capacity, organizer, is_alcohol FROM events")
        rows = cursor.fetchall()    #uložení předchozího řádku do proměnné rows
        conn.close()
        
        self.events = []    #vytvoření prázdného seznamu pro for cyklus
        for row in rows:        
            self.events.append(Event(
                event_id=row[0],
                title=row[1],
                category=row[2],
                date=row[3],
                start_time=row[4],
                end_time=row[5],
                capacity=row[6],
                organizer=row[7],
                is_alcohol=bool(row[8])  
            ))

        
        
    def get_user(self, name: str) -> User:
        return self.users.get(name)

    def delete_event(self, event_id: int):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM participants WHERE event_id = ?", (event_id,))    #smaže přihlášené

        cursor.execute("DELETE FROM events WHERE event_id = ?", (event_id,))        #smaže akci
        conn.commit()
        conn.close()
        self.load_events()

    def update_event(self, event_id: int, title:str, category:str, date: str, start_time: str, end_time: str, capacity: int, organizer: str, is_alcohol: bool):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE events 
               SET title = ?, category = ?, date = ?, start_time = ?, end_time = ?, capacity = ?, organizer = ?, is_alcohol = ?
               WHERE event_id = ?""",
            (title, category, date, start_time, end_time, capacity, organizer, int(is_alcohol), event_id)
        )
        conn.commit()
        conn.close()
        self.load_events()

    def add_user(self, name: str, user_type: str, extra_param: str = None):

        if user_type == "Admin":
            self.users[name] = AdminUser(name)
        elif user_type == "Andy":
            self.users[name] = SabotagedAdminUser(name)
        elif user_type == "abstinent":
            self.users[name] = AlcoholIntolerantUser(name)
        elif user_type == "Early Bird":
            max_h = extra_param if extra_param else "18:25"
            self.users[name] = EarlyBirdUser(name, max_h)

    def remove_user(self, name: str):
        if name in self.users:
            del self.users[name]

    def add_event(self, title: str, category: str, date: str, start_time: str, end_time: str, capacity: int, organizer: str, is_alcohol: bool = False):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        
        cursor.execute("SELECT MAX(event_id) FROM events")    #maximální ID aby šlo přidat další akci
        max_id = cursor.fetchone()[0]    #z předchozího řádku uloží první prvky (=event ID)
        new_id = 1 if max_id is None else max_id + 1
        
        cursor.execute(
            "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (new_id, title, category, date, start_time, end_time, capacity, organizer, int(is_alcohol))
        )
        conn.commit()
        conn.close()
        
        self.load_events()
        return self.events[-1]    #poslední prvek v případě, že bych chtěl s poslední vloženou pracovat


#TESTY
import pytest

def test_event_init_test():  #vytvoření instance
        conn = sqlite3.connect(DB_NAME)
        conn.cursor().execute("DELETE FROM participants")
        conn.commit()
        conn.close()
        event = Event(
            event_id = 1,
            title = "test",
            category = "test_cat",
            date = "2026 06 15",
            start_time = "10:00",
            end_time= "11:00",
            capacity= 5,
            organizer= "Eda"
        )

        assert event.title == "test"    #porovnávání event.title instance se stringem totožnýmm při tvorbě instance
        assert event.start_time == time(10, 0)  #obdobně jako event.title i tady se ptáme na shodu
        assert event.end_time == time(11,0)
        assert event.event_id == 1
        assert event.category == "test_cat"
        assert event.date == date(2026, 6, 15)
        assert event.capacity == 5
        assert event.organizer == "Eda"

def test_event_participants():
        init_db()
        conn = sqlite3.connect(DB_NAME)
        conn.cursor().execute("DELETE FROM participants")  #vymazání databáze, aby byla ta inicializační
        conn.commit()
        conn.close()
        event = Event(
                    event_id = 1,
                    title = "test",
                    category = "test_cat",
                    date = "2026 06 15",
                    start_time = "10:00",
                    end_time= "11:00",
                    capacity= 2,
                    organizer= "Eda"
                )
        assert event.capacity == 2
        event.add_participant("Eda")
        assert len(event.participants) == 1
        event.add_participant("Andy")
        assert event.is_full() == True
        assert sorted(event.participants) == ["Andy", "Eda"]  #sorted poskládá dle abecedy
        event.remove_participant("Eda")
        assert event.participants == ["Andy"]

def test_users():
        admin = AdminUser("test_admin")
        sabotaged_admin = SabotagedAdminUser("sabotaged_admin_test")
        alcoholintolerant_user = AlcoholIntolerantUser("alcoholintolerant_user_test")

        assert admin.can_manage_events() == True
        assert admin.perform_admin_action("admin_action") == ("[ADMIN] Úspěšně provedeno: admin_action")
        assert sabotaged_admin.can_manage_events() == True
        with pytest.raises(AndySabotageException):
            sabotaged_admin.perform_admin_action("admin_action")   #touto strukturou říkáme, že by měla vypadnout chyba a test tedy projde, když se tak stane
        with pytest.raises(PermissionError):
            alcoholintolerant_user.perform_admin_action("admin_action")
        assert alcoholintolerant_user.can_manage_events() == False

def test_event_manager():
        test = EventManager()

        assert len(test.events) == 4
        new_event = test.add_event("test", "test_category","2000 1 1", "0:00", "23:59", 1, "Eda", False)
        assert len(test.events) == 5
        assert new_event.event_id == 5
        assert new_event.title == "test"

        test.delete_event(new_event.event_id)
        assert len(test.events) == 4

def test_early_bird():
    test_early_bird = EarlyBirdUser("test", "15:00")
    assert test_early_bird.max_hour == time(15,0)
    test_default_early_bird = EarlyBirdUser("test2")
    assert test_default_early_bird.max_hour == time(18, 25)

    event = Event(
                event_id = 1,
                title = "test",
                category = "test_cat",
                date = "2026 06 15",
                start_time = "10:00",
                end_time= "17:00",
                capacity= 5,
                organizer= "Eda"
            )
    assert test_default_early_bird.filter_events([event]) == [event]
    assert test_early_bird.filter_events([event]) == []

def test_alcohol_intolerant():
    test_alcohol_intolerant = AlcoholIntolerantUser("test")

    event = Event(
                    event_id = 1,
                    title = "test",
                    category = "test_cat",
                    date = "2026 06 15",
                    start_time = "10:00",
                    end_time= "17:00",
                    capacity= 5,
                    organizer= "Eda",
                    is_alcohol= True
                )
    assert test_alcohol_intolerant.filter_events([event]) == []

    event2 = Event(
                    event_id = 1,
                    title = "test",
                    category = "test_cat",
                    date = "2026 06 15",
                    start_time = "10:00",
                    end_time= "17:00",
                    capacity= 5,
                    organizer= "Eda",
                    is_alcohol= False
                    )
    assert test_alcohol_intolerant.filter_events([event, event2]) == [event2]

def test_update_event():
    conn = sqlite3.connect(DB_NAME)
    conn.cursor().execute("DELETE FROM participants")
    conn.cursor().execute("DELETE FROM events")
    conn.commit()
    conn.close()
    manager = EventManager()
    assert manager.events[0].title == "Ranní běh"
    manager.update_event(1, "Ranní spěch", "Sport", "2026 11 28", "6:30", "7:15", 9, "Eda", False)
    assert manager.events[0].title == "Ranní spěch"

def test_remove_participant():
    conn = sqlite3.connect(DB_NAME)
    conn.cursor().execute("DELETE FROM participants")
    conn.cursor().execute("DELETE FROM events")
    conn.commit()
    conn.close()
    manager = EventManager()
    event = manager.events[0]
    assert event.remove_participant("abcd") is False  #tj nepovedlo se odstranit účastníka, protože tam nebyl

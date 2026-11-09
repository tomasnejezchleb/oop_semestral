import random
from datetime import datetime, time
from abc import ABC, abstractmethod

class Event:
    def __init__(self, event_id: int, title: str, category: str, date: str, start_time: str, end_time: str, capacity: int, organizer: str, is_alcohol: bool = False):
        self.event_id = event_id
        self.title = title
        self.category = category
        self.date = datetime.strptime(date, "%Y %m %d").date()
        self.start_time = datetime.strptime(start_time, "%H:%M").time()
        self.end_time = datetime.strptime(end_time, "%H:%M").time()
        self.capacity = capacity
        self.organizer = organizer
        self.is_alcohol = is_alcohol
        self.participants = []  

    def is_full(self) -> bool:
        return len(self.participants) >= self.capacity  

    def add_participant(self, username: str) -> bool:
        if not self.is_full() and username not in self.participants:
            self.participants.append(username)
            return True
        return False

    def remove_participant(self, username: str) -> bool:
        if username in self.participants:
            self.participants.remove(username)
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
    def can_manage_events(self) -> bool:
        pass

    @abstractmethod
    def perform_admin_action(self, action_desc: str):
        pass

    def filter_events(self, events: list[Event]) -> list[Event]:
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
            "Chyba: Server raději předstíral pád, než aby tohle uložil.",
            "Systém vyhodnotil tvůj požadavek jako otravný a smazal ho.",
            "Chviličku, systém si musí odpočinout",
            "Chyba: požadavek se nezpracoval. Třeba někdy příště"
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
    def __init__(self, name: str, max_hour: str = "18:25"):
        super().__init__(name)
        self.max_hour = datetime.strptime(max_hour, "%H:%M").time()

    def can_manage_events(self) -> bool:
        return False

    def perform_admin_action(self, action_desc: str):
        raise PermissionError("Pro tuto akci jsou vyžadována administrátorská práva!")

    def filter_events(self, events: list[Event]) -> list[Event]:
        return [e for e in events if e.end_time <= self.max_hour]

class EventManager:
    def __init__(self):
        self.users = {
            "Eda": AdminUser("Eda"),
            "Andy": SabotagedAdminUser("Andy"),
            "Zuzka": AlcoholIntolerantUser("Zuzka"),
            "Evžen": EarlyBirdUser("Evžen"),
        }
        # Opravené datum a správné pořadí argumentů u Frisbee (kapacita 10, organizer Eda)
        self.events = [
            Event(1, "Ranní běh", "Sport", "2026 11 28", "6:30", "7:15", 9, "Eda", is_alcohol=False),
            Event(2, "Python", "Vzdělávání", "2026 12 24", "18:00", "20:00", 2, "Eda", is_alcohol=False),
            Event(3, "Věže", "Zábava", "2027 7 5", "8:00", "18:00", 4, "Eda", is_alcohol=True),
            Event(4, "Frisbee", "Zábava", "2026 12 31", "18:00", "23:59", 10, "Eda", is_alcohol=False)
        ]

    def get_user(self, name: str) -> User:
        return self.users.get(name)

    def add_event(self, title: str, category: str, date: str, start_time: str, end_time: str, capacity: int, organizer: str, is_alcohol: bool = False):
        new_id = len(self.events) + 1
        event = Event(new_id, title, category, date, start_time, end_time, capacity, organizer, is_alcohol)
        self.events.append(event)
        return event



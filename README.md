# Vývoj tříd

Větev `classes_development` obsahuje návrh a implementaci tříd a správy dat.

## Hlavní komponenty

- **`Event`:** reprezentace události, kapacita, správa seznamu účastníků.
- **`EventManager`:** správa událostí a uživatelů, perzistence do SQLite (`events_app.db`), načítání a aktualizace stavu.
- **Uživatelské třídy:** role, oprávnění a filtrování událostí (např. `EarlyBirdUser`, `AlcoholIntolerantUser`, admin třídy).

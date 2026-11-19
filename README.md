# Správa akcí a uživatelů (Streamlit)

Webová aplikace postavená na Streamlit a SQLite pro správu akcí, registraci účastníků, práci s kapacitami a řízení přístupu podle uživatelských rolí.

## Instalace a spuštění

```bash
pip install -r requirements.txt
streamlit run app.py
```

Aplikace běží lokálně  a při prvním spuštění automaticky inicializuje SQLite databázi (`DB_NAME` v `classes.py`).

## Funkce a role uživatelů

- **Přihlašování a odhlašování:** Uživatelé se mohou registrovat na dostupné akce, odhlašovat se z nich a sledovat zbývající kapacitu.
- **Admin panel:** Správa akcí (tvorba, úprava) a uživatelů.
- **Role:**
  - `AdminUser` (Eda) – plný přístup včetně admin panelu.
  - `SabotagedAdminUser` (Andy) – vidí admin panel, ale operace selžou s `AndySabotageException` (ošetřenou chybovou hláškou bez pádu aplikace).
  - `AlcoholIntolerantUser` (Zuzka) – filtruje akce s alkoholem, nemá přístup do admin panelu.
  - `EarlyBirdUser` (Evžen) – filtruje akce podle časového limitu, nemá přístup do admin panelu.

## Struktura projektu

- `app.py` – uživatelské rozhraní ve Streamlit
- `classes.py` – doménová logika, role, výjimky a práce s databází
- `test_interface.py` – automatizované UI testy (`pytest` + `AppTest`)
- `classes_tests.py` - testy classes.py
- `requirements.txt` – seznam závislostí

## Testování classes

Obsahuje testy pro `Event`, `EventManager`, uživatelské třídy (`AdminUser`, `SabotagedAdminUser`, `AlcoholIntolerantUser`, `EarlyBirdUser`) a ukládání do SQLite (`events_app.db`).

### Spuštění testů

```bash
pip install pytest
python -m pytest classes_tests.py
```

## Testování rozhraní

### 1. Ruční testování

- **Správa databáze a přepínání rolí:** Ověřen reset databáze v bočním panelu a chování rolí (`AdminUser`, `SabotagedAdminUser`, `AlcoholIntolerantUser`, `EarlyBirdUser`).
- **Přihlašování, odhlašování a kapacity:** Ověřena změna volné kapacity, přesun akcí mezi dostupnými a přihlášenými, stav `Kapacita vyčerpána` a přehled účastníků v admin panelu.
- **Kontrola ošetření chyb:** Ověřena minimální kapacita `1` (`min_value=1`), kontrola duplicity jmen bez ohledu na velikost písmen (`.lower()`) a zobrazení chybových hlášek (`st.error`) místo tracebacku při chybném formátu data nebo času.

### 2. Automatizované testování

- **Izolované prostředí (`test_interface.py`):** Funkce `start_app(tmp_path, monkeypatch)` přesměruje `classes.DB_NAME` do dočasné databáze v `tmp_path` a spustí aplikaci přes `streamlit.testing.v1.AppTest`.
- **Pokryté scénáře (`pytest`):**
  - `test_zuzka_and_eda_admin_panel`: ověří viditelnost záložek admin panelu podle role (`Zuzka` → `0`, `Eda` → `3`).
  - `test_sabotaged_admin_blocks_actions`: ověří chybovou hlášku v `at.sidebar.error` u role `Andy`.
  - `test_case_insensitive_duplicate_user`: ověří odmítnutí duplicitního uživatele `"eda"` při existenci `"Eda"`.
  - `test_invalid_date`: ověří hlášku `"Neplatný formát data"` při zadání neplatného data (`"dneska"`).
- **Spuštění testů:**

```bash
pytest test_interface.py
```

## Poznámky a omezení

- Databázové soubory (`.db`) nejsou verzovány v repozitáři; při testování se používá dočasná databáze, při ostrém běhu se vytvoří nová.
- Datum při tvorbě akce vyžaduje očekávaný formát (např. `Year Month Day`), jinak aplikace vypíše validační chybu.

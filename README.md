## Testování rozhraní

### 1. Ruční testování

* **Správa databáze a přepínání rolí:** Ověřen reset databáze tlačítkem v bočním panelu a chování různých rolí – `AdminUser` (Eda) má plný přístup včetně správy akcí a uživatelů, `SabotagedAdminUser` (Andy) vidí admin panel, ale operace bezpečně selžou s chybovou hláškou (`AndySabotageException`) bez pádu aplikace, `AlcoholIntolerantUser` (Zuzka) filtruje akce s alkoholem a nemá přístup do admin panelu, `EarlyBirdUser` (Evžen) filtruje akce podle časového limitu.
* **Přihlašování, odhlašování a kapacity:** Ověřeno snižování a zvyšování volné kapacity při přihlašování a odhlašování, přesun mezi dostupnými a přihlášenými akcemi, zobrazení stavu `Kapacita vyčerpána` i viditelnost přihlášených účastníků v admin panelu.
* **Kontrola ošetření chyb:** Ověřeno omezení minimální kapacity na hodnotu `1` (`min_value=1`), kontrola duplicity jmen uživatelů bez ohledu na velikost písmen (`.lower()`) a zobrazení srozumitelné chybové hlášky (`st.error`) místo systémového tracebacku při zadání neplatného formátu data nebo času u tvorby i úpravy akce.

### 2. Automatizované testování


* Pokrytí scénářů: přepínání uživatelů a rolí, chování SabotagedAdminUser při pokusu o akci, odmítnutí duplicitního jména s jinou velikostí písmen a ošetření neplatného formátu data.

```bash
pytest test_interface.py

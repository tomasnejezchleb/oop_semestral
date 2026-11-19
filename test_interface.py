from pathlib import Path
from streamlit.testing.v1 import AppTest
import classes

def start_app(tmp_path, monkeypatch):
    test_db = tmp_path/ "test_events.db"    #cesta k dočasné databázi uvnitř složky tmp_path

    monkeypatch.setattr(classes, "DB_NAME", str(test_db))   #přesměruju DB_NAME na dočasnou databázi

    app_path = str(Path(__file__).resolve().parent / "app.py")  #abs cesta k app.py

    at = AppTest.from_file(app_path).run()  #spučtění aplikace pomocí apptest
    assert not at.exception #kontrola ok startu
    return at

def test_zuzka_and_eda_admin_panel(tmp_path, monkeypatch):
    at = start_app(tmp_path, monkeypatch)

    
    at.sidebar.selectbox[0].select("Zuzka").run()
    assert not at.exception
    
    assert len(at.tabs) == 0    #nemá záložky admin panelu

    at.sidebar.selectbox[0].select("Eda").run()
    assert not at.exception
    assert len(at.tabs) == 3    #vidí 3 záložky na admin panelu

def test_sabotaged_admin_blocks_actions(tmp_path, monkeypatch):
    at = start_app(tmp_path, monkeypatch)

    at.sidebar.selectbox[0].select("Andy").run()
    assert not at.exception
    assert len(at.tabs) == 3
    at.sidebar.button[1].click().run()
    assert not at.exception     #tj že nespadla aplikace
    assert len(at.sidebar.error) > 0    #v bočním panelu se objeví nenulový počet chybových hlášek

def test_case_insensitive_duplicate_user(tmp_path, monkeypatch):
    at = start_app(tmp_path, monkeypatch)
    name_inputs = [ti for ti in at.text_input if ti.label == "Jméno uživatele"]     #textové okno pro username
    create_buttons = [b for b in at.button if b.label == "Vytvořit uživatele"]      #potvrzující tlačítko

    name_inputs[0].input("eda").run()   #eda == Eda ?
    create_buttons[0].click().run()
    assert not at.exception
    assert any("již existuje" in err.value for err in at.error)

def test_invalid_date(tmp_path, monkeypatch):
    at = start_app(tmp_path, monkeypatch)
    title_inputs = [ti for ti in at.text_input if ti.label == "Název"]
    cat_inputs = [ti for ti in at.text_input if ti.label == "Kategorie"]
    date_inputs = [ti for ti in at.text_input if ti.label == "Datum: Year Month Day"]
    submit_buttons = [b for b in at.button if b.label == "Vytvořit akci"]

    title_inputs[-1].input("Chybná akce").run()
    cat_inputs[-1].input("Test").run()
    date_inputs[-1].input("dneska").run()   #neplatný formát data
    submit_buttons[-1].click().run()

    assert not at.exception
    assert any("Neplatný formát data" in err.value for err in at.error)

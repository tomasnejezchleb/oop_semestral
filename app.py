import streamlit as st
from classes import EventManager, AndySabotageException
from classes import Event, AdminUser, SabotagedAdminUser, AlcoholIntolerantUser, EarlyBirdUser


# Inicializace managera v session state. Podmínka, aby se po každé akci neinicializoval znovu
if "manager" not in st.session_state:
    st.session_state.manager = EventManager()

manager = st.session_state.manager

import os

# Tlačítko pro vyčištění databáze v bočním panelu
if st.sidebar.button("Resetovat databázi"):
    if os.path.exists("events_app.db"):
        os.remove("events_app.db")    #existuje soubor s databází? if true, smaže ho
    # Vymaže a vytvoří nového s čistou DB
    if "manager" in st.session_state:
        del st.session_state.manager    #existuje instance EventManagera (manager)? If true, smaže ho
    st.success("Databáze byla resetována")
    st.rerun()

# Výběr aktuálního uživatele v bočním panelu (Sidebar)
user_names = list(manager.users.keys())
selected_user_name = st.sidebar.selectbox("Přihlásit se jako:", user_names)
current_user = manager.get_user(selected_user_name)

st.sidebar.write(f"**Role:** {type(current_user).__name__}")
st.sidebar.write(f"**Může spravovat:** {current_user.can_manage_events()}")

st.sidebar.divider()
st.sidebar.subheader("Test")
if st.sidebar.button("Provést administrátorskou akci"):
    try:
        vysledek = current_user.perform_admin_action("úprava")
        st.sidebar.success(vysledek)
    except AndySabotageException as e:
        st.sidebar.error(str(e))
    except Exception as e:
        st.sidebar.error(str(e))

# Hlavní stránka – ukázka filtrování akcí pro vybraného uživatele
st.header(f"Vítej, {current_user.name}!")
filtr_dle_usera = current_user.filter_events(manager.events)
dostupne_akce = [a for a in filtr_dle_usera if current_user.name not in a.participants]    #filtr + nezobrazení již přihlášených akcí

st.subheader("Dostupné akce:")

for akce in dostupne_akce:
    date_str = akce.date.strftime("%d. %m. %Y")
    start_str = akce.start_time.strftime("%H:%M")
    end_str = akce.end_time.strftime("%H:%M")
  
    volno = akce.capacity - len(akce.participants)
    
    if volno > 0:
        kapacita_html = f"<span style= 'color: green; font-weight: bold;'>Kapacita {volno}</span>"
    else:
        kapacita_html = f"<span style= 'color: red; font-weight: bold;'>Kapacita vyčerpána</span>"


    col1, col2 = st.columns([3, 1])    #poměr šířky sloupců

    with col1:
        st.markdown(
            f"**{akce.title}**    *{akce.category}*    {date_str}    {start_str} - {end_str}    {kapacita_html}",
            unsafe_allow_html=True)

    with col2:
        
        if st.button("Přihlásit", key = f"prihlas_{akce.event_id}"):
                uspech = akce. add_participant(current_user.name)
                if uspech:
                    st.success("Jsi přihlášen")
                    st.rerun()
                else:
                    st.error("Akce je plná nebo error")

st.divider()

st.subheader("Přihlášené akce:")

moje_akce = [a for a in manager.events if current_user.name in a.participants]    #for cyklem projede akce a testuje shodu current_user a prvky participants

if not moje_akce:    #testuje prázdnost seznamu
    st.info("Žádné přihlášené akce")
else:
    for akce in moje_akce:
        date_str = akce.date.strftime("%d. %m. %Y")
        start_str = akce.start_time.strftime("%H:%M")
        end_str = akce.end_time.strftime("%H:%M")
        
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{akce.title}**    *{akce.category}*    {date_str}    {start_str} - {end_str}", unsafe_allow_html=True)

        with col2:
            if st.button("Odhlásit", key = f"odhlas_{akce.event_id}"):
                akce.remove_participant(current_user.name)
                st.success(f"Byl jsi odhlášen z akce {akce.title}")
                st.rerun()

if current_user.can_manage_events():
    st.divider()
    st.header("administrátorský panel")

    tab_akce, tab_nova_akce, tab_uzivatele = st.tabs(["Správa akcí", "Přidat akci", "Správa uživatelů"])    #vytvoření tlačítek

    with tab_akce:
        st.subheader("Seznam akcí")
        for akce in manager.events:
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{akce.title}** ({akce.date.strftime('%d.%m.%Y')})")

                if akce.participants and current_user.can_manage_events():
                    ucastnici_str = ", ".join(akce.participants)
                    st.caption(f"Přihlášeni: {ucastnici_str}")
                else:
                    pass
            with col2:
                if st.button('Smazat', key=f"admin_del_{akce.event_id}"):
                    try:
                        current_user.perform_admin_action(f"Smazání akce{akce.title}")
                        manager.delete_event(akce.event_id)
                        st.success("Smazáno")
                        st.rerun()
                    except AndySabotageException as e:
                        st.error(str(e))

            
            with st.expander(f"Upravit: {akce.title}"):
                with st.form(key=f"edit_form_{akce.event_id}"):
                    
                    new_title = st.text_input("Název", value=akce.title)
                    new_cat = st.text_input("Kategorie", value=akce.category)
                    new_date = st.text_input("Datum: Year Month Day", value=akce.date.strftime("%Y %m %d"))
                    new_start = st.text_input("Začátek (HH:MM)", value=akce.start_time.strftime("%H:%M"))
                    new_end = st.text_input("Konec (HH:MM)", value=akce.end_time.strftime("%H:%M"))
                    new_cap = st.number_input("Kapacita", value=akce.capacity)
                    new_org = st.text_input("Organizátor", value=akce.organizer)
                    new_alk = st.checkbox("Alkohol True?", value=akce.is_alcohol)
                    
                    if st.form_submit_button("Uložit změny"):
                        if new_title and new_cat and new_date and new_start and new_end and new_cap and new_org:
                            try:
                               current_user.perform_admin_action(f"Úprava akce{akce.title}") 
                                manager.update_event(
                                akce.event_id, new_title, new_cat, new_date, 
                                new_start, new_end, int(new_cap), new_org, new_alk
                                    )
                                st.success(f" Akce {new_title} byla upravena")
                                st.rerun()
                            except AndySabotageException as e:
                                st.error(str(e))
                        else:
                            st.error("chybějící pole")
                

    with tab_nova_akce:
        st.subheader("Vytvořit novou akci")

        with st.form("new_event_form"):
            new_title = st.text_input("Název")
            new_cat = st.text_input("Kategorie")
            new_date = st.text_input("Datum: Year Month Day", value="2026 11 28")
            new_start = st.text_input("Začátek (HH:MM)", value=10:00 ("%H:%M"))
            new_end = st.text_input("Konec (HH:MM)", value=12:00("%H:%M"))
            new_cap = st.number_input("Kapacita", value=5)
            new_org = st.text_input("Organizátor", value=current_user.name)
            new_alk = st.checkbox("Alkohol True?", value=False)

            if st.form_submit_button("Vytvořit akci"):
                if new_title and new_cat and new_date and new_start and new_end and new_cap and new_org:
                    try:
                        current_user.perform_admin_action(f"Vytvoření akce {akce.title}")
                        manager.add_event(
                            new_title, new_cat, new_date, new_start, new_end, int(new_cap), new_org, new_alk
                                )
                        st.success(f" Akce {new_title} byla vytvořena")
                        st.rerun()
                    except AndySabotageException as e:
                        st.error(str(e))
                else:
                    st.error("chybějící pole")

    with tab_uzivatele:
        st.subheader("Seznam uživatelů")

        for u_name, u_obj in list(manager.users.items()):
            col1, col2 = st.columns([3,1])
            with col1:
                role_name = type(u_obj).__name__    #magic method name vytáhne AdminUser, ALcoholIntolerantUser...jako string

                detail = ""     #vytvoření prázdné string
                if isinstance(u_obj, EarlyBirdUser): #pokud je instancí třídy earlybirduser
                    detail = (f" (Limit do {u_obj.max_hour.strftime('%H:%M')})")
                st.write(f"**{u_name}** — *Typ:* `{role_name}`{detail}")

            with col2: #do užšího sloupce (1/4) tlačítka
                if u_name != "Eda":
                    if st.button("Smazat uživatele", key=f"del_user_{u_name}"):
                        try:
                            current_user.perform_admin_action("Smazání uživatele")
                            manager.remove_user(u_name)
                            st.success(f"Uživatel {u_name} byl odstraněn.")
                            st.rerun()
                        except AndySabotageException as e:
                            st.error(str(e))
                else:
                    st.write("Nope. Administrátor nelze smazat")


        st.divider()
        st.subheader("přidat nového uživatele")

        new_u_name = st.text_input("Jméno uživatele")
        new_u_type = st.selectbox(
                "Typ uživatele (Role)", 
                ["Admin", "Andy", "abstinent", "Early Bird"],
                key = "selected_user_type"
            )
        new_u_extra = "cokoli"  #string jen musí existovat, aby se v manage.add_user nnevyvolala chyba chybějícím argumentem. Early bird si string přepíše, ostatní třídy to zahodí

        if st.session_state.get("selected_user_type") == "Early Bird":
                new_u_extra = st.text_input(
                    "Early Bird limit (HH:MM - platí jen pro Early Bird)", 
                    value="18:25",
                    key="early_bird_limit_input"
                )

        if st.button("Vytvořit uživatele"):
            try:
                current_user.perform_admin_action("přidání uživatele")
                if new_u_name.strip():
                    if new_u_name in manager.users:
                        st.error("Uživatel s tímto jménem již existuje!")
                    else:
                        manager.add_user(new_u_name, new_u_type, new_u_extra)
                        st.success(f"Uživatel '{new_u_name}' byl úspěšně vytvořen!")
                        st.rerun()
        
                else:
                    st.error("Zadej prosím jméno uživatele.")

            except AndySabotageException as e:
                st.error(str(e))


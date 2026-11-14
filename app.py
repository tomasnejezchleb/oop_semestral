import streamlit as st
from classes import EventManager, AndySabotageException


# Inicializace managera v session state, aby se resetem vymazal stav
if "manager" not in st.session_state:
    st.session_state.manager = EventManager()

manager = st.session_state.manager

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
dostupne_akce = [a for a in filtr_dle_usera if current_user.name not in a.participants]

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


    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            f"**{akce.title}**    *{akce.category}*    {date_str}    {start_str} - {end_str}    {kapacita_html}",
            unsafe_allow_html=True)

    with col2:
        already_signed = current_user.name in akce.participants

        if already_signed:
            st.write("Přihlášen")
        else:
            if st.button("Přihlásit", key = f"prihlas_{akce.event_id}"):
                uspech = akce. add_participant(current_user.name)
                if uspech or current_user.name in akce.participants:
                    st.success("Jsi přihlášen")
                    st.rerun()
                else:
                    st.error("Akce je plná nebo si se už přihlásil")

st.divider()

st.subheader("Přihlášené akce:")

moje_akce = [a for a in manager.events if current_user.name in a.participants]

if not moje_akce:    #testuje prázdnost seznamu
    date_str = akce.date.strftime("%d. %m. %Y")
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

if current_user.can_manage_events() and current_user.name != "Andy":
    st.divider()
    st.header("administrátorský panel")

    tab_akce, tab_nova_akce, tab_uzivatele = st.tabs(["Správa akcí", "Přidat akci", "Správa uživatelů"])    #vytvoření tlačítek

    with tab_akce:
        st.subheader("Seznam akcí")
        for akce in manager.events:
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{akce.title}** ({akce.date.strftime('%d.%m.%Y')})")
            with col2:
                if st.button('Smazat', key=f"admin_del_{akce.event_id}"):
                    manager.delete_event(akce.event_id)
                    st.rerun()

            
            with st.expander(f"Upravit: {akce.title}"):
                with st.form(key=f"edit_form_{akce.event_id}"):
                    
                    new_title = st.text_input("Název", value=akce.title)
                    new_cat = st.text_input("Kategorie", value=akce.category)
                    new_date = st.text_input("Datum", value=akce.date.strftime("%Y %m %d"))
                    new_start = st.text_input("Začátek (HH:MM)", value=akce.start_time.strftime("%H:%M"))
                    new_end = st.text_input("Konec (HH:MM)", value=akce.end_time.strftime("%H:%M"))
                    new_cap = st.number_input("Kapacita", value=akce.capacity)
                    new_org = st.text_input("Organizátor", value=akce.organizer)
                    new_alk = st.checkbox("Alkohol True?", value=akce.is_alcohol)
                    
                    if st.form_submit_button("Uložit změny"):
                    
                        manager.update_event(
                            akce.event_id, new_title, new_cat, new_date, 
                            new_start, new_end, int(new_cap), new_org, new_alk
                        )
                        st.success("Upraveno!")
                        st.rerun()

    with tab_nova_akce:
        st.subheader("Vytvořit novou akci")

        with st.form("new_event_form"):
            new_title = st.text_input("Název", value=akce.title)
            new_cat = st.text_input("Kategorie", value=akce.category)
            new_date = st.text_input("Datum Year Month Day", value=akce.date.strftime("%Y %m %d"))
            new_start = st.text_input("Začátek (HH:MM)", value=akce.start_time.strftime("%H:%M"))
            new_end = st.text_input("Konec (HH:MM)", value=akce.end_time.strftime("%H:%M"))
            new_cap = st.number_input("Kapacita", value=akce.capacity)
            new_org = st.text_input("Organizátor", value=akce.organizer)
            new_alk = st.checkbox("Alkohol True?", value=akce.is_alcohol)

            if st.form_submit_button("Vytvořit akci"):
                if new_title and new_date:
                    manager.add_event(
                        new_title, new_cat, new_date, new_start, new_end, int(new_cap), new_org, new_alk
                    )
                    st.succedd(f" Akce {new_title} byla vytvořena")
                    st.rerun()
                else:
                    st.error("chybějící pole")

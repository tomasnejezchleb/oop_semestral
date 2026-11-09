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

# Hlavní stránka – ukázka filtrování akcí pro vybraného uživatele
st.header(f"Vítej, {current_user.name}!")
dostupne_akce = current_user.filter_events(manager.events)

st.subheader("Dostupné akce:")

for akce in dostupne_akce:
    date_str = akce.date.strftime("%d. %m. %Y")
    start_str = akce.start_time.strftime("%H:%M")
    end_str = akce.end_time.strftime("%H:%M")
    
    # Výpočet volných míst
    volno = akce.capacity - len(akce.participants)
    
    # Určení barvy podle kapacity
    if volno > 0:
        kapacita_html = f"<span style= 'color: green; font-weight: bold;'>Kapacita {volno}</span>"
    else:
        kapacita_html = f"<span style= 'color: red; font-weight: bold;'>Kapacita vyčerpána'</span>"


    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            f"**{akce.title}**    *{akce.category}*    {date_str}    {start_str} - {end_str}    {kapacita_html}"
            )

    with col2:
        already_signed = current_user.name in akce.participants

        if already_signed:
            st.write(f"<span style = 'color: green; font-weight: bold;'> Přihlášen")
        else:
            if st.button("Přihlásit", key = f"prihlas_{akce.event_id}"):
                uspech = akce. add_participant(current_user.name)
                if uspech or current_user.name in akce.participants:
                    st.success(f"<span style = 'color:green'> Jsi přihlášen")
                    st.rerun()
                else:
                    st.error("Akce je plná nebo si se už přihlásil")

st.divider()

st.subheader("Přihlášené akce:")

moje_akce = [a for a in manager.events if current_user.name in a.participants]

if not moje_akce:    #testuje prázdnost seznamu
    date_str = akce.date.strftime("%d. %m. %Y")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(f"**{akce.title}**    *{akce.category}*    {date_str}    {start_str} - {end_str}    {kapacita_html}")

    with col2:
        if st.button("Odhlásit", key = f"odhlas_{akce.event_id}"):
            akce.remove_participant(current_user.name)
            st.success(f"Byl jsi odhlášen z akce {akce.title}")
            st.rerun()



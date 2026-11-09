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
    # Formátování data a časů pro hezčí výpis
    date_str = akce.date.strftime("%d. %m. %Y")
    start_str = akce.start_time.strftime("%H:%M")
    end_str = akce.end_time.strftime("%H:%M")
    
    # Výpočet volných míst
    volno = akce.capacity - len(akce.participants)
    
    # Určení barvy podle kapacity
    if volno > 0:
        kapacita_html = f"<span style='color: green; font-weight: bold;>'Kapacita {volno}</span>"
    else:
        kapacita_html = f"<span style='color: red; font-weight: bold;>'kapacita vyčerpána'</span>"
    
    # Vykreslení řádku akce pomocí Markdownu s HTML pro barvu
    st.markdown(
        f"- **{akce.title}** | *{akce.category}* |  {date_str} |  {start_str} - {end_str} | Kapacita: {kapacita_html}",
        unsafe_allow_html=True
    )

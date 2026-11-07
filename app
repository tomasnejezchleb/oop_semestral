import streamlit as st
from classes import EventManager, AndySabotageException

st.setTitle("Správa akcí")

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
    st.write(f"- **{akce.title}** (Kategorie: {akce.category}, Alkohol: {akce.is_alcohol})")

# Test administrátorské akce / sabotáže
if st.button("Provést administrátorskou akci"):
    try:
        vysledek = current_user.perform_admin_action("Testovací zásah z webu")
        st.success(vysledek)
    except AndySabotageException as e:
        st.error(f"⚠️ Andy úřaduje: {e}")

"""
Registro de las páginas de la aplicación.

Las páginas se definen UNA sola vez aquí y se usan en dos lugares:
    - app.py arma el menú lateral con SECCIONES.
    - Las páginas que enlazan a otras (Inicio y Marco teórico) usan estos
      mismos objetos con st.page_link(), que exige la página registrada.
"""

import streamlit as st

from interfaz import pag_despejes, pag_directo, pag_inicio, pag_tasas, pag_teoria


INICIO = st.Page(pag_inicio.mostrar, title="Inicio", icon=":material/home:",
                 url_path="inicio", default=True)
TEORIA = st.Page(pag_teoria.mostrar, title="Marco teórico", icon=":material/menu_book:",
                 url_path="teoria")
TASAS = st.Page(pag_tasas.mostrar, title="Conversión de tasas", icon=":material/percent:",
                url_path="tasas")
DIRECTO = st.Page(pag_directo.mostrar, title="Cálculo directo", icon=":material/calculate:",
                  url_path="directo")
DESPEJES = st.Page(pag_despejes.mostrar, title="Despejes", icon=":material/function:",
                   url_path="despejes")

# Menú lateral agrupado por secciones
SECCIONES = {
    "General": [INICIO],
    "Aprender": [TEORIA],
    "Practicar": [TASAS, DIRECTO, DESPEJES],
}

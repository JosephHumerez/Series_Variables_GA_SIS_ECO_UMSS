"""
Calculadora de Series Variables en Gradiente Aritmético (G.A.)
Ingeniería Económica — M. Sc. Emir Vargas Peredo, Unidad 2.

Para iniciar la aplicación (con el entorno virtual activado):
    streamlit run app.py

Este archivo solo arma el menú de navegación. El contenido de cada página
está en la carpeta "interfaz" y toda la matemática en la carpeta "gradiente".
"""

import streamlit as st

from interfaz import comun, pag_directo, pag_inicio, pag_tasas


st.set_page_config(
    page_title="Calculadora de Gradiente Aritmético",
    page_icon="📈",
    layout="wide",
)

# Menú lateral con las páginas de la aplicación
navegacion = st.navigation([
    st.Page(pag_inicio.mostrar, title="Inicio", icon="🏠", url_path="inicio", default=True),
    st.Page(pag_tasas.mostrar, title="Conversión de tasas", icon="🔄", url_path="tasas"),
    st.Page(pag_directo.mostrar, title="Cálculo directo", icon="🧮", url_path="directo"),
])

with st.sidebar:
    st.caption("Ingeniería Económica · M. Sc. Emir Vargas Peredo · Unidad 2")

# Dibuja la página elegida
navegacion.run()

# Se dibuja DESPUÉS de la página, para que muestre la tasa recién guardada
comun.mostrar_tasa_activa_en_barra()

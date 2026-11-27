"""
Calculadora de Series Variables en Gradiente Aritmético (G.A.)
Ingeniería Económica — M. Sc. Emir Vargas Peredo, Unidad 2.

Para iniciar la aplicación (con el entorno virtual activado):
    streamlit run app.py

Este archivo solo arma el menú de navegación. El contenido de cada página
está en la carpeta "interfaz" y toda la matemática en la carpeta "gradiente".
"""

import streamlit as st

from interfaz import comun, estilo, pag_despejes, pag_directo, pag_inicio, pag_tasas


st.set_page_config(
    page_title="Calculadora de Gradiente Aritmético",
    page_icon=":material/functions:",
    layout="wide",
    initial_sidebar_state="locked",   # la barra lateral no se puede esconder (en computadora)
)

# Colores de las tarjetas de resultado (ver interfaz/estilo.py)
estilo.aplicar_estilos()

# Menú lateral con las páginas de la aplicación
navegacion = st.navigation([
    st.Page(pag_inicio.mostrar, title="Inicio", icon=":material/home:",
            url_path="inicio", default=True),
    st.Page(pag_tasas.mostrar, title="Conversión de tasas", icon=":material/percent:",
            url_path="tasas"),
    st.Page(pag_directo.mostrar, title="Cálculo directo", icon=":material/calculate:",
            url_path="directo"),
    st.Page(pag_despejes.mostrar, title="Despejes", icon=":material/function:",
            url_path="despejes"),
])

# Dibuja la página elegida
navegacion.run()

# Barra lateral. Se dibuja DESPUÉS de la página, para que muestre la tasa recién guardada
comun.mostrar_tasa_activa_en_barra()
estilo.mostrar_leyenda()
with st.sidebar:
    st.divider()
    st.caption(":material/menu_book: *Ingeniería Económica*, M. Sc. Emir Vargas Peredo · Unidad 2")

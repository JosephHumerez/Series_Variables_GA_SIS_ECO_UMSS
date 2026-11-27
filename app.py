"""
Calculadora de Series Variables en Gradiente Aritmético (G.A.)
Ingeniería Económica — M. Sc. Emir Vargas Peredo, Unidad 2.

Para iniciar la aplicación (con el entorno virtual activado):
    streamlit run app.py

Este archivo solo arma el menú de navegación. El contenido de cada página
está en la carpeta "interfaz" y toda la matemática en la carpeta "gradiente".
"""

import streamlit as st

from interfaz import comun, estilo, paginas


st.set_page_config(
    page_title="Calculadora de Gradiente Aritmético",
    page_icon=":material/functions:",
    layout="wide",
    initial_sidebar_state="locked",   # la barra lateral no se puede esconder (en computadora)
)

# Colores de las tarjetas de resultado (ver interfaz/estilo.py)
estilo.aplicar_estilos()

# Menú lateral agrupado en secciones (las páginas se definen en interfaz/paginas.py)
navegacion = st.navigation(paginas.SECCIONES)

# Dibuja la página elegida
navegacion.run()

# Barra lateral. Se dibuja DESPUÉS de la página, para que muestre la tasa recién guardada
comun.mostrar_tasa_activa_en_barra()
estilo.mostrar_leyenda()
with st.sidebar:
    st.divider()
    st.caption(":material/book: *Ingeniería Económica*, M. Sc. Emir Vargas Peredo · Unidad 2")

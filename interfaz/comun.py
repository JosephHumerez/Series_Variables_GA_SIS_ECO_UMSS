"""
Piezas compartidas por todas las páginas de la interfaz.
"""

import streamlit as st

from gradiente.procedimiento import Paso, formato_porcentaje


# ---------------------------------------------------------------------------
# Mostrar el procedimiento paso a paso
# ---------------------------------------------------------------------------

def mostrar_pasos(pasos: list[Paso]) -> None:
    """Dibuja cada paso en un recuadro: título, ecuaciones (LaTeX) y explicación."""
    for paso in pasos:
        with st.container(border=True):
            st.markdown(f"**{paso.titulo}**")
            if paso.ecuaciones:
                # Todas las líneas del paso en un solo bloque, alineadas a la izquierda
                lineas = r" \\[6pt] ".join(paso.ecuaciones)
                st.latex(r"\begin{array}{l}" + lineas + r"\end{array}")
            if paso.explicacion:
                st.markdown(paso.explicacion)


# ---------------------------------------------------------------------------
# Tasa en uso (compartida entre páginas)
#
# st.session_state es un diccionario que Streamlit conserva mientras la
# pestaña del navegador esté abierta. Así, la tasa convertida en la página
# de tasas puede reutilizarse en las páginas de cálculo.
# ---------------------------------------------------------------------------

CLAVE_TASA = "tasa_activa"


def guardar_tasa(i: float, periodo: str, descripcion: str) -> None:
    st.session_state[CLAVE_TASA] = {"i": i, "periodo": periodo, "descripcion": descripcion}


def tasa_activa() -> dict | None:
    """Devuelve {'i', 'periodo', 'descripcion'} o None si no hay tasa guardada."""
    return st.session_state.get(CLAVE_TASA)


def borrar_tasa() -> None:
    st.session_state.pop(CLAVE_TASA, None)


def mostrar_tasa_activa_en_barra() -> None:
    """Recuadro en la barra lateral con la tasa que se está usando."""
    tasa = tasa_activa()
    with st.sidebar:
        st.divider()
        st.markdown("**Tasa en uso**")
        if tasa is None:
            st.caption("Ninguna. Puedes convertir una en «Conversión de tasas» "
                       "o escribirla directamente en cada cálculo.")
            return
        st.success(f"{formato_porcentaje(tasa['i'])} efectiva {tasa['periodo']}")
        st.caption(tasa["descripcion"])
        if st.button("Quitar tasa", key="quitar_tasa"):
            borrar_tasa()
            st.rerun()

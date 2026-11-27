"""
Piezas compartidas por todas las páginas de la interfaz.
"""

import pandas as pd
import streamlit as st

from gradiente.procedimiento import Paso, formato_numero, formato_porcentaje
from gradiente.serie import Pago
from interfaz.estilo import COLORES, coloreado, concepto_de_ecuacion, latex_coloreado, tarjeta


# ---------------------------------------------------------------------------
# Mostrar el procedimiento paso a paso
# ---------------------------------------------------------------------------

def mostrar_pasos(pasos: list[Paso]) -> None:
    """
    Dibuja cada paso en un recuadro: título, ecuaciones (LaTeX) y explicación.
    La última ecuación (el resultado del paso) se enmarca con el color de su variable.
    """
    for paso in pasos:
        with st.container(border=True):
            st.markdown(f"**{paso.titulo}**")
            if paso.ecuaciones:
                ecuaciones = list(paso.ecuaciones)
                concepto = concepto_de_ecuacion(ecuaciones[-1])
                if concepto is not None:
                    ecuaciones[-1] = latex_coloreado(concepto, rf"\boxed{{{ecuaciones[-1]}}}")
                # Todas las líneas del paso en un solo bloque, alineadas a la izquierda
                lineas = r" \\[6pt] ".join(ecuaciones)
                st.latex(r"\begin{array}{l}" + lineas + r"\end{array}")
            if paso.explicacion:
                st.markdown(paso.explicacion)


def mostrar_tabla_pagos(pagos: tuple[Pago, ...]) -> None:
    """Tabla con cada cuota: base en azul, gradiente en naranja y pago en negrita."""
    tabla = pd.DataFrame([
        {
            "Cuota": p.numero,
            "Periodo": p.periodo,
            "Base A'": formato_numero(p.base),
            "Gradiente": formato_numero(p.gradiente),
            "Pago Xₖ": formato_numero(p.monto),
        }
        for p in pagos
    ])
    con_color = (
        tabla.style
        .set_properties(subset=["Base A'"], color=COLORES["cuota"].hex)
        .set_properties(subset=["Gradiente"], color=COLORES["G"].hex)
        .set_properties(subset=["Pago Xₖ"], **{"font-weight": "bold"})
    )
    st.dataframe(con_color, hide_index=True, width="stretch")
    base = coloreado("cuota", "A'")
    gradiente = coloreado("G", "G")
    st.caption(f"Xₖ = {base} ± (k − 1)·{gradiente}")


def pedir_tasa(prefijo: str, valor_defecto: float) -> float:
    """
    Usa la tasa guardada en «Conversión de tasas» o pide una nueva.
    Devuelve i en forma decimal.

    prefijo       : distingue los controles de cada página (ej. "dir" -> "dir_i")
    valor_defecto : tasa sugerida en %, si no hay tasa guardada
    """
    tasa = tasa_activa()
    if tasa is not None:
        usar = st.checkbox(
            f"Usar la tasa en uso: {formato_porcentaje(tasa['i'])} efectiva {tasa['periodo']}",
            value=True, key=f"{prefijo}_usar_tasa",
        )
        if usar:
            return tasa["i"]
    return st.number_input(
        f"Tasa efectiva por periodo, {coloreado('i', 'i')} (%)", min_value=0.0,
        value=valor_defecto, step=0.1,
        format="%.4f", key=f"{prefijo}_i",
        help="Debe estar en el mismo periodo que las cuotas. Si no, conviértela primero.",
    ) / 100


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
    """Sección de la barra lateral con la tasa que se está usando (tarjeta amarilla)."""
    tasa = tasa_activa()
    with st.sidebar:
        st.divider()
        st.markdown("**:material/percent: Tasa en uso**")
        if tasa is None:
            st.caption("Ninguna guardada. Puedes convertir una en «Conversión de tasas».")
            return
        tarjeta("i", f"efectiva {tasa['periodo']}", formato_porcentaje(tasa["i"]), clave="barra")
        st.caption(tasa["descripcion"])
        if st.button("Quitar tasa", key="quitar_tasa", icon=":material/close:", type="tertiary"):
            borrar_tasa()
            st.rerun()

"""
Página 1: Conversión de tasas.

Lleva una tasa nominal o efectiva a la tasa efectiva del periodo de pago,
muestra el procedimiento y permite guardarla para usarla en los cálculos.
"""

import streamlit as st

from gradiente.procedimiento import formato_porcentaje, procedimiento_conversion
from gradiente.tasas import PERIODICIDADES, convertir_a_periodo_de_pago
from interfaz.comun import guardar_tasa, mostrar_pasos
from interfaz.estilo import tarjeta


def mostrar() -> None:
    st.title(":material/percent: Conversión de tasas")
    st.markdown(
        "Antes de aplicar los factores, la tasa debe ser la **tasa efectiva del "
        "periodo de pago**. Por ejemplo, si las cuotas son semestrales, se necesita "
        "la tasa efectiva semestral."
    )

    # ------------------------------------------------------------------
    # Datos
    # ------------------------------------------------------------------
    col_datos, col_pago = st.columns(2)

    with col_datos:
        st.subheader(":material/input: Tasa dada")
        tipo = st.radio("Tipo de tasa", ["Nominal", "Efectiva"], horizontal=True)
        tasa_pct = st.number_input(
            "Valor de la tasa (%)", min_value=0.0, value=24.0, step=0.5, format="%.4f",
            help="Escribe el porcentaje: para 24 % escribe 24.",
        )
        periodicidad = st.selectbox(
            "Periodo de la tasa", PERIODICIDADES, index=PERIODICIDADES.index("anual"),
            help="Una tasa nominal normalmente es anual (ej. 24 % anual capitalizable mensualmente).",
        )
        capitalizacion = None
        if tipo == "Nominal":
            capitalizacion = st.selectbox(
                "Capitalización", PERIODICIDADES, index=PERIODICIDADES.index("mensual"),
                help="Cada cuánto se capitalizan los intereses.",
            )

    with col_pago:
        st.subheader(":material/event_repeat: Pagos de la serie")
        periodo_pago = st.selectbox(
            "Periodicidad de los pagos", PERIODICIDADES,
            index=PERIODICIDADES.index("semestral"),
        )

    # Frase que describe la tasa tal como se lee en un enunciado
    if tipo == "Nominal":
        descripcion = (f"{formato_porcentaje(tasa_pct / 100)} nominal {periodicidad} "
                       f"capitalizable {capitalizacion}mente")
    else:
        descripcion = f"{formato_porcentaje(tasa_pct / 100)} efectiva {periodicidad}"
    st.info(f"Se interpreta como: **{descripcion}**, con pagos **{periodo_pago}es**.",
            icon=":material/info:")

    # ------------------------------------------------------------------
    # Cálculo
    # ------------------------------------------------------------------
    try:
        conversion = convertir_a_periodo_de_pago(
            tasa_pct / 100, tipo.lower(), periodicidad, periodo_pago, capitalizacion
        )
    except ValueError as error:
        st.error(str(error), icon=":material/error:")
        return

    # ------------------------------------------------------------------
    # Resultado y procedimiento
    # ------------------------------------------------------------------
    st.divider()
    col_resultado, col_boton = st.columns([2, 1], vertical_alignment="bottom")
    with col_resultado:
        tarjeta("i", f"Tasa efectiva {periodo_pago}", formato_porcentaje(conversion.tasa_pago),
                clave="tasas")
        st.caption(f"Valor decimal con precisión completa: {conversion.tasa_pago:.10f}")
    with col_boton:
        if st.button("Usar esta tasa en los cálculos", icon=":material/check_circle:",
                     type="primary", width="stretch"):
            guardar_tasa(conversion.tasa_pago, periodo_pago, descripcion)
            st.success("Tasa guardada. Se usará en las páginas de cálculo.",
                       icon=":material/task_alt:")

    st.subheader(":material/format_list_numbered: Procedimiento")
    mostrar_pasos(procedimiento_conversion(conversion))

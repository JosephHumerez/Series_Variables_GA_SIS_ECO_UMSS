"""
Página 2: Cálculo directo.

A partir de A', G, i, n y el tipo de gradiente calcula la anualidad
equivalente A, el valor presente P, el valor futuro F y las cuotas X_k.
Muestra el diagrama de flujo, el procedimiento del libro y la tabla de pagos.

Los valores por defecto son los del Ejercicio 1 del libro (pág. 35).
"""

import streamlit as st

from gradiente.procedimiento import formato_numero, procedimiento_cuota, procedimiento_serie
from gradiente.serie import SerieGradiente, calcular
from interfaz.comun import mostrar_pasos, mostrar_tabla_pagos, pedir_tasa
from interfaz.diagrama import diagrama_flujo


def mostrar() -> None:
    st.title(":material/calculate: Cálculo directo")
    st.markdown("Calcula **A**, **P**, **F** y las cuotas **Xₖ** de una serie en gradiente aritmético.")

    # ------------------------------------------------------------------
    # Datos
    # ------------------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    with col1:
        A_prima = st.number_input("Primer pago, A'", value=30_000.0, step=100.0,
                                  format="%.2f", key="dir_A")
        G = st.number_input("Gradiente, G", min_value=0.0, value=2_000.0, step=100.0,
                            format="%.2f", key="dir_G",
                            help="Siempre positivo. El sentido se elige en «Tipo de gradiente».")
    with col2:
        tipo = st.radio("Tipo de gradiente", ["Creciente", "Decreciente"], index=1,
                        horizontal=True, key="dir_tipo")
        n = st.number_input("Número de cuotas, n", min_value=1, value=11, step=1, key="dir_n")
    with col3:
        i = pedir_tasa("dir", 9.27)

    with st.expander("Opciones avanzadas: serie diferida y diagrama"):
        c1, c2, c3 = st.columns(3)
        inicio = c1.number_input(
            "Periodo de la primera cuota", min_value=1, value=1, step=1, key="dir_inicio",
            help="1 = serie normal. Mayor que 1 = serie diferida.",
        )
        sentido = c2.radio("Las cuotas son", ["Egresos (↓)", "Ingresos (↑)"],
                           key="dir_sentido")
        mostrar_eq = c3.radio("Valor equivalente en el diagrama", ["P", "F", "Ninguno"],
                              horizontal=True, key="dir_equivalente")

    # ------------------------------------------------------------------
    # Cálculo
    # ------------------------------------------------------------------
    try:
        serie = SerieGradiente(A_prima=A_prima, G=G, i=i, n=int(n),
                               tipo=tipo.lower(), inicio=int(inicio))
        r = calcular(serie)
    except ValueError as error:
        st.error(str(error), icon=":material/error:")
        return

    # ------------------------------------------------------------------
    # Resultados principales
    # ------------------------------------------------------------------
    st.divider()
    signo = "+" if serie.signo > 0 else "−"
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Anualidad equivalente, A", formato_numero(r.A),
              help=f"A = A' {signo} G·(A/G) = {formato_numero(A_prima)} {signo} "
                   f"{formato_numero(abs(r.A_gradiente))}")
    m2.metric("Valor presente, P", formato_numero(r.P), help="Ubicado en el periodo 0.")
    m3.metric("Valor futuro, F", formato_numero(r.F),
              help=f"Ubicado en el periodo {serie.periodo_final}.")
    m4.metric(f"Última cuota, X{serie.n}", formato_numero(r.pagos[-1].monto))

    for aviso in r.avisos:
        st.warning(aviso, icon=":material/warning:")

    # ------------------------------------------------------------------
    # Diagrama de flujo
    # ------------------------------------------------------------------
    equivalente = {
        "P": ("P", r.P, 0),
        "F": ("F", r.F, serie.periodo_final),
        "Ninguno": None,
    }[mostrar_eq]
    figura = diagrama_flujo(serie, "ingreso" if "Ingresos" in sentido else "egreso", equivalente)
    st.plotly_chart(figura, width="stretch", key="dir_diagrama")

    # ------------------------------------------------------------------
    # Detalle en pestañas
    # ------------------------------------------------------------------
    tab_proc, tab_tabla, tab_cuota = st.tabs([
        ":material/format_list_numbered: Procedimiento",
        ":material/table_chart: Tabla de pagos",
        ":material/search: Cuota Xₖ",
    ])

    with tab_proc:
        mostrar_pasos(procedimiento_serie(r))

    with tab_tabla:
        mostrar_tabla_pagos(r.pagos)

    with tab_cuota:
        k = st.number_input("Número de cuota, k", min_value=1, max_value=serie.n,
                            value=serie.n, step=1, key="dir_k")
        mostrar_pasos([procedimiento_cuota(serie, int(k))])

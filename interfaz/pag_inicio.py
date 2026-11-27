"""
Página de inicio: qué hace la calculadora, qué metodología sigue,
el código de colores y cómo recorrer las páginas.
"""

import streamlit as st

from interfaz.estilo import COLORES, coloreado, insignia, latex_coloreado


def _formulas_coloreadas() -> str:
    """Las tres fórmulas del libro, cada variable con su color."""
    A = latex_coloreado("A", "A")
    A_prima = latex_coloreado("cuota", "A'")
    G = latex_coloreado("G", "G")
    P = latex_coloreado("P", "P")
    F = latex_coloreado("F", "F")
    i = latex_coloreado("i", "i")
    n = latex_coloreado("n", "n")
    return (
        rf"{A} = {A_prima} \pm {G}\,(A/G;\ {i};\ {n})"
        rf"\qquad {P} = {A}\,(P/A;\ {i};\ {n})"
        rf"\qquad {F} = {A}\,(F/A;\ {i};\ {n})"
    )


def mostrar() -> None:
    st.title(":material/functions: Calculadora de Series en Gradiente Aritmético")
    st.markdown(
        "Resuelve problemas de **series variables en gradiente aritmético (G.A.)** "
        "siguiendo la metodología del libro *Ingeniería Económica* de "
        "M. Sc. Emir Vargas Peredo (Unidad 2: Valor del dinero en el tiempo)."
    )

    # ------------------------------------------------------------------
    st.subheader(":material/school: Metodología")
    st.markdown(
        f"La serie se descompone en una {coloreado('cuota', 'serie uniforme base')} "
        f"(A' repetido n veces) y una {coloreado('G', 'serie gradiente pura')} "
        "(0, G, 2G, …, (n−1)G). El gradiente se convierte en una "
        f"{coloreado('A', 'anualidad equivalente')}, se suma o resta a la base, y la "
        f"anualidad total se lleva a {coloreado('P', 'valor presente')} o "
        f"{coloreado('F', 'valor futuro')}:"
    )
    st.latex(_formulas_coloreadas())

    # ------------------------------------------------------------------
    st.subheader(":material/palette: Código de colores")
    st.markdown("Cada concepto tiene **siempre el mismo color** en los datos, los "
                "resultados, el procedimiento, el diagrama y la tabla.")
    columnas = st.columns(len(COLORES))
    for columna, (concepto, color) in zip(columnas, COLORES.items()):
        with columna:
            st.markdown(f"{insignia(concepto)}  \n{color.significado}")

    # ------------------------------------------------------------------
    # Se importa aquí (y no arriba) porque paginas.py importa este módulo
    from interfaz import paginas

    st.subheader(":material/route: Cómo usarla")
    pasos = [
        ("A", paginas.TEORIA, "1. Aprende la teoría",
         "Si es tu primera vez con el tema, empieza por el manual: conceptos, fórmulas "
         "y ejemplos resueltos."),
        ("i", paginas.TASAS, "2. Convierte la tasa",
         "Si la tasa del problema no está en el periodo de los pagos, conviértela "
         "y pulsa **Usar esta tasa**."),
        ("P", paginas.DIRECTO, "3. Cálculo directo",
         "A partir de A', G, i y n obtén A, P, F, las cuotas, el diagrama de flujo "
         "y el procedimiento del libro."),
        ("G", paginas.DESPEJES, "4. Despejes",
         "Halla la incógnita que falte: n, i, A', G, o A' y G a la vez."),
    ]
    for columna, (concepto, pagina, titulo, texto) in zip(st.columns(4), pasos):
        with columna, st.container(key=f"tarjeta-{concepto}-inicio", height="stretch"):
            st.markdown(f"#### {titulo}")
            st.markdown(texto)
            st.page_link(pagina, label=f"Ir a {pagina.title}", icon=":material/arrow_forward:")
    st.caption("Cada página de cálculo viene cargada con un ejercicio resuelto del libro.")

"""
Página de inicio: qué hace la calculadora y qué metodología sigue.
"""

import streamlit as st


def mostrar() -> None:
    st.title("📈 Calculadora de Series en Gradiente Aritmético")
    st.markdown(
        "Resuelve problemas de **series variables en gradiente aritmético (G.A.)** "
        "siguiendo la metodología del libro *Ingeniería Económica* de "
        "M. Sc. Emir Vargas Peredo (Unidad 2: Valor del dinero en el tiempo)."
    )

    st.subheader("Metodología")
    st.markdown(
        "La serie se descompone en una **serie uniforme base** (A' repetido n veces) "
        "y una **serie gradiente pura** (0, G, 2G, …, (n−1)G). El gradiente se convierte "
        "en una anualidad equivalente, se suma o resta a la base, y la anualidad total "
        "se lleva a valor presente o futuro:"
    )
    st.latex(r"A = A' \pm G\,(A/G;\ i;\ n) \qquad P = A\,(P/A;\ i;\ n) \qquad F = A\,(F/A;\ i;\ n)")

    st.subheader("Notación")
    st.markdown(
        "| Símbolo | Significado |\n"
        "|---|---|\n"
        "| **A'** | Primer pago (serie base) |\n"
        "| **G** | Gradiente: aumento o disminución constante por periodo |\n"
        "| **i** | Tasa efectiva del periodo de pago |\n"
        "| **n** | Número de periodos (cuotas) |\n"
        "| **P** | Valor presente (periodo 0) |\n"
        "| **F** | Valor futuro (periodo n) |\n"
        "| **A** | Anualidad equivalente total |\n"
        "| **Xₖ** | Pago del periodo k:  Xₖ = A' ± (k − 1)·G |"
    )

    st.subheader("Cómo usarla")
    st.markdown(
        "1. **Conversión de tasas:** si la tasa del problema no está en el periodo de "
        "los pagos, conviértela primero y pulsa *Usar esta tasa*.\n"
        "2. **Cálculo directo:** P, F, A, cuotas, diagrama de flujo y procedimiento "
        "a partir de A', G, i y n.\n"
        "3. **Despejes** *(próximamente)*: hallar n, i, A' o G."
    )

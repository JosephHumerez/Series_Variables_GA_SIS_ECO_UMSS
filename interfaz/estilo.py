"""
Sistema de colores de la calculadora.

Cada concepto financiero tiene SIEMPRE el mismo color en toda la aplicación:
en los datos, los resultados, el procedimiento, el diagrama y la tabla.
Así, quien ve el sistema por primera vez puede seguir cada valor con la vista.

    Concepto                      Color
    ---------------------------   --------
    A', Xₖ  primer pago y cuotas  azul
    G       gradiente             naranja
    A       anualidad equivalente violeta
    P       valor presente        verde
    F       valor futuro          rojo
    i       tasa de interés       amarillo
    n       número de periodos    gris

Para cambiar un color en todo el sistema basta con editar el diccionario COLORES.
"""

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class Color:
    nombre: str        # nombre del color en Streamlit (para textos e insignias)
    hex: str           # código del color (para el diagrama, las fórmulas y el CSS)
    simbolo: str       # símbolo del concepto
    significado: str   # descripción para la leyenda
    corto: str         # descripción breve (leyenda de la barra lateral)


COLORES = {
    "cuota": Color("blue", "#1c83e1", "A', Xₖ", "Primer pago y cuotas", "cuotas"),
    "G": Color("orange", "#ff8700", "G", "Gradiente", "gradiente"),
    "A": Color("violet", "#803df5", "A", "Anualidad equivalente", "anualidad"),
    "P": Color("green", "#21c354", "P", "Valor presente", "presente"),
    "F": Color("red", "#ff4b4b", "F", "Valor futuro", "futuro"),
    "i": Color("yellow", "#d4a106", "i", "Tasa de interés", "tasa"),
    "n": Color("gray", "#808495", "n", "Número de periodos", "periodos"),
}


# ---------------------------------------------------------------------------
# Texto con color (sintaxis de Markdown de Streamlit)
# ---------------------------------------------------------------------------

def insignia(concepto: str, texto: str | None = None) -> str:
    """Insignia de color, ej. ':green-badge[P]'."""
    color = COLORES[concepto]
    return f":{color.nombre}-badge[{texto or color.simbolo}]"


def coloreado(concepto: str, texto: str) -> str:
    """Texto en negrita del color del concepto, ej. ':blue[**A'**]'."""
    return f":{COLORES[concepto].nombre}[**{texto}**]"


def latex_coloreado(concepto: str, latex: str) -> str:
    """Fórmula LaTeX del color del concepto."""
    return rf"\textcolor{{{COLORES[concepto].hex}}}{{{latex}}}"


def concepto_de_ecuacion(linea: str) -> str | None:
    """
    Deduce el concepto por la variable del lado izquierdo de una ecuación LaTeX.
    Ej.: "P = 146\\,111{,}54" -> "P";  "A' = ..." -> "cuota";  "g = ..." -> "G".
    """
    linea = linea.strip()
    if linea.startswith("A'"):
        return "cuota"
    return {"A": "A", "P": "P", "F": "F", "G": "G", "g": "G",
            "i": "i", "n": "n", "X": "cuota"}.get(linea[:1])


# ---------------------------------------------------------------------------
# Tarjetas de resultado
# ---------------------------------------------------------------------------

def tarjeta(concepto: str, titulo: str, valor: str, clave: str,
            simbolo: str | None = None, ayuda: str | None = None) -> None:
    """
    Recuadro de resultado con borde y fondo del color del concepto.

    El color se aplica con CSS (ver aplicar_estilos) a través de la clave del
    contenedor: Streamlit le agrega la clase "st-key-<clave>".
    """
    with st.container(key=f"tarjeta-{concepto}-{clave}"):
        st.metric(f"{insignia(concepto, simbolo)} {titulo}", valor, help=ayuda)


def _rgba(hex_color: str, opacidad: float) -> str:
    r, g, b = (int(hex_color[k:k + 2], 16) for k in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {opacidad})"


# Barra lateral: se quita el encabezado vacío (ahí estaba el botón para cerrarla)
# y se reducen un poco los márgenes, manteniendo el espaciado normal del sistema.
CSS_BARRA_LATERAL = """
[data-testid="stSidebarHeader"] { display: none; }
[data-testid="stSidebarNav"] { padding-top: 1rem; }
[data-testid="stSidebarUserContent"] { padding-top: 0.5rem; }
[data-testid="stSidebar"] hr { margin: 0.75rem 0; }
"""


def aplicar_estilos() -> None:
    """Inserta el CSS de las tarjetas de color y de la barra lateral. Se llama una vez en app.py."""
    reglas = [
        f'div[class*="st-key-tarjeta-{concepto}-"] {{'
        f"border-left: 0.4rem solid {c.hex};"
        f"background-color: {_rgba(c.hex, 0.10)};"
        "border-radius: 0.6rem; padding: 0.7rem 1rem; }"
        for concepto, c in COLORES.items()
    ]
    st.html("<style>" + "\n".join(reglas) + CSS_BARRA_LATERAL + "</style>")


# ---------------------------------------------------------------------------
# Leyenda
# ---------------------------------------------------------------------------

def mostrar_leyenda() -> None:
    """Código de colores en la barra lateral: un concepto por línea, como en Inicio."""
    with st.sidebar:
        st.divider()
        st.markdown("**:material/palette: Código de colores**")
        st.markdown("  \n".join(f"{insignia(k)}&nbsp; {c.significado}" for k, c in COLORES.items()))

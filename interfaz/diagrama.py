"""
Diagrama de flujo de caja, como en el libro:

    - Línea de tiempo horizontal de 0 a n.
    - Una flecha vertical por cuota, con su valor:
        hacia ARRIBA  = ingreso (cobro, depósito recibido)
        hacia ABAJO   = egreso  (pago)
    - La altura de cada flecha es proporcional a su monto.
    - Cada flecha muestra la DESCOMPOSICIÓN del libro (código de colores):
        creciente:   tramo azul = base A'  +  tramo naranja = gradiente (k-1)G
        decreciente: flecha azul = cuota   +  tramo naranja punteado = lo que
                     el gradiente le restó a la base A'
    - Línea punteada azul a la altura de A' (nivel de la serie base).
    - Opcionalmente, el valor equivalente en sentido contrario:
      P en verde (periodo 0) o F en rojo (periodo final).
    - La tasa i indicada arriba y una leyenda abajo.
"""

import math

import plotly.graph_objects as go

from gradiente.procedimiento import formato_numero, formato_porcentaje
from gradiente.serie import SerieGradiente, tabla_de_pagos
from interfaz.estilo import COLORES


COLOR_BASE = COLORES["cuota"].hex               # azul: base A' y cuotas
COLOR_GRADIENTE = COLORES["G"].hex              # naranja: aporte del gradiente
COLOR_CUOTA_NEGATIVA = COLORES["n"].hex         # gris: cuotas que cambiaron de signo
COLORES_EQUIVALENTE = {"P": COLORES["P"].hex, "F": COLORES["F"].hex}
COLOR_LINEA = "#9ca3af"                         # gris claro: línea de tiempo

MAX_ETIQUETAS = 24              # si hay más cuotas, se rotulan solo algunas
ALTURA_EQUIVALENTE = 1.25       # altura de la flecha de P o F (las cuotas miden hasta 1)
GROSOR = 3


def _flecha(fig: go.Figure, x: float, altura: float, color: str, desde: float = 0.0) -> None:
    """Flecha vertical desde 'desde' (por defecto la línea de tiempo) hasta 'altura'."""
    fig.add_annotation(
        x=x, y=altura, ax=x, ay=desde,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=2, arrowsize=1.1, arrowwidth=GROSOR,
        arrowcolor=color, text="",
    )


def _tramo(fig: go.Figure, x: float, y0: float, y1: float, color: str,
           punteado: bool = False) -> None:
    """Segmento vertical sin punta (para la descomposición base + gradiente)."""
    fig.add_shape(type="line", x0=x, x1=x, y0=y0, y1=y1,
                  line={"color": color, "width": GROSOR, "dash": "dot" if punteado else "solid"})


def _etiqueta(fig: go.Figure, x: float, altura: float, texto: str,
              color: str, vertical: bool) -> None:
    """Escribe el valor en la punta de la flecha."""
    arriba = altura > 0
    fig.add_annotation(
        x=x, y=altura, text=texto, showarrow=False,
        yanchor="bottom" if arriba else "top",
        yshift=6 if arriba else -6,
        textangle=-90 if vertical else 0,
        font={"size": 11, "color": color},
    )


def _entrada_leyenda(fig: go.Figure, nombre: str, color: str, punteado: bool = False) -> None:
    """Agrega una línea a la leyenda (traza vacía que no se dibuja en el gráfico)."""
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="lines", name=nombre,
        line={"color": color, "width": 4, "dash": "dot" if punteado else "solid"},
    ))


def diagrama_flujo(serie: SerieGradiente, sentido: str = "egreso",
                   equivalente: tuple[str, float, int] | None = None,
                   mostrar_tasa: bool = True) -> go.Figure:
    """
    Construye el diagrama de flujo de caja de la serie.

    serie        : la serie en gradiente
    sentido      : "ingreso" (flechas hacia arriba) o "egreso" (hacia abajo)
    equivalente  : (nombre, valor, periodo), ej. ("P", 146111.54, 0); None = no mostrar
    mostrar_tasa : False cuando la tasa no interviene (ej. hallar n por el último pago)
    """
    direccion = 1 if sentido == "ingreso" else -1
    pagos = tabla_de_pagos(serie)
    maximo = max(abs(p.monto) for p in pagos) or 1.0
    final = serie.periodo_final
    nivel_base = direccion * serie.A_prima / maximo
    descomponer = serie.A_prima > 0 and serie.G > 0

    # Si hay muchas cuotas, los textos se ponen verticales y se rotulan algunas
    vertical = len(pagos) > 12
    salto = max(1, math.ceil(len(pagos) / MAX_ETIQUETAS))

    fig = go.Figure()

    # Línea de tiempo
    fig.add_shape(type="line", x0=0, x1=final, y0=0, y1=0,
                  line={"color": COLOR_LINEA, "width": 2})

    # Nivel de la serie base A'
    if descomponer:
        fig.add_shape(type="line", x0=serie.inicio - 0.4, x1=final + 0.4,
                      y0=nivel_base, y1=nivel_base,
                      line={"color": COLOR_BASE, "width": 1, "dash": "dash"}, opacity=0.6)

    # Una flecha por cuota
    hay_negativas = False
    for indice, pago in enumerate(pagos):
        altura = direccion * pago.monto / maximo
        if altura == 0:
            continue

        if pago.monto < 0 or not descomponer or pago.gradiente == 0:
            # Cuota simple (primera cuota, sin gradiente o con signo invertido)
            color = COLOR_BASE if pago.monto > 0 else COLOR_CUOTA_NEGATIVA
            hay_negativas = hay_negativas or pago.monto < 0
            _flecha(fig, pago.periodo, altura, color)
        elif pago.gradiente > 0:
            # Creciente: base azul + gradiente naranja encima
            _tramo(fig, pago.periodo, 0, nivel_base, COLOR_BASE)
            _flecha(fig, pago.periodo, altura, COLOR_GRADIENTE, desde=nivel_base)
        else:
            # Decreciente: cuota azul + lo que restó el gradiente, punteado naranja
            _flecha(fig, pago.periodo, altura, COLOR_BASE)
            _tramo(fig, pago.periodo, altura, nivel_base, COLOR_GRADIENTE, punteado=True)

        if indice % salto == 0 or indice == len(pagos) - 1:
            color_texto = COLOR_BASE if pago.monto > 0 else COLOR_CUOTA_NEGATIVA
            _etiqueta(fig, pago.periodo, altura, formato_numero(pago.monto), color_texto, vertical)

    # Valor equivalente en sentido contrario a las cuotas
    if equivalente is not None:
        nombre, valor, periodo = equivalente
        color = COLORES_EQUIVALENTE.get(nombre, COLOR_LINEA)
        signo = 1 if valor >= 0 else -1
        altura = -direccion * signo * ALTURA_EQUIVALENTE
        _flecha(fig, periodo, altura, color)
        _etiqueta(fig, periodo, altura, f"<b>{nombre} = {formato_numero(valor)}</b>",
                  color, vertical=False)

    # Leyenda (solo los elementos que aparecen en el diagrama)
    _entrada_leyenda(fig, "Base A'" if descomponer else "Cuotas", COLOR_BASE)
    if descomponer:
        _entrada_leyenda(fig, "Gradiente (suma)" if serie.signo > 0 else "Gradiente (resta)",
                         COLOR_GRADIENTE, punteado=serie.signo < 0)
    if hay_negativas:
        _entrada_leyenda(fig, "Cuota negativa", COLOR_CUOTA_NEGATIVA)
    if equivalente is not None:
        nombres = {"P": "Valor presente P", "F": "Valor futuro F"}
        _entrada_leyenda(fig, nombres.get(equivalente[0], equivalente[0]),
                         COLORES_EQUIVALENTE.get(equivalente[0], COLOR_LINEA))

    # Tasa de interés, arriba del gráfico
    if mostrar_tasa:
        fig.add_annotation(
            x=0.5, y=1.08, xref="paper", yref="paper", showarrow=False,
            text=f"<b>i = {formato_porcentaje(serie.i)} por periodo</b>",
            font={"size": 14, "color": COLORES["i"].hex},
        )

    limite = 2.0 if vertical else 1.6
    fig.update_xaxes(
        title="Periodos", tickmode="linear", tick0=0,
        dtick=1 if final <= 30 else math.ceil(final / 30),
        range=[-0.8, final + 0.8], showgrid=False, zeroline=False,
    )
    fig.update_yaxes(visible=False, range=[-limite, limite])
    fig.update_layout(
        height=460, showlegend=True,
        legend={"orientation": "h", "x": 0.5, "xanchor": "center", "y": -0.22},
        margin={"l": 20, "r": 20, "t": 60, "b": 80},
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

"""
Diagrama de flujo de caja, como en el libro:

    - Línea de tiempo horizontal de 0 a n.
    - Una flecha vertical por cuota, con su valor:
        hacia ARRIBA  = ingreso (cobro, depósito recibido)
        hacia ABAJO   = egreso  (pago)
    - La altura de cada flecha es proporcional a su monto, así se ve
      claramente si el gradiente crece o decrece.
    - Opcionalmente, una flecha roja en sentido contrario con el valor
      equivalente (P en el periodo 0, o F en el periodo final).
    - La tasa i indicada arriba.
"""

import math

import plotly.graph_objects as go

from gradiente.procedimiento import formato_numero, formato_porcentaje
from gradiente.serie import SerieGradiente, tabla_de_pagos


COLOR_CUOTA = "#2563eb"         # azul: cuotas normales
COLOR_CUOTA_NEGATIVA = "#f59e0b"  # naranja: cuotas que cambiaron de signo
COLOR_EQUIVALENTE = "#dc2626"   # rojo: valor equivalente (P o F)
COLOR_LINEA = "#6b7280"         # gris: línea de tiempo

MAX_ETIQUETAS = 24              # si hay más cuotas, se rotulan solo algunas
ALTURA_EQUIVALENTE = 1.25       # altura de la flecha de P o F (las cuotas miden hasta 1)


def _flecha(fig: go.Figure, x: float, altura: float, color: str) -> None:
    """Dibuja una flecha vertical desde la línea de tiempo (y = 0) hasta 'altura'."""
    fig.add_annotation(
        x=x, y=altura, ax=x, ay=0,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=2.5,
        arrowcolor=color, text="",
    )


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


def diagrama_flujo(serie: SerieGradiente, sentido: str = "egreso",
                   equivalente: tuple[str, float, int] | None = None) -> go.Figure:
    """
    Construye el diagrama de flujo de caja de la serie.

    serie       : la serie en gradiente
    sentido     : "ingreso" (flechas hacia arriba) o "egreso" (hacia abajo)
    equivalente : (nombre, valor, periodo), ej. ("P", 146111.54, 0); None = no mostrar
    """
    direccion = 1 if sentido == "ingreso" else -1
    pagos = tabla_de_pagos(serie)
    maximo = max(abs(p.monto) for p in pagos) or 1.0
    final = serie.periodo_final

    # Si hay muchas cuotas, los textos se ponen verticales y se rotulan algunas
    vertical = len(pagos) > 12
    salto = max(1, math.ceil(len(pagos) / MAX_ETIQUETAS))

    fig = go.Figure()

    # Línea de tiempo
    fig.add_shape(type="line", x0=0, x1=final, y0=0, y1=0,
                  line={"color": COLOR_LINEA, "width": 2})

    # Una flecha por cuota (una cuota negativa apunta al lado contrario)
    for indice, pago in enumerate(pagos):
        altura = direccion * pago.monto / maximo
        if altura == 0:
            continue
        color = COLOR_CUOTA if pago.monto > 0 else COLOR_CUOTA_NEGATIVA
        _flecha(fig, pago.periodo, altura, color)
        if indice % salto == 0 or indice == len(pagos) - 1:
            _etiqueta(fig, pago.periodo, altura, formato_numero(pago.monto), color, vertical)

    # Valor equivalente en sentido contrario a las cuotas
    if equivalente is not None:
        nombre, valor, periodo = equivalente
        signo = 1 if valor >= 0 else -1
        altura = -direccion * signo * ALTURA_EQUIVALENTE
        _flecha(fig, periodo, altura, COLOR_EQUIVALENTE)
        _etiqueta(fig, periodo, altura, f"<b>{nombre} = {formato_numero(valor)}</b>",
                  COLOR_EQUIVALENTE, vertical=False)

    # Tasa de interés, arriba del gráfico
    fig.add_annotation(
        x=0.5, y=1.08, xref="paper", yref="paper", showarrow=False,
        text=f"<b>i = {formato_porcentaje(serie.i)} por periodo</b>",
        font={"size": 14},
    )

    limite = 2.0 if vertical else 1.6
    fig.update_xaxes(
        title="Periodos", tickmode="linear", tick0=0,
        dtick=1 if final <= 30 else math.ceil(final / 30),
        range=[-0.8, final + 0.8], showgrid=False, zeroline=False,
    )
    fig.update_yaxes(visible=False, range=[-limite, limite])
    fig.update_layout(
        height=430, showlegend=False,
        margin={"l": 20, "r": 20, "t": 60, "b": 40},
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig

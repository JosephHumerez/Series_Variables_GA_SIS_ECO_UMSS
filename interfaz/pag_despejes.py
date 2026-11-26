"""
Página 3: Despejes (cálculos inversos).

El usuario elige qué incógnita hallar. Cada tipo de despeje tiene su propia
función "_modo_..." que:
    1. pide los datos necesarios,
    2. llama al núcleo (gradiente.despejes / gradiente.despejes_numericos),
    3. devuelve una "Salida" con todo lo que hay que mostrar.

Luego _mostrar_salida() dibuja los resultados, el diagrama, el procedimiento,
la verificación (cálculo directo con la serie hallada) y la tabla de pagos.

Los valores por defecto de cada modo son ejercicios del libro (pág. 35).
"""

from dataclasses import dataclass, field

import streamlit as st

from gradiente import despejes as d
from gradiente import despejes_numericos as dn
from gradiente.procedimiento import (
    Paso, formato_numero, formato_porcentaje, procedimiento_despeje,
    procedimiento_n_ultimo, procedimiento_periodos, procedimiento_serie, procedimiento_tasa,
)
from gradiente.serie import SerieGradiente, calcular
from interfaz.comun import mostrar_pasos, mostrar_tabla_pagos, pedir_tasa
from interfaz.diagrama import diagrama_flujo


NOMBRE_DATO = {"P": "P (valor presente)", "F": "F (valor futuro)", "A": "A (anualidad equivalente)"}


@dataclass
class Salida:
    """Todo lo que la página muestra después de resolver un despeje."""
    metricas: list[tuple[str, str]]          # (etiqueta, valor) de los recuadros de resultado
    pasos: list[Paso]                        # procedimiento del despeje
    serie: SerieGradiente                    # serie completa ya resuelta
    sentido: str                             # "ingreso" o "egreso" (para el diagrama)
    dato: str | None = None                  # P, F o A (para marcarlo en el diagrama)
    avisos: list[str] = field(default_factory=list)
    con_tasa: bool = True                    # False si la tasa no interviene (n por último pago)


# ===========================================================================
# Controles reutilizables
# ===========================================================================

def _pedir_dato(prefijo: str, dato_defecto: str, valor_defecto: float) -> tuple[str, float]:
    """Qué valor se conoce (P, F o A) y cuánto vale."""
    dato = st.radio(
        "Valor conocido", list(NOMBRE_DATO), index=list(NOMBRE_DATO).index(dato_defecto),
        format_func=lambda x: NOMBRE_DATO[x], key=f"{prefijo}_dato",
    )
    valor = st.number_input(f"Valor de {dato}", value=valor_defecto, step=100.0,
                            format="%.2f", key=f"{prefijo}_valor")
    return dato, valor


def _pedir_A_prima(prefijo: str, defecto: float) -> float:
    return st.number_input("Primer pago, A'", value=defecto, step=100.0,
                           format="%.2f", key=f"{prefijo}_A")


def _pedir_G(prefijo: str, defecto: float) -> float:
    return st.number_input("Gradiente, G", min_value=0.0, value=defecto, step=100.0,
                           format="%.2f", key=f"{prefijo}_G",
                           help="Siempre positivo. El sentido se elige en «Tipo de gradiente».")


def _pedir_tipo(prefijo: str, defecto: str) -> str:
    opciones = ["Creciente", "Decreciente"]
    return st.radio("Tipo de gradiente", opciones, index=opciones.index(defecto),
                    horizontal=True, key=f"{prefijo}_tipo").lower()


def _pedir_n(prefijo: str, defecto: int) -> int:
    return int(st.number_input("Número de cuotas, n", min_value=1, value=defecto,
                               step=1, key=f"{prefijo}_n"))


def _opciones_avanzadas(prefijo: str, con_inicio: bool = True) -> tuple[int, str]:
    """Periodo de la primera cuota (series diferidas) y sentido del flujo. Devuelve (inicio, sentido)."""
    with st.expander("Opciones avanzadas: serie diferida y diagrama"):
        c1, c2 = st.columns(2)
        inicio = 1
        if con_inicio:
            inicio = int(c1.number_input(
                "Periodo de la primera cuota", min_value=1, value=1, step=1,
                key=f"{prefijo}_inicio", help="1 = serie normal. Mayor que 1 = serie diferida.",
            ))
        sentido = c2.radio("Las cuotas son", ["Egresos (↓)", "Ingresos (↑)"],
                           key=f"{prefijo}_sentido")
    return inicio, "ingreso" if "Ingresos" in sentido else "egreso"


def _metricas_n(n_exacto: float, n_sugerido: int, es_entero: bool) -> list[tuple[str, str]]:
    """Recuadros para n: el entero si es exacto; si no, el exacto y el sugerido."""
    if es_entero:
        return [("Número de periodos, n", str(n_sugerido))]
    return [("n exacto", formato_numero(n_exacto, 4)), ("n sugerido (entero)", str(n_sugerido))]


# ===========================================================================
# Modos de despeje
# ===========================================================================

def _modo_n_ultimo() -> Salida:
    """n a partir del primer pago, el último pago y G (Ejercicio 1)."""
    p = "des1"
    c1, c2, c3 = st.columns(3)
    with c1:
        A_prima = _pedir_A_prima(p, 30_000.0)
    with c2:
        ultimo = st.number_input("Último pago, Xₙ", value=10_000.0, step=100.0,
                                 format="%.2f", key=f"{p}_ultimo")
    with c3:
        G = _pedir_G(p, 2_000.0)
    _, sentido = _opciones_avanzadas(p, con_inicio=False)

    r = d.n_por_ultimo_pago(A_prima, ultimo, G)
    metricas = _metricas_n(r.n_exacto, r.n_sugerido, r.es_entero)
    metricas.append(("Tipo de gradiente", r.tipo.capitalize()))
    avisos = [] if r.es_entero else [
        f"n = {formato_numero(r.n_exacto, 4)} no es entero: el último pago no encaja "
        f"exactamente con el gradiente. El diagrama y la tabla usan n = {r.n_sugerido}."
    ]
    serie = SerieGradiente(A_prima, G, 0.0, r.n_sugerido, r.tipo)
    return Salida(metricas, procedimiento_n_ultimo(r, A_prima, ultimo, G), serie,
                  sentido, avisos=avisos, con_tasa=False)


def _modo_base() -> Salida:
    """A' conociendo G y P, F o A (Ejercicio 6)."""
    p = "des2"
    c1, c2, c3 = st.columns(3)
    with c1:
        dato, valor = _pedir_dato(p, "P", 8_000.0)
    with c2:
        G = _pedir_G(p, 500.0)
        tipo = _pedir_tipo(p, "Creciente")
    with c3:
        i = pedir_tasa(p, 15.0)
        n = _pedir_n(p, 5)
    inicio, sentido = _opciones_avanzadas(p)

    r = d.despejar_base(valor, dato, G, tipo, i, n, inicio)
    return Salida([("Primer pago, A'", formato_numero(r.A_prima))],
                  procedimiento_despeje(r), r.serie, sentido, dato)


def _modo_gradiente() -> Salida:
    """G conociendo A' y P, F o A (Ejercicio 2 al revés)."""
    p = "des3"
    c1, c2, c3 = st.columns(3)
    with c1:
        dato, valor = _pedir_dato(p, "F", 538_445.20)
    with c2:
        A_prima = _pedir_A_prima(p, 27_000.0)
    with c3:
        i = pedir_tasa(p, 0.66)
        n = _pedir_n(p, 12)
    inicio, sentido = _opciones_avanzadas(p)

    r = d.despejar_gradiente(valor, dato, A_prima, i, n, inicio)
    return Salida([("Gradiente, G", formato_numero(r.G)), ("Tipo de gradiente", r.tipo.capitalize())],
                  procedimiento_despeje(r), r.serie, sentido, dato)


def _modo_sistema() -> Salida:
    """A' y G a la vez: P, F o A más una cuota conocida X_k (Ejercicio 1)."""
    p = "des4"
    c1, c2, c3 = st.columns(3)
    with c1:
        dato, valor = _pedir_dato(p, "P", 146_111.54)
    with c2:
        k = int(st.number_input("Cuota conocida, k", min_value=1, value=11, step=1,
                                key=f"{p}_k", help="Número de la cuota cuyo monto se conoce. "
                                                   "Para el último pago, k = n."))
        X_k = st.number_input("Monto de esa cuota, Xₖ", value=10_000.0, step=100.0,
                              format="%.2f", key=f"{p}_Xk")
    with c3:
        i = pedir_tasa(p, 9.27)
        n = _pedir_n(p, 11)
    inicio, sentido = _opciones_avanzadas(p)

    r = d.despejar_base_y_gradiente(valor, dato, k, X_k, i, n, inicio)
    metricas = [("Primer pago, A'", formato_numero(r.A_prima)),
                ("Gradiente, G", formato_numero(r.G)),
                ("Tipo de gradiente", r.tipo.capitalize())]
    return Salida(metricas, procedimiento_despeje(r), r.serie, sentido, dato)


def _modo_tasa() -> Salida:
    """i por métodos numéricos (Ejercicio 2 al revés)."""
    p = "des5"
    c1, c2, c3 = st.columns(3)
    with c1:
        dato, valor = _pedir_dato(p, "F", 538_445.20)
    with c2:
        A_prima = _pedir_A_prima(p, 27_000.0)
        G = _pedir_G(p, 3_000.0)
    with c3:
        tipo = _pedir_tipo(p, "Creciente")
        n = _pedir_n(p, 12)
    inicio, sentido = _opciones_avanzadas(p)

    r = dn.despejar_tasa(valor, dato, A_prima, G, tipo, n, inicio)
    metricas = [("Tasa por periodo, i", formato_porcentaje(r.i))]
    if r.interpolacion is not None:
        metricas.append(("i por interpolación (tabla)", formato_porcentaje(r.interpolacion.i_interpolada)))
    return Salida(metricas, procedimiento_tasa(r), r.serie, sentido, dato, avisos=list(r.avisos))


def _modo_n_numerico() -> Salida:
    """n por métodos numéricos conociendo P, F o A (Ejercicio 1 al revés)."""
    p = "des6"
    c1, c2, c3 = st.columns(3)
    with c1:
        dato, valor = _pedir_dato(p, "P", 146_111.54)
    with c2:
        A_prima = _pedir_A_prima(p, 30_000.0)
        G = _pedir_G(p, 2_000.0)
    with c3:
        tipo = _pedir_tipo(p, "Decreciente")
        i = pedir_tasa(p, 9.27)
    inicio, sentido = _opciones_avanzadas(p)

    r = dn.despejar_periodos(valor, dato, A_prima, G, tipo, i, inicio)
    avisos = list(r.avisos)
    if not r.es_entero:
        avisos.insert(0, f"Con n = {r.n_sugerido}, {dato} sería {formato_numero(r.valor_con_sugerido)} "
                         f"en lugar de {formato_numero(r.valor_dato)}. El diagrama y la tabla usan n = {r.n_sugerido}.")
    return Salida(_metricas_n(r.n_exacto, r.n_sugerido, r.es_entero),
                  procedimiento_periodos(r), r.serie_sugerida, sentido, dato, avisos=avisos)


# Menú de despejes: texto que ve el usuario -> función que lo resuelve
MODOS = {
    "n: con el primer y el último pago": _modo_n_ultimo,
    "A': conociendo G y P, F o A": _modo_base,
    "G: conociendo A' y P, F o A": _modo_gradiente,
    "A' y G: conociendo P, F o A y una cuota Xₖ": _modo_sistema,
    "i: tasa de interés (método numérico)": _modo_tasa,
    "n: conociendo P, F o A (método numérico)": _modo_n_numerico,
}


# ===========================================================================
# Página
# ===========================================================================

def _mostrar_salida(s: Salida) -> None:
    """Resultados, avisos, diagrama y pestañas de detalle."""
    st.divider()
    for columna, (etiqueta, valor) in zip(st.columns(len(s.metricas)), s.metricas):
        columna.metric(etiqueta, valor)

    resultado = calcular(s.serie)
    # Se combinan los avisos del despeje con los de las cuotas, sin repetir
    for aviso in dict.fromkeys([*s.avisos, *resultado.avisos]):
        st.warning(aviso, icon=":material/warning:")

    equivalente = {
        "P": ("P", resultado.P, 0),
        "F": ("F", resultado.F, s.serie.periodo_final),
    }.get(s.dato)
    st.plotly_chart(diagrama_flujo(s.serie, s.sentido, equivalente, mostrar_tasa=s.con_tasa),
                    width="stretch", key="des_diagrama")

    pestañas = [":material/format_list_numbered: Procedimiento"]
    if s.con_tasa:
        pestañas.append(":material/verified: Verificación")
    pestañas.append(":material/table_chart: Tabla de pagos")
    tabs = st.tabs(pestañas)

    with tabs[0]:
        mostrar_pasos(s.pasos)
    if s.con_tasa:
        with tabs[1]:
            st.caption("Cálculo directo con la serie hallada: debe reproducir el dato conocido.")
            mostrar_pasos(procedimiento_serie(resultado))
    with tabs[-1]:
        mostrar_tabla_pagos(resultado.pagos)


def mostrar() -> None:
    st.title(":material/function: Despejes")
    st.markdown("Halla una incógnita de la serie a partir de los demás datos. "
                "Cada opción viene cargada con un ejercicio del libro.")

    nombre = st.selectbox("¿Qué deseas hallar?", list(MODOS), key="des_modo")
    try:
        salida = MODOS[nombre]()
    except ValueError as error:
        st.error(str(error), icon=":material/error:")
        return
    _mostrar_salida(salida)

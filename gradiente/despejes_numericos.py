"""
Despejes que NO tienen fórmula directa: la tasa i y el número de periodos n
conociendo P, F o A.

Se parte de la misma ecuación que en despejes.py:

    Valor = A'·c_base(i, n) ± G·c_gradiente(i, n)

pero ahora la incógnita está dentro de los factores, así que se busca el
valor que hace cero la función:

    func(x) = A'·c_base ± G·c_gradiente - Valor

usando los métodos de numericos.py (bisección + Newton-Raphson).

Rangos de búsqueda:
    i : de 0 % a 300 % por periodo
    n : de 1 a 1 000 periodos
"""

from bisect import bisect_left
from dataclasses import dataclass

from gradiente import numericos
from gradiente.despejes import coeficientes
from gradiente.serie import SerieGradiente, revisar_cuotas


I_MIN, I_MAX, PASO_I = 0.0, 3.0, 0.001
N_MIN, N_MAX, PASO_N = 1.0, 1000.0, 0.25

# Diferencia máxima (en dinero) para considerar que dos valores son iguales
TOLERANCIA_CENTAVO = 0.01

# Tasas que aparecen en las tablas de factores, usadas para la interpolación lineal.
# (Se pueden ajustar para que coincidan exactamente con la Tabla 1 del libro.)
TASAS_DE_TABLA = (
    0.0025, 0.005, 0.0075, 0.01, 0.0125, 0.015, 0.0175, 0.02, 0.025, 0.03,
    0.035, 0.04, 0.045, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13,
    0.14, 0.15, 0.16, 0.18, 0.20, 0.22, 0.24, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50,
)


def valor_equivalente(dato: str, A_prima: float, g_con_signo: float,
                      i: float, n: float, inicio: int = 1) -> float:
    """Calcula P, F o A de la serie:  A'·c_base + g·c_gradiente  (n puede ser decimal)."""
    c_base, c_grad = coeficientes(dato, i, n, inicio)
    return A_prima * c_base + g_con_signo * c_grad


def _aviso_otras_soluciones(cantidad: int, incognita: str) -> tuple[str, ...]:
    if cantidad == 0:
        return ()
    return (
        f"Existen {cantidad} valor(es) más de {incognita} que también cumplen la "
        f"ecuación (ocurre cuando las cuotas cambian de signo). Se muestra el menor.",
    )


# ---------------------------------------------------------------------------
# Resultados
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Interpolacion:
    """Interpolación lineal entre dos tasas de tabla, como se hace a mano."""
    i1: float
    i2: float
    valor1: float          # valor equivalente con i1
    valor2: float          # valor equivalente con i2
    i_interpolada: float   # i1 + (i2 - i1)·(Valor - valor1)/(valor2 - valor1)


@dataclass(frozen=True)
class ResultadoTasa:
    i: float                          # tasa exacta (método numérico)
    dato: str
    valor_dato: float
    serie: SerieGradiente             # serie resuelta con la tasa hallada
    iter_biseccion: int
    iter_newton: int
    interpolacion: Interpolacion | None
    avisos: tuple[str, ...]


@dataclass(frozen=True)
class ResultadoPeriodos:
    n_exacto: float                   # valor exacto (puede tener decimales)
    n_sugerido: int                   # entero más cercano
    es_entero: bool
    dato: str
    valor_dato: float
    valor_con_sugerido: float         # cuánto vale el dato usando n_sugerido
    serie_sugerida: SerieGradiente    # serie con n_sugerido
    iter_biseccion: int
    iter_newton: int
    avisos: tuple[str, ...]


# ---------------------------------------------------------------------------
# 1. Despejar la tasa i
# ---------------------------------------------------------------------------

def despejar_tasa(valor: float, dato: str, A_prima: float, G: float, tipo: str,
                  n: int, inicio: int = 1) -> ResultadoTasa:
    """Halla la tasa i por periodo conociendo A', G, n y uno de P, F o A."""
    # Serie provisional (i cualquiera) solo para validar datos y obtener el signo
    signo = SerieGradiente(A_prima, G, 0.1, n, tipo, inicio).signo
    g = signo * G
    if dato.strip().upper() == "A" and g == 0:
        raise ValueError("Sin gradiente (G = 0), la anualidad A no depende de i: no se puede despejar.")

    def func(i):
        return valor_equivalente(dato, A_prima, g, i, n, inicio) - valor

    try:
        r = numericos.resolver(func, I_MIN, I_MAX, PASO_I)
    except ValueError:
        raise ValueError(
            "No existe una tasa entre 0 % y 300 % por periodo que cumpla los datos. "
            "Revise que el valor dado sea coherente con los pagos."
        ) from None

    serie = SerieGradiente(A_prima, G, r.raiz, n, tipo, inicio)
    return ResultadoTasa(
        i=r.raiz, dato=dato.strip().upper(), valor_dato=valor, serie=serie,
        iter_biseccion=r.iter_biseccion, iter_newton=r.iter_newton,
        interpolacion=interpolar_tasa(r.raiz, valor, dato, A_prima, g, n, inicio),
        avisos=_aviso_otras_soluciones(r.otras_soluciones, "i") + revisar_cuotas(serie),
    )


def interpolar_tasa(i_exacta: float, valor: float, dato: str, A_prima: float,
                    g_con_signo: float, n: int, inicio: int = 1) -> Interpolacion | None:
    """
    Interpolación lineal entre las dos tasas de tabla que encierran a i_exacta:

        i ≈ i1 + (i2 - i1) · (Valor - V1) / (V2 - V1)

    Devuelve None si i_exacta está fuera de la tabla o coincide con una tasa de tabla.
    """
    pos = bisect_left(TASAS_DE_TABLA, i_exacta)
    if pos == 0 or pos >= len(TASAS_DE_TABLA):
        return None
    if abs(TASAS_DE_TABLA[pos] - i_exacta) < 1e-9:
        return None
    i1, i2 = TASAS_DE_TABLA[pos - 1], TASAS_DE_TABLA[pos]
    v1 = valor_equivalente(dato, A_prima, g_con_signo, i1, n, inicio)
    v2 = valor_equivalente(dato, A_prima, g_con_signo, i2, n, inicio)
    return Interpolacion(i1, i2, v1, v2, i1 + (i2 - i1) * (valor - v1) / (v2 - v1))


# ---------------------------------------------------------------------------
# 2. Despejar el número de periodos n
# ---------------------------------------------------------------------------

def despejar_periodos(valor: float, dato: str, A_prima: float, G: float, tipo: str,
                      i: float, inicio: int = 1) -> ResultadoPeriodos:
    """
    Halla n conociendo A', G, i y uno de P, F o A.

    Como n representa cuotas enteras, se devuelve el valor exacto y el entero
    más cercano, junto con el valor que resultaría usando ese entero.
    """
    signo = SerieGradiente(A_prima, G, i, 1, tipo, inicio).signo
    g = signo * G

    def func(n):
        return valor_equivalente(dato, A_prima, g, i, n, inicio) - valor

    try:
        r = numericos.resolver(func, N_MIN, N_MAX, PASO_N)
    except ValueError:
        raise ValueError(
            "No existe un número de periodos entre 1 y 1 000 que cumpla los datos. "
            "Revise que el valor dado sea coherente con los pagos y la tasa."
        ) from None

    n_sugerido = max(1, round(r.raiz))
    valor_con_sugerido = valor_equivalente(dato, A_prima, g, i, n_sugerido, inicio)
    serie = SerieGradiente(A_prima, G, i, n_sugerido, tipo, inicio)
    return ResultadoPeriodos(
        n_exacto=r.raiz, n_sugerido=n_sugerido,
        # Los datos del libro vienen redondeados al centavo, por eso n se
        # considera entero si con n_sugerido el valor coincide al centavo.
        es_entero=abs(valor_con_sugerido - valor) < TOLERANCIA_CENTAVO,
        dato=dato.strip().upper(), valor_dato=valor,
        valor_con_sugerido=valor_con_sugerido,
        serie_sugerida=serie,
        iter_biseccion=r.iter_biseccion, iter_newton=r.iter_newton,
        avisos=_aviso_otras_soluciones(r.otras_soluciones, "n") + revisar_cuotas(serie),
    )

"""
Factores financieros de capitalización discreta.

Notación del libro (Ingeniería Económica, M. Sc. Emir Vargas Peredo, Unidad 2):
    (X/Y, i, n)  se lee "X dado Y, a la tasa i, durante n periodos".
    Ejemplo: (P/A, i, n) convierte una anualidad A en un valor presente P.

Todas las funciones reciben:
    i : tasa efectiva POR PERIODO, en forma decimal (9,27 % -> 0.0927)
    n : número de periodos (normalmente entero; se acepta decimal porque
        los métodos numéricos de despeje lo necesitan)

Todas devuelven el factor con precisión completa. El redondeo a 5 decimales
(como en las tablas del libro) se hace solo al MOSTRARLO, nunca al calcular.

Convención: anualidades vencidas (el primer pago ocurre al final del periodo 1).
"""

# Los nombres P_A, A_G, etc. imitan a propósito la notación del libro (P/A, A/G),
# por eso se desactiva la regla de pylint que exige nombres en minúsculas.
# pylint: disable=invalid-name

import math


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def _validar(i: float, n: float) -> None:
    """Verifica que la tasa y los periodos tengan sentido financiero."""
    if i <= -1:
        raise ValueError(f"La tasa i debe ser mayor que -100 %. Se recibió i = {i}.")
    if n < 0:
        raise ValueError(f"El número de periodos n no puede ser negativo. Se recibió n = {n}.")


def _crecimiento(i: float, n: float) -> float:
    """
    Calcula  (1 + i)^n - 1  de forma numéricamente precisa.

    Matemáticamente es lo mismo que escribir (1 + i) ** n - 1, pero cuando i
    es muy pequeña esa resta pierde precisión en la computadora. Las funciones
    math.expm1 y math.log1p existen justamente para evitar ese problema.
    """
    return math.expm1(n * math.log1p(i))


# ---------------------------------------------------------------------------
# 1. Factores de PAGO ÚNICO
# ---------------------------------------------------------------------------

def F_P(i: float, n: float) -> float:
    """
    (F/P, i, n) — Factor de capitalización de pago único.
    Lleva un monto del periodo 0 al periodo n.

        F/P = (1 + i)^n
    """
    _validar(i, n)
    return (1 + i) ** n


def P_F(i: float, n: float) -> float:
    """
    (P/F, i, n) — Factor de actualización (valor presente) de pago único.
    Trae un monto del periodo n al periodo 0.

        P/F = 1 / (1 + i)^n
    """
    _validar(i, n)
    return 1 / (1 + i) ** n


# ---------------------------------------------------------------------------
# 2. Factores de SERIE UNIFORME (anualidades vencidas)
# ---------------------------------------------------------------------------

def P_A(i: float, n: float) -> float:
    """
    (P/A, i, n) — Valor presente de una serie uniforme.
    Convierte n pagos iguales A (periodos 1..n) en un valor P en el periodo 0.

        P/A = [(1 + i)^n - 1] / [i (1 + i)^n]

    Caso límite i = 0:  P/A = n
    """
    _validar(i, n)
    if i == 0:
        return n
    return _crecimiento(i, n) / (i * (1 + i) ** n)


def A_P(i: float, n: float) -> float:
    """
    (A/P, i, n) — Factor de recuperación de capital.
    Convierte un valor presente P en n pagos iguales A.

        A/P = [i (1 + i)^n] / [(1 + i)^n - 1]
    """
    return 1 / P_A(i, n)


def F_A(i: float, n: float) -> float:
    """
    (F/A, i, n) — Valor futuro de una serie uniforme.
    Convierte n pagos iguales A en un valor F en el periodo n.

        F/A = [(1 + i)^n - 1] / i

    Caso límite i = 0:  F/A = n
    """
    _validar(i, n)
    if i == 0:
        return n
    return _crecimiento(i, n) / i


def A_F(i: float, n: float) -> float:
    """
    (A/F, i, n) — Factor de fondo de amortización.
    Convierte un valor futuro F en n pagos iguales A.

        A/F = i / [(1 + i)^n - 1]
    """
    return 1 / F_A(i, n)


# ---------------------------------------------------------------------------
# 3. Factores de GRADIENTE ARITMÉTICO
#
#    Se aplican a la SERIE GRADIENTE PURA:
#        periodo:  1    2    3    ...   n
#        flujo:    0    G    2G   ...   (n-1)G
#
#    IMPORTANTE: el valor presente del gradiente queda ubicado UN periodo
#    antes del primer pago de la serie (en el periodo 0 si la serie empieza
#    en el periodo 1).
# ---------------------------------------------------------------------------

def P_G(i: float, n: float) -> float:
    """
    (P/G, i, n) — Valor presente de un gradiente aritmético.
    Convierte la serie gradiente pura 0, G, 2G, ..., (n-1)G en P.

        P/G = [(1 + i)^n - 1 - n·i] / [i² (1 + i)^n]

    Caso límite i = 0:  P/G = n(n - 1) / 2
    """
    _validar(i, n)
    if i == 0:
        return n * (n - 1) / 2
    return (_crecimiento(i, n) - n * i) / (i ** 2 * (1 + i) ** n)


def A_G(i: float, n: float) -> float:
    """
    (A/G, i, n) — Conversión de gradiente a serie uniforme.
    Convierte la serie gradiente pura en una anualidad equivalente A_G.
    Es el paso intermedio que usa el libro:  A = A' ± G·(A/G, i, n)

        A/G = 1/i - n / [(1 + i)^n - 1]

    Caso límite i = 0:  A/G = (n - 1) / 2
    """
    _validar(i, n)
    if n == 0:
        raise ValueError("(A/G, i, n) no está definido para n = 0.")
    if i == 0:
        return (n - 1) / 2
    return 1 / i - n / _crecimiento(i, n)


def F_G(i: float, n: float) -> float:
    """
    (F/G, i, n) — Valor futuro de un gradiente aritmético.
    Convierte la serie gradiente pura en un valor F en el periodo n.

        F/G = [(1 + i)^n - 1 - n·i] / i²

    Caso límite i = 0:  F/G = n(n - 1) / 2
    """
    _validar(i, n)
    if i == 0:
        return n * (n - 1) / 2
    return (_crecimiento(i, n) - n * i) / i ** 2

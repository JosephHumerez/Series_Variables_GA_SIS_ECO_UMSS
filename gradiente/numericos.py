"""
Métodos numéricos para hallar raíces de ecuaciones:  func(x) = 0

Se usan cuando la incógnita (la tasa i o el número de periodos n) está
"atrapada" dentro de los factores y no se puede despejar con álgebra.

Estrategia de resolver():
    1. BÚSQUEDA DE INTERVALOS: se recorre el rango [a, b] a pasos pequeños
       buscando dónde func cambia de signo. Cada cambio de signo encierra
       una solución. Si hay más de una, se avisa.
    2. BISECCIÓN: se parte el intervalo por la mitad una y otra vez,
       quedándose con la mitad donde sigue el cambio de signo.
       Es lento pero SIEMPRE converge.
    3. NEWTON-RAPHSON: desde el punto que dejó la bisección, se afina con
           x_nuevo = x - func(x) / func'(x)
       Es muy rápido cuando ya está cerca de la solución.
       Si Newton falla o se sale del intervalo, se sigue con bisección.
"""

from dataclasses import dataclass
from typing import Callable

Funcion = Callable[[float], float]


@dataclass(frozen=True)
class ResultadoRaiz:
    """Solución encontrada y cómo se llegó a ella."""
    raiz: float
    iter_biseccion: int
    iter_newton: int
    otras_soluciones: int   # cuántos cambios de signo adicionales se encontraron


# ---------------------------------------------------------------------------
# 1. Búsqueda de intervalos con cambio de signo
# ---------------------------------------------------------------------------

def buscar_intervalos(func: Funcion, a: float, b: float, paso: float) -> list[tuple[float, float]]:
    """
    Recorre [a, b] y devuelve los intervalos (x0, x1) donde func cambia de
    signo. Si func vale exactamente 0 en un punto, se devuelve (x, x).
    """
    intervalos = []
    x0, f0 = a, func(a)
    k = 1
    while True:
        x1 = min(a + k * paso, b)     # se multiplica (no se suma) para no acumular error
        f1 = func(x1)
        if f0 == 0:
            intervalos.append((x0, x0))
        elif f0 * f1 < 0:
            intervalos.append((x0, x1))
        if x1 >= b:
            if f1 == 0:
                intervalos.append((x1, x1))
            return intervalos
        x0, f0 = x1, f1
        k += 1


# ---------------------------------------------------------------------------
# 2. Bisección
# ---------------------------------------------------------------------------

def biseccion(func: Funcion, a: float, b: float,
              tol: float = 1e-13, max_iter: int = 200) -> tuple[float, float, float, int]:
    """
    Achica el intervalo [a, b] (con cambio de signo) hasta que mida menos que tol.
    Devuelve (punto medio, a final, b final, iteraciones).
    """
    fa = func(a)
    if fa * func(b) > 0:
        raise ValueError("La bisección necesita un cambio de signo entre a y b.")
    iteraciones = 0
    while (b - a) > tol * max(1.0, abs(a)) and iteraciones < max_iter:
        medio = (a + b) / 2
        fm = func(medio)
        if fm == 0:
            return medio, medio, medio, iteraciones + 1
        if fa * fm < 0:
            b = medio                 # la raíz está en la mitad izquierda
        else:
            a, fa = medio, fm         # la raíz está en la mitad derecha
        iteraciones += 1
    return (a + b) / 2, a, b, iteraciones


# ---------------------------------------------------------------------------
# 3. Newton-Raphson
# ---------------------------------------------------------------------------

def derivada(func: Funcion, x: float) -> float:
    """Derivada numérica por diferencia central:  [f(x+h) - f(x-h)] / 2h"""
    h = 1e-7 * max(1.0, abs(x))
    return (func(x + h) - func(x - h)) / (2 * h)


def newton(func: Funcion, x0: float,
           tol: float = 1e-13, max_iter: int = 50) -> tuple[float | None, int]:
    """
    Método de Newton-Raphson:  x_nuevo = x - f(x) / f'(x)
    Devuelve (raíz, iteraciones), o (None, iteraciones) si no converge.
    """
    x = x0
    for iteracion in range(1, max_iter + 1):
        pendiente = derivada(func, x)
        if pendiente == 0:
            return None, iteracion
        paso = func(x) / pendiente
        x -= paso
        if abs(paso) < tol * max(1.0, abs(x)):
            return x, iteracion
    return None, max_iter


# ---------------------------------------------------------------------------
# Estrategia combinada
# ---------------------------------------------------------------------------

def resolver(func: Funcion, a: float, b: float, paso: float) -> ResultadoRaiz:
    """
    Halla la PRIMERA (la menor) solución de func(x) = 0 dentro de [a, b].

    Lanza ValueError si no hay ningún cambio de signo en el rango.
    """
    intervalos = buscar_intervalos(func, a, b, paso)
    if not intervalos:
        raise ValueError(f"No se encontró ninguna solución entre {a} y {b}.")
    otras = len(intervalos) - 1
    lo, hi = intervalos[0]

    if lo == hi:                                   # cayó justo en la solución
        return ResultadoRaiz(lo, 0, 0, otras)

    # Bisección "gruesa" para acercarse de forma segura
    x, lo, hi, it_b = biseccion(func, lo, hi, tol=1e-6)

    # Newton para afinar; se acepta solo si queda dentro del intervalo
    x_newton, it_n = newton(func, x)
    if x_newton is not None and lo <= x_newton <= hi:
        return ResultadoRaiz(x_newton, it_b, it_n, otras)

    # Si Newton falló, se termina con bisección fina
    x, _, _, it_extra = biseccion(func, lo, hi)
    return ResultadoRaiz(x, it_b + it_extra, it_n, otras)

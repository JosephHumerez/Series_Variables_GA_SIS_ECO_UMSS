"""
Pruebas de los métodos numéricos con funciones de solución conocida.

Ejecutar desde la carpeta del proyecto:
    python -m pytest
"""

import math

import pytest

from gradiente import numericos as num


def cuadratica(x):
    return x ** 2 - 2


def cubica(x):
    return x ** 3 - x


def test_biseccion_raiz_de_2():
    raiz, _, _, iteraciones = num.biseccion(cuadratica, 0, 2)
    assert raiz == pytest.approx(math.sqrt(2), abs=1e-12)
    assert iteraciones > 0


def test_biseccion_sin_cambio_de_signo_da_error():
    with pytest.raises(ValueError):
        num.biseccion(cuadratica, 2, 3)


def test_newton_raiz_de_2():
    raiz, iteraciones = num.newton(cuadratica, 1.0)
    assert raiz == pytest.approx(math.sqrt(2), abs=1e-12)
    assert iteraciones < 10


def test_newton_con_pendiente_cero_no_converge():
    raiz, _ = num.newton(lambda x: x ** 2 + 1, 0.0)
    assert raiz is None


def test_buscar_intervalos_encuentra_las_tres_raices():
    intervalos = num.buscar_intervalos(cubica, -2, 2, 0.3)
    assert len(intervalos) == 3
    for (a, b), raiz in zip(intervalos, (-1, 0, 1)):
        assert a <= raiz <= b


def test_buscar_intervalos_cuando_cae_justo_en_la_raiz():
    intervalos = num.buscar_intervalos(cubica, -2, 2, 0.5)
    assert intervalos == [(-1, -1), (0, 0), (1, 1)]


def test_resolver_devuelve_la_menor_y_cuenta_las_otras():
    r = num.resolver(cubica, -2, 2, 0.3)
    assert r.raiz == pytest.approx(-1)
    assert r.otras_soluciones == 2


def test_resolver_sin_solucion_da_error():
    with pytest.raises(ValueError):
        num.resolver(cuadratica, 2, 5, 0.1)

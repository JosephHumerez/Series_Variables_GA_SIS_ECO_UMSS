"""
Pruebas de los despejes numéricos de i y n, usando los ejercicios del libro.

Ejecutar desde la carpeta del proyecto:
    python -m pytest
"""

import pytest

from gradiente import despejes_numericos as dn
from gradiente.serie import SerieGradiente, calcular


# ---------------------------------------------------------------------------
# Despejar la tasa i
# ---------------------------------------------------------------------------

def test_tasa_ejercicio_1_libro():
    """P = 146 111,54, A' = 30 000, G = 2 000 decreciente, n = 11 -> i = 9,27 %"""
    r = dn.despejar_tasa(valor=146_111.54, dato="P", A_prima=30_000, G=2_000,
                         tipo="decreciente", n=11)
    assert r.i == pytest.approx(0.0927, abs=1e-6)
    assert r.avisos == ()


def test_tasa_ejercicio_2_libro_con_interpolacion():
    """F = 538 445,20, A' = 27 000, G = 3 000, n = 12 -> i = 0,66 % (entre 0,5 % y 0,75 %)"""
    r = dn.despejar_tasa(valor=538_445.20, dato="F", A_prima=27_000, G=3_000,
                         tipo="creciente", n=12)
    assert r.i == pytest.approx(0.0066, abs=1e-6)
    interp = r.interpolacion
    assert (interp.i1, interp.i2) == (0.005, 0.0075)
    assert interp.i_interpolada == pytest.approx(0.0066, abs=1e-4)   # aproximada


def test_tasa_ejercicio_6_libro():
    """P = 8 000, A' = 1 525,12, G = 500, n = 5 -> i ≈ 15 % (tasa de tabla: sin interpolación)"""
    r = dn.despejar_tasa(valor=8_000, dato="P", A_prima=1_525.12, G=500,
                         tipo="creciente", n=5)
    assert r.i == pytest.approx(0.15, abs=1e-5)


@pytest.mark.parametrize("dato", ["P", "F", "A"])
def test_tasa_ida_y_vuelta(dato):
    original = calcular(SerieGradiente(A_prima=4_000, G=250, i=0.037, n=15))
    valor = {"P": original.P, "F": original.F, "A": original.A}[dato]
    r = dn.despejar_tasa(valor=valor, dato=dato, A_prima=4_000, G=250,
                         tipo="creciente", n=15)
    assert r.i == pytest.approx(0.037, abs=1e-9)


def test_tasa_imposible_da_error():
    # P mayor que la suma de todos los pagos: ninguna tasa positiva lo cumple
    with pytest.raises(ValueError):
        dn.despejar_tasa(valor=1_000_000, dato="P", A_prima=1_000, G=100,
                         tipo="creciente", n=5)


def test_tasa_con_A_y_sin_gradiente_da_error():
    with pytest.raises(ValueError):
        dn.despejar_tasa(valor=1_000, dato="A", A_prima=1_000, G=0, tipo="creciente", n=5)


# ---------------------------------------------------------------------------
# Despejar el número de periodos n
# ---------------------------------------------------------------------------

def test_periodos_ejercicio_1_libro():
    """P = 146 111,54 -> n = 11. Hay otra solución con cuotas negativas: se avisa."""
    r = dn.despejar_periodos(valor=146_111.54, dato="P", A_prima=30_000, G=2_000,
                             tipo="decreciente", i=0.0927)
    assert r.n_exacto == pytest.approx(11, abs=1e-4)
    assert r.n_sugerido == 11
    assert r.es_entero
    assert any("valor(es) más de n" in a for a in r.avisos)


def test_periodos_ejercicio_2_libro():
    r = dn.despejar_periodos(valor=538_445.20, dato="F", A_prima=27_000, G=3_000,
                             tipo="creciente", i=0.0066)
    assert r.n_exacto == pytest.approx(12, abs=1e-4)
    assert r.avisos == ()


def test_periodos_no_entero_sugiere_entero():
    r = dn.despejar_periodos(valor=9_000, dato="P", A_prima=1_525.12, G=500,
                             tipo="creciente", i=0.15)
    assert not r.es_entero
    assert r.n_sugerido == round(r.n_exacto)
    assert r.serie_sugerida.n == r.n_sugerido
    # Con n exacto la ecuación se cumple:
    assert dn.valor_equivalente("P", 1_525.12, 500, 0.15, r.n_exacto) == pytest.approx(9_000)


@pytest.mark.parametrize("dato", ["P", "F", "A"])
def test_periodos_ida_y_vuelta(dato):
    original = calcular(SerieGradiente(A_prima=2_000, G=100, i=0.02, n=24))
    valor = {"P": original.P, "F": original.F, "A": original.A}[dato]
    r = dn.despejar_periodos(valor=valor, dato=dato, A_prima=2_000, G=100,
                             tipo="creciente", i=0.02)
    assert r.n_exacto == pytest.approx(24, abs=1e-6)


def test_periodos_imposible_da_error():
    with pytest.raises(ValueError):
        dn.despejar_periodos(valor=10, dato="P", A_prima=1_000, G=100,
                             tipo="creciente", i=0.05)

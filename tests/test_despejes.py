"""
Pruebas de los despejes algebraicos (n por último pago, A', G y sistema 2x2).

La forma más segura de probar un despeje es "ida y vuelta": se despeja la
incógnita y luego, con la serie obtenida, se recalcula el dato original.

Ejecutar desde la carpeta del proyecto:
    python -m pytest
"""

import pytest

from gradiente import despejes as d
from gradiente.serie import SerieGradiente, calcular


def valor_de(serie, dato):
    """Recalcula P, F o A de una serie para verificar el despeje."""
    r = calcular(serie)
    return {"P": r.P, "F": r.F, "A": r.A}[dato]


# ---------------------------------------------------------------------------
# 1. n por último pago
# ---------------------------------------------------------------------------

def test_n_ejercicio_1_libro():
    """A' = 30 000, último = 10 000, G = 2 000 -> n = 11 (decreciente)"""
    r = d.n_por_ultimo_pago(A_prima=30_000, ultimo_pago=10_000, G=2_000)
    assert r.n_exacto == 11
    assert r.es_entero
    assert r.tipo == "decreciente"


def test_n_creciente():
    r = d.n_por_ultimo_pago(A_prima=27_000, ultimo_pago=60_000, G=3_000)
    assert r.n_exacto == 12
    assert r.tipo == "creciente"


def test_n_no_entero_sugiere_el_mas_cercano():
    r = d.n_por_ultimo_pago(A_prima=1_000, ultimo_pago=2_100, G=300)   # 4,67
    assert r.n_exacto == pytest.approx(4.6667, abs=1e-4)
    assert not r.es_entero
    assert r.n_sugerido == 5


def test_n_con_gradiente_cero_da_error():
    with pytest.raises(ValueError):
        d.n_por_ultimo_pago(A_prima=1_000, ultimo_pago=2_000, G=0)


# ---------------------------------------------------------------------------
# 2. Despejar A' conociendo G
# ---------------------------------------------------------------------------

def test_base_ejercicio_6_libro():
    """P = 8 000, G = 500 creciente, i = 15 %, n = 5 -> A' = 1 525,12"""
    r = d.despejar_base(valor=8_000, dato="P", G=500, tipo="creciente", i=0.15, n=5)
    assert round(r.A_prima, 2) == 1_525.12
    assert r.incognita == "A'"


@pytest.mark.parametrize("dato", ["P", "F", "A"])
@pytest.mark.parametrize("tipo", ["creciente", "decreciente"])
def test_base_ida_y_vuelta(dato, tipo):
    r = d.despejar_base(valor=50_000, dato=dato, G=300, tipo=tipo, i=0.04, n=8)
    assert valor_de(r.serie, dato) == pytest.approx(50_000)


def test_base_serie_diferida():
    r = d.despejar_base(valor=20_000, dato="P", G=200, tipo="creciente",
                        i=0.05, n=6, inicio=4)
    assert valor_de(r.serie, "P") == pytest.approx(20_000)


# ---------------------------------------------------------------------------
# 3. Despejar G conociendo A'
# ---------------------------------------------------------------------------

def test_gradiente_ejercicio_2_libro():
    """F = 538 445,20, A' = 27 000, i = 0,66 %, n = 12 -> G = 3 000 creciente"""
    r = d.despejar_gradiente(valor=538_445.20, dato="F", A_prima=27_000, i=0.0066, n=12)
    assert r.G == pytest.approx(3_000, abs=0.01)
    assert r.tipo == "creciente"


def test_gradiente_ejercicio_1_libro_detecta_decreciente():
    """P = 146 111,54, A' = 30 000, i = 9,27 %, n = 11 -> G = 2 000 decreciente"""
    r = d.despejar_gradiente(valor=146_111.54, dato="P", A_prima=30_000, i=0.0927, n=11)
    assert r.G == pytest.approx(2_000, abs=0.01)
    assert r.tipo == "decreciente"


@pytest.mark.parametrize("dato", ["P", "F", "A"])
def test_gradiente_ida_y_vuelta(dato):
    r = d.despejar_gradiente(valor=40_000, dato=dato, A_prima=4_000, i=0.06, n=10)
    assert valor_de(r.serie, dato) == pytest.approx(40_000)


def test_gradiente_con_n_igual_a_1_da_error():
    with pytest.raises(ValueError):
        d.despejar_gradiente(valor=1_000, dato="P", A_prima=900, i=0.1, n=1)


# ---------------------------------------------------------------------------
# 4. Sistema de dos ecuaciones: A' y G a la vez
# ---------------------------------------------------------------------------

def test_sistema_ejercicio_1_libro():
    """P = 146 111,54 y último pago X_11 = 10 000 -> A' = 30 000, G = 2 000 decreciente"""
    r = d.despejar_base_y_gradiente(valor=146_111.54, dato="P", k=11, X_k=10_000,
                                    i=0.0927, n=11)
    assert r.A_prima == pytest.approx(30_000, abs=0.01)
    assert r.G == pytest.approx(2_000, abs=0.01)
    assert r.tipo == "decreciente"


def test_sistema_ejercicio_2_libro():
    """F = 538 445,20 y X_12 = 60 000 -> A' = 27 000, G = 3 000 creciente"""
    r = d.despejar_base_y_gradiente(valor=538_445.20, dato="F", k=12, X_k=60_000,
                                    i=0.0066, n=12)
    assert r.A_prima == pytest.approx(27_000, abs=0.01)
    assert r.G == pytest.approx(3_000, abs=0.01)


@pytest.mark.parametrize("dato", ["P", "F", "A"])
@pytest.mark.parametrize("k", [1, 4, 9])
def test_sistema_ida_y_vuelta(dato, k):
    original = SerieGradiente(A_prima=2_500, G=150, i=0.03, n=9, tipo="creciente")
    r = d.despejar_base_y_gradiente(valor=valor_de(original, dato), dato=dato,
                                    k=k, X_k=original.cuota(k), i=0.03, n=9)
    assert r.A_prima == pytest.approx(2_500)
    assert r.G == pytest.approx(150)


def test_sistema_cuota_fuera_de_rango():
    with pytest.raises(ValueError):
        d.despejar_base_y_gradiente(valor=1_000, dato="P", k=7, X_k=100, i=0.1, n=5)


# ---------------------------------------------------------------------------
# Coeficientes
# ---------------------------------------------------------------------------

def test_dato_invalido():
    with pytest.raises(ValueError):
        d.coeficientes("X", 0.1, 5)


def test_dato_no_distingue_mayusculas():
    assert d.coeficientes(" p ", 0.1, 5) == d.coeficientes("P", 0.1, 5)

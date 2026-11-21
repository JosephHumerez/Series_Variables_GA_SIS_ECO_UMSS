"""
Pruebas de los factores financieros.

Se verifican de tres formas:
    1. Contra valores de tabla conocidos (5 decimales, i = 10 %, n = 10).
    2. Contra las relaciones matemáticas entre factores.
    3. Contra el paso intermedio de un ejercicio del libro.

Ejecutar desde la carpeta del proyecto:
    python -m pytest
"""

import pytest

from gradiente import factores as f


# ---------------------------------------------------------------------------
# 1. Valores de tabla (i = 10 %, n = 10)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "factor, esperado",
    [
        (f.F_P, 2.59374),
        (f.P_F, 0.38554),
        (f.P_A, 6.14457),
        (f.A_P, 0.16275),
        (f.F_A, 15.93742),
        (f.A_F, 0.06275),
        (f.P_G, 22.89134),
        (f.A_G, 3.72546),
        (f.F_G, 59.37425),
    ],
)
def test_valores_de_tabla(factor, esperado):
    assert round(factor(0.10, 10), 5) == esperado


# ---------------------------------------------------------------------------
# 2. Relaciones entre factores
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("i, n", [(0.0927, 11), (0.0066, 12), (0.15, 5), (0.02, 36)])
def test_relaciones_entre_factores(i, n):
    # Los factores inversos multiplican 1
    assert f.P_F(i, n) * f.F_P(i, n) == pytest.approx(1)
    assert f.P_A(i, n) * f.A_P(i, n) == pytest.approx(1)
    assert f.F_A(i, n) * f.A_F(i, n) == pytest.approx(1)
    # P/G = (A/G)(P/A)   y   F/G = (P/G)(F/P)
    assert f.P_G(i, n) == pytest.approx(f.A_G(i, n) * f.P_A(i, n))
    assert f.F_G(i, n) == pytest.approx(f.P_G(i, n) * f.F_P(i, n))


def test_gradiente_es_suma_de_flujos_descontados():
    """P/G debe ser igual a sumar cada (k-1)G traído al periodo 0 (con G = 1)."""
    i, n = 0.08, 7
    suma = sum((k - 1) / (1 + i) ** k for k in range(1, n + 1))
    assert f.P_G(i, n) == pytest.approx(suma)


# ---------------------------------------------------------------------------
# 3. Paso intermedio del libro (Unidad 2, pág. 35, Ejercicio 1)
#    i = 9,27 % semestral, n = 11  ->  (A/G) = 4,12734
# ---------------------------------------------------------------------------

def test_factor_AG_ejercicio_1_libro():
    assert round(f.A_G(0.0927, 11), 5) == 4.12734


# ---------------------------------------------------------------------------
# Casos límite y validaciones
# ---------------------------------------------------------------------------

def test_tasa_cero_coincide_con_limite():
    """Con i = 0 los factores deben coincidir con una tasa casi nula."""
    for factor in (f.P_A, f.F_A, f.P_G, f.A_G, f.F_G):
        assert factor(0, 10) == pytest.approx(factor(1e-9, 10), rel=1e-6)


def test_datos_invalidos():
    with pytest.raises(ValueError):
        f.P_A(-1.5, 10)   # tasa menor a -100 %
    with pytest.raises(ValueError):
        f.P_A(0.10, -3)   # periodos negativos

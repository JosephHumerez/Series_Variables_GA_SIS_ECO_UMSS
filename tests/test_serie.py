"""
Pruebas del cálculo directo de series en gradiente aritmético.

Incluye los ejercicios resueltos del libro (Unidad 2, pág. 35).

Ejecutar desde la carpeta del proyecto:
    python -m pytest
"""

import pytest

from gradiente.serie import SerieGradiente, calcular


def valor_presente_flujo_a_flujo(serie):
    """Trae cada cuota al periodo 0 una por una (verificación sin factores)."""
    return sum(serie.cuota(k) / (1 + serie.i) ** (serie.inicio + k - 1)
               for k in range(1, serie.n + 1))


def valor_futuro_flujo_a_flujo(serie):
    """Lleva cada cuota al periodo final una por una (verificación sin factores)."""
    return sum(serie.cuota(k) * (1 + serie.i) ** (serie.n - k)
               for k in range(1, serie.n + 1))


# ---------------------------------------------------------------------------
# Ejercicios del libro
# ---------------------------------------------------------------------------

def test_ejercicio_1_libro_gradiente_decreciente():
    """A' = 30 000, disminuye 2 000 por semestre, i = 9,27 %, n = 11 -> P = 146 111,54"""
    r = calcular(SerieGradiente(A_prima=30_000, G=2_000, i=0.0927, n=11, tipo="decreciente"))
    assert round(r.factor_AG, 5) == 4.12734
    assert round(r.A, 2) == 21_745.33
    assert round(r.P, 2) == 146_111.54
    assert r.pagos[-1].monto == 10_000          # último pago del enunciado


def test_ejercicio_2_libro_gradiente_creciente():
    """A' = 27 000, aumenta 3 000 por mes, i = 0,66 %, n = 12 -> F = 538 445,20"""
    r = calcular(SerieGradiente(A_prima=27_000, G=3_000, i=0.0066, n=12, tipo="creciente"))
    assert round(r.A, 2) == 43_264.85
    assert round(r.F, 2) == 538_445.20


def test_ejercicio_6_libro_en_sentido_directo():
    """Con A' = 1 525,12 (respuesta del libro), G = 500, i = 15 %, n = 5 -> P ≈ 8 000"""
    r = calcular(SerieGradiente(A_prima=1_525.12, G=500, i=0.15, n=5))
    # A' viene redondeado a 2 decimales (error máx. 0,005), y al multiplicarlo por
    # (P/A; 15 %; 5) = 3,35216 el error en P puede llegar a ~0,017.
    assert r.P == pytest.approx(8_000, abs=0.02)


# ---------------------------------------------------------------------------
# Coherencia interna
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tipo", ["creciente", "decreciente"])
def test_factores_coinciden_con_flujo_a_flujo(tipo):
    serie = SerieGradiente(A_prima=5_000, G=400, i=0.03, n=10, tipo=tipo)
    r = calcular(serie)
    assert r.P == pytest.approx(valor_presente_flujo_a_flujo(serie))
    assert r.F == pytest.approx(valor_futuro_flujo_a_flujo(serie))


def test_metodo_alternativo_da_lo_mismo():
    r = calcular(SerieGradiente(A_prima=30_000, G=2_000, i=0.0927, n=11, tipo="decreciente"))
    assert r.P_base + r.P_gradiente == pytest.approx(r.P)
    assert r.F_base + r.F_gradiente == pytest.approx(r.F)
    assert r.A_gradiente < 0                    # decreciente -> el aporte resta


def test_tabla_de_pagos():
    r = calcular(SerieGradiente(A_prima=1_000, G=200, i=0.05, n=4))
    assert [p.monto for p in r.pagos] == [1_000, 1_200, 1_400, 1_600]
    assert [p.gradiente for p in r.pagos] == [0, 200, 400, 600]
    assert [p.periodo for p in r.pagos] == [1, 2, 3, 4]


def test_cuota_de_un_periodo_especifico():
    serie = SerieGradiente(A_prima=30_000, G=2_000, i=0.0927, n=11, tipo="decreciente")
    assert serie.cuota(1) == 30_000
    assert serie.cuota(6) == 20_000
    with pytest.raises(ValueError):
        serie.cuota(12)


def test_tasa_cero():
    r = calcular(SerieGradiente(A_prima=100, G=10, i=0, n=4))
    assert r.P == pytest.approx(100 + 110 + 120 + 130)


# ---------------------------------------------------------------------------
# Series diferidas
# ---------------------------------------------------------------------------

def test_serie_diferida():
    """Primera cuota en el periodo 4 -> P queda en el periodo 3 y se trae al 0."""
    serie = SerieGradiente(A_prima=5_000, G=500, i=0.08, n=6, inicio=4)
    r = calcular(serie)
    assert serie.periodo_origen == 3
    assert serie.periodo_final == 9
    assert r.P_origen * (1.08 ** -3) == pytest.approx(r.P)
    assert r.P == pytest.approx(valor_presente_flujo_a_flujo(serie))
    assert [p.periodo for p in r.pagos] == [4, 5, 6, 7, 8, 9]


def test_serie_no_diferida_no_usa_paso_4():
    r = calcular(SerieGradiente(A_prima=5_000, G=500, i=0.08, n=6))
    assert r.factor_PF_diferido is None
    assert r.P == r.P_origen


# ---------------------------------------------------------------------------
# Avisos de cuotas no positivas
# ---------------------------------------------------------------------------

def test_aviso_cuota_negativa():
    # Cuotas: 10 000, 7 000, 4 000, 1 000, -2 000, -5 000
    r = calcular(SerieGradiente(A_prima=10_000, G=3_000, i=0.05, n=6, tipo="decreciente"))
    assert len(r.avisos) == 1
    assert "cuota número 5" in r.avisos[0]
    assert "negativa" in r.avisos[0]
    assert r.P != 0                              # el cálculo NO se bloquea


def test_aviso_cuota_cero():
    r = calcular(SerieGradiente(A_prima=10_000, G=2_500, i=0.05, n=6, tipo="decreciente"))
    assert "cuota número 5" in r.avisos[0]
    assert "vale cero" in r.avisos[0]


def test_sin_avisos_si_todo_es_positivo():
    r = calcular(SerieGradiente(A_prima=30_000, G=2_000, i=0.0927, n=11, tipo="decreciente"))
    assert r.avisos == ()


# ---------------------------------------------------------------------------
# Validaciones
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "datos",
    [
        dict(A_prima=100, G=-10, i=0.05, n=5),                    # G negativo
        dict(A_prima=100, G=10, i=0.05, n=0),                     # n < 1
        dict(A_prima=100, G=10, i=0.05, n=4.5),                   # n no entero
        dict(A_prima=100, G=10, i=0.05, n=5, tipo="variable"),    # tipo inválido
        dict(A_prima=100, G=10, i=0.05, n=5, inicio=0),           # inicio < 1
    ],
)
def test_datos_invalidos(datos):
    with pytest.raises(ValueError):
        SerieGradiente(**datos)


def test_tipo_no_distingue_mayusculas():
    assert SerieGradiente(A_prima=100, G=10, i=0.05, n=5, tipo=" Decreciente ").signo == -1

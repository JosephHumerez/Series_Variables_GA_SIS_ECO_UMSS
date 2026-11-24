"""
Pruebas de la conversión de tasas.

Ejecutar desde la carpeta del proyecto:
    python -m pytest
"""

import pytest

from gradiente import tasas as t


def test_periodicidades_del_curso():
    assert t.PERIODICIDADES == (
        "mensual", "bimestral", "trimestral", "cuatrimestral", "semestral", "anual"
    )


def test_periodicidad_no_distingue_mayusculas_ni_espacios():
    assert t.periodos_por_anio("  Semestral ") == 2


def test_periodicidad_desconocida():
    with pytest.raises(ValueError):
        t.periodos_por_anio("quincenal")


@pytest.mark.parametrize(
    "capitalizacion, periodo_nominal, m",
    [
        ("mensual", "anual", 12),
        ("cuatrimestral", "anual", 3),
        ("trimestral", "semestral", 2),
        ("mensual", "trimestral", 3),
        ("anual", "anual", 1),
    ],
)
def test_capitalizaciones_por_periodo(capitalizacion, periodo_nominal, m):
    assert t.capitalizaciones_por_periodo(capitalizacion, periodo_nominal) == m


@pytest.mark.parametrize(
    "capitalizacion, periodo_nominal",
    [
        ("anual", "semestral"),
        ("trimestral", "bimestral"),
        ("cuatrimestral", "semestral"),
    ],
)
def test_capitalizacion_imposible(capitalizacion, periodo_nominal):
    with pytest.raises(ValueError):
        t.capitalizaciones_por_periodo(capitalizacion, periodo_nominal)


def test_nominal_a_efectiva_y_regreso():
    i = t.nominal_a_efectiva(0.24, "mensual")
    assert i == pytest.approx(0.02)
    assert t.efectiva_a_nominal(i, "mensual") == pytest.approx(0.24)


def test_nominal_semestral_capitalizable_trimestralmente():
    assert t.nominal_a_efectiva(0.09, "trimestral", "semestral") == pytest.approx(0.045)


@pytest.mark.parametrize(
    "i, origen, destino, esperado",
    [
        (0.03, "trimestral", "semestral", 0.0609),
        (0.02, "mensual", "anual", 1.02 ** 12 - 1),
        (0.1236, "anual", "semestral", 0.06),
        (0.01, "mensual", "cuatrimestral", 1.01 ** 4 - 1),
        (0.05, "bimestral", "bimestral", 0.05),
    ],
)
def test_efectiva_a_efectiva(i, origen, destino, esperado):
    assert t.efectiva_a_efectiva(i, origen, destino) == pytest.approx(esperado)


def test_ida_y_vuelta_no_cambia_la_tasa():
    i_sem = t.efectiva_a_efectiva(0.0066, "mensual", "semestral")
    assert t.efectiva_a_efectiva(i_sem, "semestral", "mensual") == pytest.approx(0.0066)


def test_conversion_nominal_guarda_pasos_intermedios():
    r = t.convertir_a_periodo_de_pago(
        0.24, "nominal", "anual", "semestral", capitalizacion="mensual"
    )
    assert r.m == 12
    assert r.tasa_capitalizacion == pytest.approx(0.02)
    assert r.tasa_pago == pytest.approx(1.02 ** 6 - 1)


def test_conversion_nominal_cuando_capitaliza_igual_que_el_pago():
    r = t.convertir_a_periodo_de_pago(
        0.18, "nominal", "anual", "semestral", capitalizacion="semestral"
    )
    assert r.tasa_pago == pytest.approx(0.09)


def test_conversion_efectiva():
    r = t.convertir_a_periodo_de_pago(0.12, "efectiva", "anual", "trimestral")
    assert r.capitalizacion is None
    assert r.tasa_capitalizacion is None
    assert r.tasa_pago == pytest.approx(1.12 ** 0.25 - 1)


def test_conversion_nominal_sin_capitalizacion_da_error():
    with pytest.raises(ValueError):
        t.convertir_a_periodo_de_pago(0.24, "nominal", "anual", "mensual")


def test_tipo_de_tasa_invalido():
    with pytest.raises(ValueError):
        t.convertir_a_periodo_de_pago(0.24, "anticipada", "anual", "mensual")

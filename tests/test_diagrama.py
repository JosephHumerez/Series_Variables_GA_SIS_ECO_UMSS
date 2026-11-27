"""
Pruebas del diagrama de flujo de caja.

Ejecutar desde la carpeta del proyecto:
    python -m pytest
"""

from gradiente.serie import SerieGradiente
from interfaz.diagrama import (
    COLOR_BASE, COLOR_CUOTA_NEGATIVA, COLOR_GRADIENTE, COLORES_EQUIVALENTE, diagrama_flujo,
)


def flechas(fig):
    """Anotaciones que son flechas (las demás son textos)."""
    return [a for a in fig.layout.annotations if a.showarrow]


SERIE_EJ1 = SerieGradiente(A_prima=30_000, G=2_000, i=0.0927, n=11, tipo="decreciente")


def test_una_flecha_por_cuota():
    fig = diagrama_flujo(SERIE_EJ1)
    assert len(flechas(fig)) == 11


def test_egresos_apuntan_hacia_abajo_e_ingresos_hacia_arriba():
    abajo = diagrama_flujo(SERIE_EJ1, "egreso")
    arriba = diagrama_flujo(SERIE_EJ1, "ingreso")
    assert all(a.y < 0 for a in flechas(abajo))
    assert all(a.y > 0 for a in flechas(arriba))


def test_altura_proporcional_al_monto():
    fig = diagrama_flujo(SERIE_EJ1, "ingreso")
    alturas = [a.y for a in flechas(fig)]
    assert alturas[0] == 1
    assert alturas[-1] == 10_000 / 30_000
    assert alturas == sorted(alturas, reverse=True)


def test_equivalente_en_sentido_contrario():
    fig = diagrama_flujo(SERIE_EJ1, "egreso", equivalente=("P", 146_111.54, 0))
    verde = [a for a in flechas(fig) if a.arrowcolor == COLORES_EQUIVALENTE["P"]]
    assert len(verde) == 1
    assert verde[0].x == 0 and verde[0].y > 0


def test_creciente_muestra_base_azul_y_gradiente_naranja():
    serie = SerieGradiente(A_prima=1_000, G=200, i=0.05, n=4, tipo="creciente")
    fig = diagrama_flujo(serie, "ingreso")
    puntas = flechas(fig)
    assert puntas[0].arrowcolor == COLOR_BASE
    assert all(a.arrowcolor == COLOR_GRADIENTE for a in puntas[1:])
    assert all(a.ay == 1_000 / 1_600 for a in puntas[1:])


def test_decreciente_muestra_lo_restado_punteado():
    fig = diagrama_flujo(SERIE_EJ1, "ingreso")
    punteados = [s for s in fig.layout.shapes if s.line.dash == "dot"]
    assert len(punteados) == 10
    assert all(s.line.color == COLOR_GRADIENTE for s in punteados)


def test_leyenda():
    fig = diagrama_flujo(SERIE_EJ1, "egreso", equivalente=("F", 387_431.46, 11))
    assert [t.name for t in fig.data] == ["Base A'", "Gradiente (resta)", "Valor futuro F"]


def test_cuota_negativa_cambia_de_sentido_y_color():
    serie = SerieGradiente(A_prima=10_000, G=3_000, i=0.05, n=6, tipo="decreciente")
    fig = diagrama_flujo(serie, "ingreso")
    ultima = flechas(fig)[-1]
    assert ultima.y < 0
    assert ultima.arrowcolor == COLOR_CUOTA_NEGATIVA


def test_serie_diferida_empieza_en_su_periodo():
    serie = SerieGradiente(A_prima=5_000, G=500, i=0.08, n=6, inicio=4)
    fig = diagrama_flujo(serie)
    assert [a.x for a in flechas(fig)] == [4, 5, 6, 7, 8, 9]


def test_tasa_aparece_en_el_diagrama():
    fig = diagrama_flujo(SERIE_EJ1)
    assert any("9,27 %" in (a.text or "") for a in fig.layout.annotations)

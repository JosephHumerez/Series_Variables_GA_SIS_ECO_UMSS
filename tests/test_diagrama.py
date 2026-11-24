"""
Pruebas del diagrama de flujo de caja.

Ejecutar desde la carpeta del proyecto:
    python -m pytest
"""

from gradiente.serie import SerieGradiente
from interfaz.diagrama import COLOR_CUOTA_NEGATIVA, COLOR_EQUIVALENTE, diagrama_flujo


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
    roja = [a for a in flechas(fig) if a.arrowcolor == COLOR_EQUIVALENTE]
    assert len(roja) == 1
    assert roja[0].x == 0 and roja[0].y > 0


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

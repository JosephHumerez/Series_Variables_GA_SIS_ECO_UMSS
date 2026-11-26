"""
Pruebas de la interfaz con el simulador de Streamlit (AppTest).

AppTest ejecuta la aplicación sin abrir el navegador y permite revisar
lo que se dibuja y simular clics.

Ejecutar desde la carpeta del proyecto:
    python -m pytest
"""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = Path(__file__).parent.parent / "app.py"


def test_aplicacion_completa_carga_sin_errores():
    at = AppTest.from_file(APP).run()
    assert not at.exception


def _pagina_tasas():
    from interfaz import pag_tasas
    pag_tasas.mostrar()


def test_pagina_tasas_valores_por_defecto():
    """Por defecto: 24 % nominal anual capitalizable mensualmente, pagos semestrales."""
    at = AppTest.from_function(_pagina_tasas).run()
    assert not at.exception
    assert at.metric[0].value == "12,6162 %"


def test_pagina_tasas_efectiva():
    at = AppTest.from_function(_pagina_tasas).run()
    at.radio[0].set_value("Efectiva").run()
    at.number_input[0].set_value(12.0).run()
    at.selectbox[1].set_value("trimestral").run()
    assert at.metric[0].value == "2,8737 %"


def test_pagina_tasas_capitalizacion_imposible_muestra_error():
    at = AppTest.from_function(_pagina_tasas).run()
    at.selectbox[0].set_value("semestral").run()
    at.selectbox[1].set_value("anual").run()
    assert at.error
    assert not at.exception


def _pagina_directo():
    from interfaz import pag_directo
    pag_directo.mostrar()


def test_pagina_directo_ejercicio_1_por_defecto():
    """Los valores por defecto son los del Ejercicio 1 del libro."""
    at = AppTest.from_function(_pagina_directo).run()
    assert not at.exception
    valores = [m.value for m in at.metric]
    assert valores == ["21 745,33", "146 111,54", "387 431,46", "10 000,00"]
    assert not at.warning


def test_pagina_directo_ejercicio_2():
    at = AppTest.from_function(_pagina_directo).run()
    at.number_input(key="dir_A").set_value(27_000.0)
    at.number_input(key="dir_G").set_value(3_000.0)
    at.radio(key="dir_tipo").set_value("Creciente")
    at.number_input(key="dir_n").set_value(12)
    at.number_input(key="dir_i").set_value(0.66).run()
    assert at.metric[2].value == "538 445,20"


def test_pagina_directo_aviso_cuota_negativa():
    at = AppTest.from_function(_pagina_directo).run()
    at.number_input(key="dir_n").set_value(20).run()
    assert at.warning
    assert not at.exception


def test_pagina_directo_usa_la_tasa_guardada():
    at = AppTest.from_function(_pagina_directo)
    at.session_state["tasa_activa"] = {"i": 0.0927, "periodo": "semestral", "descripcion": "x"}
    at.run()
    assert at.checkbox(key="dir_usar_tasa").value is True
    assert at.metric.values[1] == "146 111,54"

def test_boton_guarda_la_tasa():
    at = AppTest.from_function(_pagina_tasas).run()
    at.button[0].click().run()
    tasa = at.session_state["tasa_activa"]
    assert tasa["i"] == pytest.approx(1.02 ** 6 - 1)
    assert tasa["periodo"] == "semestral"


def _pagina_despejes():
    from interfaz import pag_despejes
    pag_despejes.mostrar()


def _despeje(modo):
    """Abre la página de despejes en el modo indicado, con sus datos por defecto."""
    at = AppTest.from_function(_pagina_despejes, default_timeout=15).run()
    at.selectbox(key="des_modo").set_value(modo).run()
    assert not at.exception
    assert not at.error
    return at


@pytest.mark.parametrize(
    "modo, esperado",
    [
        ("n: con el primer y el último pago", ["11", "Decreciente"]),
        ("A': conociendo G y P, F o A", ["1 525,12"]),
        ("G: conociendo A' y P, F o A", ["3 000,00", "Creciente"]),
        ("A' y G: conociendo P, F o A y una cuota Xₖ", ["30 000,00", "2 000,00", "Decreciente"]),
        ("i: tasa de interés (método numérico)", ["0,66 %", "0,6596 %"]),
        ("n: conociendo P, F o A (método numérico)", ["11"]),
    ],
)
def test_despejes_ejercicios_del_libro(modo, esperado):
    at = _despeje(modo)
    assert list(at.metric.values) == esperado


def test_despeje_n_numerico_avisa_otra_solucion():
    at = _despeje("n: conociendo P, F o A (método numérico)")
    assert any("valor(es) más de n" in w.value for w in at.warning)


def test_despeje_con_datos_imposibles_muestra_error():
    at = AppTest.from_function(_pagina_despejes, default_timeout=15).run()
    at.selectbox(key="des_modo").set_value("i: tasa de interés (método numérico)").run()
    at.number_input(key="des5_valor").set_value(1_000.0).run()
    assert at.error
    assert not at.exception

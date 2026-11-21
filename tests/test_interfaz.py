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

APP = Path(__file__).parent.parent / "app.py"     # app.py está en la raíz del proyecto


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
    at.number_input[0].set_value(12.0).run()          # 12 % efectiva anual
    at.selectbox[1].set_value("trimestral").run()      # pagos trimestrales
    assert at.metric[0].value == "2,8737 %"           # 1,12^(1/4) - 1


def test_pagina_tasas_capitalizacion_imposible_muestra_error():
    at = AppTest.from_function(_pagina_tasas).run()
    at.selectbox[0].set_value("semestral").run()       # tasa nominal semestral...
    at.selectbox[1].set_value("anual").run()           # ...capitalizable anualmente
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
    at.number_input(key="dir_n").set_value(20).run()      # 30 000 - 19·2 000 < 0
    assert at.warning
    assert not at.exception


def test_pagina_directo_usa_la_tasa_guardada():
    at = AppTest.from_function(_pagina_directo)
    at.session_state["tasa_activa"] = {"i": 0.0927, "periodo": "semestral", "descripcion": "x"}
    at.run()
    assert at.checkbox(key="dir_usar_tasa").value is True
    assert at.metric[1].value == "146 111,54"


def test_boton_guarda_la_tasa():
    at = AppTest.from_function(_pagina_tasas).run()
    at.button[0].click().run()
    tasa = at.session_state["tasa_activa"]
    assert tasa["i"] == pytest.approx(1.02 ** 6 - 1)
    assert tasa["periodo"] == "semestral"

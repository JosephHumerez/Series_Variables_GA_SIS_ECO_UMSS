"""
Pruebas del procedimiento paso a paso (formato de números y contenido de los pasos).

Ejecutar desde la carpeta del proyecto:
    python -m pytest
"""

import pytest

from gradiente import despejes as d
from gradiente import despejes_numericos as dn
from gradiente import procedimiento as pr
from gradiente.serie import SerieGradiente, calcular
from gradiente.tasas import convertir_a_periodo_de_pago


def todo_el_texto(pasos):
    """Une títulos, ecuaciones y explicaciones para buscar contenido fácilmente."""
    partes = []
    for p in pasos:
        partes += [p.titulo, p.explicacion, *p.ecuaciones]
    return "\n".join(partes)


# ---------------------------------------------------------------------------
# Formato de números
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "x, decimales, esperado",
    [
        (146_111.5378, 2, "146 111,54"),
        (-2_000, 2, "-2 000,00"),
        (4.127338, 5, "4,12734"),
        (12.5, 2, "12,50"),
        (-0.001, 2, "0,00"),          # no muestra "-0,00"
    ],
)
def test_formato_numero(x, decimales, esperado):
    assert pr.formato_numero(x, decimales) == esperado


@pytest.mark.parametrize(
    "i, esperado",
    [(0.0927, "9,27 %"), (0.0066, "0,66 %"), (0.15, "15 %"), (1.02 ** 6 - 1, "12,6162 %")],
)
def test_formato_porcentaje(i, esperado):
    assert pr.formato_porcentaje(i) == esperado


def test_numeros_en_latex():
    assert pr.num(146_111.54) == r"146\,111{,}54"
    assert pr.num(-500) == r"(-500{,}00)"
    assert pr.num(-500, parentesis=False) == r"-500{,}00"
    assert pr.pct(0.0927) == r"9{,}27\,\%"
    assert pr.notacion("A/G", 0.0927, 11) == r"(A/G;\ 9{,}27\,\%;\ 11)"


# ---------------------------------------------------------------------------
# Cálculo directo
# ---------------------------------------------------------------------------

def test_procedimiento_ejercicio_1_libro():
    r = calcular(SerieGradiente(A_prima=30_000, G=2_000, i=0.0927, n=11, tipo="decreciente"))
    texto = todo_el_texto(pr.procedimiento_serie(r))
    assert r"A = A' - G\,(A/G;\ i;\ n)" in texto     # fórmula del libro con signo menos
    assert "4{,}12734" in texto                       # factor A/G a 5 decimales
    assert r"21\,745{,}33" in texto                   # anualidad equivalente
    assert r"146\,111{,}54" in texto                  # valor presente


def test_procedimiento_ejercicio_2_libro():
    r = calcular(SerieGradiente(A_prima=27_000, G=3_000, i=0.0066, n=12))
    texto = todo_el_texto(pr.procedimiento_serie(r))
    assert r"A = A' + G\,(A/G;\ i;\ n)" in texto
    assert r"538\,445{,}20" in texto


def test_procedimiento_serie_diferida_tiene_paso_de_traslado():
    r = calcular(SerieGradiente(A_prima=5_000, G=500, i=0.08, n=6, inicio=4))
    pasos = pr.procedimiento_serie(r)
    titulos = [p.titulo for p in pasos]
    assert "Paso 2b: Traslado al periodo 0 (serie diferida)" in titulos
    assert "P_{3}" in todo_el_texto(pasos)


def test_procedimiento_cuota():
    serie = SerieGradiente(A_prima=30_000, G=2_000, i=0.0927, n=11, tipo="decreciente")
    paso = pr.procedimiento_cuota(serie, 11)
    assert paso.ecuaciones[-1] == r"X_{11} = 10\,000{,}00"


# ---------------------------------------------------------------------------
# Conversión de tasas
# ---------------------------------------------------------------------------

def test_procedimiento_tasa_nominal():
    c = convertir_a_periodo_de_pago(0.24, "nominal", "anual", "semestral", capitalizacion="mensual")
    pasos = pr.procedimiento_conversion(c)
    assert len(pasos) == 2
    texto = todo_el_texto(pasos)
    assert r"\frac{24\,\%}{12} = 2\,\%" in texto
    assert "12{,}6162" in texto


def test_procedimiento_tasa_sin_conversion():
    c = convertir_a_periodo_de_pago(0.09, "efectiva", "semestral", "semestral")
    pasos = pr.procedimiento_conversion(c)
    assert "no requiere conversión" in pasos[0].explicacion


# ---------------------------------------------------------------------------
# Despejes
# ---------------------------------------------------------------------------

def test_procedimiento_n_ultimo_pago():
    r = d.n_por_ultimo_pago(30_000, 10_000, 2_000)
    texto = todo_el_texto(pr.procedimiento_n_ultimo(r, 30_000, 10_000, 2_000))
    assert "decreciente" in texto
    assert "n = 11" in texto


def test_procedimiento_despeje_base_ejercicio_6():
    r = d.despejar_base(8_000, "P", G=500, tipo="creciente", i=0.15, n=5)
    texto = todo_el_texto(pr.procedimiento_despeje(r))
    assert r"A' = 1\,525{,}12" in texto


def test_procedimiento_despeje_gradiente_indica_decreciente():
    r = d.despejar_gradiente(146_111.54, "P", A_prima=30_000, i=0.0927, n=11)
    texto = todo_el_texto(pr.procedimiento_despeje(r))
    assert "negativo" in texto
    assert "**decreciente**" in texto


def test_procedimiento_sistema():
    r = d.despejar_base_y_gradiente(146_111.54, "P", k=11, X_k=10_000, i=0.0927, n=11)
    texto = todo_el_texto(pr.procedimiento_despeje(r))
    assert "Cramer" in texto
    assert r"30\,000{,}00" in texto


def test_procedimiento_despeje_diferido_traslada_P():
    r = d.despejar_base(20_000, "P", G=200, tipo="creciente", i=0.05, n=6, inicio=4)
    pasos = pr.procedimiento_despeje(r)
    assert pasos[0].titulo == "Traslado del valor presente (serie diferida)"


def test_procedimiento_tasa_numerica_con_interpolacion():
    r = dn.despejar_tasa(538_445.20, "F", A_prima=27_000, G=3_000, tipo="creciente", n=12)
    pasos = pr.procedimiento_tasa(r)
    texto = todo_el_texto(pasos)
    assert r"i = 0{,}66\,\%" in texto
    assert "interpolación" in texto.lower()


def test_procedimiento_periodos_no_entero():
    r = dn.despejar_periodos(9_000, "P", A_prima=1_525.12, G=500, tipo="creciente", i=0.15)
    pasos = pr.procedimiento_periodos(r)
    assert pasos[-1].titulo == "Periodos enteros"

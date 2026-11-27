"""
Página: Marco teórico (manual).

Explica la teoría de las series en gradiente aritmético, desde los conceptos
básicos hasta los cálculos inversos, siguiendo el libro de Emir Vargas Peredo.
Cada capítulo termina con un enlace a la página del sistema donde se practica.

Los ejemplos numéricos NO están escritos a mano: se calculan con el mismo
núcleo matemático (paquete "gradiente"), así siempre coinciden con la calculadora.
"""

import streamlit as st

from gradiente import factores as f
from gradiente.procedimiento import formato_numero, procedimiento_conversion, procedimiento_serie
from gradiente.serie import SerieGradiente, calcular
from gradiente.tasas import convertir_a_periodo_de_pago
from interfaz.comun import mostrar_pasos
from interfaz.diagrama import diagrama_flujo
from interfaz.estilo import coloreado, latex_coloreado


# ---------------------------------------------------------------------------
# Variables en LaTeX con su color (para las fórmulas)
# ---------------------------------------------------------------------------

A_PRIMA = latex_coloreado("cuota", "A'")
X_K = latex_coloreado("cuota", "X_k")
G = latex_coloreado("G", "G")
A = latex_coloreado("A", "A")
P = latex_coloreado("P", "P")
F = latex_coloreado("F", "F")
I = latex_coloreado("i", "i")
N = latex_coloreado("n", "n")

A_PRIMA_TEXTO = coloreado("cuota", "A'")   # "A'" en azul, para el texto normal


def _practica(pagina, texto: str, concepto: str, clave: str) -> None:
    """Recuadro de color con la invitación a practicar y el enlace a la página."""
    with st.container(key=f"tarjeta-{concepto}-practica-{clave}"):
        st.markdown(f"**:material/exercise: Ponlo en práctica**  \n{texto}")
        st.page_link(pagina, label=f"Ir a {pagina.title}", icon=":material/arrow_forward:")


def _idea_clave(texto: str) -> None:
    st.info(texto, icon=":material/lightbulb:")


# ===========================================================================
# Capítulo 1: Conceptos básicos
# ===========================================================================

def _cap_conceptos() -> None:
    st.header("1. Conceptos básicos")

    st.subheader("Valor del dinero en el tiempo")
    st.markdown(
        "Un monto de dinero **hoy** vale más que el mismo monto en el **futuro**, porque "
        "hoy puede invertirse y generar intereses. Por eso no se pueden sumar ni comparar "
        "directamente cantidades que ocurren en fechas distintas: primero hay que llevarlas "
        "a un **mismo punto en el tiempo** usando una tasa de interés."
    )

    st.subheader("Interés compuesto")
    st.markdown("Con interés compuesto, los intereses de cada periodo se suman al capital "
                "y en el periodo siguiente también generan intereses:")
    st.latex(rf"{F} = {P}\,(1 + {I})^{{{N}}}")
    ejemplo = 1_000 * f.F_P(0.10, 3)
    st.markdown(f"Ejemplo: 1 000 al 10 % durante 3 periodos se convierten en "
                f"1 000 · (1,10)³ = **{formato_numero(ejemplo)}**.")

    st.subheader("Elementos de un problema")
    st.markdown(
        "| Símbolo | Significado |\n|---|---|\n"
        f"| {coloreado('P', 'P')} | **Valor presente**: monto equivalente en el periodo 0 (hoy) |\n"
        f"| {coloreado('F', 'F')} | **Valor futuro**: monto equivalente al final del periodo n |\n"
        f"| {coloreado('A', 'A')} | **Anualidad**: pago igual que se repite cada periodo |\n"
        f"| {coloreado('i', 'i')} | **Tasa de interés** efectiva por periodo |\n"
        f"| {coloreado('n', 'n')} | **Número de periodos** |"
    )

    st.subheader("Diagrama de flujo de caja")
    st.markdown(
        "Es la representación gráfica de un problema: una **línea de tiempo horizontal** "
        "de 0 a n y una **flecha vertical** por cada flujo de dinero.\n"
        "- **Flecha hacia arriba:** ingreso (dinero que se recibe).\n"
        "- **Flecha hacia abajo:** egreso (dinero que se paga).\n"
        "- El **periodo 0** es el presente (hoy).\n"
        "- **Convención de fin de periodo:** el pago del periodo k ocurre **al final** "
        "del periodo k (anualidades vencidas). Por eso el primer pago está en el periodo 1."
    )
    _idea_clave("**Equivalencia:** dos flujos de dinero son equivalentes si, a la misma tasa "
                "de interés, tienen el mismo valor en un mismo punto del tiempo. Todo el tema "
                "consiste en encontrar valores equivalentes.")


# ===========================================================================
# Capítulo 2: Tasas de interés
# ===========================================================================

def _cap_tasas(paginas) -> None:
    st.header("2. Tasas de interés")

    st.subheader("Tasa nominal y tasa efectiva")
    st.markdown(
        "- **Tasa nominal (j):** tasa \"de nombre\" que se capitaliza **m** veces dentro de su "
        "periodo. Ejemplo: *24 % anual capitalizable mensualmente* (m = 12).\n"
        "- **Tasa efectiva (i):** la tasa que **realmente** se gana en un periodo. "
        "Ejemplo: *2 % efectiva mensual*."
    )

    st.subheader("Fórmulas de conversión")
    st.markdown("**De nominal a efectiva del periodo de capitalización:**")
    st.latex(rf"{I} = \frac{{j}}{{m}}")
    st.markdown("**Entre tasas efectivas de distinta periodicidad** "
                "(m₁ y m₂ = cantidad de periodos de cada tipo en un año):")
    st.latex(rf"{I}_2 = (1 + {I}_1)^{{m_1/m_2}} - 1")
    st.markdown(
        "| Periodicidad | Mensual | Bimestral | Trimestral | Cuatrimestral | Semestral | Anual |\n"
        "|---|---|---|---|---|---|---|\n"
        "| Periodos por año (m) | 12 | 6 | 4 | 3 | 2 | 1 |"
    )

    _idea_clave("**Regla de oro:** antes de usar cualquier factor, la tasa debe ser la "
                "**tasa efectiva del mismo periodo que los pagos**. Si los pagos son "
                "semestrales, se necesita la tasa efectiva semestral.")

    st.subheader("Ejemplo")
    st.markdown("24 % nominal anual capitalizable mensualmente, con pagos semestrales:")
    mostrar_pasos(procedimiento_conversion(
        convertir_a_periodo_de_pago(0.24, "nominal", "anual", "semestral", "mensual")
    ))

    _practica(paginas.TASAS, "Convierte tasas nominales o efectivas entre las seis "
              "periodicidades del curso y guarda el resultado para usarlo en los cálculos.",
              "i", "tasas")


# ===========================================================================
# Capítulo 3: Factores financieros
# ===========================================================================

def _cap_factores() -> None:
    st.header("3. Factores financieros")
    st.markdown(
        "Un **factor** es un número que convierte un valor en otro equivalente. "
        "Se escribe **(X/Y; i; n)** y se lee *\"X dado Y\"*: por ejemplo, (P/A; i; n) "
        "convierte una anualidad A en un valor presente P."
    )

    st.subheader("Pago único")
    st.markdown(
        "| Factor | Nombre | Fórmula |\n|---|---|---|\n"
        "| (F/P; i; n) | Capitalización de pago único | $(1+i)^n$ |\n"
        "| (P/F; i; n) | Actualización de pago único | $\\dfrac{1}{(1+i)^n}$ |"
    )

    st.subheader("Serie uniforme (anualidad)")
    st.markdown("Una serie de **n pagos iguales A**, del periodo 1 al n.")
    st.markdown(
        "| Factor | Nombre | Fórmula |\n|---|---|---|\n"
        "| (P/A; i; n) | Valor presente de una serie uniforme | "
        "$\\dfrac{(1+i)^n - 1}{i\\,(1+i)^n}$ |\n"
        "| (A/P; i; n) | Recuperación de capital | $\\dfrac{i\\,(1+i)^n}{(1+i)^n - 1}$ |\n"
        "| (F/A; i; n) | Valor futuro de una serie uniforme | $\\dfrac{(1+i)^n - 1}{i}$ |\n"
        "| (A/F; i; n) | Fondo de amortización | $\\dfrac{i}{(1+i)^n - 1}$ |"
    )
    _idea_clave("El valor presente de una serie uniforme queda ubicado **un periodo antes "
                "del primer pago**. Si la serie empieza en el periodo 1, P queda en el periodo 0.")
    st.caption("En las tablas del libro los factores aparecen con 5 decimales. "
               f"Ejemplo: (P/A; 10 %; 10) = {formato_numero(f.P_A(0.10, 10), 5)}.")


# ===========================================================================
# Capítulo 4: Gradiente aritmético
# ===========================================================================

def _cap_gradiente(paginas) -> None:
    st.header("4. Series en gradiente aritmético")

    st.subheader("Definición")
    st.markdown(
        f"Una **serie en gradiente aritmético** es una serie de pagos que **aumentan o "
        f"disminuyen en una cantidad constante** {coloreado('G', 'G')} cada periodo. "
        f"El primer pago {A_PRIMA_TEXTO} ocurre al final "
        "del periodo 1; el gradiente aparece recién en el periodo 2, y en el periodo n "
        "acumula n − 1 variaciones."
    )
    st.latex(rf"{X_K} = {A_PRIMA} \pm (k - 1)\,{G}")
    st.markdown(
        "- **Creciente (+):** cada pago es G mayor que el anterior.\n"
        "- **Decreciente (−):** cada pago es G menor que el anterior. Para que todas las cuotas "
        "sean positivas se necesita A' > (n − 1)·G."
    )

    st.subheader("Descomposición")
    st.markdown(
        "El libro resuelve toda serie en gradiente **separándola en dos series** independientes:"
    )
    st.latex(
        r"\begin{array}{lcccccc}"
        r"\text{Periodo:} & 1 & 2 & 3 & \cdots & n \\"
        rf"\text{{Serie base:}} & {A_PRIMA} & {A_PRIMA} & {A_PRIMA} & \cdots & {A_PRIMA} \\"
        rf"\text{{Gradiente puro:}} & 0 & {G} & 2{G} & \cdots & (n-1){G} \\"
        r"\end{array}"
    )
    st.markdown("En el diagrama, cada flecha muestra esa descomposición: el tramo "
                f"{coloreado('cuota', 'azul')} es la base A' y el tramo "
                f"{coloreado('G', 'naranja')} es lo que aporta el gradiente. Ejemplo con "
                "A' = 1 000, G = 200 creciente, n = 6:")
    ejemplo = SerieGradiente(A_prima=1_000, G=200, i=0.10, n=6, tipo="creciente")
    st.plotly_chart(diagrama_flujo(ejemplo, "ingreso"), width="stretch", key="teo_diagrama")

    st.subheader("Factores de gradiente")
    st.markdown("Se aplican a la serie gradiente pura (0, G, 2G, …, (n−1)G):")
    st.markdown(
        "| Factor | Convierte el gradiente en… | Fórmula |\n|---|---|---|\n"
        "| (P/G; i; n) | valor presente | $\\dfrac{(1+i)^n - 1 - n\\,i}{i^2\\,(1+i)^n}$ |\n"
        "| (A/G; i; n) | anualidad equivalente | $\\dfrac{1}{i} - \\dfrac{n}{(1+i)^n - 1}$ |\n"
        "| (F/G; i; n) | valor futuro | $\\dfrac{(1+i)^n - 1 - n\\,i}{i^2}$ |"
    )
    st.markdown("Se relacionan con los factores de serie uniforme:")
    st.latex(r"(P/G) = \frac{1}{i}\left[(P/A) - \frac{n}{(1+i)^n}\right]"
             r"\qquad (A/G) = (P/G)\,(A/P)\qquad (F/G) = \frac{1}{i}\left[(F/A) - n\right]")

    st.subheader("Procedimiento del libro")
    st.markdown("El autor convierte primero el gradiente en una **anualidad equivalente**, "
                "la suma o resta a la base, y lleva esa anualidad total a P o F:")
    st.latex(
        r"\begin{array}{ll}"
        rf"\text{{Paso 1:}} & {A} = {A_PRIMA} \pm {G}\,(A/G;\ {I};\ {N}) \\[4pt]"
        rf"\text{{Paso 2:}} & {P} = {A}\,(P/A;\ {I};\ {N}) \\[4pt]"
        rf"\text{{Paso 3:}} & {F} = {A}\,(F/A;\ {I};\ {N})"
        r"\end{array}"
    )
    st.markdown("**Método alternativo** (sirve para verificar): "
                "P = A'·(P/A) ± G·(P/G)  y  F = A'·(F/A) ± G·(F/G).")

    st.subheader("Ejemplo resuelto: Ejercicio 1 del libro (pág. 35)")
    st.markdown("*Un primer pago de 30 000 disminuye en 2 000 cada semestre hasta un último pago "
                "de 10 000. Con una tasa de 9,27 % semestral, ¿cuál es el valor presente?*")
    st.markdown("Primero el número de periodos: n = (30 000 − 10 000) / 2 000 + 1 = **11**.")
    r = calcular(SerieGradiente(A_prima=30_000, G=2_000, i=0.0927, n=11, tipo="decreciente"))
    mostrar_pasos(procedimiento_serie(r)[1:3])     # Paso 1 (A) y Paso 2 (P)

    _practica(paginas.DIRECTO, "La página ya viene cargada con este ejercicio. Cambia los datos "
              "y observa cómo cambian A, P, F, el diagrama y la tabla de pagos. Prueba también "
              "n = 20 para ver qué pasa cuando las cuotas llegan a cero.", "P", "directo")


# ===========================================================================
# Capítulo 5: Series diferidas
# ===========================================================================

def _cap_diferidas(paginas) -> None:
    st.header("5. Series diferidas")
    st.markdown(
        "Una serie es **diferida** cuando su primer pago no ocurre en el periodo 1 sino en un "
        "periodo posterior k. Los factores siguen funcionando igual, pero hay que recordar dónde "
        "queda ubicado el resultado:"
    )
    _idea_clave("El valor presente equivalente de una serie (uniforme o gradiente) queda "
                "**un periodo antes de su primer pago**. Si el primer pago está en el periodo k, "
                "P queda en el periodo k − 1 y luego hay que trasladarlo al periodo 0.")
    st.latex(rf"{P}_0 = {P}_{{k-1}}\,(P/F;\ {I};\ k - 1)")

    serie = SerieGradiente(A_prima=5_000, G=500, i=0.08, n=6, inicio=4)
    r = calcular(serie)
    st.markdown(
        f"**Ejemplo:** A' = 5 000, G = 500 creciente, i = 8 %, n = 6, primer pago en el periodo 4.\n"
        f"- P de la serie (ubicado en el periodo 3): **{formato_numero(r.P_origen)}**\n"
        f"- Trasladado al periodo 0: {formato_numero(r.P_origen)} · (P/F; 8 %; 3) = "
        f"**{formato_numero(r.P)}**"
    )

    _practica(paginas.DIRECTO, "En «Cálculo directo», abre **Opciones avanzadas** y cambia el "
              "**periodo de la primera cuota**. El procedimiento agrega el paso de traslado y el "
              "diagrama muestra dónde empieza la serie.", "P", "diferidas")


# ===========================================================================
# Capítulo 6: Cálculos inversos
# ===========================================================================

def _cap_despejes(paginas) -> None:
    st.header("6. Cálculos inversos (despejes)")
    st.markdown("Muchos problemas dan el valor equivalente y piden otro dato. La clave es que "
                "P, F y A se pueden escribir como una **ecuación lineal** en A' y G:")
    st.latex(rf"\text{{Valor}} = {A_PRIMA}\cdot c_{{\text{{base}}}} \pm {G}\cdot c_{{\text{{gradiente}}}}")
    st.markdown(
        "| Valor conocido | c_base | c_gradiente |\n|---|---|---|\n"
        "| A | 1 | (A/G; i; n) |\n"
        "| P | (P/A; i; n) | (P/G; i; n) |\n"
        "| F | (F/A; i; n) | (F/G; i; n) |"
    )

    st.subheader("Despejes con fórmula directa")
    st.markdown("**Número de periodos** a partir del primer y el último pago:")
    st.latex(rf"{N} = \frac{{|X_n - {A_PRIMA}|}}{{{G}}} + 1")
    st.markdown("**Primer pago** conociendo G, o **gradiente** conociendo A' "
                "(si el gradiente sale negativo, la serie es decreciente):")
    st.latex(rf"{A_PRIMA} = \frac{{\text{{Valor}} \mp {G}\cdot c_{{\text{{gradiente}}}}}}{{c_{{\text{{base}}}}}}"
             rf"\qquad \pm{G} = \frac{{\text{{Valor}} - {A_PRIMA}\cdot c_{{\text{{base}}}}}}{{c_{{\text{{gradiente}}}}}}")
    st.markdown("**A' y G a la vez:** con un solo valor hay una sola ecuación, así que se "
                "necesita un segundo dato, por ejemplo una cuota conocida Xₖ. Con las dos "
                "ecuaciones se forma un sistema 2×2 que se resuelve por la regla de Cramer:")
    st.latex(rf"\begin{{cases}} {A_PRIMA}\cdot c_{{\text{{base}}}} + g\cdot c_{{\text{{gradiente}}}} "
             rf"= \text{{Valor}} \\ {A_PRIMA} + (k-1)\,g = X_k \end{{cases}}\qquad g = \pm{G}")

    st.subheader("Despejes por métodos numéricos")
    st.markdown(
        f"Cuando la incógnita es la tasa {coloreado('i', 'i')} o el número de periodos "
        f"{coloreado('n', 'n')} a partir de P, F o A, la incógnita queda \"atrapada\" dentro de "
        "los factores y no se puede despejar con álgebra. Se busca el valor que cumple la "
        "ecuación con métodos numéricos:\n"
        "- **Bisección:** parte el intervalo por la mitad una y otra vez, quedándose con la mitad "
        "donde está la solución. Es lento, pero siempre converge.\n"
        "- **Newton-Raphson:** desde un valor cercano, mejora la estimación con "
        "x₁ = x₀ − f(x₀)/f′(x₀). Es muy rápido."
    )
    st.markdown("A mano, con las tablas del libro, se usa la **interpolación lineal** entre dos "
                "tasas de tabla i₁ e i₂:")
    st.latex(rf"{I} \approx {I}_1 + ({I}_2 - {I}_1)\,\frac{{V - V_1}}{{V_2 - V_1}}")
    _idea_clave("El número de periodos representa **cuotas enteras**. Si el resultado numérico "
                "de n tiene decimales, se toma el entero más cercano y se revisa cuánto cambia el valor.")

    _practica(paginas.DESPEJES, "Elige qué incógnita hallar: n, A', G, A' y G a la vez, o i. "
              "Cada opción viene cargada con un ejercicio del libro y muestra la verificación "
              "con el cálculo directo.", "G", "despejes")


# ===========================================================================
# Capítulo 7: Resumen de fórmulas
# ===========================================================================

def _cap_resumen() -> None:
    st.header("Resumen de fórmulas")
    st.markdown(
        "| Tema | Fórmula |\n|---|---|\n"
        "| Interés compuesto | $F = P\\,(1+i)^n$ |\n"
        "| Nominal → efectiva | $i = j/m$ |\n"
        "| Efectiva → efectiva | $i_2 = (1+i_1)^{m_1/m_2} - 1$ |\n"
        "| Cuota del periodo k | $X_k = A' \\pm (k-1)\\,G$ |\n"
        "| Anualidad equivalente | $A = A' \\pm G\\,(A/G;\\ i;\\ n)$ |\n"
        "| Valor presente | $P = A\\,(P/A;\\ i;\\ n)$ |\n"
        "| Valor futuro | $F = A\\,(F/A;\\ i;\\ n)$ |\n"
        "| Serie diferida | $P_0 = P_{k-1}\\,(P/F;\\ i;\\ k-1)$ |\n"
        "| n por último pago | $n = \\lvert X_n - A' \\rvert / G + 1$ |\n"
        "| (A/G; i; n) | $\\dfrac{1}{i} - \\dfrac{n}{(1+i)^n - 1}$ |\n"
        "| (P/G; i; n) | $\\dfrac{(1+i)^n - 1 - n\\,i}{i^2\\,(1+i)^n}$ |\n"
        "| (F/G; i; n) | $\\dfrac{(1+i)^n - 1 - n\\,i}{i^2}$ |\n"
        "| (P/A; i; n) | $\\dfrac{(1+i)^n - 1}{i\\,(1+i)^n}$ |\n"
        "| (F/A; i; n) | $\\dfrac{(1+i)^n - 1}{i}$ |\n"
        "| (P/F; i; n) | $\\dfrac{1}{(1+i)^n}$ |"
    )
    st.caption("Fuente: *Ingeniería Económica*, M. Sc. Emir Vargas Peredo, Unidad 2: "
               "Valor del dinero en el tiempo.")


# ===========================================================================
# Página
# ===========================================================================

def mostrar() -> None:
    # Se importa aquí (y no arriba) porque paginas.py importa este módulo
    from interfaz import paginas

    st.title(":material/menu_book: Marco teórico")
    st.markdown(
        "Manual para aprender el tema desde cero. Cada capítulo explica la teoría y sus "
        "fórmulas, y termina con un enlace a la página del sistema donde se practica. "
        f"Los colores siguen el código del sistema: {coloreado('cuota', 'cuotas')}, "
        f"{coloreado('G', 'gradiente')}, {coloreado('A', 'anualidad')}, "
        f"{coloreado('P', 'valor presente')}, {coloreado('F', 'valor futuro')}, "
        f"{coloreado('i', 'tasa')} y {coloreado('n', 'periodos')}."
    )

    capitulos = st.tabs([
        "1. Conceptos básicos", "2. Tasas de interés", "3. Factores financieros",
        "4. Gradiente aritmético", "5. Series diferidas", "6. Despejes",
        ":material/summarize: Resumen",
    ])
    with capitulos[0]:
        _cap_conceptos()
    with capitulos[1]:
        _cap_tasas(paginas)
    with capitulos[2]:
        _cap_factores()
    with capitulos[3]:
        _cap_gradiente(paginas)
    with capitulos[4]:
        _cap_diferidas(paginas)
    with capitulos[5]:
        _cap_despejes(paginas)
    with capitulos[6]:
        _cap_resumen()

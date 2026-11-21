"""
Procedimiento paso a paso "estilo libro".

Convierte los resultados de los otros módulos en una lista de pasos
(título + ecuaciones en LaTeX + explicación), listos para mostrarse en la
interfaz. Este módulo NO resuelve nada: solo da formato a lo ya calculado.

Convenciones de presentación:
    - Factores a 5 decimales (como la Tabla 1 del libro).
    - Montos a 2 decimales.
    - Separador de miles: espacio. Separador decimal: coma.  ->  146 111,54
    - Notación de factores: (A/G; 9,27 %; 11)
    - Internamente todo se calcula con precisión completa; por eso, si se
      multiplican a mano los números mostrados, puede haber diferencias de
      centavos con el resultado (que es el exacto).
"""

from dataclasses import dataclass

from gradiente import factores as f
from gradiente.despejes import ResultadoDespeje, ResultadoN
from gradiente.despejes_numericos import ResultadoPeriodos, ResultadoTasa
from gradiente.serie import CRECIENTE, ResultadoSerie, SerieGradiente, calcular
from gradiente.tasas import ConversionTasa, periodos_por_anio


DECIMALES_DINERO = 2
DECIMALES_FACTOR = 5


@dataclass(frozen=True)
class Paso:
    """Un paso del procedimiento."""
    titulo: str
    ecuaciones: tuple[str, ...] = ()   # cada elemento es una línea en LaTeX
    explicacion: str = ""              # texto normal (admite Markdown)


# ===========================================================================
# Formato de números
# ===========================================================================

def formato_numero(x: float, decimales: int = DECIMALES_DINERO) -> str:
    """146111.5378 -> '146 111,54'  (texto normal)"""
    if round(x, decimales) == 0:
        x = 0.0                                   # evita mostrar "-0,00"
    texto = f"{x:,.{decimales}f}"                 # '146,111.54'
    return texto.replace(",", "_").replace(".", ",").replace("_", " ")


def formato_porcentaje(i: float, max_decimales: int = 4) -> str:
    """0.0927 -> '9,27 %'   (sin ceros sobrantes)"""
    texto = f"{i * 100:.{max_decimales}f}".rstrip("0").rstrip(".")
    return texto.replace(".", ",") + " %"


def num(x: float, decimales: int = DECIMALES_DINERO, parentesis: bool = True) -> str:
    """Número en LaTeX: '146\\,111{,}54'. Los negativos van entre paréntesis."""
    # Primero la coma decimal y DESPUÉS el espacio de miles (el orden importa:
    # si se hiciera al revés, la coma de "\," también se cambiaría por "{,}")
    texto = formato_numero(x, decimales).replace(",", "{,}").replace(" ", r"\,")
    if parentesis and texto.startswith("-"):
        return f"({texto})"
    return texto


def fac(x: float) -> str:
    """Valor de un factor en LaTeX, a 5 decimales: '4{,}12734'"""
    return num(x, DECIMALES_FACTOR, parentesis=False)


def pct(i: float) -> str:
    """Porcentaje en LaTeX: '9{,}27\\,\\%'"""
    return formato_porcentaje(i).replace(",", "{,}").replace(" %", r"\,\%")


def dec(i: float) -> str:
    """Tasa en forma decimal en LaTeX: 0.0927 -> '0{,}0927'"""
    texto = f"{i:.8f}".rstrip("0").rstrip(".")
    return texto.replace(".", "{,}")


def notacion(nombre: str, i: float | None = None, n: float | None = None) -> str:
    """Notación de factor: '(A/G;\\ i;\\ n)'  o, con valores, '(A/G;\\ 9{,}27\\,\\%;\\ 11)'"""
    if i is None:
        return rf"({nombre};\ i;\ n)"
    return rf"({nombre};\ {pct(i)};\ {n})"


# ===========================================================================
# Piezas comunes
# ===========================================================================

OPERADOR = {CRECIENTE: "+", "decreciente": "-"}
OPUESTO = {"+": "-", "-": "+"}

# Factores que acompañan a A' y a G según el dato (None = A' va solo)
FACTORES_DEL_DATO = {"P": ("P/A", "P/G"), "F": ("F/A", "F/G"), "A": (None, "A/G")}


def _valores_factores(dato: str, i: float, n: int) -> tuple[float, float]:
    """Valores numéricos de los factores que acompañan a A' y a G."""
    if dato == "P":
        return f.P_A(i, n), f.P_G(i, n)
    if dato == "F":
        return f.F_A(i, n), f.F_G(i, n)
    return 1.0, f.A_G(i, n)


def _termino_base(dato: str, i=None, n=None, valor_factor=None) -> str:
    """A'·(P/A; i; n)  — o solo A' si el dato es A."""
    nombre = FACTORES_DEL_DATO[dato][0]
    if nombre is None:
        return "A'"
    if valor_factor is not None:
        return rf"A'\,({fac(valor_factor)})"
    return rf"A'\,{notacion(nombre, i, n)}"


def _ecuacion_simbolica(dato: str, izquierda: str, op: str, g: str = "G") -> str:
    """Ej.: 'P = A'\\,(P/A;\\ i;\\ n) - G\\,(P/G;\\ i;\\ n)'"""
    nombre_g = FACTORES_DEL_DATO[dato][1]
    return rf"{izquierda} = {_termino_base(dato)} {op} {g}\,{notacion(nombre_g)}"


def _valor_de(resultado: ResultadoSerie, dato: str) -> float:
    return {"P": resultado.P, "F": resultado.F, "A": resultado.A}[dato]


def _paso_traslado_diferida(serie: SerieGradiente, valor_P0: float) -> tuple[Paso, float, str]:
    """
    En despejes con P de una serie diferida: lleva P del periodo 0 al periodo
    (inicio - 1), donde los factores de la serie lo ubican.
    Devuelve (paso, valor trasladado, etiqueta LaTeX del valor).
    """
    k0 = serie.periodo_origen
    factor = f.F_P(serie.i, k0)
    trasladado = valor_P0 * factor
    etiqueta = f"P_{{{k0}}}"
    paso = Paso(
        "Traslado del valor presente (serie diferida)",
        (
            rf"{etiqueta} = P\,{notacion('F/P', serie.i, k0)} = {num(valor_P0)}\,({fac(factor)})",
            rf"{etiqueta} = {num(trasladado, parentesis=False)}",
        ),
        f"La primera cuota ocurre en el periodo {serie.inicio}, así que el valor presente "
        f"de la serie queda ubicado un periodo antes, en el periodo {k0}. Se lleva P "
        f"desde el periodo 0 hasta el periodo {k0}.",
    )
    return paso, trasladado, etiqueta


# ===========================================================================
# 1. Cálculo directo
# ===========================================================================

def procedimiento_serie(r: ResultadoSerie) -> list[Paso]:
    """Pasos del cálculo directo: datos, A, P, (traslado), F y verificación."""
    s = r.serie
    i, n = s.i, s.n
    op = OPERADOR[s.tipo]
    etiqueta_P = f"P_{{{s.periodo_origen}}}" if s.es_diferida else "P"

    pasos = [Paso(
        "Datos",
        explicacion=(
            f"A' = {formato_numero(s.A_prima)}  ·  G = {formato_numero(s.G)} ({s.tipo})  ·  "
            f"i = {formato_porcentaje(i)} por periodo  ·  n = {n} cuotas  ·  "
            f"primera cuota en el periodo {s.inicio}"
        ),
    )]

    # Paso 1: anualidad equivalente
    pasos.append(Paso(
        "Paso 1: Anualidad equivalente total",
        (
            rf"A = A' {op} G\,{notacion('A/G')}",
            rf"A = {num(s.A_prima)} {op} {num(s.G)}\,{notacion('A/G', i, n)}"
            rf" = {num(s.A_prima)} {op} {num(s.G)}\,({fac(r.factor_AG)})",
            rf"A = {num(s.A_prima)} {op} {num(abs(r.A_gradiente))}",
            rf"A = {num(r.A, parentesis=False)}",
        ),
        "El gradiente puro se convierte en una anualidad uniforme equivalente y se "
        + ("suma al" if op == "+" else "resta del") + " pago base A'.",
    ))

    # Paso 2: valor presente
    pasos.append(Paso(
        "Paso 2: Valor presente",
        (
            rf"{etiqueta_P} = A\,{notacion('P/A')}",
            rf"{etiqueta_P} = {num(r.A)}\,{notacion('P/A', i, n)} = {num(r.A)}\,({fac(r.factor_PA)})",
            rf"{etiqueta_P} = {num(r.P_origen, parentesis=False)}",
        ),
        f"El valor presente queda ubicado en el periodo {s.periodo_origen}, "
        "un periodo antes de la primera cuota.",
    ))

    # Paso extra para series diferidas: traslado al periodo 0
    if s.es_diferida:
        k0 = s.periodo_origen
        pasos.append(Paso(
            "Paso 2b: Traslado al periodo 0 (serie diferida)",
            (
                rf"P_0 = {etiqueta_P}\,{notacion('P/F', i, k0)} = "
                rf"{num(r.P_origen)}\,({fac(r.factor_PF_diferido)})",
                rf"P_0 = {num(r.P, parentesis=False)}",
            ),
            f"Se trae el valor del periodo {k0} al periodo 0 como un pago único.",
        ))

    # Paso 3: valor futuro
    pasos.append(Paso(
        "Paso 3: Valor futuro",
        (
            rf"F = A\,{notacion('F/A')}",
            rf"F = {num(r.A)}\,{notacion('F/A', i, n)} = {num(r.A)}\,({fac(r.factor_FA)})",
            rf"F = {num(r.F, parentesis=False)}",
        ),
        f"El valor futuro queda ubicado en el periodo {s.periodo_final}, junto con la última cuota.",
    ))

    # Verificación por el método alternativo (desglose base + gradiente)
    pasos.append(Paso(
        "Verificación: aporte de la base y del gradiente",
        (
            rf"{etiqueta_P} = A'\,{notacion('P/A')} {op} G\,{notacion('P/G')}",
            rf"{etiqueta_P} = {num(s.A_prima)}\,({fac(r.factor_PA)}) {op} {num(s.G)}\,({fac(r.factor_PG)})",
            rf"{etiqueta_P} = {num(r.P_base)} {op} {num(abs(r.P_gradiente))} = {num(r.P_origen, parentesis=False)}",
        ),
        f"La serie base aporta {formato_numero(r.P_base)} y el gradiente "
        f"{formato_numero(r.P_gradiente)} al valor presente. Coincide con el Paso 2.",
    ))
    return pasos


def procedimiento_cuota(serie: SerieGradiente, k: int) -> Paso:
    """Paso para hallar una cuota específica X_k."""
    op = OPERADOR[serie.tipo]
    periodo = serie.inicio + k - 1
    return Paso(
        f"Cuota número {k} (periodo {periodo})",
        (
            rf"X_{{{k}}} = A' {op} (k - 1)\,G",
            rf"X_{{{k}}} = {num(serie.A_prima)} {op} ({k} - 1)\,{num(serie.G)}",
            rf"X_{{{k}}} = {num(serie.cuota(k), parentesis=False)}",
        ),
    )


# ===========================================================================
# 2. Conversión de tasas
# ===========================================================================

def procedimiento_conversion(c: ConversionTasa) -> list[Paso]:
    """Pasos para llevar una tasa nominal o efectiva a la tasa del periodo de pago."""
    pasos = []
    numero = 1

    if c.tipo == "nominal":
        pasos.append(Paso(
            f"Paso {numero}: Tasa efectiva del periodo de capitalización",
            (
                r"i = \frac{j}{m}",
                rf"i = \frac{{{pct(c.tasa_dada)}}}{{{c.m}}} = {pct(c.tasa_capitalizacion)}",
            ),
            f"Tasa nominal de {formato_porcentaje(c.tasa_dada)} {c.periodicidad_dada} "
            f"capitalizable {c.capitalizacion}mente: se capitaliza m = {c.m} veces "
            f"en el periodo, lo que da una tasa efectiva {c.capitalizacion}.",
        ))
        numero += 1
        i_origen, periodo_origen = c.tasa_capitalizacion, c.capitalizacion
    else:
        i_origen, periodo_origen = c.tasa_dada, c.periodicidad_dada

    if periodo_origen == c.periodo_pago:
        pasos.append(Paso(
            f"Paso {numero}: Tasa del periodo de pago",
            (rf"i = {pct(c.tasa_pago)}",),
            f"La tasa ya es efectiva {c.periodo_pago}, igual que los pagos: no requiere conversión.",
        ))
        return pasos

    m1 = periodos_por_anio(periodo_origen)
    m2 = periodos_por_anio(c.periodo_pago)
    pasos.append(Paso(
        f"Paso {numero}: Tasa efectiva del periodo de pago",
        (
            r"i_2 = (1 + i_1)^{m_1/m_2} - 1",
            rf"i_2 = (1 + {dec(i_origen)})^{{{m1}/{m2}}} - 1",
            rf"i_2 = {pct(c.tasa_pago)}",
        ),
        f"m₁ = {m1} periodos {periodo_origen}es por año y m₂ = {m2} periodos "
        f"{c.periodo_pago}es por año. Resultado: tasa efectiva {c.periodo_pago}.",
    ))
    return pasos


# ===========================================================================
# 3. Despejes algebraicos
# ===========================================================================

def procedimiento_n_ultimo(r: ResultadoN, A_prima: float, ultimo_pago: float, G: float) -> list[Paso]:
    """Pasos para hallar n a partir del primer pago, el último y G."""
    op = OPERADOR[r.tipo]
    pasos = [Paso(
        "Número de periodos a partir del último pago",
        (
            rf"X_n = A' {op} (n - 1)\,G",
            r"n = \frac{|X_n - A'|}{G} + 1",
            rf"n = \frac{{|{num(ultimo_pago)} - {num(A_prima)}|}}{{{num(G)}}} + 1",
            rf"n = {num(r.n_exacto, 4, parentesis=False)}",
        ),
        f"El último pago es {'mayor' if op == '+' else 'menor'} que el primero, "
        f"por lo tanto el gradiente es {r.tipo}.",
    )]
    if not r.es_entero:
        pasos.append(Paso(
            "Periodos enteros",
            explicacion=(
                f"n debe ser un número entero de cuotas. El valor exacto "
                f"{formato_numero(r.n_exacto, 4)} indica que el último pago no encaja "
                f"exactamente con el gradiente; se sugiere n = {r.n_sugerido}."
            ),
        ))
    return pasos


def procedimiento_despeje(r: ResultadoDespeje) -> list[Paso]:
    """Pasos para despejar A', G o ambos (sistema de dos ecuaciones)."""
    s = r.serie
    i, n = s.i, s.n
    pasos = []

    # Si la serie es diferida y el dato es P, primero se traslada P
    valor, etiqueta = r.valor_dato, r.dato
    if r.dato == "P" and s.es_diferida:
        paso, valor, etiqueta = _paso_traslado_diferida(s, r.valor_dato)
        pasos.append(paso)

    vb, vg = _valores_factores(r.dato, i, n)
    nombre_b, nombre_g = FACTORES_DEL_DATO[r.dato]
    base_num = _termino_base(r.dato, valor_factor=vb)

    if r.incognita == "A'":
        op = OPERADOR[s.tipo]
        inv = OPUESTO[op]
        numerador = rf"{num(valor)} {inv} {num(s.G)}\,({fac(vg)})"
        despeje = numerador if nombre_b is None else rf"\frac{{{numerador}}}{{{fac(vb)}}}"
        simbolico = rf"{etiqueta} {inv} G\,{notacion(nombre_g)}"
        if nombre_b is not None:
            simbolico = rf"\frac{{{simbolico}}}{{{notacion(nombre_b)}}}"
        pasos.append(Paso(
            "Planteamiento",
            (
                _ecuacion_simbolica(r.dato, etiqueta, op),
                rf"{num(valor)} = {base_num} {op} {num(s.G)}\,({fac(vg)})",
            ),
            f"Se conoce {r.dato} y el gradiente G; la incógnita es el primer pago A'.",
        ))
        pasos.append(Paso(
            "Despeje de A'",
            (rf"A' = {simbolico}", rf"A' = {despeje}", rf"A' = {num(r.A_prima, parentesis=False)}"),
        ))

    elif r.incognita == "G":
        termino_A = num(r.A_prima) if nombre_b is None else rf"{num(r.A_prima)}\,({fac(vb)})"
        g = (valor - r.A_prima * vb) / vg
        pasos.append(Paso(
            "Planteamiento",
            (
                _ecuacion_simbolica(r.dato, etiqueta, "+", g="g"),
                rf"{num(valor)} = {termino_A} + g\,({fac(vg)})",
            ),
            f"Se conoce {r.dato} y el primer pago A'; la incógnita es el gradiente. "
            "Se usa g = ±G: su signo dirá si el gradiente es creciente o decreciente.",
        ))
        pasos.append(Paso(
            "Despeje del gradiente",
            (
                rf"g = \frac{{{num(valor)} - {termino_A}}}{{{fac(vg)}}}",
                rf"g = {num(g, parentesis=False)}",
            ),
            f"g es {'positivo' if g >= 0 else 'negativo'}: el gradiente es **{r.tipo}** "
            f"y G = {formato_numero(r.G)}.",
        ))

    else:  # Sistema de dos ecuaciones: A' y G
        k, X_k = r.k, r.X_k
        delta = vb * (k - 1) - vg
        a_num = rf"{num(valor)}\,({k - 1}) - {fac(vg)}\,({num(X_k)})"
        g_num = rf"{fac(vb)}\,({num(X_k)}) - {num(valor)}"
        g = (vb * X_k - valor) / delta
        pasos.append(Paso(
            "Planteamiento del sistema",
            (
                rf"\text{{(1)}}\quad {_ecuacion_simbolica(r.dato, etiqueta, '+', g='g')}",
                rf"\text{{(2)}}\quad X_{{{k}}} = A' + ({k} - 1)\,g",
                rf"\text{{(1)}}\quad {num(valor)} = {base_num} + g\,({fac(vg)})",
                rf"\text{{(2)}}\quad {num(X_k)} = A' + {k - 1}\,g",
            ),
            f"Se conocen {r.dato} y la cuota X_{k}. Hay dos incógnitas (A' y g = ±G) "
            "y dos ecuaciones: se resuelve el sistema por la regla de Cramer.",
        ))
        pasos.append(Paso(
            "Solución por la regla de Cramer",
            (
                rf"\Delta = ({fac(vb)})({k - 1}) - {fac(vg)} = {fac(delta)}",
                rf"A' = \frac{{{a_num}}}{{{fac(delta)}}} = {num(r.A_prima, parentesis=False)}",
                rf"g = \frac{{{g_num}}}{{{fac(delta)}}} = {num(g, parentesis=False)}",
            ),
            f"g es {'positivo' if g >= 0 else 'negativo'}: el gradiente es **{r.tipo}** "
            f"y G = {formato_numero(r.G)}.",
        ))

    pasos.append(Paso(
        "Resultado",
        explicacion=f"A' = {formato_numero(r.A_prima)}  ·  G = {formato_numero(r.G)} ({r.tipo})",
    ))
    return pasos


# ===========================================================================
# 4. Despejes numéricos
# ===========================================================================

def _ecuacion_con_incognita(serie: SerieGradiente, dato: str, valor: float,
                            i_txt: str, n_txt: str) -> tuple[str, str]:
    """Ecuación simbólica y ecuación con los datos conocidos (i o n como incógnita)."""
    op = OPERADOR[serie.tipo]
    nombre_b, nombre_g = FACTORES_DEL_DATO[dato]

    def fct(nombre):
        return rf"({nombre};\ {i_txt};\ {n_txt})"

    base = num(serie.A_prima) if nombre_b is None else rf"{num(serie.A_prima)}\,{fct(nombre_b)}"
    derecha = rf"{base} {op} {num(serie.G)}\,{fct(nombre_g)}"
    simbolica = _ecuacion_simbolica(dato, dato, op)
    if dato == "P" and serie.es_diferida:
        k0 = serie.periodo_origen
        derecha = rf"\left[{derecha}\right]\,(P/F;\ {i_txt};\ {k0})"
        simbolica = (rf"P = \left[{_termino_base('P')} {op} G\,{notacion('P/G')}\right]"
                     rf"\,(P/F;\ i;\ {k0})")
    return simbolica, rf"{num(valor)} = {derecha}"


def procedimiento_tasa(r: ResultadoTasa) -> list[Paso]:
    """Pasos para hallar la tasa i por métodos numéricos (y su interpolación)."""
    s = r.serie
    simbolica, con_datos = _ecuacion_con_incognita(s, r.dato, r.valor_dato, "i", str(s.n))
    verificacion = _valor_de(calcular(s), r.dato)

    pasos = [
        Paso("Planteamiento", (simbolica, con_datos),
             "La tasa i aparece dentro de los factores y no se puede despejar con álgebra."),
        Paso(
            "Solución por métodos numéricos",
            (rf"i = {pct(r.i)}",
             rf"\text{{Verificación: }} {r.dato} = {num(verificacion, parentesis=False)}"),
            f"Se buscó el valor de i que cumple la ecuación: primero por bisección "
            f"({r.iter_biseccion} iteraciones) y luego afinando con Newton-Raphson "
            f"({r.iter_newton} iteraciones).",
        ),
    ]

    if r.interpolacion is not None:
        t = r.interpolacion
        pasos.append(Paso(
            "Referencia: interpolación lineal con tasas de tabla",
            (
                rf"i_1 = {pct(t.i1)} \Rightarrow {r.dato}_1 = {num(t.valor1, parentesis=False)}",
                rf"i_2 = {pct(t.i2)} \Rightarrow {r.dato}_2 = {num(t.valor2, parentesis=False)}",
                rf"i \approx i_1 + (i_2 - i_1)\,\frac{{{r.dato} - {r.dato}_1}}{{{r.dato}_2 - {r.dato}_1}}",
                rf"i \approx {pct(t.i1)} + ({pct(t.i2)} - {pct(t.i1)})\,"
                rf"\frac{{{num(r.valor_dato)} - {num(t.valor1)}}}{{{num(t.valor2)} - {num(t.valor1)}}}",
                rf"i \approx {pct(t.i_interpolada)}",
            ),
            "Así se obtendría la tasa a mano con las tablas. Es una aproximación: "
            f"el valor exacto es {formato_porcentaje(r.i)}.",
        ))
    return pasos


def procedimiento_periodos(r: ResultadoPeriodos) -> list[Paso]:
    """Pasos para hallar n por métodos numéricos."""
    s = r.serie_sugerida
    simbolica, con_datos = _ecuacion_con_incognita(s, r.dato, r.valor_dato, pct(s.i), "n")

    pasos = [
        Paso("Planteamiento", (simbolica, con_datos),
             "El número de periodos n aparece dentro de los factores y no se puede despejar con álgebra."),
        Paso(
            "Solución por métodos numéricos",
            (rf"n = {num(r.n_exacto, 4, parentesis=False)}",),
            f"Se buscó el valor de n que cumple la ecuación: primero por bisección "
            f"({r.iter_biseccion} iteraciones) y luego afinando con Newton-Raphson "
            f"({r.iter_newton} iteraciones).",
        ),
    ]

    if r.es_entero:
        pasos.append(Paso("Resultado", explicacion=f"n = {r.n_sugerido} periodos."))
    else:
        diferencia = r.valor_con_sugerido - r.valor_dato
        pasos.append(Paso(
            "Periodos enteros",
            (rf"n = {r.n_sugerido} \Rightarrow {r.dato} = {num(r.valor_con_sugerido, parentesis=False)}",),
            f"En el libro n es un número entero de cuotas. Se sugiere n = {r.n_sugerido}; "
            f"con ese valor, {r.dato} difiere del dato en {formato_numero(diferencia)}.",
        ))
    return pasos

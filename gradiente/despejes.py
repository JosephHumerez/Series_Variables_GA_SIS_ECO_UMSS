"""
Cálculos inversos (despejes) de una serie en Gradiente Aritmético.

IDEA CLAVE: cualquiera de los tres valores equivalentes (P, F o A) se puede
escribir como una combinación LINEAL de A' y G:

    Valor = A'·c_base  ±  G·c_gradiente

donde los coeficientes son factores conocidos (dependen solo de i y n):

    Dato   c_base                       c_gradiente
    ----   --------------------------   --------------------------
     A     1                            (A/G, i, n)
     P     (P/A, i, n)                  (P/G, i, n)
     F     (F/A, i, n)                  (F/G, i, n)

    Si la serie es diferida, P está en el periodo 0, así que los dos
    coeficientes de P se multiplican además por (P/F, i, inicio - 1).

Con UNA ecuación se puede despejar UNA incógnita:
    - A' conociendo G:   A' = (Valor ∓ G·c_gradiente) / c_base
    - G  conociendo A':  ±G = (Valor - A'·c_base) / c_gradiente

Con una SEGUNDA condición (una cuota conocida X_k = A' ± (k-1)·G) se forma un
sistema de dos ecuaciones y se despejan A' y G a la vez.

En los despejes de G, el SIGNO del resultado indica el tipo de gradiente:
positivo -> creciente, negativo -> decreciente.
"""

from dataclasses import dataclass

from gradiente import factores as f
from gradiente.serie import CRECIENTE, DECRECIENTE, SerieGradiente


DATOS = ("P", "F", "A")


# ---------------------------------------------------------------------------
# Coeficientes de la ecuación  Valor = A'·c_base ± G·c_gradiente
# ---------------------------------------------------------------------------

def coeficientes(dato: str, i: float, n: int, inicio: int = 1) -> tuple[float, float]:
    """Devuelve (c_base, c_gradiente) según el dato conocido: 'P', 'F' o 'A'."""
    dato = dato.strip().upper()
    if dato == "A":
        return 1.0, f.A_G(i, n)
    if dato == "F":
        return f.F_A(i, n), f.F_G(i, n)
    if dato == "P":
        traslado = f.P_F(i, inicio - 1)   # vale 1 si la serie no es diferida
        return f.P_A(i, n) * traslado, f.P_G(i, n) * traslado
    raise ValueError(f"Dato '{dato}' no válido. Use uno de: {', '.join(DATOS)}.")


def _tipo_desde_signo(g_con_signo: float) -> tuple[float, str]:
    """Convierte un gradiente con signo en (G positivo, tipo)."""
    if g_con_signo < 0:
        return -g_con_signo, DECRECIENTE
    return g_con_signo, CRECIENTE


# ---------------------------------------------------------------------------
# Resultados
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ResultadoN:
    """Resultado de hallar n a partir del primer pago, el último y G."""
    n_exacto: float     # valor que sale de la fórmula
    n_sugerido: int     # entero más cercano
    es_entero: bool     # True si n_exacto ya es entero
    tipo: str           # creciente o decreciente (deducido de los pagos)


@dataclass(frozen=True)
class ResultadoDespeje:
    """
    Resultado de despejar A', G o ambos.
    Guarda los coeficientes usados para poder mostrar el procedimiento.
    """
    incognita: str          # "A'", "G" o "A' y G"
    dato: str               # "P", "F" o "A"
    valor_dato: float
    c_base: float
    c_gradiente: float
    A_prima: float
    G: float                # siempre positivo
    tipo: str               # creciente o decreciente
    serie: SerieGradiente   # serie completa ya resuelta (para calcular P, F, X_k...)
    # Solo para el sistema de dos ecuaciones:
    k: int | None = None
    X_k: float | None = None
    determinante: float | None = None


# ---------------------------------------------------------------------------
# 1. Número de periodos a partir del primer y último pago
# ---------------------------------------------------------------------------

def n_por_ultimo_pago(A_prima: float, ultimo_pago: float, G: float) -> ResultadoN:
    """
    Despeja n de  X_n = A' ± (n - 1)·G :

        n = |X_n - A'| / G + 1

    El tipo se deduce de los datos: si el último pago es mayor que el
    primero, el gradiente es creciente; si es menor, decreciente.

    Ej. 1 del libro: A' = 30 000, X_n = 10 000, G = 2 000  ->  n = 11
    """
    if G <= 0:
        raise ValueError("G debe ser mayor que cero para poder hallar n.")
    tipo = CRECIENTE if ultimo_pago >= A_prima else DECRECIENTE
    n_exacto = abs(ultimo_pago - A_prima) / G + 1
    n_sugerido = round(n_exacto)
    return ResultadoN(
        n_exacto=n_exacto,
        n_sugerido=n_sugerido,
        es_entero=abs(n_exacto - n_sugerido) < 1e-9,
        tipo=tipo,
    )


# ---------------------------------------------------------------------------
# 2. Despejar A' conociendo G
# ---------------------------------------------------------------------------

def despejar_base(valor: float, dato: str, G: float, tipo: str,
                  i: float, n: int, inicio: int = 1) -> ResultadoDespeje:
    """
    Halla el primer pago A' conociendo G y uno de los valores P, F o A.

        A' = (Valor ∓ G·c_gradiente) / c_base

    Ej. 6 del libro: P = 8 000, G = 500 creciente, i = 15 %, n = 5 -> A' = 1 525,12
    """
    # Se crea una serie provisional solo para validar los datos y obtener el signo
    signo = SerieGradiente(A_prima=0, G=G, i=i, n=n, tipo=tipo, inicio=inicio).signo
    c_base, c_grad = coeficientes(dato, i, n, inicio)

    A_prima = (valor - signo * G * c_grad) / c_base

    serie = SerieGradiente(A_prima=A_prima, G=G, i=i, n=n, tipo=tipo, inicio=inicio)
    return ResultadoDespeje(
        incognita="A'", dato=dato.strip().upper(), valor_dato=valor,
        c_base=c_base, c_gradiente=c_grad,
        A_prima=A_prima, G=G, tipo=serie.tipo, serie=serie,
    )


# ---------------------------------------------------------------------------
# 3. Despejar G conociendo A'
# ---------------------------------------------------------------------------

def despejar_gradiente(valor: float, dato: str, A_prima: float,
                       i: float, n: int, inicio: int = 1) -> ResultadoDespeje:
    """
    Halla el gradiente conociendo A' y uno de los valores P, F o A.

        ±G = (Valor - A'·c_base) / c_gradiente

    Si el resultado es negativo, el gradiente es decreciente.
    """
    if n < 2:
        raise ValueError("Con n = 1 no existe gradiente (solo hay una cuota).")
    c_base, c_grad = coeficientes(dato, i, n, inicio)

    g_con_signo = (valor - A_prima * c_base) / c_grad
    G, tipo = _tipo_desde_signo(g_con_signo)

    serie = SerieGradiente(A_prima=A_prima, G=G, i=i, n=n, tipo=tipo, inicio=inicio)
    return ResultadoDespeje(
        incognita="G", dato=dato.strip().upper(), valor_dato=valor,
        c_base=c_base, c_gradiente=c_grad,
        A_prima=A_prima, G=G, tipo=tipo, serie=serie,
    )


# ---------------------------------------------------------------------------
# 4. Despejar A' y G a la vez (sistema de dos ecuaciones)
# ---------------------------------------------------------------------------

def despejar_base_y_gradiente(valor: float, dato: str, k: int, X_k: float,
                              i: float, n: int, inicio: int = 1) -> ResultadoDespeje:
    """
    Halla A' y G conociendo uno de los valores P, F o A, y además una cuota X_k
    (por ejemplo el último pago, k = n).

    Sistema (g = ±G, con signo):
        Ecuación 1:  A'·c_base + g·c_gradiente = Valor
        Ecuación 2:  A'        + g·(k - 1)     = X_k

    Se resuelve por la regla de Cramer:
        Δ  = c_base·(k - 1) - c_gradiente
        A' = [Valor·(k - 1) - c_gradiente·X_k] / Δ
        g  = [c_base·X_k - Valor] / Δ
    """
    if n < 2:
        raise ValueError("Con n = 1 no existe gradiente (solo hay una cuota).")
    if not 1 <= k <= n:
        raise ValueError(f"La cuota conocida debe estar entre 1 y {n}. Se recibió k = {k}.")
    c_base, c_grad = coeficientes(dato, i, n, inicio)

    det = c_base * (k - 1) - c_grad
    if abs(det) < 1e-12:
        raise ValueError(
            "El sistema no tiene solución única con estos datos: la cuota "
            f"X_{k} no aporta información nueva. Pruebe con otra cuota."
        )
    A_prima = (valor * (k - 1) - c_grad * X_k) / det
    g_con_signo = (c_base * X_k - valor) / det
    G, tipo = _tipo_desde_signo(g_con_signo)

    serie = SerieGradiente(A_prima=A_prima, G=G, i=i, n=n, tipo=tipo, inicio=inicio)
    return ResultadoDespeje(
        incognita="A' y G", dato=dato.strip().upper(), valor_dato=valor,
        c_base=c_base, c_gradiente=c_grad,
        A_prima=A_prima, G=G, tipo=tipo, serie=serie,
        k=k, X_k=X_k, determinante=det,
    )

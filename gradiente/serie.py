"""
Cálculo directo de una serie en Gradiente Aritmético (G.A.).

Metodología del libro (Unidad 2):

    La serie se DESCOMPONE en dos series independientes:

        Serie uniforme base:   A'  A'   A'   ...  A'
        Serie gradiente pura:  0   G    2G   ...  (n-1)G
                               ----------------------------
        Serie total:           A'  A'±G A'±2G ... A'±(n-1)G

    Cuota de la posición k:   X_k = A' ± (k - 1)·G
        (+) gradiente creciente     (-) gradiente decreciente

    Procedimiento que sigue el autor:
        Paso 1. Anualidad equivalente:  A = A' ± G·(A/G, i, n)
        Paso 2. Valor presente:         P = A·(P/A, i, n)
        Paso 3. Valor futuro:           F = A·(F/A, i, n)

    Método alternativo (sirve para verificar y para desglosar):
        P = A'·(P/A, i, n) ± G·(P/G, i, n)
        F = A'·(F/A, i, n) ± G·(F/G, i, n)

Series diferidas:
    Si la primera cuota no ocurre en el periodo 1 sino en el periodo "inicio",
    el valor presente calculado con los factores queda ubicado UN PERIODO ANTES
    de la primera cuota (periodo inicio - 1). Luego se traslada al periodo 0:

        Paso 4. P₀ = P·(P/F, i, inicio - 1)
"""

from dataclasses import dataclass

from gradiente import factores as f


CRECIENTE = "creciente"
DECRECIENTE = "decreciente"


# ---------------------------------------------------------------------------
# Datos de entrada
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SerieGradiente:
    """
    Datos de una serie en gradiente aritmético.

    A_prima : primer pago (serie base A')
    G       : monto del gradiente, siempre POSITIVO; el sentido lo da "tipo"
    i       : tasa efectiva del periodo de pago, decimal (9,27 % -> 0.0927)
    n       : número de cuotas (entero >= 1)
    tipo    : "creciente" o "decreciente"
    inicio  : periodo en que ocurre la primera cuota (1 = serie normal;
              mayor que 1 = serie diferida)
    """
    A_prima: float
    G: float
    i: float
    n: int
    tipo: str = CRECIENTE
    inicio: int = 1

    def __post_init__(self):
        # Se normalizan los datos (frozen=True obliga a usar object.__setattr__)
        tipo = self.tipo.strip().lower()
        if tipo not in (CRECIENTE, DECRECIENTE):
            raise ValueError(f"Tipo '{self.tipo}' no válido. Use 'creciente' o 'decreciente'.")
        object.__setattr__(self, "tipo", tipo)

        if self.G < 0:
            raise ValueError("G debe ser positivo; indique si decrece con tipo='decreciente'.")
        if self.i <= -1:
            raise ValueError("La tasa i debe ser mayor que -100 %.")
        if int(self.n) != self.n or self.n < 1:
            raise ValueError(f"n debe ser un entero mayor o igual a 1. Se recibió n = {self.n}.")
        if int(self.inicio) != self.inicio or self.inicio < 1:
            raise ValueError(f"El periodo de inicio debe ser un entero >= 1. Se recibió {self.inicio}.")
        object.__setattr__(self, "n", int(self.n))
        object.__setattr__(self, "inicio", int(self.inicio))

    @property
    def signo(self) -> int:
        """+1 si el gradiente es creciente, -1 si es decreciente."""
        return 1 if self.tipo == CRECIENTE else -1

    @property
    def es_diferida(self) -> bool:
        return self.inicio > 1

    @property
    def periodo_origen(self) -> int:
        """Periodo donde quedan P (calculado con factores): uno antes de la 1.ª cuota."""
        return self.inicio - 1

    @property
    def periodo_final(self) -> int:
        """Periodo de la última cuota (donde queda ubicado F)."""
        return self.inicio + self.n - 1

    def cuota(self, k: int) -> float:
        """X_k: monto de la cuota número k (k = 1..n).  X_k = A' ± (k - 1)·G"""
        if not 1 <= k <= self.n:
            raise ValueError(f"La cuota debe estar entre 1 y {self.n}. Se pidió k = {k}.")
        return self.A_prima + self.signo * (k - 1) * self.G


# ---------------------------------------------------------------------------
# Resultados
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Pago:
    """Una fila de la tabla de pagos."""
    numero: int        # número de cuota (1..n)
    periodo: int       # periodo en la línea de tiempo
    base: float        # aporte de la serie base: A'
    gradiente: float   # aporte del gradiente: ±(k - 1)·G
    monto: float       # X_k = base + gradiente


@dataclass(frozen=True)
class ResultadoSerie:
    """
    Todos los valores del cálculo directo, incluidos los intermedios,
    para poder mostrar el procedimiento paso a paso como en el libro.
    Los aportes del gradiente llevan signo (negativos si es decreciente).
    """
    serie: SerieGradiente

    # Paso 1: anualidad equivalente  A = A' ± G·(A/G)
    factor_AG: float
    A_gradiente: float     # ±G·(A/G)
    A: float

    # Paso 2: valor presente  P = A·(P/A)   (ubicado en serie.periodo_origen)
    factor_PA: float
    P_origen: float

    # Paso 3: valor futuro  F = A·(F/A)   (ubicado en serie.periodo_final)
    factor_FA: float
    F: float

    # Paso 4 (solo diferidas): P₀ = P·(P/F, i, inicio - 1)
    factor_PF_diferido: float | None
    P: float               # valor presente en el periodo 0

    # Desglose por el método alternativo
    factor_PG: float
    P_base: float          # A'·(P/A)
    P_gradiente: float     # ±G·(P/G)
    factor_FG: float
    F_base: float          # A'·(F/A)
    F_gradiente: float     # ±G·(F/G)

    pagos: tuple[Pago, ...]
    avisos: tuple[str, ...]


# ---------------------------------------------------------------------------
# Cálculo
# ---------------------------------------------------------------------------

def calcular(serie: SerieGradiente) -> ResultadoSerie:
    """Resuelve la serie: A, P, F, tabla de pagos y avisos."""
    i, n, s = serie.i, serie.n, serie.signo

    # Paso 1: convertir el gradiente puro en anualidad y sumarlo (o restarlo) a la base
    factor_AG = f.A_G(i, n)
    A_gradiente = s * serie.G * factor_AG
    A = serie.A_prima + A_gradiente

    # Paso 2: llevar la anualidad total a valor presente
    factor_PA = f.P_A(i, n)
    P_origen = A * factor_PA

    # Paso 3: llevar la anualidad total a valor futuro
    factor_FA = f.F_A(i, n)
    F = A * factor_FA

    # Paso 4: si es diferida, trasladar P al periodo 0
    if serie.es_diferida:
        factor_PF = f.P_F(i, serie.periodo_origen)
        P = P_origen * factor_PF
    else:
        factor_PF = None
        P = P_origen

    # Desglose: aporte de la base y aporte del gradiente
    factor_PG = f.P_G(i, n)
    factor_FG = f.F_G(i, n)

    return ResultadoSerie(
        serie=serie,
        factor_AG=factor_AG, A_gradiente=A_gradiente, A=A,
        factor_PA=factor_PA, P_origen=P_origen,
        factor_FA=factor_FA, F=F,
        factor_PF_diferido=factor_PF, P=P,
        factor_PG=factor_PG,
        P_base=serie.A_prima * factor_PA,
        P_gradiente=s * serie.G * factor_PG,
        factor_FG=factor_FG,
        F_base=serie.A_prima * factor_FA,
        F_gradiente=s * serie.G * factor_FG,
        pagos=tabla_de_pagos(serie),
        avisos=revisar_cuotas(serie),
    )


def tabla_de_pagos(serie: SerieGradiente) -> tuple[Pago, ...]:
    """Lista de todas las cuotas con su periodo y su desglose base + gradiente."""
    return tuple(
        Pago(
            numero=k,
            periodo=serie.inicio + k - 1,
            base=serie.A_prima,
            gradiente=serie.signo * (k - 1) * serie.G,
            monto=serie.cuota(k),
        )
        for k in range(1, serie.n + 1)
    )


def revisar_cuotas(serie: SerieGradiente) -> tuple[str, ...]:
    """
    Advierte si alguna cuota vale cero o es negativa (no bloquea el cálculo).
    Suele ocurrir en gradientes decrecientes con demasiados periodos.
    """
    for k in range(1, serie.n + 1):
        x = serie.cuota(k)
        if x <= 0:
            periodo = serie.inicio + k - 1
            estado = "vale cero" if x == 0 else f"es negativa ({x:,.2f})"
            return (
                f"La cuota número {k} (periodo {periodo}) {estado}. "
                f"Desde ese punto el flujo deja de tener el sentido original "
                f"(un pago se convertiría en cobro o viceversa). Revise los datos.",
            )
    return ()

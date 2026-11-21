"""
Conversión de tasas de interés (capitalización discreta).

Antes de aplicar los factores, la tasa debe estar expresada como TASA EFECTIVA
DEL PERIODO DE PAGO. Por ejemplo, si los pagos son semestrales, se necesita la
tasa efectiva semestral.

Conceptos:
    Tasa nominal (j):  tasa "de nombre" que se capitaliza m veces dentro de su
                       periodo. Ej.: 24 % anual capitalizable mensualmente.
    Tasa efectiva (i): tasa que realmente se gana en un periodo.
                       Ej.: 2 % efectiva mensual.

Fórmulas:
    1) Nominal -> efectiva del periodo de capitalización:
           i = j / m        (m = capitalizaciones dentro del periodo nominal)

    2) Efectiva -> efectiva de otra periodicidad:
           i_destino = (1 + i_origen)^(m_origen / m_destino) - 1
       donde m_origen y m_destino son la cantidad de periodos que caben en un año.

Todas las tasas se manejan en forma DECIMAL (24 % -> 0.24).
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Periodicidades usadas en el curso
# ---------------------------------------------------------------------------

# Cuántos periodos de cada tipo caben en un año
PERIODOS_POR_ANIO = {
    "mensual": 12,
    "bimestral": 6,
    "trimestral": 4,
    "cuatrimestral": 3,
    "semestral": 2,
    "anual": 1,
}

# Lista ordenada, útil para los menús de la interfaz
PERIODICIDADES = tuple(PERIODOS_POR_ANIO)


def periodos_por_anio(periodicidad: str) -> int:
    """Devuelve cuántos periodos de esa periodicidad hay en un año (mensual -> 12)."""
    clave = periodicidad.strip().lower()
    if clave not in PERIODOS_POR_ANIO:
        opciones = ", ".join(PERIODICIDADES)
        raise ValueError(f"Periodicidad '{periodicidad}' no reconocida. Opciones: {opciones}.")
    return PERIODOS_POR_ANIO[clave]


def capitalizaciones_por_periodo(capitalizacion: str, periodo_nominal: str = "anual") -> int:
    """
    Calcula m: cuántas veces se capitaliza la tasa nominal dentro de su periodo.

    Ejemplos:
        anual capitalizable mensualmente         -> m = 12
        semestral capitalizable trimestralmente  -> m = 2
    """
    m_cap = periodos_por_anio(capitalizacion)
    m_nom = periodos_por_anio(periodo_nominal)
    if m_cap < m_nom or m_cap % m_nom != 0:
        raise ValueError(
            f"Una tasa nominal {periodo_nominal} no puede capitalizarse "
            f"{capitalizacion}mente: la capitalización debe caber un número "
            f"entero de veces dentro del periodo de la tasa."
        )
    return m_cap // m_nom


# ---------------------------------------------------------------------------
# Conversiones básicas
# ---------------------------------------------------------------------------

def nominal_a_efectiva(j: float, capitalizacion: str, periodo_nominal: str = "anual") -> float:
    """
    Tasa nominal -> tasa efectiva del periodo de capitalización.

        i = j / m

    Ej.: j = 24 % anual capitalizable mensualmente -> i = 0.24 / 12 = 2 % mensual.
    """
    m = capitalizaciones_por_periodo(capitalizacion, periodo_nominal)
    return j / m


def efectiva_a_nominal(i: float, capitalizacion: str, periodo_nominal: str = "anual") -> float:
    """
    Tasa efectiva del periodo de capitalización -> tasa nominal.

        j = i · m

    Ej.: i = 2 % mensual -> j = 24 % anual capitalizable mensualmente.
    """
    m = capitalizaciones_por_periodo(capitalizacion, periodo_nominal)
    return i * m


def efectiva_a_efectiva(i: float, origen: str, destino: str) -> float:
    """
    Tasa efectiva de una periodicidad -> tasa efectiva de otra periodicidad.

        i_destino = (1 + i_origen)^(m_origen / m_destino) - 1

    Ej.: 3 % efectiva trimestral -> semestral:  (1.03)^(4/2) - 1 = 6.09 %
    """
    if i <= -1:
        raise ValueError(f"La tasa debe ser mayor que -100 %. Se recibió {i}.")
    m_origen = periodos_por_anio(origen)
    m_destino = periodos_por_anio(destino)
    return (1 + i) ** (m_origen / m_destino) - 1


# ---------------------------------------------------------------------------
# Conversión completa (la que usará la interfaz)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ConversionTasa:
    """
    Resultado de convertir una tasa a la tasa efectiva del periodo de pago.
    Guarda los valores intermedios para poder mostrar el procedimiento.
    """
    tipo: str                    # "nominal" o "efectiva"
    tasa_dada: float             # la tasa que ingresó el usuario
    periodicidad_dada: str       # periodo de la tasa dada (ej. "anual")
    capitalizacion: str | None   # solo para nominales (ej. "mensual")
    m: int | None                # capitalizaciones por periodo (solo nominales)
    tasa_capitalizacion: float | None  # i = j/m (paso intermedio, solo nominales)
    periodo_pago: str            # periodicidad de los pagos de la serie
    tasa_pago: float             # RESULTADO: tasa efectiva del periodo de pago


def convertir_a_periodo_de_pago(
    tasa: float,
    tipo: str,
    periodicidad: str,
    periodo_pago: str,
    capitalizacion: str | None = None,
) -> ConversionTasa:
    """
    Convierte cualquier tasa a la tasa efectiva del periodo de pago.

    Parámetros:
        tasa           : valor decimal de la tasa (24 % -> 0.24)
        tipo           : "nominal" o "efectiva"
        periodicidad   : periodo al que está referida la tasa (ej. "anual")
        periodo_pago   : periodicidad de los pagos de la serie (ej. "semestral")
        capitalizacion : frecuencia de capitalización (obligatoria si es nominal)

    Ejemplo:
        24 % nominal anual capitalizable mensualmente, pagos semestrales:
            paso 1:  i = 0.24 / 12 = 2 % mensual
            paso 2:  i_sem = (1.02)^(12/2) - 1 = 12.6162 % semestral
    """
    tipo = tipo.strip().lower()

    if tipo == "nominal":
        if capitalizacion is None:
            raise ValueError("Una tasa nominal necesita su frecuencia de capitalización.")
        m = capitalizaciones_por_periodo(capitalizacion, periodicidad)
        tasa_cap = tasa / m                                   # Paso 1
        tasa_pago = efectiva_a_efectiva(tasa_cap, capitalizacion, periodo_pago)  # Paso 2
        return ConversionTasa(tipo, tasa, periodicidad, capitalizacion, m,
                              tasa_cap, periodo_pago, tasa_pago)

    if tipo == "efectiva":
        tasa_pago = efectiva_a_efectiva(tasa, periodicidad, periodo_pago)
        return ConversionTasa(tipo, tasa, periodicidad, None, None,
                              None, periodo_pago, tasa_pago)

    raise ValueError(f"Tipo de tasa '{tipo}' no válido. Use 'nominal' o 'efectiva'.")

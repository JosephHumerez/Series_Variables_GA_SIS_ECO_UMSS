"""
Núcleo matemático de la calculadora de Series Variables en Gradiente Aritmético.

Este paquete NO depende de la interfaz web: se puede usar y probar por separado.

Módulos:
    factores  -> factores financieros (P/F, F/P, P/A, A/P, F/A, A/F, P/G, A/G, F/G)
    tasas     -> conversión de tasas nominales y efectivas al periodo de pago
    serie     -> cálculo directo de la serie (A, P, F, cuotas X_k, diferidas, avisos)
    despejes  -> cálculos inversos: n por último pago, A', G y sistema de 2 ecuaciones
    numericos -> métodos numéricos: búsqueda de intervalos, bisección, Newton-Raphson
    despejes_numericos -> despejes de i y n conociendo P, F o A (con interpolación)
    procedimiento -> pasos "estilo libro" (LaTeX) a partir de los resultados
"""

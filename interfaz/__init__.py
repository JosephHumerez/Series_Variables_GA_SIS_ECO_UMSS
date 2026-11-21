"""
Interfaz web (Streamlit) de la calculadora.

Cada página es un módulo con una función mostrar() que dibuja su contenido.
Toda la matemática está en el paquete "gradiente"; aquí solo se piden los
datos, se llama al núcleo y se muestran los resultados.

Módulos:
    comun       -> piezas compartidas (mostrar pasos, tasa en uso, entradas)
    pag_inicio  -> página de bienvenida
    pag_tasas   -> página 1: conversión de tasas
"""

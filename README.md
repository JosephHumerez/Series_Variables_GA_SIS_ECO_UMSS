# Calculadora de Series Variables en Gradiente Aritmético

Aplicación web local para resolver problemas de **series en gradiente aritmético (G.A.)** siguiendo la metodología del libro **_Ingeniería Económica_ de M. Sc. Emir Vargas Peredo** (Unidad 2: Valor del dinero en el tiempo, sección *Factor de conversión de gradiente aritmético*).

La calculadora no solo da el resultado: muestra el **procedimiento paso a paso tal como lo resuelve el libro**, el **diagrama de flujo de caja** y la **tabla de pagos**.

> Proyecto semestral: Sistemas Económicos, UMSS.

---

## Contenido

1. [Funcionalidades](#funcionalidades)
2. [Metodología del libro](#metodología-del-libro)
3. [Tech stack](#tech-stack)
4. [Estructura del proyecto](#estructura-del-proyecto)
5. [Instalación](#instalación)
6. [Modo de uso](#modo-de-uso)
7. [Tutorial](#tutorial)
8. [Pruebas automáticas](#pruebas-automáticas)
9. [Convenciones y decisiones](#convenciones-y-decisiones)
10. [Estado del proyecto](#estado-del-proyecto)

---

## Funcionalidades

| Módulo | Qué hace |
|---|---|
| **Marco teórico** | Manual para aprender el tema desde cero, en 7 capítulos: conceptos básicos, tasas de interés, factores financieros, gradiente aritmético (con el Ejercicio 1 resuelto), series diferidas, despejes y un resumen de fórmulas. Cada capítulo termina con un enlace a la página donde se practica. |
| **Conversión de tasas** | Convierte una tasa nominal (con cualquier capitalización) o efectiva a la **tasa efectiva del periodo de pago**. Periodicidades: mensual, bimestral, trimestral, cuatrimestral, semestral y anual. |
| **Cálculo directo** | Con A', G, i, n y el tipo de gradiente calcula la **anualidad equivalente A** (desglosada en base + gradiente), el **valor presente P**, el **valor futuro F** y cualquier cuota **Xₖ**. |
| **Series diferidas** | Series cuya primera cuota no ocurre en el periodo 1: P se ubica un periodo antes de la primera cuota y luego se traslada al periodo 0. |
| **Diagrama de flujo** | Línea de tiempo de 0 a n con flechas ↑ (ingresos) o ↓ (egresos) proporcionales al monto, el valor equivalente P o F y la tasa i. |
| **Avisos** | Si en un gradiente decreciente alguna cuota llega a cero o se vuelve negativa, se avisa en qué periodo ocurre (sin bloquear el cálculo). |
| **Despejes** | n por último pago; A' o G conociendo P, F o A; A' y G a la vez (sistema 2×2); i y n por métodos numéricos (bisección + Newton-Raphson), con interpolación lineal de referencia. |

---

## Metodología del libro

Una serie en gradiente aritmético es una secuencia de pagos que **aumentan o disminuyen en un monto constante G** en cada periodo. El primer pago ocurre al final del periodo 1 y el gradiente recién aparece en el periodo 2:

```
Periodo:   1     2       3        ...   n
Pago:      A'    A'±G    A'±2G    ...   A'±(n−1)G
```

El libro **descompone** la serie en dos:

```
Serie uniforme base:    A'   A'   A'   ...  A'
Serie gradiente pura:   0    G    2G   ...  (n−1)G
```

Y la resuelve en este orden, que la calculadora respeta y muestra:

| Paso | Fórmula |
|---|---|
| 1. Anualidad equivalente | A = A' ± G·(A/G; i; n) |
| 2. Valor presente | P = A·(P/A; i; n) |
| 3. Valor futuro | F = A·(F/A; i; n) |
| Serie diferida | P₀ = P·(P/F; i; inicio − 1) |
| Cuota del periodo k | Xₖ = A' ± (k − 1)·G |

(+) gradiente creciente · (−) gradiente decreciente

**Factores implementados** (capitalización discreta, anualidades vencidas):

| Factor | Fórmula |
|---|---|
| (F/P; i; n) | (1 + i)ⁿ |
| (P/F; i; n) | 1 / (1 + i)ⁿ |
| (P/A; i; n) | [(1 + i)ⁿ − 1] / [i(1 + i)ⁿ] |
| (F/A; i; n) | [(1 + i)ⁿ − 1] / i |
| (A/P), (A/F) | inversos de (P/A) y (F/A) |
| (P/G; i; n) | [(1 + i)ⁿ − 1 − n·i] / [i²(1 + i)ⁿ] |
| (A/G; i; n) | 1/i − n / [(1 + i)ⁿ − 1] |
| (F/G; i; n) | [(1 + i)ⁿ − 1 − n·i] / i² |

**Notación** (la del libro):

| Símbolo | Significado |
|---|---|
| A' | Primer pago (serie base) |
| G | Gradiente: variación constante por periodo |
| i | Tasa efectiva del periodo de pago |
| n | Número de periodos (cuotas) |
| P | Valor presente (periodo 0) |
| F | Valor futuro (periodo n) |
| A | Anualidad equivalente total |
| Xₖ | Pago del periodo k |

---

## Tech stack

| Tecnología | Uso |
|---|---|
| **Python 3.12+** (desarrollado con 3.14) | Lenguaje principal |
| **[Streamlit](https://streamlit.io)** | Interfaz web local (formularios, resultados, fórmulas LaTeX con KaTeX) |
| **[Plotly](https://plotly.com/python/)** | Diagrama de flujo de caja interactivo |
| **[pytest](https://pytest.org)** | Pruebas automáticas (incluye los ejercicios del libro) |
| Biblioteca estándar (`math`, `dataclasses`, `bisect`) | Toda la matemática financiera y los métodos numéricos, **sin librerías externas** |

La matemática está **separada de la interfaz**: el paquete `gradiente/` no depende de Streamlit, se puede usar y probar por sí solo.

---

## Estructura del proyecto

```
Series_Variables_GA_SIS_ECO_UMSS/
├── app.py                     # Punto de entrada: menú de navegación
├── requirements.txt           # Librerías necesarias
├── pytest.ini                 # Configuración de las pruebas
│
├── gradiente/                 # NÚCLEO MATEMÁTICO (sin interfaz)
│   ├── factores.py            # P/F, F/P, P/A, A/P, F/A, A/F, P/G, A/G, F/G
│   ├── tasas.py               # Conversión nominal ↔ efectiva
│   ├── serie.py               # Cálculo directo: A, P, F, Xₖ, diferidas, avisos
│   ├── despejes.py            # n por último pago, A', G, sistema 2×2
│   ├── numericos.py           # Bisección y Newton-Raphson
│   ├── despejes_numericos.py  # Despeje de i y n (con interpolación lineal)
│   └── procedimiento.py       # Pasos "estilo libro" en LaTeX
│
├── interfaz/                  # INTERFAZ WEB (Streamlit)
│   ├── comun.py               # Piezas compartidas (pasos, tasa en uso)
│   ├── estilo.py              # Código de colores, tarjetas y leyenda
│   ├── diagrama.py            # Diagrama de flujo de caja (Plotly)
│   ├── paginas.py             # Registro de páginas y secciones del menú
│   ├── pag_inicio.py          # Página de inicio
│   ├── pag_teoria.py          # Página: marco teórico (manual)
│   ├── pag_tasas.py           # Página: conversión de tasas
│   ├── pag_directo.py         # Página: cálculo directo
│   └── pag_despejes.py        # Página: despejes (n, A', G, i)
│
└── tests/                     # Pruebas automáticas
```

---

## Instalación

### Requisitos

- **Python 3.12 o superior**: [python.org/downloads](https://www.python.org/downloads/). En Windows, marca la casilla *"Add Python to PATH"* al instalar.
- **Git** (opcional, para clonar el repositorio).

### Pasos

**1. Descargar el proyecto**

```bash
git clone https://github.com/JosephHumerez/Series_Variables_GA_SIS_ECO_UMSS.git
cd Series_Variables_GA_SIS_ECO_UMSS
```

(O descarga el ZIP desde GitHub con *Code → Download ZIP* y descomprímelo.)

**2. Crear el entorno virtual** (una carpeta `.venv` con las librerías del proyecto, aislada del resto del sistema)

```bash
python -m venv .venv
```

**3. Activar el entorno virtual**

| Sistema | Comando |
|---|---|
| Windows (PowerShell) | `.\.venv\Scripts\Activate.ps1` |
| Windows (CMD) | `.venv\Scripts\activate.bat` |
| macOS / Linux | `source .venv/bin/activate` |

Al activarlo, la línea de la terminal empieza con `(.venv)`.

> **Error en PowerShell "la ejecución de scripts está deshabilitada":** ejecuta una sola vez
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a intentarlo.

**4. Instalar las librerías**

```bash
pip install -r requirements.txt
```

---

## Modo de uso

### Iniciar la calculadora

Con el entorno virtual activado:

```bash
streamlit run app.py
```

Se abre el navegador en **http://localhost:8501**. Si no se abre solo, copia esa dirección.

> La primera vez Streamlit puede pedir un correo en la terminal: deja el campo vacío y pulsa Enter.

### Detenerla

En la terminal, pulsa **Ctrl + C**. Para salir del entorno virtual: `deactivate`.

### Partes de la pantalla

```
┌──────────────────────┬────────────────────────────────────────┐
│ BARRA LATERAL        │  CONTENIDO DE LA PÁGINA                │
│                      │                                        │
│ GENERAL              │  Datos  →  Resultados  →  Diagrama     │
│   Inicio             │                                        │
│ APRENDER             │  [Procedimiento] [Tabla] [Cuota Xₖ]    │
│   Marco teórico      │                                        │
│ PRACTICAR            │                                        │
│   Conversión de tasas│                                        │
│   Cálculo directo    │                                        │
│   Despejes           │                                        │
│ ──────────────────── │                                        │
│ Tasa en uso          │                                        │
│ Código de colores    │                                        │
└──────────────────────┴────────────────────────────────────────┘
```

- **Menú lateral:** cambia de página. Está agrupado en *General*, *Aprender* (el manual) y *Practicar* (las calculadoras). La barra no se puede esconder.
- **Tasa en uso:** la tasa guardada desde *Conversión de tasas*; las páginas de cálculo la toman automáticamente.
- **Tema claro u oscuro:** en el menú **⋮** (arriba a la derecha) se elige *Light*, *Dark* o *System*, que sigue la configuración del sistema operativo.

### Código de colores

Cada concepto tiene **siempre el mismo color** en toda la aplicación: en las etiquetas de los datos, las tarjetas de resultado, el resultado de cada paso del procedimiento, el diagrama y la tabla de pagos. La leyenda también aparece en la barra lateral.

| Color | Concepto |
|---|---|
| Azul | A', Xₖ: primer pago y cuotas (base) |
| Naranja | G: gradiente |
| Violeta | A: anualidad equivalente |
| Verde | P: valor presente |
| Rojo | F: valor futuro |
| Amarillo | i: tasa de interés |
| Gris | n: número de periodos |

En el **diagrama de flujo**, cada flecha muestra la descomposición del libro:
- **Gradiente creciente:** tramo azul (la base A') y encima un tramo naranja (lo que suma el gradiente).
- **Gradiente decreciente:** flecha azul (la cuota) y un tramo naranja punteado (lo que el gradiente le restó a la base).
- Una línea azul punteada marca el nivel de A'.

Los colores se definen en un solo lugar: [`interfaz/estilo.py`](interfaz/estilo.py).

### Ingreso de datos

- Los porcentajes se escriben **sin el símbolo %**: para 9,27 % escribe `9.27`.
- En las casillas, el separador decimal lo decide el **navegador según su idioma**: en español muestra coma (`9,2700`), en inglés punto (`9.2700`). Escribe los decimales con el separador que veas en la casilla. Los resultados siempre se muestran con **coma decimal** (`146 111,54`), como en el libro.
- **G siempre se escribe positivo**; si disminuye, elige *Decreciente*.
- Los resultados se actualizan solos al cambiar cualquier dato.

---

## Tutorial

> **¿Primera vez con el tema?** Empieza por **Marco teórico** en el menú (sección *Aprender*). Es un manual con la teoría, las fórmulas y ejemplos resueltos; al final de cada capítulo, el botón **Ir a…** lleva a la página donde se practica lo aprendido.

### Ejemplo 1: Gradiente decreciente, valor presente (Ejercicio 1 del libro, pág. 35)

> *Un primer pago de 30 000 disminuye en 2 000 cada semestre hasta un último pago de 10 000. Con una tasa de 9,27 % semestral, ¿cuál es el valor presente?*

1. Abre **Cálculo directo** en el menú. Ya viene cargada con estos datos:

   | Campo | Valor |
   |---|---|
   | Primer pago, A' | 30000 |
   | Gradiente, G | 2000 |
   | Tipo de gradiente | Decreciente |
   | Número de cuotas, n | 11 |
   | Tasa, i (%) | 9.27 |

2. Lee los resultados:

   | A | P | F | Última cuota |
   |---|---|---|---|
   | 21 745,33 | **146 111,54** | 387 431,46 | 10 000,00 |

3. Revisa el **diagrama**: las flechas bajan de altura de 30 000 a 10 000 y la flecha roja muestra P en el periodo 0.
4. Abre la pestaña **Procedimiento**:

   ```
   A = A' − G (A/G; 9,27 %; 11) = 30 000 − 2 000 (4,12734) = 21 745,33
   P = A (P/A; 9,27 %; 11) = 21 745,33 (6,71922) = 146 111,54
   ```

5. En **Tabla de pagos** están las 11 cuotas, y en **Cuota Xₖ** puedes calcular cualquiera.

> **Nota:** n se obtuvo con n = (30 000 − 10 000)/2 000 + 1 = 11.

### Ejemplo 2: Gradiente creciente, valor futuro (Ejercicio 2 del libro)

> *Se depositan mensualmente ingresos que empiezan en 27 000 y aumentan 3 000 cada mes durante un año, al 0,66 % mensual. ¿Cuánto se acumula?*

1. En **Cálculo directo** ingresa:

   | Campo | Valor |
   |---|---|
   | A' | 27000 |
   | G | 3000 |
   | Tipo | Creciente |
   | n | 12 |
   | i (%) | 0.66 |

2. Resultado: **F = 538 445,20** (A = 43 264,85).
3. En **Opciones avanzadas** elige *Las cuotas son: Ingresos (↑)* y *Valor equivalente: F* para ver la flecha de F en el periodo 12.

### Ejemplo 3: Convertir una tasa nominal y usarla

> *La tasa es 24 % anual capitalizable mensualmente y los pagos son semestrales.*

1. Abre **Conversión de tasas**. Ingresa: *Nominal*, `24`, periodo *anual*, capitalización *mensual*, pagos *semestrales*.
2. Comprueba el recuadro azul: *"24 % nominal anual capitalizable mensualmente, con pagos semestrales"*.
3. Resultado: **12,6162 % semestral**. El procedimiento muestra:

   ```
   i = j / m = 24 % / 12 = 2 % mensual
   i_sem = (1 + 0,02)^(12/2) − 1 = 12,6162 %
   ```

4. Pulsa **Usar esta tasa en los cálculos**. La tasa aparece en la barra lateral.
5. Ve a **Cálculo directo**: la casilla *"Usar la tasa en uso"* ya está marcada.

### Ejemplo 4: Serie diferida

> *Igual que el Ejemplo 1, pero la primera cuota ocurre en el periodo 4.*

1. En **Cálculo directo** abre **Opciones avanzadas** y pon *Periodo de la primera cuota* = `4`.
2. El procedimiento agrega el **Paso 2b**: el valor presente de la serie queda en el periodo 3 y se trae al periodo 0 con (P/F; i; 3).
3. En el diagrama las cuotas empiezan en el periodo 4.

### Ejemplo 5: Aviso de cuotas negativas

1. Con los datos del Ejemplo 1, cambia **n** a `20`.
2. Aparece un aviso amarillo: la cuota 16 vale cero y desde ahí las cuotas serían negativas, o sea que el flujo cambia de sentido. En el diagrama se ven en naranja apuntando al lado contrario.

### Ejemplo 6: Despejes

Abre **Despejes** en el menú y elige en *¿Qué deseas hallar?* la incógnita. Cada opción viene cargada con un ejercicio del libro:

| Opción | Datos por defecto | Resultado |
|---|---|---|
| n: con el primer y el último pago | A' = 30 000, último = 10 000, G = 2 000 | n = 11, decreciente |
| A': conociendo G y P, F o A | P = 8 000, G = 500 ↑, i = 15 %, n = 5 | A' = 1 525,12 |
| G: conociendo A' y P, F o A | F = 538 445,20, A' = 27 000, i = 0,66 %, n = 12 | G = 3 000, creciente |
| A' y G: conociendo P, F o A y una cuota Xₖ | P = 146 111,54, X₁₁ = 10 000, i = 9,27 %, n = 11 | A' = 30 000, G = 2 000, decreciente |
| i: tasa de interés (método numérico) | F = 538 445,20, A' = 27 000, G = 3 000 ↑, n = 12 | i = 0,66 % (interpolada: 0,6596 %) |
| n: conociendo P, F o A (método numérico) | P = 146 111,54, A' = 30 000, G = 2 000 ↓, i = 9,27 % | n = 11 |

Debajo de los resultados aparecen:
- El **diagrama** de la serie hallada, con el dato conocido (P o F) en rojo.
- **Procedimiento:** el despeje paso a paso, por ejemplo la regla de Cramer en el sistema 2×2 o la interpolación lineal en el despeje de i.
- **Verificación:** el cálculo directo con la serie hallada, que debe reproducir el dato conocido.
- **Tabla de pagos.**

> **Nota:** al despejar G, el **signo** del resultado indica el tipo de gradiente: si sale negativo, es decreciente. En el despeje numérico de n del Ejercicio 1 aparece un aviso de que existe otra solución; corresponde a una serie con cuotas negativas y por eso se muestra la menor (n = 11).

---

## Pruebas automáticas

El proyecto tiene **más de 150 pruebas**, entre ellas los **ejercicios resueltos del libro**. Con el entorno virtual activado:

```bash
python -m pytest -v
```

Solo las pruebas de los ejercicios del libro:

```bash
python -m pytest -v -k "libro"
```

| Ejercicio del libro (pág. 35) | Datos | Resultado oficial | Calculadora |
|---|---|---|---|
| Ej. 1: hallar n | A' = 30 000, último = 10 000, G = 2 000 ↓ | n = 11 | n = 11 (correcto) |
| Ej. 1: hallar P | i = 9,27 % semestral | P = 146 111,54 | 146 111,54 (correcto) |
| Ej. 2: hallar F | A' = 27 000, G = 3 000 ↑, n = 12, i = 0,66 % | F = 538 445,20 | 538 445,20 (correcto) |
| Ej. 6: hallar A' | P = 8 000, n = 5, G = 500 ↑, i = 15 % | A' = 1 525,12 | 1 525,12 (correcto) |

Además de los ejercicios, las pruebas verifican:
- Los factores contra los valores de tabla (5 decimales).
- Que P y F calculados con factores coinciden con descontar cada cuota una por una.
- Los despejes "de ida y vuelta": se despeja la incógnita y se recalcula el dato original.
- La interfaz, con el simulador de Streamlit (`AppTest`).

---

## Convenciones y decisiones

- **Precisión:** todo se calcula con precisión completa. Los factores se **muestran** a 5 decimales (como la Tabla 1 del libro) y los montos a 2. Si se multiplican a mano los valores mostrados, puede haber diferencias de centavos; el resultado de la calculadora es el exacto.
- **Formato:** `146 111,54` (espacio para miles, coma decimal); factores como **(A/G; 9,27 %; 11)**.
- **Anualidades vencidas** y **capitalización discreta**, como en la Unidad 2 del libro. No se incluyen tasas anticipadas ni capitalización continua.
- **Cuotas negativas:** no bloquean el cálculo; se avisa en qué periodo ocurren.
- **n con decimales** (despejes numéricos): se muestra el valor exacto y se sugiere el entero más cercano.
- **Varias soluciones** (cuando las cuotas cambian de signo puede haber más de un n o i): se muestra la menor y se avisa.

---

## Estado del proyecto

| Parte | Estado |
|---|---|
| Núcleo matemático (factores, tasas, serie, despejes, métodos numéricos, procedimiento) | Completo y probado |
| Página de inicio | Completo |
| Marco teórico (manual con enlaces a la práctica) | Completo |
| Página de conversión de tasas | Completo |
| Página de cálculo directo con diagrama de flujo | Completo |
| Página de despejes (n, i, A', G, sistema 2×2) | Completo |

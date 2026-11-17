# ⚡ Planificador de Red de Distribución Eléctrica Municipal
## Árbol de Expansión Mínima: Prim y Kruskal

**Asignatura:** Análisis y Diseño de Algoritmos – UNEG  
**Bitácora 2 – Parte 1**  
**Equipo 5**  
**Repositorio:** https://github.com/Joha0012/Bitacora-2-Arbol-de-expansion-minima-Prim-y-Kruskal

### Integrantes

| Nombre | Rol |
|---|---|
| Ing. Bryan Salazar | Integrante |
| Ing. Johana Carvajal | Integrante |
| Ing. David González | Integrante |
| Ing. Yrene Corrales | Integrante |
| Ing. José Ortiz | Integrante |

---

## 📋 Descripción del Problema

Diseño óptimo de la red de tendido eléctrico que interconecta subestaciones
de distribución de un municipio, minimizando el costo total de instalación
de cables de alta tensión.

Cada subestación es un **vértice** del grafo; cada ruta posible de tendido
entre dos subestaciones es una **arista** con peso = costo estimado (miles de USD).
El Árbol de Expansión Mínima (MST) define el subconjunto de cables de menor
costo que conecta todas las subestaciones sin ciclos.

---

## 📂 Estructura del Repositorio

```
Bitacora-2-Arbol-de-expansion-minima-Prim-y-Kruskal/
├── src/
│   ├── grafo.py              # Clase Grafo (lista de adyacencia)
│   ├── union_find.py         # Union-Find (compresión de caminos + rango)
│   ├── prim.py               # Algoritmo de Prim (min-heap)
│   ├── kruskal.py            # Algoritmo de Kruskal (Union-Find)
│   ├── mst_algorithms.py     # Fachada + red eléctrica de ejemplo (demo consola)
│   ├── planificador.py       # Lógica de aplicación (carga CSV, trazas, mediciones)
│   ├── interfaz.py           # Interfaz gráfica de escritorio (Tkinter + Matplotlib)
│   └── servidor_web.py       # Servidor web local (interfaz en el navegador)
├── tests/
│   ├── test_mst.py           # 10 pruebas (unitarias, Hypothesis, diferencial NetworkX)
│   ├── test_union_find.py    # 5 pruebas unitarias de Union-Find
│   └── test_planificador.py  # 14 pruebas de la lógica de la aplicación
├── experiments/
│   ├── piloto.py             # Medición piloto y generación de gráficas
│   ├── datos_piloto.csv      # Datos experimentales
│   └── grafica_piloto.png    # Gráfica de rendimiento
├── data/
│   └── red_municipal.csv     # Red de Ciudad Guayana (12 subestaciones)
├── docs/
│   └── Equipo_5_Bitacora2.md # Informe completo (fuente del PDF)
├── requirements.txt
└── README.md
```

---

## 🔧 Requisitos Previos

- **Python** 3.10 o superior
- **pip** (gestor de paquetes de Python)
- **Git** (para clonar el repositorio)

Verificar que Python está instalado:

```bash
python --version
```

> Debe mostrar `Python 3.10.x` o superior (ej. `Python 3.13.17`).

---

## 📦 Instalación Paso a Paso

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/Joha0012/Bitacora-2-Arbol-de-expansion-minima-Prim-y-Kruskal.git
```

### Paso 2: Entrar al directorio del proyecto

```bash
cd Bitacora-2-Arbol-de-expansion-minima-Prim-y-Kruskal
```

### Paso 3: Instalar las dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:

| Librería | Versión mínima | Para qué se usa |
|---|---|---|
| `networkx` | 3.0 | Referencia diferencial en pruebas y layouts del grafo |
| `hypothesis` | 6.0 | Pruebas basadas en propiedades aleatorias |
| `matplotlib` | 3.5 | Gráficas de rendimiento e interfaz de escritorio |
| `pytest` | 7.0 | Ejecución de pruebas automatizadas |
| `numpy` | 1.24 | Dependencia de matplotlib |

### Paso 4: Verificar la instalación (ejecutar las pruebas)

```bash
python -m pytest tests -v
```

Resultado esperado: **29 pruebas pasan** ✅

---

## 🚀 Cómo Usar el Programa

El programa ofrece **3 formas de ejecución**:

---

### Opción A: 🌐 Interfaz Web en el Navegador (Recomendada)

La forma más sencilla. Levanta un servidor local y se usa desde Google Chrome u otro navegador.

**Paso 1:** Iniciar el servidor web:

```bash
cd src
python servidor_web.py
```

Verá el mensaje:
```
Servidor Web Planificador MST levantado en http://localhost:5000
```

**Paso 2:** Abrir el navegador (Chrome, Firefox, Edge) y visitar:

```
http://localhost:5000
```

**Paso 3:** Usar la interfaz web:

1. **Cargar una red** — En la barra lateral izquierda, elija una de las tres opciones:
   - **📍 Red Ejemplo (8 Subestaciones):** Red predefinida para probar rápidamente.
   - **🏙️ Red Ciudad Guayana (12 SE):** Datos ilustrativos de 12 subestaciones.
   - **🎲 Red Aleatoria:** Ingrese la cantidad de subestaciones (3–100) y pulse el botón.

2. **Seleccionar el algoritmo** — Elija **Kruskal**, **Prim** o **Ambos**:
   - Si elige **Prim**, seleccione el nodo de origen (la subestación central).

3. **Calcular el MST** — Pulse **⚡ Calcular MST Óptimo**:
   - El grafo se actualiza resaltando en azul los cables del plan óptimo.
   - En las tarjetas superiores aparece: costo del MST, costo total de todas las rutas, ahorro obtenido (%) y tiempo de cómputo.
   - La tabla inferior muestra cada cable seleccionado con su costo.

4. **Animar paso a paso** — Pulse **▶ Animar Traza** para ver cómo decide el algoritmo:
   - **Amarillo:** arista que se está evaluando en ese paso.
   - **Azul:** arista aceptada (cable incluido en el plan).
   - **Rojo punteado:** arista rechazada (formaría un ciclo).
   - Use **⏭ Paso** para avanzar manualmente un paso a la vez.

5. **Editar la red** — En la sección "Editar Conexión Candidata":
   - Seleccione dos subestaciones y un costo, pulse **Guardar** para agregar/actualizar la ruta.
   - Pulse **Eliminar** para quitar una ruta existente.

**Paso 4:** Para detener el servidor, presione `Ctrl+C` en la terminal.

---

### Opción B: 🖥️ Interfaz Gráfica de Escritorio (Tkinter)

Aplicación nativa de Python con más funcionalidades avanzadas.

```bash
cd src
python interfaz.py
```

Se abre una ventana con 3 pestañas:

**Pestaña 1 — Diseño de la Red:**
1. **Cargar red** — Botones: red de ejemplo, red municipal, abrir CSV propio, o generar aleatoria.
2. **Editar rutas** — Agregar/actualizar/eliminar rutas y agregar nuevas subestaciones.
3. **Algoritmo** — Seleccionar Prim, Kruskal o Ambos. Elegir origen para Prim.
4. **Calcular MST** — Muestra el grafo con el MST resaltado y la tabla de decisiones.
5. **Animar** — Animación automática o paso a paso con velocidad ajustable.
6. **Exportar** — Guardar el plan de tendido a CSV para licitación.

**Pestaña 2 — Rendimiento Prim vs Kruskal:**
- Configure tamaños de entrada (ej. `50, 100, 500, 1000`), repeticiones, semilla y densidad.
- Pulse **Ejecutar medición** → genera gráfica comparativa log-log y tabla de tiempos.

**Pestaña 3 — Ayuda:**
- Instrucciones completas, formato CSV, leyenda del gráfico y ventajas/desventajas de cada algoritmo.

---

### Opción C: 💻 Demo en Consola

La versión mínima para ver los algoritmos en acción:

```bash
cd src
python mst_algorithms.py
```

Salida esperada:
```
============================================================
  MST – Algoritmo de Prim
============================================================
  Subestación Central    --- SE Sur                 (3.0 k$)
  Subestación Central    --- SE Norte               (4.0 k$)
  SE Norte               --- SE Industrial          (2.0 k$)
  SE Industrial          --- SE Residencial B       (2.0 k$)
  SE Industrial          --- SE Este                (3.0 k$)
  SE Sur                 --- SE Residencial A       (4.0 k$)
  Subestación Central    --- SE Oeste               (5.0 k$)
------------------------------------------------------------
  Costo total MST: 23.0 miles de USD
  Aristas en MST : 7
============================================================

OK: Prim y Kruskal producen el mismo costo total MST.
```

---

## 📊 Formato CSV para Redes Propias

Puede crear su propio archivo CSV con las rutas candidatas de su red eléctrica:

```csv
origen,destino,costo
Subestación A,Subestación B,12.5
Subestación B,Subestación C,8
Subestación A,Subestación C,15
```

**Reglas:**
- **Encabezado obligatorio:** `origen,destino,costo` (también acepta `desde,hasta,peso` o `u,v,w`).
- **Separador:** coma `,` o punto y coma `;`.
- **Costo decimal:** acepta punto (`12.5`) o coma (`12,5`).
- **Costos no negativos:** los pesos representan costos reales de tendido.
- **Sin lazos:** una subestación no puede conectarse consigo misma.

**Cargar CSV:**
- **Web:** Modifique `data/red_municipal.csv` y recargue con el botón "Red Ciudad Guayana".
- **Escritorio:** Use el botón **Abrir CSV…** en la pestaña "Diseño de la red".

---

## 🧪 Ejecución de Pruebas

### Todas las pruebas (29 pruebas):
```bash
python -m pytest tests -v
```

### Solo pruebas de algoritmos MST (10 pruebas):
```bash
python -m pytest tests/test_mst.py -v
```

### Solo pruebas de Union-Find (5 pruebas):
```bash
python -m pytest tests/test_union_find.py -v
```

### Solo pruebas de la lógica de la interfaz (14 pruebas):
```bash
python -m pytest tests/test_planificador.py -v
```

---

## 📈 Experimento Piloto de Rendimiento

Genera un CSV con mediciones y una gráfica PNG:

```bash
python experiments/piloto.py
```

**Resultados verificados** (semilla 42, densidad ≈ 3n aristas, 5 repeticiones):

| n (vértices) | Prim (ms) | Kruskal (ms) | Razón K/P |
|---|---|---|---|
| 50 | 0.076 | 0.148 | 1.95× |
| 500 | 1.439 | 2.372 | 1.65× |
| 1 000 | 4.156 | 8.237 | 1.98× |
| 5 000 | 27.876 | 59.924 | 2.15× |

**Conclusión piloto:** Prim es ≈ 2× más rápido que Kruskal en grafos dispersos tipo red eléctrica.

---

## 🔢 Complejidades Teóricas

| Algoritmo | Tiempo | Espacio |
|---|---|---|
| Prim (min-heap) | O((V+E) log V) | O(V + E) |
| Kruskal (Union-Find) | O(E log E) | O(V + E) |

---

## 🎯 Control de Semillas

Todas las pruebas y experimentos que involucran aleatoriedad utilizan la
semilla fija **42**. Esto garantiza **reproducibilidad completa**:

- **Prueba diferencial** (`test_diferencial_networkx`): `random.Random(42)`
- **Experimento piloto** (`piloto.py`): `SEMILLA = 42`
- **Red aleatoria** en la interfaz: semilla configurable (default 42)

---

## 📝 Declaración de Transparencia Tecnológica

**Herramienta:** Antigravity (Gemini) – noviembre 2026  
**Uso:** Generación de estructura inicial del código, sugerencias de pseudocódigo y formato del README.  
**Verificación:** Todos los algoritmos fueron verificados manualmente con trazas paso a paso, comparados contra NetworkX y validados con 29 pruebas unitarias.  
**Descartes:** Se descartaron sugerencias de código con lógica de heap incorrecta que no preservaba el invariante del MST.

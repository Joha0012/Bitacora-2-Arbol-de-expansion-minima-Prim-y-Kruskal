# MST – Red de Distribución Eléctrica Municipal
## Árbol de Expansión Mínima: Prim y Kruskal

**Asignatura:** Análisis y Diseño de Algoritmos – UNEG  
**Bitácora 2 – Parte 1**  
**Equipo 5**

### Integrantes
| Nombre | Rol |
|---|---|
| Ing. Bryan Salazar | Integrante |
| Ing. Johana Carvajal | Integrante |
| Ing. David González | Integrante |
| Ing. Yrene Corrales | Integrante |
| Ing. José Ortiz | Integrante |

---

## Descripción del Problema

Diseño óptimo de la red de tendido eléctrico que interconecta subestaciones
de distribución de un municipio, minimizando el costo total de instalación
de cables de alta tensión.

Cada subestación es un **vértice** del grafo; cada ruta posible de tendido
entre dos subestaciones es una **arista** con peso = costo estimado (USD/km).
El árbol de expansión mínima (MST) define el subconjunto de cables de menor
costo que conecta todas las subestaciones sin ciclos.

---

## Estructura del Repositorio

```
mst-redes-electricas/
├── src/
│   └── mst_algorithms.py     # Implementación de Prim, Kruskal y UnionFind
├── tests/
│   └── test_mst.py           # 10 pruebas (unitarias, Hypothesis, diferencial)
├── experiments/
│   ├── piloto.py             # Medición piloto y generación de gráficas
│   ├── datos_piloto.csv      # Datos experimentales (generado al correr piloto.py)
│   └── grafica_piloto.png    # Gráfica de rendimiento (generada al correr piloto.py)
├── requirements.txt
└── README.md
```

---

## Instalación

```bash
pip install -r requirements.txt
```

> **Python requerido:** 3.10 o superior  
> **Semilla fija reproducible:** `SEMILLA = 42` (definida en `piloto.py` y `test_mst.py`)

---

## Ejecución

### Demostración del algoritmo (red de 8 subestaciones)
```bash
python src/mst_algorithms.py
```

### Pruebas unitarias y de propiedades
```bash
pytest tests/test_mst.py -v
```

### Experimento piloto (genera CSV y PNG)
```bash
python experiments/piloto.py
```

---

## Dependencias y versiones

| Librería      | Versión mínima | Uso                                        |
|---------------|----------------|--------------------------------------------|
| networkx      | 3.0            | Referencia diferencial (prueba Test 9)     |
| hypothesis    | 6.0            | Pruebas basadas en propiedades (Test 7, 8) |
| matplotlib    | 3.5            | Gráfica de rendimiento piloto              |
| pytest        | 7.0            | Framework de pruebas                       |
| numpy         | 1.24           | Dependencia de matplotlib                  |

---

## Control de Semillas

Todas las pruebas y experimentos que involucran aleatoriedad utilizan la
semilla fija `42`. Esto garantiza reproducibilidad completa:

- **Prueba diferencial** (`test_diferencial_networkx`): `random.Random(42)`
- **Experimento piloto** (`piloto.py`): `SEMILLA = 42`

---

## Complejidades teóricas

| Algoritmo | Tiempo        | Espacio   |
|-----------|---------------|-----------|
| Prim      | O((V+E) log V)| O(V + E)  |
| Kruskal   | O(E log E)    | O(V + E)  |

---

## Declaración de Transparencia Tecnológica

**Herramienta:** Antigravity (Gemini) – noviembre 2026  
**Uso:** Generación de estructura inicial del código, sugerencias de pseudocódigo y formato del README.  
**Verificación:** Todos los algoritmos fueron verificados manualmente con trazas paso a paso, comparados contra NetworkX y validados con las pruebas unitarias.  
**Descartes:** Se descartaron sugerencias de código con lógica de heap incorrecta que no preservaba el invariante del MST.

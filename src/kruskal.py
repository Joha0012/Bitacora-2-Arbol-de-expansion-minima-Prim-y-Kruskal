"""
Módulo: kruskal.py
Algoritmo de Kruskal con Union-Find.
Complejidad: O(E log E) tiempo, O(V + E) espacio.

Equipo 5 – Análisis y Diseño de Algoritmos – UNEG
Integrantes:
  - Ing. Bryan Salazar
  - Ing. Johana Carvajal
  - Ing. David González
  - Ing. Yrene Corrales
  - Ing. José Ortiz
"""

from __future__ import annotations

from grafo import Grafo
from prim import ResultadoMST
from union_find import UnionFind


def kruskal(grafo: Grafo) -> ResultadoMST:
    """
    Algoritmo de Kruskal con Union-Find (compresión de caminos + rango).

    Encuentra el Árbol de Expansión Mínima (o Bosque de Expansión Mínima
    para grafos desconectados) procesando aristas en orden creciente de peso
    y agregando cada una al MST si no forma un ciclo.

    ──────────────────────────────────────────────────────────────────
    INVARIANTE DE BUCLE:
        Al inicio de cada iteración, el conjunto MST es un subconjunto
        de aristas de algún árbol de expansión mínima de grafo, y no
        contiene ciclos (es un bosque acíclico).

    DEMOSTRACIÓN (inducción sobre el número de aristas procesadas):
        Base: MST = {} → subconjunto vacío de cualquier MST. ✓
        Paso: Sea e = (u, v, w) la arista examinada en orden creciente.
              • Si UF.unir(u, v) = False → u y v ya están conectados
                en MST → agregar e formaría ciclo → se descarta. ✓
              • Si UF.unir(u, v) = True  → u y v en componentes distintas.
                Consideremos el corte (componente(u), resto). La arista e
                es la más ligera que cruza ese corte (porque las anteriores
                de menor peso ya fueron procesadas sin unir estos componentes).
                Por el Teorema del Corte, e pertenece a algún MST. ✓
        Término: |MST| = |V| − 1 (grafo conexo) → MST es árbol de exp. mín. □
    ──────────────────────────────────────────────────────────────────

    Pre-condición:
        - grafo no dirigido, con pesos ≥ 0.
        - Puede ser desconectado (resultado = bosque de expansión mínima).

    Post-condición:
        - resultado contiene hasta (n − 1) aristas acíclicas de peso
          mínimo que conectan todos los componentes del grafo.
        - Para grafo conexo: len(resultado.aristas_mst) == n − 1.

    Complejidad temporal : O(E log E)   (dominada por la ordenación)
                         = O(E log V)   (ya que E ≤ V²)
    Complejidad espacial : O(V + E)

    Args:
        grafo: Grafo no dirigido ponderado (lista de adyacencia).

    Returns:
        ResultadoMST con las aristas del MST/bosque y el peso total.
    """
    n = grafo.n_vertices
    resultado = ResultadoMST()

    if n == 0:
        return resultado

    # Paso 1: Ordenar todas las aristas por peso (creciente) → O(E log E)
    aristas_ordenadas = sorted(grafo.aristas())   # aristas() devuelve (w, u, v)

    # Paso 2: Inicializar Union-Find con n componentes disjuntos
    uf = UnionFind(n)

    # Paso 3: Iterar sobre aristas en orden creciente de peso
    for w, u, v in aristas_ordenadas:
        # ── INVARIANTE SE MANTIENE: solo agregamos si no forma ciclo ──
        if uf.unir(u, v):
            resultado.agregar(u, v, w)
            # Terminar anticipadamente cuando el MST está completo
            if len(resultado.aristas_mst) == n - 1:
                break

    return resultado

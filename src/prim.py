"""
Módulo: prim.py
Algoritmo de Prim con cola de prioridad mínima (min-heap).
Complejidad: O((V + E) log V) tiempo, O(V + E) espacio.

Equipo 5 – Análisis y Diseño de Algoritmos – UNEG
Integrantes:
  - Ing. Bryan Salazar
  - Ing. Johana Carvajal
  - Ing. David González
  - Ing. Yrene Corrales
  - Ing. José Ortiz
"""

from __future__ import annotations
import heapq
from typing import List, Optional

from grafo import Grafo, Vertice


class ResultadoMST:
    """Contiene el árbol de expansión mínima resultante."""

    def __init__(self):
        self.aristas_mst: List[tuple] = []   # [(u, v, w), ...]
        self.peso_total: float = 0.0
        self.vertices_incluidos: List[Vertice] = []

    def agregar(self, u: Vertice, v: Vertice, w: float) -> None:
        """Agrega una arista al MST y acumula su peso."""
        self.aristas_mst.append((u, v, w))
        self.peso_total += w

    def __repr__(self) -> str:
        return (f"ResultadoMST(aristas={len(self.aristas_mst)}, "
                f"peso_total={self.peso_total})")


def prim(grafo: Grafo, origen: Vertice = 0) -> ResultadoMST:
    """
    Algoritmo de Prim con cola de prioridad mínima (min-heap binario).

    Encuentra el Árbol de Expansión Mínima (MST) de un grafo no dirigido
    ponderado creciendo el árbol vértice a vértice desde 'origen'.

    ──────────────────────────────────────────────────────────────────
    INVARIANTE DE BUCLE:
        Al inicio de cada iteración del ciclo while, el conjunto de aristas
        {(padre[v], v, clave[v]) | v ∈ en_mst} forma un árbol de expansión
        mínima del subgrafo inducido por los vértices en en_mst.

    DEMOSTRACIÓN (inducción sobre |en_mst|):
        Base: en_mst = {origen}, árbol vacío → trivialmente es MST del
              subgrafo de un vértice.
        Paso: Sea u = argmin{clave[v] | v ∉ en_mst}. Por el Teorema del
              Corte aplicado al corte (en_mst, V − en_mst), la arista
              (padre[u], u, clave[u]) es la de menor peso que cruza el
              corte y pertenece a algún MST. Agregar u mantiene el
              invariante. □
    ──────────────────────────────────────────────────────────────────

    Pre-condición:
        - grafo es conexo, no dirigido, con pesos ≥ 0.
        - 0 ≤ origen < grafo.n_vertices.

    Post-condición:
        - resultado contiene (n − 1) aristas que forman un árbol de
          expansión mínima de grafo.
        - resultado.peso_total = suma de los pesos de las aristas del MST.

    Complejidad temporal : O((V + E) log V)  con heap binario
    Complejidad espacial : O(V + E)

    Args:
        grafo  : Grafo no dirigido ponderado (lista de adyacencia).
        origen : Vértice semilla desde el cual crece el árbol (default 0).

    Returns:
        ResultadoMST con las aristas del MST y el peso total.

    Raises:
        ValueError: si origen está fuera del rango de vértices válidos.
    """
    n = grafo.n_vertices
    if n == 0:
        return ResultadoMST()

    if not (0 <= origen < n):
        raise ValueError(f"Vértice de origen {origen} fuera de rango [0, {n - 1}]")

    en_mst: List[bool]  = [False] * n
    clave:  List[float] = [float('inf')] * n
    padre:  List[int]   = [-1] * n

    clave[origen] = 0.0
    # Heap lazy: puede contener entradas obsoletas (clave mayor a la actual)
    # Se detectan con la comprobación en_mst[u]
    heap: list = [(0.0, origen)]

    resultado = ResultadoMST()

    while heap:
        peso_actual, u = heapq.heappop(heap)

        # Entrada obsoleta: u ya fue procesado con un clave menor
        if en_mst[u]:
            continue

        # ── INVARIANTE SE MANTIENE: añadimos u al árbol ──
        en_mst[u] = True
        resultado.vertices_incluidos.append(u)

        if padre[u] != -1:
            resultado.agregar(padre[u], u, clave[u])

        # Actualizar claves de vecinos no visitados
        for v, w in grafo.adj[u]:
            if not en_mst[v] and w < clave[v]:
                clave[v] = w
                padre[v] = u
                heapq.heappush(heap, (w, v))

    return resultado

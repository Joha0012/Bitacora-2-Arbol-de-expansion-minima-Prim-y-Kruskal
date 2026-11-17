"""
Árbol de Expansión Mínima (MST) – Algoritmos de Prim y Kruskal
Problema real: Diseño óptimo de red eléctrica de distribución municipal
Asignatura: Análisis y Diseño de Algoritmos – UNEG
Equipo 5:
  - Ing. Bryan Salazar
  - Ing. Johana Carvajal
  - Ing. David González
  - Ing. Yrene Corrales
  - Ing. José Ortiz

Módulo fachada: reexporta Grafo, UnionFind, prim, kruskal y ofrece la red
eléctrica de ejemplo (8 subestaciones) usada en el informe.

Uso:
    python src/mst_algorithms.py
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from grafo import Grafo, Vertice, Arista
from union_find import UnionFind
from prim import prim, ResultadoMST
from kruskal import kruskal

__all__ = [
    "Grafo", "Vertice", "Arista", "UnionFind", "ResultadoMST",
    "prim", "kruskal", "construir_red_electrica_ejemplo", "imprimir_mst",
]


def construir_red_electrica_ejemplo() -> Tuple[Grafo, List[str]]:
    """
    Red de distribución eléctrica simplificada de un municipio.

    8 subestaciones (vértices) y 13 rutas candidatas de tendido (aristas).
    Los pesos representan el costo estimado de tendido en miles de USD.
    MST óptimo: 7 aristas, costo total = 23 k$.
    """
    nombres = [
        "Subestación Central",   # 0
        "SE Norte",              # 1
        "SE Sur",                # 2
        "SE Este",               # 3
        "SE Oeste",              # 4
        "SE Industrial",         # 5
        "SE Residencial A",      # 6
        "SE Residencial B",      # 7
    ]
    g = Grafo(n_vertices=8)
    conexiones = [
        (0, 1, 4), (0, 2, 3), (0, 3, 7), (0, 4, 5),
        (1, 3, 6), (1, 5, 2), (2, 4, 8), (2, 6, 4),
        (3, 5, 3), (3, 7, 5), (4, 6, 7), (5, 7, 2),
        (6, 7, 9),
    ]
    for u, v, w in conexiones:
        g.agregar_arista(u, v, w)
    return g, nombres


def imprimir_mst(resultado: ResultadoMST, nombres: Optional[List[str]] = None,
                 algoritmo: str = "") -> None:
    """Muestra el MST de forma legible en consola."""
    def nombre_v(v: int) -> str:
        return nombres[v] if nombres else str(v)

    print(f"\n{'=' * 60}")
    print(f"  MST – Algoritmo de {algoritmo}")
    print(f"{'=' * 60}")
    for u, v, w in resultado.aristas_mst:
        print(f"  {nombre_v(u):22s} --- {nombre_v(v):22s} ({w:.1f} k$)")
    print(f"{'-' * 60}")
    print(f"  Costo total MST: {resultado.peso_total:.1f} miles de USD")
    print(f"  Aristas en MST : {len(resultado.aristas_mst)}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    grafo, nombres = construir_red_electrica_ejemplo()
    res_prim = prim(grafo, origen=0)
    res_kruskal = kruskal(grafo)

    imprimir_mst(res_prim, nombres, "Prim")
    imprimir_mst(res_kruskal, nombres, "Kruskal")

    assert abs(res_prim.peso_total - res_kruskal.peso_total) < 1e-9
    print("OK: Prim y Kruskal producen el mismo costo total MST.")

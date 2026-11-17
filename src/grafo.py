"""
Módulo: grafo.py
Clase Grafo – representación de red eléctrica como grafo no dirigido y ponderado.

Equipo 5 – Análisis y Diseño de Algoritmos – UNEG
Integrantes:
  - Ing. Bryan Salazar
  - Ing. Johana Carvajal
  - Ing. David González
  - Ing. Yrene Corrales
  - Ing. José Ortiz
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

Vertice = int
Arista  = Tuple[float, int, int]   # (peso, u, v)


@dataclass
class Grafo:
    """
    Representación de un grafo no dirigido y ponderado con lista de adyacencia.

    En el problema de red eléctrica:
    - Vértices : subestaciones / centros de transformación
    - Aristas  : cables conductores con costo de tendido (en miles de USD)
    """
    n_vertices: int
    adj: Dict[Vertice, List[Tuple[Vertice, float]]] = field(default_factory=dict)

    def __post_init__(self):
        for v in range(self.n_vertices):
            self.adj.setdefault(v, [])

    def agregar_arista(self, u: Vertice, v: Vertice, peso: float) -> None:
        """
        Agrega (o actualiza) una arista no dirigida (u, v) con el peso dado.
        Si ya existe la arista (u,v), conserva el menor peso para garantizar
        la equivalencia Prim ↔ Kruskal ante entradas con multiaristas.

        Pre-condición : peso >= 0
        Post-condición: Adj[u] contiene (v, peso_min) y Adj[v] contiene (u, peso_min)
        """
        if peso < 0:
            raise ValueError(f"Peso negativo no permitido: ({u},{v}) = {peso}")
        for i, (nb, w) in enumerate(self.adj[u]):
            if nb == v:
                if peso < w:
                    self.adj[u][i] = (v, peso)
                    for j, (nb2, _) in enumerate(self.adj[v]):
                        if nb2 == u:
                            self.adj[v][j] = (u, peso)
                            break
                return
        self.adj[u].append((v, peso))
        self.adj[v].append((u, peso))

    def aristas(self) -> List[Arista]:
        """Devuelve todas las aristas sin duplicados como (peso, u, v)."""
        vistas: set = set()
        resultado: List[Arista] = []
        for u in range(self.n_vertices):
            for v, w in self.adj[u]:
                llave = (min(u, v), max(u, v))
                if llave not in vistas:
                    vistas.add(llave)
                    resultado.append((w, u, v))
        return resultado

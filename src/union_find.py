"""
Módulo: union_find.py
Estructura Union-Find con compresión de caminos y unión por rango.
Usada en el algoritmo de Kruskal para detección de ciclos en O(α(n)).

Equipo 5 – Análisis y Diseño de Algoritmos – UNEG
Integrantes:
  - Ing. Bryan Salazar
  - Ing. Johana Carvajal
  - Ing. David González
  - Ing. Yrene Corrales
  - Ing. José Ortiz
"""

from typing import List


class UnionFind:
    """
    Estructura Union-Find (Conjuntos Disjuntos) con:
    - Compresión de caminos en ENCONTRAR   → O(α(n)) amortizado
    - Unión por rango en UNIR              → O(α(n)) amortizado

    donde α es la función inversa de Ackermann (prácticamente constante ≤ 4
    para cualquier n razonable).

    En el contexto de Kruskal para redes eléctricas:
    - Cada componente representa un sub-árbol de subestaciones conectadas.
    - UNIR(u, v) conecta dos sub-redes distintas al tender un nuevo cable.
    - ENCONTRAR(v) identifica a qué sub-red pertenece la subestación v.
    """

    def __init__(self, n: int):
        """
        Inicializa n conjuntos disjuntos (uno por vértice).

        Pre-condición : n >= 1
        Post-condición: padre[i] = i, rango[i] = 0 para todo i ∈ [0, n)
        """
        if n < 1:
            raise ValueError(f"n debe ser >= 1, recibido: {n}")
        self.padre: List[int] = list(range(n))
        self.rango:  List[int] = [0] * n
        self._n_componentes: int = n

    # ------------------------------------------------------------------
    def encontrar(self, x: int) -> int:
        """
        Halla la raíz del conjunto que contiene x, con compresión de caminos.

        Invariante: padre[x] = raiz(x) después de la llamada (aplanamiento).
        """
        if self.padre[x] != x:
            self.padre[x] = self.encontrar(self.padre[x])
        return self.padre[x]

    # ------------------------------------------------------------------
    def unir(self, x: int, y: int) -> bool:
        """
        Une los conjuntos de x e y usando unión por rango.

        Devuelve:
            True  — si x e y estaban en conjuntos distintos (se unieron).
            False — si x e y ya pertenecían al mismo conjunto (ciclo detectado).

        Post-condición: si True, n_componentes disminuye en 1.
        """
        rx, ry = self.encontrar(x), self.encontrar(y)
        if rx == ry:
            return False   # mismo componente → ciclo detectado → no agregar arista

        # Unión por rango: árbol de menor rango cuelga del de mayor rango
        if self.rango[rx] < self.rango[ry]:
            rx, ry = ry, rx
        self.padre[ry] = rx
        if self.rango[rx] == self.rango[ry]:
            self.rango[rx] += 1

        self._n_componentes -= 1
        return True

    # ------------------------------------------------------------------
    @property
    def n_componentes(self) -> int:
        """Número actual de componentes conexos."""
        return self._n_componentes

    def misma_componente(self, x: int, y: int) -> bool:
        """Devuelve True si x e y pertenecen al mismo componente."""
        return self.encontrar(x) == self.encontrar(y)

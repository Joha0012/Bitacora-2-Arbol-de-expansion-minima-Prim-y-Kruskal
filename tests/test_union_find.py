"""
Pruebas unitarias de la estructura Union-Find (soporte de Kruskal).

Equipo 5 – Análisis y Diseño de Algoritmos – UNEG
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from union_find import UnionFind


def test_inicializacion_componentes_disjuntos():
    uf = UnionFind(5)
    assert uf.n_componentes == 5
    for i in range(5):
        assert uf.encontrar(i) == i


def test_unir_reduce_componentes():
    uf = UnionFind(4)
    assert uf.unir(0, 1) is True
    assert uf.unir(2, 3) is True
    assert uf.n_componentes == 2
    assert uf.misma_componente(0, 1)
    assert not uf.misma_componente(1, 2)


def test_unir_detecta_ciclo():
    """Unir dos vértices ya conectados devuelve False (ciclo en Kruskal)."""
    uf = UnionFind(3)
    uf.unir(0, 1)
    uf.unir(1, 2)
    assert uf.unir(0, 2) is False
    assert uf.n_componentes == 1


def test_compresion_de_caminos():
    """Tras encontrar(), el nodo apunta directamente a la raíz."""
    uf = UnionFind(6)
    for i in range(5):
        uf.unir(i, i + 1)
    raiz = uf.encontrar(5)
    assert uf.padre[5] == raiz


def test_n_invalido_lanza_excepcion():
    with pytest.raises(ValueError):
        UnionFind(0)

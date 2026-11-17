"""
Pruebas para los algoritmos MST – Prim y Kruskal
Incluye:
  - 5 pruebas unitarias con casos límite
  - 2 pruebas basadas en propiedades con Hypothesis
  - 1 prueba diferencial contra NetworkX (semilla fija y reproducible)
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mst_algorithms import Grafo, prim, kruskal, construir_red_electrica_ejemplo

# ============================================================
# HELPERS
# ============================================================

def _grafo_simple_triangulo() -> Grafo:
    """Triángulo: 0-1 (1), 1-2 (2), 0-2 (4)  → MST peso=3."""
    g = Grafo(3)
    g.agregar_arista(0, 1, 1)
    g.agregar_arista(1, 2, 2)
    g.agregar_arista(0, 2, 4)
    return g


def _grafo_lineal(n: int, peso: float = 1.0) -> Grafo:
    """Grafo lineal 0─1─2─…─(n-1), cada arista con peso dado."""
    g = Grafo(n)
    for i in range(n - 1):
        g.agregar_arista(i, i + 1, peso)
    return g


# ============================================================
# PRUEBA 1: Grafo trivial (un único vértice)
# ============================================================
def test_grafo_un_vertice():
    """Un vértice produce MST con 0 aristas y peso 0."""
    g = Grafo(1)
    res_p = prim(g, origen=0)
    res_k = kruskal(g)
    assert res_p.aristas_mst == []
    assert res_p.peso_total == 0.0
    assert res_k.aristas_mst == []
    assert res_k.peso_total == 0.0


# ============================================================
# PRUEBA 2: Grafo de dos vértices
# ============================================================
def test_grafo_dos_vertices():
    """Dos vértices con una arista de peso 7."""
    g = Grafo(2)
    g.agregar_arista(0, 1, 7)
    res_p = prim(g, origen=0)
    res_k = kruskal(g)
    assert len(res_p.aristas_mst) == 1
    assert res_p.peso_total == pytest.approx(7.0)
    assert len(res_k.aristas_mst) == 1
    assert res_k.peso_total == pytest.approx(7.0)


# ============================================================
# PRUEBA 3: Triangulo – selección correcta de arista mínima
# ============================================================
def test_triangulo_peso_correcto():
    """
    Triángulo 0-1-2.
    Aristas: (0,1)=1, (1,2)=2, (0,2)=4.
    MST esperado: peso 3 (aristas de peso 1 y 2).
    """
    g = _grafo_simple_triangulo()
    for algo, res in [("Prim", prim(g)), ("Kruskal", kruskal(g))]:
        assert res.peso_total == pytest.approx(3.0), \
            f"{algo}: peso_total esperado 3.0, obtenido {res.peso_total}"
        assert len(res.aristas_mst) == 2, \
            f"{algo}: número de aristas MST esperado 2"


# ============================================================
# PRUEBA 4: Grafo lineal de 5 vértices
# ============================================================
def test_grafo_lineal_5():
    """Un grafo lineal sólo tiene un árbol de expansión (él mismo)."""
    n = 5
    g = _grafo_lineal(n, peso=3.0)
    for algo, res in [("Prim", prim(g)), ("Kruskal", kruskal(g))]:
        assert len(res.aristas_mst) == n - 1, f"{algo}: aristas MST"
        assert res.peso_total == pytest.approx((n - 1) * 3.0), \
            f"{algo}: peso total"


# ============================================================
# PRUEBA 5: Caso límite – aristas con mismo peso
# ============================================================
def test_aristas_peso_igual():
    """
    Grafo completo K4 con todas las aristas de peso 1.
    MST debe tener 3 aristas con peso total 3.
    """
    g = Grafo(4)
    for u in range(4):
        for v in range(u + 1, 4):
            g.agregar_arista(u, v, 1)
    for algo, res in [("Prim", prim(g)), ("Kruskal", kruskal(g))]:
        assert len(res.aristas_mst) == 3, f"{algo}: 3 aristas en K4"
        assert res.peso_total == pytest.approx(3.0), f"{algo}: peso=3"


# ============================================================
# PRUEBA 6: Pesos negativos deben lanzar excepción
# ============================================================
def test_peso_negativo_lanza_excepcion():
    g = Grafo(3)
    with pytest.raises(ValueError, match="Peso negativo"):
        g.agregar_arista(0, 1, -5)


# ============================================================
# PRUEBA 7 (Hypothesis): Prim y Kruskal siempre coinciden en peso
# ============================================================
from hypothesis import given, settings
from hypothesis import strategies as st

@given(
    n=st.integers(min_value=2, max_value=20),
    aristas=st.lists(
        st.tuples(
            st.integers(min_value=0, max_value=19),
            st.integers(min_value=0, max_value=19),
            st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False),
        ),
        min_size=1,
        max_size=60,
    ),
)
@settings(max_examples=200, deadline=None)
def test_prim_kruskal_mismo_peso(n, aristas):
    """
    Propiedad: dado cualquier grafo conexo, el peso del MST de Prim
    es igual al de Kruskal (ambos son correctos por el teorema de corte).
    """
    g = Grafo(n)
    for u, v, w in aristas:
        u_v, v_v = u % n, v % n
        if u_v != v_v:
            g.agregar_arista(u_v, v_v, w)

    # Forzar conectividad: cadena lineal con peso 1
    for i in range(n - 1):
        g.agregar_arista(i, i + 1, 1.0)

    res_p = prim(g, origen=0)
    res_k = kruskal(g)
    assert res_p.peso_total == pytest.approx(res_k.peso_total, rel=1e-6), \
        f"Prim={res_p.peso_total} ≠ Kruskal={res_k.peso_total}"


# ============================================================
# PRUEBA 8 (Hypothesis): MST tiene exactamente n-1 aristas
# ============================================================
@given(n=st.integers(min_value=2, max_value=30))
@settings(max_examples=100, deadline=None)
def test_mst_tiene_n_menos_1_aristas(n):
    """
    Propiedad estructural: un MST sobre grafo conexo de n vértices
    tiene exactamente n-1 aristas.
    """
    g = _grafo_lineal(n, peso=1.0)
    # Añadir algunas aristas extra aleatorias
    for i in range(0, n - 1, 2):
        g.agregar_arista(i, min(i + 2, n - 1), 2.0)

    for algo, res in [("Prim", prim(g)), ("Kruskal", kruskal(g))]:
        assert len(res.aristas_mst) == n - 1, \
            f"{algo}: n={n}, aristas MST={len(res.aristas_mst)}"


# ============================================================
# PRUEBA 9 (Diferencial – NetworkX): semilla fija y reproducible
# ============================================================
import random
import networkx as nx

SEMILLA = 42

def test_diferencial_networkx():
    """
    Prueba diferencial: el peso total del MST producido por Prim y Kruskal
    debe coincidir con el de networkx.minimum_spanning_tree con semilla fija.

    Semilla: 42  |  n=12 vértices  |  grafo aleatorio reproducible
    """
    rng = random.Random(SEMILLA)
    n = 12
    g_propio = Grafo(n)
    g_nx = nx.Graph()
    g_nx.add_nodes_from(range(n))

    # Forzar conectividad
    for i in range(n - 1):
        w = round(rng.uniform(1.0, 20.0), 2)
        g_propio.agregar_arista(i, i + 1, w)
        g_nx.add_edge(i, i + 1, weight=w)

    # Aristas aleatorias adicionales (sin duplicar pares ya usados)
    pares_usados = set((i, i + 1) for i in range(n - 1))
    for _ in range(20):
        u = rng.randint(0, n - 1)
        v = rng.randint(0, n - 1)
        par = (min(u, v), max(u, v))
        if u != v and par not in pares_usados:
            pares_usados.add(par)
            w = round(rng.uniform(1.0, 20.0), 2)
            g_propio.agregar_arista(u, v, w)
            g_nx.add_edge(u, v, weight=w)

    res_prim    = prim(g_propio, origen=0)
    res_kruskal = kruskal(g_propio)

    mst_nx      = nx.minimum_spanning_tree(g_nx, algorithm='kruskal')
    peso_nx     = sum(d['weight'] for _, _, d in mst_nx.edges(data=True))

    assert res_prim.peso_total    == pytest.approx(peso_nx, rel=1e-6), \
        f"Prim {res_prim.peso_total} ≠ NetworkX {peso_nx}"
    assert res_kruskal.peso_total == pytest.approx(peso_nx, rel=1e-6), \
        f"Kruskal {res_kruskal.peso_total} ≠ NetworkX {peso_nx}"


# ============================================================
# PRUEBA 10: Red eléctrica de ejemplo
# ============================================================
def test_red_electrica_ejemplo():
    """
    El MST de la red eléctrica de ejemplo debe tener n-1=7 aristas
    y Prim y Kruskal deben concordar en el mismo peso total.
    """
    g, _ = construir_red_electrica_ejemplo()
    res_p = prim(g)
    res_k = kruskal(g)
    # Ambos algoritmos deben producir el mismo peso
    assert res_p.peso_total == pytest.approx(res_k.peso_total, rel=1e-9), \
        f"Prim={res_p.peso_total} ≠ Kruskal={res_k.peso_total}"
    assert len(res_p.aristas_mst) == 7   # n-1 = 8-1 = 7
    assert len(res_k.aristas_mst) == 7
    # El MST óptimo para esta red es 23 k$ (verificado manualmente y con NetworkX)
    assert res_p.peso_total == pytest.approx(23.0)

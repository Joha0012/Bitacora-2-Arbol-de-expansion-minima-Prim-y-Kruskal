"""
Pruebas del módulo planificador (lógica de la interfaz gráfica).

Equipo 5 – Análisis y Diseño de Algoritmos – UNEG
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from kruskal import kruskal
from mst_algorithms import construir_red_electrica_ejemplo
from planificador import (cargar_red_csv, componentes, copiar_grafo, ejecutar,
                          exportar_mst_csv, generar_red_aleatoria, guardar_red_csv,
                          traza_kruskal, traza_prim)
from grafo import Grafo

RUTA_MUNICIPAL = os.path.join(os.path.dirname(__file__), '..', 'data', 'red_municipal.csv')


def test_traza_kruskal_coincide_con_kruskal():
    g, _ = construir_red_electrica_ejemplo()
    pasos = traza_kruskal(g)
    aceptadas = [p for p in pasos if p[3]]
    assert len(aceptadas) == g.n_vertices - 1
    assert sum(p[2] for p in aceptadas) == pytest.approx(kruskal(g).peso_total)
    # Los pesos evaluados están en orden no decreciente
    pesos = [p[2] for p in pasos]
    assert pesos == sorted(pesos)


def test_traza_prim_parte_del_origen():
    g, _ = construir_red_electrica_ejemplo()
    pasos = traza_prim(g, origen=3)
    assert pasos[0][0] == 3
    assert all(p[3] for p in pasos)


def test_red_municipal_prim_igual_kruskal():
    g, nombres = cargar_red_csv(RUTA_MUNICIPAL)
    assert len(nombres) == 12
    assert len(componentes(g)) == 1
    p = ejecutar(g, "Prim", 0)
    k = ejecutar(g, "Kruskal")
    assert p.resultado.peso_total == pytest.approx(k.resultado.peso_total)
    assert len(k.resultado.aristas_mst) == 11


def test_csv_ida_y_vuelta(tmp_path):
    g, nombres = construir_red_electrica_ejemplo()
    ruta = tmp_path / "red.csv"
    guardar_red_csv(str(ruta), g, nombres)
    g2, nombres2 = cargar_red_csv(str(ruta))
    assert sorted(nombres2) == sorted(nombres)
    assert kruskal(g2).peso_total == pytest.approx(kruskal(g).peso_total)


def test_csv_punto_y_coma_y_coma_decimal(tmp_path):
    ruta = tmp_path / "red.csv"
    ruta.write_text("Origen;Destino;Costo\nA;B;2,5\nB;C;1,5\nA;C;9\n", encoding="utf-8")
    g, nombres = cargar_red_csv(str(ruta))
    assert nombres == ["A", "B", "C"]
    assert kruskal(g).peso_total == pytest.approx(4.0)


@pytest.mark.parametrize("contenido", [
    "origen,destino,costo\nA,A,3\n",          # lazo
    "origen,destino,costo\nA,B,-1\n",         # costo negativo
    "origen,destino,costo\nA,B,abc\n",        # costo no numérico
    "desde,precio\nA,3\n",                    # columnas faltantes
    "",                                       # vacío
])
def test_csv_invalido_lanza_error(tmp_path, contenido):
    ruta = tmp_path / "malo.csv"
    ruta.write_text(contenido, encoding="utf-8")
    with pytest.raises(ValueError):
        cargar_red_csv(str(ruta))


def test_red_aleatoria_conexa_y_reproducible():
    g1, _ = generar_red_aleatoria(40, semilla=7)
    g2, _ = generar_red_aleatoria(40, semilla=7)
    assert len(componentes(g1)) == 1
    assert sorted(g1.aristas()) == sorted(g2.aristas())


def test_copiar_grafo_excluye_y_amplia():
    g, _ = construir_red_electrica_ejemplo()
    c = copiar_grafo(g, n_nuevo=9, excluir=(0, 1))
    assert c.n_vertices == 9
    assert len(c.aristas()) == len(g.aristas()) - 1
    assert len(componentes(c)) == 2   # el vértice nuevo queda aislado


def test_componentes_red_desconectada():
    g = Grafo(4)
    g.agregar_arista(0, 1, 1)
    g.agregar_arista(2, 3, 1)
    assert len(componentes(g)) == 2
    assert len(ejecutar(g, "Kruskal").resultado.aristas_mst) == 2   # bosque


def test_exportar_plan(tmp_path):
    g, nombres = construir_red_electrica_ejemplo()
    ruta = tmp_path / "plan.csv"
    exportar_mst_csv(str(ruta), [ejecutar(g, "Prim"), ejecutar(g, "Kruskal")], nombres)
    lineas = ruta.read_text(encoding="utf-8").strip().splitlines()
    assert lineas[0].startswith("algoritmo")
    assert lineas.count("Prim,TOTAL,,,23") == 1
    assert lineas.count("Kruskal,TOTAL,,,23") == 1

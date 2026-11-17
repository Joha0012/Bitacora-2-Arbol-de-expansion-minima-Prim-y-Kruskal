"""
Módulo: planificador.py
Lógica de aplicación (sin interfaz gráfica) del Planificador de Red Eléctrica.

Provee:
  - Ejecución instrumentada de Prim y Kruskal (tiempo + traza paso a paso).
  - Carga / guardado de redes en CSV (origen, destino, costo).
  - Generación de redes aleatorias reproducibles (semilla).
  - Medición de rendimiento para la pestaña de comparación.

Equipo 5 – Análisis y Diseño de Algoritmos – UNEG
Integrantes:
  - Ing. Bryan Salazar
  - Ing. Johana Carvajal
  - Ing. David González
  - Ing. Yrene Corrales
  - Ing. José Ortiz
"""

from __future__ import annotations

import csv
import random
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from grafo import Grafo
from kruskal import kruskal
from prim import ResultadoMST, prim
from union_find import UnionFind

# (u, v, peso, aceptada)
Paso = Tuple[int, int, float, bool]

ALGORITMOS = ("Prim", "Kruskal")


@dataclass
class EjecucionMST:
    """Resultado de ejecutar un algoritmo MST sobre una red."""
    algoritmo: str
    resultado: ResultadoMST
    pasos: List[Paso]
    tiempo_ms: float
    origen: Optional[int] = None


# ---------------------------------------------------------------------------
# Trazas paso a paso (para la animación)
# ---------------------------------------------------------------------------

def traza_kruskal(grafo: Grafo) -> List[Paso]:
    """
    Reproduce Kruskal registrando cada arista evaluada en orden creciente
    de peso y si fue aceptada (une dos sub-redes) o rechazada (formaría ciclo).
    """
    n = grafo.n_vertices
    pasos: List[Paso] = []
    if n == 0:
        return pasos
    uf = UnionFind(n)
    aceptadas = 0
    for w, u, v in sorted(grafo.aristas()):
        ok = uf.unir(u, v)
        pasos.append((u, v, w, ok))
        if ok:
            aceptadas += 1
            if aceptadas == n - 1:
                break
    return pasos


def traza_prim(grafo: Grafo, origen: int = 0) -> List[Paso]:
    """Aristas en el orden en que Prim incorpora cada vértice al árbol."""
    res = prim(grafo, origen)
    return [(u, v, w, True) for u, v, w in res.aristas_mst]


def ejecutar(grafo: Grafo, algoritmo: str, origen: int = 0) -> EjecucionMST:
    """Ejecuta Prim o Kruskal midiendo el tiempo y generando la traza."""
    if algoritmo not in ALGORITMOS:
        raise ValueError(f"Algoritmo desconocido: {algoritmo}")
    t0 = time.perf_counter()
    if algoritmo == "Prim":
        res = prim(grafo, origen)
    else:
        res = kruskal(grafo)
    t_ms = (time.perf_counter() - t0) * 1000.0
    pasos = traza_prim(grafo, origen) if algoritmo == "Prim" else traza_kruskal(grafo)
    return EjecucionMST(algoritmo, res, pasos, t_ms,
                        origen if algoritmo == "Prim" else None)


# ---------------------------------------------------------------------------
# Utilidades de red
# ---------------------------------------------------------------------------

def costo_total_rutas(grafo: Grafo) -> float:
    """Costo de tender TODAS las rutas candidatas (referencia de ahorro)."""
    return sum(w for w, _, _ in grafo.aristas())


def componentes(grafo: Grafo) -> List[List[int]]:
    """Componentes conexos de la red (subestaciones mutuamente alcanzables)."""
    n = grafo.n_vertices
    if n == 0:
        return []
    uf = UnionFind(n)
    for _, u, v in grafo.aristas():
        uf.unir(u, v)
    grupos: Dict[int, List[int]] = {}
    for v in range(n):
        grupos.setdefault(uf.encontrar(v), []).append(v)
    return list(grupos.values())


def copiar_grafo(grafo: Grafo, n_nuevo: Optional[int] = None,
                 excluir: Optional[Tuple[int, int]] = None) -> Grafo:
    """Copia la red, opcionalmente con más vértices o sin la arista 'excluir'."""
    n = grafo.n_vertices if n_nuevo is None else n_nuevo
    if n < grafo.n_vertices:
        raise ValueError("n_nuevo no puede ser menor que el número actual de vértices")
    llave_ex = None if excluir is None else (min(excluir), max(excluir))
    nuevo = Grafo(n)
    for w, u, v in grafo.aristas():
        if llave_ex is not None and (min(u, v), max(u, v)) == llave_ex:
            continue
        nuevo.agregar_arista(u, v, w)
    return nuevo


def existe_ruta(grafo: Grafo, u: int, v: int) -> bool:
    return any(nb == v for nb, _ in grafo.adj[u])


def generar_red_aleatoria(n: int, semilla: int = 42,
                          densidad: int = 3) -> Tuple[Grafo, List[str]]:
    """
    Red aleatoria conexa y reproducible con ≈ densidad·n rutas candidatas.
    Costos uniformes en [1, 100] miles de USD (mismo generador que piloto.py).
    """
    if n < 2:
        raise ValueError("La red debe tener al menos 2 subestaciones")
    rng = random.Random(semilla)
    g = Grafo(n)
    vertices = list(range(n))
    rng.shuffle(vertices)
    for i in range(1, n):
        u = vertices[i]
        v = vertices[rng.randint(0, i - 1)]
        g.agregar_arista(u, v, round(rng.uniform(1, 100), 2))
    for _ in range(n * max(densidad - 1, 0)):
        u = rng.randint(0, n - 1)
        v = rng.randint(0, n - 1)
        if u != v:
            g.agregar_arista(u, v, round(rng.uniform(1, 100), 2))
    nombres = [f"SE {i + 1}" for i in range(n)]
    return g, nombres


# ---------------------------------------------------------------------------
# Entrada / salida CSV
# ---------------------------------------------------------------------------

_ALIAS = {
    "origen": "origen", "desde": "origen", "u": "origen",
    "destino": "destino", "hasta": "destino", "v": "destino",
    "costo": "costo", "peso": "costo", "w": "costo",
}


def cargar_red_csv(ruta: str) -> Tuple[Grafo, List[str]]:
    """
    Lee una red desde CSV con columnas: origen, destino, costo.
    Acepta separador ',' o ';' y coma decimal en el costo (p. ej. 3,5).
    """
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        contenido = f.read()
    if not contenido.strip():
        raise ValueError("El archivo está vacío")
    primera = contenido.splitlines()[0]
    delim = ";" if primera.count(";") > primera.count(",") else ","
    lector = csv.DictReader(contenido.splitlines(), delimiter=delim)
    if lector.fieldnames is None:
        raise ValueError("No se encontró la fila de encabezado")
    mapa = {}
    for campo in lector.fieldnames:
        clave = _ALIAS.get(campo.strip().lower())
        if clave:
            mapa[clave] = campo
    faltan = {"origen", "destino", "costo"} - set(mapa)
    if faltan:
        raise ValueError(f"Faltan columnas: {', '.join(sorted(faltan))} "
                         "(se esperan: origen, destino, costo)")

    nombres: List[str] = []
    indice: Dict[str, int] = {}
    filas: List[Tuple[int, int, float]] = []
    for num, fila in enumerate(lector, start=2):
        o = (fila[mapa["origen"]] or "").strip()
        d = (fila[mapa["destino"]] or "").strip()
        c_txt = (fila[mapa["costo"]] or "").strip().replace(",", ".")
        if not o and not d and not c_txt:
            continue
        if not o or not d:
            raise ValueError(f"Fila {num}: origen y destino son obligatorios")
        if o == d:
            raise ValueError(f"Fila {num}: una ruta no puede ir de '{o}' a sí misma")
        try:
            costo = float(c_txt)
        except ValueError:
            raise ValueError(f"Fila {num}: costo inválido '{c_txt}'") from None
        if costo < 0:
            raise ValueError(f"Fila {num}: el costo no puede ser negativo")
        for nombre in (o, d):
            if nombre not in indice:
                indice[nombre] = len(nombres)
                nombres.append(nombre)
        filas.append((indice[o], indice[d], costo))

    if not filas:
        raise ValueError("El archivo no contiene rutas")
    g = Grafo(len(nombres))
    for u, v, c in filas:
        g.agregar_arista(u, v, c)
    return g, nombres


def guardar_red_csv(ruta: str, grafo: Grafo, nombres: Sequence[str]) -> None:
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["origen", "destino", "costo"])
        for peso, u, v in sorted(grafo.aristas(), key=lambda a: (a[1], a[2])):
            w.writerow([nombres[u], nombres[v], f"{peso:g}"])


def exportar_mst_csv(ruta: str, ejecuciones: Sequence[EjecucionMST],
                     nombres: Sequence[str]) -> None:
    """Exporta el plan de tendido (aristas del MST) de cada algoritmo."""
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["algoritmo", "orden", "desde", "hasta", "costo_miles_usd"])
        for e in ejecuciones:
            for i, (u, v, peso) in enumerate(e.resultado.aristas_mst, start=1):
                w.writerow([e.algoritmo, i, nombres[u], nombres[v], f"{peso:g}"])
            w.writerow([e.algoritmo, "TOTAL", "", "", f"{e.resultado.peso_total:g}"])


# ---------------------------------------------------------------------------
# Medición de rendimiento
# ---------------------------------------------------------------------------

def medir_rendimiento(tamanios: Sequence[int], repeticiones: int = 3,
                      semilla: int = 42, densidad: int = 3,
                      progreso: Optional[Callable[[int, int], None]] = None
                      ) -> List[Dict[str, object]]:
    """
    Mide Prim y Kruskal sobre redes aleatorias de cada tamaño.
    Devuelve [{'n', 'prim_ms': [...], 'kruskal_ms': [...]}, ...].
    """
    total = len(tamanios) * repeticiones
    hechos = 0
    salida: List[Dict[str, object]] = []
    for n in tamanios:
        tp: List[float] = []
        tk: List[float] = []
        for rep in range(1, repeticiones + 1):
            g, _ = generar_red_aleatoria(n, semilla + rep, densidad)
            t0 = time.perf_counter()
            prim(g, 0)
            tp.append((time.perf_counter() - t0) * 1000.0)
            t0 = time.perf_counter()
            kruskal(g)
            tk.append((time.perf_counter() - t0) * 1000.0)
            hechos += 1
            if progreso:
                progreso(hechos, total)
        salida.append({"n": n, "prim_ms": tp, "kruskal_ms": tk})
    return salida

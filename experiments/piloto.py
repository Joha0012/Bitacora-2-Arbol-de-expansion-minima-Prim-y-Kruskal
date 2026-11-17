"""
Experimento piloto de medición de rendimiento
Mínimo 3 tamaños de entrada, 3 repeticiones cada uno.
Genera gráfica de rendimiento y datos CSV.
"""

import sys
import os
import time
import random
import csv

import matplotlib
matplotlib.use('Agg')  # Backend sin GUI para entornos sin pantalla
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from mst_algorithms import Grafo, prim, kruskal

# ─────────────────────────────────────────
# Configuración del experimento
# ─────────────────────────────────────────
SEMILLA          = 42
TAMANIOS         = [50, 100, 250, 500, 1_000, 2_000, 5_000]
REPETICIONES     = 5
DENSIDAD_FACTOR  = 3   # aristas ≈ n * factor (grafo disperso tipo red eléctrica)
DIRECTORIO_SALIDA = os.path.dirname(os.path.abspath(__file__))


def generar_grafo_aleatorio(n: int, semilla: int) -> Grafo:
    """
    Genera un grafo aleatorio conexo con ~n*DENSIDAD_FACTOR aristas.
    Simulación de una red eléctrica con n subestaciones.
    """
    rng = random.Random(semilla)
    g = Grafo(n)
    # Garantizar conectividad con árbol generador aleatorio
    vertices = list(range(n))
    rng.shuffle(vertices)
    for i in range(1, n):
        u = vertices[i]
        v = vertices[rng.randint(0, i - 1)]
        w = round(rng.uniform(1, 100), 2)
        g.agregar_arista(u, v, w)
    # Aristas adicionales para densidad
    extras = n * (DENSIDAD_FACTOR - 1)
    for _ in range(extras):
        u = rng.randint(0, n - 1)
        v = rng.randint(0, n - 1)
        if u != v:
            w = round(rng.uniform(1, 100), 2)
            g.agregar_arista(u, v, w)
    return g


def medir_tiempo(fn, *args) -> float:
    """Mide tiempo de ejecución de fn(*args) en segundos."""
    inicio = time.perf_counter()
    fn(*args)
    return time.perf_counter() - inicio


def ejecutar_experimento():
    print("\n" + "=" * 60)
    print("  EXPERIMENTO PILOTO – MST Prim vs Kruskal")
    print(f"  Semilla: {SEMILLA} | Densidad: ~{DENSIDAD_FACTOR}n aristas")
    print("=" * 60)

    resultados = []  # (n, rep, prim_s, kruskal_s)

    for n in TAMANIOS:
        tiempos_prim    = []
        tiempos_kruskal = []

        for rep in range(1, REPETICIONES + 1):
            g = generar_grafo_aleatorio(n, SEMILLA + rep)

            t_p = medir_tiempo(prim,    g, 0)
            t_k = medir_tiempo(kruskal, g)

            tiempos_prim.append(t_p)
            tiempos_kruskal.append(t_k)
            resultados.append((n, rep, t_p, t_k))
            print(f"  n={n:5d}  rep={rep}  Prim={t_p*1000:.3f}ms  Kruskal={t_k*1000:.3f}ms")

        media_p = sum(tiempos_prim)    / REPETICIONES
        media_k = sum(tiempos_kruskal) / REPETICIONES
        print(f"  → Medias   n={n:5d}  Prim={media_p*1000:.3f}ms  Kruskal={media_k*1000:.3f}ms")
        print()

    return resultados


def guardar_csv(resultados):
    path_csv = os.path.join(DIRECTORIO_SALIDA, 'datos_piloto.csv')
    with open(path_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['n_vertices', 'repeticion', 'prim_seg', 'kruskal_seg'])
        w.writerows(resultados)
    print(f"Datos guardados en: {path_csv}")
    return path_csv


def graficar(resultados):
    from collections import defaultdict

    datos_prim    = defaultdict(list)
    datos_kruskal = defaultdict(list)
    for n, _, tp, tk in resultados:
        datos_prim[n].append(tp * 1000)
        datos_kruskal[n].append(tk * 1000)

    ns          = sorted(datos_prim.keys())
    medias_p    = [sum(datos_prim[n])    / len(datos_prim[n])    for n in ns]
    medias_k    = [sum(datos_kruskal[n]) / len(datos_kruskal[n]) for n in ns]
    std_p       = [(sum((x - m) ** 2 for x in datos_prim[n]) / len(datos_prim[n])) ** 0.5
                   for n, m in zip(ns, medias_p)]
    std_k       = [(sum((x - m) ** 2 for x in datos_kruskal[n]) / len(datos_kruskal[n])) ** 0.5
                   for n, m in zip(ns, medias_k)]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        'Medición Piloto: Prim vs Kruskal – Red de Distribución Eléctrica\n'
        f'(semilla={SEMILLA}, densidad≈{DENSIDAD_FACTOR}n aristas, {REPETICIONES} repeticiones)',
        fontsize=12, fontweight='bold'
    )

    # -- Gráfica izquierda: tiempo vs n
    ax = axes[0]
    ax.errorbar(ns, medias_p, yerr=std_p, marker='o', label='Prim',
                capsize=4, linewidth=1.8, color='steelblue')
    ax.errorbar(ns, medias_k, yerr=std_k, marker='s', label='Kruskal',
                capsize=4, linewidth=1.8, color='darkorange', linestyle='--')
    ax.set_xlabel('Número de vértices (n)', fontsize=11)
    ax.set_ylabel('Tiempo medio (ms)', fontsize=11)
    ax.set_title('Tiempo de ejecución vs Tamaño de entrada')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')
    ax.set_yscale('log')

    # -- Gráfica derecha: comparación barras en tamaños piloto pequeños
    ax2   = axes[1]
    idx   = [0, 2, 4]  # tamaños representativos
    ns_s  = [ns[i] for i in idx]
    mp_s  = [medias_p[i] for i in idx]
    mk_s  = [medias_k[i] for i in idx]
    x     = range(len(ns_s))
    ancho = 0.35
    ax2.bar([xi - ancho/2 for xi in x], mp_s, ancho, label='Prim',    color='steelblue')
    ax2.bar([xi + ancho/2 for xi in x], mk_s, ancho, label='Kruskal', color='darkorange')
    ax2.set_xticks(list(x))
    ax2.set_xticklabels([f'n={n}' for n in ns_s])
    ax2.set_ylabel('Tiempo medio (ms)', fontsize=11)
    ax2.set_title('Comparación directa en tamaños seleccionados')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    path_png = os.path.join(DIRECTORIO_SALIDA, 'grafica_piloto.png')
    plt.savefig(path_png, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Gráfica guardada en: {path_png}")
    return path_png


if __name__ == '__main__':
    resultados = ejecutar_experimento()
    guardar_csv(resultados)
    graficar(resultados)
    print("\n✓ Experimento piloto completado.")

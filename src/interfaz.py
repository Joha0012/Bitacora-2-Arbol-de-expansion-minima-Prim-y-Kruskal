"""
Interfaz gráfica – Planificador de Red de Distribución Eléctrica
Árbol de Expansión Mínima con los algoritmos de Prim y Kruskal.

Ejecutar:
    python src/interfaz.py

Pestañas:
  1. Diseño de la red  – cargar/editar la red, calcular el MST, animación
                         paso a paso y exportación del plan de tendido.
  2. Rendimiento       – medición comparativa Prim vs Kruskal.
  3. Ayuda             – instrucciones, formato CSV y ventajas/desventajas.

Equipo 5 – Análisis y Diseño de Algoritmos – UNEG
Integrantes:
  - Ing. Bryan Salazar
  - Ing. Johana Carvajal
  - Ing. David González
  - Ing. Yrene Corrales
  - Ing. José Ortiz
"""

from __future__ import annotations

import os
import random
import sys
import textwrap
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Dict, List, Optional, Sequence, Tuple

DIR_SRC = os.path.dirname(os.path.abspath(__file__))
DIR_RAIZ = os.path.dirname(DIR_SRC)
DIR_DATOS = os.path.join(DIR_RAIZ, "data")
sys.path.insert(0, DIR_SRC)

import matplotlib  # noqa: E402

matplotlib.use("TkAgg")
import networkx as nx  # noqa: E402
from matplotlib.backends.backend_tkagg import (  # noqa: E402
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.colors import to_rgb  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from grafo import Grafo  # noqa: E402
from mst_algorithms import construir_red_electrica_ejemplo  # noqa: E402
from planificador import (  # noqa: E402
    EjecucionMST, Paso, cargar_red_csv, componentes, copiar_grafo,
    costo_total_rutas, ejecutar, existe_ruta, exportar_mst_csv,
    generar_red_aleatoria, guardar_red_csv, medir_rendimiento)

COLORES = {"Prim": "#1f77b4", "Kruskal": "#e6550d"}
COLOR_RECHAZO = "#d62728"
COLOR_ACTUAL = "#f2b705"
COLOR_ORIGEN = "#2ca02c"
COLOR_CANDIDATA = "#bdbdbd"

# Posiciones "geográficas" de la red de ejemplo de 8 subestaciones
POS_EJEMPLO = {
    0: (0.0, 0.0), 1: (0.2, 2.0), 2: (-0.3, -2.0), 3: (2.2, 0.6),
    4: (-2.2, -0.2), 5: (2.0, 2.4), 6: (-1.6, -2.6), 7: (3.6, 1.6),
}


def _aclarar(color: str, factor: float = 0.45) -> Tuple[float, float, float]:
    r, g, b = to_rgb(color)
    return (1 - (1 - r) * factor, 1 - (1 - g) * factor, 1 - (1 - b) * factor)


def dibujar_red(ax, grafo: Grafo, nombres: Sequence[str], pos: Dict[int, tuple],
                mst: Sequence[tuple] = (), rechazadas: Sequence[tuple] = (),
                actual: Optional[Paso] = None, color: str = "#1f77b4",
                origen: Optional[int] = None, titulo: str = "") -> None:
    """Dibuja la red candidata y resalta el MST / la traza de la animación."""
    n = grafo.n_vertices
    ax.set_axis_off()
    if titulo:
        ax.set_title(titulo, fontsize=11, fontweight="bold")
    if n == 0:
        return
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for w, u, v in grafo.aristas():
        G.add_edge(u, v, weight=w)
    grande = n > 40

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=COLOR_CANDIDATA,
                           style="dashed", width=0.7 if grande else 1.2, alpha=0.9)
    if rechazadas:
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=[(u, v) for u, v, _ in rechazadas],
                               edge_color=COLOR_RECHAZO, style="dotted", width=2.2)
    if mst:
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=[(u, v) for u, v, _ in mst],
                               edge_color=color, width=2.0 if grande else 3.6)
    if actual is not None:
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=[(actual[0], actual[1])],
                               edge_color=COLOR_ACTUAL, width=6.5, alpha=0.85)

    en_arbol = {x for u, v, _ in mst for x in (u, v)}
    claro = _aclarar(color)
    colores = []
    for i in range(n):
        if i == origen:
            colores.append(COLOR_ORIGEN)
        elif i in en_arbol:
            colores.append(claro)
        else:
            colores.append("#f2f2f2")
    tam = 1150 if n <= 10 else 800 if n <= 20 else 380 if n <= 40 else 50
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colores, node_size=tam,
                           edgecolors="#424242", linewidths=1.0)
    if not grande:
        etiquetas = {i: textwrap.fill(nombres[i], 12) for i in range(n)}
        nx.draw_networkx_labels(G, pos, labels=etiquetas, ax=ax,
                                font_size=7 if n > 12 else 8)
    if n <= 30:
        pesos = {(u, v): f"{d['weight']:g}" for u, v, d in G.edges(data=True)}
        nx.draw_networkx_edge_labels(
            G, pos, edge_labels=pesos, ax=ax, font_size=7,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))

    leyenda = [Line2D([0], [0], color=COLOR_CANDIDATA, ls="--", label="Ruta candidata")]
    if mst or actual is not None:
        leyenda.append(Line2D([0], [0], color=color, lw=3.5, label="Cable en el plan (MST)"))
    if rechazadas:
        leyenda.append(Line2D([0], [0], color=COLOR_RECHAZO, ls=":", lw=2.2,
                              label="Rechazada (formaría ciclo)"))
    if actual is not None:
        leyenda.append(Line2D([0], [0], color=COLOR_ACTUAL, lw=6, label="Arista evaluada"))
    if origen is not None:
        leyenda.append(Line2D([0], [0], marker="o", color="w", markerfacecolor=COLOR_ORIGEN,
                              markeredgecolor="#424242", markersize=9, label="Origen (Prim)"))
    ax.legend(handles=leyenda, loc="lower left", fontsize=7, framealpha=0.92)
    ax.margins(0.08)


class AppMST(tk.Tk):
    """Ventana principal del Planificador de Red Eléctrica."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Planificador de Red Eléctrica – MST (Prim y Kruskal) · Equipo 5 UNEG")
        self.geometry("1380x840")
        self.minsize(1100, 700)
        self._configurar_estilos()

        self.grafo: Grafo = Grafo(0)
        self.nombres: List[str] = []
        self.pos: Dict[int, tuple] = {}
        self.ejecuciones: List[EjecucionMST] = []
        self.pasos: List[Paso] = []
        self.paso_idx = 0
        self.algoritmo_anim: Optional[str] = None
        self.origen_anim: Optional[int] = None
        self._job: Optional[str] = None

        self._construir_ui()
        self.cargar_ejemplo()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)

    # ------------------------------------------------------------------ UI
    def _configurar_estilos(self) -> None:
        estilo = ttk.Style(self)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 15, "bold"), foreground="#1b3a5c")
        estilo.configure("Sub.TLabel", font=("Segoe UI", 9), foreground="#555555")
        estilo.configure("Dato.TLabel", font=("Segoe UI", 10, "bold"), foreground="#1b3a5c")
        estilo.configure("Accion.TButton", font=("Segoe UI", 10, "bold"))
        estilo.configure("TLabelframe.Label", font=("Segoe UI", 9, "bold"), foreground="#1b3a5c")
        estilo.configure("Treeview", rowheight=22)

    def _construir_ui(self) -> None:
        cab = ttk.Frame(self, padding=(12, 8, 12, 4))
        cab.pack(fill="x")
        ttk.Label(cab, text="⚡ Planificador de Red de Distribución Eléctrica",
                  style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(cab, text="Árbol de Expansión Mínima con Prim y Kruskal · Equipo 5 – "
                            "Análisis y Diseño de Algoritmos (UNEG)",
                  style="Sub.TLabel").pack(anchor="w")

        self.estado = tk.StringVar(value="Listo.")
        ttk.Label(self, textvariable=self.estado, relief="sunken", anchor="w",
                  padding=(8, 3)).pack(fill="x", side="bottom")

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=8, pady=(0, 4))
        t1, t2, t3 = ttk.Frame(self.nb), ttk.Frame(self.nb), ttk.Frame(self.nb)
        self.nb.add(t1, text="  Diseño de la red  ")
        self.nb.add(t2, text="  Rendimiento Prim vs Kruskal  ")
        self.nb.add(t3, text="  Ayuda  ")
        self._construir_tab_diseno(t1)
        self._construir_tab_rendimiento(t2)
        self._construir_tab_ayuda(t3)

    def _construir_tab_diseno(self, tab: ttk.Frame) -> None:
        panel = ttk.Frame(tab, padding=(6, 8))
        panel.pack(side="left", fill="y")

        # 1. Red de entrada
        f1 = ttk.LabelFrame(panel, text="1. Red de entrada", padding=8)
        f1.pack(fill="x", pady=(0, 6))
        ttk.Button(f1, text="Red de ejemplo (8 subestaciones)",
                   command=self.cargar_ejemplo).pack(fill="x")
        ttk.Button(f1, text="Red municipal Ciudad Guayana (12 SE)",
                   command=self.cargar_municipal).pack(fill="x", pady=(4, 0))
        fila = ttk.Frame(f1)
        fila.pack(fill="x", pady=4)
        ttk.Button(fila, text="Abrir CSV…", command=self.abrir_csv).pack(
            side="left", expand=True, fill="x")
        ttk.Button(fila, text="Guardar CSV…", command=self.guardar_csv).pack(
            side="left", expand=True, fill="x", padx=(4, 0))
        g = ttk.Frame(f1)
        g.pack(fill="x", pady=(2, 0))
        ttk.Label(g, text="Subestaciones:").grid(row=0, column=0, sticky="w")
        self.var_n = tk.IntVar(value=15)
        ttk.Spinbox(g, from_=2, to=500, textvariable=self.var_n, width=6).grid(row=0, column=1)
        ttk.Label(g, text=" Semilla:").grid(row=0, column=2)
        self.var_semilla = tk.IntVar(value=42)
        ttk.Spinbox(g, from_=0, to=99999, textvariable=self.var_semilla, width=6).grid(
            row=0, column=3)
        ttk.Button(f1, text="Generar red aleatoria",
                   command=self.generar_aleatoria).pack(fill="x", pady=(4, 0))

        # 2. Editar rutas
        f2 = ttk.LabelFrame(panel, text="2. Editar rutas candidatas", padding=8)
        f2.pack(fill="x", pady=(0, 6))
        ttk.Label(f2, text="Desde:").grid(row=0, column=0, sticky="w")
        self.cb_desde = ttk.Combobox(f2, state="readonly", width=24)
        self.cb_desde.grid(row=0, column=1, columnspan=2, sticky="ew", pady=1)
        ttk.Label(f2, text="Hasta:").grid(row=1, column=0, sticky="w")
        self.cb_hasta = ttk.Combobox(f2, state="readonly", width=24)
        self.cb_hasta.grid(row=1, column=1, columnspan=2, sticky="ew", pady=1)
        ttk.Label(f2, text="Costo (k$):").grid(row=2, column=0, sticky="w")
        self.var_costo = tk.StringVar(value="5")
        ttk.Entry(f2, textvariable=self.var_costo, width=10).grid(row=2, column=1, sticky="w",
                                                                   pady=1)
        ttk.Button(f2, text="Agregar / actualizar", command=self.agregar_ruta).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        ttk.Button(f2, text="Eliminar", command=self.eliminar_ruta).grid(
            row=3, column=2, sticky="ew", pady=(4, 0), padx=(4, 0))
        ttk.Button(f2, text="Agregar subestación…", command=self.agregar_subestacion).grid(
            row=4, column=0, columnspan=3, sticky="ew", pady=(4, 0))
        f2.columnconfigure(1, weight=1)

        # 3. Algoritmo
        f3 = ttk.LabelFrame(panel, text="3. Algoritmo", padding=8)
        f3.pack(fill="x", pady=(0, 6))
        self.var_algo = tk.StringVar(value="Kruskal")
        fr = ttk.Frame(f3)
        fr.pack(fill="x")
        for texto, valor in (("Prim", "Prim"), ("Kruskal", "Kruskal"), ("Ambos", "Ambos")):
            ttk.Radiobutton(fr, text=texto, value=valor, variable=self.var_algo,
                            command=self._algoritmo_cambiado).pack(side="left", padx=(0, 8))
        fo = ttk.Frame(f3)
        fo.pack(fill="x", pady=(4, 0))
        ttk.Label(fo, text="Origen (Prim):").pack(side="left")
        self.cb_origen = ttk.Combobox(fo, state="readonly", width=20)
        self.cb_origen.pack(side="left", fill="x", expand=True, padx=(4, 0))
        ttk.Button(f3, text="Calcular MST", style="Accion.TButton",
                   command=self.calcular).pack(fill="x", pady=(8, 4))
        fb = ttk.Frame(f3)
        fb.pack(fill="x")
        self.btn_animar = ttk.Button(fb, text="▶ Animar", command=self.animar)
        self.btn_animar.pack(side="left", expand=True, fill="x")
        ttk.Button(fb, text="Paso ⏭", command=self.siguiente_paso).pack(
            side="left", expand=True, fill="x", padx=4)
        ttk.Button(fb, text="↺ Reiniciar", command=self.reiniciar).pack(
            side="left", expand=True, fill="x")
        fv = ttk.Frame(f3)
        fv.pack(fill="x", pady=(4, 0))
        ttk.Label(fv, text="Velocidad:").pack(side="left")
        self.var_vel = tk.DoubleVar(value=700)
        ttk.Scale(fv, from_=1500, to=100, variable=self.var_vel).pack(
            side="left", fill="x", expand=True, padx=(4, 0))

        # 4. Resultados
        f4 = ttk.LabelFrame(panel, text="4. Resultados del plan", padding=8)
        f4.pack(fill="x")
        self.var_res: Dict[str, tk.StringVar] = {}
        filas = (("costo", "Costo del MST:"), ("total", "Todas las rutas:"),
                 ("ahorro", "Ahorro:"), ("aristas", "Cables a tender:"),
                 ("tiempo", "Tiempo de cómputo:"), ("conexa", "Conectividad:"))
        for i, (clave, texto) in enumerate(filas):
            ttk.Label(f4, text=texto).grid(row=i, column=0, sticky="w")
            self.var_res[clave] = tk.StringVar(value="—")
            ttk.Label(f4, textvariable=self.var_res[clave], style="Dato.TLabel",
                      wraplength=190).grid(row=i, column=1, sticky="w", padx=(6, 0))
        ttk.Button(f4, text="Exportar plan a CSV…", command=self.exportar).grid(
            row=len(filas), column=0, columnspan=2, sticky="ew", pady=(6, 0))

        # Área derecha: gráfico + tabla
        area = ttk.Frame(tab)
        area.pack(side="left", fill="both", expand=True, padx=(4, 0))
        pan = ttk.PanedWindow(area, orient="vertical")
        pan.pack(fill="both", expand=True)
        marco_fig = ttk.Frame(pan)
        marco_tabla = ttk.Frame(pan)
        pan.add(marco_fig, weight=4)
        pan.add(marco_tabla, weight=1)

        self.fig = Figure(figsize=(8, 5.4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=marco_fig)
        barra = NavigationToolbar2Tk(self.canvas, marco_fig, pack_toolbar=False)
        barra.update()
        barra.pack(side="bottom", fill="x")
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        cols = ("paso", "algoritmo", "desde", "hasta", "costo", "estado")
        titulos = ("#", "Algoritmo", "Desde", "Hasta", "Costo (k$)", "Estado")
        anchos = (45, 85, 200, 200, 85, 260)
        self.tabla = ttk.Treeview(marco_tabla, columns=cols, show="headings", height=7)
        for c, t, a in zip(cols, titulos, anchos):
            self.tabla.heading(c, text=t)
            self.tabla.column(c, width=a, anchor="center" if c in ("paso", "costo") else "w")
        self.tabla.tag_configure("rechazada", foreground=COLOR_RECHAZO)
        self.tabla.tag_configure("aceptada", foreground="#1b5e20")
        sb = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sb.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _construir_tab_rendimiento(self, tab: ttk.Frame) -> None:
        sup = ttk.Frame(tab, padding=8)
        sup.pack(fill="x")
        ttk.Label(sup, text="Tamaños (n):").pack(side="left")
        self.var_tamanios = tk.StringVar(value="50, 100, 250, 500, 1000, 2000")
        ttk.Entry(sup, textvariable=self.var_tamanios, width=30).pack(side="left", padx=4)
        ttk.Label(sup, text="Repeticiones:").pack(side="left", padx=(8, 0))
        self.var_reps = tk.IntVar(value=3)
        ttk.Spinbox(sup, from_=1, to=20, textvariable=self.var_reps, width=4).pack(
            side="left", padx=4)
        ttk.Label(sup, text="Semilla:").pack(side="left", padx=(8, 0))
        self.var_sem_rend = tk.IntVar(value=42)
        ttk.Spinbox(sup, from_=0, to=99999, textvariable=self.var_sem_rend, width=6).pack(
            side="left", padx=4)
        ttk.Label(sup, text="Densidad (aristas ≈ k·n), k:").pack(side="left", padx=(8, 0))
        self.var_dens = tk.IntVar(value=3)
        ttk.Spinbox(sup, from_=1, to=50, textvariable=self.var_dens, width=4).pack(
            side="left", padx=4)
        self.btn_medir = ttk.Button(sup, text="Ejecutar medición", style="Accion.TButton",
                                    command=self.ejecutar_medicion)
        self.btn_medir.pack(side="left", padx=(12, 0))
        self.progreso = ttk.Progressbar(sup, length=180, mode="determinate")
        self.progreso.pack(side="left", padx=8)

        cuerpo = ttk.PanedWindow(tab, orient="horizontal")
        cuerpo.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        mf = ttk.Frame(cuerpo)
        mt = ttk.Frame(cuerpo)
        cuerpo.add(mf, weight=3)
        cuerpo.add(mt, weight=1)
        self.fig_rend = Figure(figsize=(7, 5), dpi=100)
        self.canvas_rend = FigureCanvasTkAgg(self.fig_rend, master=mf)
        self.canvas_rend.get_tk_widget().pack(fill="both", expand=True)
        ax = self.fig_rend.add_subplot(111)
        ax.text(0.5, 0.5, "Pulse «Ejecutar medición» para comparar Prim y Kruskal",
                ha="center", va="center", fontsize=11, color="#666666")
        ax.set_axis_off()

        cols = ("n", "prim", "kruskal", "razon")
        self.tabla_rend = ttk.Treeview(mt, columns=cols, show="headings")
        for c, t, a in zip(cols, ("n", "Prim (ms)", "Kruskal (ms)", "Kruskal/Prim"),
                           (70, 95, 95, 95)):
            self.tabla_rend.heading(c, text=t)
            self.tabla_rend.column(c, width=a, anchor="center")
        self.tabla_rend.pack(fill="both", expand=True)

    def _construir_tab_ayuda(self, tab: ttk.Frame) -> None:
        txt = tk.Text(tab, wrap="word", font=("Segoe UI", 10), padx=16, pady=12,
                      relief="flat", background="#fbfbfb")
        sb = ttk.Scrollbar(tab, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        txt.pack(fill="both", expand=True)
        txt.tag_configure("h", font=("Segoe UI", 12, "bold"), foreground="#1b3a5c",
                          spacing1=10, spacing3=4)
        for linea in AYUDA.strip("\n").splitlines():
            if linea.startswith("# "):
                txt.insert("end", linea[2:] + "\n", "h")
            else:
                txt.insert("end", linea + "\n")
        txt.configure(state="disabled")

    # ------------------------------------------------------------ red
    def _set_red(self, grafo: Grafo, nombres: Sequence[str],
                 pos: Optional[Dict[int, tuple]] = None, mensaje: str = "Red cargada") -> None:
        self._detener_anim()
        self.grafo = grafo
        self.nombres = list(nombres)
        self.pos = dict(pos) if pos else self._calcular_layout()
        self._refrescar_combos()
        self._limpiar_resultados()
        self._dibujar()
        comps = componentes(grafo)
        msg = (f"{mensaje}: {grafo.n_vertices} subestaciones, "
               f"{len(grafo.aristas())} rutas candidatas.")
        if len(comps) > 1:
            msg += (f"  ⚠ La red tiene {len(comps)} componentes desconectados: "
                    "no existe un árbol que conecte todas las subestaciones.")
        self.estado.set(msg)

    def _calcular_layout(self) -> Dict[int, tuple]:
        G = nx.Graph()
        G.add_nodes_from(range(self.grafo.n_vertices))
        G.add_edges_from((u, v) for _, u, v in self.grafo.aristas())
        return nx.spring_layout(G, seed=42)

    def _refrescar_combos(self) -> None:
        for cb in (self.cb_desde, self.cb_hasta, self.cb_origen):
            cb["values"] = self.nombres
        if self.nombres:
            self.cb_desde.current(0)
            self.cb_hasta.current(1 if len(self.nombres) > 1 else 0)
            self.cb_origen.current(0)

    def _idx(self, cb: ttk.Combobox) -> int:
        return self.nombres.index(cb.get()) if cb.get() in self.nombres else 0

    def cargar_ejemplo(self) -> None:
        g, nombres = construir_red_electrica_ejemplo()
        self._set_red(g, nombres, POS_EJEMPLO, "Red de ejemplo cargada")

    def cargar_municipal(self) -> None:
        ruta = os.path.join(DIR_DATOS, "red_municipal.csv")
        self._cargar_csv(ruta, "Red municipal (datos ilustrativos) cargada")

    def generar_aleatoria(self) -> None:
        try:
            n, semilla = int(self.var_n.get()), int(self.var_semilla.get())
            g, nombres = generar_red_aleatoria(n, semilla)
        except (ValueError, tk.TclError) as e:
            messagebox.showerror("Datos inválidos", str(e))
            return
        self._set_red(g, nombres, mensaje=f"Red aleatoria generada (semilla {semilla})")

    def abrir_csv(self) -> None:
        ruta = filedialog.askopenfilename(
            title="Abrir red (CSV: origen, destino, costo)", initialdir=DIR_DATOS,
            filetypes=[("Archivos CSV", "*.csv"), ("Todos", "*.*")])
        if ruta:
            self._cargar_csv(ruta, f"Archivo «{os.path.basename(ruta)}» cargado")

    def _cargar_csv(self, ruta: str, mensaje: str) -> None:
        try:
            g, nombres = cargar_red_csv(ruta)
        except (OSError, ValueError) as e:
            messagebox.showerror("No se pudo cargar la red", str(e))
            return
        self._set_red(g, nombres, mensaje=mensaje)

    def guardar_csv(self) -> None:
        ruta = filedialog.asksaveasfilename(
            title="Guardar red", defaultextension=".csv", initialdir=DIR_DATOS,
            filetypes=[("Archivos CSV", "*.csv")])
        if ruta:
            guardar_red_csv(ruta, self.grafo, self.nombres)
            self.estado.set(f"Red guardada en {ruta}")

    def agregar_ruta(self) -> None:
        if len(self.nombres) < 2:
            return
        u, v = self._idx(self.cb_desde), self._idx(self.cb_hasta)
        if u == v:
            messagebox.showwarning("Ruta inválida", "Origen y destino deben ser distintos.")
            return
        try:
            costo = float(self.var_costo.get().replace(",", "."))
            if costo < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Costo inválido", "Ingrese un costo numérico ≥ 0.")
            return
        accion = "actualizada" if existe_ruta(self.grafo, u, v) else "agregada"
        nuevo = copiar_grafo(self.grafo, excluir=(u, v))
        nuevo.agregar_arista(u, v, costo)
        self._set_red(nuevo, self.nombres, self.pos,
                      f"Ruta {self.nombres[u]} – {self.nombres[v]} {accion} ({costo:g} k$)")

    def eliminar_ruta(self) -> None:
        u, v = self._idx(self.cb_desde), self._idx(self.cb_hasta)
        if not existe_ruta(self.grafo, u, v):
            messagebox.showinfo("Sin cambios", "No existe una ruta entre esas subestaciones.")
            return
        nuevo = copiar_grafo(self.grafo, excluir=(u, v))
        self._set_red(nuevo, self.nombres, self.pos,
                      f"Ruta {self.nombres[u]} – {self.nombres[v]} eliminada")

    def agregar_subestacion(self) -> None:
        nombre = simpledialog.askstring("Nueva subestación", "Nombre de la subestación:",
                                        parent=self)
        if nombre is None:
            return
        nombre = nombre.strip()
        if not nombre or nombre in self.nombres:
            messagebox.showwarning("Nombre inválido", "El nombre debe ser único y no vacío.")
            return
        n = self.grafo.n_vertices
        nuevo = copiar_grafo(self.grafo, n_nuevo=n + 1)
        pos = dict(self.pos)
        if pos:
            xs = [p[0] for p in pos.values()]
            ys = [p[1] for p in pos.values()]
            pos[n] = (max(xs) + (max(xs) - min(xs) or 1) * 0.15,
                      sum(ys) / len(ys) + random.uniform(-0.2, 0.2))
        else:
            pos[n] = (0.0, 0.0)
        self._set_red(nuevo, self.nombres + [nombre], pos,
                      f"Subestación «{nombre}» agregada (añada sus rutas candidatas)")
        self.cb_hasta.set(nombre)

    # ------------------------------------------------------- cálculo
    def _algoritmo_cambiado(self) -> None:
        self._detener_anim()
        self.pasos, self.paso_idx = [], 0

    def _validar(self) -> bool:
        if self.grafo.n_vertices < 2 or not self.grafo.aristas():
            messagebox.showwarning("Red incompleta",
                                   "La red necesita al menos 2 subestaciones y 1 ruta.")
            return False
        return True

    def calcular(self) -> None:
        if not self._validar():
            return
        self._detener_anim()
        self.pasos, self.paso_idx = [], 0
        algo = self.var_algo.get()
        origen = self._idx(self.cb_origen)
        algos = ["Prim", "Kruskal"] if algo == "Ambos" else [algo]
        self.ejecuciones = [ejecutar(self.grafo, a, origen) for a in algos]
        self._mostrar_resultados()

    def _mostrar_resultados(self) -> None:
        self.tabla.delete(*self.tabla.get_children())
        for e in self.ejecuciones:
            for i, (u, v, w) in enumerate(e.resultado.aristas_mst, start=1):
                self.tabla.insert("", "end", values=(i, e.algoritmo, self.nombres[u],
                                                     self.nombres[v], f"{w:g}", "En el plan"),
                                  tags=("aceptada",))
        self._actualizar_etiquetas(self.ejecuciones)
        capas = []
        for e in self.ejecuciones:
            capas.append(dict(titulo=f"{e.algoritmo}: costo total {e.resultado.peso_total:g} k$",
                              mst=e.resultado.aristas_mst, color=COLORES[e.algoritmo],
                              origen=e.origen))
        self._dibujar(capas)
        comps = componentes(self.grafo)
        if len(self.ejecuciones) == 2:
            p, k = (e.resultado.peso_total for e in self.ejecuciones)
            if abs(p - k) < 1e-9:
                msg = (f"Prim y Kruskal coinciden: costo mínimo {p:g} k$ "
                       f"(los árboles pueden diferir si hay empates de costo).")
            else:
                msg = (f"Prim cubre solo el componente del origen ({p:g} k$); "
                       f"Kruskal construye un bosque ({k:g} k$).")
        else:
            e = self.ejecuciones[0]
            msg = (f"{e.algoritmo}: plan de {len(e.resultado.aristas_mst)} cables, "
                   f"costo {e.resultado.peso_total:g} k$, calculado en {e.tiempo_ms:.3f} ms.")
        if len(comps) > 1:
            msg += f"  ⚠ Red desconectada ({len(comps)} componentes)."
        self.estado.set(msg)

    def _actualizar_etiquetas(self, ejecuciones: Sequence[EjecucionMST],
                              mst_parcial: Optional[Sequence[tuple]] = None) -> None:
        total = costo_total_rutas(self.grafo)
        m = len(self.grafo.aristas())
        comps = componentes(self.grafo)
        self.var_res["total"].set(f"{total:,.2f} k$ ({m} rutas)")
        self.var_res["conexa"].set("Conexa ✔" if len(comps) == 1
                                   else f"{len(comps)} componentes ⚠")
        if not ejecuciones:
            for k in ("costo", "ahorro", "aristas", "tiempo"):
                self.var_res[k].set("—")
            return
        aristas = mst_parcial if mst_parcial is not None else ejecuciones[0].resultado.aristas_mst
        costo = sum(w for _, _, w in aristas)
        ahorro = total - costo
        pct = (ahorro / total * 100) if total else 0.0
        self.var_res["costo"].set(f"{costo:,.2f} k$")
        self.var_res["ahorro"].set(f"{ahorro:,.2f} k$ ({pct:.1f} %)")
        self.var_res["aristas"].set(f"{len(aristas)} de {m} rutas")
        self.var_res["tiempo"].set("  ·  ".join(f"{e.algoritmo}: {e.tiempo_ms:.3f} ms"
                                                for e in ejecuciones))

    def _limpiar_resultados(self) -> None:
        self.ejecuciones, self.pasos, self.paso_idx = [], [], 0
        self.tabla.delete(*self.tabla.get_children())
        self._actualizar_etiquetas([])

    def _dibujar(self, capas: Optional[List[dict]] = None) -> None:
        self.fig.clear()
        if not capas:
            capas = [dict(titulo="Red candidata (todas las rutas posibles)")]
        for i, capa in enumerate(capas, start=1):
            ax = self.fig.add_subplot(1, len(capas), i)
            dibujar_red(ax, self.grafo, self.nombres, self.pos,
                        mst=capa.get("mst", ()), rechazadas=capa.get("rechazadas", ()),
                        actual=capa.get("actual"), color=capa.get("color", COLORES["Prim"]),
                        origen=capa.get("origen"), titulo=capa.get("titulo", ""))
        self.fig.tight_layout()
        self.canvas.draw_idle()

    # ------------------------------------------------------ animación
    def _preparar_anim(self) -> bool:
        algo = self.var_algo.get()
        if algo == "Ambos":
            messagebox.showinfo("Animación", "Seleccione Prim o Kruskal para ver el "
                                             "algoritmo paso a paso.")
            return False
        if not self._validar():
            return False
        origen = self._idx(self.cb_origen)
        e = ejecutar(self.grafo, algo, origen)
        self.ejecuciones = [e]
        self.pasos, self.paso_idx = e.pasos, 0
        self.algoritmo_anim, self.origen_anim = algo, e.origen
        self.tabla.delete(*self.tabla.get_children())
        self._actualizar_etiquetas([e], mst_parcial=[])
        self._dibujar_paso(None)
        if algo == "Prim":
            self.estado.set(f"Prim parte desde «{self.nombres[origen]}» y en cada paso "
                            "incorpora la subestación más barata de conectar al árbol.")
        else:
            self.estado.set("Kruskal ordena las rutas por costo y acepta cada una si une "
                            "dos sub-redes distintas (si no, formaría un ciclo).")
        return True

    def _anim_vigente(self) -> bool:
        return (bool(self.pasos) and self.algoritmo_anim == self.var_algo.get()
                and (self.var_algo.get() != "Prim"
                     or self.origen_anim == self._idx(self.cb_origen)))

    def siguiente_paso(self) -> bool:
        """Avanza un paso. Devuelve True si quedan pasos por mostrar."""
        if not self._anim_vigente() or self.paso_idx >= len(self.pasos):
            return self._preparar_anim() and bool(self.pasos)
        u, v, w, ok = self.pasos[self.paso_idx]
        self.paso_idx += 1
        algo = self.algoritmo_anim
        if ok:
            estado = ("Aceptada: une dos sub-redes" if algo == "Kruskal"
                      else f"Incorpora «{self.nombres[v]}» al árbol")
        else:
            estado = "Rechazada: formaría un ciclo"
        self.tabla.insert("", "end", values=(self.paso_idx, algo, self.nombres[u],
                                             self.nombres[v], f"{w:g}", estado),
                          tags=("aceptada" if ok else "rechazada",))
        self.tabla.yview_moveto(1.0)
        self._dibujar_paso((u, v, w, ok))
        mst = [(a, b, c) for a, b, c, acc in self.pasos[:self.paso_idx] if acc]
        self._actualizar_etiquetas(self.ejecuciones, mst_parcial=mst)
        self.estado.set(f"Paso {self.paso_idx}/{len(self.pasos)} – {self.nombres[u]} – "
                        f"{self.nombres[v]} ({w:g} k$): {estado.lower()}.")
        if self.paso_idx == len(self.pasos):
            total = sum(c for _, _, c in mst)
            self.estado.set(f"{algo} terminado: {len(mst)} cables, costo mínimo {total:g} k$.")
            return False
        return True

    def _dibujar_paso(self, actual: Optional[Paso]) -> None:
        hechos = self.pasos[:self.paso_idx]
        mst = [(u, v, w) for u, v, w, ok in hechos if ok]
        rech = [(u, v, w) for u, v, w, ok in hechos if not ok]
        algo = self.algoritmo_anim or self.var_algo.get()
        titulo = (f"{algo} – paso {self.paso_idx}/{len(self.pasos)} · "
                  f"costo acumulado {sum(w for _, _, w in mst):g} k$")
        self._dibujar([dict(titulo=titulo, mst=mst, rechazadas=rech, actual=actual,
                            color=COLORES.get(algo, COLORES["Prim"]),
                            origen=self.origen_anim)])

    def animar(self) -> None:
        if self._job is not None:
            self._detener_anim()
            return
        if not self._anim_vigente() or self.paso_idx >= len(self.pasos):
            if not self._preparar_anim():
                return
        self.btn_animar.configure(text="⏸ Pausar")
        self._job = self.after(int(self.var_vel.get()), self._tick)

    def _tick(self) -> None:
        if self.siguiente_paso():
            self._job = self.after(int(self.var_vel.get()), self._tick)
        else:
            self._job = None
            self.btn_animar.configure(text="▶ Animar")

    def _detener_anim(self) -> None:
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None
        self.btn_animar.configure(text="▶ Animar")

    def reiniciar(self) -> None:
        self._detener_anim()
        self._limpiar_resultados()
        self._dibujar()
        self.estado.set("Vista reiniciada.")

    def exportar(self) -> None:
        if not self.ejecuciones:
            messagebox.showinfo("Sin plan", "Primero calcule el MST.")
            return
        ruta = filedialog.asksaveasfilename(
            title="Exportar plan de tendido", defaultextension=".csv",
            initialfile="plan_tendido_mst.csv", filetypes=[("Archivos CSV", "*.csv")])
        if ruta:
            exportar_mst_csv(ruta, self.ejecuciones, self.nombres)
            self.estado.set(f"Plan exportado a {ruta}")

    # ---------------------------------------------------- rendimiento
    def ejecutar_medicion(self) -> None:
        try:
            tamanios = [int(x) for x in self.var_tamanios.get().replace(";", ",").split(",")
                        if x.strip()]
            reps = int(self.var_reps.get())
            semilla = int(self.var_sem_rend.get())
            dens = int(self.var_dens.get())
            if not tamanios or min(tamanios) < 2 or reps < 1 or dens < 1:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showerror("Datos inválidos", "Ingrese tamaños enteros ≥ 2 separados "
                                                    "por comas, y repeticiones/densidad ≥ 1.")
            return
        self.btn_medir.state(["disabled"])
        self.progreso["value"] = 0

        def avance(hechos: int, total: int) -> None:
            self.progreso["value"] = hechos * 100 / total
            self.estado.set(f"Midiendo… {hechos}/{total} ejecuciones")
            self.update()

        try:
            datos = medir_rendimiento(sorted(set(tamanios)), reps, semilla, dens, avance)
        finally:
            self.btn_medir.state(["!disabled"])
        self._mostrar_rendimiento(datos, reps, semilla, dens)

    def _mostrar_rendimiento(self, datos, reps: int, semilla: int, dens: int) -> None:
        ns = [d["n"] for d in datos]
        mp = [sum(d["prim_ms"]) / len(d["prim_ms"]) for d in datos]
        mk = [sum(d["kruskal_ms"]) / len(d["kruskal_ms"]) for d in datos]
        self.tabla_rend.delete(*self.tabla_rend.get_children())
        for n, p, k in zip(ns, mp, mk):
            self.tabla_rend.insert("", "end", values=(n, f"{p:.3f}", f"{k:.3f}",
                                                      f"{(k / p if p else 0):.2f}×"))
        self.fig_rend.clear()
        ax = self.fig_rend.add_subplot(111)
        ax.plot(ns, mp, "o-", color=COLORES["Prim"], lw=2, label="Prim (min-heap)")
        ax.plot(ns, mk, "s--", color=COLORES["Kruskal"], lw=2, label="Kruskal (Union-Find)")
        if len(ns) > 1:
            ax.set_xscale("log")
            ax.set_yscale("log")
        ax.set_xlabel("Número de subestaciones (n)")
        ax.set_ylabel("Tiempo medio (ms)")
        ax.set_title(f"Prim vs Kruskal · aristas ≈ {dens}n · {reps} rep. · semilla {semilla}",
                     fontsize=11, fontweight="bold")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        self.fig_rend.tight_layout()
        self.canvas_rend.draw_idle()
        self.estado.set(f"Medición completada para n = {', '.join(map(str, ns))}.")

    def _cerrar(self) -> None:
        self._detener_anim()
        self.quit()
        self.destroy()


AYUDA = """
# ¿Qué resuelve esta herramienta?
Una empresa distribuidora debe interconectar todas sus subestaciones eléctricas con el menor costo de tendido posible. Cada subestación es un vértice y cada ruta posible de cable es una arista cuyo peso es el costo estimado (miles de USD). El Árbol de Expansión Mínima (MST) es el conjunto de cables más barato que conecta todas las subestaciones sin ciclos.

# Cómo usarla
1. Red de entrada: cargue la red de ejemplo, la red municipal de Ciudad Guayana (datos ilustrativos), un archivo CSV propio o genere una red aleatoria con semilla reproducible.
2. Editar rutas: agregue, actualice o elimine rutas candidatas y agregue nuevas subestaciones.
3. Algoritmo: elija Prim (y su subestación de origen), Kruskal o Ambos. «Calcular MST» muestra el plan óptimo; «Animar» y «Paso» muestran cómo decide cada algoritmo.
4. Resultados: costo del plan, ahorro respecto a tender todas las rutas candidatas, número de cables y tiempo de cómputo. «Exportar plan a CSV» guarda la lista de cables para licitación.

# Formato CSV de la red
Encabezado: origen,destino,costo   (también se acepta ';' como separador y coma decimal)
Ejemplo:
  SE Alta Vista,SE Unare,12
  SE Unare,SE Los Olivos,10

# Leyenda del gráfico
• Gris discontinuo: ruta candidata.   • Azul (Prim) / naranja (Kruskal): cable incluido en el plan.
• Rojo punteado: ruta rechazada por formar un ciclo (Kruskal).   • Amarillo: arista evaluada en el paso actual.
• Verde: subestación de origen de Prim.

# Prim – ventajas y desventajas para la red eléctrica
+ Crece desde una subestación conocida (p. ej. la central), igual que una red que se expande por etapas.
+ Eficiente en redes densas: O((V+E) log V) con min-heap.
− Solo cubre el componente conexo del origen; no sirve si hay zonas aisladas.
− Requiere elegir un origen y una cola de prioridad más compleja.

# Kruskal – ventajas y desventajas para la red eléctrica
+ Trabaja con el catálogo global de rutas ordenado por costo; implementación sencilla.
+ Si la red está desconectada, entrega un bosque de expansión mínima (un plan por zona).
+ Muy adecuado para redes dispersas (pocas rutas por subestación): O(E log E).
− Necesita conocer y ordenar todas las rutas antes de empezar.
− Peor localidad de memoria en redes muy grandes.

Ambos algoritmos garantizan el mismo costo mínimo (Teorema del Corte); si hay costos empatados pueden elegir cables distintos con igual costo total.

# Créditos
Equipo 5 – Análisis y Diseño de Algoritmos, UNEG: Ing. Bryan Salazar, Ing. Johana Carvajal, Ing. David González, Ing. Yrene Corrales, Ing. José Ortiz.
"""


def main() -> None:
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:  # pragma: no cover - depende del sistema
            pass
    app = AppMST()
    app.mainloop()


if __name__ == "__main__":
    main()

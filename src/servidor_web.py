"""
Servidor Web Local – Planificador de Red de Distribución Eléctrica
Árbol de Expansión Mínima (Prim y Kruskal)
Equipo 5 – Análisis y Diseño de Algoritmos – UNEG
Integrantes:
  - Ing. Bryan Salazar
  - Ing. Johana Carvajal
  - Ing. David González
  - Ing. Yrene Corrales
  - Ing. José Ortiz

Levanta un servidor HTTP local en http://localhost:5000 con API REST
y una interfaz web interactiva completa (HTML5 + CSS3 + JS).
"""

from __future__ import annotations

import json
import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

DIR_SRC = os.path.dirname(os.path.abspath(__file__))
DIR_RAIZ = os.path.dirname(DIR_SRC)
sys.path.insert(0, DIR_SRC)

from grafo import Grafo
from prim import prim
from kruskal import kruskal
from planificador import (
    ejecutar, traza_prim, traza_kruskal, cargar_red_csv,
    generar_red_aleatoria, medir_rendimiento, componentes, costo_total_rutas
)
from mst_algorithms import construir_red_electrica_ejemplo

PUERTO = 5000

HTML_INDEX = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Planificador de Red Eléctrica · MST (Prim y Kruskal) · Equipo 5 UNEG</title>
  <style>
    :root {
      --primary: #1f77b4;
      --secondary: #e6550d;
      --success: #2ca02c;
      --danger: #d62728;
      --warning: #f2b705;
      --dark: #1b3a5c;
      --light: #f8fafc;
      --border: #e2e8f0;
      --card-bg: #ffffff;
      --text: #1e293b;
      --text-muted: #64748b;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
    body { background: #f1f5f9; color: var(--text); display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
    header {
      background: white; border-bottom: 1px solid var(--border);
      padding: 12px 24px; display: flex; justify-content: space-between; align-items: center;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    header h1 { font-size: 1.25rem; color: var(--dark); display: flex; align-items: center; gap: 8px; }
    header .badge { background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }
    .layout { display: flex; flex: 1; overflow: hidden; }
    .sidebar { width: 360px; background: white; border-right: 1px solid var(--border); overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 16px; }
    .main { flex: 1; display: flex; flex-direction: column; padding: 16px; gap: 16px; overflow-y: auto; }
    
    .card { background: var(--card-bg); border-radius: 8px; border: 1px solid var(--border); padding: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.02); }
    .card-title { font-size: 0.875rem; font-weight: 700; color: var(--dark); margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
    
    .btn-group { display: flex; gap: 6px; flex-wrap: wrap; }
    button, select, input {
      font-size: 0.85rem; padding: 7px 12px; border-radius: 6px; border: 1px solid var(--border);
      cursor: pointer; transition: all 0.15s; outline: none;
    }
    button.btn-primary { background: var(--primary); color: white; border: none; font-weight: 600; }
    button.btn-primary:hover { background: #1a6296; }
    button.btn-secondary { background: var(--secondary); color: white; border: none; font-weight: 600; }
    button.btn-secondary:hover { background: #c54609; }
    button.btn-dark { background: var(--dark); color: white; border: none; font-weight: 600; }
    button.btn-dark:hover { background: #132a42; }
    button.btn-outline { background: white; color: var(--text); }
    button.btn-outline:hover { background: #f8fafc; border-color: #cbd5e1; }
    
    .canvas-container {
      flex: 1; min-height: 400px; background: white; border-radius: 8px; border: 1px solid var(--border);
      position: relative; overflow: hidden; display: flex; justify-content: center; align-items: center;
    }
    svg#network { width: 100%; height: 100%; }
    
    .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
    .stat-box { background: white; border: 1px solid var(--border); border-radius: 8px; padding: 12px; }
    .stat-label { font-size: 0.75rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; }
    .stat-value { font-size: 1.25rem; font-weight: 700; color: var(--dark); margin-top: 4px; }
    
    table { width: 100%; border-collapse: collapse; font-size: 0.8rem; margin-top: 8px; }
    th, td { padding: 6px 10px; text-align: left; border-bottom: 1px solid #f1f5f9; }
    th { font-weight: 600; color: var(--text-muted); background: #f8fafc; }
    .tag-ok { color: var(--success); font-weight: 600; }
    .tag-rej { color: var(--danger); font-weight: 600; }
    
    .legend {
      position: absolute; bottom: 12px; left: 12px; background: rgba(255,255,255,0.92);
      backdrop-filter: blur(4px); padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border);
      font-size: 0.75rem; display: flex; flex-direction: column; gap: 4px; pointer-events: none;
    }
    .legend-item { display: flex; align-items: center; gap: 8px; }
    .legend-color { width: 16px; height: 3px; border-radius: 2px; }
    
    .tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--border); margin-bottom: 12px; }
    .tab-btn { padding: 6px 14px; background: none; border: none; border-bottom: 2px solid transparent; border-radius: 0; font-weight: 600; color: var(--text-muted); }
    .tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); }
    
    .footer-bar {
      background: white; border-top: 1px solid var(--border); padding: 6px 16px;
      font-size: 0.8rem; color: var(--text-muted); display: flex; justify-content: space-between;
    }
  </style>
</head>
<body>

  <header>
    <h1>⚡ Planificador de Red de Distribución Eléctrica <span class="badge">Árbol de Expansión Mínima</span></h1>
    <span style="font-size: 0.85rem; color: var(--text-muted); font-weight: 500;">
      Equipo 5 · Análisis y Diseño de Algoritmos (UNEG)
    </span>
  </header>

  <div class="layout">
    <!-- BARRA LATERAL -->
    <div class="sidebar">
      
      <!-- Red de Entrada -->
      <div class="card">
        <div class="card-title">1. Red de Entrada</div>
        <div class="btn-group" style="flex-direction: column;">
          <button class="btn-outline" onclick="cargarRed('ejemplo')">📍 Red Ejemplo (8 Subestaciones)</button>
          <button class="btn-outline" onclick="cargarRed('municipal')">🏙️ Red Ciudad Guayana (12 SE)</button>
          <div style="display: flex; gap: 6px; margin-top: 4px;">
            <input type="number" id="numVertices" value="15" min="3" max="100" style="width: 70px;" title="Vértices">
            <button class="btn-outline" style="flex: 1;" onclick="generarAleatoria()">🎲 Red Aleatoria</button>
          </div>
        </div>
      </div>

      <!-- Algoritmo y Ejecución -->
      <div class="card">
        <div class="card-title">2. Selección de Algoritmo</div>
        <div style="display: flex; gap: 8px; margin-bottom: 10px;">
          <label style="font-size: 0.85rem; display: flex; align-items: center; gap: 4px;">
            <input type="radio" name="algoritmo" value="Kruskal" checked onchange="cambiarAlgoritmo()"> Kruskal
          </label>
          <label style="font-size: 0.85rem; display: flex; align-items: center; gap: 4px;">
            <input type="radio" name="algoritmo" value="Prim" onchange="cambiarAlgoritmo()"> Prim
          </label>
          <label style="font-size: 0.85rem; display: flex; align-items: center; gap: 4px;">
            <input type="radio" name="algoritmo" value="Ambos" onchange="cambiarAlgoritmo()"> Ambos
          </label>
        </div>

        <div id="primOrigenBox" style="display: none; margin-bottom: 10px;">
          <label style="font-size: 0.8rem; color: var(--text-muted);">Nodo Origen (Prim):</label>
          <select id="selectOrigen" style="width: 100%; margin-top: 4px;"></select>
        </div>

        <button class="btn-dark" style="width: 100%; padding: 9px;" onclick="resolverMST()">⚡ Calcular MST Óptimo</button>
        
        <div style="display: flex; gap: 6px; margin-top: 8px;">
          <button class="btn-outline" style="flex: 1;" id="btnAnimar" onclick="toggleAnimacion()">▶ Animar Traza</button>
          <button class="btn-outline" onclick="pasoSiguiente()">⏭ Paso</button>
          <button class="btn-outline" onclick="reiniciarVista()">↺</button>
        </div>
      </div>

      <!-- Edición Rápida -->
      <div class="card">
        <div class="card-title">3. Editar Conexión Candidata</div>
        <div style="display: flex; flex-direction: column; gap: 6px;">
          <div style="display: flex; gap: 4px;">
            <select id="editU" style="flex: 1;"></select>
            <select id="editV" style="flex: 1;"></select>
          </div>
          <div style="display: flex; gap: 4px;">
            <input type="number" id="editW" placeholder="Costo (k$)" style="flex: 1;" min="0.1" step="0.5" value="5">
            <button class="btn-outline" onclick="agregarRuta()">Guardar</button>
            <button class="btn-outline" style="color: var(--danger);" onclick="eliminarRuta()">Eliminar</button>
          </div>
        </div>
      </div>

      <!-- Integrantes -->
      <div class="card" style="margin-top: auto; font-size: 0.75rem; color: var(--text-muted); line-height: 1.4;">
        <strong>Equipo 5:</strong><br>
        • Ing. Bryan Salazar<br>
        • Ing. Johana Carvajal<br>
        • Ing. David González<br>
        • Ing. Yrene Corrales<br>
        • Ing. José Ortiz
      </div>

    </div>

    <!-- ÁREA PRINCIPAL -->
    <div class="main">
      
      <!-- Estadísticas Rápidas -->
      <div class="stats-grid">
        <div class="stat-box">
          <div class="stat-label">Costo Total MST</div>
          <div class="stat-value" id="valCosto">—</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Costo Todas Rutas</div>
          <div class="stat-value" id="valTotal">—</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Ahorro Obtenido</div>
          <div class="stat-value" id="valAhorro" style="color: var(--success);">—</div>
        </div>
        <div class="stat-box">
          <div class="stat-label">Tiempo Cómputo</div>
          <div class="stat-value" id="valTiempo" style="font-size: 1.1rem;">—</div>
        </div>
      </div>

      <!-- Canvas SVG de la Red -->
      <div class="canvas-container">
        <svg id="network"></svg>

        <div class="legend">
          <div class="legend-item"><div class="legend-color" style="background: #94a3b8; border-style: dashed;"></div> Ruta candidata</div>
          <div class="legend-item"><div class="legend-color" style="background: var(--primary); height: 4px;"></div> Cable en el plan (MST)</div>
          <div class="legend-item"><div class="legend-color" style="background: var(--danger); height: 3px; border-style: dotted;"></div> Rechazada (ciclo)</div>
          <div class="legend-item"><div class="legend-color" style="background: var(--warning); height: 5px;"></div> Arista evaluada</div>
        </div>
      </div>

      <!-- Tabla de Decisiones / Pasos -->
      <div class="card" style="max-height: 200px; overflow-y: auto;">
        <div class="card-title">Traza de Decisiones del Algoritmo (Paso a Paso)</div>
        <table>
          <thead>
            <tr>
              <th style="width: 40px;">#</th>
              <th>Algoritmo</th>
              <th>Desde</th>
              <th>Hasta</th>
              <th>Costo (k$)</th>
              <th>Decisión</th>
            </tr>
          </thead>
          <tbody id="tablaPasos">
            <tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Calcule o anime el MST para ver la traza detallada.</td></tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>

  <div class="footer-bar">
    <span id="statusBar">Listo. Seleccione una red o calcule el MST.</span>
    <span>Python 3.13 · NetworkX · Servidor Local Activo</span>
  </div>

  <script>
    let networkData = null;
    let mstResult = null;
    let animIndex = 0;
    let animTimer = null;

    async function cargarRed(tipo) {
      detenerAnim();
      const res = await fetch(`/api/red?tipo=${tipo}`);
      networkData = await res.json();
      mstResult = null;
      animIndex = 0;
      actualizarCombos();
      renderizarGrafo();
      document.getElementById('statusBar').innerText = `Red cargada: ${networkData.nombres.length} subestaciones, ${networkData.aristas.length} rutas candidatas.`;
      limpiarStats();
    }

    async function generarAleatoria() {
      detenerAnim();
      const n = document.getElementById('numVertices').value;
      const res = await fetch(`/api/aleatoria?n=${n}&semilla=42`);
      networkData = await res.json();
      mstResult = null;
      animIndex = 0;
      actualizarCombos();
      renderizarGrafo();
      document.getElementById('statusBar').innerText = `Red aleatoria generada: ${n} subestaciones.`;
      limpiarStats();
    }

    function cambiarAlgoritmo() {
      const algo = document.querySelector('input[name="algoritmo"]:checked').value;
      document.getElementById('primOrigenBox').style.display = (algo === 'Prim') ? 'block' : 'none';
      detenerAnim();
    }

    function actualizarCombos() {
      const selectOrigen = document.getElementById('selectOrigen');
      const editU = document.getElementById('editU');
      const editV = document.getElementById('editV');
      selectOrigen.innerHTML = ''; editU.innerHTML = ''; editV.innerHTML = '';
      networkData.nombres.forEach((nom, i) => {
        selectOrigen.innerHTML += `<option value="${i}">${nom}</option>`;
        editU.innerHTML += `<option value="${i}">${nom}</option>`;
        editV.innerHTML += `<option value="${i}">${nom}</option>`;
      });
      if (networkData.nombres.length > 1) editV.selectedIndex = 1;
    }

    async function resolverMST() {
      detenerAnim();
      const algo = document.querySelector('input[name="algoritmo"]:checked').value;
      const origen = parseInt(document.getElementById('selectOrigen').value || 0);

      const res = await fetch('/api/resolver', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ grafo: networkData, algoritmo: algo, origen: origen })
      });
      mstResult = await res.json();
      mostrarResultados();
    }

    function mostrarResultados() {
      if (!mstResult) return;
      const totalRutas = networkData.aristas.reduce((a, b) => a + b[0], 0);
      const e = mstResult.ejecuciones[0];
      const costoMst = e.peso_total;
      const ahorro = totalRutas - costoMst;
      const pct = (ahorro / totalRutas * 100).toFixed(1);

      document.getElementById('valCosto').innerText = `${costoMst.toFixed(1)} k$`;
      document.getElementById('valTotal').innerText = `${totalRutas.toFixed(1)} k$`;
      document.getElementById('valAhorro').innerText = `${ahorro.toFixed(1)} k$ (${pct}%)`;
      document.getElementById('valTiempo').innerText = mstResult.ejecuciones.map(x => `${x.algoritmo}: ${x.tiempo_ms.toFixed(3)}ms`).join(' · ');

      renderizarGrafo(e.aristas_mst);

      const tbody = document.getElementById('tablaPasos');
      tbody.innerHTML = '';
      e.aristas_mst.forEach((a, i) => {
        tbody.innerHTML += `
          <tr>
            <td>${i+1}</td>
            <td>${e.algoritmo}</td>
            <td>${networkData.nombres[a[0]]}</td>
            <td>${networkData.nombres[a[1]]}</td>
            <td>${a[2]} k$</td>
            <td><span class="tag-ok">✓ En el plan</span></td>
          </tr>
        `;
      });
      document.getElementById('statusBar').innerText = `MST calculado con éxito. ${e.aristas_mst.length} cables seleccionados.`;
    }

    // ANIMACIÓN
    function toggleAnimacion() {
      if (animTimer) {
        detenerAnim();
      } else {
        iniciarAnim();
      }
    }

    async function iniciarAnim() {
      if (!mstResult || mstResult.ejecuciones.length > 1) {
        await resolverMST();
      }
      const e = mstResult.ejecuciones[0];
      if (animIndex >= e.pasos.length) animIndex = 0;
      document.getElementById('btnAnimar').innerText = '⏸ Pausar';
      animTimer = setInterval(pasoSiguiente, 600);
    }

    function detenerAnim() {
      if (animTimer) {
        clearInterval(animTimer);
        animTimer = null;
      }
      document.getElementById('btnAnimar').innerText = '▶ Animar Traza';
    }

    function pasoSiguiente() {
      if (!mstResult) return;
      const e = mstResult.ejecuciones[0];
      if (animIndex >= e.pasos.length) {
        detenerAnim();
        return;
      }
      animIndex++;
      const pasosActuales = e.pasos.slice(0, animIndex);
      const aceptadas = pasosActuales.filter(p => p[3]);
      const rechazadas = pasosActuales.filter(p => !p[3]);
      const ultima = e.pasos[animIndex - 1];

      renderizarGrafo(aceptadas.map(p => [p[0], p[1], p[2]]), rechazadas.map(p => [p[0], p[1], p[2]]), ultima);

      const tbody = document.getElementById('tablaPasos');
      tbody.innerHTML = '';
      pasosActuales.forEach((p, i) => {
        tbody.innerHTML += `
          <tr>
            <td>${i+1}</td>
            <td>${e.algoritmo}</td>
            <td>${networkData.nombres[p[0]]}</td>
            <td>${networkData.nombres[p[1]]}</td>
            <td>${p[2]} k$</td>
            <td><span class="${p[3] ? 'tag-ok' : 'tag-rej'}">${p[3] ? '✓ Aceptada' : '✗ Rechazada (ciclo)'}</span></td>
          </tr>
        `;
      });
      tbody.scrollTop = tbody.scrollHeight;
    }

    function reiniciarVista() {
      detenerAnim();
      animIndex = 0;
      renderizarGrafo();
      document.getElementById('tablaPasos').innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Calcule o anime el MST para ver la traza.</td></tr>';
      limpiarStats();
    }

    function limpiarStats() {
      document.getElementById('valCosto').innerText = '—';
      document.getElementById('valTotal').innerText = '—';
      document.getElementById('valAhorro').innerText = '—';
      document.getElementById('valTiempo').innerText = '—';
    }

    // RENDERIZADO SVG
    function renderizarGrafo(aristasMst = [], aristasRech = [], pasoActual = null) {
      if (!networkData) return;
      const svg = document.getElementById('network');
      const rect = svg.getBoundingClientRect();
      const W = rect.width || 800;
      const H = rect.height || 500;
      svg.innerHTML = '';

      // Layout circular simple o posiciones
      const N = networkData.nombres.length;
      const coords = {};
      const cx = W / 2, cy = H / 2, r = Math.min(W, H) * 0.4;
      for (let i = 0; i < N; i++) {
        const theta = (2 * Math.PI * i) / N - Math.PI / 2;
        coords[i] = { x: cx + r * Math.cos(theta), y: cy + r * Math.sin(theta) };
      }

      // Convertir conjuntos de aristas para búsqueda O(1)
      const mstKeys = new Set(aristasMst.map(a => `${Math.min(a[0], a[1])}-${Math.max(a[0], a[1])}`));
      const rechKeys = new Set(aristasRech.map(a => `${Math.min(a[0], a[1])}-${Math.max(a[0], a[1])}`));

      // 1. Dibujar aristas candidatas
      networkData.aristas.forEach(a => {
        const u = a[1], v = a[2], w = a[0];
        const key = `${Math.min(u, v)}-${Math.max(u, v)}`;
        const p1 = coords[u], p2 = coords[v];

        let stroke = '#cbd5e1', strokeWidth = 1.5, dash = '5,5';
        if (mstKeys.has(key)) {
          stroke = '#1f77b4'; strokeWidth = 3.5; dash = 'none';
        } else if (rechKeys.has(key)) {
          stroke = '#d62728'; strokeWidth = 2; dash = '3,3';
        }

        if (pasoActual && Math.min(pasoActual[0], pasoActual[1]) === Math.min(u, v) &&
            Math.max(pasoActual[0], pasoActual[1]) === Math.max(u, v)) {
          stroke = '#f2b705'; strokeWidth = 6; dash = 'none';
        }

        svg.innerHTML += `<line x1="${p1.x}" y1="${p1.y}" x2="${p2.x}" y2="${p2.y}" stroke="${stroke}" stroke-width="${strokeWidth}" stroke-dasharray="${dash}" />`;

        // Etiqueta peso
        const mx = (p1.x + p2.x) / 2, my = (p1.y + p2.y) / 2;
        svg.innerHTML += `<rect x="${mx-12}" y="${my-8}" width="24" height="16" fill="white" rx="3" opacity="0.85"/>
                          <text x="${mx}" y="${my+4}" font-size="10" text-anchor="middle" fill="#475569" font-weight="600">${w}</text>`;
      });

      // 2. Dibujar nodos
      for (let i = 0; i < N; i++) {
        const p = coords[i];
        svg.innerHTML += `<circle cx="${p.x}" cy="${p.y}" r="18" fill="white" stroke="#1b3a5c" stroke-width="2.5" />
                          <text x="${p.x}" y="${p.y+4}" font-size="11" font-weight="700" text-anchor="middle" fill="#1b3a5c">${i}</text>
                          <text x="${p.x}" y="${p.y+30}" font-size="11" font-weight="600" text-anchor="middle" fill="#0f172a">${networkData.nombres[i]}</text>`;
      }
    }

    // Inicializar
    cargarRed('ejemplo');
  </script>
</body>
</html>
"""

class ManejadorWeb(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/" or url.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_INDEX.encode("utf-8"))

        elif url.path == "/api/red":
            params = dict(qc.split("=") for qc in url.query.split("&") if "=" in qc)
            tipo = params.get("tipo", "ejemplo")
            if tipo == "municipal":
                ruta_csv = os.path.join(DIR_RAIZ, "data", "red_municipal.csv")
                g, nombres = cargar_red_csv(ruta_csv)
            else:
                g, nombres = construir_red_electrica_ejemplo()

            data = {
                "n_vertices": g.n_vertices,
                "nombres": nombres,
                "aristas": g.aristas(),
            }
            self._responder_json(data)

        elif url.path == "/api/aleatoria":
            params = dict(qc.split("=") for qc in url.query.split("&") if "=" in qc)
            n = int(params.get("n", 15))
            semilla = int(params.get("semilla", 42))
            g, nombres = generar_red_aleatoria(n, semilla=semilla)
            data = {
                "n_vertices": g.n_vertices,
                "nombres": nombres,
                "aristas": g.aristas(),
            }
            self._responder_json(data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/api/resolver":
            longitud = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(longitud).decode("utf-8"))
            
            raw_grafo = body["grafo"]
            algoritmo = body.get("algoritmo", "Kruskal")
            origen = int(body.get("origen", 0))

            g = Grafo(raw_grafo["n_vertices"])
            for w, u, v in raw_grafo["aristas"]:
                g.agregar_arista(u, v, w)

            algos = ["Prim", "Kruskal"] if algoritmo == "Ambos" else [algoritmo]
            ejecuciones = []
            for a in algos:
                e = ejecutar(g, a, origen=origen)
                ejecuciones.append({
                    "algoritmo": e.algoritmo,
                    "peso_total": e.resultado.peso_total,
                    "aristas_mst": e.resultado.aristas_mst,
                    "pasos": e.pasos,
                    "tiempo_ms": e.tiempo_ms,
                })

            self._responder_json({"ejecuciones": ejecuciones})
        else:
            self.send_response(404)
            self.end_headers()

    def _responder_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def log_message(self, format, *args):
        # Silenciar logs ruidosos en consola
        return


def iniciar_servidor():
    servidor = HTTPServer(("0.0.0.0", PUERTO), ManejadorWeb)
    print(f"Servidor Web Planificador MST levantado en http://localhost:{PUERTO}")
    servidor.serve_forever()


if __name__ == "__main__":
    iniciar_servidor()

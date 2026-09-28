#!/usr/bin/env python3
"""
Analizador de wallets en los mercados "Bitcoin Up or Down" de Polymarket.
Solo lee datos públicos: no envía órdenes ni necesita clave.

Qué hace:
  1. Recorre las ventanas ya cerradas de las últimas --horas (mercados de 5m o 15m).
  2. Descarga todas las operaciones de cada mercado (data-api /trades) y ve qué wallets operan y cuánto.
  3. A las wallets con más volumen y más ganancia aparente les descarga su actividad completa
     (data-api /activity): compras, ventas, SPLIT (crear pares Up+Down por 1 $) y MERGE (deshacerlos).
  4. Para cada wallet y ventana calcula cuánto gastó, cuánto cobró y cuánto valían al cierre las
     acciones que le quedaban (con la resolución oficial). De ahí sale su ganancia.
  5. Mide cómo opera: en qué segundo de la ventana compra, a qué precio, si compra los dos lados
     (y cuánto le cuesta el par), si vende antes del cierre y si toma o pone liquidez.
  6. Genera un informe HTML que compara las wallets que más ganan con las que más pierden.

Uso:
  pip install requests websocket-client
  python wallets.py                         # últimas 6 horas de mercados de 5 min
  python wallets.py --horas 12 --periodo 15m
  python wallets.py --demo                  # datos inventados, para ver el informe sin conexión
  python wallets.py --informe resultados_wallets_X/datos.json   # regenera solo el HTML
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import requests

from simulador import DATA_API, HTTP, PERIODOS, cargar_mercado, iso, resolucion_oficial, slug_para

N_TRAMOS = 10  # la ventana se divide en 10 tramos para ver cuándo compra cada wallet


# ---------------------------------------------------------------------------
# Descarga con reintentos y paginación
# ---------------------------------------------------------------------------

class RechazoAPI(Exception):
    """La API rechazó la petición (400/404/422): no tiene sentido reintentar."""


def get_reintentos(url: str, params: dict, intentos: int = 5):
    espera, err = 1.0, None
    for _ in range(intentos):
        try:
            r = HTTP.get(url, params=params, timeout=20)
        except requests.RequestException as e:
            err = e
        else:
            if r.status_code == 200:
                return r.json()
            if r.status_code in (400, 404, 422):
                raise RechazoAPI(f"HTTP {r.status_code}: {r.text[:200]}")
            err = f"HTTP {r.status_code}"  # 429 o 5xx: esperar y reintentar
        time.sleep(espera)
        espera *= 2
    raise RuntimeError(f"{url} falló tras {intentos} intentos: {err}")


def paginar(url: str, params: dict, max_filas: int, pausa: float, pagina: int = 500) -> tuple[list, bool]:
    """Pide páginas con limit/offset hasta que se acaben. Devuelve (filas, truncado)."""
    filas, offset = [], 0
    while offset < max_filas:
        try:
            lote = get_reintentos(url, {**params, "limit": pagina, "offset": offset})
        except RechazoAPI:
            if offset == 0:
                raise
            return filas, True  # la API no deja pasar de cierto offset
        if isinstance(lote, dict):
            lote = lote.get("data") or []
        filas.extend(lote)
        if len(lote) < pagina:
            return filas, False
        offset += pagina
        if pausa:
            time.sleep(pausa)
    return filas, True


# ---------------------------------------------------------------------------
# Fuentes de datos: Polymarket real o datos inventados (--demo)
# ---------------------------------------------------------------------------

class FuentePolymarket:
    def __init__(self, args, log):
        self.a, self.log = args, log

    def mercados(self, desde: int, hasta: int) -> list[dict]:
        P = PERIODOS[self.a.periodo]
        inicios = list(range(desde, hasta, P))

        def uno(inicio):
            try:
                m = cargar_mercado(self.a.periodo, inicio)
            except Exception as e:
                self.log(f"  Error cargando {slug_para(self.a.periodo, inicio)}: {e}")
                return None
            if m is None:
                return None
            r = resolucion_oficial(m)
            m["resultado"], m["resultado_origen"] = r if r else (None, None)
            return m

        with ThreadPoolExecutor(self.a.hilos) as ex:
            return [m for m in ex.map(uno, inicios) if m]

    def operaciones(self, m: dict, solo_taker: bool) -> tuple[list, bool]:
        return paginar(f"{DATA_API}/trades",
                       {"market": m["condition_id"], "takerOnly": "true" if solo_taker else "false"},
                       self.a.max_filas, self.a.pausa)

    def actividad(self, wallet: str, desde: int, hasta: int) -> tuple[list, bool]:
        """Actividad de una wallet entre dos instantes. Si un tramo tiene demasiadas filas, lo parte en dos."""
        out, truncado, pend = [], False, [(desde, hasta)]
        while pend:
            a, b = pend.pop()
            try:
                filas, t = paginar(f"{DATA_API}/activity", {"user": wallet, "start": a, "end": b},
                                   self.a.max_filas, self.a.pausa)
            except RechazoAPI as e:
                self.log(f"  /activity rechazó {wallet[:10]}…: {e}")
                return out, True
            if t and b - a > 120:
                medio = (a + b) // 2
                pend += [(a, medio), (medio + 1, b)]
                continue
            truncado |= t
            out += filas
        return out, truncado


class FuenteDemo:
    """Genera mercados, operaciones y actividad con el mismo formato que la API, a partir de
    arquetipos de wallets. Sirve para ver el informe y probar el análisis sin conexión."""

    ARQUETIPOS = [  # (nombre, cuántas wallets, probabilidad de operar en cada ventana)
        ("dos_lados", 4, 0.85), ("split_vende", 3, 0.9), ("scalper", 5, 0.7),
        ("tardio", 5, 0.6), ("temprano", 5, 0.6), ("minorista", 70, 0.08),
    ]

    def __init__(self, args, log):
        self.a, self.log = args, log
        self.rng = random.Random(args.semilla if args.semilla is not None else 7)
        self.P = PERIODOS[args.periodo]
        self.trades: dict[str, list] = {}
        self.act: dict[str, list] = {}
        self.wallets = []
        for tipo, n, prob in self.ARQUETIPOS:
            for i in range(n):
                w = "0x" + "".join(self.rng.choice("0123456789abcdef") for _ in range(40))
                nombre = f"{tipo}-{i + 1}" if tipo != "minorista" else ("" if self.rng.random() < 0.6 else f"user{self.rng.randint(100, 9999)}")
                self.wallets.append({"w": w, "tipo": tipo, "prob": prob, "nombre": nombre,
                                     "habilidad": self.rng.uniform(-0.02, 0.05)})

    def _tx(self):
        return "0x" + "".join(self.rng.choice("0123456789abcdef") for _ in range(64))

    def mercados(self, desde: int, hasta: int) -> list[dict]:
        out = []
        for inicio in range(desde, hasta, self.P):
            m = self._ventana(inicio)
            out.append(m)
        return out

    def _ventana(self, inicio: int) -> dict:
        rng, P = self.rng, self.P
        slug = slug_para(self.a.periodo, inicio)
        cond = "0x" + "".join(rng.choice("0123456789abcdef") for _ in range(64))
        m = {"slug": slug, "titulo": f"Bitcoin Up or Down (demo) {iso(inicio)}", "inicio": inicio, "fin": inicio + P,
             "condition_id": cond, "idx_up": 0, "idx_down": 1, "token_up": "demo-up", "token_down": "demo-down",
             "fee_rate": 0.07, "resolution_source": "https://data.chain.link/streams/btc-usd", "fuente": "chainlink-spot",
             "precio_a_batir": round(rng.uniform(60000, 70000), 2), "precio_a_batir_origen": "demo"}
        # Camino del precio: diferencia frente al precio a batir, paso a paso cada segundo
        sigma = 3.5 * math.sqrt(P / 300)
        dif, camino = 0.0, []
        for s in range(P + 1):
            camino.append(dif)
            dif += rng.gauss(0, sigma / math.sqrt(P / 300))

        def p_up(trel):
            trel = max(0, min(P, int(trel)))
            resto = max(1, P - trel)
            z = camino[trel] / (sigma / math.sqrt(P / 300) * math.sqrt(resto))
            return min(0.98, max(0.02, 0.5 * (1 + math.erf(z / math.sqrt(2)))))

        m["resultado"] = "up" if camino[-1] >= 0 else "down"
        m["resultado_origen"] = "demo"
        trades = []

        def op(w, trel, lado, side, size, taker, spread=0.01):
            pu = p_up(trel)
            mid = pu if lado == "up" else 1 - pu
            px = mid + (spread if side == "BUY" else -spread) * (1 if taker else -1)
            px = round(min(0.99, max(0.01, px + rng.gauss(0, 0.005))), 2)
            size = round(size, 2)
            rec = {"proxyWallet": w["w"], "side": side, "size": size, "price": px,
                   "timestamp": int(inicio + trel), "outcome": "Up" if lado == "up" else "Down",
                   "outcomeIndex": 0 if lado == "up" else 1, "conditionId": cond, "slug": slug,
                   "transactionHash": self._tx(), "asset": "demo-" + lado, "name": w["nombre"], "pseudonym": w["nombre"],
                   "_taker": taker}
            trades.append(rec)
            self.act.setdefault(w["w"], []).append({**rec, "type": "TRADE", "usdcSize": round(size * px, 4)})
            return px

        def otro(w, trel, tipo, size):
            self.act.setdefault(w["w"], []).append({"proxyWallet": w["w"], "timestamp": int(inicio + trel), "conditionId": cond,
                                                   "type": tipo, "size": size, "usdcSize": size, "price": 0, "side": "",
                                                   "outcome": "", "outcomeIndex": None, "slug": slug,
                                                   "transactionHash": self._tx()})

        for w in self.wallets:
            if rng.random() > w["prob"]:
                continue
            t = w["tipo"]
            ganador = m["resultado"]
            if t == "dos_lados":
                # compra el lado que se abarata, poco a poco, hasta tener los dos
                tiene = {"up": 0.0, "down": 0.0}
                for trel in sorted(rng.uniform(5, P - 20) for _ in range(rng.randint(6, 14))):
                    pu = p_up(trel)
                    lado = "up" if pu < 0.5 else "down"
                    if tiene[lado] > tiene["up" if lado == "down" else "down"] + 60:
                        lado = "up" if lado == "down" else "down"
                    if min(pu, 1 - pu) < 0.47 or rng.random() < 0.3:
                        tam = rng.uniform(20, 60)
                        op(w, trel, lado, "BUY", tam, rng.random() < 0.3)
                        tiene[lado] += tam
            elif t == "split_vende":
                tam = rng.choice([200, 300, 500])
                otro(w, rng.uniform(-40, 5), "SPLIT", tam)
                quedan = {"up": float(tam), "down": float(tam)}
                for trel in sorted(rng.uniform(0, P - 10) for _ in range(rng.randint(10, 20))):
                    lado = rng.choice(["up", "down"])
                    q = min(quedan[lado], rng.uniform(10, 40))
                    if q >= 5:
                        op(w, trel, lado, "SELL", q, False, spread=0.015)
                        quedan[lado] -= q
                par = min(quedan.values())
                if par >= 5:
                    otro(w, P - 5, "MERGE", round(par, 2))
            elif t == "scalper":
                for _ in range(rng.randint(1, 4)):
                    trel = rng.uniform(10, P - 60)
                    tendencia = camino[int(trel)] - camino[max(0, int(trel) - 20)]
                    lado = "up" if tendencia > 0 else "down"
                    if rng.random() < 0.5 + w["habilidad"]:
                        pass
                    else:
                        lado = "up" if lado == "down" else "down"
                    tam = rng.uniform(30, 120)
                    op(w, trel, lado, "BUY", tam, True)
                    op(w, trel + rng.uniform(15, 50), lado, "SELL", tam, True)
            elif t == "tardio":
                trel = rng.uniform(P * 0.8, P - 8)
                pu = p_up(trel)
                if max(pu, 1 - pu) > 0.8:
                    op(w, trel, "up" if pu > 0.5 else "down", "BUY", rng.uniform(100, 400), True)
            elif t == "temprano":
                trel = rng.uniform(5, P * 0.25)
                lado = ganador if rng.random() < 0.52 + w["habilidad"] else ("up" if ganador == "down" else "down")
                tam = rng.uniform(40, 150)
                op(w, trel, lado, "BUY", tam, rng.random() < 0.5)
                if rng.random() < 0.4:
                    op(w, rng.uniform(P * 0.5, P - 15), lado, "SELL", tam, True)
            else:  # minorista
                for _ in range(rng.randint(1, 3)):
                    trel = rng.uniform(-30, P - 5)
                    op(w, trel, rng.choice(["up", "down"]), "BUY", rng.uniform(5, 50), True)
        self.trades[cond] = trades
        return m

    def operaciones(self, m: dict, solo_taker: bool) -> tuple[list, bool]:
        filas = [{k: v for k, v in r.items() if k != "_taker"} for r in self.trades.get(m["condition_id"], [])
                 if r["_taker"] or not solo_taker]
        return filas, False

    def actividad(self, wallet: str, desde: int, hasta: int) -> tuple[list, bool]:
        filas = [{k: v for k, v in r.items() if k != "_taker"} for r in self.act.get(wallet, [])
                 if desde <= r["timestamp"] <= hasta]
        return filas, False


# ---------------------------------------------------------------------------
# Normalización y contabilidad
# ---------------------------------------------------------------------------

def _f(x, defecto=0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return defecto


def lado_de(rec: dict, m: dict) -> str | None:
    try:
        oi = int(rec.get("outcomeIndex"))
    except (TypeError, ValueError):
        oi = None
    if oi is not None:
        return "up" if oi == m["idx_up"] else "down" if oi == m["idx_down"] else None
    o = str(rec.get("outcome") or "").lower()
    return o if o in ("up", "down") else None


def clave_taker(tx, wallet, lado, side, size):
    return (str(tx or "").lower(), str(wallet or "").lower(), lado, str(side or "").upper(), round(_f(size), 2))


def normalizar(rec: dict, m: dict, takers: set, hay_tx: bool) -> dict | None:
    """Convierte una fila de /trades o /activity en un evento interno. None si no afecta a la posición."""
    tipo = str(rec.get("type") or "TRADE").upper()
    t = _f(rec.get("timestamp"), None)
    if t is None:
        return None
    if t > 1e12:  # por si llega en milisegundos
        t /= 1000
    size = _f(rec.get("size"))
    if size <= 0:
        return None
    if tipo == "TRADE":
        side = str(rec.get("side") or "").upper()
        lado = lado_de(rec, m)
        if side not in ("BUY", "SELL") or not lado:
            return None
        precio = _f(rec.get("price"))
        usdc = _f(rec.get("usdcSize"), None)
        if usdc is None or usdc <= 0:
            usdc = size * precio
        taker = None
        if hay_tx and rec.get("transactionHash"):
            taker = clave_taker(rec.get("transactionHash"), rec.get("proxyWallet"), lado, side, size) in takers
        return {"t": t, "tipo": "B" if side == "BUY" else "S", "lado": lado, "precio": precio,
                "size": size, "usdc": usdc, "taker": taker}
    if tipo in ("SPLIT", "MERGE"):
        usdc = _f(rec.get("usdcSize"), None) or size
        return {"t": t, "tipo": tipo, "lado": "", "precio": 1.0, "size": size, "usdc": usdc, "taker": None}
    return None  # REDEEM, REWARD, CONVERSION…: el pago al cierre se calcula con la resolución


def contabilizar(evs: list[dict], m: dict, max_eventos: int) -> dict:
    """Resultado de una wallet en una ventana: flujos de dinero, acciones finales y ganancia."""
    acc = {"up": 0.0, "down": 0.0}
    compra = {"up": [0.0, 0.0], "down": [0.0, 0.0]}  # acciones, usdc
    venta = [0.0, 0.0]
    caja = comision = split = merge = 0.0
    primera = None
    t_compras, usdc_compras = [], []
    eventos = []
    for e in sorted(evs, key=lambda x: x["t"]):
        trel = e["t"] - m["inicio"]
        if e["tipo"] == "B":
            caja -= e["usdc"]
            acc[e["lado"]] += e["size"]
            compra[e["lado"]][0] += e["size"]
            compra[e["lado"]][1] += e["usdc"]
            primera = trel if primera is None else primera
            t_compras.append(trel)
            usdc_compras.append((e["precio"], e["usdc"]))
        elif e["tipo"] == "S":
            caja += e["usdc"]
            acc[e["lado"]] -= e["size"]
            venta[0] += e["size"]
            venta[1] += e["usdc"]
        elif e["tipo"] == "SPLIT":
            caja -= e["usdc"]
            acc["up"] += e["size"]
            acc["down"] += e["size"]
            split += e["size"]
        elif e["tipo"] == "MERGE":
            caja += e["usdc"]
            acc["up"] -= e["size"]
            acc["down"] -= e["size"]
            merge += e["size"]
        if e["tipo"] in ("B", "S") and e["taker"]:
            p = e["precio"]
            comision += e["size"] * m["fee_rate"] * p * (1 - p)
        if len(eventos) < max_eventos:
            eventos.append([round(trel, 1), e["tipo"], e["lado"], round(e["precio"], 3), round(e["size"], 2),
                            None if e["taker"] is None else int(e["taker"])])

    res = m.get("resultado")
    pago = None
    if res in ("up", "down", "empate"):
        pago = {l: 0.5 if res == "empate" else 1.0 if res == l else 0.0 for l in ("up", "down")}
    valor = sum(max(0.0, acc[l]) * pago[l] for l in acc) if pago else None
    pnl = caja + valor if valor is not None else None
    vwap = {l: compra[l][1] / compra[l][0] if compra[l][0] > 0 else None for l in compra}
    # "Dos lados" = llegó a tener el par: compró ambos y los mantuvo hasta el cierre o los deshizo con merge
    ambos = compra["up"][0] >= 5 and compra["down"][0] >= 5 and min(acc.values()) + merge >= 5
    n_ops = len(evs)
    tomado = [e for e in evs if e["tipo"] in ("B", "S")]
    con_info = [e for e in tomado if e["taker"] is not None]
    return {
        "slug": m["slug"], "inicio": m["inicio"], "resultado": res,
        "up_sh": round(compra["up"][0], 2), "up_px": round(vwap["up"], 4) if vwap["up"] else None,
        "down_sh": round(compra["down"][0], 2), "down_px": round(vwap["down"], 4) if vwap["down"] else None,
        "coste_par": round(vwap["up"] + vwap["down"], 4) if ambos else None,
        "vend_sh": round(venta[0], 2), "vend_px": round(venta[1] / venta[0], 4) if venta[0] else None,
        "split": round(split, 2), "merge": round(merge, 2),
        "fin_up": round(acc["up"], 2), "fin_down": round(acc["down"], 2),
        "compras_usdc": round(compra["up"][1] + compra["down"][1], 4), "ventas_usdc": round(venta[1], 4),
        "invertido": round(compra["up"][1] + compra["down"][1] + split, 4),
        "volumen": round(compra["up"][1] + compra["down"][1] + venta[1], 4),
        "pnl": round(pnl, 4) if pnl is not None else None,
        "comision": round(comision, 4),
        "pnl_neto": round(pnl - comision, 4) if pnl is not None else None,
        "primera_compra": round(primera, 1) if primera is not None else None,
        "t_compras": t_compras, "px_compras": usdc_compras,
        "ambos": ambos, "vendio": venta[0] >= 1, "al_cierre": max(acc.values()) >= 1,
        "inconsistente": min(acc.values()) < -0.5,
        "n_ops": n_ops,
        "taker_usdc": sum(e["usdc"] for e in con_info if e["taker"]), "info_usdc": sum(e["usdc"] for e in con_info),
        "eventos": eventos, "eventos_recortados": max(0, n_ops - max_eventos),
    }


def mediana(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 4) if xs else None


def tramo(trel: float, P: int) -> int:
    """0 = antes de empezar la ventana, 1..N_TRAMOS dentro, N_TRAMOS+1 = después."""
    if trel < 0:
        return 0
    if trel >= P:
        return N_TRAMOS + 1
    return 1 + int(trel / P * N_TRAMOS)


def agregar(wallet: str, nombre: str, fuente: str, truncado: bool, ventanas: list[dict], P: int, con_detalle: bool) -> dict:
    res = [v for v in ventanas if v["pnl"] is not None]
    n = len(ventanas)
    invertido = sum(v["invertido"] for v in ventanas)
    pnl = sum(v["pnl"] for v in res)
    com = sum(v["comision"] for v in res)
    pnl_neto = pnl - com
    compras = [(p, u) for v in ventanas for p, u in v["px_compras"]]
    usdc_compras = sum(u for _, u in compras)
    hist_t = [0.0] * (N_TRAMOS + 2)
    for v in ventanas:
        for trel, (_, u) in zip(v["t_compras"], v["px_compras"]):
            hist_t[tramo(trel, P)] += u
    hist_p = [0.0] * 10
    for p, u in compras:
        hist_p[min(9, max(0, int(p * 10)))] += u
    acciones_compradas = sum(v["up_sh"] + v["down_sh"] + v["split"] for v in ventanas)
    info = sum(v["info_usdc"] for v in ventanas)
    con_compras = [v for v in ventanas if v["up_sh"] + v["down_sh"] > 0]
    ambos = [v for v in con_compras if v["ambos"]]
    pares = [v["coste_par"] for v in ambos if v["coste_par"] is not None]
    w = {
        "wallet": wallet, "nombre": nombre, "fuente": fuente, "truncado": truncado,
        "ventanas": n, "ventanas_resueltas": len(res),
        "n_ops": sum(v["n_ops"] for v in ventanas),
        "volumen": round(sum(v["volumen"] for v in ventanas), 2),
        "invertido": round(invertido, 2),
        "pnl": round(pnl, 2), "comisiones": round(com, 2), "pnl_neto": round(pnl_neto, 2),
        "pnl_ventana": round(pnl_neto / len(res), 3) if res else None,
        "pct_ganadas": round(sum(1 for v in res if v["pnl_neto"] > 0) / len(res), 4) if res else None,
        "roi": round(pnl_neto / invertido, 4) if invertido > 0 else None,
        "seg_entrada_med": mediana([v["primera_compra"] for v in ventanas]),
        "seg_compra_med": mediana([t for v in ventanas for t in v["t_compras"]]),
        "precio_compra_medio": round(usdc_compras / sum(u / p for p, u in compras if p > 0), 4) if compras else None,
        "pct_favorito": round(sum(u for p, u in compras if p > 0.5) / usdc_compras, 4) if usdc_compras else None,
        "pct_ambos": round(len(ambos) / len(con_compras), 4) if con_compras else None,
        "coste_par_medio": mediana(pares),
        "pct_par_bajo_1": round(sum(1 for x in pares if x < 1) / len(pares), 4) if pares else None,
        "pct_vende_antes": round(sum(1 for v in ventanas if v["vendio"]) / n, 4) if n else None,
        "pct_vendido": round(sum(v["vend_sh"] + v["merge"] for v in ventanas) / acciones_compradas, 4) if acciones_compradas else None,
        "pct_al_cierre": round(sum(1 for v in ventanas if v["al_cierre"]) / n, 4) if n else None,
        "pct_taker": round(sum(v["taker_usdc"] for v in ventanas) / info, 4) if info > 0 else None,
        "ops_ventana": round(sum(v["n_ops"] for v in ventanas) / n, 2) if n else None,
        "ventanas_split": sum(1 for v in ventanas if v["split"] > 0),
        "inconsistentes": sum(1 for v in ventanas if v["inconsistente"]),
        "hist_tiempo": [round(x, 2) for x in hist_t], "hist_precio": [round(x, 2) for x in hist_p],
    }
    w["estilo"], w["etiquetas"] = clasificar(w, P)
    w["detalle"] = None
    if con_detalle:
        quitar = {"t_compras", "px_compras", "taker_usdc", "info_usdc"}
        w["detalle"] = [{k: x for k, x in v.items() if k not in quitar} for v in sorted(ventanas, key=lambda v: v["inicio"])]
    return w


ESTILOS = ["split_vende", "dos_lados", "sale_pronto", "maker", "direccional"]


def clasificar(w: dict, P: int) -> tuple[str, list[str]]:
    et = []
    split_vende = w["ventanas_split"] >= max(1, w["ventanas"] * 0.3) and (w["pct_vendido"] or 0) > 0.5
    if split_vende:
        et.append("crea pares (split) y vende")
    if w["pct_taker"] is not None:
        if w["pct_taker"] < 0.3:
            et.append("pone órdenes en el libro (maker)")
        elif w["pct_taker"] > 0.8:
            et.append("toma liquidez (taker)")
    if (w["pct_ambos"] or 0) >= 0.5:
        et.append("compra los dos lados")
    if (w["pct_vende_antes"] or 0) >= 0.5:
        et.append("vende antes del cierre")
    elif (w["pct_al_cierre"] or 0) >= 0.8:
        et.append("aguanta hasta el cierre")
    s = w["seg_entrada_med"]
    if s is not None:
        if s >= 0.8 * P:
            et.append("entra al final")
        elif s <= 0.2 * P:
            et.append("entra al principio")
    pm = w["precio_compra_medio"]
    if pm is not None:
        if pm >= 0.8:
            et.append("compra favoritos caros")
        elif pm <= 0.3:
            et.append("compra lados baratos")
    if split_vende:
        estilo = "split_vende"
    elif (w["pct_ambos"] or 0) >= 0.5:
        estilo = "dos_lados"
    elif (w["pct_vende_antes"] or 0) >= 0.5:
        estilo = "sale_pronto"
    elif w["pct_taker"] is not None and w["pct_taker"] < 0.3:
        estilo = "maker"
    else:
        estilo = "direccional"
    return estilo, et


METRICAS_COMPARACION = [
    ("pnl_ventana", "Ganancia neta por ventana", "usd"),
    ("roi", "Rentabilidad sobre lo invertido", "pct"),
    ("pct_ganadas", "Ventanas ganadas", "pct"),
    ("ops_ventana", "Operaciones por ventana", "num"),
    ("seg_entrada_med", "Segundo de la primera compra", "seg"),
    ("seg_compra_med", "Segundo típico de compra", "seg"),
    ("precio_compra_medio", "Precio medio de compra", "px"),
    ("pct_favorito", "Compras en el lado favorito (>0,50)", "pct"),
    ("pct_ambos", "Ventanas comprando los dos lados", "pct"),
    ("coste_par_medio", "Coste del par Up+Down", "px"),
    ("pct_vende_antes", "Ventanas en las que vende antes", "pct"),
    ("pct_vendido", "Acciones que vende o deshace antes del cierre", "pct"),
    ("pct_taker", "Volumen tomando liquidez (taker)", "pct"),
    ("volumen", "Volumen total (USDC)", "vol"),
]


# ---------------------------------------------------------------------------
# Análisis completo
# ---------------------------------------------------------------------------

def analizar(fuente, args, log) -> dict:
    P = PERIODOS[args.periodo]
    ahora = time.time()
    # Solo ventanas cerradas hace al menos 2 min; `hasta` es el inicio de la primera ventana que NO entra
    hasta = int((ahora - 120 - args.hasta_hace * 60 - P) // P) * P + P
    desde = hasta - int(args.horas * 3600 // P) * P
    log(f"Ventanas de {args.periodo} entre {iso(desde)} y {iso(hasta)} ({(hasta - desde) // P} ventanas)")

    mercados = fuente.mercados(desde, hasta)
    mercados.sort(key=lambda m: m["inicio"])
    por_cond = {m["condition_id"].lower(): m for m in mercados}
    log(f"{len(mercados)} mercados encontrados, {sum(1 for m in mercados if m['resultado'])} resueltos")
    if not mercados:
        sys.exit("No se encontró ningún mercado en ese intervalo.")

    # --- Fase 1: todas las operaciones de cada mercado ---
    takers: set = set()
    hay_tx = False
    crudas: dict[str, list] = {}  # conditionId -> filas de /trades (maker y taker)
    info_m: dict[str, dict] = {}
    lock = threading.Lock()

    def bajar(m):
        todas, t1 = fuente.operaciones(m, solo_taker=False)
        solo, t2 = fuente.operaciones(m, solo_taker=True)
        return m, todas, solo, t1 or t2

    hechos = 0
    with ThreadPoolExecutor(args.hilos) as ex:
        for m, todas, solo, trunc in ex.map(bajar, mercados):
            hechos += 1
            with lock:
                for r in solo:
                    lado = lado_de(r, m)
                    if r.get("transactionHash"):
                        hay_tx = True
                    takers.add(clave_taker(r.get("transactionHash"), r.get("proxyWallet"), lado, r.get("side"), r.get("size")))
                crudas[m["condition_id"].lower()] = todas or solo
                wallets_m = {str(r.get("proxyWallet") or "").lower() for r in (todas or solo)}
                info_m[m["slug"]] = {"n_operaciones": len(solo), "volumen": round(sum(_f(r.get("size")) * _f(r.get("price")) for r in solo), 2),
                                     "n_wallets": len(wallets_m - {""}), "truncado": trunc}
            if trunc:
                log(f"  {m['slug']}: más operaciones de las que deja bajar la API (sube --max-filas)")
            if hechos % 10 == 0 or hechos == len(mercados):
                log(f"  operaciones descargadas: {hechos}/{len(mercados)} mercados")

    # Eventos por wallet y mercado
    eventos: dict[str, dict[str, list]] = {}
    nombres: dict[str, str] = {}
    vistos: set = set()
    for cond, filas in crudas.items():
        m = por_cond[cond]
        for r in filas:
            w = str(r.get("proxyWallet") or "").lower()
            if not w:
                continue
            k = (r.get("transactionHash"), w, r.get("outcomeIndex"), r.get("side"), r.get("size"), r.get("price"), r.get("timestamp"))
            if k in vistos:
                continue
            vistos.add(k)
            e = normalizar(r, m, takers, hay_tx)
            if e:
                eventos.setdefault(w, {}).setdefault(cond, []).append(e)
            if r.get("name") or r.get("pseudonym"):
                nombres.setdefault(w, r.get("name") or r.get("pseudonym"))
    log(f"{len(eventos)} wallets distintas han operado")

    def resumen_rapido(w):
        vs = [contabilizar(evs, por_cond[c], 0) for c, evs in eventos[w].items()]
        return sum(v["volumen"] for v in vs), sum(v["pnl_neto"] or 0 for v in vs), len(vs)

    rapido = {w: resumen_rapido(w) for w in eventos}

    # --- Fase 2: actividad completa de las wallets más relevantes ---
    candidatas = [w for w in rapido if rapido[w][2] >= args.min_ventanas]
    por_vol = sorted(candidatas, key=lambda w: -rapido[w][0])[:args.analizar]
    por_pnl = sorted(candidatas, key=lambda w: -rapido[w][1])[:args.analizar]
    peores = sorted(candidatas, key=lambda w: rapido[w][1])[:max(5, args.analizar // 3)]
    elegidas = list(dict.fromkeys(por_vol + por_pnl + peores))
    log(f"Descargando la actividad completa de {len(elegidas)} wallets (compras, ventas, split y merge)…")
    fuente_w: dict[str, str] = {}
    trunc_w: dict[str, bool] = {}

    def bajar_act(w):
        try:
            return w, *fuente.actividad(w, desde - 3600, hasta + P + 600)
        except Exception as e:
            log(f"  Error en la actividad de {w[:10]}…: {e}")
            return w, None, False

    with ThreadPoolExecutor(args.hilos) as ex:
        for i, (w, filas, trunc) in enumerate(ex.map(bajar_act, elegidas), 1):
            if filas is None:
                continue
            nuevos: dict[str, list] = {}
            for r in filas:
                m = por_cond.get(str(r.get("conditionId") or "").lower())
                if not m:
                    continue
                e = normalizar(r, m, takers, hay_tx)
                if e:
                    nuevos.setdefault(m["condition_id"].lower(), []).append(e)
            if nuevos:
                eventos[w] = nuevos
                fuente_w[w] = "actividad"
                trunc_w[w] = trunc
            if i % 10 == 0 or i == len(elegidas):
                log(f"  actividad descargada: {i}/{len(elegidas)} wallets")

    # --- Contabilidad y métricas ---
    wallets = []
    for w, por_m in eventos.items():
        con_detalle = w in fuente_w
        vs = [contabilizar(evs, por_cond[c], args.max_eventos if con_detalle else 0) for c, evs in por_m.items()]
        wallets.append(agregar(w, nombres.get(w, ""), fuente_w.get(w, "operaciones"), trunc_w.get(w, False), vs, P, con_detalle))
    wallets.sort(key=lambda x: -x["pnl_neto"])

    # --- Comparación: las que más ganan frente a las que más pierden ---
    validas = [w for w in wallets if w["ventanas_resueltas"] >= args.min_ventanas]
    n = min(args.grupo, max(1, len(validas) // 2))
    grupos = {"ganadoras": validas[:n], "perdedoras": validas[::-1][:n], "todas": validas}
    comparacion = {"n": n, "metricas": [], "hist_tiempo": {}, "hist_precio": {}}
    for clave, etiqueta, fmt in METRICAS_COMPARACION:
        comparacion["metricas"].append({"clave": clave, "etiqueta": etiqueta, "formato": fmt,
                                        **{g: mediana([w[clave] for w in ws]) for g, ws in grupos.items()}})
    for g, ws in grupos.items():
        for h in ("hist_tiempo", "hist_precio"):
            tot = [sum(x) for x in zip(*[w[h] for w in ws])] if ws else []
            s = sum(tot)
            comparacion[h][g] = [round(x / s, 4) for x in tot] if s else []
        comparacion.setdefault("estilos", {})[g] = {e: sum(1 for w in ws if w["estilo"] == e) for e in ESTILOS}

    vol_taker = sum(i["volumen"] for i in info_m.values())
    vol_w = sorted((w["volumen"] for w in wallets), reverse=True)
    mercados_out = []
    for m in mercados:
        mercados_out.append({k: m.get(k) for k in ("slug", "titulo", "inicio", "fin", "resultado", "resultado_origen",
                                                  "precio_a_batir", "fee_rate")} | info_m.get(m["slug"], {}))
    return {
        "version": 1,
        "demo": bool(args.demo),
        "generado_utc": iso(time.time()),
        "config": {k: getattr(args, k) for k in ("periodo", "horas", "hasta_hace", "analizar", "min_ventanas", "grupo", "max_filas")},
        "desde": desde, "hasta": hasta, "periodo_seg": P, "n_tramos": N_TRAMOS,
        "resumen": {
            "mercados": len(mercados), "resueltos": sum(1 for m in mercados if m["resultado"]),
            "wallets": len(wallets), "analizadas": len(fuente_w), "volumen_taker": round(vol_taker, 2),
            "pct_top10": round(sum(vol_w[:10]) / sum(vol_w), 4) if sum(vol_w) else None,
            "validas": len(validas),
            "rentables": sum(1 for w in validas if w["pnl_neto"] > 0),
            "mercados_truncados": sum(1 for i in info_m.values() if i.get("truncado")),
            "info_taker": hay_tx,
        },
        "estilos": ESTILOS,
        "comparacion": comparacion,
        "mercados": mercados_out,
        "wallets": wallets,
    }


def resumen_texto(d: dict) -> str:
    r = d["resumen"]
    lin = [f"Mercados: {r['mercados']} ({r['resueltos']} resueltos) · wallets: {r['wallets']} · "
           f"analizadas a fondo: {r['analizadas']} · volumen taker: {r['volumen_taker']:,.0f} USDC",
           f"Wallets con al menos {d['config']['min_ventanas']} ventanas: {r['validas']}, rentables: {r['rentables']}", "",
           f"{'wallet':<14}{'nombre':<18}{'estilo':<13}{'vent.':>6}{'volumen':>11}{'P&L neto':>10}{'por vent.':>10}  etiquetas"]
    validas = [w for w in d["wallets"] if w["ventanas_resueltas"] >= d["config"]["min_ventanas"]]
    filas = validas[:15] + [None] + validas[-15:] if len(validas) > 30 else validas
    for w in filas:
        if w is None:
            lin.append("   …")
            continue
        lin.append(f"{w['wallet'][:12]:<14}{(w['nombre'] or '')[:16]:<18}{w['estilo']:<13}{w['ventanas']:>6}"
                   f"{w['volumen']:>11,.0f}{w['pnl_neto']:>+10.2f}{(w['pnl_ventana'] or 0):>+10.2f}  {', '.join(w['etiquetas'])}")
    lin += ["", "Mediana de cada grupo:  métrica | ganadoras | perdedoras | todas"]
    for x in d["comparacion"]["metricas"]:
        lin.append(f"  {x['etiqueta']:<48}{str(x['ganadoras']):>10}{str(x['perdedoras']):>12}{str(x['todas']):>10}")
    return "\n".join(lin)


def main():
    ap = argparse.ArgumentParser(description="Analiza qué wallets ganan en Polymarket BTC Up/Down y cómo operan.")
    ap.add_argument("--horas", type=float, default=6, help="horas de ventanas cerradas a analizar (def. 6)")
    ap.add_argument("--hasta-hace", type=float, default=0, help="terminar hace N minutos (def. 0 = lo más reciente)")
    ap.add_argument("--periodo", choices=list(PERIODOS), default="5m", help="mercados de 5m o 15m (def. 5m)")
    ap.add_argument("--analizar", type=int, default=25, help="wallets a analizar a fondo por volumen y por ganancia (def. 25)")
    ap.add_argument("--min-ventanas", type=int, default=3, help="ventanas mínimas para entrar en rankings (def. 3)")
    ap.add_argument("--grupo", type=int, default=10, help="tamaño de los grupos ganadoras/perdedoras (def. 10)")
    ap.add_argument("--max-filas", type=int, default=5000, help="filas máximas por consulta paginada (def. 5000)")
    ap.add_argument("--max-eventos", type=int, default=300, help="operaciones guardadas por wallet y ventana en el informe (def. 300)")
    ap.add_argument("--hilos", type=int, default=4, help="descargas en paralelo (def. 4)")
    ap.add_argument("--pausa", type=float, default=0.1, help="segundos entre páginas (def. 0.1)")
    ap.add_argument("--demo", action="store_true", help="usa datos inventados en lugar de Polymarket")
    ap.add_argument("--semilla", type=int, default=None)
    ap.add_argument("--informe", metavar="DATOS_JSON", help="solo regenera informe.html a partir de un datos.json")
    args = ap.parse_args()

    from informe_wallets import generar_informe

    if args.informe:
        ruta = Path(args.informe)
        generar_informe(json.loads(ruta.read_text(encoding="utf-8")), ruta.with_name("informe.html"))
        print(f"Informe regenerado: {ruta.with_name('informe.html')}")
        return

    carpeta = Path(f"resultados_wallets_{'demo_' if args.demo else ''}{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    carpeta.mkdir()
    log_f = open(carpeta / "log.txt", "w", encoding="utf-8")

    def log(msg: str):
        linea = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        print(linea, flush=True)
        log_f.write(linea + "\n")
        log_f.flush()

    fuente = FuenteDemo(args, log) if args.demo else FuentePolymarket(args, log)
    try:
        datos = analizar(fuente, args, log)
    except KeyboardInterrupt:
        log("Interrumpido.")
        return
    (carpeta / "datos.json").write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    generar_informe(datos, carpeta / "informe.html")
    texto = resumen_texto(datos)
    (carpeta / "resumen.txt").write_text(texto + "\n", encoding="utf-8")
    log("\n" + texto)
    log(f"Abre ./{carpeta}/informe.html en el navegador para ver los resultados.")
    log_f.close()


if __name__ == "__main__":
    main()

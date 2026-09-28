#!/usr/bin/env python3
"""
Simulador (paper trading) de Jev sobre los mercados "Bitcoin Up or Down" de Polymarket.
Compra Y VENDE dentro de cada ventana. NO envía ninguna orden real.

Cada --cada segundos (10 por defecto):
  1. Lee el precio de BTC de Chainlink que usa Polymarket para resolver (stream público RTDS).
  2. Lee el libro de órdenes de Up y Down y las operaciones reales de los últimos 30/60 s
     (quién compra y quién vende de forma agresiva).
  3. Le pasa todo a Jev, junto con la posición que tenemos abierta, y Jev decide:
     comprar Up, comprar Down, vender lo que tenemos o no hacer nada.
  4. Simula las compras al precio de venta (ask) y las ventas al precio de compra (bid) del libro real,
     con comisión. Lo que no se vende antes del final se liquida con la resolución oficial de Polymarket.
  5. Genera un informe HTML con precio, libros, flujo de órdenes, decisiones, compras/ventas y resultado.

Estrategias (una posición abierta como máximo por estrategia):
  - jev_eleccion: sigue la respuesta de Jev (buy_up / buy_down / sell / hold) si su confianza supera un umbral
  - jev_ventaja:  compra si la probabilidad de Jev supera el ask; vende si el bid supera su probabilidad
  - flujo:        sin Jev. Si los compradores empujan un lado, compra ese lado; si la presión se da la vuelta, vende
  - favorito:     compra una vez por ventana el lado favorito del mercado y espera al cierre
  - moneda:       compra una vez por ventana un lado al azar y espera al cierre

Uso:
  pip install requests websocket-client
  export TYPESAFE_API_KEY="tu_clave"             (Windows PowerShell: $env:TYPESAFE_API_KEY="tu_clave")
  python simulador.py                             # 60 min, mercados de 5 min, decisión cada 10 s
  python simulador.py --sin-jev --minutos 10      # prueba el flujo sin clave de Jev
  python simulador.py --informe resultados_X/datos.json   # regenera solo el HTML
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
DATA_API = "https://data-api.polymarket.com"
RTDS = "wss://ws-live-data.polymarket.com"
JEV_URL = "https://api.typesafe.ai/v1/systemone"
JEV_MODEL = "jev-latest"

PERIODOS = {"5m": 300, "15m": 900}
ESTRATEGIAS = ["jev_eleccion", "jev_ventaja", "flujo", "favorito", "moneda"]

# Temas del stream RTDS de Polymarket -> fuente de precio Chainlink
TEMAS_RTDS = {
    "crypto_prices_chainlink": "chainlink-spot",
    "crypto_prices_twap_thirty": "chainlink-twap-30s",
    "crypto_prices_twap_sixty": "chainlink-twap-60s",
}

HTTP = requests.Session()
HTTP.headers.update({
    "User-Agent": "Mozilla/5.0 (paper-trading research script)",
    "Accept": "application/json",
})


def ahora() -> float:
    return time.time()


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def get_json(url: str, params: dict | None = None, timeout: float = 10.0):
    r = HTTP.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def post_json(url: str, body, timeout: float = 10.0):
    r = HTTP.post(url, json=body, timeout=timeout)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# Precio de Chainlink (el mismo que usa Polymarket), vía RTDS
# ---------------------------------------------------------------------------

class FeedChainlink:
    """Escucha wss://ws-live-data.polymarket.com (sin autenticación) y guarda cada observación
    de Chainlink BTC/USD por fuente: spot, TWAP 30 s y TWAP 60 s. Marca de tiempo en ms."""

    def __init__(self, log):
        self.log = log
        self.ticks: dict[str, dict[int, float]] = {s: {} for s in TEMAS_RTDS.values()}
        self.lock = threading.Lock()
        self.parar = threading.Event()
        self.ws = None
        self.ultimo_msg = 0.0

    # -- procesamiento de mensajes (separado para poder probarlo) --
    def ingerir(self, msg: dict):
        fuente = TEMAS_RTDS.get(msg.get("topic"))
        payload = msg.get("payload")
        if not fuente or not isinstance(payload, dict) or payload.get("symbol") != "btc/usd":
            return
        entradas = payload["data"] if isinstance(payload.get("data"), list) else [payload]
        with self.lock:
            for e in entradas:
                try:
                    ts, val = int(float(e["timestamp"])), float(e["value"])
                except (KeyError, TypeError, ValueError):
                    continue
                if val > 0:
                    self.ticks[fuente][ts] = val

    # -- consultas --
    def ultimo(self, fuente: str) -> tuple[int, float] | None:
        with self.lock:
            d = self.ticks[fuente]
            if not d:
                return None
            ts = max(d)
            return ts, d[ts]

    def exacto(self, fuente: str, ts_ms: int) -> float | None:
        with self.lock:
            return self.ticks[fuente].get(ts_ms)

    def hasta(self, fuente: str, ts_ms: int) -> tuple[int, float] | None:
        """Última observación con marca de tiempo <= ts_ms."""
        with self.lock:
            cand = [t for t in self.ticks[fuente] if t <= ts_ms]
            if not cand:
                return None
            t = max(cand)
            return t, self.ticks[fuente][t]

    def serie(self, fuente: str, desde_ms: int, hasta_ms: int, paso_ms: int = 0) -> list[tuple[int, float]]:
        with self.lock:
            pts = sorted((t, v) for t, v in self.ticks[fuente].items() if desde_ms <= t <= hasta_ms)
        if paso_ms <= 0 or not pts:
            return pts
        out, siguiente = [], pts[0][0]
        for t, v in pts:
            if t >= siguiente:
                out.append((t, v))
                siguiente = t + paso_ms
        if out[-1] != pts[-1]:
            out.append(pts[-1])
        return out

    # -- conexión --
    def iniciar(self):
        try:
            import websocket  # pip install websocket-client
        except ImportError:
            sys.exit("Falta la librería websocket-client: pip install websocket-client")

        def on_open(ws):
            subs = [{"topic": t, "type": "*" if t == "crypto_prices_chainlink" else "update",
                     "filters": json.dumps({"symbol": "btc/usd"})} for t in TEMAS_RTDS]
            ws.send(json.dumps({"action": "subscribe", "subscriptions": subs}))
            self.log("Conectado al stream de Chainlink de Polymarket (RTDS).")

        def on_message(ws, texto):
            self.ultimo_msg = ahora()
            try:
                self.ingerir(json.loads(texto))
            except (ValueError, TypeError):
                pass  # RTDS también manda "PONG"

        def on_error(ws, err):
            self.log(f"RTDS error: {err}")

        def bucle():
            espera = 1
            while not self.parar.is_set():
                self.ws = websocket.WebSocketApp(RTDS, on_open=on_open, on_message=on_message, on_error=on_error)
                self.ws.run_forever()
                if self.parar.is_set():
                    break
                self.log(f"RTDS desconectado, reintento en {espera} s")
                time.sleep(espera)
                espera = min(30, espera * 2)

        def latido():
            # La documentación pide mandar el texto PING cada 5 s
            while not self.parar.wait(5):
                try:
                    if self.ws and self.ws.sock and self.ws.sock.connected:
                        self.ws.send("PING")
                        if self.ultimo_msg and ahora() - self.ultimo_msg > 20:
                            self.ws.close()
                except Exception:
                    pass

        threading.Thread(target=bucle, daemon=True).start()
        threading.Thread(target=latido, daemon=True).start()

    def detener(self):
        self.parar.set()
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass


def fuente_de(resolution_source: str) -> str | None:
    """Qué precio de Chainlink usa el mercado según su resolutionSource."""
    if "data.chain.link" not in (resolution_source or ""):
        return None
    ruta = resolution_source.rstrip("/")
    if re.search(r"/btc-usd-twap-60s-streams$", ruta):
        return "chainlink-twap-60s"
    if re.search(r"/btc-usd-twap-30s-streams$", ruta):
        return "chainlink-twap-30s"
    if re.search(r"/btc-usd(-streams)?$", ruta):
        return "chainlink-spot"
    return None


# ---------------------------------------------------------------------------
# Polymarket
# ---------------------------------------------------------------------------

def slug_para(periodo: str, inicio: int) -> str:
    return f"btc-updown-{periodo}-{inicio}"


def cargar_mercado(periodo: str, inicio: int) -> dict | None:
    slug = slug_para(periodo, inicio)
    try:
        ev = get_json(f"{GAMMA}/events/slug/{slug}")
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return None
        raise
    mercados = ev.get("markets") or []
    m = next((x for x in mercados if x.get("slug") == slug), mercados[0] if mercados else None)
    if not m:
        return None
    outcomes = [o.lower() for o in json.loads(m["outcomes"])]
    tokens = json.loads(m["clobTokenIds"])
    res_src = m.get("resolutionSource") or ev.get("resolutionSource") or ""
    fee = 0.0
    if m.get("feesEnabled") is not False and isinstance(m.get("feeSchedule"), dict):
        fee = float(m["feeSchedule"].get("rate", 0.0))
    meta = ev.get("eventMetadata") if isinstance(ev.get("eventMetadata"), dict) else {}
    ptb = meta.get("priceToBeat")
    try:
        ptb = float(ptb) if ptb not in (None, "") else None
    except (TypeError, ValueError):
        ptb = None
    return {
        "slug": slug,
        "titulo": m.get("question") or ev.get("title") or slug,
        "inicio": inicio,
        "fin": inicio + PERIODOS[periodo],
        "condition_id": m.get("conditionId", ""),
        "idx_up": outcomes.index("up"),
        "idx_down": outcomes.index("down"),
        "token_up": tokens[outcomes.index("up")],
        "token_down": tokens[outcomes.index("down")],
        "fee_rate": fee,
        "resolution_source": res_src,
        "fuente": fuente_de(res_src),
        "precio_a_batir": ptb,
        "precio_a_batir_origen": "polymarket (priceToBeat)" if ptb else None,
        "precio_final": None,
        "resultado": None,
        "resultado_origen": None,
    }


def _niveles(xs, desc: bool):
    return sorted(((float(x["price"]), float(x["size"])) for x in xs), key=lambda p: -p[0] if desc else p[0])


def libros(token_up: str, token_down: str) -> dict:
    """Libros de órdenes de Up y Down. bids = órdenes de compra (mejor primero), asks = órdenes de venta."""
    try:
        data = post_json(f"{CLOB}/books", [{"token_id": token_up}, {"token_id": token_down}])
        por_id = {b.get("asset_id"): b for b in data}
        bu, bd = por_id[token_up], por_id[token_down]
    except Exception:
        bu = get_json(f"{CLOB}/book", {"token_id": token_up})
        bd = get_json(f"{CLOB}/book", {"token_id": token_down})
    return {
        "up": {"bids": _niveles(bu.get("bids", []), True), "asks": _niveles(bu.get("asks", []), False)},
        "down": {"bids": _niveles(bd.get("bids", []), True), "asks": _niveles(bd.get("asks", []), False)},
    }


def resumen_libro(lb: dict) -> dict:
    bb = lb["bids"][0][0] if lb["bids"] else None
    ba = lb["asks"][0][0] if lb["asks"] else None
    return {
        "best_bid": bb,
        "best_ask": ba,
        "mid": round((bb + ba) / 2, 4) if bb is not None and ba is not None else None,
        "bid_shares_top5": round(sum(s for _, s in lb["bids"][:5]), 1),
        "ask_shares_top5": round(sum(s for _, s in lb["asks"][:5]), 1),
    }


def simular_compra(asks: list[tuple[float, float]], usdc: float, fee_rate: float):
    """Recorre las órdenes de venta comprando hasta gastar `usdc`. Devuelve (acciones, precio_medio, comision) o None."""
    restante, acciones, coste = usdc, 0.0, 0.0
    for precio, tam in asks:
        if precio >= 0.99:
            break
        puedo = min(tam, restante / precio)
        acciones += puedo
        coste += puedo * precio
        restante -= puedo * precio
        if restante <= 1e-6:
            break
    if acciones < 5 or restante > 0.01 * usdc:  # mínimo de 5 acciones en Polymarket / sin liquidez
        return None
    p = coste / acciones
    comision = acciones * fee_rate * p * (1 - p)  # comisión taker crypto_fees_v2
    return acciones, p, comision


def resolucion_oficial(m: dict) -> tuple[str, str] | None:
    """('up'|'down'|'empate', origen) cuando Polymarket ya ha resuelto."""
    try:
        data = get_json(f"{DATA_API}/v2/resolutions", {"condition": m["condition_id"]})
        for row in data.get("data", []):
            if (row.get("condition_id") or "").lower() == m["condition_id"].lower() and row.get("status") == "resolved":
                p = row.get("payouts")
                if isinstance(p, list) and len(p) == 2 and sum(p) == 1_000_000:
                    if p[0] == p[1]:
                        return "empate", "polymarket (resolución oficial)"
                    gan = 0 if p[0] > p[1] else 1
                    return ("up" if gan == m["idx_up"] else "down"), "polymarket (resolución oficial)"
    except Exception:
        pass
    try:  # respaldo: precios finales en Gamma
        ev = get_json(f"{GAMMA}/events/slug/{m['slug']}")
        mk = next((x for x in ev.get("markets", []) if x.get("slug") == m["slug"]), None)
        if mk and mk.get("closed"):
            precios = [float(x) for x in json.loads(mk["outcomePrices"])]
            if max(precios) >= 0.99:
                gan = precios.index(max(precios))
                return ("up" if gan == m["idx_up"] else "down"), "polymarket (gamma)"
    except Exception:
        pass
    return None




def simular_venta(bids: list[tuple[float, float]], acciones: float, fee_rate: float):
    """Vende `acciones` recorriendo las órdenes de compra. Devuelve (precio_medio, ingreso_bruto, comision) o None."""
    restante, ingreso = acciones, 0.0
    for precio, tam in bids:
        if precio <= 0.01:
            break
        v = min(tam, restante)
        ingreso += v * precio
        restante -= v
        if restante <= 1e-9:
            break
    if restante > 1e-6:  # no hay compradores suficientes: no se puede vender todo
        return None
    p = ingreso / acciones
    return p, ingreso, acciones * fee_rate * p * (1 - p)


def flujo_operaciones(m: dict, t: float) -> dict:
    """Quién está comprando y quién vendiendo: operaciones reales del mercado en los últimos 30 y 60 s.
    `side` es el lado del que toma liquidez (BUY = compró agresivamente, SELL = vendió agresivamente)."""
    try:
        trades = get_json(f"{DATA_API}/trades", {"market": m["condition_id"], "limit": 500, "takerOnly": "true"})
    except Exception:
        return {"disponible": False}
    out = {"disponible": True}
    for ventana in (30, 60):
        d = {"up": {"taker_buy_shares": 0.0, "taker_sell_shares": 0.0, "trades": 0},
             "down": {"taker_buy_shares": 0.0, "taker_sell_shares": 0.0, "trades": 0}}
        for tr in trades:
            try:
                ts, lado = int(tr["timestamp"]), str(tr.get("outcome", "")).lower()
                size, side = float(tr["size"]), str(tr["side"]).upper()
            except (KeyError, TypeError, ValueError):
                continue
            if lado not in d or ts < t - ventana or ts > t + 2:
                continue
            d[lado]["taker_buy_shares" if side == "BUY" else "taker_sell_shares"] += size
            d[lado]["trades"] += 1
        # Presión hacia Up: comprar Up o vender Down empujan a Up; lo contrario empuja a Down
        pro_up = d["up"]["taker_buy_shares"] + d["down"]["taker_sell_shares"]
        pro_down = d["down"]["taker_buy_shares"] + d["up"]["taker_sell_shares"]
        total = pro_up + pro_down
        for lado in ("up", "down"):
            for k in ("taker_buy_shares", "taker_sell_shares"):
                d[lado][k] = round(d[lado][k], 1)
        d["pressure_toward_up"] = round((pro_up - pro_down) / total, 3) if total > 0 else 0.0
        d["total_shares"] = round(total, 1)
        out[f"last_{ventana}s"] = d
    return out


# ---------------------------------------------------------------------------
# Jev
# ---------------------------------------------------------------------------

PREGUNTAS_JEV = {
    "accion": {
        "type": "choice",
        "instructions": (
            "You manage a paper-trading position in a Polymarket binary market that can be bought and sold "
            "at any time before it closes. Up pays $1 per share if the Chainlink BTC/USD reference price at the "
            "end of the window is >= price_to_beat; otherwise Down pays $1. Buying costs the side's best_ask, "
            "selling receives its best_bid, both minus a small taker fee. Use the reference price vs "
            "price_to_beat, time remaining, order flow (who is aggressively buying or selling) and the order "
            "books. What should we do right now with our_position?"
        ),
        "criteria": {
            "buy_up": "We hold nothing and buying Up now at its ask has positive expected value (buyers are pushing Up and/or the price favors Up)",
            "buy_down": "We hold nothing and buying Down now at its ask has positive expected value (buyers are pushing Down and/or the price favors Down)",
            "sell": "We hold a position and should sell it now at its bid: the flow or price turned against it, or the bid already pays more than it is worth",
            "hold": "Do nothing: keep the current position, or stay out if there is no clear edge",
        },
    },
    "up_gana": {
        "type": "noul",
        "instructions": "The Chainlink BTC/USD reference price at the end of this window will be greater than or equal to price_to_beat.",
    },
}


def preguntar_jev(estado: dict, api_key: str) -> dict:
    t0 = ahora()
    r = HTTP.post(
        JEV_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": JEV_MODEL, "state": estado, "questions": PREGUNTAS_JEV},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    a = data["answers"]
    return {
        "accion": a["accion"]["choice"],
        "accion_conf": a["accion"].get("confidence"),
        "accion_probs": a["accion"].get("probabilities"),
        "p_up": a["up_gana"]["noul"],
        "latencia_ms": round((ahora() - t0) * 1000),
        "modelo": data.get("model"),
    }


def heuristica_sin_jev(estado: dict) -> dict:
    """Sustituto simple de Jev para probar el flujo sin clave: precio vs precio a batir + presión de órdenes."""
    cambio = estado["change_vs_price_to_beat_pct"]
    presion = (estado["order_flow"].get("last_30s") or {}).get("pressure_toward_up", 0.0)
    p_up = 1 / (1 + math.exp(-(cambio * 40 + presion * 1.5)))
    pos = estado["our_position"]["side"]
    if pos is None:
        accion = "buy_up" if p_up > 0.62 else "buy_down" if p_up < 0.38 else "hold"
    else:
        p_mio = p_up if pos == "up" else 1 - p_up
        accion = "sell" if p_mio < 0.45 else "hold"
    return {"accion": accion, "accion_conf": round(abs(p_up - 0.5) * 2, 4), "accion_probs": None,
            "p_up": p_up, "latencia_ms": 0, "modelo": "heurística"}


# ---------------------------------------------------------------------------
# Simulación
# ---------------------------------------------------------------------------

class Simulador:
    def __init__(self, args, log):
        self.a = args
        self.log = log
        self.P = PERIODOS[args.periodo]
        self.api_key = None if args.sin_jev else os.environ.get("TYPESAFE_API_KEY")
        self.rng = random.Random(args.semilla)
        self.feed = FeedChainlink(log)
        self.ventanas: dict[str, dict] = {}
        self.decisiones: list[dict] = []
        self.posiciones: list[dict] = []
        self.abiertas: dict[str, dict] = {}          # estrategia -> posición abierta en la ventana actual
        self.entradas_ventana: dict[tuple[str, str], int] = {}  # (estrategia, slug) -> nº de entradas

    # ---------- mercado ----------
    def mercado(self, inicio: int) -> dict | None:
        slug = slug_para(self.a.periodo, inicio)
        m = self.ventanas.get(slug)
        if m is None or m["precio_a_batir"] is None:
            nuevo = cargar_mercado(self.a.periodo, inicio)
            if nuevo is None:
                return m
            if m is not None:
                nuevo["precio_a_batir"] = nuevo["precio_a_batir"] or m["precio_a_batir"]
                nuevo["precio_a_batir_origen"] = nuevo["precio_a_batir_origen"] or m["precio_a_batir_origen"]
            m = nuevo
            self.ventanas[slug] = m
        if m["precio_a_batir"] is None and m["fuente"]:
            v = self.feed.exacto(m["fuente"], m["inicio"] * 1000)
            if v:
                m["precio_a_batir"], m["precio_a_batir_origen"] = v, "chainlink RTDS (tick exacto de apertura)"
        return m

    # ---------- operaciones ----------
    def comprar(self, est: str, m: dict, lado: str, lb: dict, t: float, motivo: str, dec: dict, extra=None) -> bool:
        if est in self.abiertas or m["fin"] - t < self.a.sin_entradas_final:
            return False
        if self.entradas_ventana.get((est, m["slug"]), 0) >= self.a.max_entradas:
            return False
        fill = simular_compra(lb[lado]["asks"], self.a.stake, m["fee_rate"])
        if fill is None:
            return False
        acciones, p, fee = fill
        pos = {"id": len(self.posiciones), "estrategia": est, "slug": m["slug"], "lado": lado,
               "t_compra": t, "seg_restantes_compra": int(m["fin"] - t), "precio_compra": round(p, 4),
               "acciones": round(acciones, 4), "coste": round(acciones * p, 4), "comision_compra": round(fee, 4),
               "motivo_compra": motivo, "t_venta": None, "precio_venta": None, "ingreso": None,
               "comision_venta": 0.0, "motivo_venta": None, "cierre": None, "resultado": None, "pnl": None,
               **(extra or {})}
        self.posiciones.append(pos)
        self.abiertas[est] = pos
        self.entradas_ventana[(est, m["slug"])] = self.entradas_ventana.get((est, m["slug"]), 0) + 1
        dec["acciones"].append({"estrategia": est, "tipo": "compra", "lado": lado, "precio": pos["precio_compra"], "pos": pos["id"]})
        return True

    def vender(self, est: str, m: dict, lb: dict, t: float, motivo: str, dec: dict) -> bool:
        pos = self.abiertas.get(est)
        if not pos or pos["slug"] != m["slug"]:
            return False
        v = simular_venta(lb[pos["lado"]]["bids"], pos["acciones"], m["fee_rate"])
        if v is None:
            return False
        p, ingreso, fee = v
        pos.update({"t_venta": t, "seg_restantes_venta": int(m["fin"] - t), "precio_venta": round(p, 4),
                    "ingreso": round(ingreso, 4), "comision_venta": round(fee, 4), "motivo_venta": motivo,
                    "cierre": "vendida"})
        pos["pnl"] = round(ingreso - fee - pos["coste"] - pos["comision_compra"], 4)
        del self.abiertas[est]
        dec["acciones"].append({"estrategia": est, "tipo": "venta", "lado": pos["lado"], "precio": pos["precio_venta"], "pos": pos["id"]})
        return True

    def pasar_a_cierre(self, slug_actual: str):
        """Las posiciones de ventanas anteriores que no se vendieron se quedan hasta la resolución."""
        for est, pos in list(self.abiertas.items()):
            if pos["slug"] != slug_actual:
                pos["cierre"] = "al cierre"
                del self.abiertas[est]

    # ---------- decisión ----------
    def decidir(self, m: dict):
        t = ahora()
        if not m["fuente"]:
            self.log(f"  Fuente de resolución desconocida ({m['resolution_source']}), salto")
            return
        if m["precio_a_batir"] is None:
            self.log("  Aún no tengo el precio a batir de esta ventana, salto")
            return
        ref = self.feed.hasta(m["fuente"], int(t * 1000))
        spot = self.feed.hasta("chainlink-spot", int(t * 1000))
        if not ref or t * 1000 - ref[0] > 15000:
            self.log("  Precio de Chainlink desactualizado, salto")
            return
        lb = libros(m["token_up"], m["token_down"])
        ru, rd = resumen_libro(lb["up"]), resumen_libro(lb["down"])
        flujo = flujo_operaciones(m, t)
        serie = self.feed.serie(m["fuente"], int((t - 120) * 1000), int(t * 1000), 10000)
        ptb, precio = m["precio_a_batir"], ref[1]

        pj = self.abiertas.get("jev_eleccion")
        mi_pos = {"side": None}
        if pj:
            bid = (ru if pj["lado"] == "up" else rd)["best_bid"]
            mi_pos = {"side": pj["lado"], "shares": pj["acciones"], "entry_price": pj["precio_compra"],
                      "current_best_bid": bid,
                      "unrealized_pnl_usdc": round((bid or 0) * pj["acciones"] - pj["coste"], 2),
                      "seconds_held": int(t - pj["t_compra"])}

        def imbalance(r):
            tot = r["bid_shares_top5"] + r["ask_shares_top5"]
            return round((r["bid_shares_top5"] - r["ask_shares_top5"]) / tot, 3) if tot else 0.0

        estado = {
            "market": f"Polymarket 'Bitcoin Up or Down' {self.a.periodo} window",
            "rule": "Up wins if the Chainlink BTC/USD reference at window end >= price_to_beat; otherwise Down wins. Winner pays $1 per share. Shares can be sold before the end at the best bid.",
            "reference_price_type": m["fuente"],
            "seconds_elapsed": int(t - m["inicio"]),
            "seconds_remaining": int(m["fin"] - t),
            "price_to_beat": round(ptb, 2),
            "reference_price_now": round(precio, 2),
            "change_vs_price_to_beat_usd": round(precio - ptb, 2),
            "change_vs_price_to_beat_pct": round((precio / ptb - 1) * 100, 4),
            "chainlink_spot_now": round(spot[1], 2) if spot else None,
            "reference_price_last_2min_every_10s_oldest_first": [round(v, 2) for _, v in serie],
            "polymarket_up_side": ru | {"book_imbalance_bids_minus_asks": imbalance(ru)},
            "polymarket_down_side": rd | {"book_imbalance_bids_minus_asks": imbalance(rd)},
            "order_flow": flujo,
            "our_position": mi_pos,
            "taker_fee_rate": m["fee_rate"],
        }
        try:
            j = preguntar_jev(estado, self.api_key) if self.api_key else heuristica_sin_jev(estado)
        except Exception as e:
            self.log(f"  Error llamando a Jev: {e}")
            j = None

        dec = {"id": len(self.decisiones), "slug": m["slug"], "t": t, "hora_utc": iso(t),
               "seg_restantes": int(m["fin"] - t), "precio_ref": precio, "precio_a_batir": ptb,
               "spot": spot[1] if spot else None,
               "libro_up": {"bids": lb["up"]["bids"][:8], "asks": lb["up"]["asks"][:8]},
               "libro_down": {"bids": lb["down"]["bids"][:8], "asks": lb["down"]["asks"][:8]},
               "resumen_up": ru, "resumen_down": rd, "flujo": flujo, "jev": j, "acciones": []}
        a = self.a

        # --- Referencias que compran una vez por ventana y esperan al cierre ---
        if (("moneda", m["slug"]) not in self.entradas_ventana):
            self.comprar("moneda", m, self.rng.choice(["up", "down"]), lb, t, "al azar", dec)
        if (("favorito", m["slug"]) not in self.entradas_ventana) and ru["mid"] is not None and rd["mid"] is not None:
            self.comprar("favorito", m, "up" if ru["mid"] >= rd["mid"] else "down", lb, t, "lado favorito del mercado", dec)

        # --- Flujo: si todos compran, compra; si todos venden, vende (sin Jev) ---
        f30 = flujo.get("last_30s") if flujo.get("disponible") else None
        if f30 and f30["total_shares"] >= a.min_volumen:
            pr = f30["pressure_toward_up"]
            pos = self.abiertas.get("flujo")
            if pos:
                en_contra = pr < -a.umbral_flujo if pos["lado"] == "up" else pr > a.umbral_flujo
                if en_contra:
                    self.vender("flujo", m, lb, t, f"presión en contra ({pr:+.0%})", dec)
            elif pr > a.umbral_flujo:
                self.comprar("flujo", m, "up", lb, t, f"compradores empujan Up ({pr:+.0%})", dec)
            elif pr < -a.umbral_flujo:
                self.comprar("flujo", m, "down", lb, t, f"compradores empujan Down ({pr:+.0%})", dec)

        if j:
            extra = {"p_up_jev": round(j["p_up"], 4), "conf_jev": j["accion_conf"]}
            conf = j["accion_conf"] or 0
            # --- Jev · elección: sigue su respuesta Choice ---
            pos = self.abiertas.get("jev_eleccion")
            if conf >= a.umbral_conf:
                if pos and (j["accion"] == "sell" or j["accion"] == f"buy_{'down' if pos['lado'] == 'up' else 'up'}"):
                    self.vender("jev_eleccion", m, lb, t, f"Jev: {j['accion']} ({conf:.0%})", dec)
                elif not pos and j["accion"] in ("buy_up", "buy_down"):
                    self.comprar("jev_eleccion", m, j["accion"].split("_")[1], lb, t, f"Jev: {j['accion']} ({conf:.0%})", dec, extra)
            # --- Jev · ventaja: su probabilidad frente a los precios ---
            p_up = j["p_up"]
            pos = self.abiertas.get("jev_ventaja")
            if pos:
                p_mio = p_up if pos["lado"] == "up" else 1 - p_up
                bid = (ru if pos["lado"] == "up" else rd)["best_bid"]
                if bid is not None and bid > p_mio + a.margen_salida:
                    self.vender("jev_ventaja", m, lb, t, f"bid {bid:.2f} > valor Jev {p_mio:.2f}", dec)
            else:
                au, ad = ru["best_ask"], rd["best_ask"]
                if au is not None and p_up - au > a.margen:
                    self.comprar("jev_ventaja", m, "up", lb, t, f"valor Jev {p_up:.2f} > ask {au:.2f}", dec, extra)
                elif ad is not None and (1 - p_up) - ad > a.margen:
                    self.comprar("jev_ventaja", m, "down", lb, t, f"valor Jev {1 - p_up:.2f} > ask {ad:.2f}", dec, extra)

        acc = ", ".join(f"{x['estrategia']} {x['tipo']} {x['lado']}@{x['precio']:.2f}" for x in dec["acciones"]) or "sin cambios"
        pr = f"{f30['pressure_toward_up']:+.0%}" if f30 else "n/d"
        jt = f"Jev {j['accion']} ({j['accion_conf']}) P(up)={j['p_up']:.2f} {j['latencia_ms']}ms" if j else "Jev error"
        self.log(f"  {int(m['fin'] - t):>3}s · ref {precio:,.2f} vs {ptb:,.2f} · presión {pr} · {jt} · {acc}")
        self.decisiones.append(dec)

    # ---------- resolución ----------
    def cerrar_ventana(self, m: dict, forzar_estimacion: bool = False) -> bool:
        if m["resultado"]:
            return True
        fin_ms = m["fin"] * 1000
        if m["fuente"] and m["precio_final"] is None:
            v = self.feed.exacto(m["fuente"], fin_ms) or (self.feed.hasta(m["fuente"], fin_ms) or (None, None))[1]
            m["precio_final"] = v
        r = resolucion_oficial(m)
        if r:
            m["resultado"], m["resultado_origen"] = r
        elif forzar_estimacion and m["precio_final"] and m["precio_a_batir"]:
            m["resultado"] = "up" if m["precio_final"] >= m["precio_a_batir"] else "down"
            m["resultado_origen"] = "estimado con Chainlink (Polymarket no resolvió a tiempo)"
        if not m["resultado"]:
            return False
        self.log(f"Resuelto {m['slug']}: {m['resultado'].upper()} ({m['resultado_origen']})")
        for p in self.posiciones:
            if p["slug"] != m["slug"]:
                continue
            p["resultado"] = m["resultado"]
            if p["cierre"] != "vendida":
                p["cierre"] = "al cierre"
                pago = 0.5 if m["resultado"] == "empate" else 1.0 if m["resultado"] == p["lado"] else 0.0
                p["precio_venta"], p["t_venta"] = pago, m["fin"]
                p["ingreso"] = round(p["acciones"] * pago, 4)
                p["pnl"] = round(p["ingreso"] - p["coste"] - p["comision_compra"], 4)
                if self.abiertas.get(p["estrategia"]) is p:
                    del self.abiertas[p["estrategia"]]
        return True

    # ---------- bucle principal ----------
    def ejecutar(self):
        a = self.a
        self.log(f"Modo: {'heurística (sin Jev)' if a.sin_jev else 'Jev'} · mercados {a.periodo} · {a.minutos:g} min · "
                 f"decisión cada {a.cada} s · {a.stake} USDC ficticios por compra. NO se envían órdenes reales.")
        self.feed.iniciar()
        t0 = ahora()
        while not self.feed.ultimo("chainlink-spot") and ahora() - t0 < 30:
            time.sleep(0.5)
        if not self.feed.ultimo("chainlink-spot"):
            self.feed.detener()
            sys.exit("No llega ningún precio de Chainlink desde Polymarket en 30 s. Revisa tu conexión y reintenta.")

        self.inicio_sim, fin = ahora(), ahora() + a.minutos * 60
        offsets = list(range(5, self.P - 3, a.cada))
        hechos: set[tuple[int, int]] = set()
        ultimo_cierre = 0.0
        try:
            while ahora() < fin:
                t = ahora()
                v0 = int(t // self.P) * self.P
                slug = slug_para(a.periodo, v0)
                self.pasar_a_cierre(slug)
                if slug not in self.ventanas and t - v0 < 20:
                    try:
                        self.mercado(v0)
                    except Exception as e:
                        self.log(f"Error cargando mercado: {e}")
                pend = [o for o in offsets if (v0, o) not in hechos and t >= v0 + o]
                if pend:
                    for o in pend:
                        hechos.add((v0, o))
                    try:
                        m = self.mercado(v0)
                        if not m:
                            self.log(f"No encuentro el mercado {slug}")
                        else:
                            self.decidir(m)
                    except Exception as e:
                        self.log(f"  Error en la decisión: {e}")
                if ahora() - ultimo_cierre > 15:
                    ultimo_cierre = ahora()
                    for m in list(self.ventanas.values()):
                        if not m["resultado"] and ahora() > m["fin"] + 60:
                            self.cerrar_ventana(m)
                time.sleep(0.25)
        except KeyboardInterrupt:
            self.log("Interrumpido: paso a resolver lo que haya.")

        self.fin_sim = ahora()
        self.pasar_a_cierre("")
        con_pos = [m for m in self.ventanas.values() if any(p["slug"] == m["slug"] for p in self.posiciones)]
        self.log(f"Fin de las decisiones ({len(self.posiciones)} posiciones ficticias). Esperando resoluciones…")
        limite = ahora() + self.P + 600
        try:
            while ahora() < limite and any(not m["resultado"] for m in con_pos):
                for m in con_pos:
                    if not m["resultado"] and ahora() > m["fin"] + 30:
                        self.cerrar_ventana(m)
                time.sleep(15)
        except KeyboardInterrupt:
            self.log("Espera interrumpida.")
        for m in con_pos:
            if not m["resultado"] and ahora() > m["fin"] + 5:
                self.cerrar_ventana(m, forzar_estimacion=True)
        self.feed.detener()

    def datos(self) -> dict:
        ventanas = []
        for m in sorted(self.ventanas.values(), key=lambda x: x["inicio"]):
            serie = []
            if m["fuente"]:
                serie = self.feed.serie(m["fuente"], (m["inicio"] - 30) * 1000, (m["fin"] + 15) * 1000, 2000)
            ventanas.append({k: v for k, v in m.items() if k not in ("token_up", "token_down")} | {"serie": serie})
        return {
            "version": 2,
            "generado_utc": iso(ahora()),
            "config": {k: getattr(self.a, k) for k in ("periodo", "minutos", "stake", "cada", "umbral_conf", "margen",
                                                       "margen_salida", "umbral_flujo", "min_volumen", "max_entradas")}
                      | {"modo": "heurística (sin Jev)" if self.a.sin_jev else "Jev"},
            "inicio_utc": iso(self.inicio_sim), "fin_utc": iso(self.fin_sim),
            "estrategias": ESTRATEGIAS,
            "ventanas": ventanas, "decisiones": self.decisiones, "posiciones": self.posiciones,
        }


def resumen_texto(posiciones: list[dict]) -> str:
    lineas = [f"{'estrategia':<14}{'posic.':>7}{'vendidas':>9}{'ganadas':>9}{'% ganadas':>11}{'invertido':>11}{'P&L':>10}{'ROI':>8}"]
    for est in ESTRATEGIAS:
        xs = [p for p in posiciones if p["estrategia"] == est and p["pnl"] is not None]
        if not xs:
            lineas.append(f"{est:<14}{0:>7}{'-':>9}{'-':>9}{'-':>11}{'-':>11}{'-':>10}{'-':>8}")
            continue
        gan = sum(1 for p in xs if p["pnl"] > 0)
        vend = sum(1 for p in xs if p["cierre"] == "vendida")
        inv = sum(p["coste"] + p["comision_compra"] for p in xs)
        pnl = sum(p["pnl"] for p in xs)
        lineas.append(f"{est:<14}{len(xs):>7}{vend:>9}{gan:>9}{gan / len(xs) * 100:>10.1f}%{inv:>11.2f}{pnl:>+10.2f}{pnl / inv * 100:>+7.1f}%")
    return "\n".join(lineas)


def main():
    ap = argparse.ArgumentParser(description="Paper trading de Jev en Polymarket BTC Up/Down (sin dinero real).")
    ap.add_argument("--minutos", type=float, default=60, help="cuánto tiempo tomar decisiones (def. 60)")
    ap.add_argument("--periodo", choices=list(PERIODOS), default="5m", help="mercados de 5m o 15m (def. 5m)")
    ap.add_argument("--cada", type=int, default=10, help="segundos entre decisiones (def. 10)")
    ap.add_argument("--stake", type=float, default=10.0, help="USDC ficticios por compra (def. 10)")
    ap.add_argument("--umbral-conf", type=float, default=0.5, help="confianza mínima de Jev para jev_eleccion (def. 0.5)")
    ap.add_argument("--margen", type=float, default=0.05, help="jev_ventaja compra si P(Jev) - ask > margen (def. 0.05)")
    ap.add_argument("--margen-salida", type=float, default=0.02, help="jev_ventaja vende si bid > P(Jev) + margen (def. 0.02)")
    ap.add_argument("--umbral-flujo", type=float, default=0.4, help="presión de órdenes para la estrategia flujo, 0-1 (def. 0.4)")
    ap.add_argument("--min-volumen", type=float, default=50, help="acciones negociadas mínimas en 30 s para que flujo actúe (def. 50)")
    ap.add_argument("--max-entradas", type=int, default=3, help="máximo de compras por estrategia y ventana (def. 3)")
    ap.add_argument("--sin-entradas-final", type=int, default=20, help="no abrir posiciones en los últimos N segundos (def. 20)")
    ap.add_argument("--sin-jev", action="store_true", help="usa una heurística simple en lugar de Jev")
    ap.add_argument("--semilla", type=int, default=None)
    ap.add_argument("--informe", metavar="DATOS_JSON", help="solo regenera informe.html a partir de un datos.json")
    args = ap.parse_args()

    from informe import generar_informe

    if args.informe:
        ruta = Path(args.informe)
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        salida = ruta.with_name("informe.html")
        generar_informe(datos, salida)
        print(f"Informe regenerado: {salida}")
        return

    if not args.sin_jev and not os.environ.get("TYPESAFE_API_KEY"):
        sys.exit("Falta TYPESAFE_API_KEY. Ponla en el entorno o usa --sin-jev para probar el flujo.")

    carpeta = Path(f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    carpeta.mkdir()
    log_f = open(carpeta / "log.txt", "w", encoding="utf-8")

    def log(msg: str):
        linea = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        print(linea, flush=True)
        log_f.write(linea + "\n")
        log_f.flush()

    sim = Simulador(args, log)
    sim.ejecutar()

    datos = sim.datos()
    (carpeta / "datos.json").write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    generar_informe(datos, carpeta / "informe.html")
    texto = resumen_texto(sim.posiciones)
    (carpeta / "resumen.txt").write_text(texto + "\n", encoding="utf-8")
    log("\n" + texto)
    log(f"Abre ./{carpeta}/informe.html en el navegador para ver los resultados.")
    log_f.close()


if __name__ == "__main__":
    main()

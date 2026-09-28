# Contexto para continuar: simulador Jev + Polymarket

Pega este texto al empezar una conversación nueva y adjunta `simulador.py` e `informe.py`.

---

Hola. Continúo un proyecto: pruebo **Jev** (el modelo "System One" de TypeSafe AI) haciendo **paper trading** en los mercados **"Bitcoin Up or Down" de 5 minutos de Polymarket**. Sin dinero real, solo simulación con datos reales. Adjunto `simulador.py` e `informe.py` (versión actual). Responde en español.

## Estado actual (ya hecho)

`simulador.py` (Python 3.10+, `pip install requests websocket-client`):
- Toma una decisión cada `--cada` segundos (10 por defecto) durante `--minutos` (60 por defecto), en mercados de `--periodo` `5m` o `15m`.
- **Precio**: Chainlink BTC/USD, el mismo con el que Polymarket resuelve. Llega por el stream público RTDS de Polymarket. Del `resolutionSource` de cada mercado saca si se usa el precio instantáneo o la media (TWAP) de 30 o 60 s.
- **Precio a batir**: `eventMetadata.priceToBeat` de Gamma. Si no está, el tick exacto de apertura en RTDS. Si tampoco, la ventana se salta (no se inventa).
- **Libro de órdenes** de Up y Down, y **flujo de operaciones** reales de los últimos 30 y 60 s: presión compradora/vendedora hacia Up o hacia Down.
- Se lo pasa todo a **Jev** junto con la posición abierta. Jev responde con un `choice` (`buy_up`, `buy_down`, `sell`, `hold`) y un `noul` (P de que gane Up).
- 5 estrategias, cada una con como mucho una posición abierta, que compran al ask y venden al bid con la comisión real:
  - `jev_eleccion`: sigue el `choice` de Jev si la confianza pasa `--umbral-conf`.
  - `jev_ventaja`: compra si P(Jev) − ask > `--margen` y vende si bid > P(Jev) + `--margen-salida`.
  - `flujo`: sin Jev. Compra el lado hacia el que empuja el dinero y vende si la presión se da la vuelta.
  - `favorito` y `moneda`: compran una vez por ventana y esperan al cierre (sirven de comparación).
- La resolución es la oficial de Polymarket (`/v2/resolutions`). Si no llega, se estima con Chainlink y queda marcado.
- Genera `resultados_*/informe.html`: ganancia por estrategia, gráfico del precio de Chainlink y de los precios de Up/Down con cada compra ▲ y venta ▼, las decisiones de Jev, y el libro y el flujo al pulsar una decisión. También `datos.json`, `resumen.txt` y `log.txt`. Con `--informe datos.json` se regenera el HTML.
- Con `--sin-jev` se usa una heurística en vez de Jev, para probar sin clave. La clave de Jev va en `TYPESAFE_API_KEY`.

## Datos de API verificados (no inventar nombres de campos)

- **Jev**: `POST https://api.typesafe.ai/v1/systemone`, cabecera `Authorization: Bearer <key>`. Cuerpo `{model:"jev-latest", state, questions}`. Tipos de pregunta: `choice` (`criteria` como dict), `score` (`criteria` como lista) y `noul`. Respuesta: `answers.<key>.choice / .confidence / .probabilities / .score / .noul`. Tarda 70-500 ms, cuesta $0.042/MTok de entrada y la salida es gratis. Docs: https://docs.typesafe.ai
- **Gamma**: `GET https://gamma-api.polymarket.com/events/slug/btc-updown-5m-<inicio_unix>`. Campos: `markets[].outcomes` y `clobTokenIds` (strings JSON), `conditionId`, `feeSchedule.rate`, `resolutionSource`, `eventMetadata.priceToBeat`.
- **Libros**: `POST https://clob.polymarket.com/books` con `[{token_id}]` → `asset_id, bids[], asks[]` con `{price,size}`.
- **Operaciones**: `GET https://data-api.polymarket.com/trades?market=<conditionId>&limit=500&takerOnly=true` → `proxyWallet, side (BUY/SELL, lado taker), size, price, timestamp (s), outcome, outcomeIndex`.
- **Actividad de una wallet**: `GET https://data-api.polymarket.com/activity?user=<0x..>&market=&start=&end=&limit<=500` → `proxyWallet, timestamp, conditionId, type, size, usdcSize, price, side, outcome, outcomeIndex, slug`.
- **Resolución**: `GET https://data-api.polymarket.com/v2/resolutions?condition=<conditionId>` → `data[].status=="resolved"`, `payouts` (suman 1 000 000).
- **Chainlink (RTDS)**: `wss://ws-live-data.polymarket.com`, sin clave. Suscripción `{"action":"subscribe","subscriptions":[{"topic":"crypto_prices_chainlink"|"crypto_prices_twap_thirty"|"crypto_prices_twap_sixty","type":"*"/"update","filters":"{\"symbol\":\"btc/usd\"}"}]}`. Mensajes: `payload.symbol, payload.timestamp (ms), payload.value` (a veces `payload.data[]`). Hay que mandar el texto `PING` cada 5 s.
- **Canal de mercado en tiempo real**: `wss://ws-subscriptions-clob.polymarket.com/ws/market`, suscripción `{"assets_ids":[...],"type":"market","custom_feature_enabled":true}`. Eventos: `book`, `price_change`, `last_trade_price`, `best_bid_ask`, `market_resolved`. `PING` cada 10 s. No incluye la wallet de quien opera.
- **Comisión taker** (crypto_fees_v2): `acciones × rate × p × (1−p)`, con `rate` = 0.07. Mínimo 5 acciones por orden.

## Lo aprendido investigando bots

- Desde enero/febrero de 2026, Polymarket cobra comisiones dinámicas (máximas cerca de 50¢) y quitó el retraso de 500 ms. El arbitraje de latencia basado en tomar órdenes dejó de ser rentable.
- Lo que sigue funcionando:
  - **Poner órdenes en el libro** (maker) en vez de tomarlas, y cobrar reembolsos.
  - **Comprar los dos lados** en momentos distintos, cuando cada uno está barato, hasta que Up medio + Down medio < 1 $ (estilo "gabagool").
  - **Salir pronto** en lugar de aguantar hasta el cierre.
- Los bots reaccionan a **eventos** (cambios del libro, operaciones, movimientos de precio), no a intervalos fijos.

## Próximos pasos (elegir uno)

1. **Analizador de wallets**: durante X horas de mercados BTC 5m, encontrar las wallets que más operan y más ganan, y medir cuándo compran dentro de la ventana, a qué precio, si compran los dos lados, si venden antes y cuánto ganan por ventana. Todo en un informe HTML.
2. **Simulador por eventos**: sustituir el intervalo fijo por triggers del canal de mercado en tiempo real y de Chainlink (el libro se mueve, entra una operación grande, salta el precio, un lado se abarata). En cada trigger decide Jev. Añadir la estrategia de comprar los dos lados con seguimiento del coste del par, y simular órdenes maker.

## Cosas a tener en cuenta

- Cada vez que hago cambios, entregar los archivos completos y un informe de ejemplo generado con datos inventados.
- El código tiene que correr en mi ordenador o en un servidor. El espacio en la nube de Claude no llega a Polymarket.
- Todavía no lo he ejecutado con datos reales: si falla, te paso `log.txt`.

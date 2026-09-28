# Polybro

Paper trading de **Jev** (System One de TypeSafe AI) en los mercados "Bitcoin Up or Down" de 5 y 15 minutos de Polymarket. Solo simulación con datos reales, sin dinero real.

- `simulador.py`: simulador y generador del informe HTML.
- `informe.py`: generación del informe.
- `wallets.py` + `informe_wallets.py`: analizador de wallets (quién gana en BTC Up/Down y cómo opera).
- `ejemplos/informe_ejemplo.html` y `ejemplos/wallets_ejemplo.html`: informes generados con datos inventados.
- `CONTEXTO.md`: estado del proyecto, APIs verificadas y próximos pasos.

## Uso

```bash
pip install -r requirements.txt
export TYPESAFE_API_KEY=...        # o usa --sin-jev
python simulador.py --periodo 5m --minutos 60 --cada 10
```

Los resultados quedan en `resultados_*/` (`informe.html`, `datos.json`, `resumen.txt`, `log.txt`).

## Analizador de wallets

```bash
python wallets.py                          # últimas 6 h de mercados de 5 min
python wallets.py --horas 12 --periodo 15m
python wallets.py --demo                   # datos inventados, sin conexión
python wallets.py --informe resultados_wallets_X/datos.json
```

Opciones útiles: `--analizar 25` (wallets que se analizan a fondo por volumen y por ganancia),
`--min-ventanas 3`, `--max-filas 5000` (súbelo si el log avisa de mercados truncados), `--hilos 4`.
Los resultados quedan en `resultados_wallets_*/` (`informe.html`, `datos.json`, `resumen.txt`, `log.txt`).

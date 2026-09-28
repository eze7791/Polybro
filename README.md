# Polybro

Paper trading de **Jev** (System One de TypeSafe AI) en los mercados "Bitcoin Up or Down" de 5 y 15 minutos de Polymarket. Solo simulación con datos reales, sin dinero real.

- `simulador.py`: simulador y generador del informe HTML.
- `informe.py`: generación del informe.
- `ejemplos/informe_ejemplo.html`: informe generado con datos inventados.
- `CONTEXTO.md`: estado del proyecto, APIs verificadas y próximos pasos.

## Uso

```bash
pip install -r requirements.txt
export TYPESAFE_API_KEY=...        # o usa --sin-jev
python simulador.py --periodo 5m --minutos 60 --cada 10
```

Los resultados quedan en `resultados_*/` (`informe.html`, `datos.json`, `resumen.txt`, `log.txt`).

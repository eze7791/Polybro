# Elita Adventures

Identidad visual del canal de YouTube **Elita Adventures**: caminatas por calles y senderos, sin hablar, solo con sonido ambiente.

> Calles y caminos, sólo con sonido ambiente · Streets and trails, ambient sound only

## Contenido

- `entregables/Elita-Logo-camino/`: logo final (camino punteado, continuo y de puntos; muy sobrio y color; claro, oscuro y transparente).
- `entregables/Elita-YouTube-ES-EN/`: banners 2560×1440 (ES y EN, crema y noche) y fotos de perfil 800×800.
- `entregables/Elita-Marca-de-agua/`: marcas de agua en PNG transparente ("Elita" con camino, monograma "E" y "ADVENTURES" con camino), en crema y tinta; la versión `_video` lleva un halo oscuro suave para leerse sobre cualquier escena.
  Elegida: `elegida-adventures-camino/marca-de-agua_1080p.png` y `_4K.png`.
- `scripts/`: generadores en SVG renderizados con Playwright.
- `fuentes/`: Cormorant Garamond y Josefin Sans (Google Fonts, licencia OFL; ver `OFL-*.txt`).
- `CONTEXTO.md`: decisiones de diseño, paleta y pendientes.

## Regenerar

```bash
pip install -r requirements.txt
python3 -m playwright install chromium
cd scripts
python3 yt2.py     # banners y perfiles → scripts/yt2/
python3 yt.py      # combinaciones anteriores → scripts/yt/
python3 logo.py    # logo v2 (curva marcada) → scripts/out/
python3 marca.py   # marcas de agua → scripts/marca/
```

Los scripts se ejecutan desde `scripts/` y leen las fuentes de `../fuentes/`.

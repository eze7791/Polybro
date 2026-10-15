# Elita Adventures

Identidad visual del canal de YouTube **Elita Adventures**: caminatas por calles y senderos, sin hablar, solo con sonido ambiente.

> Calles y caminos, sólo con sonido ambiente · Streets and trails, ambient sound only

## Contenido

- `entregables/Elita-Logo-camino/`: logo final (camino punteado, continuo y de puntos; muy sobrio y color; claro, oscuro y transparente).
- `entregables/Elita-YouTube-ES-EN/`: banners 2560×1440 (ES y EN, crema y noche) y fotos de perfil 800×800.
- `entregables/Elita-Marca-de-agua/`: marcas de agua en PNG transparente ("Elita" con camino, monograma "E" y "ADVENTURES" con camino), en crema y tinta; la versión `_video` lleva un halo oscuro suave para leerse sobre cualquier escena.
- `entregables/Elita-Video/`: opening animado (6 s) y closing (24 s: frase de despedida + pantalla final de 20 s), en crema y noche, closing en ES y EN. Finales en `4K-60fps/`, borradores en `borrador-1080p/`.
  Elegida: `elegida-adventures-camino/marca-de-agua_1080p.png` y `_4K.png`.
- `entregables/Elita-Miniatura/`: miniaturas 1280×720 con el estilo marco (elegido), alternativas ventana y mínima, ejemplos y el marco solo en PNG transparente.
- `entregables/Elita-Agregados/`: iconos, placas de información 4K (lugar, clima, dato, historia, tip, recorrido, nota) y `GUIA-TEXTO.md` (fuente, color y sombra para el texto en video).
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
python3 logo.py    # logo elegido → scripts/out/Elita-Logo-camino/  (python3 logo.py v2: variante no elegida)
python3 marca.py   # marcas de agua → scripts/marca/
python3 miniatura.py foto.jpg "Título" "Lugar · País" --lang ES -o mini.jpg   # miniatura (estilo marco; también --estilo ventana | minima)
python3 agregados.py  # iconos y placas → scripts/agregados/
python3 miniatura.py --marco -o marco.png                                     # solo el marco
python3 video.py [1080|4K] [fps] [opening|closing|todo]   # por defecto 4K 60 todo → scripts/video/
```

Los scripts se ejecutan desde `scripts/` y leen las fuentes de `../fuentes/`.

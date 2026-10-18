# Elita Adventures

Identidad visual y piezas de video del canal de YouTube **Elita Adventures**: caminatas por calles y senderos, sin hablar, solo sonido ambiente.

> Calles y caminos, sólo con sonido ambiente · Streets and trails, ambient sound only

Decisiones y estado: `CONTEXTO.md`. Medidas para Premiere: `entregables/Elita-Agregados/GUIA-TEXTO.md`.

## Trabajar en local (Mac)

```bash
git clone https://github.com/eze7791/Polybro.git
cd Polybro && git checkout claude/ecstatic-lovelace-bzek5u
cd elita-aventuras
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -m playwright install chromium
brew install ffmpeg          # solo para video.py y musica.py
```

Las fuentes están en `fuentes/` (instalarlas también en la Mac para Premiere: doble clic → Instalar). Los scripts se ejecutan desde `scripts/` y escriben en carpetas de salida dentro de `scripts/` (ignoradas por git); lo final se copia a `entregables/`.

## Scripts (`cd scripts`)

| Script | Qué genera |
|---|---|
| `python3 logo.py` | logo elegido → `out/Elita-Logo-camino/` (`logo.py v2`: variante descartada) |
| `python3 yt2.py` | banners A/B/C/ES/EN y fotos de perfil → `yt2/` (variantes `ES2`, `ES3` en `yt2.banner`) |
| `python3 video.py 4K 60 opening\|closing\|closing-sin-videos\|todo` | opening y closing → `video/4K-60fps/` (`ELITA_LANGS=ES` para un idioma) |
| `python3 musica.py DIR` | música lofi del opening y closing (WAV); `musica.mux(video, wav, salida)` la agrega a un MP4 |
| `python3 marca2.py DIR` | marcas de agua "Elita ADVENTURES" (`crema-linea`, `crema-linea-nota`, …) |
| `python3 miniatura.py foto.jpg "Título" "Lugar · País" --lang ES -o mini.jpg` | miniatura estilo marco (`--estilo ventana\|minima`) |
| `python3 miniatura.py foto.HEIC "Título" "Lugar · País" --lang ES --otono -o mini.jpg` | miniatura cozy de otoño (color cálido, viñeta y hojas) |
| `python3 sendero.py kit` | kit sendero completo → `sendero-kit/` (cartel por tipo de lugar, clima, nota) |
| `python3 sendero.py clima-arriba DIR` | píldora de clima a la altura del cartel |
| `python3 sendero.py FOTO DIR [temas]` | prueba del kit sobre una foto |
| `python3 agregados.py` | íconos y placas (primeras versiones) |

## Entregables

- `Elita-Logo-camino/` · `Elita-YouTube-ES-EN/` · `Elita-Marca-de-agua/` (elegida: `v2-elita-adventures/marca-de-agua_crema-linea*`) · `Elita-Miniatura/`
- `Elita-Video/4K-60fps/` y `4K-60fps-con-musica/`: opening, closing con y sin videos (ES/EN, crema/noche)
- `Elita-Agregados/sendero-kit/`: el kit que se usa en los videos (por temporada) + `pais/`

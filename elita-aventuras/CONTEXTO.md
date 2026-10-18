# Contexto: canal "Elita Adventures"

Actualizado: 18 de octubre de 2026. Todo vive en `elita-aventuras/` dentro del repo `eze7791/Polybro`, rama `claude/ecstatic-lovelace-bzek5u`. Para trabajar en local ver `README.md` (instalación) y este archivo (decisiones). Las medidas exactas para Premiere están en `entregables/Elita-Agregados/GUIA-TEXTO.md`.

## El canal

- Canal de YouTube de Ivan (Dublín, Irlanda): caminatas por calles y senderos, sin hablar, solo sonido ambiente y textos en pantalla. Notas firmadas "— Elita".
- Edita en Adobe Premiere (Mac). Graba en **4K 60 fps** con iPhone 15 (y pronto Osmo Pocket; la cámara lenta de 240 fps se interpreta en una secuencia de 60).
- Frase: "Calles y caminos, sólo con sonido ambiente" / "Streets and trails, ambient sound only" (con "y", "and" y "sólo" con tilde, elección de Ivan).
- Regla: "Elita Adventures" no tiene que aparecer en todos lados (va en perfil, opening, closing y marca de agua; no en la miniatura ni en el banner).
- En español se usa tuteo neutro: **SUSCRÍBETE** (no "suscribite").

## Paleta y tipografía

- Crema `#F2EEE6` · tinta `#2A2C27` · arena `#8C6A3C` (sobre oscuro `#C9A978`) · arena claro para video `#D2B587` · noche `#1A2236` · sombra `#141A26`.
- Kit sendero (un solo color general en todas las temporadas): papel `#F4EEE2`, marrón `#9A7444`, borde `#5E4626`.
- **Cormorant Garamond** (títulos, frases, notas en cursiva) y **Josefin Sans** (mayúsculas espaciadas, etiquetas, temperatura). En video siempre **Bold**. Licencia OFL, en `fuentes/` (`CG.ttf`, `CGi.ttf`, `JS.ttf`).
- Los números en Cormorant son de estilo antiguo (bajan): para temperatura y números usar Josefin.

## Logo — "Elita-Logo-camino" (`logo.py`)

4 ventanas 220×320 en el orden de un día: Argentina al amanecer (Obelisco, jacarandás, avenida hasta la base del Obelisco), Alemania de día (castillo con puerta en arco sobre colina verde de un solo tono, Alpes), Irlanda con lluvia (ovejas, torre en ruinas apoyada tras la colina, sin muros), noche con auroras (sin óvalo en el lago). Debajo "Elita" + camino suave punto→pin + ADVENTURES. Tono "muy sobrio" (saturación 0.55). Se probaron y descartaron: bandera argentina, cara clara en la colina alemana, Patagonia (`ar_pat` queda en el código), variante v2.

## YouTube (`yt.py`, `yt2.py`)

- Banner 2560×1440 (zona segura 1546×423), ventanas a la izquierda y texto a la derecha, crema o noche. Último pedido (18/10): español en dos líneas, `variant='ES2'` "Calles y caminos, / sólo sonido ambiente." y `variant='ES3'` "Calles y caminos, / sólo con sonido ambiente." (`entregables/Elita-YouTube-ES-EN/Espanol/dos-lineas*/`). Ivan no confirmó cuál sube.
- Fotos de perfil 800×800 en 5 fondos (crema, amanecer, día, lluvia, noche con auroras).

## Video (`video.py`, `musica.py`)

- **Opening** 6 s (aprobado): ventanas una por una → "Elita" → el camino se dibuja → pin → ADVENTURES. Crema (días normales) y noche (noche, lluvia, bosque).
- **Closing** 24 s: "Thanks for walking with me." / "Gracias por caminar conmigo." + "— Elita" (0–4 s), luego pantalla final de 20 s con "Elita" + camino + ADVENTURES y círculo de suscripción. Dos variantes: **con** cuadros ANTERIOR/SIGUIENTE (huecos 680×383 en (1140,150) y (1140,620) en 1080p) y **sin videos** (nombre y suscripción centrados, `que='closing-sin-videos'`). Guías `_guias.png` para YouTube Studio.
- **Música** lofi original sintetizada (`musica.py`, 79 BPM, sin derechos de terceros), sincronizada: una campanita por ventana, acorde y batería cuando entra "Elita", campana en el pin. Versiones con música en `Elita-Video/4K-60fps-con-musica/` + WAV sueltos.
- Render: `python3 video.py 4K 60 opening|closing|closing-sin-videos|todo`; `ELITA_LANGS=ES` para solo un idioma. Tarda ~5 min por video 4K.

## Marca de agua (`marca.py`, `marca2.py`)

- **Elegida (17/10): "Elita ADVENTURES" en una línea, crema, chica**, con halo suave, opacidad 88 %. Dos posiciones: esquina inferior derecha (`crema-linea`) y alineada al borde derecho de la nota del kit sendero, abajo (`crema-linea-nota`, la última). Cuadro completo transparente 4K y 1080p, escala 100 %.
- Anteriores (no usadas): ADVENTURES + camino, monograma E, Elita + camino, papel.

## Miniatura (`miniatura.py`)

- Estilo elegido: **marco** (foto completa, borde crema redondeado, etiqueta "4K · SONIDO AMBIENTE", título Cormorant, camino punteado con pin y lugar). Alternativas: `--estilo ventana`, `--estilo minima`.
- Modo **cozy otoño** (`--otono`): color cálido, viñeta y hojas de arce cayendo; acepta HEIC del iPhone. Ejemplo hecho: "Paseo de otoño por el Grand Canal" · DUBLÍN · IRLANDA (fotos de Ivan, no se suben al repo).

## Agregados para video (`agregados.py`, `temporadas.py`, `ventanas_temporada.py`, `sendero.py`)

- Íconos de línea (25), placas de información, ubicación, clima, bloque de clima, placa completa: primeras versiones, quedaron como alternativas. Ivan las encontró "sosas".
- Probadas y descartadas: placas con tarjeta de color por temporada, ventana ilustrada por temporada, datos en color por temporada (sin dibujos).
- **Kit sendero (el que se usa)**, inspirado en una referencia que trajo Ivan: papel crema sólido + un solo color general (marrón arena) + **un iconito por pieza según la época**, dentro del papel:
  - Temporadas: otoño (hojas), halloween (calabaza con cabo, murciélago, fantasma), invierno-muneco, invierno-gorro, primavera (tulipán, mariposa), verano-mar (olas, sol, caracola), verano-sombrilla, navidad (acebo, bola), sanpatricio (trébol, sombrero de duende).
  - **Cartel de lugar** (flecha) corto y largo, con **pestaña de la temporada** arriba (ES/EN) y círculo con el **tipo de lugar** (17: parque, bosque, ciudad, pueblo, museo, iglesia, castillo, monumento, mercado, pub, café, playa, faro, montaña, lago-río, puente, jardín).
  - **Pestaña del país** colgando debajo del cartel (corta y larga, igual para todas las temporadas).
  - **Píldora de clima** por estado del cielo; versión `clima-arriba_` a la misma altura que el cartel (aparecen en momentos distintos).
  - **Nota de Elita** con cintas, camino punteado y firma "— ELITA".
  - Ivan escribe los textos en Premiere (medidas en `GUIA-TEXTO.md`).

## Pendiente / ideas

- Elegir banner ES2 o ES3 y subirlo; elegir foto de perfil.
- Imagen 150×150 para "Marca de agua del video" de YouTube (botón de suscripción en todos los videos).
- Link de suscripción para la descripción: `https://www.youtube.com/@HANDLE?sub_confirmation=1`.
- Posibles tipos de lugar extra (cementerio, estación de tren, estadio, zoológico).

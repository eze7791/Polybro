# Contexto: canal "Elita Adventures" (logo y YouTube)

Actualizado: 15 de octubre de 2026. Puntos de partida: `Elita-Logo-camino` y `Elita-YouTube-ES-EN` (en `entregables/`).

Textos definitivos del banner: "Calles y caminos, sólo con sonido ambiente" (con "y" y "sólo" con tilde) / "Streets and trails, ambient sound only" (con "and", no "&").

## El canal

- Canal de YouTube de Ivan (Dublín, Irlanda): caminatas por calles de ciudades y senderos (hikings), sin hablar, solo con sonido ambiente y comentarios escritos en pantalla.
- Nombre: Elita Adventures. Las notas en pantalla van firmadas "— Elita".
- Idioma: probablemente inglés, con piezas en español.
- Edita en Adobe Premiere (Mac) y graba con un iPhone 15. El viento irlandés le arruina el audio; se le recomendó deadcat, micrófono USB‑C estéreo y filtro de paso alto + DeNoise.

## Logo elegido: "Elita-Logo-camino"

Arriba, 4 ventanas (paneles verticales con esquinas redondeadas, 220×320, separación 20), en el orden de un día:

1. Argentina al amanecer: Buenos Aires con el Obelisco, jacarandás lilas, sol bajo, cielo lila → durazno. La avenida llega hasta la base del Obelisco.
2. Alemania de día: castillo blanco con torres de techo azul pizarra y puerta en arco, sobre una colina verde, Alpes nevados y pinos.
3. Irlanda con lluvia: colinas verdes, ovejas de cara negra, torre en ruinas apoyada detrás de la cresta de la colina, lluvia en diagonal (sin muros de piedra).
4. Noche: auroras verdes, luna creciente, estrellas, montaña, lago con reflejo de la aurora y pinos.

Ajustes del 15/10 (pedido de Ivan, sin cambiar la estética): (se probó una bandera argentina y una cara más clara en la colina de Alemania; Ivan pidió sacarlas) calle hasta el Obelisco, colina del castillo verde (un solo tono) + puerta, torre de Irlanda sin flotar y sin las líneas crema de los muros, sin el óvalo gris del lago. Se regeneraron logo, banners, vista previa de la marca de agua y opening (el closing y las fotos de perfil no usan las ventanas).

Descartado: Argentina con Patagonia (`ar_pat` en `logo.py`). Ivan eligió Buenos Aires.

Debajo: "Elita" en Cormorant Garamond SemiBold; un camino curvo suave de un punto a un pin (estilos puntos, punteado y continuo); ADVENTURES en Josefin Sans SemiBold con mucho espaciado.

Tonos: "muy sobrio" (saturación 0.55) y "color" (0.9). En lo final se usó el muy sobrio.

No elegida: "Elita-Logo-camino-v2" (curva más marcada y opción sin punto ni pin).

## YouTube

- Regla de Ivan: "Elita Adventures" no tiene que aparecer en todos lados. El nombre va en la foto de perfil; el banner muestra las ventanas y la frase.
- Banner 2560×1440: ventanas en fila a la izquierda, texto a la derecha a la misma altura, sin línea de camino, todo dentro del área segura 1546×423. Fondo crema `#F2EEE6` o noche `#1A2236`, con dos colinas de línea muy tenues.
- Opciones bilingües (`yt2.py`, variantes A/B/C). Se recomendó la A.
- Banners por idioma (entregados): ES "Calles y caminos, / sólo con sonido / ambiente." · EN "Streets and trails, / ambient / sound only.", en crema y noche.
- Foto de perfil 800×800 (recorte circular): "Elita" + camino punteado + ADVENTURES en 5 fondos: crema, amanecer Argentina, día Alemania, lluvia Irlanda, noche con auroras (camino verde aurora).

## Paleta y tipografía

- Crema `#F2EEE6` · tinta `#2A2C27` · arena `#8C6A3C` (sobre oscuro `#C9A978`) · noche `#1A2236` · texto claro `#EEE7DA`.
- Cormorant Garamond SemiBold, recta y cursiva: títulos y frases (`lining-nums`).
- Josefin Sans SemiBold: ADVENTURES y etiquetas en mayúsculas espaciadas.

## Otras piezas ya hechas (fuera de este repo)

- Kit de overlays sobrios para video (Cormorant + Josefin, hueso `#F2EEE6` + arena `#D2B587`), con versiones por temporada.
- Placas de Waterstown Park (Dublín 20), EN y ES, 1080p y 4K: lugar, clima, historia del Silver Bridge de los Guinness, ¿sabías que?, tip y nota. Sombra suave detrás. Es el estilo de texto de los videos.

## Pendiente

- Ivan elige el banner (A/B/C o ES/EN), el fondo (crema o noche) y el color de la foto de perfil.
- ~~Marca de agua~~ **Elegida: "ADVENTURES" + camino punteado** (`entregables/Elita-Marca-de-agua/elegida-adventures-camino/`, cuadros completos transparentes 1080p y 4K, opacidad 80 % incluida: se arrastran a la pista de arriba en Premiere sin escalar). Encaja con la regla de no repetir "Elita" en todos lados. Las otras (Elita + camino, monograma) quedan como alternativas.
- Opening: **aprobado en crema**; también va en noche para tomas de noche, lluvia o bosque. Final en 4K a 60 fps (`entregables/Elita-Video/4K-60fps/`). Ivan graba en 4K 60 con iPhone 15 y quizás pronto Osmo Pocket (la cámara lenta a 240 fps se interpreta en la secuencia de 60).
- Closing (`video.py`, 24 s, un solo archivo para poner al final del video): frase de despedida "Thanks for walking with me." / "Gracias por caminar conmigo." + "— Elita" (0:00–0:04), y desde 0:04,2 la pantalla final de 20 s: "Elita" + camino + ADVENTURES y el círculo de suscripción a la izquierda; a la derecha 2 cuadros punteados con etiqueta PREVIOUS/NEXT (ANTERIOR/SIGUIENTE) para los videos anterior y siguiente, huecos de 680×383 en (1140,150) y (1140,620). `_guias.png` muestra dónde poner los elementos en YouTube Studio. (Se descartó el outro con el logo que se desarma.)
- Marco de miniatura.
- (Intro/outro: ver opening y pantalla final.)

## Notas de los scripts

- `logo.py`: escenas de las ventanas en SVG (diccionario `P`: `ar_ba`, `ar_pat`, `de`, `ie`, `nt`). `python3 logo.py` genera el logo elegido (`logo_camino()`, verificado contra los PNG originales); `python3 logo.py v2` la variante no elegida.
- `yt.py`: `windows()`, `trail()` (estilos `puntos` / `punteado` / `continuo`) y `hills()`.
- `yt2.py`: `banner(variant='A'|'B'|'C'|'ES'|'EN')` y perfiles (`PERF`). Verificado: reproduce los entregables píxel por píxel.

# Guía de texto para los videos de Elita

## Fuentes (instalalas en la Mac: doble clic en cada .ttf de `fuentes/` → Instalar)

| Para qué | Fuente | Peso |
|---|---|---|
| Títulos, nombres de lugares, frases | **Cormorant Garamond** | **Bold** |
| Notas firmadas ("— Elita") | Cormorant Garamond *Italic* | **Bold** |
| Etiquetas chicas (CLIMA, ¿SABÍAS QUE?, DUBLÍN · IRLANDA) | **Josefin Sans** en MAYÚSCULAS | **Bold**, espaciado 150–200 |

En video usá siempre **Bold**. Los pesos finos (Regular, Light) se pierden.

## Colores

| Uso | Color |
|---|---|
| Texto principal | **Crema `#F2EEE6`** (nunca blanco puro) |
| Etiquetas y firma | **Arena `#D2B587`** |

Nunca texto oscuro sobre el video.

## La sombra (lo más importante para que se lea siempre)

En Premiere → Gráficos esenciales → Apariencia → **Sombra**:

- Color: `#141A26` (azul noche)
- Opacidad: **70 %**
- Ángulo: 135° · Distancia: **2**
- Tamaño: **6** · Desenfoque: **30**

Para cielos muy claros o nieve, agregá una segunda sombra igual con distancia 0 y desenfoque 60, o usá las placas PNG de esta carpeta, que ya la traen.

## Tamaños (secuencia 4K, 3840×2160)

| Elemento | Tamaño |
|---|---|
| Título | 190 px |
| Texto | 115 px |
| Nota en cursiva | 130 px |
| Etiqueta | 64 px |

En una secuencia 1080p, la mitad de cada valor.

## Ubicación y tiempo

- Abajo a la izquierda, con margen de 5 % (≈ 190 px en 4K) del borde.
- 5 a 7 segundos en pantalla, con fundido de entrada y salida de 0,5 s.
- Máximo dos líneas de texto; una placa a la vez.

## Ícono de ubicación + texto (texto a 115 en 4K)

Archivos en `ubicacion/`: `ubicacion-icono_4K.png` (el ícono ya ubicado) y `guia-texto_4K.png` (líneas rojas temporales). En 1080p, los `_1080p.png`.

| | 4K | 1080p |
|---|---|---|
| Ícono | PNG a cuadro completo, escala 100 %, posición sin tocar | igual |
| Texto: inicio (izquierda) | X = 380 | X = 190 |
| Texto: línea base (donde se apoyan las letras) | Y = 1900 | Y = 950 |
| Tamaño | 115 | 57,5 |

Alineación a la izquierda. Con la guía encima, mové el texto hasta que arranque en la línea roja vertical y se apoye en la horizontal; después borrá la guía y guardalo como plantilla.

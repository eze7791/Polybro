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

## Fila de clima (va arriba de la ubicación)

Archivos en `clima/`: `clima-iconos_<estado>_4K.png` con el termómetro y el ícono del cielo ya ubicados (despejado, parcial, nublado, lluvia, niebla, viento, nieve, noche-despejada) y `guia-clima_4K.png`. En 1080p, los `_1080p.png` y la mitad de cada número.

| Texto | Fuente | Tamaño | X (4K) | Línea base Y (4K) |
|---|---|---|---|---|
| Temperatura ("12°C") | **Josefin Sans Bold** (sus números quedan todos a la misma altura; los de Cormorant bajan) | 100 | 380 | 1720 |
| Estado ("Despejado") | Cormorant Garamond Bold | 115 | 920 | 1720 |

Íconos sueltos a mano (Controles de efectos, escala 106): termómetro en posición 277 · 1668; cielo en 805 · 1668.

## Fila estación + temperatura + clima (la que usa Ivan)

Archivos en `estacion/`: íconos sueltos transparentes (`icono_temperatura.png` y para el cielo `icono_sol`, `icono_sol_nube`, `icono_nube`, `icono_lluvia`, `icono_niebla`, `icono_viento`, `icono_nieve`, `icono_luna`), `guia-estacion_4K.png` y `ejemplo.jpg`. Va arriba de la ubicación.

Secuencia 4K (en 1080p, la mitad de cada número y escala 53):

| Elemento | Qué es | Posición | Tamaño / escala |
|---|---|---|---|
| Estación | texto: Cormorant Garamond Bold, alineado a la izquierda | X 192 · Y 1720 (línea base) | 115 |
| Termómetro | `icono_temperatura.png` | 845 · 1668 | escala 106 |
| Temperatura | texto: **Josefin Sans Bold** | X 930 · Y 1720 (línea base) | 100 |
| Clima | `icono_nube.png`, `icono_sol.png`, etc. | 1365 · 1668 | escala 106 |
| (Ubicación, abajo) | `ubicacion.png` + texto | 277 · 1848 / texto X 380 · Y 1900 | 106 / 115 |

## Bloque de clima (estación / temperatura / cielo, uno abajo del otro)

Archivos en `bloque-clima/`: `bloque-clima_<estado>_4K.png` (calendario + termómetro + ícono del cielo, ya ubicados; estados: despejado, parcial, nublado, lluvia, niebla, viento, nieve, noche-despejada), `guia-bloque_4K.png` y `ejemplo.jpg`. No incluye la ubicación; queda justo arriba de ella, así pueden convivir.

Textos (4K; en 1080p la mitad), alineados a la izquierda, X = 380:

| Línea | Ejemplo | Fuente | Tamaño | Línea base Y |
|---|---|---|---|---|
| Estación | Otoño | Cormorant Garamond Bold | 115 | 1360 |
| Temperatura | 12°C | Josefin Sans Bold | 100 | 1540 |
| Cielo | Parcialmente nublado | Cormorant Garamond Bold | 115 | 1720 |

Plantilla (una vez por cada estado del cielo que uses): Gráficos esenciales → Editar → Nueva capa → Desde archivo → `bloque-clima_<estado>_4K.png`; agregar las 3 capas de texto con las medidas de arriba; clic derecho en el clip → Exportar como plantilla de gráficos animados → "Elita – clima <estado>".

## Placa completa: fecha/estación, temperatura, cielo y ubicación (la que conviene usar)

Archivos en `placa-completa/`: `placa-completa_<estado>_4K.png` con los 4 íconos ya ubicados (calendario, termómetro, cielo y pin más grande), `guia-placa-completa_4K.png` y `ejemplo.jpg`. Estados: despejado, parcial, nublado, lluvia, niebla, viento, nieve, noche-despejada.

Textos (4K; en 1080p la mitad), alineados a la izquierda, todos en X = 400:

| Línea | Ejemplo | Fuente | Tamaño | Línea base Y |
|---|---|---|---|---|
| Fecha / estación | Otoño · 15 de octubre | Cormorant Garamond Bold | 115 | 1315 |
| Temperatura | 12°C | Josefin Sans Bold | 100 | 1495 |
| Cielo | Parcialmente nublado | Cormorant Garamond Bold | 115 | 1675 |
| Ubicación | Waterstown Park · Dublín | Cormorant Garamond Bold | **150** | 1900 |

Plantilla: Gráficos esenciales → Nueva capa → Desde archivo → el PNG del estado; 4 capas de texto con las medidas de arriba; Exportar como plantilla de gráficos animados → "Elita – placa <estado>".

import argparse, asyncio, os
from playwright.async_api import async_playwright
# Agregados para los videos: iconos de línea y placas de información (lugar, clima, dato, historia,
# tip, recorrido, nota) en crema con sombra suave para que se lean sobre cualquier toma.
# Las placas salen como cuadro completo 4K transparente (3840x2160) con la placa abajo a la izquierda:
# se arrastran a una pista de arriba en Premiere sin mover ni escalar.
# Uso:
#   python3 agregados.py                      → todos los iconos y las placas de ejemplo (ES y EN)
#   python3 agregados.py placa --tipo clima --icono lluvia --titulo "11°C · Llovizna" --texto "Viento del oeste" --lang ES -o placa.png
CREMA='#F2EEE6'; ARENA='#D2B587'; TINTA='#2A2C27'; NOCHE='#141A26'
# ---------- iconos: grilla de 48, trazo redondeado ----------
I={
 'ubicacion':'<path d="M24 43 C16 33 11 27 11 19 a13 13 0 0 1 26 0 c0 8 -5 14 -13 24z"/><circle cx="24" cy="19" r="4.5"/>',
 'ruta':'<circle cx="7" cy="34" r="2.6" fill="currentColor" stroke="none"/><path d="M11 33 C17 27 22 38 28 31 S36 24 38 26" stroke-dasharray="3.2 3.6"/><path d="M40 29 c-4 -5 -6 -7 -6 -10 a6 6 0 0 1 12 0 c0 3 -2 5 -6 10z"/>',
 'sol':'<circle cx="24" cy="24" r="8"/>'+''.join(f'<path d="M{24+13*c:.1f} {24+13*s:.1f} L{24+18*c:.1f} {24+18*s:.1f}"/>' for c,s in [(1,0),(.707,.707),(0,1),(-.707,.707),(-1,0),(-.707,-.707),(0,-1),(.707,-.707)]),
 'nube':'<path d="M14 36 h21 a8 8 0 0 0 0 -16 a11 11 0 0 0 -21 -2 a8 8 0 0 0 0 18z"/>',
 'sol_nube':'<path d="M19 13 a7 7 0 0 1 11 6"/><path d="M19 6 v-2 M8 12 l-2 -1 M30 8 l1.5 -1.5 M10 22 h-2"/><path d="M16 39 h19 a7 7 0 0 0 0 -14 a10 10 0 0 0 -19 -1 a7.5 7.5 0 0 0 0 15z"/>',
 'lluvia':'<path d="M14 29 h21 a8 8 0 0 0 0 -16 a11 11 0 0 0 -21 -2 a8 8 0 0 0 0 18z"/><path d="M17 34 l-2 6 M25 34 l-2 6 M33 34 l-2 6"/>',
 'viento':'<path d="M6 18 h22 a5 5 0 1 0 -5 -5"/><path d="M6 26 h30 a5 5 0 1 1 -5 5"/><path d="M6 34 h14"/>',
 'niebla':'<path d="M8 16 h32 M5 24 h26 M14 32 h29 M9 40 h20"/>',
 'nieve':'<path d="M24 6 v36 M8.4 15 l31.2 18 M8.4 33 l31.2 -18"/><path d="M19 9 l5 4 l5 -4 M19 39 l5 -4 l5 4"/>',
 'luna':'<path d="M31 8 a17 17 0 1 0 10 25 a13 13 0 0 1 -10 -25z"/>',
 'temperatura':'<path d="M20 28 V10 a4 4 0 0 1 8 0 v18 a8 8 0 1 1 -8 0z"/><path d="M24 31 v-14"/><circle cx="24" cy="34" r="2.6" fill="currentColor"/>',
 'reloj':'<circle cx="24" cy="24" r="17"/><path d="M24 13 v11 l7 5"/>',
 'arbol':'<circle cx="24" cy="18" r="12"/><path d="M24 30 v13 M24 36 l-5 -4 M24 33 l5 -4"/>',
 'pino':'<path d="M24 5 L35 22 h-6 L38 35 H10 L19 22 h-6z"/><path d="M24 35 v8"/>',
 'montana':'<path d="M4 40 L18 16 L26 28 L32 20 L44 40z"/><path d="M14 23 l4 2 l3 -3"/>',
 'agua':'<path d="M5 18 q4.75 -5 9.5 0 t9.5 0 t9.5 0 t9.5 0"/><path d="M5 27 q4.75 -5 9.5 0 t9.5 0 t9.5 0 t9.5 0"/><path d="M5 36 q4.75 -5 9.5 0 t9.5 0 t9.5 0 t9.5 0"/>',
 'puente':'<path d="M3 22 h42"/><path d="M6 38 v-16 M42 38 v-16"/><path d="M6 38 a18 13 0 0 1 36 0"/><path d="M15 22 v6 M24 22 v3 M33 22 v6"/>',
 'historia':'<path d="M12 42 V16 h4 v-5 h4 v5 h8 v-5 h4 v5 h4 v26z"/><path d="M21 42 v-8 a3 3 0 0 1 6 0 v8"/><path d="M8 42 h32"/>',
 'info':'<circle cx="24" cy="24" r="17"/><path d="M24 22 v11"/><circle cx="24" cy="15.5" r="1.6" fill="currentColor"/>',
 'camara':'<path d="M7 16 h8 l3 -5 h12 l3 5 h8 v22 H7z"/><circle cx="24" cy="26" r="7"/>',
 'cafe':'<path d="M9 21 h24 v8 a10 10 0 0 1 -10 10 h-4 a10 10 0 0 1 -10 -10z"/><path d="M33 23 h3 a4.5 4.5 0 0 1 0 9 h-4"/><path d="M16 9 q-2 3 0 6 M22 8 q-2 3 0 6 M28 9 q-2 3 0 6"/>',
 'pajaro':'<path d="M6 22 q7 -7 12 2 q5 -9 12 -2"/><path d="M24 33 q4.5 -5 8 1 q3.5 -6 8 -1"/>',
 'ciudad':'<path d="M5 42 h38"/><path d="M8 42 V22 h10 v20 M18 42 V10 h12 v32 M30 42 V18 h10 v24"/><path d="M22 16 h4 M22 22 h4 M22 28 h4 M12 28 h2 M34 24 h2 M34 30 h2"/>',
 'pasos':'<ellipse cx="17" cy="15" rx="4.5" ry="7"/><path d="M14.5 26 h5"/><ellipse cx="31" cy="27" rx="4.5" ry="7"/><path d="M28.5 38 h5"/>',
}
def icono(nombre,col=CREMA,tam=48,sw=2.4):
    return f'<svg width="{tam}" height="{tam}" viewBox="0 0 48 48" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" style="color:{col};overflow:visible">{I[nombre]}</svg>'
# ---------- placas ----------
TIPOS={  # tipo: (icono, etiqueta ES, etiqueta EN)
 'lugar':('ubicacion',None,None),
 'clima':('nube','CLIMA','WEATHER'),
 'dato':('info','¿SABÍAS QUE?','DID YOU KNOW?'),
 'historia':('historia','UN POCO DE HISTORIA','A BIT OF HISTORY'),
 'tip':('ruta','TIP','TIP'),
 'recorrido':('pasos','RECORRIDO','ROUTE'),
 'nota':(None,None,None),
}
SOMBRA='0 0 24px rgba(20,26,38,.7), 0 0 8px rgba(20,26,38,.5), 0 2px 4px rgba(0,0,0,.5)'
def placa(tipo,titulo='',texto='',etiqueta=None,icono_nombre=None,lang='ES',firma=True):
    ic,es,en=TIPOS[tipo]
    ic=icono_nombre or ic
    et=etiqueta if etiqueta is not None else (es if lang=='ES' else en)
    if tipo=='nota':
        cont=f'''<div class="tx" style="font-size:66px;font-style:italic;max-width:1250px">{texto}</div>{f'<div class="tx" style="font-size:50px;font-style:italic;color:{ARENA};margin-top:10px">— Elita</div>' if firma else ''}'''
        fila=f'<div>{cont}</div>'
    else:
        cont=(f'<div class="et">{et}</div>' if et else '')+(f'<div class="ti">{titulo}</div>' if titulo else '')+(f'<div class="tx">{texto}</div>' if texto else '')
        fila=f'<div style="display:flex;gap:32px;align-items:flex-start"><div style="padding-top:4px;filter:drop-shadow(0 0 10px rgba(20,26,38,.6)) drop-shadow(0 2px 3px rgba(0,0,0,.4))">{icono(ic,CREMA,104,2.6)}</div><div>{cont}</div></div>'
    return f'''<div id="m" style="position:relative;width:1920px;height:1080px">
<div style="position:absolute;left:96px;bottom:108px">
<div style="position:absolute;inset:-60px -90px -60px -70px;background:radial-gradient(closest-side,rgba(20,26,38,.55),rgba(20,26,38,0));filter:blur(10px)"></div>
<div style="position:relative">{fila}</div></div></div>'''
def css(fuentes):
    return f'''@font-face{{font-family:CG;src:url(file://{fuentes}/CG.ttf);font-weight:300 700;font-style:normal}}
@font-face{{font-family:CG;src:url(file://{fuentes}/CGi.ttf);font-weight:300 700;font-style:italic}}
@font-face{{font-family:JS;src:url(file://{fuentes}/JS.ttf);font-weight:100 700}}
html,body{{margin:0;background:transparent}}
.et{{font-family:JS;font-weight:700;font-size:32px;letter-spacing:7px;color:{ARENA};text-shadow:{SOMBRA};margin-bottom:8px}}
.ti{{font-family:CG;font-weight:700;font-size:96px;line-height:1.05;color:{CREMA};text-shadow:{SOMBRA};font-variant-numeric:lining-nums}}
.tx{{font-family:CG;font-weight:700;font-size:58px;line-height:1.15;text-wrap:balance;color:{CREMA};text-shadow:{SOMBRA};max-width:1150px;margin-top:6px;font-variant-numeric:lining-nums}}'''
EJEMPLOS={
 'ES':[('lugar',dict(etiqueta='DUBLÍN · IRLANDA',titulo='Waterstown Park')),
       ('clima',dict(titulo='12°C · Nublado',texto='Viento suave del oeste')),
       ('clima',dict(icono_nombre='lluvia',titulo='9°C · Llovizna',texto='Un día bien irlandés')),
       ('dato',dict(texto='Acá va un dato curioso del lugar, en una o dos líneas.')),
       ('historia',dict(titulo='Nombre del lugar',texto='Una o dos líneas con su historia.')),
       ('tip',dict(texto='Un consejo corto para quien quiera hacer esta caminata.')),
       ('recorrido',dict(titulo='4,2 km · 55 min',texto='Ida y vuelta junto al río')),
       ('nota',dict(texto='Me encanta cómo suena el río en esta parte.'))],
 'EN':[('lugar',dict(etiqueta='DUBLIN · IRELAND',titulo='Waterstown Park')),
       ('clima',dict(titulo='12°C · Cloudy',texto='Light westerly breeze')),
       ('clima',dict(icono_nombre='lluvia',titulo='9°C · Drizzle',texto='A very Irish day')),
       ('dato',dict(texto='A fun fact about this place, in one or two lines.')),
       ('historia',dict(titulo='Place name',texto='One or two lines about its history.')),
       ('tip',dict(texto='A short tip for anyone who wants to do this walk.')),
       ('recorrido',dict(titulo='4.2 km · 55 min',texto='Out and back along the river')),
       ('nota',dict(texto='I love how the river sounds along this stretch.'))],
}
async def generar(trabajos):
    fuentes=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fuentes')
    tmp=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_a.html')
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for path,body,(w,h),dsf in trabajos:
            os.makedirs(os.path.dirname(path) or '.',exist_ok=True)
            pg=await b.new_page(viewport={'width':w,'height':h},device_scale_factor=dsf)
            open(tmp,'w').write(f'<html><head><meta charset="utf-8"><style>{css(fuentes)}</style></head><body>{body}</body></html>')
            await pg.goto('file://'+tmp); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(150)
            await pg.screenshot(path=path,omit_background=True,clip={'x':0,'y':0,'width':w,'height':h}); await pg.close()
        await b.close()
    os.remove(tmp)
def todo(out='agregados'):
    t=[]
    halo='filter:drop-shadow(0 0 10px rgba(20,26,38,.65)) drop-shadow(0 2px 3px rgba(0,0,0,.45))'
    for n in I:
        t.append((f'{out}/iconos/video-crema/{n}.png',f'<div style="padding:24px;width:80px;height:80px;{halo}">{icono(n,CREMA,80,2.4)}</div>',(128,128),2))
        t.append((f'{out}/iconos/tinta/{n}.png',f'<div style="padding:24px;width:80px;height:80px">{icono(n,TINTA,80,2.4)}</div>',(128,128),2))
    # hoja de iconos para ver todos juntos
    hoja=''.join(f'<div style="width:150px;text-align:center;font-family:JS;font-weight:600;font-size:13px;letter-spacing:2px;color:{TINTA}"><div style="height:80px;display:flex;justify-content:center">{icono(n,TINTA,64,2.4)}</div>{n.upper()}</div>' for n in I)
    t.append((f'{out}/iconos/hoja-de-iconos.png',f'<div style="background:{CREMA};width:1200px;height:340px;padding:40px 0;display:flex;flex-wrap:wrap;row-gap:30px;justify-content:center">{hoja}</div>',(1200,420),2))
    for lang,ej in EJEMPLOS.items():
        for k,(tipo,kw) in enumerate(ej,1):
            t.append((f'{out}/placas-4K/{lang}/{k}-{tipo}{"-"+kw["icono_nombre"] if kw.get("icono_nombre") else ""}.png',placa(tipo,lang=lang,**kw),(1920,1080),2))
    asyncio.run(generar(t))
if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='placa':
        a=argparse.ArgumentParser(description='Placa de información 4K transparente')
        a.add_argument('placa'); a.add_argument('--tipo',choices=list(TIPOS),required=True)
        a.add_argument('--titulo',default=''); a.add_argument('--texto',default=''); a.add_argument('--etiqueta')
        a.add_argument('--icono',choices=list(I)); a.add_argument('--lang',choices=['ES','EN'],default='ES')
        a.add_argument('--sin-firma',action='store_true'); a.add_argument('-o','--salida',default='placa.png')
        o=a.parse_args()
        asyncio.run(generar([(o.salida,placa(o.tipo,o.titulo,o.texto,o.etiqueta,o.icono,o.lang,not o.sin_firma),(1920,1080),2)]))
    else:
        todo()

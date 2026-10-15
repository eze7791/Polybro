import argparse, asyncio, base64, mimetypes, os
from playwright.async_api import async_playwright
# Marco de miniatura de YouTube (1280x720): borde redondeado como las ventanas del logo,
# degradado oscuro abajo para que el texto se lea sobre cualquier foto, título en Cormorant,
# camino punteado con pin, lugar en Josefin y etiqueta arriba ("4K · SONIDO AMBIENTE").
# Uso:
#   python3 miniatura.py foto.jpg "Waterstown Park" "DUBLÍN · IRLANDA" --lang ES -o mini.jpg
#   python3 miniatura.py --marco -o marco.png        (solo el marco, PNG transparente)
ETIQUETA={'ES':'4K · SONIDO AMBIENTE','EN':'4K · AMBIENT SOUND'}
CREMA='#F2EEE6'; ARENA='#D2B587'
SOMBRA='0 2px 14px rgba(0,0,0,.45), 0 1px 3px rgba(0,0,0,.35)'
def camino(lw=300):
    d=f'M14 0 C {lw*.21} -26, {lw*.33} 22, {lw*.5} 2 S {lw*.81} -24, {lw-12} 2'
    return f'''<svg width="{lw+20}" height="44" viewBox="-8 -30 {lw+20} 44" style="filter:drop-shadow(0 1px 4px rgba(0,0,0,.5));display:block">
<circle cx="0" cy="0" r="5" fill="{ARENA}"/><path d="{d}" fill="none" stroke="{ARENA}" stroke-width="3" stroke-linecap="round" stroke-dasharray="9 8"/>
<path d="M{lw} 6 c-9 -12 -14 -17 -14 -24 a14 14 0 0 1 28 0 c0 7 -5 12 -14 24z" fill="none" stroke="{ARENA}" stroke-width="2.8"/><circle cx="{lw}" cy="-18" r="4.5" fill="{ARENA}"/></svg>'''
def html(foto=None,titulo='',lugar='',etiqueta='',texto=True):
    fuentes=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fuentes')
    css=f'''@font-face{{font-family:CG;src:url(file://{fuentes}/CG.ttf);font-weight:300 700}}
@font-face{{font-family:JS;src:url(file://{fuentes}/JS.ttf);font-weight:100 700}}
html,body{{margin:0;background:transparent}}
#m{{position:relative;width:1280px;height:720px;overflow:hidden;font-family:CG}}
#foto{{position:absolute;inset:0;background-size:cover;background-position:center}}
#deg{{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(20,26,38,.5) 0%,rgba(20,26,38,0) 22%),linear-gradient(to top,rgba(20,26,38,.74) 0%,rgba(20,26,38,.38) 30%,rgba(20,26,38,0) 56%)}}
#marco{{position:absolute;inset:24px;border:3px solid rgba(242,238,230,.92);border-radius:26px;box-shadow:0 0 12px rgba(0,0,0,.25),inset 0 0 12px rgba(0,0,0,.18)}}
#et{{position:absolute;left:62px;top:56px;font-family:JS;font-weight:600;font-size:22px;letter-spacing:6px;color:{CREMA};text-shadow:{SOMBRA}}}
#tx{{position:absolute;left:66px;right:66px;bottom:60px;color:{CREMA}}}
#ti{{font-weight:600;font-size:110px;line-height:.98;text-wrap:balance;max-width:1080px;text-shadow:{SOMBRA};font-variant-numeric:lining-nums}}
#ca{{margin:10px 0 4px 4px}}
#lu{{font-family:JS;font-weight:600;font-size:26px;letter-spacing:8px;margin-left:4px;text-shadow:{SOMBRA}}}'''
    fondo=''
    if foto:
        mime=mimetypes.guess_type(foto)[0] or 'image/jpeg'
        fondo=f'<div id="foto" style="background-image:url(data:{mime};base64,{base64.b64encode(open(foto,"rb").read()).decode()})"></div>'
    cuerpo=f'<div id="et">{etiqueta}</div><div id="tx"><div id="ti">{titulo}</div><div id="ca">{camino()}</div><div id="lu">{lugar}</div></div>' if texto else ''
    # el título se achica solo si no entra en dos líneas
    js='''const t=document.getElementById('ti'); if(t){let s=110; while(t.offsetHeight>2*s*1.0+4 && s>56){s-=4; t.style.fontSize=s+'px';}}'''
    return f'<html><head><meta charset="utf-8"><style>{css}</style></head><body><div id="m">{fondo}<div id="deg"></div><div id="marco"></div>{cuerpo}</div><script>{js}</script></body></html>'
async def render(path,doc,transparente):
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720})
        tmp=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_m.html'); open(tmp,'w').write(doc)
        await pg.goto('file://'+tmp); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(200)
        jpg=path.lower().endswith(('.jpg','.jpeg'))
        await pg.screenshot(path=path,omit_background=transparente and not jpg,type='jpeg' if jpg else 'png',**({'quality':92} if jpg else {}))
        await b.close()
    os.remove(tmp)
if __name__=='__main__':
    a=argparse.ArgumentParser(description='Miniatura de YouTube con el marco de Elita')
    a.add_argument('foto',nargs='?'); a.add_argument('titulo',nargs='?',default=''); a.add_argument('lugar',nargs='?',default='')
    a.add_argument('--lang',choices=['ES','EN'],default='EN'); a.add_argument('--etiqueta',help='texto de arriba (por defecto 4K · AMBIENT SOUND / SONIDO AMBIENTE; "" para ninguno)')
    a.add_argument('--marco',action='store_true',help='solo el marco, sin foto ni texto (PNG transparente)')
    a.add_argument('-o','--salida',default='miniatura.jpg')
    o=a.parse_args()
    et=ETIQUETA[o.lang] if o.etiqueta is None else o.etiqueta
    doc=html(None if o.marco else o.foto,o.titulo,o.lugar.upper(),et,texto=not o.marco)
    asyncio.run(render(o.salida,doc,transparente=o.marco or not o.foto))

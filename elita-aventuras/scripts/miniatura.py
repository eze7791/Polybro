import argparse, asyncio, base64, mimetypes, os
from playwright.async_api import async_playwright
# Miniatura de YouTube (1280x720) con la estética de Elita. Tres estilos (el elegido es "marco"):
#   marco:   foto completa con borde crema redondeado, etiqueta arriba y texto abajo a la izquierda.
#   ventana: la foto dentro de una ventana redondeada (como las del logo) sobre crema, texto al costado en tinta.
#   minima:  foto completa sin marco, título centrado abajo con el camino punteado y el lugar.
# Uso:
#   python3 miniatura.py foto.jpg "Waterstown Park" "Dublín · Irlanda" --lang ES -o mini.jpg
#   python3 miniatura.py foto.jpg "Waterstown Park" "Dublin · Ireland" --estilo minima -o mini.jpg
#   python3 miniatura.py --marco -o marco.png        (solo el marco del estilo "marco", PNG transparente)
ETIQUETA={'ES':'4K · SONIDO AMBIENTE','EN':'4K · AMBIENT SOUND'}
CREMA='#F2EEE6'; TINTA='#2A2C27'; ARENA='#D2B587'; ARENA_OSC='#8C6A3C'
SOMBRA='0 2px 14px rgba(0,0,0,.45), 0 1px 3px rgba(0,0,0,.35)'
def camino(lw=300,col=ARENA,sombra=True):
    # el lienzo deja margen para el pin de llegada (arriba hasta y=-33, a la derecha hasta x=lw+15) y la sombra
    d=f'M14 0 C {lw*.21} -26, {lw*.33} 22, {lw*.5} 2 S {lw*.81} -24, {lw-12} 2'
    f='filter:drop-shadow(0 1px 4px rgba(0,0,0,.5));' if sombra else ''
    return f'''<svg width="{lw+34}" height="56" viewBox="-12 -42 {lw+34} 56" style="{f}display:block;overflow:visible">
<circle cx="0" cy="0" r="5" fill="{col}"/><path d="{d}" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round" stroke-dasharray="9 8"/>
<path d="M{lw} 6 c-9 -12 -14 -17 -14 -24 a14 14 0 0 1 28 0 c0 7 -5 12 -14 24z" fill="none" stroke="{col}" stroke-width="2.8" stroke-linejoin="round"/><circle cx="{lw}" cy="-18" r="4.5" fill="{col}"/></svg>'''
def html(estilo='ventana',foto=None,titulo='',lugar='',etiqueta='',texto=True):
    fuentes=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fuentes')
    img=''
    if foto:
        mime=mimetypes.guess_type(foto)[0] or 'image/jpeg'
        img=f'url(data:{mime};base64,{base64.b64encode(open(foto,"rb").read()).decode()})'
    css=f'''@font-face{{font-family:CG;src:url(file://{fuentes}/CG.ttf);font-weight:300 700}}
@font-face{{font-family:JS;src:url(file://{fuentes}/JS.ttf);font-weight:100 700}}
html,body{{margin:0;background:transparent}}
#m{{position:relative;width:1280px;height:720px;overflow:hidden;font-family:CG}}
#foto{{position:absolute;inset:0;background:{img or 'none'} center/cover}}
#ti{{font-weight:600;line-height:.98;text-wrap:balance;font-variant-numeric:lining-nums}}
.js{{font-family:JS;font-weight:600}}
.sh{{text-shadow:{SOMBRA}}}'''
    if estilo=='ventana':
        tam,lineas=92,3
        cuerpo=f'''<div id="m" style="background:{CREMA}">
<div id="foto" style="left:44px;top:44px;width:700px;height:632px;border-radius:30px;box-shadow:0 0 0 2px rgba(42,44,39,.18)"></div>
<div style="position:absolute;left:800px;right:40px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;color:{TINTA}">
<div class="js" style="font-size:20px;letter-spacing:6px;color:{ARENA_OSC};margin-bottom:26px">{etiqueta}</div>
<div id="ti" style="font-size:{tam}px">{titulo}</div>
<div style="margin:16px 0 4px -2px">{camino(300,ARENA_OSC,False)}</div>
<div class="js" style="font-size:24px;letter-spacing:7px">{lugar}</div></div></div>'''
    elif estilo=='minima':
        tam,lineas=112,2
        cuerpo=f'''<div id="m"><div id="foto"></div>
<div style="position:absolute;inset:0;background:linear-gradient(to top,rgba(20,26,38,.7),rgba(20,26,38,0) 50%)"></div>
<div style="position:absolute;left:60px;right:60px;bottom:54px;text-align:center;color:{CREMA}">
<div id="ti" class="sh" style="font-size:{tam}px">{titulo}</div>
<div style="display:flex;justify-content:center;margin:12px 0 2px">{camino(300)}</div>
<div class="js sh" style="font-size:26px;letter-spacing:9px">{lugar}</div></div></div>'''
    else:  # marco
        tam,lineas=110,2
        txt=f'''<div class="js sh" style="position:absolute;left:62px;top:56px;font-size:22px;letter-spacing:6px;color:{CREMA}">{etiqueta}</div>
<div style="position:absolute;left:66px;right:66px;bottom:60px;color:{CREMA}"><div id="ti" class="sh" style="font-size:{tam}px;max-width:1080px">{titulo}</div>
<div style="margin:8px 0 2px 0">{camino(300)}</div><div class="js sh" style="font-size:26px;letter-spacing:8px;margin-left:4px">{lugar}</div></div>''' if texto else ''
        cuerpo=f'''<div id="m">{'<div id="foto"></div>' if img else ''}
<div style="position:absolute;inset:0;background:linear-gradient(to bottom,rgba(20,26,38,.5) 0%,rgba(20,26,38,0) 22%),linear-gradient(to top,rgba(20,26,38,.74) 0%,rgba(20,26,38,.38) 30%,rgba(20,26,38,0) 56%)"></div>
<div style="position:absolute;inset:24px;border:3px solid rgba(242,238,230,.92);border-radius:26px;box-shadow:0 0 12px rgba(0,0,0,.25),inset 0 0 12px rgba(0,0,0,.18)"></div>{txt}</div>'''
    # el título se achica solo si no entra en el máximo de líneas del estilo
    js=f'''const t=document.getElementById('ti'); if(t){{let s={tam}; while(t.offsetHeight>{lineas}*s*1.0+4 && s>48){{s-=4; t.style.fontSize=s+'px';}}}}'''
    return f'<html><head><meta charset="utf-8"><style>{css}</style></head><body>{cuerpo}<script>{js}</script></body></html>'
async def render(path,doc,transparente):
    tmp=os.path.join(os.path.dirname(os.path.abspath(__file__)),'_m.html'); open(tmp,'w').write(doc)
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1280,'height':720})
        await pg.goto('file://'+tmp); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(200)
        jpg=path.lower().endswith(('.jpg','.jpeg'))
        await pg.screenshot(path=path,omit_background=transparente and not jpg,type='jpeg' if jpg else 'png',**({'quality':92} if jpg else {}))
        await b.close()
    os.remove(tmp)
# ---------- modo "cozy otoño": color cálido + viñeta + hojas cayendo (miniatura del Grand Canal, 18/10) ----------
def calidez(foto,salida,pos_y=.45):
    """Recorta a 16:9 (pos_y: 0 arriba … 1 abajo), calienta el color y agrega viñeta suave. Lee HEIC si está pillow-heif."""
    from PIL import Image, ImageEnhance, ImageOps
    import numpy as np
    try:
        import pillow_heif; pillow_heif.register_heif_opener()
    except ImportError: pass
    im=ImageOps.exif_transpose(Image.open(foto)).convert('RGB'); w,h=im.size; ch=int(w*9/16)
    if ch<=h: y0=int((h-ch)*pos_y); im=im.crop((0,y0,w,y0+ch))
    im=im.resize((2560,1440),Image.LANCZOS); a=np.asarray(im).astype(float)/255; a=a**0.95
    a[...,0]=a[...,0]*1.07+0.02; a[...,1]=a[...,1]*1.02+0.01; a[...,2]=a[...,2]*0.88
    yy,xx=np.mgrid[0:1440,0:2560]; r=np.sqrt(((xx-1280)/1280)**2+((yy-720)/720)**2)
    a*=(1-0.32*np.clip(r-0.55,0,1)**1.4)[...,None]
    im=Image.fromarray((np.clip(a,0,1)*255).astype('uint8'))
    im=ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.12)).enhance(1.05); im.save(salida,quality=95)
def hojas_otono():
    import sendero as S
    h=''.join(S.hoja_arce(x,y,s,r,c) if k%2==0 else S.hoja_oval(x,y,s*.9,r,c) for k,(x,y,s,r,c) in enumerate([(1120,95,1.5,20,'#E3A040'),(1200,190,1.1,-35,'#C8682E'),(1060,240,.9,50,'#D98A3A'),(1215,315,.8,10,'#B5532A'),(980,130,.7,-15,'#E3B052')]))
    return f'<svg style="position:absolute;left:0;top:0;overflow:visible;filter:drop-shadow(0 3px 6px rgba(0,0,0,.35))" width="1280" height="720">{h}</svg>'
if __name__=='__main__':
    a=argparse.ArgumentParser(description='Miniatura de YouTube con la estética de Elita')
    a.add_argument('foto',nargs='?'); a.add_argument('titulo',nargs='?',default=''); a.add_argument('lugar',nargs='?',default='')
    a.add_argument('--estilo',choices=['marco','ventana','minima'],default='marco')
    a.add_argument('--lang',choices=['ES','EN'],default='EN'); a.add_argument('--etiqueta',help='texto de arriba (por defecto 4K · AMBIENT SOUND / SONIDO AMBIENTE; "" para ninguno)')
    a.add_argument('--marco',action='store_true',help='solo el marco del estilo "marco", sin foto ni texto (PNG transparente)')
    a.add_argument('--otono',action='store_true',help='modo cozy otoño: color cálido, viñeta y hojas cayendo (acepta HEIC)')
    a.add_argument('--pos-y',type=float,default=.45,help='dónde recortar la foto a 16:9 (0 arriba, 1 abajo)')
    a.add_argument('-o','--salida',default='miniatura.jpg')
    o=a.parse_args()
    et=ETIQUETA[o.lang] if o.etiqueta is None else o.etiqueta
    if o.marco: doc=html('marco',None,texto=False)
    else:
        foto=o.foto
        if o.otono:
            foto=os.path.splitext(o.salida)[0]+'_calida.jpg'; calidez(o.foto,foto,o.pos_y)
        doc=html(o.estilo,foto,o.titulo,o.lugar.upper(),et)
        if o.otono: doc=doc.replace('</div><script>',hojas_otono()+'</div><script>',1)
    asyncio.run(render(o.salida,doc,transparente=o.marco))

import asyncio, os
from playwright.async_api import async_playwright
import yt as Y
# Marcas de agua para video: 1) "Elita" + camino punteado, 2) monograma "E" en círculo,
# 3) "ADVENTURES" + camino punteado.
# PNG transparente a 2x, en crema y tinta. La versión "_video" lleva un halo oscuro suave
# para que se lea sobre cualquier escena (cielo claro, lluvia, noche) mientras el fondo cambia.
COL={'crema':('#F2EEE6','#F2EEE6'),'tinta':('#2A2C27','#8C6A3C')}
HALO='''<filter id="sh" x="-40%" y="-80%" width="180%" height="260%">
<feMorphology in="SourceAlpha" operator="dilate" radius="12" result="d"/><feGaussianBlur in="d" stdDeviation="22" result="b"/>
<feFlood flood-color="#141A26" flood-opacity=".5"/><feComposite in2="b" operator="in" result="halo"/>
<feMerge><feMergeNode in="halo"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'''
def camino(x,y,lw,sand):
    # camino más grueso que en el logo para que se lea a tamaño de marca de agua
    return Y.trail(x,y,lw,'punteado',col=sand).replace('stroke-dasharray="9 9" stroke-width="2.6"','stroke-dasharray="13 11" stroke-width="5"').replace('stroke-width="2.6"','stroke-width="4.5"')
def elita(ink,sand):
    w,h=700,360
    b=f'<text x="{w/2}" y="205" text-anchor="middle" font-family="CG" font-weight="600" font-size="170" fill="{ink}">Elita</text>'
    b+=camino(w/2-200,255,400,sand)
    return w,h,b
def monograma(ink,sand):
    w=h=420; c=w/2
    b=f'<circle cx="{c}" cy="{c}" r="128" fill="none" stroke="{ink}" stroke-width="5"/>'
    b+=f'<text x="{c}" y="{c+46}" text-anchor="middle" font-family="CG" font-weight="600" font-size="170" fill="{ink}">E</text>'
    b+=f'<path d="M{c-58} {c+84} C {c-30} {c+70}, {c-6} {c+96}, {c+22} {c+82} S {c+48} {c+74}, {c+58} {c+80}" fill="none" stroke="{sand}" stroke-width="5" stroke-linecap="round" stroke-dasharray="9 9"/>'
    b+=f'<circle cx="{c-60}" cy="{c+85}" r="6" fill="{sand}"/><circle cx="{c+60}" cy="{c+80}" r="6" fill="{sand}"/>'
    return w,h,b
def adventures(ink,sand):
    w,h,ls=1000,320,24
    # letter-spacing deja un espacio extra tras la última letra: se compensa corriendo el centro ls/2
    b=f'<text x="{w/2+ls/2}" y="150" text-anchor="middle" font-family="JS" font-weight="600" font-size="72" letter-spacing="{ls}" fill="{ink}">ADVENTURES</text>'
    b+=camino(w/2-360,215,720,sand)
    return w,h,b
DISENOS=[('1-elita-camino',elita),('2-monograma',monograma),('3-adventures-camino',adventures)]
def svg(fn,ink,sand,video):
    w,h,b=fn(ink,sand)
    g=f'<g filter="url(#sh)">{b}</g>' if video else b
    return w,h,f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{HALO}</defs>{g}</svg>'
# Vista previa: cada fila es una marca, cada columna un cuadro de video (1920x1080 a escala),
# incluido el peor caso: cielo nublado casi blanco. Marca al ~12 % del ancho, opacidad 80 %.
CW,CH,GAP=768,432,12
FONDOS=[('ar_ba','0 150 220 124'),('de','0 0 220 124'),('ie','0 150 220 124'),('nt','0 0 220 124'),('cielo',None)]
def preview():
    out=''
    for r,(_,fn) in enumerate(DISENOS):
        for c,(k,vb) in enumerate(FONDOS):
            x,y=c*(CW+GAP),r*(CH+GAP)
            if vb: out+=f'<svg x="{x}" y="{y}" width="{CW}" height="{CH}" viewBox="{vb}" preserveAspectRatio="xMidYMid slice"><g filter="url(#sat)">{Y.P[k]}</g></svg>'
            else: out+=f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" fill="url(#cielo)"/>'
            w,h,m=fn('#F2EEE6','#F2EEE6')
            sc={elita:CW*.12/400,monograma:CW*.075/260,adventures:CW*.16/740}[fn]
            out+=f'<g transform="translate({x+CW-w*sc-CW*.025},{y+CH-h*sc-CH*.03}) scale({sc})" opacity=".8"><g filter="url(#sh)">{m}</g></g>'
    W=5*CW+4*GAP; H=3*CH+2*GAP
    return W,H,f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><defs>{HALO}<filter id="sat"><feColorMatrix type="saturate" values="{Y.SAT}"/></filter><linearGradient id="cielo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9dee0"/><stop offset="1" stop-color="#f4f5f3"/></linearGradient></defs><rect width="{W}" height="{H}" fill="#fff"/>{out}</svg>'
# Marca elegida (ADVENTURES + camino) ya ubicada en un cuadro completo transparente:
# se arrastra a la pista de arriba en Premiere sin escalar ni mover. Opacidad 80 % incluida.
def cuadro(fw,fh):
    w,h,m=adventures('#F2EEE6','#F2EEE6')
    sc=fw*.16/740
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{fw}" height="{fh}"><defs>{HALO}</defs><g transform="translate({fw-w*sc-fw*.025},{fh-h*sc-fh*.03}) scale({sc})" opacity=".8"><g filter="url(#sh)">{m}</g></g></svg>'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        async def r(pg,path,s,w,h,transparent=True):
            os.makedirs(os.path.dirname(path),exist_ok=True)
            open('_y.html','w').write(f'<html><head><meta charset="utf-8"><style>{Y.CSS}</style></head><body>{s}</body></html>')
            await pg.set_viewport_size({'width':w,'height':h}); await pg.goto('file://'+os.getcwd()+'/_y.html')
            await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(200)
            await pg.screenshot(path=path,omit_background=transparent,clip={'x':0,'y':0,'width':w,'height':h})
        pg=await b.new_page(device_scale_factor=2)
        for dname,fn in DISENOS:
            for cname,(ink,sand) in COL.items():
                for video in (False,True):
                    w,h,s=svg(fn,ink,sand,video)
                    await r(pg,f'marca/{dname}/{cname}{"_video" if video else ""}.png',s,w,h)
        pv=await b.new_page()
        for nombre,fw,fh in [('1080p',1920,1080),('4K',3840,2160)]:
            await r(pv,f'marca/elegida-adventures-camino/marca-de-agua_{nombre}.png',cuadro(fw,fh),fw,fh)
        W,H,s=preview()
        await r(pv,'marca/vista-previa.png',s,W,H,False)
        await b.close()
if __name__=="__main__": asyncio.run(main())

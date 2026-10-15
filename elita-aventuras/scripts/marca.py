import asyncio, os
from playwright.async_api import async_playwright
import yt as Y
# Marcas de agua: 1) "Elita" + camino punteado, 2) monograma "E" en círculo.
# Se exportan en PNG transparente a 2x, en crema (para video) y tinta (para fondos claros),
# con y sin sombra suave (mismo estilo que las placas de los videos).
COL={'crema':('#F2EEE6','#F2EEE6'),'tinta':('#2A2C27','#8C6A3C')}
SHADOW='<filter id="sh" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="2" stdDeviation="6" flood-color="#000" flood-opacity=".45"/></filter>'
def elita(ink,sand,shadow):
    w,h=560,250
    b=f'<text x="{w/2}" y="150" text-anchor="middle" font-family="CG" font-weight="600" font-size="170" fill="{ink}">Elita</text>'
    # camino más grueso que en el logo para que se lea a tamaño de marca de agua
    b+=Y.trail(w/2-200,200,400,'punteado',col=sand).replace('stroke-dasharray="9 9" stroke-width="2.6"','stroke-dasharray="13 11" stroke-width="5"').replace('stroke-width="2.6"','stroke-width="4.5"')
    return w,h,b
def monograma(ink,sand,shadow):
    w=h=300; c=w/2
    b=f'<circle cx="{c}" cy="{c}" r="128" fill="none" stroke="{ink}" stroke-width="5"/>'
    b+=f'<text x="{c}" y="{c+46}" text-anchor="middle" font-family="CG" font-weight="600" font-size="170" fill="{ink}">E</text>'
    b+=f'<path d="M{c-58} {c+84} C {c-30} {c+70}, {c-6} {c+96}, {c+22} {c+82} S {c+48} {c+74}, {c+58} {c+80}" fill="none" stroke="{sand}" stroke-width="5" stroke-linecap="round" stroke-dasharray="9 9"/>'
    b+=f'<circle cx="{c-60}" cy="{c+85}" r="6" fill="{sand}"/><circle cx="{c+60}" cy="{c+80}" r="6" fill="{sand}"/>'
    return w,h,b
def svg(fn,ink,sand,shadow):
    w,h,b=fn(ink,sand,shadow)
    g=f'<g filter="url(#sh)">{b}</g>' if shadow else b
    return w,h,f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs>{SHADOW}</defs>{g}</svg>'
def preview():
    # Simula un cuadro de video 1920x1080 por escena, con la marca en la esquina inferior derecha.
    out=''
    for i,k in enumerate(Y.ORDER):
        x,y=(i%2)*980,(i//2)*560
        bg=f'<svg x="{x}" y="{y}" width="960" height="540" viewBox="0 40 220 124" preserveAspectRatio="xMidYMid slice"><g filter="url(#sat)">{Y.P[k]}</g></svg>'
        fn=elita if i%2==0 else monograma
        w,h,m=fn('#F2EEE6','#F2EEE6',True)
        sc=0.32 if fn is elita else 0.26
        out+=bg+f'<g transform="translate({x+960-w*sc-28},{y+540-h*sc-24}) scale({sc})" opacity=".8" filter="url(#sh)">{m}</g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1940" height="1100"><defs>{SHADOW}<filter id="sat"><feColorMatrix type="saturate" values="{Y.SAT}"/></filter></defs><rect width="1940" height="1100" fill="#fff"/>{out}</svg>'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(device_scale_factor=2)
        async def r(path,s,w,h,transparent=True):
            os.makedirs(os.path.dirname(path),exist_ok=True)
            open('_y.html','w').write(f'<html><head><meta charset="utf-8"><style>{Y.CSS}</style></head><body>{s}</body></html>')
            await pg.set_viewport_size({'width':w,'height':h}); await pg.goto('file://'+os.getcwd()+'/_y.html')
            await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(200)
            await pg.screenshot(path=path,omit_background=transparent,clip={'x':0,'y':0,'width':w,'height':h})
        for dname,fn in [('1-elita-camino',elita),('2-monograma',monograma)]:
            for cname,(ink,sand) in COL.items():
                for sh in (False,True):
                    w,h,s=svg(fn,ink,sand,sh)
                    await r(f'marca/{dname}/{cname}{"_sombra" if sh else ""}.png',s,w,h)
        await pg.set_viewport_size({'width':1940,'height':1100})
        await r('marca/vista-previa.png',preview(),1940,1100,False)
        await b.close()
if __name__=="__main__": asyncio.run(main())

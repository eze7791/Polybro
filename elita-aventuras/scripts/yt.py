import asyncio, os
from playwright.async_api import async_playwright
import logo as L
P,W,H,G=L.P,L.W,L.H,L.G
ORDER=['ar_ba','de','ie','nt']
CREAM='#F2EEE6'; INK='#2A2C27'; SAND='#8C6A3C'; SAT=0.55
STYLES={'puntos':'stroke-dasharray="0.1 11" stroke-width="5.5"','punteado':'stroke-dasharray="9 9" stroke-width="2.6"','continuo':'stroke-width="2.6"'}
def trail(x,y,lw,style,col=SAND,marks=True,sc=1):
    return f'''<g transform="translate({x},{y}) scale({sc})">{f'<circle cx="0" cy="0" r="6" fill="{col}"/>' if marks else ''}
<path d="M14 0 C {lw*.21} -26, {lw*.33} 22, {lw*.5} 2 S {lw*.81} -24, {lw-12} 2" fill="none" stroke="{col}" stroke-linecap="round" {STYLES[style]}/>
{f'<path d="M{lw} 6 c-9 -12 -14 -17 -14 -24 a14 14 0 0 1 28 0 c0 7 -5 12 -14 24z" fill="none" stroke="{col}" stroke-width="2.6"/><circle cx="{lw}" cy="-18" r="4.5" fill="{col}"/>' if marks else ''}</g>'''
def windows(x,y,sc,grid='row',uid='w'):
    out=''
    for i,k in enumerate(ORDER):
        if grid=='row': px,py=i*(W+G),0
        else: px,py=(i%2)*(W+G),(i//2)*(H+G)
        out+=f'<g transform="translate({px},{py})"><clipPath id="{uid}{i}"><rect width="{W}" height="{H}" rx="22"/></clipPath><g clip-path="url(#{uid}{i})">{P[k]}</g><rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="22" fill="none" stroke="{INK}" stroke-opacity=".22" stroke-width="1.5"/></g>'
    return f'<g transform="translate({x},{y}) scale({sc})" filter="url(#sat)">{out}</g>'
DEFS=f'<defs><filter id="sat"><feColorMatrix type="saturate" values="{SAT}"/></filter></defs>'
def hills(w,h,op=.10):
    return f'''<g fill="none" stroke="{SAND}" stroke-opacity="{op}" stroke-width="3">
<path d="M0 {h-120} C {w*.15} {h-210}, {w*.3} {h-90}, {w*.45} {h-150} S {w*.75} {h-230}, {w} {h-130}"/>
<path d="M0 {h-60} C {w*.2} {h-130}, {w*.35} {h-30}, {w*.55} {h-90} S {w*.85} {h-150}, {w} {h-70}"/></g>'''
TAG_ES='Calles y caminos, sólo con sonido ambiente'
TAG_EN='Streets and trails, ambient sound only'
def tagline(x,y,anchor='start',size=1):
    return f'''<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="CG" font-style="italic" font-weight="600" font-size="{int(58*size)}" fill="{INK}">{TAG_ES}</text>
<text x="{x}" y="{y+int(62*size)}" text-anchor="{anchor}" font-family="JS" font-weight="600" font-size="{int(26*size)}" letter-spacing="{int(8*size)}" fill="{SAND}">{TAG_EN.upper()}</text>'''
def svg(w,h,body): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{DEFS}<rect width="{w}" height="{h}" fill="{CREAM}"/>{body}</svg>'
# --- perfiles 800x800
def perfil_ventanas(style):
    sc=0.84; gw=(2*W+G)*sc; gh=(2*H+G)*sc
    x=(800-gw)/2; y=(800-gh)/2-26
    return svg(800,800,windows(x,y,sc,'grid','p')+trail(400-160,y+gh+46,320,style,marks=True,sc=1))
def perfil_nombre(style):
    return svg(800,800,f'<text x="400" y="440" text-anchor="middle" font-family="CG" font-weight="600" font-size="250" fill="{INK}">Elita</text>'+trail(400-230,505,460,style))
# --- banners 2560x1440, safe 1546x423 centrado (507..2053, 508..931)
def banner_nombre(style):
    b=hills(2560,1440)
    cx=1000
    b+=f'<text x="{cx}" y="745" text-anchor="middle" font-family="CG" font-weight="600" font-size="190" fill="{INK}">Elita</text>'
    b+=f'<text x="{cx}" y="890" text-anchor="middle" font-family="JS" font-weight="600" font-size="46" letter-spacing="19" fill="{INK}">ADVENTURES</text>'
    b+=trail(cx-280,810,560,style)
    b+=f'<line x1="1330" y1="590" x2="1330" y2="860" stroke="{SAND}" stroke-opacity=".5" stroke-width="2"/>'
    for k,t in enumerate(['Calles y caminos,','sólo con sonido ambiente']):
        b+=f'<text x="1400" y="{690+k*66}" font-family="CG" font-style="italic" font-weight="600" font-size="58" fill="{INK}">{t}</text>'
    b+=f'<text x="1402" y="840" font-family="CG" font-style="italic" font-weight="500" font-size="36" fill="{SAND}">Streets and trails, ambient sound only</text>'
    return svg(2560,1440,b)
def banner_ventanas(style):
    sc=1.0; gw=(4*W+3*G)*sc; gh=H*sc
    x=540; y=720-gh/2
    b=hills(2560,1440)+windows(x,y,sc,'row','b')
    tx=x+gw+70
    for k,t in enumerate(['Calles y caminos,','sólo con sonido','ambiente']):
        b+=f'<text x="{tx}" y="{640+k*64}" font-family="CG" font-style="italic" font-weight="600" font-size="56" fill="{INK}">{t}</text>'
    b+=trail(tx+4,812,420,style)
    for k,t in enumerate(['Streets and trails,','ambient sound only']):
        b+=f'<text x="{tx}" y="{870+k*40}" font-family="CG" font-style="italic" font-weight="500" font-size="34" fill="{SAND}">{t}</text>'
    return svg(2560,1440,b)
CSS='@font-face{font-family:CG;src:url(../fuentes/CG.ttf);font-weight:300 700;font-style:normal}@font-face{font-family:CG;src:url(../fuentes/CGi.ttf);font-weight:300 700;font-style:italic}@font-face{font-family:JS;src:url(../fuentes/JS.ttf);font-weight:100 700}html,body{margin:0}'
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page()
        async def r(path,s,w,h):
            os.makedirs(os.path.dirname(path),exist_ok=True)
            open('_y.html','w').write(f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{s}</body></html>')
            await pg.set_viewport_size({'width':w,'height':h}); await pg.goto('file://'+os.getcwd()+'/_y.html')
            await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(200)
            await pg.screenshot(path=path,clip={'x':0,'y':0,'width':w,'height':h})
        for st in STYLES:
            await r(f'yt/{st}/combo-1/perfil-ventanas.png',perfil_ventanas(st),800,800)
            await r(f'yt/{st}/combo-1/banner-nombre.png',banner_nombre(st),2560,1440)
            await r(f'yt/{st}/combo-2/perfil-nombre.png',perfil_nombre(st),800,800)
            await r(f'yt/{st}/combo-2/banner-ventanas.png',banner_ventanas(st),2560,1440)
        await b.close()
if __name__=="__main__": asyncio.run(main())

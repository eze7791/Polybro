import asyncio, os
from playwright.async_api import async_playwright
import yt as Y
Y_BAN=Y.banner_ventanas
def banner(bg='#F2EEE6',ink='#2A2C27',sand='#8C6A3C',variant='A'):
    W,H,G=Y.W,Y.H,Y.G
    sc=0.9; gw=(4*W+3*G)*sc; gh=H*sc; x=530; y=720-gh/2
    b=f'<rect width="2560" height="1440" fill="{bg}"/>'+Y.hills(2560,1440).replace(Y.SAND,sand)+Y.windows(x,y,sc,'row','b')
    tx=x+gw+64; top=y; bot=y+gh
    def T(yy,txt,fam,size,col,w=600,it=False,ls=0,op=1):
        return f'<text x="{tx}" y="{yy}" font-family="{fam}" font-weight="{w}" font-size="{size}" letter-spacing="{ls}" fill="{col}" fill-opacity="{op}"{" font-style=\'italic\'" if it else ""}>{txt}</text>'
    if variant in ('ES','EN'):
        L={'ES':['Calles y caminos,','sólo con sonido','ambiente.'],'EN':['Streets and trails,','ambient','sound only.']}[variant]
        b+=T(top+66,L[0],'CG',76,ink)
        b+=T(top+66+98,L[1],'CG',76,ink,it=True)
        b+=T(top+66+196,L[2],'CG',76,ink,it=True)
    elif variant=='ES2':  # dos líneas: "Calles y caminos," / "sólo sonido ambiente." (pedido de Ivan, 18/10)
        mid=(top+bot)/2
        b+=T(mid-12,'Calles y caminos,','CG',88,ink)
        b+=T(mid+90,'sólo sonido ambiente.','CG',72,ink,it=True)
    elif variant=='A':
        b+=T(top+56,'Calles y caminos,','CG',72,ink)
        b+=T(top+126,'sólo con sonido ambiente','CG',54,ink,it=True)
        b+=f'<line x1="{tx+2}" y1="{bot-92}" x2="{tx+60}" y2="{bot-92}" stroke="{sand}" stroke-width="2.4"/>'
        b+=T(bot-46,'STREETS AND TRAILS','JS',24,sand,ls=7)
        b+=T(bot-6,'AMBIENT SOUND ONLY','JS',24,sand,ls=7)
    elif variant=='B':
        b+=T(top+44,'CALLES Y CAMINOS','JS',40,ink,ls=9)
        b+=T(top+100,'sólo con sonido ambiente','CG',52,ink,it=True)
        b+=f'<line x1="{tx+2}" y1="{bot-92}" x2="{tx+60}" y2="{bot-92}" stroke="{sand}" stroke-width="2.4"/>'
        b+=T(bot-44,'STREETS AND TRAILS','JS',24,sand,ls=7)
        b+=T(bot-6,'ambient sound only','CG',36,sand,it=True,w=500)
    else:
        b+=T(top+56,'Calles y caminos,','CG',58,ink)
        b+=T(top+116,'sólo con sonido ambiente.','CG',58,ink)
        b+=f'<line x1="{tx+2}" y1="{bot-92}" x2="{tx+60}" y2="{bot-92}" stroke="{sand}" stroke-width="2.4"/>'
        b+=T(bot-46,'Streets and trails,','CG',40,ink,it=True,w=500,op=.6)
        b+=T(bot-6,'ambient sound only.','CG',40,ink,it=True,w=500,op=.6)
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="2560" height="1440">{Y.DEFS}{b}</svg>'
def perfil(bg,ink,sand,ink2=None,grad=None):
    ink2=ink2 or ink
    fill=f'url(#g)' if grad else bg
    gdef=f'<linearGradient id="g" x1="0" y1="0" x2="0" y2="1">{"".join(f"<stop offset=\"{o}\" stop-color=\"{c}\"/>" for o,c in grad)}</linearGradient>' if grad else ''
    b=f'<defs>{gdef}</defs><rect width="800" height="800" fill="{fill}"/>'
    b+=f'<text x="400" y="408" text-anchor="middle" font-family="CG" font-weight="600" font-size="230" fill="{ink}">Elita</text>'
    b+=Y.trail(400-210,470,420,'punteado',col=sand)
    b+=f'<text x="402" y="555" text-anchor="middle" font-family="JS" font-weight="600" font-size="46" letter-spacing="17" fill="{ink2}">ADVENTURES</text>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800">{b}</svg>'
PERF={
 '1-crema':dict(bg='#F2EEE6',ink='#2A2C27',sand='#8C6A3C'),
 '2-amanecer-argentina':dict(bg=None,ink='#FBF4EA',sand='#FBE7C8',grad=[(0,'#8f86b3'),(.55,'#c99aa0'),(1,'#e8b98e')]),
 '3-dia-alemania':dict(bg=None,ink='#2F3E4C',sand='#5D7D5C',grad=[(0,'#a9c3d6'),(1,'#e3ecef')]),
 '4-lluvia-irlanda':dict(bg=None,ink='#F3F1EA',sand='#E2E6DC',grad=[(0,'#8f9b97'),(1,'#5f7f5c')]),
 '5-noche-auroras':dict(bg=None,ink='#EEE7DA',sand='#8FD3B0',ink2='#EEE7DA',grad=[(0,'#141c33'),(.6,'#1e2d48'),(1,'#22334d')]),
}
CSS=Y.CSS
async def main():
    [os.makedirs('yt2/'+d,exist_ok=True) for d in ('ES','EN','A','B','C')]
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page()
        async def r(path,s,w,h):
            open('_y.html','w').write(f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{s}</body></html>')
            await pg.set_viewport_size({'width':w,'height':h}); await pg.goto('file://'+os.getcwd()+'/_y.html')
            await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(200)
            await pg.screenshot(path=path,clip={'x':0,'y':0,'width':w,'height':h})
        for v in ('ES','EN','A','B','C'):
            await r(f'yt2/{v}/banner-crema.png',banner(variant=v),2560,1440)
            await r(f'yt2/{v}/banner-noche.png',banner('#1A2236','#EEE7DA','#C9A978',variant=v),2560,1440)
        for k,v in PERF.items(): await r(f'yt2/perfil-{k}.png',perfil(**v),800,800)
        await b.close()
asyncio.run(main())

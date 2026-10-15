import asyncio, os, shutil, subprocess, sys
from playwright.async_api import async_playwright
import yt as Y
# Opening (logo animado) y pantalla final para los videos.
# Se dibuja un SVG con ids, una función JS lo pone en el instante t, y cada cuadro se captura con
# Playwright; ffmpeg arma el MP4. Uso: python3 video.py [1080|4K]
FPS=30
W,H,G=Y.W,Y.H,Y.G
TEMAS={'crema':dict(bg='#F2EEE6',ink='#2A2C27',sand='#8C6A3C'),
       'noche':dict(bg='#1A2236',ink='#EEE7DA',sand='#C9A978')}
TXT={'EN':(['Thanks for walking','with me.'],'SUBSCRIBE'),'ES':(['Gracias por caminar','conmigo.'],'SUSCRIBITE')}
LW=520
TRAIL_D=f'M14 0 C {LW*.21} -26, {LW*.33} 22, {LW*.5} 2 S {LW*.81} -24, {LW-12} 2'
PIN=f'M{LW} 6 c-9 -12 -14 -17 -14 -24 a14 14 0 0 1 28 0 c0 7 -5 12 -14 24z'
def ventanas(ink,ids=True):
    out=''
    for i,k in enumerate(Y.ORDER):
        out+=f'''<g{f' id="w{i}"' if ids else ''} transform="translate({i*(W+G)},0)"><clipPath id="c{i}"><rect width="{W}" height="{H}" rx="22"/></clipPath>
<g clip-path="url(#c{i})">{Y.P[k]}</g><rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="22" fill="none" stroke="{ink}" stroke-opacity=".22" stroke-width="1.5"/></g>'''
    return f'<g filter="url(#sat)">{out}</g>'
def defs():
    return f'''<defs><filter id="sat"><feColorMatrix type="saturate" values="{Y.SAT}"/></filter>
<mask id="draw" maskUnits="userSpaceOnUse" x="-40" y="-60" width="{LW+80}" height="120"><path id="mpath" d="{TRAIL_D}" pathLength="1" fill="none" stroke="#fff" stroke-width="14" stroke-linecap="round" stroke-dasharray="1 1" stroke-dashoffset="1"/></mask></defs>'''
# ---------- opening: logo como en Elita-Logo-camino (camino punteado, muy sobrio) ----------
def opening(bg,ink,sand):
    tw=4*W+3*G; th=H+315; sc=1.12
    x0=(1920-tw*sc)/2; y0=(1080-th*sc)/2
    cx=tw/2
    logo=f'''{ventanas(ink)}
<text id="nm" x="{cx}" y="{H+150}" text-anchor="middle" font-family="CG" font-weight="600" font-size="150" fill="{ink}" opacity="0">Elita</text>
<g transform="translate({cx-LW/2},{H+208})">
<circle id="dot" cx="0" cy="0" r="6.5" fill="{sand}" opacity="0"/>
<path d="{TRAIL_D}" fill="none" stroke="{sand}" stroke-linecap="round" stroke-dasharray="11 9" stroke-width="3.2" mask="url(#draw)"/>
<g id="pin" opacity="0" style="transform-origin:{LW}px 6px"><path d="{PIN}" fill="none" stroke="{sand}" stroke-width="2.8"/><circle cx="{LW}" cy="-18" r="4.5" fill="{sand}"/></g></g>
<text id="adv" x="{cx}" y="{H+285}" text-anchor="middle" font-family="JS" font-weight="600" font-size="40" letter-spacing="17" fill="{ink}" opacity="0">ADVENTURES</text>'''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">{defs()}<rect width="1920" height="1080" fill="{bg}"/><g transform="translate({x0},{y0}) scale({sc})">{logo}</g></svg>'
JS_OPENING='''
const E=t=>1-Math.pow(1-Math.max(0,Math.min(1,t)),3), IO=t=>{t=Math.max(0,Math.min(1,t));return t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2};
const seg=(t,a,b)=>(t-a)/(b-a);
window.setT=t=>{
  for(let i=0;i<4;i++){const p=E(seg(t,.3+.38*i,1.1+.38*i)),g=document.getElementById('w'+i);
    g.setAttribute('opacity',p); g.setAttribute('transform',`translate(${i*240},${(1-p)*26})`);}
  const n=E(seg(t,2.0,2.9)); const nm=document.getElementById('nm'); nm.setAttribute('opacity',n); nm.setAttribute('transform',`translate(0,${(1-n)*14})`);
  document.getElementById('dot').setAttribute('opacity',E(seg(t,2.6,2.9)));
  document.getElementById('mpath').setAttribute('stroke-dashoffset',1-IO(seg(t,2.75,4.0)));
  const pp=E(seg(t,3.85,4.3)), pin=document.getElementById('pin'); pin.setAttribute('opacity',pp); pin.style.transform=`scale(${.6+.4*pp})`;
  const a=E(seg(t,3.5,4.6)), adv=document.getElementById('adv'); adv.setAttribute('opacity',a); adv.setAttribute('letter-spacing',17+10*(1-a));
};'''
OPENING_DUR=6.0
# ---------- pantalla final: ventanas + frase + firma; huecos para elementos de YouTube ----------
# Huecos (1080p): 2 videos 16:9 de 720x405 a la derecha, botón de suscripción (círculo) abajo a la izquierda.
VIDEOS=[(1100,120,720,405),(1100,560,720,405)]
SUBS=(470,800,92)
def final(bg,ink,sand,lang,guias=False):
    lines,subs=TXT[lang]
    sc=.44; tw=4*W+3*G
    b=f'<rect width="1920" height="1080" fill="{bg}"/>'+Y.hills(1920,1080).replace(Y.SAND,sand)
    # grupo exterior para la animación (el style.transform del JS pisaría el transform de posición)
    b+=f'<g id="vw"><g transform="translate({470-tw*sc/2},190) scale({sc})">{ventanas(ink,ids=False)}</g></g>'
    b+=f'<g id="tx">'+''.join(f'<text x="470" y="{462+k*80}" text-anchor="middle" font-family="CG" font-style="italic" font-weight="600" font-size="70" fill="{ink}">{t}</text>' for k,t in enumerate(lines))
    b+=f'<text x="470" y="635" text-anchor="middle" font-family="CG" font-style="italic" font-weight="500" font-size="42" fill="{sand}">— Elita</text></g>'
    cx,cy,r=SUBS
    b+=f'<g id="sb"><circle cx="{cx}" cy="{cy}" r="{r+10}" fill="none" stroke="{sand}" stroke-opacity=".55" stroke-width="2" stroke-dasharray="6 8"/>'
    b+=f'<text x="{cx+4}" y="{cy+r+62}" text-anchor="middle" font-family="JS" font-weight="600" font-size="22" letter-spacing="8" fill="{sand}">{subs}</text></g>'
    if guias:
        for x,y,w,h in VIDEOS:
            b+=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{ink}" fill-opacity=".06" stroke="{ink}" stroke-opacity=".35" stroke-width="2" stroke-dasharray="10 8"/><text x="{x+w/2}" y="{y+h/2+10}" text-anchor="middle" font-family="JS" font-weight="600" font-size="26" letter-spacing="8" fill="{ink}" fill-opacity=".45">VIDEO</text>'
        b+=f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{ink}" fill-opacity=".08"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">{defs()}{b}</svg>'
JS_FINAL='''
const E=t=>1-Math.pow(1-Math.max(0,Math.min(1,t)),3), seg=(t,a,b)=>(t-a)/(b-a);
window.setT=t=>{ [['vw',.0,1.0],['tx',.5,1.5],['sb',1.0,2.0]].forEach(([id,a,b])=>{
  const g=document.getElementById(id),p=E(seg(t,a,b)); g.setAttribute('opacity',p); g.style.transform=`translateY(${(1-p)*16}px)`;});};'''
FINAL_ANIM=2.0; FINAL_DUR=20.0
async def main(res):
    dsf={'1080':1,'4K':2}[res]
    out=f'video/{res}'; os.makedirs(out,exist_ok=True)
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=dsf)
        async def load(svg,js):
            open('_v.html','w').write(f'<html><head><meta charset="utf-8"><style>{Y.CSS}</style></head><body>{svg}<script>{js}</script></body></html>')
            await pg.goto('file://'+os.getcwd()+'/_v.html'); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(300)
        async def frames(dur):
            d='_frames'; shutil.rmtree(d,ignore_errors=True); os.makedirs(d)
            for f in range(round(dur*FPS)):
                await pg.evaluate(f'setT({f/FPS})')
                await pg.screenshot(path=f'{d}/{f:05d}.png')
            return d
        def mp4(d,path,hold=0):
            vf=f'tpad=stop_mode=clone:stop_duration={hold},' if hold else ''
            subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(FPS),'-i',f'{d}/%05d.png','-vf',vf+'format=yuv420p',
                            '-c:v','libx264','-crf','14','-preset','slow','-movflags','+faststart',path],check=True)
        for tema,c in TEMAS.items():
            await load(opening(**c),JS_OPENING)
            mp4(await frames(OPENING_DUR),f'{out}/opening_{tema}.mp4')
            await pg.evaluate(f'setT({OPENING_DUR})'); await pg.screenshot(path=f'{out}/opening_{tema}_ultimo-cuadro.png')
            for lang in TXT:
                await load(final(**c,lang=lang),JS_FINAL)
                mp4(await frames(FINAL_ANIM),f'{out}/pantalla-final_{lang}_{tema}.mp4',hold=FINAL_DUR-FINAL_ANIM)
                await pg.evaluate(f'setT({FINAL_ANIM})'); await pg.screenshot(path=f'{out}/pantalla-final_{lang}_{tema}.png')
                await load(final(**c,lang=lang,guias=True),'window.setT=()=>{}')
                await pg.screenshot(path=f'{out}/pantalla-final_{lang}_{tema}_guias.png')
        await b.close()
    shutil.rmtree('_frames',ignore_errors=True); os.remove('_v.html')
if __name__=="__main__": asyncio.run(main(sys.argv[1] if len(sys.argv)>1 else '1080'))

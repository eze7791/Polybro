import asyncio, os, shutil, subprocess, sys
from playwright.async_api import async_playwright
import yt as Y
# Opening (logo animado) y closing (outro + pantalla final) para los videos.
# Se dibuja un SVG con ids, una función JS lo pone en el instante t, y cada cuadro se captura con
# Playwright; ffmpeg arma el MP4. Uso: python3 video.py [1080|4K] [fps] [opening|closing|todo]  (por defecto 4K 60 todo)
FPS=60
W,H,G=Y.W,Y.H,Y.G
TEMAS={'crema':dict(bg='#F2EEE6',ink='#2A2C27',sand='#8C6A3C'),
       'noche':dict(bg='#1A2236',ink='#EEE7DA',sand='#C9A978')}
TXT={'EN':(['Thanks for walking','with me.'],'SUBSCRIBE',('PREVIOUS','NEXT')),'ES':(['Gracias por caminar','conmigo.'],'SUSCRÍBETE',('ANTERIOR','SIGUIENTE'))}
LW=520
TRAIL_D=f'M14 0 C {LW*.21} -26, {LW*.33} 22, {LW*.5} 2 S {LW*.81} -24, {LW-12} 2'
PIN=f'M{LW} 6 c-9 -12 -14 -17 -14 -24 a14 14 0 0 1 28 0 c0 7 -5 12 -14 24z'
def ventanas(ink,ids=True):
    out=''
    for i,k in enumerate(Y.ORDER):
        out+=f'''<g{f' id="w{i}"' if ids else ''} transform="translate({i*(W+G)},0)"><clipPath id="c{i}"><rect width="{W}" height="{H}" rx="22"/></clipPath>
<g clip-path="url(#c{i})">{Y.P[k]}</g>{f'<rect id="o{i}" width="{W}" height="{H}" rx="22" fill="#0B1020" opacity="0"/>' if ids else ''}<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="22" fill="none" stroke="{ink}" stroke-opacity=".22" stroke-width="1.5"/></g>'''
    return f'<g filter="url(#sat)">{out}</g>'
def defs():
    return f'''<defs><filter id="sat"><feColorMatrix type="saturate" values="{Y.SAT}"/></filter>
<mask id="draw" maskUnits="userSpaceOnUse" x="-40" y="-60" width="{LW+80}" height="120"><path id="mpath" d="{TRAIL_D}" pathLength="1" fill="none" stroke="#fff" stroke-width="14" stroke-linecap="round" stroke-dasharray="1 1" stroke-dashoffset="1"/></mask></defs>'''
# ---------- opening: logo como en Elita-Logo-camino (camino punteado, muy sobrio) ----------
def logo(ink,sand):
    tw=4*W+3*G; th=H+315; sc=1.12
    x0=(1920-tw*sc)/2; y0=(1080-th*sc)/2
    cx=tw/2
    return f'''<g transform="translate({x0},{y0}) scale({sc})">{ventanas(ink)}
<text id="nm" x="{cx}" y="{H+150}" text-anchor="middle" font-family="CG" font-weight="600" font-size="150" fill="{ink}" opacity="0">Elita</text>
<g transform="translate({cx-LW/2},{H+208})">
<circle id="dot" cx="0" cy="0" r="6.5" fill="{sand}" opacity="0"/>
<path d="{TRAIL_D}" fill="none" stroke="{sand}" stroke-linecap="round" stroke-dasharray="11 9" stroke-width="3.2" mask="url(#draw)"/>
<g id="pin" opacity="0" style="transform-origin:{LW}px 6px"><path d="{PIN}" fill="none" stroke="{sand}" stroke-width="2.8"/><circle cx="{LW}" cy="-18" r="4.5" fill="{sand}"/></g></g>
<text id="adv" x="{cx}" y="{H+285}" text-anchor="middle" font-family="JS" font-weight="600" font-size="40" letter-spacing="17" fill="{ink}" opacity="0">ADVENTURES</text></g>'''
def opening(bg,ink,sand):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">{defs()}<rect width="1920" height="1080" fill="{bg}"/>{logo(ink,sand)}</svg>'
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
# ---------- closing: frase de despedida y pantalla final con el nombre, el botón de suscripción
# y 2 cuadros para los videos anterior y siguiente (elementos de YouTube) ----------
# Cuadros (en 1080p): 2 videos 16:9 de 680x383 a la derecha; círculo de suscripción a la izquierda.
VIDEOS=[(1140,150,680,383),(1140,620,680,383)]
SUBS=(470,800,92)
def pantalla_final(ink,sand,lang,guias=False,videos=True):
    subs=TXT[lang][1]; rot=TXT[lang][2]
    b=f'<g id="hl">{Y.hills(1920,1080).replace(Y.SAND,sand)}</g>'
    # sin videos: el nombre y el botón de suscripción se centran
    dx=0 if videos else 490
    b+=f'<g id="e1"><g transform="translate({dx},0)"><text x="470" y="430" text-anchor="middle" font-family="CG" font-weight="600" font-size="150" fill="{ink}">Elita</text>'
    b+=Y.trail(470-200,492,400,'punteado',col=sand)
    b+=f'<text x="478" y="572" text-anchor="middle" font-family="JS" font-weight="600" font-size="38" letter-spacing="15" fill="{ink}">ADVENTURES</text></g></g>'
    cx,cy,r=SUBS
    b+=f'<g id="e2"><g transform="translate({dx},{0 if videos else -40})"><circle cx="{cx}" cy="{cy}" r="{r+10}" fill="none" stroke="{sand}" stroke-opacity=".55" stroke-width="2" stroke-dasharray="6 8"/>'
    b+=f'<text x="{cx+4}" y="{cy+r+62}" text-anchor="middle" font-family="JS" font-weight="600" font-size="22" letter-spacing="8" fill="{sand}">{subs}</text></g></g>'
    # cuadros de video: marco punteado 10 px por fuera del hueco (YouTube pone la miniatura adentro) y etiqueta arriba
    b+='<g id="e3">'
    for (x,y,w,h),lab in (zip(VIDEOS,rot) if videos else []):
        b+=f'<rect x="{x-10}" y="{y-10}" width="{w+20}" height="{h+20}" rx="22" fill="{ink}" fill-opacity=".05" stroke="{sand}" stroke-opacity=".55" stroke-width="2" stroke-dasharray="6 8"/>'
        b+=f'<text x="{x-6}" y="{y-28}" font-family="JS" font-weight="600" font-size="22" letter-spacing="8" fill="{sand}">{lab}</text>'
    b+='</g>'
    if guias:
        for x,y,w,h in (VIDEOS if videos else []):
            b+=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{ink}" fill-opacity=".08"/><text x="{x+w/2}" y="{y+h/2+10}" text-anchor="middle" font-family="JS" font-weight="600" font-size="26" letter-spacing="8" fill="{ink}" fill-opacity=".45">VIDEO</text>'
        b+=f'<circle cx="{cx+dx}" cy="{cy+(0 if videos else -40)}" r="{r}" fill="{ink}" fill-opacity=".08"/>'
    return b
def closing(bg,ink,sand,lang,videos=True):
    lines=TXT[lang][0]
    fw=f'<g id="fw" opacity="0">'+''.join(f'<text x="960" y="{480+k*112}" text-anchor="middle" font-family="CG" font-style="italic" font-weight="600" font-size="100" fill="{ink}">{t}</text>' for k,t in enumerate(lines))
    fw+=f'<text x="960" y="{480+len(lines)*112+20}" text-anchor="middle" font-family="CG" font-style="italic" font-weight="500" font-size="56" fill="{sand}">— Elita</text></g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">{defs()}<rect width="1920" height="1080" fill="{bg}"/>{fw}{pantalla_final(ink,sand,lang,videos=videos)}</svg>'
def final_guias(bg,ink,sand,lang,videos=True):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">{defs()}<rect width="1920" height="1080" fill="{bg}"/>{pantalla_final(ink,sand,lang,guias=True,videos=videos)}</svg>'
JS_CLOSING='''
const E=t=>1-Math.pow(1-Math.max(0,Math.min(1,t)),3), seg=(t,a,b)=>(t-a)/(b-a), $=id=>document.getElementById(id);
const fade=(id,p,dy=16)=>{const g=$(id); g.setAttribute('opacity',p); g.style.transform=`translateY(${(1-p)*dy}px)`;};
window.setT=t=>{
  fade('fw',E(seg(t,.3,1.3))*(1-E(seg(t,3.6,4.2))),12);
  fade('hl',E(seg(t,4.3,5.3)),0); fade('e1',E(seg(t,4.5,5.5))); fade('e2',E(seg(t,4.9,5.9))); fade('e3',E(seg(t,5.1,6.1)));
};'''
CLOSING_ANIM=6.1; FINAL_INICIO=4.2
FINAL_DUR=20.0  # la pantalla final dura 20 s desde FINAL_INICIO (máximo que permite YouTube)
async def main(res,fps,que):
    global FPS; FPS=fps
    dsf={'1080':1,'4K':2}[res]
    out=f'video/{res}-{fps}fps'; os.makedirs(out,exist_ok=True)
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
                            '-c:v','libx264','-crf','16','-preset','slow','-r',str(FPS),'-movflags','+faststart',path],check=True)
        for tema,c in TEMAS.items():
            if que in ('opening','todo'):
                await load(opening(**c),JS_OPENING)
                mp4(await frames(OPENING_DUR),f'{out}/opening_{tema}.mp4')
                await pg.evaluate(f'setT({OPENING_DUR})'); await pg.screenshot(path=f'{out}/opening_{tema}_ultimo-cuadro.png')
            if que in ('closing','closing-sin-videos','todo'):
                vids=que!='closing-sin-videos'; suf='' if vids else '_sin-videos'
                for lang in [l for l in TXT if l in os.environ.get('ELITA_LANGS','ES,EN').split(',')]:
                    await load(closing(**c,lang=lang,videos=vids),JS_CLOSING)
                    mp4(await frames(CLOSING_ANIM),f'{out}/closing{suf}_{lang}_{tema}.mp4',hold=FINAL_INICIO+FINAL_DUR-CLOSING_ANIM)
                    await pg.evaluate(f'setT({CLOSING_ANIM})'); await pg.screenshot(path=f'{out}/pantalla-final{suf}_{lang}_{tema}.png')
                    await load(final_guias(**c,lang=lang,videos=vids),'window.setT=()=>{}')
                    await pg.screenshot(path=f'{out}/pantalla-final{suf}_{lang}_{tema}_guias.png')
        await b.close()
    shutil.rmtree('_frames',ignore_errors=True); os.remove('_v.html')
if __name__=="__main__": a=sys.argv[1:]; asyncio.run(main(a[0] if a else '4K',int(a[1]) if len(a)>1 else 60,a[2] if len(a)>2 else 'todo'))

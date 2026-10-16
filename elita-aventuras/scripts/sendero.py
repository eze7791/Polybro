import asyncio, sys
import agregados as A
# Kit "sendero": cartel de lugar con forma de flecha + círculo con ícono (tipo parche de guardaparques),
# píldora de clima y nota de papel con cinta firmada "— Elita". Papel crema sólido (se lee sobre cualquier
# toma), texto en tinta, color de la temporada en círculos, bordes y detalles. Medidas en unidades 1080p
# (se renderiza a 2x para 4K).
PAPEL='#F4EEE2'; TINTA='#2A2C27'
# Un solo color general para todo (el arena del logo); lo que cambia por época son los iconitos de arriba.
GENERAL=dict(c='#9A7444',o='#5E4626',s='#E3CFA6',c2='#D2B587')
PAL={t:GENERAL for t in ('otono','halloween','invierno','verano')}
def ico(n,col,tam,sw=2.4): return A.icono(n,col,tam,sw)
# ---------- decoraciones chicas por temporada ----------
def hoja_arce(x,y,s,r,c):
    p='M0 -26 L5 -12 L16 -18 L12 -4 L24 -2 L12 6 L16 16 L4 10 L0 24 L-4 10 L-16 16 L-12 6 L-24 -2 L-12 -4 L-16 -18 L-5 -12Z'
    return f'<g transform="translate({x},{y}) rotate({r}) scale({s})"><path d="{p}" fill="{c}" stroke="#7a3f1c" stroke-width="1.6" stroke-linejoin="round"/><path d="M0 24 V-18 M0 6 L10 -2 M0 6 L-10 -2" stroke="#7a3f1c" stroke-width="1.4" fill="none"/></g>'
def hoja_oval(x,y,s,r,c): return f'<g transform="translate({x},{y}) rotate({r}) scale({s})"><path d="M0 -20 C12 -10 12 10 0 20 C-12 10 -12 -10 0 -20Z" fill="{c}" stroke="#7a3f1c" stroke-width="1.6"/><path d="M0 -16 V24" stroke="#7a3f1c" stroke-width="1.4"/></g>'
def murcielago(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><path d="M0 0 C-4 -5 -11 -7 -20 -4 C-16 -2 -15 1 -16 4 C-12 1 -8 2 -6 5 C-4 2 -2 2 0 4 C2 2 4 2 6 5 C8 2 12 1 16 4 C15 1 16 -2 20 -4 C11 -7 4 -5 0 0Z" fill="#3b2a4e" stroke="#F3B26B" stroke-width="1.2" stroke-linejoin="round"/></g>'
def calabaza(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><path d="M-2 -22 C-1 -29 3 -32 7 -32" stroke="#4d6b3a" stroke-width="4.5" fill="none" stroke-linecap="round"/><ellipse cx="-16" cy="0" rx="17" ry="21" fill="#e07a30" stroke="#8a4a1c" stroke-width="1.6"/><ellipse cx="16" cy="0" rx="17" ry="21" fill="#e07a30" stroke="#8a4a1c" stroke-width="1.6"/><ellipse cx="0" cy="0" rx="16" ry="23" fill="#ee8c3c" stroke="#8a4a1c" stroke-width="1.6"/><path d="M-8 -18 C-10 0 -10 10 -8 20 M8 -18 C10 0 10 10 8 20" stroke="#c96a26" stroke-width="1.6" fill="none"/></g>'
def copo(x,y,s,c='#ffffff'): return f'<g transform="translate({x},{y}) scale({s})" stroke="{c}" stroke-width="3" stroke-linecap="round" fill="none" style="filter:drop-shadow(0 1px 2px rgba(40,70,100,.6))"><path d="M0 -20 V20 M-17.3 -10 L17.3 10 M-17.3 10 L17.3 -10"/><path d="M-5 -15 l5 5 l5 -5 M-5 15 l5 -5 l5 5"/></g>'
def sol(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><g stroke="#E9A93A" stroke-width="4" stroke-linecap="round">'+''.join(f'<path d="M0 -26 V-36" transform="rotate({a})"/>' for a in range(0,360,45))+'</g><circle r="19" fill="#F5C85C" stroke="#C98A2A" stroke-width="2"/></g>'
def caracola(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><path d="M-16 10 C-18 -6 -6 -18 6 -14 C16 -10 18 2 10 10 C4 15 -6 14 -16 10Z" fill="#F6D7C3" stroke="#B9806A" stroke-width="1.8"/><path d="M-12 8 L4 -12 M-6 10 L8 -8 M0 11 L12 -2" stroke="#B9806A" stroke-width="1.5"/></g>'
def fantasma(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><path d="M-16 18 V-4 C-16 -16 -8 -24 0 -24 C8 -24 16 -16 16 -4 V18 L10 13 L5 18 L0 13 L-5 18 L-10 13Z" fill="#FBF7F0" stroke="#8a8090" stroke-width="1.6" stroke-linejoin="round"/><ellipse cx="-5.5" cy="-6" rx="2.6" ry="3.6" fill="#2a2430"/><ellipse cx="5.5" cy="-6" rx="2.6" ry="3.6" fill="#2a2430"/><ellipse cx="0" cy="3" rx="2.4" ry="3" fill="#2a2430"/></g>'
def nube_lluvia(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><path d="M-18 6 h34 a10 10 0 0 0 0 -20 a14 14 0 0 0 -27 -3 a10.5 10.5 0 0 0 -7 23z" fill="#E8EDF1" stroke="#7d8d9b" stroke-width="1.8" stroke-linejoin="round"/><path d="M-10 12 l-3 8 M0 12 l-3 8 M10 12 l-3 8" stroke="#6FA3C8" stroke-width="3" stroke-linecap="round"/></g>'
def mar(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><path d="M-30 0 q7.5 -9 15 0 t15 0 t15 0 t15 0 V16 H-30Z" fill="#9FD3DC" stroke="#2f7684" stroke-width="1.6" stroke-linejoin="round"/><path d="M-30 8 q7.5 -9 15 0 t15 0 t15 0 t15 0 V18 H-30Z" fill="#4FA3B3" stroke="#2f7684" stroke-width="1.6" stroke-linejoin="round"/><circle cx="-15" cy="-6" r="1.8" fill="#fff"/><circle cx="15" cy="-6" r="1.8" fill="#fff"/></g>'
DECO={  # (junto a la punta del cartel, junto al círculo de clima, esquina de la nota)
 'otono':(lambda x,y:hoja_oval(x-38,y-6,.9,-30,'#C8682E')+hoja_arce(x,y,1.0,15,'#E3A040'),
          lambda x,y:hoja_arce(x,y,.75,-20,'#D98A3A'),
          lambda x,y:hoja_oval(x-36,y+2,.8,-35,'#B5532A')+hoja_arce(x,y,.95,20,'#E3B052')),
 'halloween':(lambda x,y:calabaza(x,y+4,.9)+murcielago(x-54,y-22,.85)+murcielago(x-92,y-4,.6),
          lambda x,y:murcielago(x,y,.75),
          lambda x,y:fantasma(x-46,y-4,.9)+calabaza(x,y+6,.75)),
 'invierno':(lambda x,y:nube_lluvia(x-44,y-6,.85)+copo(x,y,1.0),
          lambda x,y:copo(x,y,.7),
          lambda x,y:copo(x,y,.95)+nube_lluvia(x-46,y+4,.7)),
 'verano':(lambda x,y:mar(x-50,y+2,.9)+caracola(x,y,.9),
          lambda x,y:caracola(x,y,.8),
          lambda x,y:caracola(x,y,.85)+mar(x-50,y+8,.8)),
}
RUIDO='<filter id="papel"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 .35  0 0 0 0 .3  0 0 0 0 .25  0 0 0 .07 0"/><feComposite in2="SourceGraphic" operator="in"/></filter>'
SOMBRA='filter:drop-shadow(0 4px 10px rgba(0,0,0,.35))'
# ---------- piezas ----------
CART=dict(cx=110,cy=830,r=58,x0=150,x1=720,alto=96)   # cartel de lugar (abajo a la izquierda)
def cartel(tema,nombre='',sub='',icono_n='pino'):
    p=PAL[tema]; c=CART; y0=c['cy']-c['alto']/2; y1=c['cy']+c['alto']/2; tip=c['x1']+44
    cuerpo=f'M{c["x0"]} {y0} H{c["x1"]} L{tip} {c["cy"]} L{c["x1"]} {y1} H{c["x0"]}Z'
    s=f'<svg style="position:absolute;left:0;top:0;overflow:visible;{SOMBRA}" width="1920" height="1080"><defs>{RUIDO}</defs>'
    s+=f'<path d="{cuerpo}" fill="{PAPEL}" stroke="{p["o"]}" stroke-width="4" stroke-linejoin="round"/><path d="{cuerpo}" fill="{PAPEL}" filter="url(#papel)"/>'
    s+=f'<path d="M{c["x0"]+8} {y0+9} H{c["x1"]-4} L{tip-14} {c["cy"]} L{c["x1"]-4} {y1-9} H{c["x0"]+8}" fill="none" stroke="{p["o"]}" stroke-opacity=".35" stroke-width="1.6" stroke-dasharray="6 6"/>'
    s+=f'<circle cx="{c["cx"]}" cy="{c["cy"]}" r="{c["r"]}" fill="{p["c"]}" stroke="{p["o"]}" stroke-width="4"/><circle cx="{c["cx"]}" cy="{c["cy"]}" r="{c["r"]-9}" fill="none" stroke="{PAPEL}" stroke-opacity=".8" stroke-width="2" stroke-dasharray="5 5"/>'
    s+=DECO[tema][0](c['x1']-10,y0-6)+'</svg>'
    s+=f'<div style="position:absolute;left:{c["cx"]-30}px;top:{c["cy"]-30}px">{ico(icono_n,PAPEL,60,2.6)}</div>'
    if nombre:
        s+=f'<div style="position:absolute;left:{c["x0"]+40}px;top:{y0+14}px;font-family:JS;font-weight:700;font-size:38px;letter-spacing:3px;color:{TINTA}">{nombre}</div>'
        s+=f'<div style="position:absolute;left:{c["x0"]+42}px;top:{y0+54}px;font-family:CG;font-style:italic;font-weight:700;font-size:30px;color:{p["o"]}">{sub}</div>'
    return s
PILL=dict(cx=110,cy=962,r=44,x0=140,x1=470,alto=66)
def pildora(tema,texto='',cielo='viento'):
    p=PAL[tema]; c=PILL; y0=c['cy']-c['alto']/2
    s=f'<svg style="position:absolute;left:0;top:0;overflow:visible;{SOMBRA}" width="1920" height="1080"><defs>{RUIDO}</defs>'
    s+=f'<rect x="{c["x0"]-30}" y="{y0}" width="{c["x1"]-c["x0"]+30}" height="{c["alto"]}" rx="{c["alto"]/2}" fill="{PAPEL}" stroke="{p["o"]}" stroke-width="4"/><rect x="{c["x0"]-30}" y="{y0}" width="{c["x1"]-c["x0"]+30}" height="{c["alto"]}" rx="{c["alto"]/2}" fill="{PAPEL}" filter="url(#papel)"/>'
    s+=f'<circle cx="{c["cx"]}" cy="{c["cy"]}" r="{c["r"]}" fill="{p["c"]}" stroke="{p["o"]}" stroke-width="4"/><circle cx="{c["cx"]}" cy="{c["cy"]}" r="{c["r"]-8}" fill="none" stroke="{PAPEL}" stroke-opacity=".8" stroke-width="2" stroke-dasharray="5 5"/>'
    s+=DECO[tema][1](c['x1']-14,y0-4)+'</svg>'
    s+=f'<div style="position:absolute;left:{c["cx"]-24}px;top:{c["cy"]-24}px">{ico(A.CIELOS[cielo],PAPEL,48,2.8)}</div>'
    if texto: s+=f'<div style="position:absolute;left:{c["x0"]+34}px;top:{y0+15}px;font-family:JS;font-weight:700;font-size:32px;letter-spacing:1px;color:{TINTA}">{texto}</div>'
    return s
NOTA=dict(x=1180,y=700,w=660,h=250,rot=-1.6)
def nota(tema,l1='',l2='',firma=True):
    p=PAL[tema]; n=NOTA
    lw=520; d=f'M14 0 C {lw*.21} -10, {lw*.33} 8, {lw*.5} 1 S {lw*.81} -9, {lw-12} 1'
    s=f'''<div style="position:absolute;left:{n["x"]}px;top:{n["y"]}px;width:{n["w"]}px;height:{n["h"]}px;transform:rotate({n["rot"]}deg);{SOMBRA}">
<svg width="{n["w"]}" height="{n["h"]}" style="position:absolute;left:0;top:0;overflow:visible"><defs>{RUIDO}</defs>
<rect width="{n["w"]}" height="{n["h"]}" rx="6" fill="{PAPEL}"/><rect width="{n["w"]}" height="{n["h"]}" rx="6" fill="{PAPEL}" filter="url(#papel)"/>
<g transform="translate(46,{n["h"]-34})"><circle r="4" fill="{p["o"]}"/><path d="{d}" fill="none" stroke="{p["o"]}" stroke-opacity=".6" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="6 6"/><path d="M{lw} 4 c-5 -7 -8 -10 -8 -14 a8 8 0 0 1 16 0 c0 4 -3 7 -8 14z" fill="none" stroke="{p["o"]}" stroke-width="2"/></g>
<rect x="24" y="-16" width="132" height="36" fill="{p["s"]}" opacity=".85" transform="rotate(-3 90 2)"/>
<rect x="{n["w"]-150}" y="{n["h"]-22}" width="132" height="36" fill="{p["c2"]}" opacity=".7" transform="rotate(4 {n["w"]-84} {n["h"]-4})"/>
{DECO[tema][2](n["w"]-34,-8)}</svg>'''
    if l1:
        s+=f'<div style="position:absolute;left:46px;top:38px;font-family:CG;font-style:italic;font-weight:700;font-size:42px;line-height:1.18;color:{TINTA}">{l1}<br>{l2}</div>'
        if firma: s+=f'<div style="position:absolute;right:48px;top:{n["h"]-86}px;font-family:JS;font-weight:700;font-size:20px;letter-spacing:4px;color:{p["o"]}">— ELITA</div>'
    return s+'</div>'
EJ={'ES':dict(nombre='PHOENIX PARK',sub='parque · ciervos',clima='11°C · ventoso',l1='Subí el volumen:',l2='se escucha la ciudad despertando.'),
    'EN':dict(nombre='PHOENIX PARK',sub='park · deer',clima='11°C · windy',l1='Turn the volume up:',l2='you can hear the city waking up.')}
def escena(tema,lang,textos=True,fondo=''):
    e=EJ[lang] if textos else dict(nombre='',sub='',clima='',l1='',l2='')
    cielo={'otono':'viento','halloween':'niebla','invierno':'nieve','verano':'despejado'}[tema]
    b=cartel(tema,e['nombre'],e['sub'])+pildora(tema,e['clima'],cielo)+nota(tema,e['l1'],e['l2'])
    return f'<div style="position:relative;width:1920px;height:1080px;{fondo}">{b}</div>'
if __name__=='__main__':
    foto,out=sys.argv[1],sys.argv[2]
    jobs=[(f'{out}/prueba_{t}_{l}.png',escena(t,l,fondo=f'background:url(file://{foto}) center/cover'),(1920,1080),2) for t in PAL for l in ('ES','EN')]
    asyncio.run(A.generar(jobs))

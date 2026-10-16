import asyncio, sys
import agregados as A
# Kit "sendero": cartel de lugar con forma de flecha + círculo con ícono (tipo parche de guardaparques),
# píldora de clima y nota de papel con cinta firmada "— Elita". Papel crema sólido (se lee sobre cualquier
# toma), texto en tinta, color de la temporada en círculos, bordes y detalles. Medidas en unidades 1080p
# (se renderiza a 2x para 4K).
PAPEL='#F4EEE2'; TINTA='#2A2C27'
# Un solo color general para todo (el arena del logo); lo que cambia por época son los iconitos de arriba.
GENERAL=dict(c='#9A7444',o='#5E4626',s='#E3CFA6',c2='#D2B587')
PAL={t:GENERAL for t in ('otono','halloween','invierno','verano','invierno_a','invierno_b','verano_a','verano_b','verano_mar','primavera','navidad','sanpatricio')}
def ico(n,col,tam,sw=2.4): return A.icono(n,col,tam,sw)
# ---------- decoraciones chicas por temporada ----------
def hoja_arce(x,y,s,r,c):
    p='M0 -26 L5 -12 L16 -18 L12 -4 L24 -2 L12 6 L16 16 L4 10 L0 24 L-4 10 L-16 16 L-12 6 L-24 -2 L-12 -4 L-16 -18 L-5 -12Z'
    return f'<g transform="translate({x},{y}) rotate({r}) scale({s})"><path d="{p}" fill="{c}" stroke="#7a3f1c" stroke-width="1.6" stroke-linejoin="round"/><path d="M0 24 V-18 M0 6 L10 -2 M0 6 L-10 -2" stroke="#7a3f1c" stroke-width="1.4" fill="none"/></g>'
def hoja_oval(x,y,s,r,c): return f'<g transform="translate({x},{y}) rotate({r}) scale({s})"><path d="M0 -20 C12 -10 12 10 0 20 C-12 10 -12 -10 0 -20Z" fill="{c}" stroke="#7a3f1c" stroke-width="1.6"/><path d="M0 -16 V24" stroke="#7a3f1c" stroke-width="1.4"/></g>'
def murcielago(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><path d="M0 0 C-4 -5 -11 -7 -20 -4 C-16 -2 -15 1 -16 4 C-12 1 -8 2 -6 5 C-4 2 -2 2 0 4 C2 2 4 2 6 5 C8 2 12 1 16 4 C15 1 16 -2 20 -4 C11 -7 4 -5 0 0Z" fill="#3b2a4e" stroke="#F3B26B" stroke-width="1.2" stroke-linejoin="round"/></g>'
def calabaza(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><ellipse cx="-16" cy="0" rx="17" ry="21" fill="#e07a30" stroke="#8a4a1c" stroke-width="1.6"/><ellipse cx="16" cy="0" rx="17" ry="21" fill="#e07a30" stroke="#8a4a1c" stroke-width="1.6"/><ellipse cx="0" cy="0" rx="16" ry="23" fill="#ee8c3c" stroke="#8a4a1c" stroke-width="1.6"/><path d="M-8 -18 C-10 0 -10 10 -8 20 M8 -18 C10 0 10 10 8 20" stroke="#c96a26" stroke-width="1.6" fill="none"/><path d="M-1 -19 C0 -27 4 -32 9 -33" stroke="#4d6b3a" stroke-width="5" fill="none" stroke-linecap="round"/><path d="M3 -25 C8 -27 13 -24 14 -20 C9 -20 6 -22 3 -25Z" fill="#6f9a4a" stroke="#4d6b3a" stroke-width="1.2"/></g>'
def copo(x,y,s,c='#ffffff'): return f'<g transform="translate({x},{y}) scale({s})" stroke="{c}" stroke-width="3" stroke-linecap="round" fill="none" style="filter:drop-shadow(0 1px 2px rgba(40,70,100,.6))"><path d="M0 -20 V20 M-17.3 -10 L17.3 10 M-17.3 10 L17.3 -10"/><path d="M-5 -15 l5 5 l5 -5 M-5 15 l5 -5 l5 5"/></g>'
def sol(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><g stroke="#E9A93A" stroke-width="4" stroke-linecap="round">'+''.join(f'<path d="M0 -26 V-36" transform="rotate({a})"/>' for a in range(0,360,45))+'</g><circle r="19" fill="#F5C85C" stroke="#C98A2A" stroke-width="2"/></g>'
def caracola(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><path d="M-16 10 C-18 -6 -6 -18 6 -14 C16 -10 18 2 10 10 C4 15 -6 14 -16 10Z" fill="#F6D7C3" stroke="#B9806A" stroke-width="1.8"/><path d="M-12 8 L4 -12 M-6 10 L8 -8 M0 11 L12 -2" stroke="#B9806A" stroke-width="1.5"/></g>'
def fantasma(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><path d="M-16 18 V-4 C-16 -16 -8 -24 0 -24 C8 -24 16 -16 16 -4 V18 L10 13 L5 18 L0 13 L-5 18 L-10 13Z" fill="#FBF7F0" stroke="#8a8090" stroke-width="1.6" stroke-linejoin="round"/><ellipse cx="-5.5" cy="-6" rx="2.6" ry="3.6" fill="#2a2430"/><ellipse cx="5.5" cy="-6" rx="2.6" ry="3.6" fill="#2a2430"/><ellipse cx="0" cy="3" rx="2.4" ry="3" fill="#2a2430"/></g>'
def nube_lluvia(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><path d="M-18 6 h34 a10 10 0 0 0 0 -20 a14 14 0 0 0 -27 -3 a10.5 10.5 0 0 0 -7 23z" fill="#E8EDF1" stroke="#7d8d9b" stroke-width="1.8" stroke-linejoin="round"/><path d="M-10 12 l-3 8 M0 12 l-3 8 M10 12 l-3 8" stroke="#6FA3C8" stroke-width="3" stroke-linecap="round"/></g>'
def mar(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><path d="M-30 0 q7.5 -9 15 0 t15 0 t15 0 t15 0 V16 H-30Z" fill="#9FD3DC" stroke="#2f7684" stroke-width="1.6" stroke-linejoin="round"/><path d="M-30 8 q7.5 -9 15 0 t15 0 t15 0 t15 0 V18 H-30Z" fill="#4FA3B3" stroke="#2f7684" stroke-width="1.6" stroke-linejoin="round"/><circle cx="-15" cy="-6" r="1.8" fill="#fff"/><circle cx="15" cy="-6" r="1.8" fill="#fff"/></g>'
L1='stroke-linejoin="round" stroke-linecap="round"'
def copo2(x,y,s): return f'<g transform="translate({x},{y}) scale({s})" fill="none" stroke="#4E7FA6" stroke-width="3.2" {L1}><path d="M0 -21 V21 M-18.2 -10.5 L18.2 10.5 M-18.2 10.5 L18.2 -10.5"/><path d="M-5 -16 L0 -11 L5 -16 M-5 16 L0 11 L5 16 M-16.5 -3.5 L-11 -6 L-12.5 -12 M16.5 3.5 L11 6 L12.5 12 M-16.5 3.5 L-11 6 L-12.5 12 M16.5 -3.5 L11 -6 L12.5 -12"/><circle r="3.4" fill="#CFE6F5"/></g>'
def muneco(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><circle cy="10" r="15" fill="#FBFDFF" stroke="#7d93a6" stroke-width="1.8"/><circle cy="-12" r="11" fill="#FBFDFF" stroke="#7d93a6" stroke-width="1.8"/><path d="M-11 -4 Q0 2 11 -4 L11 0 Q0 6 -11 0Z" fill="#C8574A"/><path d="M6 -2 l4 12 l-6 -1z" fill="#C8574A"/><circle cx="-4" cy="-14" r="1.6" fill="#2a2c27"/><circle cx="4" cy="-14" r="1.6" fill="#2a2c27"/><path d="M0 -11 l8 2 l-8 1.6z" fill="#E8873A"/><circle cy="6" r="1.5" fill="#2a2c27"/><circle cy="13" r="1.5" fill="#2a2c27"/></g>'
def gorro(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><circle cy="-24" r="7" fill="#F4EEE2" stroke="#8a5a3a" stroke-width="1.6"/><path d="M-20 4 C-20 -14 -10 -20 0 -20 C10 -20 20 -14 20 4Z" fill="#C8574A" stroke="#7a2e26" stroke-width="1.8"/><path d="M-10 -16 V4 M0 -20 V4 M10 -16 V4" stroke="#a8433a" stroke-width="1.6"/><rect x="-23" y="2" width="46" height="11" rx="4" fill="#E8D6B4" stroke="#8a5a3a" stroke-width="1.6"/><path d="M-16 4 v7 M-8 4 v7 M0 4 v7 M8 4 v7 M16 4 v7" stroke="#b8956a" stroke-width="1.4"/></g>'
def taza(x,y,s): return f'<g transform="translate({x},{y}) scale({s})" {L1}><path d="M-15 -6 H13 V10 a10 10 0 0 1 -10 10 H-5 a10 10 0 0 1 -10 -10Z" fill="#7FA9C9" stroke="#3f6584" stroke-width="1.8"/><path d="M13 -2 h3 a5.5 5.5 0 0 1 0 11 h-4" fill="none" stroke="#3f6584" stroke-width="2.4"/><path d="M-6 -12 q-3 -4 0 -8 M2 -12 q-3 -4 0 -8" fill="none" stroke="#a8b5bf" stroke-width="2.2"/><path d="M-15 2 H13" stroke="#F4EEE2" stroke-width="2"/></g>'
def sombrilla(x,y,s): return f'<g transform="translate({x},{y}) scale({s})" {L1}><path d="M-2 -12 L6 24" stroke="#8a6a4a" stroke-width="2.6"/><path d="M-28 -2 C-24 -22 18 -30 26 -14 Z" fill="#F4EEE2" stroke="#b5443a" stroke-width="1.8"/><path d="M-28 -2 C-20 -10 -16 -12 -12 -20 C-6 -24 -2 -24 2 -26 C4 -18 10 -14 26 -14 C14 -8 6 -6 -4 -6 C-14 -6 -20 -4 -28 -2Z" fill="#D9675A" opacity=".9"/><path d="M-12 -20 C-10 -12 -6 -8 -4 -6 M2 -26 C4 -18 2 -10 -4 -6" stroke="#b5443a" stroke-width="1.4" fill="none"/></g>'
def helado(x,y,s): return f'<g transform="translate({x},{y}) scale({s})" {L1}><path d="M-11 0 L0 26 L11 0Z" fill="#E3B26B" stroke="#9a6a2a" stroke-width="1.6"/><path d="M-7 4 L3 14 M1 2 L7 8 M-3 12 L5 4" stroke="#b8803a" stroke-width="1.2"/><circle cx="-5" cy="-6" r="9" fill="#F6C6D2" stroke="#c07a8c" stroke-width="1.6"/><circle cx="6" cy="-7" r="8.5" fill="#F8EDD6" stroke="#b9a07a" stroke-width="1.6"/><circle cx="0" cy="-16" r="8" fill="#9FD3B8" stroke="#5f9a7a" stroke-width="1.6"/><circle cx="1" cy="-25" r="3" fill="#C8574A"/></g>'
def tulipan(x,y,s,c='#E98BA6'): return f'<g transform="translate({x},{y}) scale({s})" {L1}><path d="M0 26 V-2" stroke="#4f8a4c" stroke-width="3"/><path d="M0 18 C-12 14 -14 4 -12 -2 C-6 4 -2 10 0 18Z" fill="#6aa65a" stroke="#4f8a4c" stroke-width="1.4"/><path d="M-11 -18 L-5 -10 L0 -20 L5 -10 L11 -18 C12 -4 8 2 0 2 C-8 2 -12 -4 -11 -18Z" fill="{c}" stroke="#a84a68" stroke-width="1.6"/></g>'
def mariposa(x,y,s): return f'<g transform="translate({x},{y}) scale({s})" {L1}><path d="M0 0 C-8 -18 -26 -16 -22 -4 C-20 2 -10 4 0 0Z M0 0 C8 -18 26 -16 22 -4 C20 2 10 4 0 0Z" fill="#F3C766" stroke="#a87a2a" stroke-width="1.5"/><path d="M0 0 C-6 4 -16 14 -10 16 C-6 18 -2 10 0 0Z M0 0 C6 4 16 14 10 16 C6 18 2 10 0 0Z" fill="#F2B8C8" stroke="#a87a2a" stroke-width="1.5"/><path d="M0 -6 V10" stroke="#5a4030" stroke-width="2.6"/><path d="M0 -6 q-3 -6 -7 -7 M0 -6 q3 -6 7 -7" stroke="#5a4030" stroke-width="1.4" fill="none"/></g>'
def acebo(x,y,s): 
    h='M0 0 C6 -4 9 -2 13 -6 C13 0 17 1 20 0 C18 5 22 7 25 7 C20 11 20 13 21 17 C16 15 13 17 11 20 C9 15 5 15 1 15 C4 9 1 5 0 0Z'
    return f'<g transform="translate({x},{y}) scale({s})"><path d="{h}" fill="#3d7d52" stroke="#24543a" stroke-width="1.4"/><path d="{h}" fill="#2f6b45" stroke="#24543a" stroke-width="1.4" transform="scale(-1,1) rotate(20)"/><circle cx="-2" cy="-4" r="5" fill="#C8463E" stroke="#8a2a24" stroke-width="1.2"/><circle cx="6" cy="-7" r="4.6" fill="#D0524A" stroke="#8a2a24" stroke-width="1.2"/><circle cx="3" cy="2" r="4.4" fill="#B5362F" stroke="#8a2a24" stroke-width="1.2"/></g>'
def bola(x,y,s,c='#C8574A'): return f'<g transform="translate({x},{y}) scale({s})"><path d="M0 -24 V-18" stroke="#9a7a4a" stroke-width="1.6"/><rect x="-5" y="-19" width="10" height="6" rx="1.5" fill="#E3B052" stroke="#9a7a2a" stroke-width="1.2"/><circle r="15" cy="1" fill="{c}" stroke="#7a2e26" stroke-width="1.6"/><path d="M-12 2 Q0 8 12 2" stroke="#F3D27A" stroke-width="2" fill="none"/><ellipse cx="-6" cy="-5" rx="3.5" ry="2" fill="#fff" opacity=".7"/></g>'
def trebol(x,y,s,r=0): return f'<g transform="translate({x},{y}) rotate({r}) scale({s})"><path d="M0 2 C-1 10 -4 16 -9 21" stroke="#3c7d48" stroke-width="3" fill="none" stroke-linecap="round"/>'+''.join(f'<path transform="rotate({a})" d="M0 0 C-10 -7 -13 -18 -6 -21 C-2 -22 0 -20 0 -17 C0 -20 2 -22 6 -21 C13 -18 10 -7 0 0Z" fill="#5FAE66" stroke="#2f7a3c" stroke-width="1.4"/>' for a in (0,120,240))+'</g>'
def galera(x,y,s): return f'<g transform="translate({x},{y}) scale({s})" {L1}><ellipse cy="12" rx="24" ry="6" fill="#3f8a4c" stroke="#24543a" stroke-width="1.6"/><path d="M-14 12 L-12 -18 H12 L14 12Z" fill="#4f9a5c" stroke="#24543a" stroke-width="1.6"/><rect x="-13" y="2" width="26" height="7" fill="#2a2c27"/><rect x="-4" y="1" width="8" height="9" fill="none" stroke="#E3B052" stroke-width="2"/></g>'
def moneda(x,y,s): return f'<g transform="translate({x},{y}) scale({s})"><circle r="11" fill="#E8C35A" stroke="#a8802a" stroke-width="1.6"/><circle r="7" fill="none" stroke="#c49a3a" stroke-width="1.4"/></g>'
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
  'invierno_a':(lambda x,y:muneco(x-44,y-4,.9)+copo2(x,y,.95), lambda x,y:copo2(x,y,.7), lambda x,y:copo2(x,y,.9)+muneco(x-44,y+2,.75)),
 'invierno_b':(lambda x,y:gorro(x-44,y,.85)+taza(x,y+2,.9), lambda x,y:copo2(x,y,.7), lambda x,y:taza(x,y,.85)+gorro(x-46,y+4,.75)),
 'verano_a':(lambda x,y:sombrilla(x-40,y,.9)+sol(x+4,y-6,.75), lambda x,y:sol(x,y,.6), lambda x,y:sol(x,y,.7)+sombrilla(x-50,y+6,.8)),
 'verano_b':(lambda x,y:helado(x-40,y,.9)+sol(x+4,y-6,.75), lambda x,y:sol(x,y,.6), lambda x,y:sol(x,y,.7)+helado(x-46,y+6,.8)),
 'primavera':(lambda x,y:tulipan(x-40,y,.9)+mariposa(x+4,y-6,.85), lambda x,y:tulipan(x,y,.7,'#F3C766'), lambda x,y:mariposa(x,y-4,.8)+tulipan(x-42,y+6,.8)),
 'navidad':(lambda x,y:acebo(x-34,y,1.1)+bola(x+6,y+2,.85), lambda x,y:acebo(x,y,.8), lambda x,y:bola(x,y+4,.8)+acebo(x-44,y,.95)),
 'sanpatricio':(lambda x,y:trebol(x-40,y,.9,-15)+galera(x+4,y-2,.85), lambda x,y:trebol(x,y,.7,10), lambda x,y:galera(x,y,.8)+trebol(x-44,y+4,.8,-20)+moneda(x-80,y+12,.7)),
}
# Un solo iconito por pieza, dentro del papel beige (a la derecha, centrado en alto).
# tamaño natural aproximado de cada dibujo (lado mayor a escala 1) para llevarlos todos al mismo tamaño
TAM={mar:62,caracola:38,hoja_arce:50,hoja_oval:40,calabaza:68,murcielago:42,fantasma:44,muneco:52,copo2:44,gorro:48,taza:42,sombrilla:58,sol:74,helado:56,tulipan:48,mariposa:52,acebo:50,bola:42,trebol:46,galera:50}
def _ic(fn,*extra):
    def f(x,y,obj):
        sc=obj/TAM[fn]
        if fn in (hoja_arce,hoja_oval): return fn(x,y,sc,extra[0],extra[1])
        if fn is trebol: return fn(x,y-6*sc,sc,extra[0] if extra else 0)
        if fn is tulipan: return fn(x,y-3*sc,sc)
        if fn is acebo: return fn(x+2*sc,y-4*sc,sc)
        if fn is muneco: return fn(x,y-1*sc,sc)
        return fn(x,y,sc)
    return f
ICONO1={  # cartel, píldora, nota
 'otono':(_ic(hoja_arce,15,'#E3A040'),_ic(hoja_oval,-30,'#C8682E'),_ic(hoja_arce,-10,'#D98A3A')),
 'halloween':(_ic(calabaza),_ic(murcielago),_ic(fantasma)),
 'invierno_a':(_ic(muneco),_ic(copo2),_ic(copo2)),
 'invierno_b':(_ic(gorro),_ic(copo2),_ic(taza)),
 'verano_a':(_ic(sombrilla),_ic(sol),_ic(sol)),
 'verano_mar':(_ic(mar),_ic(sol),_ic(caracola)),
 'verano_b':(_ic(helado),_ic(sol),_ic(helado)),
 'primavera':(_ic(tulipan),_ic(mariposa),_ic(mariposa)),
 'navidad':(_ic(acebo),_ic(bola),_ic(bola)),
 'sanpatricio':(_ic(trebol,-10),_ic(trebol,10),_ic(galera)),
}
RUIDO='<filter id="papel"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 .35  0 0 0 0 .3  0 0 0 0 .25  0 0 0 .07 0"/><feComposite in2="SourceGraphic" operator="in"/></filter>'
SOMBRA='filter:drop-shadow(0 4px 10px rgba(0,0,0,.35))'
# ---------- piezas ----------
ETIQUETA={'otono':('OTOÑO','AUTUMN'),'halloween':('HALLOWEEN','HALLOWEEN'),'invierno':('INVIERNO','WINTER'),'invierno_a':('INVIERNO','WINTER'),
 'invierno_b':('INVIERNO','WINTER'),'verano':('VERANO','SUMMER'),'verano_a':('VERANO','SUMMER'),'verano_b':('VERANO','SUMMER'),'verano_mar':('VERANO','SUMMER'),
 'primavera':('PRIMAVERA','SPRING'),'navidad':('NAVIDAD','CHRISTMAS'),'sanpatricio':('SAN PATRICIO',"ST. PATRICK'S")}
CART=dict(cx=110,cy=830,r=58,x0=150,x1=720,alto=96)   # cartel de lugar (abajo a la izquierda)
def cartel(tema,nombre='',sub='',icono_n='pino',lang='ES',x1=None):
    p=PAL[tema]; c=dict(CART,x1=x1 or CART['x1']); y0=c['cy']-c['alto']/2; y1=c['cy']+c['alto']/2; tip=c['x1']+44
    cuerpo=f'M{c["x0"]} {y0} H{c["x1"]} L{tip} {c["cy"]} L{c["x1"]} {y1} H{c["x0"]}Z'
    s=f'<svg style="position:absolute;left:0;top:0;overflow:visible;{SOMBRA}" width="1920" height="1080"><defs>{RUIDO}</defs>'
    s+=f'<path d="{cuerpo}" fill="{PAPEL}" stroke="{p["o"]}" stroke-width="4" stroke-linejoin="round"/><path d="{cuerpo}" fill="{PAPEL}" filter="url(#papel)"/>'
    s+=f'<path d="M{c["x0"]+8} {y0+9} H{c["x1"]-4} L{tip-14} {c["cy"]} L{c["x1"]-4} {y1-9} H{c["x0"]+8}" fill="none" stroke="{p["o"]}" stroke-opacity=".35" stroke-width="1.6" stroke-dasharray="6 6"/>'
    s+=f'<circle cx="{c["cx"]}" cy="{c["cy"]}" r="{c["r"]}" fill="{p["c"]}" stroke="{p["o"]}" stroke-width="4"/><circle cx="{c["cx"]}" cy="{c["cy"]}" r="{c["r"]-9}" fill="none" stroke="{PAPEL}" stroke-opacity=".8" stroke-width="2" stroke-dasharray="5 5"/>'
    s+=ICONO1[tema][0](c['x1']-34,c['cy'],60)+'</svg>'
    # pestaña con el nombre de la temporada, apoyada sobre el borde de arriba del cartel
    et=ETIQUETA[tema][0 if lang=='ES' else 1]
    s=f'<div style="position:absolute;left:{c["x0"]+30}px;top:{y0-38}px;height:38px;padding:0 20px;box-sizing:border-box;background:{PAPEL};border:4px solid {p["o"]};border-bottom:none;border-radius:12px 12px 0 0;font-family:JS;font-weight:700;font-size:20px;letter-spacing:5px;line-height:36px;color:{p["o"]};{SOMBRA}">{et}</div>'+s
    s+=f'<div style="position:absolute;left:{c["cx"]-30}px;top:{c["cy"]-30}px">{ico(icono_n,PAPEL,60,2.6)}</div>'
    if nombre:
        s+=f'<div style="position:absolute;left:{c["x0"]+40}px;top:{y0+14}px;font-family:JS;font-weight:700;font-size:38px;letter-spacing:3px;color:{TINTA}">{nombre}</div>'
        s+=f'<div style="position:absolute;left:{c["x0"]+42}px;top:{y0+54}px;font-family:CG;font-style:italic;font-weight:700;font-size:30px;color:{p["o"]}">{sub}</div>'
    return s
PILL=dict(cx=110,cy=962,r=44,x0=140,x1=540,alto=66)
def pildora(tema,texto='',cielo='viento'):
    p=PAL[tema]; c=PILL; y0=c['cy']-c['alto']/2
    s=f'<svg style="position:absolute;left:0;top:0;overflow:visible;{SOMBRA}" width="1920" height="1080"><defs>{RUIDO}</defs>'
    s+=f'<rect x="{c["x0"]-30}" y="{y0}" width="{c["x1"]-c["x0"]+30}" height="{c["alto"]}" rx="{c["alto"]/2}" fill="{PAPEL}" stroke="{p["o"]}" stroke-width="4"/><rect x="{c["x0"]-30}" y="{y0}" width="{c["x1"]-c["x0"]+30}" height="{c["alto"]}" rx="{c["alto"]/2}" fill="{PAPEL}" filter="url(#papel)"/>'
    s+=f'<circle cx="{c["cx"]}" cy="{c["cy"]}" r="{c["r"]}" fill="{p["c"]}" stroke="{p["o"]}" stroke-width="4"/><circle cx="{c["cx"]}" cy="{c["cy"]}" r="{c["r"]-8}" fill="none" stroke="{PAPEL}" stroke-opacity=".8" stroke-width="2" stroke-dasharray="5 5"/>'
    s+=ICONO1[tema][1](c['x1']-28,c['cy'],42)+'</svg>'
    s+=f'<div style="position:absolute;left:{c["cx"]-24}px;top:{c["cy"]-24}px">{ico(A.CIELOS[cielo],PAPEL,48,2.8)}</div>'
    if texto: s+=f'<div style="position:absolute;left:{c["x0"]+34}px;top:{y0+15}px;font-family:JS;font-weight:700;font-size:32px;letter-spacing:1px;color:{TINTA}">{texto}</div>'
    return s
NOTA=dict(x=1180,y=700,w=660,h=250,rot=-1.6)
def nota(tema,l1='',l2='',firma=True,firma_fija=False):
    p=PAL[tema]; n=NOTA
    lw=520; d=f'M14 0 C {lw*.21} -10, {lw*.33} 8, {lw*.5} 1 S {lw*.81} -9, {lw-12} 1'
    s=f'''<div style="position:absolute;left:{n["x"]}px;top:{n["y"]}px;width:{n["w"]}px;height:{n["h"]}px;transform:rotate({n["rot"]}deg);{SOMBRA}">
<svg width="{n["w"]}" height="{n["h"]}" style="position:absolute;left:0;top:0;overflow:visible"><defs>{RUIDO}</defs>
<rect width="{n["w"]}" height="{n["h"]}" rx="6" fill="{PAPEL}"/><rect width="{n["w"]}" height="{n["h"]}" rx="6" fill="{PAPEL}" filter="url(#papel)"/>
<g transform="translate(46,{n["h"]-34})"><circle r="4" fill="{p["o"]}"/><path d="{d}" fill="none" stroke="{p["o"]}" stroke-opacity=".6" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="6 6"/><path d="M{lw} 4 c-5 -7 -8 -10 -8 -14 a8 8 0 0 1 16 0 c0 4 -3 7 -8 14z" fill="none" stroke="{p["o"]}" stroke-width="2"/></g>
<rect x="24" y="-16" width="132" height="36" fill="{p["s"]}" opacity=".85" transform="rotate(-3 90 2)"/>
<rect x="{n["w"]-150}" y="{n["h"]-22}" width="132" height="36" fill="{p["c2"]}" opacity=".7" transform="rotate(4 {n["w"]-84} {n["h"]-4})"/>
{ICONO1[tema][2](n["w"]-58,58,62)}</svg>'''
    if l1:
        s+=f'<div style="position:absolute;left:46px;top:38px;font-family:CG;font-style:italic;font-weight:700;font-size:42px;line-height:1.18;color:{TINTA}">{l1}<br>{l2}</div>'
    if firma and (l1 or firma_fija): s+=f'<div style="position:absolute;right:48px;top:{n["h"]-86}px;font-family:JS;font-weight:700;font-size:20px;letter-spacing:4px;color:{p["o"]}">— ELITA</div>'
    return s+'</div>'
EJ={'ES':dict(nombre='PHOENIX PARK',sub='parque · ciervos',clima='11°C · ventoso',l1='Subí el volumen:',l2='se escucha la ciudad despertando.'),
    'EN':dict(nombre='PHOENIX PARK',sub='park · deer',clima='11°C · windy',l1='Turn the volume up:',l2='you can hear the city waking up.')}
def escena(tema,lang,textos=True,fondo=''):
    e=EJ[lang] if textos else dict(nombre='',sub='',clima='',l1='',l2='')
    cielo={'otono':'viento','halloween':'niebla','navidad':'nieve','sanpatricio':'nublado','primavera':'parcial'}.get(tema,'nieve' if tema.startswith('invierno') else 'despejado')
    b=cartel(tema,e['nombre'],e['sub'],lang=lang)+pildora(tema,e['clima'],cielo)+nota(tema,e['l1'],e['l2'])
    return f'<div style="position:relative;width:1920px;height:1080px;{fondo}">{b}</div>'
# ---------- kit final: piezas sueltas, cuadro completo 4K transparente, sin texto ----------
KIT={'otono':'otono','halloween':'halloween','invierno-muneco':'invierno_a','invierno-gorro':'invierno_b','primavera':'primavera',
     'verano-mar':'verano_mar','verano-sombrilla':'verano_a','navidad':'navidad','sanpatricio':'sanpatricio'}
CARTEL_LARGO=980
def cuadro(b): return f'<div style="position:relative;width:1920px;height:1080px">{b}</div>'
def kit(out='sendero-kit'):
    jobs=[]
    for nombre,t in KIT.items():
        for l in ('ES','EN'):
            jobs.append((f'{out}/{nombre}/{l}/cartel-corto_4K.png',cuadro(cartel(t,lang=l)),(1920,1080),2))
            jobs.append((f'{out}/{nombre}/{l}/cartel-largo_4K.png',cuadro(cartel(t,lang=l,x1=CARTEL_LARGO)),(1920,1080),2))
        for c in A.CIELOS: jobs.append((f'{out}/{nombre}/clima_{c}_4K.png',cuadro(pildora(t,cielo=c)),(1920,1080),2))
        jobs.append((f'{out}/{nombre}/nota_4K.png',cuadro(nota(t,firma_fija=True)),(1920,1080),2))
    asyncio.run(A.generar(jobs))
if __name__=='__main__' and sys.argv[1:2]==['kit']:
    kit()
elif __name__=='__main__':
    foto,out=sys.argv[1],sys.argv[2]
    temas=sys.argv[3].split(',') if len(sys.argv)>3 else list(PAL)
    jobs=[(f'{out}/prueba_{t}_{l}.png',escena(t,l,fondo=f'background:url(file://{foto}) center/cover'),(1920,1080),2) for t in temas for l in ('ES','EN')]
    asyncio.run(A.generar(jobs))

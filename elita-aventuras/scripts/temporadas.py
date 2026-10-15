import asyncio, os, sys
import agregados as A
# Placa de temporada: fecha/estación, temperatura, cielo y ubicación sobre una tarjeta con la
# personalidad de cada época (color, ilustración plana como las ventanas del logo y etiqueta).
# Cuadro completo 4K transparente, tarjeta abajo a la izquierda; Ivan escribe los 4 textos.
# Uso: python3 temporadas.py            → todas las temporadas × estados del cielo × ES/EN
#      python3 temporadas.py prueba     → hoja de prueba sobre una foto
CREMA=A.CREMA
# tarjeta (4K)
CX,CB,CW,CH=150,2010,1650,870          # izquierda, borde inferior, ancho, alto
CT=CB-CH                                 # borde superior (1140)
PAD=80
ICX=CX+PAD+60                            # centro de la columna de íconos (290)
TX=CX+PAD+150                            # inicio de los textos (380)
LINEAS=[('calendario',CT+300,100,'CG'),('temperatura',CT+450,88,'JS'),(None,CT+600,100,'CG'),('ubicacion',CT+780,130,'CG')]
def ic_tam(tt): return round(130*tt/100)
def ic_cy(base,tt): return base-45*tt/100
# ---------- ilustraciones ----------
def hoja(x,y,r,s,c,v):
    return f'<g transform="translate({x},{y}) rotate({r}) scale({s})"><path d="M0 -34 C22 -20 24 14 0 34 C-24 14 -22 -20 0 -34Z" fill="{c}"/><path d="M0 -26 V40" stroke="{v}" stroke-width="2.4" stroke-linecap="round"/><path d="M0 -6 l10 -8 M0 6 l-10 -8 M0 16 l9 -7" stroke="{v}" stroke-width="1.8" stroke-linecap="round"/></g>'
def murcielago(x,y,s):
    return f'<g transform="translate({x},{y}) scale({s})" fill="#3b2a4e" stroke="#F0954A" stroke-width="2.2" stroke-linejoin="round"><path d="M0 0 C-8 -10 -22 -14 -40 -8 C-32 -4 -30 2 -32 8 C-24 2 -16 4 -12 10 C-8 4 -4 4 0 8 C4 4 8 4 12 10 C16 4 24 2 32 8 C30 2 32 -4 40 -8 C22 -14 8 -10 0 0Z"/><circle cx="0" cy="-4" r="6"/><path d="M-5 -8 l-2 -7 l5 4z M5 -8 l2 -7 l-5 4z"/></g>'
def copo(x,y,s,o=1):
    return f'<g transform="translate({x},{y}) scale({s})" stroke="#EEF4F8" stroke-width="3" stroke-linecap="round" fill="none" opacity="{o}"><path d="M0 -24 V24 M-20.8 -12 L20.8 12 M-20.8 12 L20.8 -12"/><path d="M-6 -18 l6 6 l6 -6 M-6 18 l6 -6 l6 6 M-21 -4 l7 0 l3 -7 M21 4 l-7 0 l-3 7 M-21 4 l7 0 l3 7 M21 -4 l-7 0 l-3 -7"/></g>'
def acebo(x,y,r,s):
    hoja_p='M0 0 C10 -6 14 -2 20 -8 C20 0 26 2 30 0 C28 8 34 10 38 10 C30 16 30 20 32 26 C24 22 20 26 16 30 C14 22 8 22 2 22 C6 14 2 8 0 0Z'
    return f'<g transform="translate({x},{y}) rotate({r}) scale({s})"><path d="{hoja_p}" fill="#2f6b45"/><path d="{hoja_p}" fill="#3d7d52" transform="scale(-1,1) rotate(25)"/><path d="M0 0 C12 6 22 12 32 20" stroke="#24543a" stroke-width="1.6" fill="none"/><circle cx="-2" cy="-6" r="7" fill="#c2413a"/><circle cx="9" cy="-10" r="6.5" fill="#d0524a"/><circle cx="4" cy="2" r="6" fill="#b5362f"/><circle cx="-4" cy="-8" r="2" fill="#f2c2b8"/></g>'
def trebol(x,y,r,s,c='#4f9a5c'):
    return f'<g transform="translate({x},{y}) rotate({r}) scale({s})" fill="{c}"><path d="M0 0 C-2 14 -6 26 -14 36" stroke="#3c7d48" stroke-width="4" fill="none" stroke-linecap="round"/>'+''.join(f'<g transform="rotate({a})"><path d="M0 0 C-14 -10 -18 -26 -8 -30 C-3 -32 0 -28 0 -24 C0 -28 3 -32 8 -30 C18 -26 14 -10 0 0Z"/></g>' for a in (0,120,240))+'</g>'
def flor(x,y,s,c='#f1b9c8',c2='#e79ab0'):
    return f'<g transform="translate({x},{y}) scale({s})">'+''.join(f'<ellipse cx="0" cy="-15" rx="10" ry="15" fill="{c if i%2 else c2}" transform="rotate({i*72})"/>' for i in range(5))+'<circle r="6" fill="#f3d27a"/></g>'
def calabaza(x,y,s):
    return f'''<g transform="translate({x},{y}) scale({s})">
<path d="M-4 -46 C-2 -60 6 -66 14 -66" stroke="#4d6b3a" stroke-width="9" fill="none" stroke-linecap="round"/>
<ellipse cx="-34" cy="0" rx="36" ry="44" fill="#d9772f"/><ellipse cx="34" cy="0" rx="36" ry="44" fill="#d9772f"/><ellipse cx="0" cy="0" rx="34" ry="48" fill="#e8873a"/>
<path d="M-40 -14 l14 -10 l6 16z M40 -14 l-14 -10 l-6 16z" fill="#3a2414"/><path d="M-36 14 Q0 40 36 14 L28 18 L22 10 L14 22 L6 12 L-2 24 L-10 12 L-18 22 L-26 10 Z" fill="#3a2414"/></g>'''
def sol(x,y,s):
    return f'<g transform="translate({x},{y}) scale({s})"><g stroke="#f3c766" stroke-width="7" stroke-linecap="round">'+''.join(f'<path d="M0 -70 V-92" transform="rotate({a})"/>' for a in range(0,360,30))+'</g><circle r="56" fill="#f3c766"/><circle r="56" fill="#f8da8a" opacity=".5" transform="translate(-10,-10) scale(.7)"/></g>'
TEMAS={
 'otono':dict(es='OTOÑO',en='AUTUMN',acento='#E3A15B',fondo='rgba(46,28,18,.62)',deco=lambda:''.join([hoja(1690,1105,-30,1.5,'#c8682e','#8a3f1c'),hoja(1785,1180,40,1.25,'#e0a040','#9a6420'),hoja(1600,1040,15,1.0,'#b5532a','#7a3416'),hoja(1835,1075,-60,0.9,'#d98a3a','#8a5420'),hoja(1735,1000,70,0.8,'#c46a2a','#7a3a16'),hoja(1525,1110,-10,0.65,'#e3b052','#9a7428')])),
 'halloween':dict(es='HALLOWEEN',en='HALLOWEEN',acento='#F0954A',fondo='rgba(34,20,44,.66)',deco=lambda:calabaza(1735,1120,1.15)+murcielago(1560,1030,1.1)+murcielago(1650,975,.8)+murcielago(1500,1090,.6)),
 'invierno':dict(es='INVIERNO',en='WINTER',acento='#BFDCEE',fondo='rgba(20,34,54,.6)',deco=lambda:copo(1735,1110,2.2)+copo(1620,1035,1.3,.9)+copo(1830,1020,1.0,.85)+copo(1545,1105,.8,.8)+copo(1800,1215,.7,.7)),
 'navidad':dict(es='NAVIDAD',en='CHRISTMAS',acento='#E07A6E',fondo='rgba(18,40,30,.64)',deco=lambda:acebo(1700,1125,-20,2.4)+acebo(1600,1080,30,1.4)+''.join(f'<path d="M{x} {y-14} L{x+4} {y-4} L{x+14} {y} L{x+4} {y+4} L{x} {y+14} L{x-4} {y+4} L{x-14} {y} L{x-4} {y-4}Z" fill="#f3d27a" opacity=".95"/>' for x,y in ((1830,1010),(1530,1030),(1790,1220)))),
 'sanpatricio':dict(es='SAN PATRICIO',en="ST. PATRICK'S",acento='#8BD08E',fondo='rgba(14,44,28,.62)',deco=lambda:trebol(1715,1110,-15,2.4)+trebol(1590,1050,20,1.4,'#62ad6c')+trebol(1825,1030,-35,1.0,'#3f8a4c')+''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#e3bd5a"/><circle cx="{x}" cy="{y}" r="{r*.6}" fill="none" stroke="#b8902e" stroke-width="2"/>' for x,y,r in ((1820,1215,16),(1520,1105,12)))),
 'primavera':dict(es='PRIMAVERA',en='SPRING',acento='#F2B8C8',fondo='rgba(52,30,44,.58)',deco=lambda:'<path d="M1500 1060 C1600 1090 1680 1070 1860 1150" stroke="#6b4a3a" stroke-width="8" fill="none" stroke-linecap="round"/><path d="M1690 1080 C1720 1040 1750 1030 1790 1020" stroke="#6b4a3a" stroke-width="6" fill="none" stroke-linecap="round"/>'+flor(1600,1075,1.6)+flor(1720,1085,2.0)+flor(1790,1020,1.3)+flor(1840,1140,1.5,'#f6cbd6','#eaa3b8')+flor(1530,1050,1.0)),
 'verano':dict(es='VERANO',en='SUMMER',acento='#F3C766',fondo='rgba(14,44,52,.56)',deco=lambda:sol(1735,1120,1.35)+'<path d="M1500 1215 q25 -14 50 0 t50 0 t50 0" stroke="#bfe3e8" stroke-width="5" fill="none" stroke-linecap="round" opacity=".8"/>'),
}
def tarjeta(tema,cielo,lang,textos=None,fondo='',guia=False):
    T=TEMAS[tema]; ac=T['acento']
    halo='filter:drop-shadow(0 0 14px rgba(20,26,38,.5))'
    etiqueta=T['es'] if lang=='ES' else T['en']
    b=f'<div style="position:absolute;left:{CX}px;top:{CT}px;width:{CW}px;height:{CH}px;border-radius:44px;background:{T["fondo"]};box-shadow:0 10px 40px rgba(0,0,0,.25);border:3px solid {ac}55"></div>'
    # etiqueta de la temporada y camino punteado con pin (el motivo del logo)
    b+=f'<div style="position:absolute;left:{CX+PAD}px;top:{CT+48}px;font-family:JS;font-weight:700;font-size:54px;letter-spacing:12px;color:{ac}">{etiqueta}</div>'
    lw=520; d=f'M14 0 C {lw*.21} -20, {lw*.33} 16, {lw*.5} 2 S {lw*.81} -18, {lw-12} 2'
    b+=f'''<svg style="position:absolute;left:{CX+PAD}px;top:{CT+150}px;overflow:visible" width="{lw+30}" height="40" viewBox="-10 -30 {lw+30} 40"><circle r="7" fill="{ac}"/><path d="{d}" fill="none" stroke="{ac}" stroke-width="4" stroke-linecap="round" stroke-dasharray="12 10"/><path d="M{lw} 6 c-9 -12 -14 -17 -14 -24 a14 14 0 0 1 28 0 c0 7 -5 12 -14 24z" fill="none" stroke="{ac}" stroke-width="3.5" stroke-linejoin="round"/><circle cx="{lw}" cy="-18" r="5" fill="{ac}"/></svg>'''
    for n,base,tt,fam in LINEAS:
        n=n or A.CIELOS[cielo]; t=ic_tam(tt); cy=ic_cy(base,tt)
        b+=f'<div style="position:absolute;left:{ICX-t/2}px;top:{cy-t/2}px;{halo}">{A.icono(n,ac,t,2.6*130/t)}</div>'
    # ilustración agrandada desde la esquina superior derecha de la tarjeta
    ex,ey=CX+CW,CT
    b+=f'<svg style="position:absolute;left:0;top:0;overflow:visible" width="3840" height="2160"><g transform="translate({ex} {ey}) scale(1.5) translate({-ex} {-ey})">{T["deco"]()}</g></svg>'
    if textos:
        b+='<svg style="position:absolute;left:0;top:0;overflow:visible" width="3840" height="2160"><defs><filter id="s" x="-20%" y="-60%" width="140%" height="220%"><feDropShadow dx="0" dy="2" stdDeviation="8" flood-color="#000" flood-opacity=".45"/></filter></defs>'
        b+=''.join(f'<text x="{TX}" y="{base}" font-family="{fam}" font-weight="700" font-size="{tt}" fill="{CREMA}" filter="url(#s)">{t}</text>' for (n,base,tt,fam),t in zip(LINEAS,textos))+'</svg>'
    if guia:
        b+=''.join(f'<div style="position:absolute;left:{TX}px;top:{base}px;width:1000px;height:4px;background:#ff3b6b"></div>' for n,base,tt,fam in LINEAS)
    return f'<div style="position:relative;width:3840px;height:2160px;{fondo}">{b}</div>'
EJ={'otono':('Otoño · 15 de octubre','12°C','Parcialmente nublado','Waterstown Park · Dublín','parcial'),
    'halloween':('31 de octubre','9°C','Niebla','Phoenix Park · Dublín','niebla'),
    'invierno':('Invierno · enero','3°C','Despejado','Howth · Dublín','despejado'),
    'navidad':('24 de diciembre','5°C','Lluvia','Grafton Street · Dublín','lluvia'),
    'sanpatricio':('17 de marzo','10°C','Nublado',"O'Connell Street · Dublín",'nublado'),
    'primavera':('Primavera · abril','14°C','Parcialmente nublado','St Stephen\'s Green','parcial'),
    'verano':('Verano · julio','22°C','Despejado','Bray · Wicklow','despejado')}
def prueba(foto,out):
    jobs=[(f'{out}/prueba_{k}.png',tarjeta(k,v[4],'ES',v[:4],fondo=f'background:url(file://{foto}) center/cover'),(3840,2160),1) for k,v in EJ.items()]
    asyncio.run(A.generar(jobs))
def todo(out='temporadas'):
    jobs=[]
    for k in TEMAS:
        for lang in ('ES','EN'):
            for c in A.CIELOS:
                jobs.append((f'{out}/{k}/{lang}/placa-{k}_{c}_4K.png',tarjeta(k,c,lang),(3840,2160),1))
        jobs.append((f'{out}/{k}/guia_4K.png',tarjeta(k,'nublado','ES',guia=True).replace('<div style="position:absolute;left:{}px;top:{}px;width:{}px'.format(CX,CT,CW),'<div style="display:none;left:0;top:0;width:0px'),(3840,2160),1))
    asyncio.run(A.generar(jobs))
if __name__=='__main__':
    if len(sys.argv)>2 and sys.argv[1]=='prueba': prueba(sys.argv[2],sys.argv[3])
    else: todo()

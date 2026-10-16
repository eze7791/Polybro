import asyncio, sys
import agregados as A
import logo as L
# Placa "ventana de temporada": una ventana ilustrada como las del logo (220x320, esquinas redondeadas)
# con una escena de la época, y al lado la info del día: etiqueta, fecha/estación, temperatura + cielo
# y ubicación (más grande). Cuadro completo 4K transparente; Ivan escribe 4 textos.
# Uso: python3 ventanas_temporada.py           → todas las escenas × estados del cielo × ES/EN
#      python3 ventanas_temporada.py prueba FOTO DIR
CREMA=A.CREMA
def arbol(x,y,s,cols,tronco='#5a3c2c'):
    c=''.join(f'<circle cx="{x+dx*s:.1f}" cy="{y+dy*s:.1f}" r="{r*s:.1f}" fill="{cols[i%len(cols)]}"/>' for i,(dx,dy,r) in enumerate([(-14,0,15),(0,-12,17),(14,-2,15),(-6,8,14),(9,8,13)]))
    return f'<path d="M{x} {y+44*s} V{y+4*s}" stroke="{tronco}" stroke-width="{3.4*s}" stroke-linecap="round"/>{c}'
def hojita(x,y,r,c): return f'<ellipse cx="{x}" cy="{y}" rx="3.2" ry="5.5" fill="{c}" transform="rotate({r} {x} {y})"/>'
def pino(x,base,h,c,nieve=None):
    p=L.pine(x,base,h,c)
    return p+(L.pine(x,base-h*.45,h*.55,nieve).replace('<path','<path opacity=".9"') if nieve else '')
ESCENAS={}
ESCENAS['otono']='''<defs><linearGradient id="vo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e3a07a"/><stop offset=".6" stop-color="#f4d3a6"/></linearGradient></defs>
<rect width="220" height="320" fill="url(#vo)"/><circle cx="165" cy="118" r="26" fill="#f9e2b6"/>
<path d="M0 192 Q60 160 120 182 T220 170 V320 H0Z" fill="#b07a4c"/><path d="M0 232 Q80 202 150 222 T220 214 V320 H0Z" fill="#8a8a4c"/>
'''+arbol(46,196,1.25,['#c8682e','#d98a3a','#b5532a'])+arbol(176,190,1.1,['#e0a040','#c8682e','#d98a3a'])+arbol(112,176,.75,['#d98a3a','#b5532a','#e3b052'])+'''
<path d="M0 290 Q100 274 220 286 V320 H0Z" fill="#717640"/>
<path d="M58 320 C78 290 130 272 112 240 L124 240 C154 270 126 296 168 320Z" fill="#ead2a2"/>'''+''.join(hojita(x,y,r,c) for x,y,r,c in [(90,120,30,'#c8682e'),(140,150,-40,'#e0a040'),(30,110,60,'#b5532a'),(200,130,10,'#d98a3a'),(120,90,-20,'#e3b052'),(60,150,45,'#d98a3a'),(160,300,80,'#c8682e'),(40,305,-30,'#e0a040'),(190,300,20,'#b5532a')])
ESCENAS['halloween']='''<defs><linearGradient id="vh" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d1630"/><stop offset=".75" stop-color="#4a3462"/></linearGradient>
<radialGradient id="vhg"><stop offset="0" stop-color="#f3a04a" stop-opacity=".7"/><stop offset="1" stop-color="#f3a04a" stop-opacity="0"/></radialGradient></defs>
<rect width="220" height="320" fill="url(#vh)"/>'''+''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity=".8"/>' for x,y,r in [(20,30,1.2),(60,60,.9),(190,40,1.1),(100,20,.8),(30,140,.8),(205,150,1)])+'''
<circle cx="140" cy="92" r="40" fill="#efe2c2"/><circle cx="128" cy="82" r="7" fill="#e2d2ae"/><circle cx="152" cy="104" r="5" fill="#e2d2ae"/>
<g fill="#120c1a">'''+''.join(f'<path transform="translate({x},{y}) scale({s})" d="M0 0 C-4 -5 -11 -7 -20 -4 C-16 -2 -15 1 -16 4 C-12 1 -8 2 -6 5 C-4 2 -2 2 0 4 C2 2 4 2 6 5 C8 2 12 1 16 4 C15 1 16 -2 20 -4 C11 -7 4 -5 0 0Z"/>' for x,y,s in [(110,70,1.2),(170,120,.9),(80,110,.7)])+'''</g>
<path d="M0 210 Q70 180 140 200 T220 190 V320 H0Z" fill="#2a1f3c"/>
<g fill="#1a1226"><rect x="38" y="118" width="22" height="92"/><path d="M36 120 L49 96 L62 120Z"/><rect x="60" y="170" width="26" height="40"/><path d="M60 170 v-6 h5 v6 h5 v-8 h5 v8 h5 v-5 h6 v5"/></g>
<rect x="45" y="140" width="4" height="7" fill="#f3c46a" opacity=".85"/>
<path d="M0 255 Q100 240 220 252 V320 H0Z" fill="#1c1626"/>
<circle cx="150" cy="272" r="40" fill="url(#vhg)"/>
<g transform="translate(150,276) scale(.42)"><path d="M-4 -46 C-2 -60 6 -66 14 -66" stroke="#4d6b3a" stroke-width="9" fill="none" stroke-linecap="round"/><ellipse cx="-34" cy="0" rx="36" ry="44" fill="#d9772f"/><ellipse cx="34" cy="0" rx="36" ry="44" fill="#d9772f"/><ellipse cx="0" cy="0" rx="34" ry="48" fill="#e8873a"/><path d="M-40 -14 l14 -10 l6 16z M40 -14 l-14 -10 l-6 16z M-36 14 Q0 40 36 14 L28 18 L22 10 L14 22 L6 12 L-2 24 L-10 12 L-18 22 L-26 10 Z" fill="#fbd27a"/></g>'''
ESCENAS['navidad']='''<defs><linearGradient id="vn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#121c34"/><stop offset=".8" stop-color="#2c3d60"/></linearGradient></defs>
<rect width="220" height="320" fill="url(#vn)"/>'''+''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity="{o}"/>' for x,y,r,o in [(20,40,1.2,.8),(80,20,1,.8),(200,60,1.3,.8),(150,30,.9,.7),(30,120,2,.5),(110,90,1.6,.5),(190,150,1.8,.5),(60,170,1.4,.5),(170,200,1.6,.5)])+'''
<path d="M0 248 Q90 228 220 244 V320 H0Z" fill="#e6edf3"/><path d="M0 270 Q110 256 220 268 V320 H0Z" fill="#cfd9e3"/>
<rect x="18" y="168" width="96" height="84" fill="#9a4d3c"/><path d="M12 170 L66 132 L120 170Z" fill="#6f3a30"/><path d="M14 170 L66 134 L118 170 L110 172 L66 142 L22 172Z" fill="#f2f5f8"/>
<g fill="#f3d27a"><rect x="28" y="182" width="16" height="20"/><rect x="88" y="182" width="16" height="20"/><rect x="28" y="214" width="16" height="20"/><rect x="88" y="214" width="16" height="20"/></g>
<path d="M56 252 V222 a10 10 0 0 1 20 0 V252Z" fill="#b8362f"/><path d="M56 222 a10 10 0 0 1 20 0Z" fill="#f3d27a" opacity=".8"/>
<circle cx="66" cy="234" r="6" fill="none" stroke="#2f6b45" stroke-width="3.2"/><circle cx="66" cy="239" r="1.6" fill="#d0524a"/>
'''+pino(170,262,128,'#2f6b45')+''.join(f'<circle cx="{x}" cy="{y}" r="2.6" fill="{c}"/>' for x,y,c in [(160,180,'#f3d27a'),(178,196,'#e07a6e'),(156,214,'#bfdcee'),(184,226,'#f3d27a'),(150,240,'#e07a6e'),(170,248,'#bfdcee'),(190,246,'#f3d27a'),(168,206,'#e07a6e')])+'<path d="M170 128 l4 9 l9 1 l-7 6 l2 9 l-8 -5 l-8 5 l2 -9 l-7 -6 l9 -1z" fill="#f3d27a"/>'
ESCENAS['invierno']='''<defs><linearGradient id="vi" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b6c7d8"/><stop offset=".7" stop-color="#eaf0f4"/></linearGradient></defs>
<rect width="220" height="320" fill="url(#vi)"/><circle cx="60" cy="96" r="22" fill="#f6f3e8" opacity=".9"/>
<path d="M0 180 L50 128 L84 156 L128 104 L172 150 L220 124 V230 H0Z" fill="#9fb2c4"/><path d="M128 104 L144 122 L136 120 L128 130 L118 118Z M50 128 L62 140 L50 138 L42 146 Z" fill="#f4f7fa"/>
<path d="M0 220 Q70 196 140 214 T220 206 V320 H0Z" fill="#f2f5f8"/><ellipse cx="120" cy="262" rx="70" ry="12" fill="#cfe0ea"/><ellipse cx="110" cy="260" rx="36" ry="4" fill="#eaf3f8"/>
<path d="M0 286 Q110 270 220 284 V320 H0Z" fill="#e2e9ef"/>
<g stroke="#6b5a50" stroke-linecap="round" fill="none"><path d="M40 270 V200 M40 222 L26 206 M40 212 L54 194 M40 236 L52 226 M26 206 L20 198 M54 194 L58 184" stroke-width="3"/><path d="M186 262 V206 M186 224 L174 212 M186 216 L198 200 M174 212 L170 204" stroke-width="2.6"/></g>
'''+''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity=".85"/>' for x,y,r in [(20,40,1.6),(90,30,1.2),(160,60,1.8),(200,100,1.3),(130,150,1.5),(30,160,1.2),(100,190,1.6),(180,180,1.2)])
ESCENAS['sanpatricio']='''<defs><linearGradient id="vs" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#93c3e0"/><stop offset=".7" stop-color="#e2eff5"/></linearGradient></defs>
<rect width="220" height="320" fill="url(#vs)"/><g fill="#fff" opacity=".85"><ellipse cx="50" cy="60" rx="26" ry="9"/><ellipse cx="66" cy="54" rx="16" ry="8"/></g>
<g fill="none" stroke-width="7" opacity=".75">'''+''.join(f'<path d="M{110-r} 236 A{r} {r} 0 0 1 {110+r} 236" stroke="{c}"/>' for r,c in [(120,'#d9776e'),(113,'#e6a35a'),(106,'#e8cf6a'),(99,'#7fb06a'),(92,'#6c9cc8'),(85,'#9c86c4')])+'''</g>
<path d="M0 200 Q60 168 120 190 T220 180 V320 H0Z" fill="#6fa862"/><path d="M0 238 Q80 210 150 230 T220 222 V320 H0Z" fill="#4f9450"/><path d="M0 280 Q100 262 220 276 V320 H0Z" fill="#3f8244"/>
<g transform="translate(206,232) scale(.55)"><ellipse cx="0" cy="0" rx="22" ry="16" fill="#2a2a2a"/>'''+''.join(f'<circle cx="{x}" cy="{y}" r="7" fill="#e8c35a" stroke="#b8902e" stroke-width="1.5"/>' for x,y in [(-10,-14),(4,-18),(14,-12),(-2,-10)])+'''</g>
<g fill="#5fae66">'''+''.join(f'<g transform="translate({x},{y}) scale({s})">'+''.join(f'<path transform="rotate({a})" d="M0 0 C-14 -10 -18 -26 -8 -30 C-3 -32 0 -28 0 -24 C0 -28 3 -32 8 -30 C18 -26 14 -10 0 0Z"/>' for a in (0,120,240))+'<path d="M0 0 C-2 14 -6 26 -14 36" stroke="#3c7d48" stroke-width="4" fill="none"/></g>' for x,y,s in [(40,292,.42),(90,305,.32),(170,298,.38)])+'</g>'
ESCENAS['primavera']='''<defs><linearGradient id="vp" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b8d4ea"/><stop offset=".75" stop-color="#f6e2e6"/></linearGradient></defs>
<rect width="220" height="320" fill="url(#vp)"/><g fill="#fff" opacity=".85"><ellipse cx="160" cy="56" rx="24" ry="8"/><ellipse cx="176" cy="50" rx="14" ry="7"/></g>
<path d="M0 196 Q60 166 120 186 T220 176 V320 H0Z" fill="#a6cb8e"/><path d="M0 240 Q80 214 150 232 T220 226 V320 H0Z" fill="#8bba76"/>
<path d="M70 262 V170 M70 200 L48 180 M70 188 L96 166" stroke="#6b4a3a" stroke-width="6" stroke-linecap="round" fill="none"/>
'''+''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for x,y,r,c in [(40,160,20,'#f1b9c8'),(64,140,24,'#e79ab0'),(92,150,22,'#f6cbd6'),(108,170,16,'#f1b9c8'),(50,184,16,'#e79ab0'),(80,176,20,'#f6cbd6'),(28,178,12,'#f6cbd6')])+''.join(f'<ellipse cx="{x}" cy="{y}" rx="2.6" ry="1.8" fill="#f1b9c8" transform="rotate({r} {x} {y})"/>' for x,y,r in [(130,200,20),(150,230,-30),(120,250,40),(30,230,10),(100,220,-20)])+'''
<path d="M0 286 Q100 272 220 284 V320 H0Z" fill="#79a866"/>'''+L.sheep(150,262,1.2)+L.sheep(186,276,.9)+''.join(f'<circle cx="{x}" cy="{y}" r="2" fill="{c}"/>' for x,y,c in [(20,300,'#f3d27a'),(50,310,'#fff'),(110,302,'#f1b9c8'),(200,306,'#f3d27a'),(130,312,'#fff')])
ESCENAS['verano']='''<defs><linearGradient id="vv" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#78bde6"/><stop offset=".6" stop-color="#d4eef8"/></linearGradient>
<linearGradient id="vm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a95ae"/><stop offset="1" stop-color="#5fb6c4"/></linearGradient></defs>
<rect width="220" height="320" fill="url(#vv)"/><g stroke="#f8d77a" stroke-width="3" stroke-linecap="round">'''+''.join(f'<path d="M60 70 m0 -36 v-10" transform="rotate({a} 60 70)"/>' for a in range(0,360,45))+'''</g><circle cx="60" cy="70" r="24" fill="#f8d77a"/>
<rect x="0" y="190" width="220" height="80" fill="url(#vm)"/><g stroke="#eaf7fa" stroke-width="2" stroke-linecap="round" opacity=".8"><path d="M20 210 h18 M70 226 h14 M30 246 h20 M110 214 h12"/></g>
<path d="M120 320 L120 186 Q150 160 220 166 V320Z" fill="#6f9a5a"/><path d="M120 186 L120 320 L140 320 L136 200Z" fill="#a49a86"/>
<rect x="168" y="118" width="16" height="50" fill="#f4f1ea"/><rect x="168" y="128" width="16" height="7" fill="#c8574a"/><rect x="168" y="146" width="16" height="7" fill="#c8574a"/><rect x="165" y="110" width="22" height="9" fill="#3a3a3a"/><path d="M164 110 L176 98 L188 110Z" fill="#c8574a"/><rect x="171" y="112" width="10" height="5" fill="#f8d77a"/>
<path d="M0 268 Q60 256 120 266 V320 H0Z" fill="#ecd9a8"/><path d="M0 262 q15 -6 30 0 t30 0 t30 0 t30 0" stroke="#fff" stroke-width="2.5" fill="none" opacity=".8"/>'''
ESCENAS['argentina']=L.P['ar_ba']
ESCENAS['patagonia']=L.P['ar_pat']
TEMAS={  # etiqueta ES, EN, color de acento
 'otono':('OTOÑO','AUTUMN','#E3A15B'),'halloween':('HALLOWEEN','HALLOWEEN','#F0954A'),'navidad':('NAVIDAD','CHRISTMAS','#E07A6E'),
 'invierno':('INVIERNO','WINTER','#BFDCEE'),'sanpatricio':('SAN PATRICIO',"ST. PATRICK'S",'#8BD08E'),'primavera':('PRIMAVERA','SPRING','#F2B8C8'),
 'verano':('VERANO','SUMMER','#F3C766'),'argentina':('ARGENTINA','ARGENTINA','#9CCBEA'),'patagonia':('PATAGONIA','PATAGONIA','#86CFC8')}
# ---------- medidas (4K) ----------
WS=1.6; WW,WH=220*WS,320*WS; WX=150; WY=2010-WH          # ventana 352x512, abajo a la izquierda
X0=WX+WW+70                                              # columna de íconos/etiqueta (572)
ICX=X0+55; TX=X0+128                                     # centro de íconos (627) y textos (700)
B_ET,B_FE,B_TC,B_UB=1580,1745,1870,2000                  # líneas base: etiqueta, fecha, temp+cielo, ubicación
CIELO_IC,CIELO_TX=1010,1085
def placa(tema,cielo,lang,textos=None,fondo='',guia=False):
    es,en,ac=TEMAS[tema]; et=es if lang=='ES' else en
    halo='filter:drop-shadow(0 0 16px rgba(20,26,38,.65)) drop-shadow(0 3px 5px rgba(0,0,0,.4))'
    b=f'<div style="position:absolute;left:{X0-120}px;top:{WY-60}px;width:1650px;height:{WH+140}px;background:radial-gradient(closest-side,rgba(20,26,38,.5),rgba(20,26,38,0));filter:blur(12px)"></div>'
    b+=f'''<div style="position:absolute;left:{WX}px;top:{WY}px;width:{WW}px;height:{WH}px;border-radius:{22*WS}px;overflow:hidden;box-shadow:0 12px 40px rgba(0,0,0,.35),0 0 0 4px rgba(242,238,230,.9)">
<svg width="{WW}" height="{WH}" viewBox="0 0 220 320"><defs><filter id="satv"><feColorMatrix type="saturate" values=".75"/></filter></defs><g filter="url(#satv)">{ESCENAS[tema]}</g></svg></div>'''
    b+=f'<div style="position:absolute;left:{X0}px;top:{B_ET-48}px;font-family:JS;font-weight:700;font-size:50px;letter-spacing:12px;color:{ac};{halo}">{et}</div>'
    lw=480; d=f'M14 0 C {lw*.21} -18, {lw*.33} 14, {lw*.5} 2 S {lw*.81} -16, {lw-12} 2'
    b+=f'<svg style="position:absolute;left:{X0}px;top:{B_ET+22}px;overflow:visible;{halo}" width="{lw+30}" height="40" viewBox="-10 -30 {lw+30} 40"><circle r="7" fill="{ac}"/><path d="{d}" fill="none" stroke="{ac}" stroke-width="4" stroke-linecap="round" stroke-dasharray="12 10"/><path d="M{lw} 6 c-9 -12 -14 -17 -14 -24 a14 14 0 0 1 28 0 c0 7 -5 12 -14 24z" fill="none" stroke="{ac}" stroke-width="3.5" stroke-linejoin="round"/><circle cx="{lw}" cy="-18" r="5" fill="{ac}"/></svg>'
    def ic(n,cx,base,tam): return f'<div style="position:absolute;left:{cx-tam/2}px;top:{base-tam*.37-tam/2}px;{halo}">{A.icono(n,ac,tam,2.6*120/tam)}</div>'
    b+=ic('calendario',ICX,B_FE,120)+ic('temperatura',ICX,B_TC,116)+ic(A.CIELOS[cielo],CIELO_IC,B_TC,120)+ic('ubicacion',ICX,B_UB,150)
    if textos:
        b+='<svg style="position:absolute;left:0;top:0;overflow:visible" width="3840" height="2160"><defs><filter id="s" x="-20%" y="-60%" width="140%" height="220%"><feDropShadow dx="0" dy="0" stdDeviation="14" flood-color="#141A26" flood-opacity=".7"/></filter></defs>'
        for (x,y,fam,tt),t in zip(((TX,B_FE,'CG',92),(TX,B_TC,'JS',84),(CIELO_TX,B_TC,'CG',92),(TX,B_UB,'CG',124)),textos):
            b+=f'<text x="{x}" y="{y}" font-family="{fam}" font-weight="700" font-size="{tt}" fill="{CREMA}" filter="url(#s)">{t}</text>'
        b+='</svg>'
    if guia:
        b+=''.join(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:4px;background:#ff3b6b"></div>' for x,y,w in ((TX,B_FE,900),(TX,B_TC,250),(CIELO_TX,B_TC,800),(TX,B_UB,1200)))
    return f'<div style="position:relative;width:3840px;height:2160px;{fondo}">{b}</div>'
EJ={'otono':('Otoño · 15 de octubre','12°C','Parcialmente nublado','Waterstown Park · Dublín','parcial'),
    'halloween':('31 de octubre','9°C','Niebla','Phoenix Park · Dublín','niebla'),
    'navidad':('24 de diciembre','5°C','Lluvia','Grafton Street · Dublín','lluvia'),
    'invierno':('Invierno · enero','3°C','Despejado','Howth · Dublín','despejado'),
    'sanpatricio':('17 de marzo','10°C','Nublado',"O'Connell Street · Dublín",'nublado'),
    'primavera':('Primavera · abril','14°C','Parcialmente nublado',"St Stephen's Green",'parcial'),
    'verano':('Verano · julio','22°C','Despejado','Bray · Wicklow','despejado'),
    'argentina':('Primavera · noviembre','24°C','Despejado','Av. 9 de Julio · Buenos Aires','despejado'),
    'patagonia':('Verano · enero','16°C','Viento','El Chaltén · Santa Cruz','viento')}
def prueba(foto,out):
    asyncio.run(A.generar([(f'{out}/prueba_{k}.png',placa(k,v[4],'ES',v[:4],fondo=f'background:url(file://{foto}) center/cover'),(3840,2160),1) for k,v in EJ.items()]))
def todo(out='ventanas-temporada'):
    jobs=[(f'{out}/{k}/{lang}/placa-{k}_{c}_4K.png',placa(k,c,lang),(3840,2160),1) for k in TEMAS for lang in ('ES','EN') for c in A.CIELOS]
    jobs+=[(f'{out}/{k}/guia_4K.png',placa(k,'nublado','ES',guia=True),(3840,2160),1) for k in TEMAS]
    asyncio.run(A.generar(jobs))
if __name__=='__main__':
    if len(sys.argv)>3 and sys.argv[1]=='prueba': prueba(sys.argv[2],sys.argv[3])
    else: todo()

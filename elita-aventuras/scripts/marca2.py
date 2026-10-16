import asyncio, sys
import agregados as A, sendero as S
# Marca de agua v2 "Elita Adventures", en sintonía con el kit sendero, el opening y el closing.
# Tres estilos: crema (texto con halo), blanco (texto con halo) y papel (píldora del kit sendero).
# Cuadro completo transparente, abajo a la derecha. Medidas en unidades 1080p (se renderiza a 2x = 4K).
HALO='filter:drop-shadow(0 0 6px rgba(20,26,38,.7)) drop-shadow(0 1px 2px rgba(0,0,0,.5))'
def camino(col,lw=150,sw=2.2):
    d=f'M8 0 C {lw*.21} -8, {lw*.33} 6, {lw*.5} 1 S {lw*.81} -7, {lw-8} 1'
    return f'<svg width="{lw+16}" height="20" viewBox="-6 -14 {lw+16} 20" style="display:block;overflow:visible"><circle r="2.6" fill="{col}"/><path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-dasharray="5 4"/><path d="M{lw} 3 c-4 -5 -6 -7 -6 -10 a6 6 0 0 1 12 0 c0 3 -2 5 -6 10z" fill="none" stroke="{col}" stroke-width="1.8"/><circle cx="{lw}" cy="-7.5" r="2" fill="{col}"/></svg>'
def texto(col,col2):
    # "Elita" en Cormorant + camino + ADVENTURES en Josefin, centrados
    return f'''<div style="display:flex;flex-direction:column;align-items:center;color:{col}">
<div style="font-family:CG;font-weight:700;font-size:40px;line-height:.9">Elita</div>
<div style="margin:3px 0 2px">{camino(col2)}</div>
<div style="font-family:JS;font-weight:700;font-size:13px;letter-spacing:5.5px;margin-left:5.5px">ADVENTURES</div></div>'''
def marca(estilo):
    if estilo=='crema': b=f'<div style="{HALO}">{texto("#F2EEE6","#F2EEE6")}</div>'
    elif estilo=='blanco': b=f'<div style="{HALO}">{texto("#FFFFFF","#FFFFFF")}</div>'
    else:
        p=S.GENERAL
        b=f'''<div style="display:flex;align-items:center;height:46px;padding:0 18px 0 6px;background:{S.PAPEL};border:3px solid {p["o"]};border-radius:26px;{S.SOMBRA.replace('10px','6px')}">
<div style="width:34px;height:34px;border-radius:50%;background:{p["c"]};border:2px solid {p["o"]};display:flex;align-items:center;justify-content:center;margin-right:10px">{A.icono("ubicacion",S.PAPEL,22,2.8)}</div>
<div style="font-family:CG;font-weight:700;font-size:24px;color:#2A2C27;margin-right:8px">Elita</div>
<div style="font-family:JS;font-weight:700;font-size:13px;letter-spacing:4px;color:{p["o"]};padding-top:3px">ADVENTURES</div></div>'''
    return f'<div style="position:relative;width:1920px;height:1080px"><div style="position:absolute;right:56px;bottom:44px;opacity:.88">{b}</div></div>'
ESTILOS=('crema','blanco','papel')
if __name__=='__main__':
    if sys.argv[1:2]==['prueba']:
        fotos=sys.argv[2].split(','); out=sys.argv[3]; jobs=[]
        for e in ESTILOS:
            for i,f in enumerate(fotos):
                jobs.append((f'{out}/{e}_{i}.png',marca(e).replace('<div style="position:relative;width:1920px;height:1080px">',f'<div style="position:relative;width:1920px;height:1080px;background:url(file://{f}) center/cover">',1),(1920,1080),2))
        asyncio.run(A.generar(jobs))
    else:
        out=sys.argv[1] if len(sys.argv)>1 else 'marca2'
        asyncio.run(A.generar([(f'{out}/marca-de-agua_{e}_4K.png',marca(e),(1920,1080),2) for e in ESTILOS]+[(f'{out}/marca-de-agua_{e}_1080p.png',marca(e),(1920,1080),1) for e in ESTILOS]))

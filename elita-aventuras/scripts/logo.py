import asyncio, os, random
from playwright.async_api import async_playwright
random.seed(7)
W,H,G=220,320,20
def rain():
    s=''
    for i in range(70):
        x=random.uniform(-40,240);y=random.uniform(-20,300)
        s+=f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x-7:.1f}" y2="{y+18:.1f}"/>'
    return f'<g stroke="#e9eef0" stroke-width="1.1" opacity=".55" stroke-linecap="round">{s}</g>'
def stars():
    return ''.join(f'<circle cx="{random.uniform(5,215):.1f}" cy="{random.uniform(5,150):.1f}" r="{random.choice([.7,.9,1.2,1.5])}" fill="#fff" opacity="{random.uniform(.5,1):.2f}"/>' for _ in range(45))
def jacaranda(x,y,s=1):
    blobs=''.join(f'<circle cx="{x+dx*s:.1f}" cy="{y+dy*s:.1f}" r="{r*s:.1f}" fill="{c}"/>' for dx,dy,r,c in
      [(-18,0,16,'#8f78b8'),(0,-10,19,'#a08bc9'),(18,-2,16,'#8f78b8'),(-6,8,15,'#b3a0d6'),(10,8,14,'#9c86c4'),(-24,10,10,'#a08bc9'),(24,10,10,'#b3a0d6')])
    return f'<path d="M{x} {y+50*s} L{x} {y+6*s} M{x} {y+22*s} L{x-12*s} {y+6*s} M{x} {y+18*s} L{x+12*s} {y+4*s}" stroke="#4a3b3a" stroke-width="{3*s}" fill="none" stroke-linecap="round"/>{blobs}'
def sheep(x,y,s=1):
    return f'<g transform="translate({x},{y}) scale({s})"><ellipse cx="0" cy="0" rx="9" ry="6" fill="#f4f1ea"/><circle cx="-6" cy="-3" r="4" fill="#f4f1ea"/><circle cx="5" cy="-3" r="4" fill="#f4f1ea"/><ellipse cx="10" cy="-1" rx="3.2" ry="4" fill="#2d2a28"/><line x1="-4" y1="5" x2="-4" y2="10" stroke="#2d2a28" stroke-width="1.6"/><line x1="4" y1="5" x2="4" y2="10" stroke="#2d2a28" stroke-width="1.6"/></g>'
def pine(x,base,h,c):
    w=h*.36
    return f'<path d="M{x} {base-h} L{x+w*.55} {base-h*.55} L{x+w*.3} {base-h*.55} L{x+w*.8} {base-h*.2} L{x+w*.45} {base-h*.2} L{x+w} {base} L{x-w} {base} L{x-w*.45} {base-h*.2} L{x-w*.8} {base-h*.2} L{x-w*.3} {base-h*.55} L{x-w*.55} {base-h*.55}Z" fill="{c}"/>'
P={}
P['ar_ba']=f'''
<defs><linearGradient id="s1" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8f86b3"/><stop offset=".45" stop-color="#d9a7a0"/><stop offset=".75" stop-color="#f3c79a"/></linearGradient></defs>
<rect width="220" height="320" fill="url(#s1)"/>
<circle cx="150" cy="205" r="34" fill="#f8dfb2" opacity=".95"/>
<path d="M0 215 h20 v-22 h14 v14 h10 v-30 h16 v38 h12 v-16 h12 v22 h20 v-12 h14 v-24 h12 v30 h16 v-18 h16 v10 h12 v-28 h14 v34 h22 V320 H0Z" fill="#9a8aa6" opacity=".75"/>
<path d="M104 92 L110 70 L116 92 L119 236 L101 236Z" fill="#efe6da"/><path d="M110 70 L116 92 L119 236 L110 236Z" fill="#cdbfb5"/>
<rect x="0" y="232" width="220" height="88" fill="#7d6f78"/>
<path d="M60 320 L102 236 L118 236 L160 320Z" fill="#9c8c8e"/>
<path d="M110 250 V320" stroke="#efe6da" stroke-width="2" stroke-dasharray="8 8"/>
{jacaranda(32,214,1.25)}{jacaranda(192,222,1.15)}
<g fill="#b3a0d6" opacity=".9"><circle cx="30" cy="300" r="3"/><circle cx="48" cy="292" r="2.5"/><circle cx="178" cy="304" r="3"/><circle cx="196" cy="296" r="2.4"/><circle cx="60" cy="310" r="2"/></g>'''
P['ar_pat']=f'''
<defs><linearGradient id="s1b" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8f86b3"/><stop offset=".5" stop-color="#e2aea2"/><stop offset=".8" stop-color="#f3c79a"/></linearGradient>
<linearGradient id="lk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7fb2b5"/><stop offset="1" stop-color="#4f8790"/></linearGradient></defs>
<rect width="220" height="320" fill="url(#s1b)"/>
<circle cx="40" cy="150" r="22" fill="#f8dfb2" opacity=".9"/>
<path d="M0 205 L30 170 L52 182 L74 140 L88 150 L104 74 L114 96 L122 60 L134 100 L144 86 L160 140 L178 128 L200 165 L220 152 V230 H0Z" fill="#b48b86"/>
<path d="M98 100 L104 74 L110 92 L114 96 L122 60 L130 88 L134 100 L126 96 L120 108 L114 100 L106 110Z" fill="#f2e3d6"/>
<path d="M0 205 L30 170 L52 182 L74 140 L88 150 L80 200 Z" fill="#9b7576" opacity=".6"/>
<rect x="0" y="222" width="220" height="40" fill="url(#lk)"/>
<path d="M0 222 h220" stroke="#e9d8c8" stroke-width="1.5" opacity=".6"/>
<path d="M0 262 Q60 248 120 258 T220 252 V320 H0Z" fill="#b7a170"/>
<path d="M0 286 Q70 272 140 284 T220 278 V320 H0Z" fill="#9b8656"/>
<g stroke="#7d6c45" stroke-width="1.2">{''.join(f'<line x1="{x}" y1="{300-((x*7)%9)}" x2="{x+3}" y2="{290-((x*5)%8)}"/>' for x in range(8,220,13))}</g>'''
P['de']=f'''
<defs><linearGradient id="s2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9fc0d8"/><stop offset="1" stop-color="#dfeaf0"/></linearGradient></defs>
<rect width="220" height="320" fill="url(#s2)"/>
<g fill="#fff" opacity=".85"><ellipse cx="50" cy="48" rx="26" ry="9"/><ellipse cx="68" cy="42" rx="18" ry="9"/><ellipse cx="170" cy="70" rx="22" ry="7"/></g>
<path d="M0 170 L40 110 L62 130 L96 72 L128 120 L150 98 L190 140 L220 120 V200 H0Z" fill="#9aaebf"/>
<path d="M96 72 L110 92 L102 90 L96 100 L88 88 L82 92Z M40 110 L50 124 L44 122 L36 128 L33 120Z M150 98 L160 110 L152 108 L146 114Z" fill="#f5f7f8"/>
<path d="M0 210 Q50 170 110 190 T220 180 V320 H0Z" fill="#5f7d5e"/>
<g>{''.join(pine(x,y,h,'#46634a') for x,y,h in [(14,222,40),(34,214,34),(186,212,36),(206,220,42),(170,226,30)])}</g>
<path d="M58 260 Q70 214 88 200 L100 192 L130 190 L144 204 Q160 230 170 260Z" fill="#8a8578"/><path d="M88 200 L100 192 L112 192 L98 226 L80 240Z" fill="#a19b8c"/>{''.join(pine(x,y,h,'#4c6a4f') for x,y,h in [(62,262,30),(76,266,26),(156,262,28),(170,268,32)])}
<g fill="#ece6dc"><rect x="96" y="150" width="36" height="44"/><rect x="88" y="130" width="12" height="64"/><rect x="128" y="138" width="11" height="56"/><rect x="108" y="118" width="14" height="40"/></g>
<g fill="#6f8698"><path d="M86 130 L94 108 L102 130Z"/><path d="M126 138 L133.5 118 L141 138Z"/><path d="M106 118 L115 92 L124 118Z"/><path d="M94 150 L114 138 L134 150Z"/></g>
<g fill="#7c8a96"><rect x="92" y="140" width="3" height="6"/><rect x="113" y="128" width="4" height="7"/><rect x="104" y="162" width="3" height="7"/><rect x="113" y="162" width="3" height="7"/><rect x="122" y="162" width="3" height="7"/><rect x="132" y="150" width="3" height="6"/></g>
<path d="M0 262 Q60 240 130 258 T220 250 V320 H0Z" fill="#6f8f68"/>
<path d="M0 290 Q80 276 150 290 T220 286 V320 H0Z" fill="#587a55"/>'''
P['ie']=f'''
<defs><linearGradient id="s3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9aa3a8"/><stop offset="1" stop-color="#cfd4d3"/></linearGradient></defs>
<rect width="220" height="320" fill="url(#s3)"/>
<g fill="#b4babc"><ellipse cx="60" cy="40" rx="60" ry="20"/><ellipse cx="170" cy="30" rx="70" ry="22"/></g>
<path d="M0 160 Q60 120 120 145 T220 135 V200 H0Z" fill="#8ea38a"/>
<g fill="#8b8a84"><rect x="150" y="112" width="18" height="30"/><path d="M150 112 v-6 h4 v4 h4 v-4 h4 v6 h-12" /><rect x="166" y="122" width="10" height="20"/></g>
<rect x="156" y="120" width="3" height="5" fill="#5e5d58"/>
<path d="M0 200 Q70 165 140 190 T220 180 V320 H0Z" fill="#79976e"/>
<path d="M0 250 Q80 220 160 240 T220 236 V320 H0Z" fill="#668a5d"/>
<g fill="none" stroke="#a3a097" stroke-width="3" stroke-dasharray="4 2.5" stroke-linecap="round">
<path d="M0 212 Q70 185 140 205 T220 196"/><path d="M0 262 Q80 236 160 252 T220 250"/><path d="M110 196 Q100 230 104 262"/></g>
{sheep(50,226,1.1)}{sheep(150,218,1)}{sheep(80,280,1.3)}{sheep(178,276,1.2)}
{rain()}'''
P['nt']=f'''
<defs><linearGradient id="s4" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#141c33"/><stop offset=".7" stop-color="#22334d"/></linearGradient>
<linearGradient id="au" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8be0b6" stop-opacity="0"/><stop offset=".5" stop-color="#7fd9ae" stop-opacity=".75"/><stop offset="1" stop-color="#5ab894" stop-opacity="0"/></linearGradient>
<filter id="bl"><feGaussianBlur stdDeviation="4"/></filter></defs>
<rect width="220" height="320" fill="url(#s4)"/>{stars()}
<g filter="url(#bl)"><path d="M-10 60 C40 20 80 110 130 60 S200 40 240 70 L240 140 C190 110 150 160 100 120 S20 120 -10 140Z" fill="url(#au)"/>
<path d="M20 30 C70 0 110 70 170 30 L170 80 C120 110 70 50 20 90Z" fill="#a28fd6" opacity=".25"/></g>
<path d="M176 34 a14 14 0 1 0 10 24 a11 11 0 1 1 -10 -24z" fill="#efe9d6"/>
<path d="M0 200 L40 150 L70 170 L110 120 L150 168 L180 146 L220 180 V215 H0Z" fill="#2c3b52"/>
<path d="M110 120 L122 136 L114 134 L108 142 L100 132Z" fill="#c8d0dc"/>
<rect x="0" y="212" width="220" height="50" fill="#1b2a40"/>
<g filter="url(#bl)" opacity=".45"><path d="M-10 230 C40 250 80 222 130 240 S200 236 240 228 L240 250 L-10 252Z" fill="#7fd9ae"/></g>
<ellipse cx="183" cy="226" rx="10" ry="2" fill="#efe9d6" opacity=".35"/>
<path d="M0 262 H220 V320 H0Z" fill="#121a2a"/>
{''.join(pine(x,y,h,'#0f1a24') for x,y,h in [(10,300,80),(32,296,60),(54,304,95),(170,302,90),(194,298,70),(214,304,100)])}'''
def logo(order, sat, dark=False, size_scale=1, dash='', marks=True):
    DASH=dash
    n=len(order); tw=n*W+(n-1)*G
    ink='#EEE7DA' if dark else '#2A2C27'; sand='#C9A978' if dark else '#8C6A3C'
    panels=''
    for i,k in enumerate(order):
        x=i*(W+G)
        panels+=f'<g transform="translate({x},0)"><clipPath id="c{i}"><rect width="{W}" height="{H}" rx="22"/></clipPath><g clip-path="url(#c{i})">{P[k]}</g><rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="22" fill="none" stroke="{ink}" stroke-opacity=".22" stroke-width="1.5"/></g>'
    cx=tw/2
    lw=520
    if marks:
        PATH=f'M14 4 C 90 -46, 160 52, 260 4 S 420 -46, {lw-12} 8'
        START=f'<circle cx="0" cy="4" r="6.5" fill="{sand}"/>'
        END=f'<path d="M{lw} 10 c-9 -12 -14 -17 -14 -24 a14 14 0 0 1 28 0 c0 7 -5 12 -14 24z" fill="none" stroke="{sand}" stroke-width="2.8"/><circle cx="{lw}" cy="-14" r="4.5" fill="{sand}"/>'
    else:
        PATH=f'M0 4 C 80 -46, 160 52, 260 4 S 440 -46, {lw} 4'
        START=END=''
    text=f'''<text x="{cx}" y="{H+150}" text-anchor="middle" font-family="CG" font-weight="600" font-size="150" fill="{ink}">Elita</text>
<g transform="translate({cx-lw/2},{H+208})">{START}
<path d="{PATH}" fill="none" stroke="{sand}" stroke-linecap="round" {DASH if "stroke-width" in DASH else DASH+' stroke-width="3.2"'}/>
{END}</g>
<text x="{cx}" y="{H+285}" text-anchor="middle" font-family="JS" font-weight="600" font-size="40" letter-spacing="17" fill="{ink}">ADVENTURES</text>'''
    th=H+315
    return tw,th,f'<svg xmlns="http://www.w3.org/2000/svg" width="{tw}" height="{th}" viewBox="0 0 {tw} {th}"><defs><filter id="sat"><feColorMatrix type="saturate" values="{sat}"/></filter></defs><g filter="url(#sat)">{panels}</g>{text}</svg>'
CSS='@font-face{font-family:CG;src:url(../fuentes/CG.ttf);font-weight:300 700}@font-face{font-family:JS;src:url(../fuentes/JS.ttf);font-weight:100 700}html,body{margin:0}'
async def main():
    [os.makedirs(f'out/{d}',exist_ok=True) for d in ('1-camino-punteado','2-camino-continuo','3-camino-puntos')]
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(device_scale_factor=2)
        async def render(name,svg,w,h,bg=None,pad=60):
            body=f'<div style="padding:{pad}px;background:{bg or "transparent"};display:inline-block">{svg}</div>'
            open('_l.html','w').write(f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>')
            await pg.set_viewport_size({'width':int(w+2*pad),'height':int(h+2*pad)})
            await pg.goto('file://'+os.getcwd()+'/_l.html'); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(200)
            await pg.screenshot(path=f'out/{name}.png',omit_background=bg is None,clip={'x':0,'y':0,'width':w+2*pad,'height':h+2*pad})
        order=['ar_ba','de','ie','nt']
        for pname,dash in [('1-camino-punteado','stroke-dasharray="11 9"'),('2-camino-continuo',''),('3-camino-puntos','stroke-dasharray="0.1 12" stroke-width="6.5"')]:
          for mname,marks in [('con-salida-y-llegada',True),('sin-salida-ni-llegada',False)]:
            d=f'{pname}/{mname}'; os.makedirs('out/'+d,exist_ok=True)
            for sname,sat in [('muy-sobrio',0.55),('color',0.9)]:
                w,h,svg=logo(order,sat,dash=dash,marks=marks)
                await render(f'{d}/{sname}_claro',svg,w,h,'#F2EEE6')
                await render(f'{d}/{sname}_transparente',svg,w,h)
                w,h,svg=logo(order,sat,dark=True,dash=dash,marks=marks)
                await render(f'{d}/{sname}_oscuro',svg,w,h,'#1E201D')
        await b.close()
if __name__=='__main__': asyncio.run(main())

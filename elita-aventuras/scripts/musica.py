import numpy as np, subprocess, sys, wave
# Música lofi original para el opening y el closing, sintetizada (sin samples ni derechos de terceros).
# Piano eléctrico suave, bajo, batería tenue y crujido de vinilo. 79 BPM: la corchea (0,38 s) coincide con
# el ritmo en que aparecen las ventanas del opening.
SR=48000; BPM=79; B=60/BPM
rng=np.random.default_rng(7)
def hz(n): return 440*2**((n-69)/12)
def env(n,a,d):
    t=np.arange(n)/SR; e=np.minimum(1,t/max(a,1e-4))*np.exp(-t/d); return e
def lowpass(x,fc):
    a=np.exp(-2*np.pi*fc/SR); y=np.empty_like(x); z=0.0
    for i in range(len(x)): z=(1-a)*x[i]+a*z; y[i]=z
    return y
def rhodes(nota,dur,vel=.5):
    n=int(dur*SR); t=np.arange(n)/SR; f=hz(nota)
    w=np.sin(2*np.pi*f*t)+.35*np.sin(2*np.pi*2*f*t+.3)*np.exp(-t/0.4)+.12*np.sin(2*np.pi*3.01*f*t)*np.exp(-t/0.15)
    w*=1+.18*np.sin(2*np.pi*4.5*t)            # trémolo
    return vel*w*env(n,.008,1.6)
def campana(nota,dur=1.6,vel=.35):
    n=int(dur*SR); t=np.arange(n)/SR; f=hz(nota)
    w=np.sin(2*np.pi*f*t)+.4*np.sin(2*np.pi*2.76*f*t)*np.exp(-t/.25)+.2*np.sin(2*np.pi*5.4*f*t)*np.exp(-t/.08)
    return vel*w*env(n,.002,.7)
def bajo(nota,dur,vel=.45):
    n=int(dur*SR); t=np.arange(n)/SR; f=hz(nota)
    return vel*(np.sin(2*np.pi*f*t)+.2*np.sin(2*np.pi*2*f*t))*env(n,.01,dur*.7)
def bombo(vel=.8):
    n=int(.4*SR); t=np.arange(n)/SR; f=48+90*np.exp(-t/.03)
    return vel*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/.16)
def caja(vel=.25):
    n=int(.3*SR); r=rng.standard_normal(n); r=r-lowpass(r,900); t=np.arange(n)/SR
    return vel*(r*np.exp(-t/.07)+.4*np.sin(2*np.pi*190*t)*np.exp(-t/.05))
def hat(vel=.06):
    n=int(.08*SR); r=rng.standard_normal(n); r=r-lowpass(r,5000); return vel*r*np.exp(-np.arange(n)/SR/.018)
def vinilo(dur,vel=.012):
    n=int(dur*SR); x=lowpass(rng.standard_normal(n),2500)*vel
    clics=rng.random(n)<.00012; x[clics]+=rng.uniform(-.25,.25,clics.sum())
    return x
class Mezcla:
    def __init__(s,dur): s.x=np.zeros(int(dur*SR)+SR)
    def add(s,t,w):
        i=int(t*SR); j=min(len(s.x),i+len(w)); s.x[i:j]+=w[:j-i]
    def acorde(s,t,notas,dur,vel=.22):
        for k,n in enumerate(notas): s.add(t+k*.012,rhodes(n,dur,vel))     # leve rasgueo
    def bateria(s,t0,t1,hats=True):
        t=t0; k=0
        while t<t1-1e-6:
            if k%4 in (0,): s.add(t,bombo())
            if k%4==2: s.add(t,bombo(.55))
            if k%4 in (1,3): s.add(t+.02,caja())
            if hats: s.add(t,hat()); s.add(t+B/2+.04,hat(.04))     # swing leve
            t+=B; k+=1
    def final(s,dur,fade_in=.4,fade_out=1.2):
        x=s.x[:int(dur*SR)]+vinilo(dur)
        x=lowpass(x,6500)                                        # cálido, "cinta"
        n=len(x); e=np.ones(n); fi=int(fade_in*SR); fo=int(fade_out*SR)
        e[:fi]=np.linspace(0,1,fi); e[-fo:]=np.linspace(1,0,fo)**1.5
        x*=e; x=np.tanh(1.4*x)/np.tanh(1.4)                       # saturación suave
        return x/np.max(np.abs(x))*.7                             # pico −3 dB
# Acordes (MIDI): Fmaj7, Em7, Dm7, Cmaj7(9)
FMAJ7=[53,57,60,64]; EM7=[52,55,59,62]; DM7=[50,53,57,60]; CMAJ9=[48,52,55,59,62]
def opening(dur=6.0):
    m=Mezcla(dur)
    m.acorde(0,[41+12,57,64],2.0,.10)                            # colchón suave mientras aparece el cielo
    for t,n in zip([.3,.68,1.06,1.44],[65,69,72,76]): m.add(t,campana(n))   # una nota por ventana
    m.add(2.0,bombo(.9)); m.acorde(2.0,FMAJ7,3.0,.24); m.add(2.0,bajo(41,1.5))  # "Elita"
    m.bateria(2.0+B,5.2)
    m.acorde(2.0+2*B,EM7,2.0,.18); m.add(2.0+2*B,bajo(40,1.4))
    for i,t in enumerate(np.arange(2.75,4.0,B/2)): m.add(t,campana([72,74,76,79][i%4],.8,.13))  # el camino se dibuja
    m.add(3.85,campana(81,2.2,.3))                               # el pin
    m.acorde(2.0+4*B,CMAJ9,2.6,.22); m.add(2.0+4*B,bajo(36,2.2))  # ADVENTURES, acorde final
    return m.final(dur,.25,1.0)
def closing(dur=24.2):
    m=Mezcla(dur)
    m.acorde(.3,DM7,4.0,.18); m.add(.3,bajo(38,3))               # "Thanks for walking with me."
    m.add(.9,campana(69,2,.18)); m.add(2.4,campana(72,2,.15))
    t=4.2                                                         # pantalla final: loop de 4 acordes
    prog=[(FMAJ7,41),(EM7,40),(DM7,38),(CMAJ9,36)]; k=0
    m.add(4.2,campana(81,2.4,.25))
    while t<dur-2:
        ac,b=prog[k%4]; m.acorde(t,ac,4*B+.6,.2); m.add(t,bajo(b,4*B)); k+=1; t+=4*B
    m.bateria(4.2,dur-3.5)
    m.acorde(dur-2.6,FMAJ7,2.6,.16)
    return m.final(dur,.3,3.0)
def wav(path,x):
    st=np.stack([x,np.roll(x,int(.011*SR))*.97],1)               # estéreo leve
    with wave.open(path,'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes())
def mux(video,audio,out):
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',video,'-i',audio,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-shortest','-movflags','+faststart',out],check=True)
if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else '.'
    wav(f'{out}/musica-opening.wav',opening()); wav(f'{out}/musica-closing.wav',closing())

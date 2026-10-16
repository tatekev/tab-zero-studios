from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import math
S=1024;C=(512,512);R=450;W=38
CY=(95,200,255);MG=(224,90,210)
def lerp(a,b,t):return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def plate():
    im=Image.new('RGB',(S,S),(8,8,22));d=ImageDraw.Draw(im)
    for r in range(720,0,-6):
        t=r/720;d.ellipse([512-r,512-r,512+r,512+r],fill=lerp((22,10,40),(8,8,22),t**0.8))
    return im
def grad():
    g=Image.new('RGB',(S,S));px=g.load()
    for y in range(S):
        for x in range(S):
            t=((x-S*0.15)*0.6+(y-S*0.1)*0.8)/(S*1.0); t=min(1,max(0,(t-0.1)/0.9)); px[x,y]=lerp(CY,MG,t)
    return g
G=grad()
def mask_ring(gap=None):
    m=Image.new('L',(S,S),0);d=ImageDraw.Draw(m)
    d.ellipse([C[0]-R-W//2,C[1]-R-W//2,C[0]+R+W//2,C[1]+R+W//2],fill=255)
    d.ellipse([C[0]-R+W//2,C[1]-R+W//2,C[0]+R-W//2,C[1]+R-W//2],fill=0)
    return m
def line_mask(p1,p2,w):
    m=Image.new('L',(S*2,S*2),0);d=ImageDraw.Draw(m)
    d.line([(x*2,y*2) for x,y in (p1,p2)],fill=255,width=w*2)
    for p in (p1,p2):
        d.ellipse([p[0]*2-w,p[1]*2-w,p[0]*2+w,p[1]*2+w],fill=255)
    return m.resize((S,S),Image.LANCZOS)
def glow(base,mask,col_img,blur=22,k=0.9):
    gl=Image.composite(col_img,Image.new('RGB',(S,S),(0,0,0)),mask).filter(ImageFilter.GaussianBlur(blur))
    return ImageChops.add(base,gl.point(lambda v:int(v*k)))
def paint(base,mask,col_img):return Image.composite(col_img,base,mask)
def text(base,clear=False):
    f=ImageFont.truetype('/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf',300)
    try:f.set_variation_by_axes([32,900])
    except Exception as e:
        try:f.set_variation_by_name('Black')
        except:pass
    m=Image.new('L',(S,S),0);ImageDraw.Draw(m).text((512,520),'TZS',font=f,fill=255,anchor='mm')
    m=m.filter(ImageFilter.GaussianBlur(0.6))
    base=glow(base,m,Image.new('RGB',(S,S),(150,110,255)),26,0.8)
    return paint(base,m,Image.new('RGB',(S,S),(228,248,255))),m
def solid(c):return Image.new('RGB',(S,S),c)
def save(im,n):
    im.save(n);im.resize((64,64),Image.LANCZOS).save('/tmp/'+n.replace('.png','_64.png'))
import sys
# slash geometry: bottom-left to top-right (classic Ø is top-right to bottom-left)
a=math.radians(35)  # slash angle from horizontal
def slash_pts(L):
    dx,dy=math.cos(a)*L,math.sin(a)*L
    return (C[0]-dx,C[1]+dy),(C[0]+dx,C[1]-dy)
def textfirst(base,slash_m,slash_col,textm=None):pass

# A: slash behind TZS
base=plate()
rm=mask_ring()
base=glow(base,rm,G,24,0.9);base=paint(base,rm,G)
p1,p2=slash_pts(R+W*1.3)
sm=line_mask(p1,p2,28)
sl=Image.new('RGB',(S,S),(255,120,225))
base=glow(base,sm,sl,20,1.0);base=paint(base,sm,Image.blend(sl,solid((255,210,245)),0.35))
base,_=text(base);save(base,'option-B2-a.png')

# B: slash cuts ring (gap), glow along slash
base=plate()
p1,p2=slash_pts(R+W*1.8)
cut=line_mask(p1,p2,70)
rm=ImageChops.multiply(mask_ring(),ImageChops.invert(cut))
base=glow(base,rm,G,24,0.9);base=paint(base,rm,G)
sm=line_mask(p1,p2,22)
# slash only extends through ring zone: full line, but trim middle so center stays clear
mid=Image.new('L',(S*2,S*2),0)
inner=line_mask(slash_pts(R-W*2.2)[0],slash_pts(R-W*2.2)[1],200)  # keeps full length inside; mask trimmed below
sl2=Image.new('L',(S,S),0);d=ImageDraw.Draw(sl2);d.ellipse([C[0]-R+W*4.2,C[1]-R+W*4.2,C[0]+R-W*4.2,C[1]+R-W*4.2],fill=255)
sm=ImageChops.multiply(sm,ImageChops.invert(sl2.filter(ImageFilter.GaussianBlur(1))))  # only outside inner area -> ends near ring
sc=Image.new('RGB',(S,S),(255,140,230))
base=glow(base,sm,sc,20,1.0);base=paint(base,sm,solid((255,225,248)))
base,_=text(base);save(base,'option-B2-b.png')

# C: short bold magenta stroke at lower-right overlapping ring, TZS clear
base=plate()
rm=mask_ring()
base=glow(base,rm,G,24,0.9);base=paint(base,rm,G)
ang=math.radians(45) # lower-right position on ring
cx=C[0]+R*math.cos(ang);cy=C[1]+R*math.sin(ang)
# stroke direction: perpendicular-ish slash (top-right to bottom-left)
d=math.radians(-55);L=175
q1=(cx-math.cos(d)*L,cy-math.sin(d)*L);q2=(cx+math.cos(d)*L,cy+math.sin(d)*L)
sm=line_mask(q1,q2,46)
mg=solid((255,60,200))
base=glow(base,sm,mg,26,1.1);base=paint(base,sm,mg)
hi=line_mask(q1,q2,16);base=paint(base,hi,solid((255,170,240)))
base,_=text(base);save(base,'option-B2-c.png')

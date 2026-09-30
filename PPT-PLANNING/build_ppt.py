# -*- coding: utf-8 -*-
"""Build PRAMAAN SIH2026 Idea PPT v5 — 7 slides, diagram-heavy, no emojis."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

BASE = r'C:\Users\aarja\Desktop\SIH26\PPT-PLANNING\assets'
LOGO = os.path.join(BASE, 'img_1_89631.png')
BRAIN= os.path.join(BASE, 'brain.png')
LOGODIR = os.path.join(BASE, 'logos')
def _lg(name): return os.path.join(LOGODIR, name+'.png')
STACK_LOGOS = ['react','typescript','vite','tailwind','flask','python','postgresql','redis','docker','nginx']

def C(h): return RGBColor.from_string(h)
NAVY=C('1F3A6B'); BLUE=C('1C6FC9'); STRIP=C('DCE9F8'); ACCENT=C('2563EB')
GREEN=C('15803D'); GREENBG=C('E4F4E9'); RED=C('B91C1C'); REDBG=C('FBE8E7')
ORANGE=C('C2410C'); ORANGEBG=C('FBEADD'); DBLUE=C('1E3A8A'); DBLUEBG=C('E8EFFB')
GREY=C('5A5E70'); TEXT=C('16213A'); WHITE=C('FFFFFF'); LIGHT=C('F1F4F9'); BORDER=C('C8D0DD')
PURPLE=C('6D28D9')
TF='Cambria'; BF='Calibri'
SW, SH = 13.333, 7.5

prs = Presentation(); prs.slide_width=Inches(SW); prs.slide_height=Inches(SH)
BLANK = prs.slide_layouts[6]

def _runs(p, runs):
    for r in runs:
        t=p.add_run(); t.text=r[0]; t.font.size=Pt(r[1]); t.font.bold=r[2]
        t.font.color.rgb=r[3]; t.font.italic=(r[4] if len(r)>4 else False)
        t.font.name=(r[5] if len(r)>5 else BF)

def fill(tf, paras, anchor=MSO_ANCHOR.TOP, wrap=True, m=0.06):
    tf.word_wrap=wrap; tf.auto_size=MSO_AUTO_SIZE.NONE; tf.vertical_anchor=anchor
    tf.margin_left=Inches(m); tf.margin_right=Inches(m)
    tf.margin_top=Inches(0.02); tf.margin_bottom=Inches(0.02)
    first=True
    for pa in paras:
        p=tf.paragraphs[0] if first else tf.add_paragraph(); first=False
        p.alignment=pa.get('align',PP_ALIGN.LEFT)
        p.space_after=Pt(pa.get('space_after',2)); p.space_before=Pt(pa.get('space_before',0))
        if 'line' in pa: p.line_spacing=pa['line']
        _runs(p, pa['runs'])

def rrect(s,x,y,w,h,fillc=None,line=None,lw=1.0,rad=0.06):
    sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    try: sh.adjustments[0]=rad
    except: pass
    if fillc is None: sh.fill.background()
    else: sh.fill.solid(); sh.fill.fore_color.rgb=fillc
    if line is None: sh.line.fill.background()
    else: sh.line.color.rgb=line; sh.line.width=Pt(lw)
    sh.shadow.inherit=False; return sh

def rect(s,x,y,w,h,fillc=None,line=None,lw=1.0):
    sh=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    if fillc is None: sh.fill.background()
    else: sh.fill.solid(); sh.fill.fore_color.rgb=fillc
    if line is None: sh.line.fill.background()
    else: sh.line.color.rgb=line; sh.line.width=Pt(lw)
    sh.shadow.inherit=False; return sh

def shp(s,kind,x,y,w,h,fillc,line=None,lw=1.0):
    sh=s.shapes.add_shape(kind,Inches(x),Inches(y),Inches(w),Inches(h))
    sh.fill.solid(); sh.fill.fore_color.rgb=fillc
    if line is None: sh.line.fill.background()
    else: sh.line.color.rgb=line; sh.line.width=Pt(lw)
    sh.shadow.inherit=False; return sh

def tbox(s,x,y,w,h,paras,anchor=MSO_ANCHOR.TOP,m=0.06):
    b=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    fill(b.text_frame,paras,anchor=anchor,m=m); return b

def blt(term,desc,acc=NAVY,size=9.5,tc=TEXT,dc=GREY,sa=3):
    return {'runs':[('▪  ',size,True,acc),(term,size,True,tc),('  '+desc,size,False,dc)],'space_after':sa,'line':1.04}

def bull(term,desc,acc,size=10.5,sa=9):
    return {'runs':[('•  ',size,True,acc),(term+':  ',size,True,TEXT),(desc,size,False,TEXT)],'space_after':sa,'line':1.08}

def node(s,x,y,w,h,title,sub,fc,lc,tc=None,tsize=10,ssize=7.5,rad=0.10):
    tc=tc or lc; n=rrect(s,x,y,w,h,fillc=fc,line=lc,lw=1.25,rad=rad)
    ps=[{'runs':[(title,tsize,True,tc)],'align':PP_ALIGN.CENTER,'space_after':1,'line':1.0}]
    if sub: ps.append({'runs':[(sub,ssize,False,GREY)],'align':PP_ALIGN.CENTER,'line':1.0})
    fill(n.text_frame,ps,anchor=MSO_ANCHOR.MIDDLE,m=0.04); return n

def hcard(s,x,y,w,h,title,hc,body,bf=WHITE,htc=WHITE,hsize=11):
    rect(s,x,y,w,h,fillc=bf,line=BORDER,lw=1.0)
    hb=rect(s,x,y,w,0.36,fillc=hc)
    fill(hb.text_frame,[{'runs':[(title,hsize,True,htc)],'align':PP_ALIGN.CENTER}],anchor=MSO_ANCHOR.MIDDLE)
    tb=s.shapes.add_textbox(Inches(x+0.04),Inches(y+0.42),Inches(w-0.08),Inches(h-0.48))
    fill(tb.text_frame,body); return tb

def arrow(s,x,y,w,h,color=NAVY,kind=MSO_SHAPE.RIGHT_ARROW):
    return shp(s,kind,x,y,w,h,color)

def headrule(s,x,y,w,text,color):
    tbox(s,x,y,w,0.34,[{'runs':[(text,16,True,color,False,TF)],'align':PP_ALIGN.LEFT}],anchor=MSO_ANCHOR.MIDDLE)
    rect(s,x,y+0.38,w,0.035,fillc=color)

def numstep(s,x,y,w,num,title,desc):
    d=0.32
    o=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(x),Inches(y),Inches(d),Inches(d))
    o.fill.solid(); o.fill.fore_color.rgb=NAVY; o.line.fill.background(); o.shadow.inherit=False
    fill(o.text_frame,[{'runs':[(str(num),12,True,WHITE)],'align':PP_ALIGN.CENTER}],anchor=MSO_ANCHOR.MIDDLE)
    tbox(s,x+d+0.14,y-0.05,w-d-0.14,0.62,[
        {'runs':[(title,10,True,TEXT)],'space_after':1,'line':1.0},
        {'runs':[(desc,8.6,False,GREY)],'line':1.04}])

def chrome(s,title,sub):
    bd=s.shapes.add_shape(MSO_SHAPE.OVAL,Inches(0.34),Inches(0.30),Inches(1.18),Inches(0.6))
    bd.fill.background(); bd.line.color.rgb=PURPLE; bd.line.width=Pt(1.25); bd.shadow.inherit=False
    fill(bd.text_frame,[{'runs':[('leet',13,True,NAVY,True)],'align':PP_ALIGN.CENTER}],anchor=MSO_ANCHOR.MIDDLE)
    tbox(s,1.7,0.18,8.4,0.78,[{'runs':[(title,28,True,NAVY,False,TF)],'align':PP_ALIGN.CENTER}],anchor=MSO_ANCHOR.MIDDLE)
    s.shapes.add_picture(LOGO,Inches(10.95),Inches(0.30),height=Inches(0.60))
    st=rrect(s,0.34,1.02,12.65,0.32,fillc=STRIP,rad=0.5)
    fill(st.text_frame,[{'runs':[(sub,10,True,NAVY)],'align':PP_ALIGN.CENTER}],anchor=MSO_ANCHOR.MIDDLE)

def footer(s,n):
    fb=rect(s,0,7.12,SW,0.38,fillc=BLUE); tf=fb.text_frame; tf.margin_right=Inches(0.28)
    fill(tf,[{'runs':[(str(n),11,True,WHITE)],'align':PP_ALIGN.RIGHT}],anchor=MSO_ANCHOR.MIDDLE)
    tbox(s,0.3,7.16,9,0.3,[{'runs':[('PRAMAAN — Secure Evidence Vault  ·  Team leet  ·  SIH26190',9,True,WHITE)],'align':PP_ALIGN.LEFT}],anchor=MSO_ANCHOR.MIDDLE)

def logo_row(s, names, y, h, x0, x1, gap=0.30):
    dims=[]
    for n in names:
        f=_lg(n); w,ht=Image.open(f).size; dims.append((f, h*w/ht))
    total=sum(d[1] for d in dims)+gap*(len(dims)-1)
    x=x0+((x1-x0)-total)/2
    for f,w in dims:
        s.shapes.add_picture(f,Inches(x),Inches(y),height=Inches(h)); x+=w+gap

def add(): return prs.slides.add_slide(BLANK)

# ============================== SLIDE 1 — TITLE ==============================
s=add()
tbox(s,0.6,0.42,9.7,0.85,[{'runs':[('SMART INDIA HACKATHON 2026',31,True,NAVY,False,TF)],'align':PP_ALIGN.LEFT}],anchor=MSO_ANCHOR.MIDDLE)
s.shapes.add_picture(LOGO,Inches(10.85),Inches(0.42),height=Inches(0.82))
s.shapes.add_picture(BRAIN,Inches(9.35),Inches(1.95),height=Inches(4.25))
tbox(s,0.6,1.42,7.7,0.95,[
    {'runs':[('PRAMAAN',42,True,NAVY,False,TF)],'align':PP_ALIGN.LEFT,'space_after':0},
    {'runs':[('Secure Evidence Vault',17,True,BLUE)],'align':PP_ALIGN.LEFT},
])
def kv(label,val):
    return {'runs':[(label+'  ',12,True,NAVY),(val,12,False,TEXT)],'space_after':6.5,'line':1.05}
tbox(s,0.62,2.72,7.9,3.1,[
    kv('Problem Statement ID —','SIH26190'),
    kv('Problem Statement Title —','Secure Digital Document Management'),
    {'runs':[('System for law enforcement agencies, courts and investigative departments',12,False,TEXT)],'space_after':6.5},
    kv('Theme —','Cybersecurity and Blockchain'),
    kv('PS Category —','Software'),
    kv('Team ID —','SIH-UPES-2026-T250'),
    kv('Team Name (Registered on portal) —','leet'),
])
og=rrect(s,0.62,6.05,7.7,0.42,fillc=STRIP,rad=0.2)
fill(og.text_frame,[{'runs':[('Organisation:  ',10.5,True,NAVY),('Ministry of Home Affairs  ·  National Crime Records Bureau (NCRB)',10.5,False,TEXT)],'align':PP_ALIGN.CENTER}],anchor=MSO_ANCHOR.MIDDLE)
tg=rrect(s,0.62,6.55,7.7,0.6,fillc=NAVY,rad=0.15)
fill(tg.text_frame,[
    {'runs':[('Separate the trust.   Verify before release.   Record every access.',12,True,WHITE)],'align':PP_ALIGN.CENTER,'space_after':0},
    {'runs':[('Standalone, fully on-premise  ·  no dependency on any external system',8,False,C('C9D6EE'))],'align':PP_ALIGN.CENTER},
],anchor=MSO_ANCHOR.MIDDLE)

# ==================== SLIDE 2 — IDEA / SOLUTION (flow diagram + text) ====================
s=add()
chrome(s,'IDEA  /  SOLUTION','Proposed Solution (Idea / Prototype)   |   How it addresses the problem   |   Innovation and uniqueness')
tbox(s,0.34,1.42,12.65,0.28,[{'runs':[('THE EVIDENCE LIFECYCLE — how a document moves through PRAMAAN, end to end',11,True,NAVY)],'align':PP_ALIGN.LEFT}])
flow=[('1 · Sign in','MFA enforced (TOTP)',DBLUEBG,DBLUE),('2 · Case dashboard','case-scoped · RBAC',DBLUEBG,DBLUE),
      ('3 · Upload','encrypt · chunk · OCR',ORANGEBG,ORANGE),('4 · Step-up MFA','fresh TOTP to share',DBLUEBG,DBLUE),
      ('5 · Recipient OTP','bound · time-limited',DBLUEBG,DBLUE),('6 · Audit-logged','every action, chained',GREENBG,GREEN)]
nw=1.90; ngap=0.13; nx=(SW-(6*nw+5*ngap))/2; ny=1.76; nh=0.92
for i,(t,sub,fc,lc) in enumerate(flow):
    node(s,nx,ny,nw,nh,t,sub,fc,lc,tsize=10,ssize=8)
    if i<5: arrow(s,nx+nw+0.005,ny+nh/2-0.09,ngap-0.02,0.18,NAVY)
    nx+=nw+ngap
cy=2.90; ch3=3.12; cwd=4.06
hcard(s,0.42,cy,cwd,ch3,'PROPOSED SOLUTION',NAVY,[
    blt('Encrypted evidence vault.','Replaces the station paper register + shared drive with one indexed, access-controlled case file.',NAVY),
    blt('Chunked at rest.','Every exhibit is split into 1 MB chunks, each encrypted under its own key — no file ever sits whole on disk.',NAVY),
    blt('Split-trust storage.','Metadata, ciphertext and keys live on three separate domains; no single machine can rebuild a document.',NAVY),
    blt('Verify-before-release.','Integrity is re-checked on every download; a tampered exhibit yields 0 bytes.',NAVY),
    blt('Offline OCR + search.','Tesseract indexes scans in six Indian languages — findable without leaving the network.',NAVY),
])
hcard(s,0.42+cwd+0.14,cy,cwd,ch3,'HOW IT ADDRESSES THE PROBLEM',ORANGE,[
    blt('Proves integrity.','SHA-256 per chunk + one document hash + GCM auth tags detect any alteration before serving.',ORANGE),
    blt('Least-privilege access.','Six roles, re-checked per request; case-scoped resources return 404, never confirming existence.',ORANGE),
    blt('Controlled sharing.','Court/prosecutor exhibits go out only via step-up-verified, recipient-bound, expiring links.',ORANGE),
    blt('Tamper-evident trail.','A hash-chained audit log records actor · action · case · document · result for every event.',ORANGE),
    blt('No plaintext leak surface.','Browser holds no keys; app server stores no bytes; DBA sees only metadata.',ORANGE),
])
hcard(s,0.42+2*(cwd+0.14),cy,3.68,ch3,'INNOVATION & UNIQUENESS',GREEN,[
    blt('Per-chunk derived keys.','HKDF + fresh 96-bit IV per chunk — one key never covers two chunks.',GREEN),
    blt('Split-trust + mirrors.','Opaque keys on B, hashes on A, keys in KMS; A & B mirrored for HA.',GREEN),
    blt('Integrity gate.','All checks pass → stream; any fail → 422, 0 bytes, logged.',GREEN),
    blt('Version control.','Re-uploads create immutable versions; prior versions retained & verifiable.',GREEN),
    blt('Running prototype.','Real, built and demoable today — not slideware.',GREEN),
])
tk=rrect(s,0.42,6.18,12.5,0.56,fillc=NAVY,rad=0.12)
fill(tk.text_frame,[{'runs':[('Every evidence action is authenticated, integrity-verified and audit-logged.',13.5,True,WHITE)],'align':PP_ALIGN.CENTER}],anchor=MSO_ANCHOR.MIDDLE)
footer(s,2)

# ==================== SLIDE 3 — TECHNICAL APPROACH · ARCHITECTURE ====================
s=add()
chrome(s,'TECHNICAL APPROACH','Architecture & trust boundaries   |   Technologies used   (1 of 2)')
# ---- LEFT: split-trust topology diagram ----
LX=0.42; LW=6.6; cxc=LX+LW/2
tbox(s,LX,1.42,LW,0.26,[{'runs':[('SPLIT-TRUST ARCHITECTURE — no single domain can reconstruct a document',10,True,NAVY)],'align':PP_ALIGN.CENTER}])
node(s,cxc-1.35,1.76,2.7,0.55,'OFFICER — Browser (React SPA)','holds no keys · no plaintext',WHITE,NAVY,tsize=9.5,ssize=7.5)
tbox(s,cxc+0.16,2.30,0.7,0.2,[{'runs':[('HTTPS',7,True,GREEN)],'align':PP_ALIGN.LEFT}])
arrow(s,cxc-0.13,2.33,0.26,0.20,NAVY,kind=MSO_SHAPE.DOWN_ARROW)
appsrv=rrect(s,LX+0.05,2.60,LW-0.10,0.66,fillc=DBLUEBG,line=DBLUE,lw=1.4,rad=0.06)
fill(appsrv.text_frame,[
    {'runs':[('APPLICATION SERVER — Flask 3 / Python 3.12',9.5,True,DBLUE)],'align':PP_ALIGN.CENTER,'space_after':1},
    {'runs':[('Auth (JWT + TOTP MFA) · RBAC · Services · Crypto',8,False,TEXT)],'align':PP_ALIGN.CENTER,'line':1.0},
],anchor=MSO_ANCHOR.MIDDLE)
sw=2.10; sgap=0.12; sx0=LX+0.06; sy=3.82; shh=1.18
centers=[sx0+sw/2, sx0+sw+sgap+sw/2, sx0+2*(sw+sgap)+sw/2]
for cx in centers:
    arrow(s,cx-0.11,3.36,0.24,0.16,NAVY,kind=MSO_SHAPE.DOWN_ARROW)
def store(x,title,fc,lc,sub,guard):
    b=rrect(s,x,sy,sw,shh,fillc=fc,line=lc,lw=1.3,rad=0.06)
    fill(b.text_frame,[
        {'runs':[(title,9,True,lc)],'align':PP_ALIGN.CENTER,'space_after':2,'line':1.0},
        {'runs':[(sub,7.5,False,TEXT)],'align':PP_ALIGN.CENTER,'space_after':2,'line':1.0},
        {'runs':[(guard,7.5,True,RED)],'align':PP_ALIGN.CENTER,'line':1.0}],anchor=MSO_ANCHOR.MIDDLE)
store(sx0,'SERVER A · METADATA',DBLUEBG,DBLUE,'PostgreSQL · hashes ·\naudit chain · mirrored','no document bytes')
store(sx0+sw+sgap,'SERVER B · EVIDENCE',ORANGEBG,ORANGE,'ciphertext only ·\nopaque keys · mirrored','no keys · no plaintext')
store(sx0+2*(sw+sgap),'KMS · KEYS',GREENBG,GREEN,'wrapped master key ·\nderived per chunk','no ciphertext to unlock')
tbox(s,LX,5.10,LW,0.5,[{'runs':[('Breach any ONE domain → nothing readable. Reconstructing a document needs Server A + Server B + KMS, together.',9,True,NAVY)],'align':PP_ALIGN.CENTER,'line':1.05}])
# ---- RIGHT: architecture + components text ----
RX=7.25; RW=5.66
hcard(s,RX,1.72,RW,2.28,'ARCHITECTURE',NAVY,[
    blt('Split trust.','Metadata (A), ciphertext (B) and keys (KMS) on three separate domains.',NAVY,9.3),
    blt('Chunked crypto.','Each 1 MB chunk gets an HKDF key + fresh 96-bit IV under AES-256-GCM.',NAVY,9.3),
    blt('Integrity gate.','SHA-256 per chunk + one document hash + GCM tags, verified before any byte is served.',NAVY,9.3),
    blt('Least privilege.','RBAC re-checked per request; step-up MFA on sensitive actions.',NAVY,9.3),
    blt('Resilience.','Server A & B mirrored (hot-standby); append-only version history.',NAVY,9.3),
])
hcard(s,RX,4.14,RW,1.92,'COMPONENTS',ORANGE,[
    blt('Application Server','— Flask 3 / Python 3.12: auth, RBAC, services, crypto.',ORANGE,9.3),
    blt('Server A — PostgreSQL 16','metadata, chunk order, hashes, search index, audit chain.',ORANGE,9.3),
    blt('Server B — chunk store','AES-GCM ciphertext objects with opaque filenames.',ORANGE,9.3),
    blt('KMS — key material','one wrapped master key per document; chunk keys derived on use.',ORANGE,9.3),
    blt('OCR — Tesseract','offline, six Indian languages.',ORANGE,9.3),
])
# logo wall + written stack
logo_row(s, STACK_LOGOS, 6.18, 0.42, 0.42, 12.92, gap=0.34)
tss=rect(s,0.42,6.70,12.5,0.36,fillc=LIGHT,line=BORDER,lw=0.75)
fill(tss.text_frame,[{'runs':[('TECHNOLOGY STACK   ',8.5,True,NAVY),('React 18 · Vite · TS · Tailwind  |  Flask 3 · Python 3.12 · SQLAlchemy · JWT · marshmallow  |  PostgreSQL 16  |  AES-256-GCM · HKDF-SHA256 · SHA-256 · Ed25519 · bcrypt · TOTP (pyca/cryptography)  |  Tesseract OCR ×6 langs  |  production: MinIO · Vault · Redis · Celery · Nginx (TLS)',8,False,TEXT)],'align':PP_ALIGN.CENTER}],anchor=MSO_ANCHOR.MIDDLE)
footer(s,3)

# ============ SLIDE 4 — TECHNICAL APPROACH · CHUNKED ENCRYPTION & INTEGRITY ============
s=add()
chrome(s,'TECHNICAL APPROACH','Methodology — chunked encryption · integrity verification · tamper-evident audit   (2 of 2)')
# ---- (1) CHUNKING PIPELINE ----
tbox(s,0.42,1.40,12.5,0.26,[{'runs':[('1.  CHUNKED ENCRYPTION — every exhibit is split and locked chunk by chunk',10.5,True,ORANGE)],'align':PP_ALIGN.LEFT}])
node(s,0.42,1.78,1.75,0.92,'THE EXHIBIT','up to 500 MB',WHITE,NAVY,tsize=9.5,ssize=7.5)
arrow(s,2.22,2.09,0.30,0.30,NAVY)
# chunks box with 4 squares
cb=rrect(s,2.58,1.78,2.55,0.92,fillc=LIGHT,line=NAVY,lw=1.2,rad=0.06)
tbox(s,2.58,1.82,2.55,0.24,[{'runs':[('SPLIT INTO 1 MB CHUNKS',8.5,True,NAVY)],'align':PP_ALIGN.CENTER}])
for i in range(4):
    sq=rrect(s,2.78+i*0.58,2.18,0.46,0.40,fillc=DBLUEBG,line=DBLUE,lw=1.0,rad=0.12)
    fill(sq.text_frame,[{'runs':[('c'+str(i),7.5,True,DBLUE)],'align':PP_ALIGN.CENTER}],anchor=MSO_ANCHOR.MIDDLE)
arrow(s,5.18,2.09,0.30,0.30,NAVY)
pc=rrect(s,5.54,1.78,3.55,0.92,fillc=ORANGEBG,line=ORANGE,lw=1.3,rad=0.06)
fill(pc.text_frame,[
    {'runs':[('PER-CHUNK KEY → AES-256-GCM',9,True,ORANGE)],'align':PP_ALIGN.CENTER,'space_after':2,'line':1.0},
    {'runs':[('chunk_key = HKDF(master_key, doc_id, i)',7.8,False,TEXT)],'align':PP_ALIGN.CENTER,'line':1.0},
    {'runs':[('fresh 96-bit IV · chunk_hash = SHA-256(ciphertext)',7.8,False,TEXT)],'align':PP_ALIGN.CENTER,'line':1.0},
],anchor=MSO_ANCHOR.MIDDLE)
arrow(s,9.14,2.09,0.30,0.30,NAVY)
outs=[('→ Server B','ciphertext object (opaque key)',ORANGE,ORANGEBG),
      ('→ Server A','chunk index · IV · chunk_hash',DBLUE,DBLUEBG),
      ('→ KMS','wrapped master key',GREEN,GREENBG)]
oy=1.78
for t,d,lc,fc in outs:
    ob=rrect(s,9.50,oy,3.42,0.28,fillc=fc,line=lc,lw=1.0,rad=0.2)
    fill(ob.text_frame,[{'runs':[(t+'  ',8,True,lc),(d,7.5,False,TEXT)],'align':PP_ALIGN.LEFT}],anchor=MSO_ANCHOR.MIDDLE)
    oy+=0.32
tbox(s,0.42,2.78,9.0,0.24,[{'runs':[('document_hash = SHA-256( chunk₀_hash ‖ chunk₁_hash ‖ … ‖ chunkₙ_hash )  — one fingerprint for the whole exhibit',8.5,True,NAVY)],'align':PP_ALIGN.LEFT}])
# ---- (2) INTEGRITY GATE ----
rect(s,0.42,3.18,12.5,0.015,fillc=BORDER)
tbox(s,0.42,3.24,12.5,0.26,[{'runs':[('2.  VERIFY BEFORE RELEASE — nothing is streamed until every check passes',10.5,True,GREEN)],'align':PP_ALIGN.LEFT}])
gy=3.66
node(s,0.42,gy,1.75,0.62,'Download','request',LIGHT,NAVY,tsize=9,ssize=7.5)
arrow(s,2.22,gy+0.20,0.26,0.20,NAVY)
node(s,2.54,gy,2.15,0.62,'Fetch key','+ all chunks (ordered)',LIGHT,NAVY,tsize=9,ssize=7.5)
arrow(s,4.74,gy+0.20,0.26,0.20,NAVY)
node(s,5.06,gy,2.75,0.62,'VERIFY ALL','SHA-256 == chunk_hash · GCM tag · document_hash',LIGHT,NAVY,tsize=9,ssize=6.8)
arrow(s,7.86,gy+0.20,0.26,0.20,NAVY)
dia=shp(s,MSO_SHAPE.DIAMOND,8.18,gy-0.06,1.25,0.74,C('FFF6E5'),line=ORANGE,lw=1.3)
fill(dia.text_frame,[{'runs':[('All pass?',8.5,True,ORANGE)],'align':PP_ALIGN.CENTER}],anchor=MSO_ANCHOR.MIDDLE)
rel=rrect(s,9.62,gy-0.20,3.30,0.42,fillc=GREENBG,line=GREEN,lw=1.2,rad=0.1)
fill(rel.text_frame,[{'runs':[('RELEASE  ',9,True,GREEN),('decrypt · stream in order · log DOWNLOADED',7.5,False,TEXT)],'align':PP_ALIGN.LEFT}],anchor=MSO_ANCHOR.MIDDLE)
blk=rrect(s,9.62,gy+0.28,3.30,0.44,fillc=REDBG,line=RED,lw=1.2,rad=0.1)
fill(blk.text_frame,[{'runs':[('BLOCK  ',9,True,RED),('HTTP 422 · 0 bytes · log INTEGRITY_VIOLATION',7.5,False,TEXT)],'align':PP_ALIGN.LEFT}],anchor=MSO_ANCHOR.MIDDLE)
arrow(s,9.44,gy-0.02,0.16,0.14,GREEN); arrow(s,9.44,gy+0.44,0.16,0.14,RED)
# ---- (3) AUDIT HASH CHAIN ----
rect(s,0.42,4.62,12.5,0.015,fillc=BORDER)
tbox(s,0.42,4.68,12.5,0.26,[{'runs':[('3.  TAMPER-EVIDENT AUDIT — every action hash-chained to the previous one',10.5,True,DBLUE)],'align':PP_ALIGN.LEFT}])
ev=[('Event 1 · Genesis','prev = 000…0'),('Event 2','prev = hash₁'),('Event 3','prev = hash₂'),('… Event n','prev = hashₙ₋₁')]
ex=0.42; ew=2.55; egap=0.30; eyy=5.06
for i,(t,d) in enumerate(ev):
    eb=rrect(s,ex,eyy,ew,0.82,fillc=DBLUEBG,line=DBLUE,lw=1.2,rad=0.06)
    fill(eb.text_frame,[
        {'runs':[(t,9,True,DBLUE)],'align':PP_ALIGN.CENTER,'space_after':2,'line':1.0},
        {'runs':[(d,7.5,False,GREY)],'align':PP_ALIGN.CENTER,'space_after':2,'line':1.0},
        {'runs':[('this_hash = SHA-256(prev ‖ payload)',7,False,TEXT)],'align':PP_ALIGN.CENTER,'line':1.0},
    ],anchor=MSO_ANCHOR.MIDDLE)
    if i<3: arrow(s,ex+ew+0.02,eyy+0.31,egap-0.04,0.20,NAVY)
    ex+=ew+egap
vb=rrect(s,ex,eyy,12.92-ex,0.82,fillc=GREENBG,line=GREEN,lw=1.2,rad=0.06)
fill(vb.text_frame,[
    {'runs':[('/audit/verify',9,True,GREEN)],'align':PP_ALIGN.CENTER,'space_after':2,'line':1.0},
    {'runs':[('recomputes the chain →',7.5,False,GREY)],'align':PP_ALIGN.CENTER,'space_after':1,'line':1.0},
    {'runs':[('names first_break_at',7.5,True,GREEN)],'align':PP_ALIGN.CENTER,'line':1.0},
],anchor=MSO_ANCHOR.MIDDLE)
tbox(s,0.42,5.96,12.5,0.24,[{'runs':[('Modify, delete or insert any record → every later hash breaks; verification names the first broken event. (tamper-evident, not immutable)',8.5,True,NAVY,True)],'align':PP_ALIGN.CENTER}])
vcm=rect(s,0.42,6.30,12.5,0.72,fillc=LIGHT,line=BORDER,lw=0.75)
fill(vcm.text_frame,[
    {'runs':[('VERSION CONTROL   ',9,True,DBLUE),('re-uploads create new immutable versions — prior versions retained & independently verifiable.',8.5,False,TEXT)],'align':PP_ALIGN.CENTER,'space_after':3,'line':1.0},
    {'runs':[('MIRROR SERVERS   ',9,True,ORANGE),('Server A & Server B replicate to hot-standby mirrors for redundancy & availability.',8.5,False,TEXT)],'align':PP_ALIGN.CENTER,'line':1.0},
],anchor=MSO_ANCHOR.MIDDLE)
footer(s,4)

# ==================== SLIDE 5 — FEASIBILITY & VIABILITY ====================
s=add()
chrome(s,'FEASIBILITY AND VIABILITY','Feasibility of the idea   |   Potential challenges & risks   |   Strategies for overcoming these challenges')
tbox(s,0.34,1.42,12.65,0.28,[{'runs':[('FEASIBILITY — technical, operational & financial, proven in a working prototype',11,True,NAVY)],'align':PP_ALIGN.LEFT}])
fy=1.74; fh=2.02
hcard(s,0.42,fy,4.06,fh,'TECHNICAL',NAVY,[
    blt('Open-source stack.','React · Flask · PostgreSQL · Tesseract on commodity hardware.',NAVY,9.5,sa=7),
    blt('Audited crypto only.','pyca/cryptography — nothing hand-rolled.',NAVY,9.5,sa=7),
    blt('Working prototype.','Every screen is live and demoable today.',NAVY,9.5,sa=7),
    blt('Tested paths.','Crypto & auth flows covered by tests.',NAVY,9.5,sa=7),
])
hcard(s,4.62,fy,4.06,fh,'OPERATIONAL',ORANGE,[
    blt('Standalone / on-prem.','No external dependency to deploy.',ORANGE,9.5,sa=7),
    blt('Role-based day one.','Six roles, one console, every change logged.',ORANGE,9.5,sa=7),
    blt('Clear prod path.','Vault, MinIO, Redis are drop-in swaps.',ORANGE,9.5,sa=7),
    blt('Low footprint.','One backend, one frontend, Postgres.',ORANGE,9.5,sa=7),
])
hcard(s,8.82,fy,3.68,fh,'FINANCIAL',GREEN,[
    blt('Zero licensing.','Every component open source.',GREEN,9.5,sa=7),
    blt('No mandatory cloud.','On-premise by default.',GREEN,9.5,sa=7),
    blt('No crypto-audit cost.','Audited libraries used.',GREEN,9.5,sa=7),
    blt('Commodity hardware.','No specialised budget required.',GREEN,9.5,sa=7),
])
band=rect(s,0.42,3.86,12.1,0.32,fillc=NAVY)
fill(band.text_frame,[{'runs':[('SECURITY POSTURE   ·   CHALLENGES → STRATEGY   ·   ROADMAP TO DEPLOYMENT',10.5,True,WHITE)],'align':PP_ALIGN.CENTER}],anchor=MSO_ANCHOR.MIDDLE)
ty=4.24; th=2.42
def li(t,acc,size=8.7): return {'runs':[('•  ',size,True,acc),(t,size,False,TEXT)],'space_after':3.5,'line':1.02}
def rs(risk,strat,acc,size=8.7): return {'runs':[('•  ',size,True,acc),(risk+' → ',size,True,TEXT),(strat,size,False,GREY)],'space_after':4.5,'line':1.02}
hcard(s,0.42,ty,4.06,th,'DEFENDED IN THE PROTOTYPE',GREEN,[
    li('Compromise of the metadata server alone',GREEN),li('Compromise of the chunk store alone',GREEN),
    li('A DBA reading evidence content',GREEN),li('Stolen credentials without the 2nd factor',GREEN),
    li('Cross-case / unauthorised API access',GREEN),li('Modification of stored ciphertext',GREEN),
    li('Retroactive edits to the audit trail',GREEN)])
hcard(s,4.62,ty,4.06,th,'CHALLENGES → STRATEGY',ORANGE,[
    rs('Key compromise','wrapped & isolated in KMS; Vault + rotation in prod.',ORANGE),
    rs('App-server breach','least-privilege services · step-up MFA · full audit.',ORANGE),
    rs('Stolen live session','short token TTL · step-up before sensitive actions.',ORANGE),
    rs('Large exhibits','1 MB chunk streaming · RAM-safe two-pass in prod.',ORANGE),
    rs('Availability','mirrored Server A / B · backup & HA on the roadmap.',ORANGE)])
hcard(s,8.82,ty,3.68,th,'FUTURE SCOPE / ROADMAP',DBLUE,[
    li('Security hardening & penetration testing',DBLUE),
    li('Production KMS + object storage (Vault · MinIO)',DBLUE),
    li('PKI / certified e-signatures',DBLUE),
    li('Backup & high availability (mirror servers)',DBLUE),
    li('Controlled pilot deployment',DBLUE),
    li('Evidence versioning · AI-assisted retrieval',DBLUE)])
tbox(s,0.42,6.72,12.1,0.32,[{'runs':[('PRAMAAN does not claim compromise is impossible — it limits the blast radius of partial compromise and refuses to release evidence it cannot verify.',9.5,True,NAVY,True)],'align':PP_ALIGN.CENTER}])
footer(s,5)

# ==================== SLIDE 6 — IMPACT & BENEFITS ====================
s=add()
chrome(s,'IMPACT AND BENEFITS','Potential impact on the target audience   |   Benefits of the solution (social, economic, environmental, etc.)')
# LEFT — IMPACT + BENEFITS
LX=0.42; LWi=6.0
headrule(s,LX,1.48,LWi,'IMPACT',NAVY)
tbox(s,LX,1.98,LWi,1.9,[
    bull('Tamper-evident custody','an altered chunk is caught before evidence is released.',NAVY),
    bull('Contained breach','no single server yields a readable document.',NAVY),
    bull('Provable accountability','every access sits on a hash-chained audit trail.',NAVY),
    bull('One vault, not many','replaces station registers and shared drives.',NAVY),
])
headrule(s,LX,4.02,LWi,'BENEFITS',ORANGE)
tbox(s,LX,4.52,LWi,2.2,[
    bull('Social','a stronger basis for public trust in how evidence is handled.',ORANGE),
    bull('Economic','open-source stack, no licence fees, commodity hardware, no GPU.',ORANGE),
    bull('Operational','standalone and on-premise; OCR search across Indic scripts.',ORANGE),
    bull('Security','MFA, six-role RBAC, step-up verification and time-limited sharing.',ORANGE),
])
# RIGHT — USER STORY
RX=6.72; RWi=6.18
headrule(s,RX,1.48,RWi,'FOR INSTANCE:  USER STORY',PURPLE)
sc=rrect(s,RX,1.96,RWi,0.66,fillc=STRIP,rad=0.06)
fill(sc.text_frame,[{'runs':[('Scenario   ',9.5,True,NAVY),('A state police cyber cell holds a seized-device extract for a fraud case. It must reach the prosecutor, and the defence later asks whether the file was altered.',9,False,TEXT)],'line':1.05}],anchor=MSO_ANCHOR.MIDDLE)
steps=[('Custodian uploads the exhibit','MFA sign-in; the file is chunked, encrypted, hashed and OCR-indexed on-premise.'),
       ('A stored chunk is tampered with','Verification fails on retrieval: HTTP 422, 0 bytes served, violation recorded.'),
       ('Exhibit is shared with the prosecutor','Step-up MFA, recipient-bound, time-limited; the recipient opens it via OTP.'),
       ('Auditor checks the record','Recomputes the audit chain; verification names the first event that fails.')]
sy2=2.80
for i,(t,d) in enumerate(steps):
    numstep(s,RX,sy2,RWi,i+1,t,d)
    sy2+=0.72
ib=rrect(s,RX,5.72,3.0,0.98,fillc=LIGHT,rad=0.06)
fill(ib.text_frame,[{'runs':[('Impact',9,True,NAVY)],'space_after':2,'line':1.0},
    {'runs':[('Corrupted evidence is never silently served, and one compromised host does not expose a document.',8.3,False,TEXT)],'line':1.05}])
bb=rrect(s,RX+3.18,5.72,3.0,0.98,fillc=LIGHT,rad=0.06)
fill(bb.text_frame,[{'runs':[('Benefit',9,True,ORANGE)],'space_after':2,'line':1.0},
    {'runs':[('Every step has a named actor and a record, which supports chain-of-custody review.',8.3,False,TEXT)],'line':1.05}])
footer(s,6)

# ==================== SLIDE 7 — RESEARCH & REFERENCES ====================
s=add()
chrome(s,'RESEARCH AND REFERENCES','Details / links of the reference and research work')
def ref(term,desc,acc): return {'runs':[(term,8.7,True,acc),('  '+desc,8.5,False,GREY)],'space_after':3.5,'line':1.02}
hcard(s,0.42,1.55,4.06,2.62,'CRYPTOGRAPHIC STANDARDS',NAVY,[
    ref('NIST SP 800-38D','AES-GCM mode, IV construction & tag length — our per-chunk cipher.',NAVY),
    ref('RFC 5869 — HKDF','Extract-and-expand KDF; basis of our per-chunk keys.',NAVY),
    ref('RFC 8032 — Ed25519','Deterministic EdDSA; no per-signature nonce to reuse.',NAVY),
    ref('RFC 6238 — TOTP','Time-based one-time passwords for the second factor.',NAVY),
    ref('NIST SP 800-57 Pt.1 r5','Key-management lifecycle — gen, storage, rotation, destruction.',NAVY),
    ref('NIST SP 800-88 r1','Media sanitization — basis for key & derived-data destruction.',NAVY),
])
hcard(s,4.62,1.55,4.06,2.62,'SECURITY ENGINEERING',ORANGE,[
    ref('OWASP ASVS 4.0','Verification checklist our access-control & crypto-storage map to.',ORANGE),
    ref('OWASP Top 10 (2021)','Broken access control & crypto failures drove the 404-not-403 rule.',ORANGE),
    ref('NIST SP 800-92','Log-management guidance behind the audit schema & retention.',ORANGE),
    ref('Saltzer & Schroeder (1975)','Least privilege & complete mediation — auth re-checked per request.',ORANGE),
    ref('TLS 1.3 (RFC 8446)','All transport over HTTPS in deployment — confidentiality in transit.',ORANGE),
])
hcard(s,8.82,1.55,3.68,2.62,'TECHNOLOGY & PRIOR ART',GREEN,[
    ref('pyca/cryptography','AESGCM, HKDF, Ed25519 — audited, no custom crypto.',GREEN),
    ref('PostgreSQL 16','Full-text search, GIN indexes, xact advisory locks.',GREEN),
    ref('Tesseract + Indic data','Offline OCR: Hindi, Tamil, Telugu, Bengali, Gujarati.',GREEN),
    ref('MinIO · HashiCorp Vault','Studied as production swap-ins behind our interfaces.',GREEN),
    ref('Ollama · sentence-transformers','Studied for the future on-prem AI layer.',GREEN),
])
hcard(s,0.42,4.32,4.06,2.6,'OUR OWN DESIGN RECORD',DBLUE,[
    blt('Eleven feature plans','plus architecture, security, API and edge-case docs.',DBLUE,8.7,sa=4),
    blt('Spec-first','every crypto & access-control decision written down and threat-modelled before code.',DBLUE,8.7,sa=4),
    blt('Terminology discipline','"tamper-evident" not "immutable"; "least-privilege" not "zero-trust".',DBLUE,8.7,sa=4),
])
hcard(s,4.62,4.32,4.06,2.6,'WHAT THE READING CHANGED',ORANGE,[
    blt('SP 800-38D →','per-chunk HKDF keys instead of one key per file, so an IV cannot repeat under a key.',ORANGE,8.7,sa=4),
    blt('OWASP ASVS →','404 instead of 403 on case-scoped resources, so existence is never confirmed.',ORANGE,8.7,sa=4),
    blt('NIST SP 800-92 →','audit events carry actor, action, case, document and result — not just a message.',ORANGE,8.7,sa=4),
])
hcard(s,8.82,4.32,3.68,2.6,'FUTURE SCOPE — AI (READ-ONLY)',GREEN,[
    blt('Context retrieval','semantic search over a read-only derived index, filtered to permitted cases.',GREEN,8.7,sa=4),
    blt('On-prem summarisation','a local model drafts summaries; evidence never leaves the network.',GREEN,8.7,sa=4),
    blt('Strict boundary','the AI layer reads a derived copy and can never modify original evidence.',GREEN,8.7,sa=4),
])
footer(s,7)

OUT=r'C:\Users\aarja\Desktop\SIH26\ppts\PRAMAAN_SIH2026_Idea_Submission_v5.pptx'
prs.save(OUT); print('saved', OUT)

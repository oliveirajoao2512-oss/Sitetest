"""Gera identificação de bancada NEO Polímeros em A4 paisagem (uma folha por bancada)."""
import io
from PIL import Image, ImageChops
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.graphics.barcode import code128
from reportlab.pdfgen import canvas

ORANGE = HexColor("#E8761E"); DARK = HexColor("#3A3A3C"); GRAY = HexColor("#8A8A8E"); LIGHT = HexColor("#F4F4F5")
W, H = landscape(A4)

BANCADAS = [
 ("BANCADA 1", [
   ("100.01.0700.14", ["8001034814 · ESPUMA 1 - PEÇA 2 WIRELESS 598","8001034914 · ESPUMA 2 - PEÇA 2 WIRELESS 598","8001035014 · ESPUMA 3 - PEÇA 2 WIRELESS 598"]),
   ("100.01.0725.14", ["8001034914 · ESPUMA 2 - PEÇA WIRELESS 598","8001035014 · ESPUMA 3 - PEÇA 2 WIRELESS 598","8001035114 · ESPUMA 1 - PEÇA 2 WIRELESS 598","8002039914 · BUCHA AUTO ROSCANTE WCP 291"])]),
 ("BANCADA 2", [
   ("100.01.0701.14", ["8001035114 · ESPUMA 1 - PEÇA 3 WIRELESS 598","8001035214 · ESPUMA 2 - PEÇA 3 WIRELESS 598"]),
   ("100.01.0726.14", ["8001034514 · ESPUMA 3 - DUTO MAIOR WIRELESS 2261","8001035514 · ESPUMA WCP 291"])]),
]

im = Image.open("logo_neo_original.png").convert("RGB")
bbox = ImageChops.invert(im.convert("L")).point(lambda p: 255 if p > 25 else 0).getbbox()
im = im.crop(bbox); im = im.resize((im.width*10, im.height*10), Image.LANCZOS)
buf = io.BytesIO(); im.save(buf, "PNG"); buf.seek(0)
LOGO = ImageReader(buf); LR = im.width/im.height

def fit(c, txt, font, size, maxw):
    while c.stringWidth(txt, font, size) > maxw and size > 6: size -= .5
    return size

def pagina(c, titulo, pns):
    c.setFillColor(white); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(ORANGE); c.rect(0, H-8*mm, W, 8*mm, fill=1, stroke=0)
    lh = 26*mm; c.drawImage(LOGO, 15*mm, H-12*mm-lh, width=lh*LR, height=lh)
    c.setFillColor(GRAY); c.setFont("Helvetica-Bold", 14); c.drawRightString(W-15*mm, H-24*mm, "IDENTIFICAÇÃO DE BANCADA")
    c.setFillColor(DARK); c.setFont("Helvetica-Bold", 118); c.drawCentredString(W/2, H-86*mm, titulo)
    c.setStrokeColor(ORANGE); c.setLineWidth(3); c.line(15*mm, H-96*mm, W-15*mm, H-96*mm)
    gap = 10*mm; cw = (W-30*mm-gap)/2; ch = 80*mm; y0 = 22*mm
    for i, (pn, comps) in enumerate(pns):
        x = 15*mm + i*(cw+gap)
        c.setFillColor(LIGHT); c.setStrokeColor(HexColor("#C9C9CC")); c.setLineWidth(.8)
        c.roundRect(x, y0, cw, ch, 4*mm, fill=1, stroke=1)
        c.setFillColor(ORANGE); c.rect(x, y0+ch-3*mm, cw, 3*mm, fill=1, stroke=0)
        c.setFillColor(GRAY); c.setFont("Helvetica-Bold", 12); c.drawString(x+8*mm, y0+ch-12*mm, "PN")
        c.setFillColor(DARK); c.setFont("Helvetica-Bold", 46); c.drawString(x+8*mm, y0+ch-28*mm, pn)
        bc = code128.Code128(pn, barHeight=11*mm, barWidth=.5*mm, quiet=False)
        bc.drawOn(c, x+cw-8*mm-bc.width, y0+ch-27*mm) if bc.width < 0 else None
        c.setStrokeColor(ORANGE); c.setLineWidth(1.5); c.line(x+8*mm, y0+ch-34*mm, x+cw-8*mm, y0+ch-34*mm)
        c.setFillColor(GRAY); c.setFont("Helvetica-Bold", 9); c.drawString(x+8*mm, y0+ch-41*mm, "COMPONENTES")
        yy = y0+ch-49*mm
        for t in comps:
            fs = fit(c, t, "Helvetica-Bold", 14, cw-22*mm)
            c.setFillColor(ORANGE); c.rect(x+8*mm, yy-.5*mm, 1.6*mm, 5*mm, fill=1, stroke=0)
            c.setFillColor(DARK); c.setFont("Helvetica-Bold", fs); c.drawString(x+12*mm, yy, t); yy -= 8*mm
    c.setFillColor(DARK); c.rect(0, 0, W, 12*mm, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 11)
    c.drawString(15*mm, 4.3*mm, "NEO POLÍMEROS"); c.drawRightString(W-15*mm, 4.3*mm, "BANCADA · PRODUTOS EM PRODUÇÃO")

c = canvas.Canvas("identificacao_bancadas_A4.pdf", pagesize=(W, H))
for t, p in BANCADAS: pagina(c, t, p); c.showPage()
c.save()

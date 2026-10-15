"""Gera etiquetas NEO Polímeros 10x5 cm (folha A4 e uma-por-página)."""
import io
from PIL import Image, ImageChops
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.graphics.barcode import code128
from reportlab.pdfgen import canvas

ORANGE = HexColor("#E8761E"); DARK = HexColor("#3A3A3C"); GRAY = HexColor("#8A8A8E")
W, H = 100*mm, 50*mm

ITENS = [
 ("100.01.0725.14","8001034914","ESPUMA 2 - PEÇA WIRELESS 598"),
 ("100.01.0725.14","8001035014","ESPUMA 3 - PEÇA 2 WIRELESS 598"),
 ("100.01.0725.14","8001035114","ESPUMA 1 - PEÇA 2 WIRELESS 598"),
 ("100.01.0725.14","8002039914","BUCHA AUTO ROSCANTE WCP 291"),
 ("100.01.0726.14","8001034514","ESPUMA 3 - DUTO MAIOR WIRELESS 2261"),
 ("100.01.0726.14","8001035514","ESPUMA WCP 291"),
 ("100.01.0700.14","8001034814","ESPUMA 1 - PEÇA 2 WIRELESS 598"),
 ("100.01.0700.14","8001034914","ESPUMA 2 - PEÇA 2 WIRELESS 598"),
 ("100.01.0700.14","8001035014","ESPUMA 3 - PEÇA 2 WIRELESS 598"),
 ("100.01.0701.14","8001035114","ESPUMA 1 - PEÇA 3 WIRELESS 598"),
 ("100.01.0701.14","8001035214","ESPUMA 2 - PEÇA 3 WIRELESS 598"),
]

# logo: recorta o branco, amplia e usa como imagem de alta qualidade
im = Image.open("logo_neo_original.png").convert("RGB")
bbox = ImageChops.invert(im.convert("L")).point(lambda p: 255 if p > 25 else 0).getbbox()
im = im.crop(bbox); im = im.resize((im.width*8, im.height*8), Image.LANCZOS)
buf = io.BytesIO(); im.save(buf, "PNG"); buf.seek(0)
LOGO = ImageReader(buf); LR = im.width/im.height

def etiqueta(c, x, y, cod, item, desc):
    c.saveState(); c.translate(x, y)
    # fundo e moldura
    c.setFillColor(white); c.setStrokeColor(HexColor("#C9C9CC")); c.setLineWidth(.6)
    c.roundRect(0, 0, W, H, 2*mm, fill=1, stroke=1)
    c.setFillColor(ORANGE); c.rect(0, H-2.2*mm, W, 2.2*mm, fill=1, stroke=0)   # faixa topo
    # logo
    lh = 11*mm; c.drawImage(LOGO, 5*mm, H-4.2*mm-lh, width=lh*LR, height=lh, mask=None)
    # código
    c.setFillColor(GRAY); c.setFont("Helvetica-Bold", 6.5); c.drawRightString(W-5*mm, H-8*mm, "CÓDIGO")
    c.setFillColor(DARK); c.setFont("Helvetica-Bold", 21); c.drawRightString(W-5*mm, H-16*mm, cod)
    c.setStrokeColor(ORANGE); c.setLineWidth(1.2); c.line(5*mm, 31*mm, W-5*mm, 31*mm)
    # item + barcode
    c.setFillColor(GRAY); c.setFont("Helvetica-Bold", 6.5); c.drawString(5*mm, 26.5*mm, "ITEM")
    c.setFillColor(DARK); c.setFont("Helvetica-Bold", 17); c.drawString(5*mm, 20.5*mm, item)
    bc = code128.Code128(item, barHeight=9*mm, barWidth=.33*mm, quiet=False)
    bc.drawOn(c, W-5*mm-bc.width, 20*mm)
    # descrição
    fs = 13.5
    while c.stringWidth(desc, "Helvetica-Bold", fs) > W-10*mm and fs > 9: fs -= .5
    c.setFillColor(ORANGE); c.rect(5*mm, 8.6*mm, 1.2*mm, 6.4*mm, fill=1, stroke=0)
    c.setFillColor(DARK); c.setFont("Helvetica-Bold", fs); c.drawString(8*mm, 10.4*mm, desc)
    # rodapé
    c.setFillColor(DARK); c.rect(0, 0, W, 5.2*mm, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 6.5)
    c.drawString(5*mm, 1.8*mm, "NEO POLÍMEROS"); c.drawRightString(W-5*mm, 1.8*mm, "IDENTIFICAÇÃO DE COMPONENTE")
    c.restoreState()

# 1 etiqueta por página (10x5 cm exato)
c = canvas.Canvas("etiquetas_neo_10x5_individual.pdf", pagesize=(W, H))
for it in ITENS: etiqueta(c, 0, 0, *it); c.showPage()
c.save()

# folha A4: 2 colunas x 5 linhas
c = canvas.Canvas("etiquetas_neo_A4.pdf", pagesize=A4)
mx = (A4[0]-2*W)/2; my = (A4[1]-5*H)/2
for i, it in enumerate(ITENS):
    k = i % 10
    if i and k == 0: c.showPage()
    col, row = k % 2, k // 2
    etiqueta(c, mx+col*W, A4[1]-my-(row+1)*H, *it)
c.save()

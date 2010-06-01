# encoding: utf-8
# vim: shiftwidth=4 expandtab

from __future__ import with_statement

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128

from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from subprocess import check_call

import sys, os, glob

from tracon.shirt_control.codes import generate_code

PDFTK="/usr/bin/pdftk"
DEFAULT_FILENAME="paitalipukkeet.pdf"
BACK_SIDE="media/kaantopuoli.pdf"

PAPER_SIZE = A4
PAPER_WIDTH, PAPER_HEIGHT = PAPER_SIZE

SLIPS_PER_ROW = 2
SLIP_ROWS = 4
MARGIN = 5*mm

LOGO_FONT_FILENAME = os.path.join(os.environ.get("TRACON_ROOT_DIR", "."), "media", "FOY1REG.TTF")
LOGO_FONT = TTFont("FireOfYsgard", LOGO_FONT_FILENAME)
pdfmetrics.registerFont(LOGO_FONT)

SLIPS_PER_PAGE = SLIP_ROWS * SLIPS_PER_ROW
SLIP_WIDTH = (PAPER_WIDTH - (2 * SLIPS_PER_ROW + 2 - 1) * MARGIN) / SLIPS_PER_ROW
SLIP_HEIGHT = (PAPER_HEIGHT - (2 * SLIP_ROWS + 2 - 1) * MARGIN) / SLIP_ROWS
SLIP_XDISP = SLIP_WIDTH + 2 * MARGIN
SLIP_YDISP = SLIP_HEIGHT + 2 * MARGIN

@contextmanager
def state_saved(canvas):
    try:
        canvas.saveState()
        yield canvas
    finally:
        canvas.restoreState()

def split_into_groups(iterable, group_size=8):
    y = []
    for i in iterable:
        y.append(i)
        if len(y) == group_size:
            yield y
            y = []
    if y:
        yield y
        

def generate_shirt_slip_sheets(codes, filename="paitalipukkeet.pdf"):
    c = canvas.Canvas(filename)
    
    for page_slips in split_into_groups(codes, SLIPS_PER_PAGE):
        for row_num, row_slips in enumerate(split_into_groups(page_slips, SLIPS_PER_ROW)):
            for col_num, code in enumerate(row_slips):
                with state_saved(c):
                    c.translate(col_num * SLIP_XDISP + MARGIN, row_num * SLIP_YDISP + MARGIN)
                    render_slip(c, code)

        c.showPage()

    c.save()

def render_slip(c, code, size=None):
    c.rect(0, 0, SLIP_WIDTH, SLIP_HEIGHT)

    barcode = code128.Code128(code, barHeight=10*mm, barWidth=0.4*mm)
    barcode.drawOn(c, 0, 10*mm)

    c.setFont("FireOfYsgard", 36)
    c.drawString(6*mm, 49*mm, "Tracon")
    c.drawString(46*mm, 49*mm, "V")

    c.setFont("Helvetica", 10)
    c.drawString(14*mm, 5*mm, code)

    c.setFont("Helvetica", 12)
    c.drawString(6*mm, 44*mm, u"Paitalipuke")
    c.drawString(6*mm, 35*mm, "Koko: ______")

    c.setFont("Helvetica", 10)
    c.drawString(12*mm, 28.5*mm, "Ladyfit")
    c.drawString(12*mm, 24.5*mm, "Tavallinen")

    c.rect(6.5*mm, 28*mm, 4*mm, 4*mm)
    c.rect(6.5*mm, 24*mm, 4*mm, 4*mm)

    #c.drawString(6*mm, 37*mm, "Tämä lipuke vaihdetaan")
    #c.drawString(6*mm, 33*mm, "T-paitaan tapahtumassa.")
    #c.drawString(6*mm, 28*mm, "Säilytä lipuke huolellisesti.")
    #c.drawString(6*mm, 24*mm, "Älä taita viivakoodia.")

    #c.circle(67*mm, 25.5*mm, 24*mm)
    #c.drawString(63*mm, 23*mm, "Leima")

def test():
    from tracon.shirt_control.codes import generate_code
    codes = [generate_code() for i in xrange(8)]

    generate_shirt_slip_sheets(codes)

def reconstruct(backside, pages, output):
    args = [PDFTK,]
    for page in pages:
        args.append(page)
        args.append(backside)

    args.extend(("cat", "output", output))

    check_call(args)

def burst(filename):
    check_call([PDFTK, filename, "burst"])

def cleanup(pages):
    for page in pages:
        os.unlink(page)

def interleave(output, backside, body):
    burst(body)
    pages = glob.glob("pg_*.pdf")
    pages.sort()

    reconstruct(backside, pages, output)
    cleanup(pages)

def generate(num_codes=100, filename=DEFAULT_FILENAME):
    codes = [generate_code() for i in xrange(num_codes)]

    with NamedTemporaryFile() as temp_file:
        generate_shirt_slip_sheets(codes, temp_file.name)
        interleave(filename, BACK_SIDE, temp_file.name)

    for code in codes:
        print code

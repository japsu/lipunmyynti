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

from tracon.control_slips.codes import generate_code
from tracon.pdf import render_logo, state_saved

PDFTK="/usr/bin/pdftk"
DEFAULT_FILENAME="paitalipukkeet.pdf"
BACK_SIDE="media/kaantopuoli.pdf"

PAPER_SIZE = A4
PAPER_WIDTH, PAPER_HEIGHT = PAPER_SIZE

SLIPS_PER_ROW = 2
SLIP_ROWS = 4
MARGIN = 5*mm

SLIPS_PER_PAGE = SLIP_ROWS * SLIPS_PER_ROW
SLIP_WIDTH = (PAPER_WIDTH - (2 * SLIPS_PER_ROW + 2 - 1) * MARGIN) / SLIPS_PER_ROW
SLIP_HEIGHT = (PAPER_HEIGHT - (2 * SLIP_ROWS + 2 - 1) * MARGIN) / SLIP_ROWS
SLIP_XDISP = SLIP_WIDTH + 2 * MARGIN
SLIP_YDISP = SLIP_HEIGHT + 2 * MARGIN

def split_into_groups(iterable, group_size=8):
    y = []
    for i in iterable:
        y.append(i)
        if len(y) == group_size:
            yield y
            y = []
    if y:
        yield y

def render_codes(shirt_codes, accommodation_codes, c):
    slips = [ShirtSlip(i) for i in shirt_codes] + [AccommodationSlip(i) for i in accommodation_codes]
    render_slip_sheets(slips, c)

def generate_slip_sheets(slips, filename):
    c = canvas.Canvas(filename)
    render_slip_sheets(slips, c)
    c.save()
        
def render_slip_sheets(slips, c):
    for page_slips in split_into_groups(slips, SLIPS_PER_PAGE):
        for row_num, row_slips in enumerate(split_into_groups(page_slips, SLIPS_PER_ROW)):
            for col_num, code in enumerate(row_slips):
                with state_saved(c):
                    c.translate(col_num * SLIP_XDISP + MARGIN, row_num * SLIP_YDISP + MARGIN)
                    code.render(c)

        c.showPage()

class Slip(object):
    def __init__(self, code=None):
        self.code = code

    def render(self, c):
        c.rect(0, 0, SLIP_WIDTH, SLIP_HEIGHT)

        code_str = str(self.code)

        barcode = code128.Code128(code_str, barHeight=10*mm, barWidth=0.4*mm)
        barcode.drawOn(c, 0, 10*mm)

        render_logo(6*mm, 49*mm, c)

        c.setFont("Helvetica", 10)
        c.drawString(14*mm, 5*mm, code_str)

class ShirtSlip(Slip):
    def render(self, c):
        super(ShirtSlip, self).render(c)

        c.setFont("Helvetica", 12)
        c.drawString(6*mm, 44*mm, u"Paitalipuke")

        if self.code.shirt_order is not None:
            c.drawString(6*mm, 35*mm, "Koko: %s" % self.code.shirt_order.size.name)
        else:
            c.drawString(6*mm, 35*mm, "Koko: ______")

        c.setFont("Helvetica", 10)
        c.drawString(12*mm, 28.5*mm, "Ladyfit")
        c.drawString(12*mm, 24.5*mm, "Tavallinen")

        if self.code.shirt_order is not None:
            y0 = (28*mm) if self.code.shirt_order.size.ladyfit else (24*mm)
            y1 = y0 + 4*mm
            x0 = 6.5*mm
            x1 = 6.5*mm + 4*mm

            c.line(x0, y0, x1, y1)
            c.line(x0, y1, x1, y0)

        c.rect(6.5*mm, 28*mm, 4*mm, 4*mm)
        c.rect(6.5*mm, 24*mm, 4*mm, 4*mm)

class AccommodationSlip(Slip):
    def render(self, c):
        super(AccommodationSlip, self).render(c)

        c.setFont("Helvetica", 12)
        c.drawString(6*mm, 44*mm, u"Majoituslipuke")
        c.drawString(6*mm, 38*mm, u"Sampolan koulu")
        c.drawString(6*mm, 34*mm, u"Sammonkatu 2")
        c.drawString(6*mm, 28*mm, u"Esitä majoituslipuke")
        c.drawString(6*mm, 24*mm, u"majoituspaikan valvojalle.")

def test():
    codes = [AccommodationSlip.create_random_slip() for i in xrange(8)]

    generate_slip_sheets(codes)

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
    # deprecated
    slips = [ShirtSlip.create_random_slip() for i in xrange(num_codes)]

    with NamedTemporaryFile() as temp_file:
        generate_slip_sheets(slips, temp_file.name)
        interleave(filename, BACK_SIDE, temp_file.name)

    for slip in slips:
        print slip.code

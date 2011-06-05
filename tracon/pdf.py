# encoding: utf-8
# vim: shiftwidth=4 expandtab

from __future__ import with_statement

from django.conf import settings

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

from contextlib import contextmanager

import os

FIRE_OF_YSGARD = "FireOfYsgard"
FIRE_OF_YSGARD_FILENAME = os.path.join(settings.MEDIA_ROOT, "FOY1REG.TTF")
FIRE_OF_YSGARD_FONT = TTFont(FIRE_OF_YSGARD, FIRE_OF_YSGARD_FILENAME)
pdfmetrics.registerFont(FIRE_OF_YSGARD_FONT)

LOGO_FILENAME = os.path.join(settings.MEDIA_ROOT, "images", "tracon_logo_kuitille.png")

@contextmanager
def state_saved(canvas):
    try:
        canvas.saveState()
        yield canvas
    finally:
        canvas.restoreState()

def render_logo(x, y, c):
    with state_saved(c):
        c.translate(x, y)
        c.drawImage(LOGO_FILENAME, 0, 0, 48*mm, 21.4*mm)
        

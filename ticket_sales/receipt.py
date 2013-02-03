# encoding: utf-8
# vim: shiftwidth=4 expandtab

from __future__ import with_statement

from contextlib import contextmanager
import os

from django.conf import settings

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# XXX correct path
LOGO_FILENAME = os.path.join(settings.MEDIA_ROOT, "images", "tracon_logo_kuitille.png")

BASE_INDENT = 25*mm
DEEP_INDENT = BASE_INDENT + 15*mm

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
        
def render_receipt(order, c):
    render_logo(135*mm, 265*mm, c)

    c.setFont("Times-Roman", 12)
    c.drawString(135*mm, 260*mm, u"Tampere-talossa 8.-9.9.2012")

    c.drawString(BASE_INDENT, 270*mm, order.customer.name)
    c.drawString(BASE_INDENT, 265*mm, order.customer.address)
    c.drawString(BASE_INDENT, 260*mm, u"%s %s" % (order.customer.zip_code, order.customer.city))

    c.drawString(BASE_INDENT, 200*mm, u"Hyvä vastaanottaja,")

    c.drawString(BASE_INDENT, 190*mm, u"Tässä tilaamanne Tracon 7 -tapahtuman pääsyliput:")

    ypos = 180*mm

    for op in order.order_product_set.filter(product__requires_shipping=True):
        c.drawString(BASE_INDENT, ypos, u"%d kpl" % op.count)
        c.drawString(DEEP_INDENT, ypos, op.product.name)

        ypos -= 10*mm

    non_ship = order.order_product_set.filter(product__requires_shipping=False)
    if non_ship:
        c.drawString(BASE_INDENT, ypos, u"Seuraavista tilaamistanne tuotteista saatte lisäohjeita sähköpostitse ennen tapahtumaa:")
        ypos -= 10*mm

        for op in non_ship:
            c.drawString(BASE_INDENT, ypos, u"%d kpl" % op.count)
            c.drawString(DEEP_INDENT, ypos, op.product.name)

            ypos -= 10*mm
    
    c.drawString(BASE_INDENT, ypos, u"Mikäli yllä olevassa luettelossa on virheitä tai kuoren sisältö ei vastaa luetteloa, olkaa hyvä ja")
    c.drawString(BASE_INDENT, ypos - 5*mm, u"ottakaa viipymättä yhteyttä lipunmyyntivastaavaan sähköpostitse osoitteella liput12@tracon.fi.")
    #c.drawString(BASE_INDENT, ypos - 10*mm, u"tai puhelimitse numeroon 0400 464 988 (Janne Forsell, parhaiten tavoittaa klo 10-18).")

    c.drawString(BASE_INDENT, ypos - 15*mm, u"Mainitkaa viestissänne tilausnumeronne #%04d." % order.id)

    ypos -= 30*mm

    c.drawString(BASE_INDENT, ypos, u"Lisätietoja Tracon 7 -tapahtumasta löydätte kotisivuiltamme: http://2012.tracon.fi/")

    ypos -= 15*mm

    c.drawString(BASE_INDENT, ypos, u"Ystävällisin terveisin")
    c.drawString(BASE_INDENT, ypos - 10*mm, u"Tracon 7 -tapahtuman järjestäjät")

    c.line(BASE_INDENT, 20*mm, 210*mm - BASE_INDENT, 20*mm)
    c.setFont("Helvetica", 8)
    c.drawString(BASE_INDENT, 16*mm, u"Tracon ry / Yhdrek. nro. 194.820 / hallitus@tracon.fi")

    c.showPage()

def test():
    class DummyCustomer:
        name = u"Essi Esimerkki"
        address = u"Animupolunkaarteenrinteentie 5 as. 9"
        zip_code = u"33720"
        city = "Tampere"

    class DummyOrder:
        id = 666
        customer = DummyCustomer()

        tickets = 3
        tshirts = 0
        accommodation = 1

    order = DummyOrder()

    c = canvas.Canvas("test.pdf")
    render_receipt(order, c)
    c.save()

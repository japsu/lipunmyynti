# encoding: utf-8
# vim: shiftwidth=4 expandtab

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from tracon.pdf import render_logo

BASE_INDENT = 25*mm
DEEP_INDENT = BASE_INDENT + 15*mm

def render_receipt(order, c):
    render_logo(135*mm, 265*mm, c)

    c.setFont("Times-Roman", 12)
    c.drawString(135*mm, 260*mm, u"Tampere-talossa 3.-4.9.2011")

    c.drawString(BASE_INDENT, 270*mm, order.customer.name)
    c.drawString(BASE_INDENT, 265*mm, order.customer.address)
    c.drawString(BASE_INDENT, 260*mm, u"%s %s" % (order.customer.zip_code, order.customer.city))

    c.drawString(BASE_INDENT, 200*mm, u"Hyvä vastaanottaja,")

    c.drawString(BASE_INDENT, 190*mm, u"Tässä tilaamanne Tracon VI -tapahtuman lipputuotteet:")

    ypos = 180*mm

    c.drawString(BASE_INDENT, ypos, u"%d kpl" % order.tickets)
    c.drawString(DEEP_INDENT, ypos, u"Ennakkolippu")
    c.drawString(DEEP_INDENT, ypos - 5*mm, u"Oikeuttaa sisäänpääsyyn molempina tapahtumapäivinä sekä ennakkotilaajan etuihin.")

    ypos -= 15*mm
    
    if order.accommodation > 0:
        c.drawString(BASE_INDENT, ypos, u"%d kpl" % order.accommodation)
        c.drawString(DEEP_INDENT, ypos, u"Majoitus")
        c.drawString(DEEP_INDENT, ypos - 5*mm, u"Pääsette majoitukseen ilmoittamalla lipun varaajan nimen.")
        ypos -= 15*mm

    c.drawString(BASE_INDENT, ypos, u"Mikäli yllä olevassa luettelossa on virheitä tai kuoren sisältö ei vastaa luetteloa, olkaa hyvä ja")
    c.drawString(BASE_INDENT, ypos - 5*mm, u"ottakaa viipymättä yhteyttä lipunmyyntivastaavaan sähköpostitse osoitteella")
    c.drawString(BASE_INDENT, ypos - 10*mm, u"lipunmyynti11@tracon.fi tai puhelimitse numeroon 050 550 0838.")

    c.drawString(BASE_INDENT, ypos - 20*mm, u"Mainitkaa viestissänne tilausnumeronne #%04d." % order.id)

    ypos -= 30*mm

    c.drawString(BASE_INDENT, ypos, u"Lisätietoja Tracon VI -tapahtumasta löydätte kotisivuiltamme: http://2011.tracon.fi/")

    ypos -= 15*mm

    c.drawString(BASE_INDENT, ypos, u"Ystävällisin terveisin")
    c.drawString(BASE_INDENT, ypos - 10*mm, u"Tracon VI -tapahtuman järjestäjät")

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

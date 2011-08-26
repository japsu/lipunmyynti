#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import *

PRODUCTS = [
    # (name, price_cents, description, classname, requires_shipping, sell_limit, available)
    ("Koko viikonlopun lippu", 1500, "Koko viikonlopun lippu on voimassa ovien avautumisesta lauantaiaamuna tapahtuman loppuun sunnuntai-iltana. Vain koko viikonlopun lipulla pääset nauttimaan yön tunnelmista Traconissa!", "i_viikonloppu.png", "large", True, 5500, True, None),
    ("Lauantailippu", 1000, "Lauantailippu on voimassa lauantaina kello 10-20.", "i_lauantai.png", "medium", True, 3000, True, None),
    ("Sunnuntailippu", 1000, "Sunnuntailippu on voimassa sunnuntaina kello 08-18.", "i_sunnuntai.png", "medium", True, 3000, True, None),
    ("Lattiamajoitus perjantain ja lauantain väliseksi yöksi", 700, "Majoitu kätevästi ja edullisesti Traconin lattiamajoituksessa tapahtumapaikan lähellä! Huomaathan, että majoitusvaraus on voimassa vain yhdessä viikonloppu- tai lauantailipun kanssa. Tarvitset oman makuupussin ja -alustan tai patjan.", "i_pela.png", "small", False, 500, False,

"""Lisätietoja lattiamajoituksesta lähetetään sähköpostitse lähempänä
tapahtumaa."""),
    ("Lattiamajoitus lauantain ja sunnuntain väliseksi yöksi", 700, "Majoitu kätevästi ja edullisesti Traconin lattiamajoituksessa tapahtumapaikan lähellä! Huomaathan, että majoitusvaraus on voimassa vain yhdessä viikonloppu-, lauantai- tai sunnuntailipun kanssa. Tarvitset oman makuupussin ja -alustan tai patjan.", "i_lasu.png", "small", False, 200, True,

"""Lisätietoja lattiamajoituksesta lähetetään sähköpostitse lähempänä
tapahtumaa."""),
    ("Taidekujapöytä", 1500, "Haluatko taidekujalle myymään taidettasi tai käsitöitäsi? Varaa taidekujapöytäsi tästä! Taidekujavastaavamme ottaa järjestelyistä yhteyttä henkilökohtaisesti kaikkiin varaajiin.", "i_art.png", "small", False, 50, True, 

"""Taidekujavastaava ottaa sinuun henkilökohtaisesti yhteyttä koskien
taidekujavarauksesi järjestelyitä. Tervetuloa taidekujalle!"""),
    ("Lattiamajoitus (Kaukajärvi)", 700, "TODO", "i_lasu.png", "small", False, 100, True, "TODO")
]

def create_products():
    for name, price_cents, description, image, classname, requires_shipping, sell_limit, available, mail_description in PRODUCTS:
        obj = Product(
            name=name,
            price_cents=price_cents,
            description=description,
            mail_description=mail_description,
            image=image,
            classname=classname,
            requires_shipping=requires_shipping,
            sell_limit=sell_limit,
            available=available
        )
        obj.save()

if __name__ == "__main__":
    create_products()

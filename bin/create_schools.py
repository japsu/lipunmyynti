#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from tracon.ticket_sales.models import School, Product

# TODO max_people
PERUS = Product.objects.get(name="Lattiamajoitus lauantain ja sunnuntain väliseksi yöksi")
KAUKKIS = Product.objects.get(name__icontains="Kaukaj")

def main():
    School(
        name=u"Kaukajärven koulu",
        address=u"Juvankatu 13",
        product=KAUKKIS,
        max_people=1,
        priority=0
    ).save()

    School(
        name=u"Tammerkosken koulu",
        address=u"Rautatienkatu 3-5",
        product=PERUS,
        max_people=1,
        priority=50
    ).save()

    School(
        name=u"Klassillinen koulu",
        address=u"Tuomiokirkonkatu 5",
        product=PERUS,
        max_people=1,
        priority=100
    ).save()

if __name__ == "__main__":
    main()

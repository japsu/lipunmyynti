#!/usr/bin/env python
# encoding: utf-8
# vim: shiftwidth=4 expandtab

from ticket_sales.models import School, Product

# TODO max_people
PERJANTAI = Product.objects.get(name="Lattiamajoitus perjantain ja lauantain väliseksi yöksi (Tammerkoski)")
TAMMERKOSKI1 = Product.objects.get(name="Lattiamajoitus lauantain ja sunnuntain väliseksi yöksi (Tammerkoski 1)")
AMURI1 = Product.objects.get(name="Lattiamajoitus lauantain ja sunnuntain väliseksi yöksi (Amuri 1)")
AMURI2 = Product.objects.get(name="Lattiamajoitus lauantain ja sunnuntain väliseksi yöksi (Amuri)")

def main():
    School(
        name=u"Tammerkosken koulu (pe-la)",
        address=u"Rautatienkatu 3-5",
        product=PERJANTAI,
        max_people=100,
        priority=0
    ).save()

    School(
        name=u"Tammerkosken koulu (la-su)",
        address=u"Rautatienkatu 3-5",
        product=TAMMERKOSKI1,
        max_people=67,
        priority=100
    ).save()

    School(
        name=u"Amurin koulu (virheelliset)",
        address=u"Satakunnankatu 60",
        product=AMURI1,
        max_people=50,
        priority=0
    ).save()

    School(
        name=u"Amurin koulu (tavalliset)",
        address=u"Satakunnankatu 60",
        product=AMURI2,
        max_people=100,
        priority=50
    ).save()

    School(
        name=u"Amurin koulu (siirretyt)",
        address=u"Satakunnankatu 60",
        product=TAMMERKOSKI1,
        max_people=30,
        priority=100
    ).save()

if __name__ == "__main__":
    main()

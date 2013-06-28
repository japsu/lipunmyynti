# Language: fi
Ominaisuus: Lippujen tilaaminen
  Kävijänä haluan päästä Traconiin, mutta ilkeät järjestäjät sanovat
  että tarvitsen pääsylipun.

  Tausta:
    Oletetaan että järjestelmässä on tuotteita

  Tapaus: Onnistunut tilaus
    Kun surffaan etusivulle
    Niin minun tulisi olla "Tervetuloa ostamaan Tracon 8 -lippuja!"-vaiheella

    Kun valitsen "Seuraava"
    Niin minun tulisi olla "Valitse ostettavat tuotteet"-vaiheella

    Kun valitsen haluamani tuotteet
    Ja valitsen "Seuraava"
    Niin minun tulisi olla "Toimitusosoite"-vaiheella

    Kun täytän toimitusosoitteeni
    Ja valitsen "Seuraava"
    Niin minun tulisi olla "Vahvista tilaus"-vaiheella
    Ja edellisellä vaiheella syöttämäni toimitusosoitteen tulisi näkyä
    Ja aikaisemmalla vaiheella valitsemieni tuotteiden tulisi näkyä

    Kun valitsen "Siirry maksamaan"
    Niin minun tulisi olla maksuoperaattorin maksusivulla

    Kun maksan tilaukseni
    Niin minun tulisi olla "Kiitos tilauksesta!"-vaiheella

    Ja tilaukseni tulisi olla tallentunut järjestelmään
    Ja tilaukseni tulisi olla vahvistettu
    Ja tilaukseni tulisi olla maksettu
    Ja tilaukseni tulisi olla sisältää valitsemani tuotteet
    Ja minun tulisi olla saanut sähköpostiini maksuvahvistusviesti

  Tapaus: Ei yhtään tuotetta
    Kun teen tilauksen "Valitse ostettavat tuotteet"-vaiheen alkuun asti
    Ja valitsen "Seuraava"
    Niin minun tulisi nähdä ilmoitus "Valitse vähintään yksi tuote."

  Tapaus: Puuttuvia kenttiä toimitusosoitteessa
    Kun teen tilauksen "Toimitusosoite"-vaiheen alkuun asti
    Ja valitsen "Seuraava"
    Niin minun tulisi olla "Toimitusosoite"-vaiheella
    Ja minun tulisi nähdä ilmoitus "Tarkista lomakkeen sisältö"

    Kun täytän joitain kenttiä, mutten kaikkia
    Ja valitsen "Seuraava"
    Niin minun tulisi olla "Toimitusosoite"-vaiheella
    Ja minun tulisi nähdä ilmoitus "Tarkista lomakkeen sisältö"

    Kun täytän toimitusosoitteeni
    Ja valitsen "Seuraava"
    Niin minun tulisi olla "Vahvista tilaus"-vaiheella

  Tapaus: Kelvoton sähköpostiosoite
    Kun teen tilauksen "Toimitusosoite"-vaiheen alkuun asti
    Ja täytän toimitusosoitteeni
    Mutta syötän kelvottoman sähköpostiosoitteen
    Ja valitsen "Seuraava"
    Niin minun tulisi olla "Toimitusosoite"-vaiheella
    Ja minun tulisi nähdä ilmoitus "Tarkista lomakkeen sisältö"

  Tapaus: Maksu perutaan
    Kun teen tilauksen "Vahvista tilaus"-vaiheen alkuun asti
    Ja valitsen "Siirry maksamaan"
    Ja perun maksun

    Niin minun tulisi olla "Vahvista tilaus"-vaiheella
    Ja minun tulisi nähdä ilmoitus "Maksu peruttiin."

  Tapaus: Maksu epäonnistuu
    Kun teen tilauksen "Vahvista tilaus"-vaiheen alkuun asti
    Ja valitsen "Siirry maksamaan"
    Ja maksu epäonnistuu

    Niin minun tulisi olla "Vahvista tilaus"-vaiheella
    Ja minun tulisi nähdä ilmoitus "Maksu epäonnistui. Ole hyvä ja ota yhteyttä"
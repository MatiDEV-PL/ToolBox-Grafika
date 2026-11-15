
import random
from toolbox import Dane, Obiekt, zapisz

dane = Dane()

#para 1 - przecinaja sie
dane.kontener.dodaj(
    Obiekt.z_wspolrzednych(0, 3, 0, 0, kolor=1)
)
dane.kontener.dodaj(
    Obiekt.z_wspolrzednych(0, 3, 0, 0, kolor=1)
)

#para 2 - nie przecinaja sie
dane.kontener.dodaj(
    Obiekt.z_wspolrzednych(0, 0, 2, 0, kolor=1)
)
dane.kontener.dodaj(
    Obiekt.z_wspolrzednych(3, 0, 5, 0, kolor=1)
)

#para 3 - dotykaja sie koncami
dane.kontener.dodaj(
    Obiekt.z_wspolrzednych(0, 0, 2, 0, kolor=1)
)
dane.kontener.dodaj(
    Obiekt.z_wspolrzednych(2, 0, 2, 3, kolor=1)
)

#funkcja generujaca losowy odcinek
def losowy_odcinek():
    while True:
        x1 = random.randint(-10, 10)
        y1 = random.randint(-10, 10)
        x2 = random.randint(-10, 10)
        y2 = random.randint(-10, 10)

        if (x1, y1) != (x2, y2):
            return Obiekt.z_wspolrzednych(
                x1, y1, x2, y2, kolor=1
            )

#dwie dodatkowe pary losowe
for i in range(2):
    dane.kontener.dodaj(losowy_odcinek())
    dane.kontener.dodaj(losowy_odcinek())

zapisz("odcinki.txt", dane)

print("Zapisano odcinki do pliku!")


from toolbox import wczytaj, Dane, Przeciecie, punkt_przeciecia, zapisz

#wczytujemy odcinki z pliku
dane = wczytaj("odcinki.txt")

#pobieramy wszystkie odcinki
odcinki = dane.kontener.odcinki()

#przygotowujemy dane na wyniki
wyniki = Dane(info=["Wyniki sprawdzania przeciec"])

#kolejne pary odcinkow
for i in range(0, len(odcinki), 2):

    a = odcinki[i]
    b = odcinki[i + 1]

    #sprawdzamy czy odcinki sie przecinaja
    czy_przecinaja = a.tuli_z(b)

    #obliczamy punkt przeciecia
    punkt = punkt_przeciecia(a, b)

    if czy_przecinaja:
        print(f"Punkt przeciecia {i // 2 + 1}: ({punkt.x}, {punkt.y})")
    else:
        print(f"Para {i // 2 + 1}: brak punktu przecięcia")

    nr_pary = i // 2 + 1

    if czy_przecinaja:
        print(f"Para {nr_pary}: TAK")
        wyniki.info.append(f"Para {nr_pary}: TAK")
    else:
        print(f"Para {nr_pary}: NIE")
        wyniki.info.append(f"Para {nr_pary}: NIE")

    wyniki.przeciecia.append(Przeciecie(a, b, punkt))

zapisz("wyniki.txt", wyniki)

print("Wyniki zapisano do pliku!")

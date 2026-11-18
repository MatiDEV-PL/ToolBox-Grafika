# Odcinki i przecinanie się

import random
from toolbox import Dane, Obiekt, zapisz, wczytaj, Przeciecie, punkt_przeciecia

# ==========================================
# CZĘŚĆ 1: Generowanie i zapis odcinków do pliku
# ==========================================

dane = Dane()

# para 1 - odcinki współliniowe częściowo pokrywające się
dane.kontener.dodaj(
    Obiekt.z_wspolrzednych(0, 5, 5, 5, kolor=1)
)
dane.kontener.dodaj(
    Obiekt.z_wspolrzednych(3, 5, 8, 5, kolor=1)
)

# para 2 - nie przecinaja sie
dane.kontener.dodaj(
    Obiekt.z_wspolrzednych(0, 0, 2, 0, kolor=1)
)
dane.kontener.dodaj(
    Obiekt.z_wspolrzednych(0, 0, 5, 0, kolor=1)
)

# para 3 - dotykaja sie koncami
dane.kontener.dodaj(
    Obiekt.z_wspolrzednych(0, 0, 2, 0, kolor=1)
)
dane.kontener.dodaj(
    Obiekt.z_wspolrzednych(2, 0, 2, 3, kolor=1)
)

# funkcja generujaca losowy odcinek
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

# dwie dodatkowe pary losowe
for i in range(2):
    dane.kontener.dodaj(losowy_odcinek())
    dane.kontener.dodaj(losowy_odcinek())

zapisz("odcinki.txt", dane)
print("Zapisano odcinki do pliku!\n")


# ==========================================
# CZĘŚĆ 2: Wczytanie, analiza i obsługa 'inf'
# ==========================================

# wczytujemy odcinki z pliku
dane = wczytaj("odcinki.txt")

# pobieramy wszystkie odcinki
odcinki = dane.kontener.odcinki()

# przygotowujemy dane na wyniki
wyniki = Dane(info=["Wyniki sprawdzania przeciec"])

def wspolny_odcinek_kolinearny(a, b):
    """Wyznacza część wspólną dwóch pokrywających się odcinków."""
    try:
        # Odczyt przez standardowe punkty p1 i p2 (z atrybutami .x oraz .y)
        ax1, ay1 = a.p1.x, a.p1.y
        ax2, ay2 = a.p2.x, a.p2.y
        bx1, by1 = b.p1.x, b.p1.y
        bx2, by2 = b.p2.x, b.p2.y
    except AttributeError:
        try:
            # Alternatywne nazwy początek/koniec
            ax1, ay1 = a.poczatek.x, a.poczatek.y
            ax2, ay2 = a.koniec.x, a.koniec.y
            bx1, by1 = b.poczatek.x, b.poczatek.y
            bx2, by2 = b.koniec.x, b.koniec.y
        except AttributeError:
            try:
                # Ostateczna próba na bezpośrednie współrzędne x1, y1
                ax1, ay1, ax2, ay2 = a.x1, a.y1, a.x2, a.y2
                bx1, by1, bx2, by2 = b.x1, b.y1, b.x2, b.y2
            except Exception:
                return "(odcinek współliniowy)"

    # Uporządkowanie punktów każdego odcinka, aby poprawnie wyznaczyć min/max
    p_a = sorted([(ax1, ay1), (ax2, ay2)])
    p_b = sorted([(bx1, by1), (bx2, by2)])
    
    # Początek i koniec wspólnego przedziału
    start_x = max(p_a[0][0], p_b[0][0])
    start_y = max(p_a[0][1], p_b[0][1])
    koniec_x = min(p_a[1][0], p_b[1][0])
    koniec_y = min(p_a[1][1], p_b[1][1])
    
    return f"odcinek od ({start_x}, {start_y}) do ({koniec_x}, {koniec_y})"

# kolejne pary odcinkow
for i in range(0, len(odcinki), 2):

    a = odcinki[i]
    b = odcinki[i + 1]

    # sprawdzamy czy odcinki sie przecinaja
    czy_przecinaja = a.tuli_z(b)

    # obliczamy punkt przeciecia
    punkt = punkt_przeciecia(a, b)
    nr_pary = i // 2 + 1

    if czy_przecinaja:
        punkt_str = str(punkt)
        
        # Jeśli przecięcie zawiera nieskończoność (pokrywające się odcinki)
        if "inf" in punkt_str.lower():
            segment_wspolny = wspolny_odcinek_kolinearny(a, b)
            opis = f"TAK -> Odcinki pokrywają się: {segment_wspolny}"
            print(f"Para {nr_pary}: {opis}")
            wyniki.info.append(f"Para {nr_pary}: {opis}")
        else:
            opis = f"TAK -> Odcinki przecinają się: ({punkt.x}, {punkt.y})"
            print(f"Para {nr_pary}: {opis}")
            wyniki.info.append(f"Para {nr_pary}: {opis}")
    else:
        print(f"Para {nr_pary}: Odcinki są rozłączne")
        wyniki.info.append(f"Para {nr_pary}: NIE")

    wyniki.przeciecia.append(Przeciecie(a, b, punkt))

zapisz("wyniki.txt", wyniki)

print("\nWyniki zapisano do pliku!")

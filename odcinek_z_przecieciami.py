"""Przykład: pary odcinków, przecięcia i część wspólna.

Skrypt zapisuje zestaw odcinków do pliku, wczytuje go z powrotem,
sprawdza każdą parę i zapisuje wyniki. Uruchamiać z katalogu projektu:

    python odcinek_z_przecieciami.py
"""
import random

from toolbox import (
    Dane,
    Obiekt,
    Przeciecie,
    czesc_wspolna,
    punkt_przeciecia,
    wczytaj,
    zapisz,
)

PLIK_ODCINKI = "odcinki.txt"
PLIK_WYNIKI = "wyniki.txt"


def losowy_odcinek() -> Obiekt:
    """Losowy odcinek o różnych końcach."""
    while True:
        x1, y1 = random.randint(-10, 10), random.randint(-10, 10)
        x2, y2 = random.randint(-10, 10), random.randint(-10, 10)
        if (x1, y1) != (x2, y2):
            return Obiekt.z_wspolrzednych(x1, y1, x2, y2, kolor=1)


def zbuduj_przyklad() -> Dane:
    """Trzy pary przypadków + dwie pary losowe."""
    dane = Dane()

    # para 1 - współliniowe, częściowo pokrywające się
    dane.kontener.dodaj(Obiekt.z_wspolrzednych(0, 5, 5, 5, kolor=1))
    dane.kontener.dodaj(Obiekt.z_wspolrzednych(3, 5, 8, 5, kolor=1))

    # para 2 - współliniowe, jeden odcinek zawiera drugi
    dane.kontener.dodaj(Obiekt.z_wspolrzednych(0, 0, 2, 0, kolor=1))
    dane.kontener.dodaj(Obiekt.z_wspolrzednych(0, 0, 5, 0, kolor=1))

    # para 3 - stykają się końcami
    dane.kontener.dodaj(Obiekt.z_wspolrzednych(0, 0, 2, 0, kolor=1))
    dane.kontener.dodaj(Obiekt.z_wspolrzednych(2, 0, 2, 3, kolor=1))

    # dwie dodatkowe pary losowe
    for _ in range(2):
        dane.kontener.dodaj(losowy_odcinek())
        dane.kontener.dodaj(losowy_odcinek())

    return dane


def opis_pary(nr: int, a: Obiekt, b: Obiekt) -> tuple[str, Przeciecie]:
    """Zwraca opis pary dla człowieka i gotowe przecięcie do zapisania."""
    punkt = punkt_przeciecia(a, b)

    if not a.tuli_z(b):
        return f"Para {nr}: NIE", Przeciecie(a, b, punkt)

    if punkt.jest_nieskonczony:
        czesc = czesc_wspolna(a, b)
        if czesc is None:
            return f"Para {nr}: TAK -> odcinki pokrywają się", Przeciecie(a, b, punkt)
        (x1, y1), (x2, y2) = czesc[0].wspolrzedne, czesc[1].wspolrzedne
        return (
            f"Para {nr}: TAK -> odcinki pokrywają się: "
            f"od ({x1:g}, {y1:g}) do ({x2:g}, {y2:g})",
            Przeciecie(a, b, punkt, czesc),
        )

    return (
        f"Para {nr}: TAK -> przecinają się w ({punkt.x:g}, {punkt.y:g})",
        Przeciecie(a, b, punkt),
    )


def main() -> None:
    zapisz(PLIK_ODCINKI, zbuduj_przyklad())
    print(f"Zapisano odcinki do pliku {PLIK_ODCINKI}\n")

    odcinki = wczytaj(PLIK_ODCINKI).kontener.odcinki()
    wyniki = Dane(info=["Wyniki sprawdzania przeciec"])

    for i in range(0, len(odcinki) - 1, 2):
        opis, przeciecie = opis_pary(i // 2 + 1, odcinki[i], odcinki[i + 1])
        print(opis)
        wyniki.info.append(opis)
        wyniki.przeciecia.append(przeciecie)

    zapisz(PLIK_WYNIKI, wyniki)
    print(f"\nWyniki zapisano do pliku {PLIK_WYNIKI}")


if __name__ == "__main__":
    main()

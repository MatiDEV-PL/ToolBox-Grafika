"""
Generuje pliki z punktami do testowania algorytmów otoczki wypukłej.

Uruchomienie z głównego katalogu projektu:

    python generuj_punkty.py

Powstają pliki w folderze dane/otoczka/:

    punkty_10.txt     10 losowych punktów
    punkty_100.txt    100 losowych punktów
    punkty_1000.txt   1000 losowych punktów
    kolo_100.txt      100 punktów na okręgu (każdy jest wierzchołkiem otoczki)

Ziarno losowania jest stałe, więc za każdym razem wychodzą te same pliki.
"""
import random
from math import cos, pi, sin
from pathlib import Path

from toolbox import Dane, Punkt, ZapiszDane

FOLDER = Path("dane") / "otoczka"
ZAKRES = 100          # współrzędne z przedziału [-ZAKRES, ZAKRES]
ZIARNO = 2026


def losowe(n: int, rng: random.Random) -> list[Punkt]:
    """n różnych punktów, współrzędne zaokrąglone do 3 miejsc."""
    wynik, widziane = [], set()
    while len(wynik) < n:
        x = round(rng.uniform(-ZAKRES, ZAKRES), 3)
        y = round(rng.uniform(-ZAKRES, ZAKRES), 3)
        if (x, y) not in widziane:
            widziane.add((x, y))
            wynik.append(Punkt(x, y))
    return wynik


def na_okregu(n: int, promien: float = 50.0) -> list[Punkt]:
    """n punktów równo rozłożonych na okręgu o środku w (0, 0)."""
    return [
        Punkt(round(promien * cos(2 * pi * i / n), 3),
              round(promien * sin(2 * pi * i / n), 3))
        for i in range(n)
    ]


def zapisz_zestaw(nazwa: str, opis: str, punkty: list[Punkt]) -> None:
    dane = Dane(info=[opis, f"Liczba punktów: {len(punkty)}"])
    for p in punkty:
        dane.kontener.dodaj(p)
    sciezka = FOLDER / f"{nazwa}.txt"
    ZapiszDane(sciezka, dane)
    print(f"zapisano {sciezka} ({len(punkty)} punktów)")


if __name__ == "__main__":
    FOLDER.mkdir(parents=True, exist_ok=True)
    rng = random.Random(ZIARNO)
    for n in (10, 100, 1000):
        zapisz_zestaw(f"punkty_{n}", f"Losowe punkty z kwadratu [-{ZAKRES}, {ZAKRES}]^2", losowe(n, rng))
    zapisz_zestaw("kolo_100", "Punkty na okręgu o promieniu 50 (wszystkie na otoczce)", na_okregu(100))

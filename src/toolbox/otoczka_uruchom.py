"""
Uruchamia trzy algorytmy otoczki wypukłej na plikach z punktami.

    python otoczka_uruchom.py                      # wszystkie pliki z dane/otoczka/
    python otoczka_uruchom.py dane/otoczka/punkty_100.txt   # jeden plik

Dla każdego pliku i algorytmu:
  * liczy otoczkę i mierzy czas,
  * sprawdza, czy wszystkie algorytmy dały ten sam wynik,
  * zapisuje plik wyniku w wyniki/otoczka/<zestaw>_<algorytm>.txt
    (punkty wejściowe, otoczka w sekcji [polygon] i statystyki w [info]).
"""
import sys
from pathlib import Path
from time import perf_counter

from toolbox import Dane, Wielokat, WczytajDane, ZapiszDane
from toolbox.otoczka import ALGORYTMY

WEJSCIE = Path("dane") / "otoczka"
WYJSCIE = Path("wyniki") / "otoczka"


def uruchom(sciezka: Path) -> None:
    dane = WczytajDane(sciezka)
    punkty = dane.kontener.punkty()
    zestaw = sciezka.stem
    print(f"\n=== {zestaw}: {len(punkty)} punktów ===")

    wyniki = {}
    for nazwa, algorytm in ALGORYTMY.items():
        start = perf_counter()
        otoczka = algorytm(punkty)
        czas_ms = (perf_counter() - start) * 1000
        wyniki[nazwa] = otoczka
        print(f"  {nazwa:12s} wierzchołków: {len(otoczka):4d}   t = {czas_ms:10.3f} ms")

        wynik = Dane(info=[
            f"statystyki dla zestawu {zestaw}",
            f"Algorytm {nazwa}",
            f"t = {czas_ms:.3f}ms",
            f"Liczba punktów wejściowych: {len(punkty)}",
            f"Liczba punktów wyjściowych: {len(otoczka)}",
        ])
        for p in punkty:
            wynik.kontener.dodaj(p)
        wynik.wielokaty.append(Wielokat(list(otoczka), kolor=1))
        WYJSCIE.mkdir(parents=True, exist_ok=True)
        ZapiszDane(WYJSCIE / f"{zestaw}_{nazwa}.txt", wynik)

    wspolrzedne = {n: [p.wspolrzedne for p in h] for n, h in wyniki.items()}
    if len({tuple(v) for v in wspolrzedne.values()}) == 1:
        print("  OK: wszystkie algorytmy dały ten sam wynik")
    else:
        print("  UWAGA: algorytmy dały różne wyniki!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pliki = [Path(a) for a in sys.argv[1:]]
    else:
        pliki = sorted(WEJSCIE.glob("*.txt"))
    if not pliki:
        sys.exit(f"Brak plików z punktami. Najpierw uruchom: python generuj_punkty.py")
    for p in pliki:
        uruchom(p)

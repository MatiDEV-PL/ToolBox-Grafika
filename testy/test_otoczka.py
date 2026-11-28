import random
from pathlib import Path

import pytest

from toolbox import (
    Dane, Punkt, Wielokat, WczytajDane, ZapiszDane, punkt, zakret,
)
from toolbox.otoczka import (
    ALGORYTMY, otoczka_graham, otoczka_naiwna, otoczka_przyrostowa,
)

DANE = Path(__file__).resolve().parent.parent / "dane" / "otoczka"

# Każdy test z parametrem "algorytm" uruchamia się trzy razy: raz dla każdego algorytmu.
wszystkie = pytest.mark.parametrize("algorytm", list(ALGORYTMY.values()), ids=list(ALGORYTMY))


def wsp(otoczka):
    """Lista samych współrzędnych, łatwa do porównania i wypisania."""
    return [p.wspolrzedne for p in otoczka]


def punkty(*pary):
    return [punkt(x, y) for x, y in pary]


# --- Proste, ręcznie policzone przypadki --------------------------------

@wszystkie
def test_kwadrat_z_punktem_w_srodku(algorytm):
    p = punkty((0, 0), (4, 0), (4, 4), (0, 4), (2, 2))
    wynik = wsp(algorytm(p))
    print(f"  kwadrat + srodek -> {wynik}")
    # zgodnie z zegarem, od punktu najbardziej na lewo (przy remisie najniższego)
    assert wynik == [(0.0, 0.0), (0.0, 4.0), (4.0, 4.0), (4.0, 0.0)]


@wszystkie
def test_trojkat(algorytm):
    wynik = wsp(algorytm(punkty((0, 0), (6, 0), (3, 5))))
    print(f"  trojkat -> {wynik}")
    assert wynik == [(0.0, 0.0), (3.0, 5.0), (6.0, 0.0)]


@wszystkie
def test_punkty_na_bokach_nie_sa_wierzcholkami(algorytm):
    # siatka 5x5: środkowe punkty leżą na bokach albo w środku
    siatka = [punkt(x, y) for x in range(5) for y in range(5)]
    wynik = wsp(algorytm(siatka))
    print(f"  siatka 5x5 -> {wynik}")
    assert set(wynik) == {(0.0, 0.0), (0.0, 4.0), (4.0, 4.0), (4.0, 0.0)}
    assert len(wynik) == 4


@wszystkie
def test_powtorzone_punkty_licza_sie_raz(algorytm):
    wynik = wsp(algorytm(punkty((0, 0), (0, 0), (4, 0), (4, 0), (2, 3), (2, 3))))
    print(f"  duplikaty -> {wynik}")
    assert len(wynik) == 3


# --- Zbiory zdegenerowane ------------------------------------------------

@wszystkie
def test_pusty_i_jeden_punkt(algorytm):
    assert algorytm([]) == []
    wynik = algorytm(punkty((3, 4)))
    print(f"  jeden punkt -> {wsp(wynik)}")
    assert wsp(wynik) == [(3.0, 4.0)]


@wszystkie
def test_dwa_punkty(algorytm):
    wynik = wsp(algorytm(punkty((5, 5), (1, 2))))
    print(f"  dwa punkty -> {wynik}")
    assert wynik == [(1.0, 2.0), (5.0, 5.0)]


@wszystkie
def test_wszystkie_punkty_na_jednej_prostej(algorytm):
    wynik = wsp(algorytm(punkty((0, 0), (2, 2), (1, 1), (3, 3), (-1, -1))))
    print(f"  wspolliniowe -> {wynik}")
    assert wynik == [(-1.0, -1.0), (3.0, 3.0)]


@wszystkie
def test_pionowa_prosta(algorytm):
    wynik = wsp(algorytm(punkty((0, 5), (0, 1), (0, 3))))
    print(f"  pionowa prosta -> {wynik}")
    assert wynik == [(0.0, 1.0), (0.0, 5.0)]


# --- Własności wyniku ----------------------------------------------------

def losowe(n, rng, zakres=20):
    return [punkt(rng.randint(0, zakres), rng.randint(0, zakres)) for _ in range(n)]


@wszystkie
def test_otoczka_jest_wypukla_i_zgodna_z_zegarem(algorytm):
    rng = random.Random(1)
    for _ in range(50):
        h = algorytm(losowe(40, rng))
        n = len(h)
        # w każdym wierzchołku skręt w prawo (ściśle), więc wypukła i bez punktów na bokach
        assert all(zakret(h[i], h[(i + 1) % n], h[(i + 2) % n]) < 0 for i in range(n))
    print("  50 zbiorow: kazdy skret w prawo")


@wszystkie
def test_wszystkie_punkty_sa_wewnatrz_lub_na_brzegu(algorytm):
    rng = random.Random(2)
    for _ in range(30):
        p = losowe(40, rng)
        h = algorytm(p)
        n = len(h)
        for r in p:
            # r nie może być po LEWEJ od żadnego boku
            assert all(zakret(h[i], h[(i + 1) % n], r) <= 0 for i in range(n))
    print("  30 zbiorow: zaden punkt nie wystaje poza otoczke")


# --- Zgodność algorytmów ------------------------------------------------

def test_algorytmy_daja_ten_sam_wynik_na_losowych_zbiorach():
    rng = random.Random(3)
    for _ in range(300):
        p = losowe(rng.randint(0, 30), rng, zakres=rng.choice([3, 6, 20]))
        a = wsp(otoczka_naiwna(p))
        assert wsp(otoczka_przyrostowa(p)) == a
        assert wsp(otoczka_graham(p)) == a
    print("  300 zbiorow (takze z duplikatami i wspolliniowymi): trzy algorytmy zgodne")


def test_kolejnosc_punktow_wejsciowych_nie_ma_znaczenia():
    rng = random.Random(4)
    p = losowe(50, rng)
    wzorzec = wsp(otoczka_graham(p))
    for algorytm in ALGORYTMY.values():
        for _ in range(5):
            rng.shuffle(p)
            assert wsp(algorytm(p)) == wzorzec
    print("  przetasowane wejscie -> ten sam wynik")


# --- Pliki z punktami ----------------------------------------------------

# Rozmiary otoczek policzone dla plików z folderu dane/otoczka.
PLIKI = [("punkty_10", 10, 5), ("punkty_100", 100, 11),
         ("punkty_1000", 1000, 15), ("kolo_100", 100, 100)]


@pytest.mark.parametrize("nazwa,ile_punktow,ile_wierzcholkow", PLIKI)
def test_pliki_z_punktami(nazwa, ile_punktow, ile_wierzcholkow):
    p = WczytajDane(DANE / f"{nazwa}.txt").kontener.punkty()
    assert len(p) == ile_punktow
    wyniki = {n: wsp(f(p)) for n, f in ALGORYTMY.items()}
    print(f"  {nazwa}: {ile_punktow} punktow -> otoczka {len(wyniki['graham'])} wierzcholkow")
    assert len(wyniki["graham"]) == ile_wierzcholkow
    assert wyniki["naiwny"] == wyniki["przyrostowy"] == wyniki["graham"]


def test_otoczka_zapisana_do_pliku_i_wczytana_z_powrotem(tmp_path):
    p = WczytajDane(DANE / "punkty_100.txt").kontener.punkty()
    h = otoczka_graham(p)
    dane = Dane(info=["wynik testu"])
    for x in p:
        dane.kontener.dodaj(x)
    dane.wielokaty.append(Wielokat(h, kolor=1))
    plik = tmp_path / "wynik.txt"
    ZapiszDane(plik, dane)
    odczyt = WczytajDane(plik)
    print(f"  zapis i odczyt: wielokat ma {len(odczyt.wielokaty[0].punkty)} wierzcholkow")
    assert wsp(odczyt.wielokaty[0].punkty) == wsp(h)
    assert len(odczyt.kontener.punkty()) == 100

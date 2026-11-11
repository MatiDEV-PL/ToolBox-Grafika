import math

import pytest

from toolbox import Obiekt, Punkt, PUNKT_NIESKONCZONOSCI, PUNKT_ROZBIEGAJACY
from toolbox.pliki import (
    BladPliku, Dane, Wielokat, Strona, oblicz_przeciecia, punkt_przeciecia,
    strona_punktu, z_tekstu, do_tekstu, zapisz, wczytaj,
)

PRZYKLAD = """
[info]
# Przykładowy plik z danymi

[points 0]
# Zestaw nr 3
-0.001 0.5
-10.5 10.5

[points 2]
-11.8 -5.0

[segments 1]
1.0 4.0 0.0 -12.0
10.0 12.0 -0.667 0.667

[intersections]
-1.0 0.0 1.0 0.0 1  0.0 -1.0 0.0 1.0 2  0.0 0.0
 2.0 0.0 3.0 0.0 1  0.0 -1.0 0.0 1.0 2  nan nan
-1.0 0.0 1.0 0.0 1  0.0 0.0 2.0 0.0 2  -inf inf

[polygon 1]
0.0 0.0
9.0 11.0
3.0 0.0

[side]
-1.0 0.0 1.0 0.0  1.0 -1.0 1
-1.0 0.0 1.0 0.0  0.0 1.0 -1
-1.0 0.0 1.0 0.0  0.0 0.0 0
"""


def test_odczyt_przykladu():
    d = z_tekstu(PRZYKLAD)
    print(f"  punkty={len(d.kontener.punkty())} odcinki={len(d.kontener.odcinki())} "
          f"przeciecia={len(d.przeciecia)} wielokaty={len(d.wielokaty)} strony={len(d.strony)}")
    assert d.info == ["Przykładowy plik z danymi"]
    assert [p.c for p in d.kontener.punkty()] == [0, 0, 2]
    assert d.kontener.odcinki()[0].kolor == 1
    assert d.przeciecia[0].a.kolor == 1 and d.przeciecia[0].b.kolor == 2
    assert math.isnan(d.przeciecia[1].punkt.x)
    assert d.przeciecia[2].punkt.x == -math.inf and d.przeciecia[2].punkt.y == math.inf
    assert len(d.wielokaty[0].punkty) == 3 and d.wielokaty[0].kolor == 1
    assert [s.strona for s in d.strony] == [1, -1, 0]


def test_zapis_i_odczyt_daje_to_samo(tmp_path):
    d = z_tekstu(PRZYKLAD)
    sciezka = tmp_path / "dane.txt"
    zapisz(sciezka, d)
    tekst = sciezka.read_text(encoding="utf-8")
    print(tekst)
    assert do_tekstu(wczytaj(sciezka)) == tekst


def test_przeciecia_obliczone_zgadzaja_sie_z_plikiem():
    d = z_tekstu(PRZYKLAD)
    for pr in d.przeciecia:
        obliczony = punkt_przeciecia(pr.a, pr.b)
        print(f"  plik=({pr.punkt.x}, {pr.punkt.y}) policzone=({obliczony.x}, {obliczony.y})")
        if pr.punkt.jest_specjalny:
            assert obliczony.jest_nan == pr.punkt.jest_nan
            assert obliczony.jest_nieskonczony == pr.punkt.jest_nieskonczony
        else:
            assert obliczony.wspolrzedne == pytest.approx(pr.punkt.wspolrzedne)


def test_dotkniecie_koncami_to_jeden_punkt():
    a = Obiekt.z_wspolrzednych(0, 0, 5, 0)
    b = Obiekt.z_wspolrzednych(5, 0, 10, 0)
    assert punkt_przeciecia(a, b).wspolrzedne == (5.0, 0.0)


def test_strony_zgadzaja_sie_z_plikiem():
    for s in z_tekstu(PRZYKLAD).strony:
        assert strona_punktu(s.odcinek, s.punkt) == s.strona


def test_oblicz_przeciecia_liczy_wszystkie_pary():
    odc = [Obiekt.z_wspolrzednych(0, 0, 1, 1), Obiekt.z_wspolrzednych(0, 1, 1, 0),
           Obiekt.z_wspolrzednych(5, 5, 6, 6)]
    assert len(oblicz_przeciecia(odc)) == 3


# --- Nakladanie odcinkow: linia z czescia wspolna -------------------------

def test_nakladanie_dopisuje_czesc_wspolna(tmp_path):
    """Po linii z -inf inf ma isc linia z czescia wspolna i nan nan."""
    a = Obiekt.z_wspolrzednych(-1, 0, 1, 0, kolor=1)
    b = Obiekt.z_wspolrzednych(0, 0, 2, 0, kolor=2)
    d = Dane()
    d.przeciecia = oblicz_przeciecia([a, b])

    print(f"  punkt przeciecia -> ({d.przeciecia[0].punkt.x}, {d.przeciecia[0].punkt.y})")
    assert d.przeciecia[0].punkt.jest_nieskonczony

    czesc = d.przeciecia[0].wspolna
    print(f"  czesc wspolna -> {czesc[0].wspolrzedne} .. {czesc[1].wspolrzedne}")
    assert czesc[0].wspolrzedne == (0.0, 0.0)
    assert czesc[1].wspolrzedne == (1.0, 0.0)

    tekst = do_tekstu(d)
    print(tekst)
    linie = [ln for ln in tekst.splitlines() if ln.strip() and not ln.startswith(("#", "["))]
    assert len(linie) == 2, "maja byc dwie linie: nakladanie i czesc wspolna"

    pola_nakl = linie[0].split()
    pola_czesci = linie[1].split()
    assert pola_nakl[-2:] == ["-inf", "inf"]
    assert pola_czesci[-2:] == ["nan", "nan"]
    # 12 liczb, tak samo jak w zwyklej linii
    assert len(pola_czesci) == 12
    # czesc wspolna powtorzona w kolumnach obu odcinkow
    assert pola_czesci[0:4] == pola_czesci[5:9]
    # kolory zostaja te z oryginalnych odcinkow
    assert pola_czesci[4] == "1" and pola_czesci[9] == "2"

    # zapis i odczyt musi zachowac czesc wspolna
    sciezka = tmp_path / "nakladanie.txt"
    zapisz(sciezka, d)
    d2 = wczytaj(sciezka)
    assert d2.przeciecia[0].wspolna is not None
    assert do_tekstu(d2) == do_tekstu(d)


def test_dotkniecie_koncami_nie_daje_czesci_wspolnej():
    """Styk w jednym punkcie to nie nakladanie, wiec bez dodatkowej linii."""
    a = Obiekt.z_wspolrzednych(0, 0, 5, 0)
    b = Obiekt.z_wspolrzednych(5, 0, 10, 0)
    d = Dane()
    d.przeciecia = oblicz_przeciecia([a, b])
    print(f"  punkt -> {d.przeciecia[0].punkt.wspolrzedne}, wspolna -> {d.przeciecia[0].wspolna}")
    assert d.przeciecia[0].punkt.wspolrzedne == (5.0, 0.0)
    assert d.przeciecia[0].wspolna is None


@pytest.mark.parametrize("zly", [
    "1.0 2.0",                       # dane bez sekcji
    "[nieznana]\n1 2",               # zła nazwa sekcji
    "[points 0]\n1 2 3",             # za dużo liczb
    "[points 0]\n1 abc",             # nie liczba
    "[side]\n0 0 1 0 0 1 5",         # strona spoza -1, 0, 1
])
def test_zly_plik_zglasza_blad(zly):
    with pytest.raises(BladPliku):
        z_tekstu(zly)
    print("  zly plik -> BladPliku zgloszony poprawnie")

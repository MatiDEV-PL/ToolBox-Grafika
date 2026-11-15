import math

import pytest

from toolbox import Obiekt, Punkt, PUNKT_NIESKONCZONOSCI, PUNKT_ROZBIEGAJACY
from toolbox.pliki import (
    BladPliku, Dane, Wielokat, Strona, oblicz_przeciecia, punkt_przeciecia,
    strona_punktu, z_tekstu, do_tekstu, zapisz, wczytaj,
    InfoDanych, WczytajDane, ZapiszDane, wypisz_info, wypisz_dane,
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


# --- InfoDanych / WczytajDane / ZapiszDane ---------------------------------

def _zapisz_przyklad(tmp_path):
    sciezka = tmp_path / "dane.txt"
    sciezka.write_text(PRZYKLAD.lstrip("\n"), encoding="utf-8")
    return sciezka


def test_info_danych_listuje_sekcje_z_komentarzami(tmp_path):
    sciezka = _zapisz_przyklad(tmp_path)
    info = InfoDanych(sciezka)
    nazwy = [n for n, _ in info]
    print(f"  sekcje -> {nazwy}")
    assert nazwy[:4] == ["info", "points 0", "points 2", "segments 1"]
    # komentarz sekcji [points 0]
    komentarz = dict(info)["points 0"]
    assert komentarz == ["Zestaw nr 3"]
    # [info] ma całą zawartość
    assert dict(info)["info"] == ["Przykładowy plik z danymi"]


def test_info_danych_zachowuje_duplikaty_i_kolejnosc(tmp_path):
    """[info] może wystąpić kilka razy, więc wynik to lista, nie słownik."""
    sciezka = tmp_path / "x.txt"
    sciezka.write_text("[info]\n# pierwsze\n[points 0]\n0 0\n[info]\n# drugie\n", encoding="utf-8")
    nazwy = [n for n, _ in InfoDanych(sciezka)]
    print(f"  sekcje -> {nazwy}")
    assert nazwy == ["info", "points 0", "info"]
    assert len(InfoDanych(sciezka)) == 3


def test_info_danych_obcina_puste_linie_na_koncu(tmp_path):
    sciezka = tmp_path / "x.txt"
    sciezka.write_text("[info]\n# linia\n#\n#\n[points 0]\n0 0\n", encoding="utf-8")
    komentarz = InfoDanych(sciezka)[0][1]
    print(f"  komentarze po obcieciu -> {komentarz}")
    assert komentarz == ["linia"]


def test_info_danych_zly_naglowek_zglasza_blad(tmp_path):
    sciezka = tmp_path / "x.txt"
    sciezka.write_text("[points 0\n0 0\n", encoding="utf-8")
    with pytest.raises(BladPliku):
        InfoDanych(sciezka)
    print("  zly naglowek -> BladPliku")


def test_wczytaj_dane_zwraca_to_samo_co_wczytaj(tmp_path):
    sciezka = _zapisz_przyklad(tmp_path)
    a = WczytajDane(sciezka)
    b = wczytaj(sciezka)
    print(f"  punkty={len(a.kontener.punkty())} odcinki={len(a.kontener.odcinki())}")
    assert do_tekstu(a) == do_tekstu(b)


def test_zapisz_dane_i_odczyt(tmp_path):
    sciezka = _zapisz_przyklad(tmp_path)
    dane = WczytajDane(sciezka)
    cel = tmp_path / "kopia.txt"
    ZapiszDane(cel, dane)
    print(f"  zapisano {cel.name}, {cel.stat().st_size} B")
    assert do_tekstu(WczytajDane(cel)) == do_tekstu(dane)


def test_zapisz_dane_tylko_wybrane_sekcje(tmp_path):
    """ZapiszDane ma zapisywać wybrane dane, nie zawsze wszystko."""
    dane = Dane(info=["opis"])
    dane.kontener.dodaj(Punkt(1, 1, 0))
    dane.kontener.dodaj(Obiekt.z_wspolrzednych(0, 0, 5, 0, kolor=1))
    dane.strony.append(Strona(Obiekt.z_wspolrzednych(0, 0, 1, 0), Punkt(0, 1), -1))

    cel = tmp_path / "tylko_punkty.txt"
    ZapiszDane(cel, dane, ["points"])
    tekst = cel.read_text(encoding="utf-8")
    print(tekst)
    assert "[points 0]" in tekst
    assert "[segments" not in tekst
    assert "[side]" not in tekst
    assert "[info]" not in tekst


def test_zapisz_dane_nieznana_sekcja_zglasza_blad(tmp_path):
    with pytest.raises(ValueError):
        ZapiszDane(tmp_path / "x.txt", Dane(), ["bzdury"])
    print("  nieznana sekcja -> ValueError")


def test_wypisz_info_drukuje_sekcje(tmp_path, capsys):
    sciezka = _zapisz_przyklad(tmp_path)
    wypisz_info(sciezka)
    wyjscie = capsys.readouterr().out
    print(wyjscie)
    assert "[points 0]" in wyjscie
    assert "Zestaw nr 3" in wyjscie


def test_wypisz_dane_drukuje_podsumowanie(tmp_path, capsys):
    dane = WczytajDane(_zapisz_przyklad(tmp_path))
    wypisz_dane(dane)
    wyjscie = capsys.readouterr().out
    print(wyjscie)
    assert "punkty: 3" in wyjscie
    assert "odcinki: 2" in wyjscie

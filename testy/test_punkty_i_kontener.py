import math

import pytest

from toolbox import (
    Kontener,
    Obiekt,
    Orientacja,
    Parametryka,
    PodstawoweKolory,
    Punkt,
    PUNKT_NIESKONCZONOSCI,
    PUNKT_ROZBIEGAJACY,
    punkt,
)


# --- Punkt i kolor -------------------------------------------------------

def test_punkt_wspolrzedne_i_kolor():
    p = Punkt(1.5, -2, int(PodstawoweKolory.RED))
    print(f"  Punkt(1.5, -2, RED) -> wspolrzedne={p.wspolrzedne} kolor={p.c}")
    assert p.wspolrzedne == (1.5, -2.0)
    assert p.c == int(PodstawoweKolory.RED)


def test_punkt_domyslny_kolor_to_brak():
    p = punkt(0, 0)
    print(f"  punkt(0, 0) -> kolor={p.c}")
    assert p.c == int(PodstawoweKolory.NONE)


def test_punkt_dopuszcza_kolor_uzytkownika():
    p = punkt(0, 0, c=42)
    print(f"  punkt(0, 0, c=42) -> kolor={p.c}")
    assert p.c == 42


def test_punkt_jest_niezmienny():
    p = Punkt(0, 0)
    with pytest.raises(Exception):
        p.x = 5
    print("  proba zmiany p.x -> wyjatek zgloszony poprawnie")


# --- Punkty specjalne ----------------------------------------------------

def test_punkt_rozbiegajacy():
    p = PUNKT_ROZBIEGAJACY
    print(f"  PUNKT_ROZBIEGAJACY -> x={p.x} y={p.y} nan={p.jest_nan} niesk={p.jest_nieskonczony}")
    assert math.isnan(p.x)
    assert math.isnan(p.y)
    assert p.c == 0
    assert p.jest_nan
    assert p.jest_specjalny
    assert not p.jest_nieskonczony


def test_punkt_nieskonczonosci():
    p = PUNKT_NIESKONCZONOSCI
    print(f"  PUNKT_NIESKONCZONOSCI -> x={p.x} y={p.y} niesk={p.jest_nieskonczony} nan={p.jest_nan}")
    assert p.x == -math.inf
    assert p.y == math.inf
    assert p.c == 0
    assert p.jest_nieskonczony
    assert p.jest_specjalny
    assert not p.jest_nan


def test_zwykly_punkt_nie_jest_specjalny():
    p = punkt(3, 4)
    print(f"  punkt(3, 4) -> specjalny={p.jest_specjalny}")
    assert not p.jest_specjalny


# --- Obiekt (odcinek skierowany) --------------------------------------------------

def test_odcinek_dlugosc():
    o = Obiekt.z_wspolrzednych(0, 0, 3, 4)
    print(f"  Obiekt(0,0)->(3,4) dlugosc -> {o.dlugosc()}")
    assert o.dlugosc() == 5.0


def test_odcinek_jako_parametryka():
    o = Obiekt.z_wspolrzednych(1, 1, 4, 5)
    p = o.jako_parametryka
    print(f"  jako_parametryka -> x0={p.x0} y0={p.y0} dx={p.dx} dy={p.dy}")
    assert (p.x0, p.y0, p.dx, p.dy) == (1, 1, 3, 4)


def test_odcinek_na_odcinku():
    o = Obiekt.z_wspolrzednych(0, 0, 10, 0)
    print(f"  na_odcinku(5,0)={o.na_odcinku(Punkt(5, 0))} na_odcinku(0,0)={o.na_odcinku(Punkt(0, 0))}")
    print(f"  na_odcinku(15,0)={o.na_odcinku(Punkt(15, 0))} na_odcinku(5,1)={o.na_odcinku(Punkt(5, 1))}")
    assert o.na_odcinku(Punkt(5, 0))
    assert o.na_odcinku(Punkt(0, 0))      # koniec
    assert not o.na_odcinku(Punkt(15, 0))  # na przedłużeniu
    assert not o.na_odcinku(Punkt(5, 1))


def test_odcinek_przecinanie():
    a = Obiekt.z_wspolrzednych(0, 0, 10, 0)
    b = Obiekt.z_wspolrzednych(5, -5, 5, 5)
    print(f"  krzyz -> a.tuli_z(b)={a.tuli_z(b)} b.tuli_z(a)={b.tuli_z(a)}")
    assert a.tuli_z(b) and b.tuli_z(a)


# --- Przypadki degenerowane dotyku (regresja) ----------------------------

def test_dotyk_koncami_jest_przecinaniem():
    a = Obiekt.z_wspolrzednych(0, 0, 5, 0)
    b = Obiekt.z_wspolrzednych(5, 0, 5, 5)
    print(f"  dotyk koncami (5,0) -> tuli_z={a.tuli_z(b)}")
    assert a.tuli_z(b)


def test_odcinki_wspolliniowe_nachodzace():
    a = Obiekt.z_wspolrzednych(0, 0, 10, 0)
    b = Obiekt.z_wspolrzednych(5, 0, 15, 0)
    print(f"  wspolliniowe nachodzace -> tuli_z={a.tuli_z(b)}")
    assert a.tuli_z(b)


def test_odcinki_wspolliniowe_rozlaczne():
    a = Obiekt.z_wspolrzednych(0, 0, 5, 0)
    b = Obiekt.z_wspolrzednych(6, 0, 10, 0)
    print(f"  wspolliniowe rozlaczne -> tuli_z={a.tuli_z(b)}")
    assert not a.tuli_z(b)


def test_rownolegle_rozlaczne():
    a = Obiekt.z_wspolrzednych(0, 0, 10, 0)
    b = Obiekt.z_wspolrzednych(0, 5, 10, 5)
    print(f"  rownolegle rozlaczne -> tuli_z={a.tuli_z(b)}")
    assert not a.tuli_z(b)


def test_punkt_specjalny_nie_udaje_przeciecia():
    a = Obiekt(PUNKT_ROZBIEGAJACY, Punkt(1, 1))
    b = Obiekt.z_wspolrzednych(0, 0, 10, 10)
    print(f"  odcinek z nan -> tuli_z={a.tuli_z(b)}")
    assert a.tuli_z(b) is False


# --- Kontener ------------------------------------------------------------

def test_kontener_przyjmuje_punkty_i_odcinki():
    k = Kontener()
    k.dodaj(punkt(0, 0, 1))
    k.dodaj(Obiekt.z_wspolrzednych(0, 0, 1, 1, kolor=2))
    print(f"  kontener -> razem={len(k)} punkty={len(k.punkty())} odcinki={len(k.odcinki())}")
    assert len(k) == 2
    assert len(k.punkty()) == 1
    assert len(k.odcinki()) == 1


def test_kontener_odrzuca_inny_typ():
    with pytest.raises(TypeError):
        Kontener().dodaj("to nie obiekt")
    print("  dodanie stringa -> TypeError zgloszony poprawnie")


def test_kontener_filtr_koloru():
    k = Kontener()
    k.dodaj(punkt(0, 0, int(PodstawoweKolory.RED)))
    k.dodaj(punkt(1, 1, int(PodstawoweKolory.BLUE)))
    czerwone = k.wedlug_koloru(int(PodstawoweKolory.RED))
    print(f"  filtr RED -> {len(czerwone)} element(ow)")
    assert czerwone == [k.wyslij()[0]]


def test_kontener_znajduje_specjalne():
    k = Kontener([punkt(0, 0), PUNKT_ROZBIEGAJACY, PUNKT_NIESKONCZONOSCI])
    znalezione = k.specjalne()
    print(f"  specjalne w kontenerze -> {len(znalezione)}")
    assert len(znalezione) == 2


def test_wersja_jest_spojna():
    from toolbox import __version__
    from toolbox._version import __version__ as v
    print(f"  __version__={__version__} _version={v}")
    assert __version__ == v
    assert isinstance(__version__, str)


def test_kontener_iteracja():
    k = Kontener([punkt(0, 0), punkt(1, 1)])
    print(f"  iteracja -> {len(list(k))} elementy")
    assert len(list(k)) == 2

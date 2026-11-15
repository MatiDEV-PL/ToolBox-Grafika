import pytest
from toolbox.geometria import Parametryka, Orientacja, get_orientacja, CCW, zakret, SortLex, EPS
from toolbox.kolory import PodstawoweKolory
from toolbox.punkty import Punkt

def test_dlugosc_odcinka():
    # Trójkąt pitagorejski (boki 3 i 4, przeciwprostokątna 5)
    odcinek = Parametryka(0, 0, 3, 4)
    wynik = odcinek.dlugosc()
    print(f"  dlugosc wektora (3, 4) -> {wynik}")
    assert wynik == 5.0

def test_get_punkt():
    odcinek = Parametryka(0, 0, 10, 10)

    # Środek odcinka (t=0.5)
    srodek = odcinek.get_punkt(0.5)
    print(f"  get_punkt(0.5) -> {srodek}")
    assert srodek == (5.0, 5.0)

    # Koniec odcinka (t=1.0)
    koniec = odcinek.get_punkt(1.0)
    print(f"  get_punkt(1.0) -> {koniec}")
    assert koniec == (10.0, 10.0)

def test_orientacja_punktow():
    # Odcinek poziomy na osi X: od (0,0) do (10,0)
    odcinek = Parametryka(0, 0, 10, 0)

    # Punkt leżący idealnie na przedłużeniu odcinka
    na_prostej = odcinek.check_orientacja_punkt(15, 0)
    print(f"  (15, 0) -> {na_prostej.name}")
    assert na_prostej == Orientacja.WSPOLLINIOWE

    # Punkt leżący "powyżej" odcinka
    powyzej = odcinek.check_orientacja_punkt(5, 5)
    print(f"  (5, 5)  -> {powyzej.name}")
    assert powyzej == Orientacja.PRZECIWNIE

    # Punkt leżący "poniżej"
    ponizej = odcinek.check_orientacja_punkt(5, -5)
    print(f"  (5, -5) -> {ponizej.name}")
    assert ponizej == Orientacja.ZGODNIE

def test_tuli_z_przecinanie():
    # Odcinek poziomy na osi X: od (0,0) do (10,0)
    poziomy = Parametryka(0, 0, 10, 0)

    # Odcinek pionowy: od (5, -5) do (5, 5) - tworzą krzyż
    pionowy = Parametryka(5, -5, 0, 10)

    # Powinny się przecinać z obu stron
    przecina = poziomy.tuli_z(pionowy)
    print(f"  krzyz: poziomy.tuli_z(pionowy) -> {przecina}")
    assert przecina is True
    assert pionowy.tuli_z(poziomy) is True

    # Odcinek równoległy przesunięty w górę
    rownolegly = Parametryka(0, 5, 10, 0)
    rownolegly_wynik = poziomy.tuli_z(rownolegly)
    print(f"  rownolegly przesuniety: tuli_z -> {rownolegly_wynik}")
    assert rownolegly_wynik is False

def test_kolor_domyslny_i_nadany():
    # Sprawdzenie domyślnego koloru
    odcinek_bez_koloru = Parametryka(0, 0, 1, 1)
    print(f"  domyslny kolor -> {odcinek_bez_koloru.kolor.name} ({int(odcinek_bez_koloru.kolor)})")
    assert odcinek_bez_koloru.kolor == PodstawoweKolory.NONE

    # Sprawdzenie przypisania konkretnego koloru
    odcinek_czerwony = Parametryka(0, 0, 1, 1, kolor=PodstawoweKolory.RED)
    print(f"  ustawiony kolor -> {odcinek_czerwony.kolor.name} ({int(odcinek_czerwony.kolor)})")
    assert odcinek_czerwony.kolor == PodstawoweKolory.RED


# --- Konwencja stron: -1 lewa, 0 wspolliniowo, 1 prawa --------------------

def test_wartosci_enuma_orientacji():
    """Wartosci maja byc -1, 0, 1 (a nie 0, 1, 2)."""
    print(f"  PRZECIWNIE={int(Orientacja.PRZECIWNIE)} WSPOLLINIOWE={int(Orientacja.WSPOLLINIOWE)} "
          f"ZGODNIE={int(Orientacja.ZGODNIE)}")
    assert int(Orientacja.PRZECIWNIE) == -1
    assert int(Orientacja.WSPOLLINIOWE) == 0
    assert int(Orientacja.ZGODNIE) == 1


def test_lewa_strona_to_minus_jeden():
    # Odcinek (0,0)->(10,0) idzie w prawo, wiec punkt nad nim jest po lewej
    lewa = get_orientacja(0, 0, 10, 0, 5, 5)
    prawa = get_orientacja(0, 0, 10, 0, 5, -5)
    print(f"  punkt nad odcinkiem -> {int(lewa)} (lewa) punkt pod -> {int(prawa)} (prawa)")
    assert int(lewa) == -1
    assert int(prawa) == 1


# --- CCW ------------------------------------------------------------------

def test_ccw_skret_w_lewo():
    wynik = CCW(Punkt(0, 0), Punkt(10, 0), Punkt(5, 5))
    print(f"  CCW w lewo -> {wynik}")
    assert wynik is True


def test_ccw_skret_w_prawo():
    wynik = CCW(Punkt(0, 0), Punkt(10, 0), Punkt(5, -5))
    print(f"  CCW w prawo -> {wynik}")
    assert wynik is False


def test_ccw_wspolliniowe():
    wynik = CCW(Punkt(0, 0), Punkt(10, 0), Punkt(5, 0))
    print(f"  CCW wspolliniowe -> {wynik}")
    assert wynik is False


def test_zakret_podaje_kierunek():
    """CCW mowi tylko tak/nie, zakret rozroznia lewo i prawo."""
    lewo = zakret(Punkt(0, 0), Punkt(10, 0), Punkt(5, 5))
    prawo = zakret(Punkt(0, 0), Punkt(10, 0), Punkt(5, -5))
    prosto = zakret(Punkt(0, 0), Punkt(10, 0), Punkt(5, 0))
    print(f"  zakret: lewo={lewo} prawo={prawo} prosto={prosto}")
    assert (lewo, prawo, prosto) == (1, -1, 0)


# --- Tolerancja eps -------------------------------------------------------

def test_eps_ustawione():
    print(f"  EPS = {EPS}")
    assert EPS == 1e-9


def test_eps_uznaje_prawie_wspolliniowe():
    """Bez tolerancji float wypadalby jako wyraznie po jednej stronie."""
    malenka = get_orientacja(0, 0, 10, 0, 5, 1e-12)
    wyrazna = get_orientacja(0, 0, 10, 0, 5, 1e-6)
    print(f"  odchylenie 1e-12 -> {malenka.name}, odchylenie 1e-6 -> {wyrazna.name}")
    assert malenka == Orientacja.WSPOLLINIOWE
    assert wyrazna == Orientacja.PRZECIWNIE


# --- SortLex --------------------------------------------------------------

def test_sortlex_zachowuje_wszystkie_punkty():
    punkty = [Punkt(2, 1), Punkt(1, 5), Punkt(2, 3)]
    for kierunek in ("LD", "LU", "RD", "RU"):
        wynik = SortLex(punkty, kierunek)
        print(f"  {kierunek} -> {[(p.x, p.y) for p in wynik]}")
    assert len(SortLex(punkty, "LD")) == 3


def test_sortlex_ld_rosnaco_po_x_i_y():
    punkty = [Punkt(2, 1), Punkt(1, 5), Punkt(1, -2)]
    wynik = [(p.x, p.y) for p in SortLex(punkty, "LD")]
    print(f"  LD -> {wynik}")
    assert wynik == [(1.0, -2.0), (1.0, 5.0), (2.0, 1.0)]


def test_sortlex_lu_y_malejaco():
    punkty = [Punkt(1, -2), Punkt(1, 5)]
    wynik = [(p.x, p.y) for p in SortLex(punkty, "LU")]
    print(f"  LU -> {wynik}")
    assert wynik == [(1.0, 5.0), (1.0, -2.0)]


def test_sortlex_rd_x_malejaco():
    punkty = [Punkt(1, 5), Punkt(2, 1)]
    wynik = [(p.x, p.y) for p in SortLex(punkty, "RD")]
    print(f"  RD -> {wynik}")
    assert wynik == [(2.0, 1.0), (1.0, 5.0)]


def test_sortlex_ul_os_y_glowna():
    """UL to 'od gory, od lewej', czyli y malejaco, potem x rosnaco."""
    punkty = [Punkt(2, 1), Punkt(1, 5), Punkt(1, -2)]
    wynik = [(p.x, p.y) for p in SortLex(punkty, "UL")]
    print(f"  UL -> {wynik}")
    assert wynik == [(1.0, 5.0), (2.0, 1.0), (1.0, -2.0)]


def test_sortlex_dl_os_y_glowna():
    """DL to 'od dolu, od lewej', czyli y rosnaco, potem x rosnaco."""
    punkty = [Punkt(2, 1), Punkt(1, 5), Punkt(1, -2)]
    wynik = [(p.x, p.y) for p in SortLex(punkty, "DL")]
    print(f"  DL -> {wynik}")
    assert wynik == [(1.0, -2.0), (2.0, 1.0), (1.0, 5.0)]


def test_sortlex_ta_sama_os_zglasza_blad():
    with pytest.raises(ValueError):
        SortLex([Punkt(0, 0)], "LL")
    print("  kierunek LL (dwie litery tej samej osi) -> ValueError")


def test_sortlex_nieznany_kierunek_zglasza_blad():
    with pytest.raises(ValueError):
        SortLex([Punkt(0, 0)], "XX")
    print("  nieznany kierunek -> ValueError zgloszony poprawnie")

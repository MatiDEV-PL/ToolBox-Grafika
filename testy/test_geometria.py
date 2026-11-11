import pytest
from toolbox.geometria import Parametryka, Orientacja
from toolbox.kolory import PodstawoweKolory

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

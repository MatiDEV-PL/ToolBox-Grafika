from toolbox.geometria import Parametryka

def test_dlugosc_odcinka():
    odcinek = Parametryka(0, 0, 3, 4)

    wynik = odcinek.dlugosc()

    assert wynik == 5.0
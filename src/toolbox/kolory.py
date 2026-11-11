from enum import IntEnum

class PodstawoweKolory(IntEnum):
    """Kolory jakie mamy zdefiniowane w bibliotece.

    0 to brak koloru 1 niebieski 2 czerwony 3 zielony.
    Jak ktoś chce swój kolor to może wpisać liczbę większą od 3.
    """
    NONE = 0
    BLUE = 1
    RED = 2
    GREEN = 3

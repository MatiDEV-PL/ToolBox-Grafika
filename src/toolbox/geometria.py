from enum import IntEnum
from math import hypot
from .kolory import PodstawoweKolory

class Orientacja(IntEnum):
    """Zwracane stany orientacji dla trzech punktów."""
    WSPOLLINIOWE = 0
    ZGODNIE = 1
    PRZECIWNIE = 2

def get_orientacja(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> Orientacja:
    """Sprawdza orientację uporządkowanej trójki punktów."""
    val = ((y2 - y1) * (x3 - x2)) - ((x2 - x1) * (y3 - y2))

    if val == 0:
        return Orientacja.WSPOLLINIOWE
    elif val > 0:
        return Orientacja.ZGODNIE
    return Orientacja.PRZECIWNIE

class Parametryka:
    """Odcinek zdefiniowany parametrycznie: punkt startowy + wektor kierunkowy."""
    
    def __init__(self, x0: float, y0: float, dx: float, dy: float, kolor: int = PodstawoweKolory.NONE):
        self.x0 = x0
        self.y0 = y0
        self.dx = dx
        self.dy = dy
        self.kolor = kolor

    @property
    def koniec_x(self) -> float:
        """Zwraca współrzędną X końca odcinka."""
        return self.x0 + self.dx

    @property
    def koniec_y(self) -> float:
        """Zwraca współrzędną Y końca odcinka."""
        return self.y0 + self.dy

    def get_punkt(self, t: float) -> tuple[float, float]:
        """Zwraca punkt dla parametru t (0.0 - poczatek, 1.0 - koniec)."""
        return (self.x0 + t * self.dx, self.y0 + t * self.dy)

    def dlugosc(self) -> float:
        """Zwraca długość odcinka."""
        return hypot(self.dx, self.dy)

    def check_orientacja_punkt(self, px: float, py: float) -> Orientacja:
        """Sprawdza, po której stronie odcinka znajduje się punkt."""
        return get_orientacja(self.x0, self.y0, self.koniec_x, self.koniec_y, px, py)

    def tuli_z(self, other: 'Parametryka') -> bool:
        """
        Sprawdza, czy ten odcinek przecina się z innym odcinkiem, 
        wykorzystując badanie orientacji.
        """
        o1 = self.check_orientacja_punkt(other.x0, other.y0)
        o2 = self.check_orientacja_punkt(other.koniec_x, other.koniec_y)
        
        o3 = other.check_orientacja_punkt(self.x0, self.y0)
        o4 = other.check_orientacja_punkt(self.koniec_x, self.koniec_y)

        if (o1 != o2) and (o3 != o4):
            return True
            
        return False

    def __repr__(self):
        return f"Parametryka(p=({self.x0}, {self.y0}), v=[{self.dx}, {self.dy}], kolor={self.kolor})"
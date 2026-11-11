from enum import IntEnum
from math import hypot, isfinite
from .kolory import PodstawoweKolory
from .punkty import Punkt, PUNKT_ROZBIEGAJACY, PUNKT_NIESKONCZONOSCI

class Orientacja(IntEnum):
    """Trzy możliwe odpowiedzi gdy pytamy o orientację trzech punktów."""
    WSPOLLINIOWE = 0
    ZGODNIE = 1
    PRZECIWNIE = 2

def get_orientacja(x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> Orientacja:
    """Sprawdza jak ułożone są trzy punkty, patrzymy na znak iloczynu wektorowego."""
    val = ((y2 - y1) * (x3 - x2)) - ((x2 - x1) * (y3 - y2))

    if val == 0:
        return Orientacja.WSPOLLINIOWE
    elif val > 0:
        return Orientacja.ZGODNIE
    return Orientacja.PRZECIWNIE

class Parametryka:
    """Odcinek zapisany jako punkt startowy i wektor kierunkowy.

    Używamy tego do obliczeń wewnątrz biblioteki. Jak ktoś chce odcinek
    z punktów to niech bierze Obiekt.
    """

    def __init__(self, x0: float, y0: float, dx: float, dy: float, kolor: int = PodstawoweKolory.NONE):
        self.x0 = x0
        self.y0 = y0
        self.dx = dx
        self.dy = dy
        self.kolor = kolor

    @property
    def koniec_x(self) -> float:
        """X końca odcinka czyli start plus wektor."""
        return self.x0 + self.dx

    @property
    def koniec_y(self) -> float:
        """Y końca odcinka czyli start plus wektor."""
        return self.y0 + self.dy

    def get_punkt(self, t: float) -> tuple[float, float]:
        """Punkt dla parametru t, 0.0 to początek 1.0 to koniec."""
        return (self.x0 + t * self.dx, self.y0 + t * self.dy)

    def dlugosc(self) -> float:
        """Długość odcinka z Pitagorasa."""
        return hypot(self.dx, self.dy)

    def check_orientacja_punkt(self, px: float, py: float) -> Orientacja:
        """Sprawdza po której stronie odcinka leży punkt (px, py)."""
        return get_orientacja(self.x0, self.y0, self.koniec_x, self.koniec_y, px, py)

    def na_odcinku(self, px: float, py: float) -> bool:
        """Czy punkt leży na odcinku, końce też się liczą."""
        if self.check_orientacja_punkt(px, py) != Orientacja.WSPOLLINIOWE:
            return False
        # Że współliniowy to jeszcze za mało, trzeba sprawdzić czy jest w zakresie
        return (
            min(self.x0, self.koniec_x) <= px <= max(self.x0, self.koniec_x)
            and min(self.y0, self.koniec_y) <= py <= max(self.y0, self.koniec_y)
        )

    def tuli_z(self, other: 'Parametryka') -> bool:
        """Czy te dwa odcinki mają wspólny punkt.

        Sprawdzamy trzy rzeczy: czy przecinają się w środku czy dotykają
        się końcami i czy nachodzą na siebie jak są współliniowe.
        Jak na końcu jest nan albo nieskończoność to nic mądrego nie
        policzymy i zwracamy False.
        """
        if self._ma_punkt_specjalny() or other._ma_punkt_specjalny():
            return False

        o1 = self.check_orientacja_punkt(other.x0, other.y0)
        o2 = self.check_orientacja_punkt(other.koniec_x, other.koniec_y)

        o3 = other.check_orientacja_punkt(self.x0, self.y0)
        o4 = other.check_orientacja_punkt(self.koniec_x, self.koniec_y)

        # Normalne przecięcie, końce są po różnych stronach
        if (o1 != o2) and (o3 != o4):
            return True

        # Końce leżą na drugim odcinku, dotknięcie albo nachodzenie
        if o1 == Orientacja.WSPOLLINIOWE and self.na_odcinku(other.x0, other.y0):
            return True
        if o2 == Orientacja.WSPOLLINIOWE and self.na_odcinku(other.koniec_x, other.koniec_y):
            return True
        if o3 == Orientacja.WSPOLLINIOWE and other.na_odcinku(self.x0, self.y0):
            return True
        if o4 == Orientacja.WSPOLLINIOWE and other.na_odcinku(self.koniec_x, self.koniec_y):
            return True

        return False

    def _ma_punkt_specjalny(self) -> bool:
        """Czy któryś koniec to nan albo nieskończoność."""
        return not all(
            isfinite(v) for v in (self.x0, self.y0, self.koniec_x, self.koniec_y)
        )

    def __repr__(self):
        return f"Parametryka(p=({self.x0}, {self.y0}), v=[{self.dx}, {self.dy}], kolor={self.kolor})"


class Obiekt:
    """Odcinek skierowany złożony z dwóch punktów i koloru.

    Początek i koniec to punkty z których łatwo odczytać współrzędne
    (px, py) i (qx, qy) a kolor to zwykła liczba całkowita.
    """

    def __init__(self, poczatek: Punkt, koniec: Punkt, kolor: int = int(PodstawoweKolory.NONE)):
        self.poczatek = poczatek
        self.koniec = koniec
        self.kolor = kolor

    @classmethod
    def z_wspolrzednych(
        cls,
        px: float, py: float,
        qx: float, qy: float,
        kolor: int = int(PodstawoweKolory.NONE),
    ) -> 'Obiekt':
        """Robimy odcinek z czterech liczb żeby nie budować punktów ręcznie."""
        return cls(Punkt(px, py), Punkt(qx, qy), kolor)

    @property
    def jako_parametryka(self) -> Parametryka:
        """Zamiana na zapis z punktem i wektorem bo tak się łatwiej liczy."""
        return Parametryka(
            self.poczatek.x,
            self.poczatek.y,
            self.koniec.x - self.poczatek.x,
            self.koniec.y - self.poczatek.y,
            kolor=self.kolor,
        )

    def dlugosc(self) -> float:
        """Długość odcinka z Pitagorasa."""
        return hypot(self.koniec.x - self.poczatek.x, self.koniec.y - self.poczatek.y)

    def na_odcinku(self, punkt: Punkt) -> bool:
        """Czy punkt leży na odcinku, końce też się liczą."""
        return self.jako_parametryka.na_odcinku(punkt.x, punkt.y)

    def tuli_z(self, other: 'Obiekt') -> bool:
        """Czy obiekty mają wspólny punkt."""
        return self.jako_parametryka.tuli_z(other.jako_parametryka)

    def __repr__(self):
        return (
            f"Obiekt(poczatek=({self.poczatek.x}, {self.poczatek.y}), "
            f"koniec=({self.koniec.x}, {self.koniec.y}), kolor={self.kolor})"
        )
